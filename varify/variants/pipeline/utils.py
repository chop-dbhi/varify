import re
import logging
from django.core.cache import get_cache
from django.db import IntegrityError
from varify.pipeline import PIPELINE_CACHE_ALIAS
from varify.genome.models import Chromosome
from varify.variants.models import Variant, VariantType, Effect, FunctionalClass, VariantEffect
from varify.variants.utils import calculate_md5
from varify.raw.utils.stream import VCFPGCopyEditor
from varify.genes.models import Gene, Transcript
from varify.pipeline import checks

log = logging.getLogger(__name__)


class VariantCache(object):
    """Variant cache and lookup by chromosome and position.

    If `shared` cache is enabled, this enables parallelization since this
    cache ensures atomic gets and sets. The shared cache acts as central
    reference for processes to check against.

    For loading, if a record is present in the cache, it has already been
    processed and thus can be skipped by other processes attempting to load the
    variant.

    The other use case is a central cache for looking up variant keys. This
    prevents having in-process caches that possibly redundant.
    """
    def __init__(self, size=1000, shared=True, timeout=60 * 60 * 24):
        self.size = size
        self.chrom = None
        self.start = None
        self.end = None

        self.shared = shared
        if shared:
            # Only applies to the shared cache..
            self.timeout = timeout
            self._cache = get_cache(PIPELINE_CACHE_ALIAS)
        else:
            self._cache = {}

    def _get_variants(self):
        return Variant.objects.filter(chr__value=self.chrom,
            pos__range=(self.start, self.end)).values_list('md5', 'pk')

    def ensure_cache(self, record):
        if record.CHROM != self.chrom or not (self.start <= record.POS <= self.end):
            self.chrom = record.CHROM
            self.start = record.POS
            self.end = self.start + self.size

            if self.shared:
                return

            self._cache = dict(self._get_variants())

    def __contains__(self, md5):
        if not self.shared:
            return md5 in self._cache

        # If the add is successful, that means it is not present in the
        # shared cached and thus should return False which will cause the
        # variant to be loaded. Note, this acts as a placeholder and does
        # not store the primary key of variant. This is generally not an
        # issue since subsequent processes will always load a fresh
        # snapshot of variants from the database.
        if not self._cache.add(md5, -1, self.timeout):
            return True

        present = False

        # Since these are lazily cached, hit the database for a slice of
        # variants.
        variants = self._get_variants()
        for _md5, _pk in variants.iterator():
            if _md5 == md5:
                present = True
            self._cache.set(_md5, _pk, self.timeout)

        return present

    def get(self, md5, default=None):
        if not self.shared:
            return self._cache.get(md5, default)

        pk = self._cache.get(md5)

        # Ensure this is not a placholder
        if pk is None or pk == -1:
            variants = self._get_variants()
            for _md5, _pk in variants.iterator():
                if _md5 == md5:
                    pk = _pk
                self._cache.set(_md5, _pk, self.timeout)
        return pk


class VariantStream(VCFPGCopyEditor):
    """Reads a VCF file and loads variants that are not already in the database.

    An instance of `VariantCache` is used to determine whether a variant is
    present in the database or not.
    """
    vcf_fields = ('CHROM', 'POS', 'REF', 'ALT', 'ID')

    output_columns = ('chr_id', 'pos', 'ref', 'alt', 'rsid', 'type_id', 'md5')

    def __init__(self, *args, **kwargs):
        self.use_cache = kwargs.pop('use_cache', True)
        cache_size = kwargs.pop('cache_size', 1000)
        super(VariantStream, self).__init__(*args, **kwargs)

        # Cache of chromosomes and their keys
        self.chromosomes = dict([(x.value, x) for x in Chromosome.objects.all()])

        # Cache variant types and their keys
        self.variant_types = dict([(x.value, x) for x in VariantType.objects.all()])

        # Special cache for variants
        self.variants = VariantCache(cache_size)

    def process_line(self, record):
        cleaned = super(VariantStream, self).process_line(record)

        # Replace chromosome with primary key
        cleaned[0] = str(self.chromosomes[cleaned[0]].pk)

        # Ensure the variant type exists.. this will *rarely* get updated
        var_type = record.var_type.upper()
        if var_type not in self.variant_types:
            vt = VariantType(label=var_type, value=var_type)
            try:
                vt.save()
            except IntegrityError:
                vt = VariantType.objects.get(label=var_type, value=var_type)
            self.variant_types[var_type] = vt

        # Add variant type
        cleaned.append(str(self.variant_types[var_type].pk))

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
                if self.use_cache:
                    # Ensures the cache is updated and available
                    self.variants.ensure_cache(record)

                # Calculate the MD5 of the variant itself (not the record)
                md5 = calculate_md5(record)

                # Ensure this variant is not already loaded
                if not self.use_cache or md5 not in self.variants:
                    cleaned = self.process_line(record)
                    cleaned.append(md5)
                    return self.outdel.join(cleaned) + '\n'

        return ''


class EffectStream(VCFPGCopyEditor):
    vcf_fields = ('CHROM', 'POS', 'REF', 'ALT')

    output_columns = ('variant_id', 'codon_change', 'amino_acid_change',
        'effect_id', 'functional_class_id', 'gene_id', 'transcript_id',
        'segment', 'hgvs_c', 'hgvs_p')

    def __init__(self, *args, **kwargs):
        self.chromosomes = dict([(x.value, x) for x in Chromosome.objects.all()])
        self.effects = dict(Effect.objects.values_list('value', 'pk'))
        self.functional_classes = dict(FunctionalClass.objects.values_list('value', 'pk'))
        self.genes = dict(Gene.objects.values_list('symbol', 'id'))
        self.transcripts = dict(Transcript.objects.values_list('refseq_id', 'id'))
        self.variants = VariantCache()

        self.skip_existing = kwargs.pop('skip_existing', True)
        self._cache = get_cache(PIPELINE_CACHE_ALIAS)
        self._cache_timeout = 60 * 60 * 24

        super(EffectStream, self).__init__(*args, **kwargs)

        # This is pretty hideous, but to prevent added/removed snpEff fields
        # breaking the code, the labels needs to be mapped to the fields by
        # position. The actual `process_line` method will use the dict to
        # access snpEff values.
        self._snpeff_regex = re.compile(r'(\w+)\s*\((.*)\)')

        # Remove optional fields
        desc = self.reader.infos['EFF'].desc.replace('[ | ERRORS | WARNINGS ]', '')

        # Get available fields, a dict will be created in process_line
        self.snpeff_keys = self._parse_snpeff_row(desc)[1]

    def _parse_snpeff_row(self, row):
        effect, tail = self._snpeff_regex.search(row).groups()
        effect = effect.strip()
        tail = [x.strip() for x in tail.split('|')]
        return effect, tail

    def _snpeff_dict(self, row):
        effect, values = self._parse_snpeff_row(row)
        return effect, dict(zip(self.snpeff_keys, values))

    def get_gene(self, gene_name):
        """Get a gene from the cache or attempt to disambiguate or add a
        new record.
        """
        if not gene_name:
            return

        gene_pk = self.genes.get(gene_name)
        if gene_pk:
            return gene_pk

        chrom = self.chromosomes[self.variants.chrom]
        gene = Gene.objects.find(gene_name, chrom, create=True)
        if gene:
            return gene.pk

    def get_transcript(self, gene_pk, refseq_id):
        "Get a transcript from the cache or add a new record."
        if not refseq_id:
            return
        transcript_pk = self.transcripts.get(refseq_id)
        if transcript_pk:
            return transcript_pk
        gene = Gene(pk=gene_pk)
        transcript = Transcript(refseq_id=refseq_id, gene=gene)
        try:
            transcript.save()
        except IntegrityError:
            transcript = Transcript.objects.get(refseq_id=refseq_id, gene=gene)
        self.transcripts[refseq_id] = transcript.pk
        return transcript.pk

    def _effects_exists(self, md5, variant_id):
        if not self.skip_existing:
            return False

        key = '{0}:effects'.format(md5)
        # If a successful add occurred, this means it is not in the cache,
        # fallback to database check
        if self._cache.add(key, 1, self._cache_timeout):
            return VariantEffect.objects.filter(variant__pk=variant_id).exists()
        return True

    def process_line(self, record):
        # Calculate MD5 using extracted values
        md5 = calculate_md5(record)

        # Ensures the cache is updated and available
        self.variants.ensure_cache(record)

        # Ensure the variant exists
        variant_id = self.variants.get(md5)

        if not variant_id:
            log.error('Missing variant', extra={
                'chr': record.CHROM,
                'pos': record.POS,
                'ref': record.REF,
                'alt': record.ALT,
            })
            return

        # Skip processing effects since they are only loaded once
        if self._effects_exists(md5, variant_id):
            return

        effects = []
        
        #is this returning a list now??
        effects_line = record.INFO['EFF']

        # Multiple separate SNPEff records
        for eff in effects_line:
            effect, values = self._snpeff_dict(eff)

            transcript = values.get('Transcript')
            gene_pk = self.get_gene(values.get('Gene_Name'))

            row = [
                variant_id,
                values.get('Codon_Change'),
                values.get('Amino_acid_change'),
                self.effects.get(effect),
                self.functional_classes.get(values.get('Functional_Class')),
                gene_pk,
                self.get_transcript(gene_pk, transcript),
            ]

            # Extension fields from snpEff CBMi fork
            segment = values.get('Segment')
            hgvs_c = values.get('HGVS_DNA_nomenclature')
            hgvs_p = values.get('HGVS_protein_nomenclature')

            # Trim off transcript prefix, clean up format
            if transcript:
                if segment and segment.startswith(transcript):
                    segment = segment[len(transcript):].strip('._').replace('_', '.')
                if hgvs_c and hgvs_c.startswith(transcript):
                    hgvs_c = hgvs_c[len(transcript):].lstrip(':')

            row.extend([
                segment,
                hgvs_c,
                hgvs_p,
            ])

            effects.append([self.process_column('', x) for x in row])

        if not effects:
            log.error('No effects process for variant', extra={
                'chr': record.CHROM,
                'pos': record.POS,
                'ref': record.REF,
                'alt': record.ALT,
            })

        return effects

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
                    lines = []
                    for c in cleaned:
                        lines.append(self.outdel.join([str(x) for x in c]))
                    return '\n'.join(lines) + '\n'

        return ''
