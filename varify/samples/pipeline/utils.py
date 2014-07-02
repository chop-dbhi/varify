import logging
from datetime import datetime
from varify.genome.models import Genotype
from varify.variants.utils import calculate_md5
from varify.variants.pipeline.utils import VariantCache
from varify.pipeline import checks
from varify.raw.utils.stream import VCFPGCopyEditor
from varify.samples.models import Result

log = logging.getLogger(__name__)


class ResultStream(VCFPGCopyEditor):
    vcf_fields = ('CHROM', 'POS', 'REF', 'ALT')

    info_fields = ('DB', 'DS', 'DP', 'Dels', 'MQ', 'MQ0', 'BaseQRankSum',
                   'MQRankSum', 'ReadPosRankSum', 'SB', 'Hrun',
                   'HaplotypeScore', 'QD', 'FS', 'BaseCounts')

    output_columns = ('in_dbsnp', 'downsampling', 'raw_read_depth',
                      'spanning_deletions', 'mq', 'mq0', 'baseq_rank_sum',
                      'mq_rank_sum', 'read_pos_rank_sum', 'strand_bias',
                      'homopolymer_run', 'haplotype_score', 'quality_by_depth',
                      'fisher_strand', 'base_counts', 'variant_id',
                      'sample_id', 'read_depth', 'quality', 'genotype_id',
                      'genotype_quality', 'coverage_ref', 'coverage_alt',
                      'phred_scaled_likelihood', 'created', 'modified')

    def __init__(self, *args, **kwargs):
        self.sample_id = kwargs.pop('sample_id')
        self.vcf_sample = kwargs.pop('vcf_sample')
        self.now = datetime.now()
        super(ResultStream, self).__init__(*args, **kwargs)
        self.genotypes = dict(Genotype.objects.values_list('value', 'pk'))
        self.variants = VariantCache()

    def process_line(self, record):
        # we are revisiting the same line once for each sample
        # until I figure out how the cleaning and loading will
        # work otherwise

        # Ensures the cache is updated and available
        self.variants.ensure_cache(record)

        # Calculate the MD5 of the variant itself (not the record)
        md5 = calculate_md5(record)

        # Ensure the variant exists
        variant_id = self.variants.get(md5)
        assert variant_id is not None

        cleaned = super(ResultStream, self).process_line(record)
        # Remove variant specific parts
        cleaned = cleaned[4:]

        # can these be indexed?
        call = record.genotype(self.vcf_sample)

        # Already seen this variant for this sample, otherwise we would get a
        # duplicate key value violation in sample_result.
        if Result.objects.filter(
                variant=variant_id, sample=self.sample_id).exists():
            return None

        # The possibility for multiple alleles in these wide vcfs is almost
        # infinite so we need to triage the really weird ones into having a
        # reference allele "0/#" or being off the map entirely "#/#"".
        gt = getattr(call.data, 'GT', None)
        if gt:
            try:
                keyed_geno = self.genotypes[gt]
            except KeyError:
                if gt.startswith('0'):
                    keyed_geno = self.genotypes['0/#']
                else:
                    keyed_geno = self.genotypes['#/#']
        else:
            keyed_geno = None

        dp = getattr(call.data, 'DP', None)
        gq = getattr(call.data, 'GQ', None)
        ad = getattr(call.data, 'AD', None)
        if ad and len(ad) > 1:
            ad0 = ad[0]
            ad1 = ad[1]
        else:
            ad0 = None
            ad1 = None
        pl = getattr(call.data, 'PL', None)
        if pl:
            pl = ','.join([str(x) for x in pl])

        # Append remaining columns
        other = [variant_id, self.sample_id, dp, record.QUAL, keyed_geno, gq,
                 ad0, ad1, pl, self.now, self.now]

        cleaned.extend([self.process_column('', x) for x in other])
        return cleaned

    def readline(self, size=-1):
        "Ignore the `size` since a complete line must be processed."
        while True:
            try:
                record = next(self.reader)
            except StopIteration:
                break

            # Ensure this is a valid record
            if checks.record_is_valid(record):
                # Process the line
                cleaned = self.process_line(record)
                if cleaned:
                    return self.outdel.join([str(x) for x in cleaned]) + '\n'

        return ''
