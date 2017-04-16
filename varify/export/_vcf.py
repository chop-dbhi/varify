import time
import string
import json
import textwrap
import logging
import vcf
from sys import version_info
from cStringIO import StringIO
from socket import gethostname
from django.db.models import Q
from avocado.export._base import BaseExporter
from vdw.samples.models import Result, Project, Sample

log = logging.getLogger(__name__)

# The following generates a varg list for Python 2.7, that triggers an
# exception in the Python 2.6 standard library.
if version_info < (2, 7):
    unicode_conv_vargs = {}
else:
    unicode_conv_vargs = {'errors': 'backslashreplace'}


def _grab_effects_string(variant):
    lines = []
    allEffects = variant.effects.all()
    for effect in allEffects:
        nextLine = effect.effect.value
        nextLine += '('
        nextLine += effect.effect.impact.label
        nextLine += '|' + ((effect.functional_class.label or '')
                           if effect.functional_class else '')
        nextLine += '|' + (effect.codon_change or '')
        nextLine += '|' + (effect.amino_acid_change or '')
        nextLine += '|' + ((effect.gene.symbol or '')
                           if effect.gene else '')
        nextLine += '|' + ((effect.transcript.refseq_id or '')
                           if effect.transcript else '')
        nextLine += '|' + (effect.segment or '')
        nextLine += '|' + (effect.hgvs_c or '')
        nextLine += '|' + (effect.hgvs_p or '')
        nextLine += ")"
        lines.append(nextLine)
    if(len(allEffects) > 0):
        return string.join(lines, ",")
    else:
        return None


class VcfExporter(BaseExporter):
    # VCF exporter
    # The primary purpose of this exporter is not to generate verbatim copies
    # of VCF entries loaded into the db, but to use VCF as a common format that
    # integrates into a bioinformatics workflow.  This exporter works with a
    # client currently hosted at http://github.com/awenocur/varify_client.

    short_name = 'VCF'
    long_name = 'Variant Call Format'

    file_extension = 'vcf'
    content_type = 'text/variant-call-format'

    def write(self, iterable, buff=None, request=None, *args, **kwargs):
        # Figure out what we call this data source.
        vcf_source = gethostname()
        if request:
            vcf_source = request.get_host()

        # These are descriptions of the fields currently supported by the
        # exporter. This is to be prepended to the actual header, describing
        # lines.
        vcf_file_header = textwrap.dedent('''\
            ##fileformat=VCFv4.1
            ##fileDate= ''' + time.strftime("%Y%m%d") + '''
            ##source=''' + vcf_source + '''
            ##reference=GRCh37
            ##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
            ##FORMAT=<ID=AD,Number=.,Type=Integer,Description="Allelic depths for the ref and alt alleles in the order listed">
            ##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Approximate read depth (reads with MQ=255 or with bad mates are filtered)">
            ##FORMAT=<ID=GQ,Number=1,Type=Float,Description="Genotype Quality">
            ##INFO=<ID=EFF,Number=.,Type=String,Description="Predicted effects for this variant.Format: 'Effect (Effect_Impact | Functional_Class | Codon_Change | Amino_Acid_Change | Gene_Name | Transcript_ID | Segment | HGVS_DNA_nomenclature | HGVS_protein_nomenclature)' ">
            #CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT''')  # noqa

        buff = self.get_file_obj(buff)

        # This shall contain sample labels if POST data are detected.
        labels = None

        # These shall contain ranges if POST data are detected.
        chromosomes = []
        beginning_bp = []
        ending_bp = []

        # This is an array to manage project permissions from the command line
        # utility.
        permitted_projects = None

        # POST should ignore the iterable by design, since it interfaces with
        # a dedicated client. Decode the parameters passed from the client.
        if request and request.method == 'POST':
            data = json.load(request._stream)

            # Get the list of sample labels.
            labels = data['samples']

            # These are dictionaries encoded by the client to store chromosome
            # ranges.
            range_dicts = None

            # Chromosome ranges are optional.
            if 'ranges' in data:
                range_dicts = data['ranges']

            if range_dicts:
                for dict in range_dicts:
                    if "chrom" in dict and "start" in dict and "end" in dict:
                        range_chrom = str(dict["chrom"])
                        range_start = int(dict["start"])
                        range_end = int(dict["end"])
                        if(range_end >= range_start):
                            chromosomes.append(range_chrom)
                            beginning_bp.append(range_start)
                            ending_bp.append(range_end)

            permitted_projects = []

            # Results may be limited to a list of projects; this is required
            # for queries that span multiple projects.
            if 'projects' in data:
                permitted_project_labels = str(data["projects"])
                get_permitted_projects = \
                    Project.objects.\
                    filter(label__in=permitted_project_labels)
                for permitted_project in get_permitted_projects:
                    permitted_projects.append(permitted_project.id)

            else:
                get_permitted_project_samples = \
                    Sample.objects. \
                    filter(label__in=labels).distinct('project')
                for sample in get_permitted_project_samples:
                    permitted_projects.append(sample.project.id)
                # No projects were specified on the command line, so there
                # should be only one permitted.
                assert len(permitted_projects) <= 1

        # The following is an ORM-based implementation that works for now;
        # this should be migrated to use Avocado if possible. Start with a
        # QuerySet for all results.
        all_results = Result.objects.get_query_set()

        # These shall be Q objects.
        label_criteria = None
        range_criteria = None

        # Labels are specified by the client; the iterable is not used.
        if labels is not None:
            # Take the union of all sets matching sample labels in the labels
            # array; store the predicate as a Q object.
            for next_label in labels:
                next_criterion = Q(sample__label=next_label)
                if label_criteria is None:
                    label_criteria = next_criterion
                else:
                    label_criteria |= next_criterion

            # Take the union of all sets matching ranges in the 3 corresponding
            # arrays; store the predicate as a Q object.
            for chr, start, end in zip(chromosomes, beginning_bp, ending_bp):
                next_criterion = Q(variant__chr__label=chr) & Q(
                    variant__pos__lt=end + 1) & Q(
                    variant__pos__gt=start - 1)
                if range_criteria is None:
                    range_criteria = next_criterion
                else:
                    range_criteria |= next_criterion

        else:  # The iterable is being used.
            result_ids = []
            for row in iterable:
                result_ids.append(row[0])

            # Here, range_criteria actually matches the results from the
            # iterator, not any specific range.  The variable is used for
            # convenience.
            label_criteria = Q(id__in=result_ids)

        # If no ranges were provided, or the iterator is being used,
        # use a dummy Q object.
        if range_criteria is None:
            range_criteria = Q()

        label_and_range_criteria = label_criteria & range_criteria

        # Grab the results, finally; take the intersection of the two Q
        # objects defined above, sort by the order defined in the VCF v4
        # specification.
        selected_results = all_results.prefetch_related('sample', 'variant')\
            .prefetch_related('variant__chr')\
            .filter(label_and_range_criteria)\
            .order_by('variant__chr__order', 'variant__pos')

        # Ensure results are from a particular project.
        if permitted_projects:
            selected_results = selected_results.filter(
                sample__project__id__in=permitted_projects)

        # This dict of rows in the VCF file is used to look up rows (_Record
        # objects) that were already created, to aggregate samples by variant;
        # each row represents one variant.
        rows = {}

        # This is an array of VCF rows in the proper order, defined by the DBMS
        # sorting by variant positon.
        ordered_rows = []

        # This is something pyVCF needs to know how the call is formatted;
        # each sample listed in a row has sub-columns in this order.
        # pyVCF requires this info to be declared again a different way.
        row_call_format = vcf.model.make_calldata_tuple(['GT',
                                                         'AD',
                                                         'DP',
                                                         'GQ'])

        # These are data types for the fields declared on the prior line.
        row_call_format._types.append('String')
        row_call_format._types.append('String')
        row_call_format._types.append('Integer')
        row_call_format._types.append('Integer')

        # This is a lookup dict for sample indexes; this is linked to each
        # PyVCF Record object.
        sample_indexes = {}

        # Keep track of the number of samples detected.
        sample_num = 0

        # Loop over all Results returned.
        for result in selected_results:
            # This sample may or may not be the first for a particular
            # variant.
            sample = result.sample

            # PyVCF uses ASCII, sorry; here's where we check whether we're
            # already handling a particular sample; if we're not, assign
            # it an index
            if sample.label.encode('ascii', **unicode_conv_vargs) \
                    not in sample_indexes:
                sample_indexes[
                    sample.label.encode(
                        'ascii', **unicode_conv_vargs)] = sample_num
                sample_num += 1
            variant = result.variant

            # Here's where we check whether we're already handling a
            # particular variant; if we're not, create a new PyVCF record.
            if variant.id in rows:
                next_row = rows[variant.id]
            else:
                rsid = variant.rsid
                if rsid:
                    rsid = rsid.encode('ascii', **unicode_conv_vargs)

                # We haven't seen this variant before; create a new record.
                next_row = vcf.model._Record(
                    ID=rsid,
                    CHROM=variant.chr.label,
                    POS=variant.pos,
                    REF=variant.ref,
                    ALT=variant.alt,
                    QUAL=result.quality,
                    FILTER=None,
                    # here's where the call format is specified
                    # a second time, as required by PyVCF
                    INFO={'EFF': _grab_effects_string(variant)},
                    FORMAT='GT:AD:DP:GQ',
                    sample_indexes=sample_indexes,
                    samples=[])

                # Make it known that this variant has a PyVCF record.
                rows[variant.id] = next_row

                # The order of rows as retrieved from the DB should be
                # right for the VCF.
                ordered_rows.append(next_row)

            # This is a hack to replace NULLs in the DB with zero where
            # appropriate.
            ref_coverage = result.coverage_ref or 0
            alt_coverage = result.coverage_alt or 0

            # Populate the allelic depth field for a particular call.
            next_row_call_allelicDepth = '{0:d},{1:d}'.format(
                ref_coverage, alt_coverage)

            # Generate the call values array for PyVCF.
            result_genotype_string = None
            if(result.genotype):
                result_genotype_string = result.genotype.value.encode(
                    'ascii', **unicode_conv_vargs)
            next_row_call_values = [result_genotype_string,
                                    next_row_call_allelicDepth,
                                    result.read_depth,
                                    result.genotype_quality]

            # Add the call to its corresponding PyVCF record.
            next_row.samples.append(
                vcf.model._Call(next_row, sample.label,
                                row_call_format(*next_row_call_values)))

        # Sort samples as they are found on the command line.
        i = 0
        if labels:
            for label in labels:
                if (label in sample_indexes):
                    sample_indexes[label] = i
                    i += 1

        # Prepare a string for the sample headers.
        just_sample_indexes = sample_indexes.values()
        just_sample_names = sample_indexes.keys()
        sorted_sample_names = zip(*sorted(zip(just_sample_indexes,
                                              just_sample_names)))[1]
        template_sample_string = '\t' + '\t'.join(sorted_sample_names)

        # Create a VCF writer based on a programmatically generated
        # template.
        fake_template_file = StringIO(vcf_file_header +
                                      template_sample_string)
        template_reader = vcf.Reader(fake_template_file)
        writer = vcf.Writer(buff, template_reader)
        fake_template_file.close()

        # Add nulls to replace missing calls; this is necessary for
        # variants not called for all samples in the VCF; this should
        # really be done by PyVCF.
        for next_row in ordered_rows:
            remaining_sample_labels = sample_indexes.keys()
            if len(next_row.samples) < len(remaining_sample_labels):
                for next_sample in next_row.samples:
                    remaining_sample_labels.remove(next_sample.sample)
                for next_label in remaining_sample_labels:
                    next_row.samples.append(
                        vcf.model._Call(
                            next_row, next_label,
                            row_call_format(None, None, None, None)))

            # The following code really should be part of PyVCF:
            # sorting the calls within the row:
            reordered_samples = [None] * len(next_row.samples)
            for call in next_row.samples:
                index = next_row._sample_indexes[call.sample]

                # The following line checks for an exceptional condition;
                # this should be handled in a later version of Varify
                # rather than being thrown, and should not be added
                # to PyVCF.
                assert reordered_samples[index] is None
                reordered_samples[index] = call

            next_row.samples = reordered_samples

            writer.write_record(next_row)

        return buff
