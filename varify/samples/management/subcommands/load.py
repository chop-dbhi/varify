from __future__ import division

import logging
import os
import re
import sys
import vcf
import time
import traceback
from optparse import make_option
from ConfigParser import ConfigParser
from django.db import transaction, connections, DEFAULT_DB_ALIAS
from django.core.management.base import BaseCommand
from django.core.management import CommandError
from varify.genome.models import Genotype, Chromosome
from varify.genes.models import Gene, Transcript
from varify.variants.models import VariantType, Variant, VariantEffect, \
    Effect, FunctionalClass
from varify.variants.utils import calculate_md5
from varify.samples.models import Project, Batch, Sample, Result
from varify.samples.metrics.models import SampleLoad

BATCH_SIZE = 1000

log = logging.getLogger(__name__)


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--database', action='store', dest='database',
                    default=DEFAULT_DB_ALIAS,
                    help='Specifies the target database loading results.'),
    )

    def load_batch(self, batch):
        "Performs a bulk save of model instances."
        if not batch:
            return
        model_class = batch[0].__class__
        model_class.objects.bulk_create(batch)

    def clean_value(self, data, key):
        value = data.get(key, None)
        if value == '.':
            value = None
        return value

    def check_cache(self, chrom):
        if not getattr(self, 'chrom', None) or chrom != self.chrom:
            log.debug('Loading cache for chr{0}...'.format(chrom))
            if hasattr(self, 'chrom'):
                transaction.savepoint()
            self.cache_variants(chrom)
            self.chrom = chrom
            log.debug('done')

    def cache_variants(self, chrom):
        "Cache variants by chromosome."
        queryset = Variant.objects.filter(chr__value=chrom)
        self.variant_cache = dict(queryset.values_list('md5', 'id'))

    def cache_genes(self):
        "Cache genes."
        queryset = Gene.objects.all()
        self.gene_cache = dict(queryset.values_list('symbol', 'id'))

    def cache_transcripts(self):
        "Cache transcripts."
        queryset = Transcript.objects.all()
        self.transcript_cache = dict(queryset.values_list('refseq_id', 'id'))

    def get_variant(self, record):
        "Get or create a variant."
        chrom, pos, ref, alt = record.CHROM, record.POS, record.REF, '/'.join(
            [str(x) for x in record.ALT])

        # Calculate MD5 and attempt to fetch the primary key from
        # the local cache, otherwise use it when inserting.
        md5 = calculate_md5(chrom, pos, ref, alt)

        # Ensure the cache is valid for the chromosome
        self.check_cache(chrom)

        variant_id = self.variant_cache.get(md5, None)

        # Just make a faux instance
        if variant_id:
            variant = Variant(pk=variant_id)
        # Create if it does not exist
        else:
            variant = Variant(pos=pos, ref=ref, alt=alt, md5=md5)

            # Update foreign key references
            variant.chr = self.get_chromosome(chrom)
            variant.type = self.get_variant_type(record.var_type.upper())

            # Periods are useless..
            variant.rsid = record.ID == '.' and None or record.ID
            variant.save()
            self.file_variants += 1

            # Update cache
            self.variant_cache[md5] = variant.pk

            # Process SNPEff data if this is the first time this variant
            # has been seen.
            if 'EFF' in record.INFO:
                effs = record.INFO['EFF'].split(',')
                self.load_effects(effs, variant)
        return variant

    def get_gene(self, gene_name):
        """
        Get a gene from the cache or attempt to disambiguate or add a new
        record.
        """
        if not gene_name:
            return

        gene_pk = self.gene_cache.get(gene_name, None)
        if gene_pk:
            return Gene(pk=gene_pk)

        # Attempt to disambiguate, only if this is the only synonym may it be
        # associated.
        potential_genes = list(Gene.objects.filter(
            synonyms__label__iexact=gene_name).distinct())
        if len(potential_genes) == 1:
            self.gene_cache[gene_name] = potential_genes[0].pk
            return potential_genes[0]

        # Only if there are no matches should we create a new record,
        # otherwise the synonym war will continue
        if len(potential_genes) == 0:
            gene = Gene(chr=self.get_chromosome(self.chrom), symbol=gene_name)
            gene.save()
            self.gene_cache[gene_name] = gene.pk
            return gene

    def get_transcript(self, gene, refseq_id):
        "Get a transcript from the cache or add a new record."
        if not refseq_id:
            return

        transcript = self.transcript_cache.get(refseq_id, None)
        if transcript:
            return Transcript(pk=transcript)

        transcript = Transcript(refseq_id=refseq_id, gene=gene)
        transcript.save()
        self.transcript_cache[refseq_id] = transcript.pk
        return transcript

    def load_effects(self, effs, variant):
        # Trivial regex for extracting out the SNPEff data. The pipe-delimited
        # group is split below.
        snpeff_regex = re.compile(r'(\w+)\((.*)\)')

        for eff in effs:
            effect, tail = snpeff_regex.search(eff).groups()
            tail = tail.split('|')

            vareffect = VariantEffect(
                codon_change=tail[2], amino_acid_change=tail[3])

            # Update foreign key references...
            vareffect.effect = self.get_effect(effect)
            vareffect.functional_class = self.get_functional_class(tail[1])
            vareffect.gene = self.get_gene(tail[5])
            vareffect.transcript = self.get_transcript(vareffect.gene, tail[8])
            vareffect.variant = variant

            self.effect_batch.append(vareffect)
            self.effect_batch_size += 1
            self.file_effects += 1

            if self.effect_batch_size == BATCH_SIZE:
                self.load_batch(self.effect_batch)
                self.effect_batch = []
                self.effect_batch_size = 0

    def load_result(self, record, call, sample):
        variant = self.get_variant(record)
        info = record.INFO

        genotype = self.get_genotype(call['GT'])

        # Create result
        result = Result(
            quality=record.QUAL,

            read_depth=getattr(call, 'DP', None),

            genotype=genotype,
            genotype_quality=getattr(call, 'GQ', None),

            coverage_ref=call['AD'][0] if getattr(call, 'AD') else None,
            coverage_alt=call['AD'][1] if getattr(call, 'AD') else None,

            phred_scaled_likelihood=','.join(
                [str(x) for x in getattr(call, 'PL', [])]),

            in_dbsnp=bool(self.clean_value(info, 'DB')),

            downsampling=self.clean_value(info, 'DS'),
            spanning_deletions=self.clean_value(info, 'Dels'),
            mq=self.clean_value(info, 'MQ'),
            mq0=self.clean_value(info, 'MQ0'),
            baseq_rank_sum=self.clean_value(info, 'BaseQRankSum'),
            mq_rank_sum=self.clean_value(info, 'MQRankSum'),
            read_pos_rank_sum=self.clean_value(info, 'ReadPosRankSum'),
            strand_bias=self.clean_value(info, 'SB'),
            homopolymer_run=self.clean_value(info, 'HRun'),
            haplotype_score=self.clean_value(info, 'HaplotypeScore'),
            quality_by_depth=self.clean_value(info, 'QD'),
            fisher_strand=self.clean_value(info, 'FS'),
        )

        result.variant = variant
        result.sample = sample

        self.result_batch.append(result)
        self.result_batch_size += 1
        self.file_results += 1

        if self.result_batch_size == BATCH_SIZE:
            self.load_batch(self.result_batch)
            self.result_batch = []
            self.result_batch_size = 0

    def load_vcf(self, cursor, path):
        "Process and load the VCF file."
        with open(path) as fin:
            log.debug("opening {0} in {1} load_vcf".format(path, __name__))
            reader = vcf.Reader(fin, preserve_order=False)
            for record in reader:
                # No random contigs
                if record.CHROM.startswith('GL'):
                    continue

                # Skip results with a read depth <= 5
                if record.INFO['DP'] < 5:
                    continue

                for sample_colname in record.samples:
                    # We have to honor the column name with multiple columns
                    self.load_result(record, sample_colname)

            # Loading remaining elements in each batch
            self.load_batch(self.result_batch)
            self.load_batch(self.effect_batch)
        return record.samples

    def handle(self, *args, **options):
        if not args:
            raise CommandError('A directory path must be specified.')
        source = args[0]
        using = options.get('database')
        connection = connections[using]
        cursor = connection.cursor()

        # Total time to process all files
        total_t0 = time.time()

        # Total counts across all files
        self.total_variants = 0
        self.total_effects = 0
        self.total_results = 0
        self.total_samples = 0

        # Results and variant effects are batchable since nothing references
        # them. These are shared across all files.
        self.result_batch = []
        self.result_batch_size = 0

        self.effect_batch = []
        self.effect_batch_size = 0

        # Cache genes for fast lookups
        log.debug('Loading all known genes...')
        self.cache_genes()
        log.debug('{0:n}'.format(len(self.gene_cache)))
        log.debug('Loading all known transcripts...')
        self.cache_transcripts()
        log.debug('{0:n}'.format(len(self.transcript_cache)))

        # Walk the source tree and find all directories with a valid MANIFEST
        # file.
        for root, dirs, files in os.walk(source):
            if 'MANIFEST' not in files:
                continue

            parser = ConfigParser()
            parser.read([os.path.join(root, 'MANIFEST')])

            # Light check in case there are other MANIFEST formats encountered
            if (not parser.has_section('general') or
                    not parser.has_section('files')):
                log.warn(
                    'Not a valid MANIFEST in {0}. Skipping...'.format(root))
                continue

            sample_info = dict(parser.items('general'))
            sample_files = dict(parser.items('files'))

            project, created = Project.objects.get_or_create(
                name=sample_info['project'],
                defaults={'label': sample_info['project']})
            batch, created = Batch.objects.get_or_create(
                name=sample_info['cohort'], project=project,
                defaults={'label': sample_info['cohort']})
            file_t0 = time.time()

            self.file_variants = 0
            self.file_results = 0
            self.file_effects = 0

            with transaction.commit_manually(using):
                try:
                    if 'vcf' in sample_files:
                        path = os.path.join(root, sample_files['vcf'])
                        loaded_samples = self.load_vcf(cursor, path)
                        for loaded_sample in loaded_samples:
                            # If not loading all samples get the name from the
                            # manifest.
                            sample, created = Sample.objects.get_or_create(
                                name=loaded_sample, batch=batch,
                                version=int(sample_info['version']),
                                defaults={'label': loaded_sample})

                            sample_name = '{0}.{1}.{2}.{3}'.format(
                                project.name, batch.name, sample.name,
                                sample.version)

                            # This version of the sample has already been
                            # loaded, skip it
                            if not created:
                                log.warn(
                                    'Sample {0} already loaded. Skipping...'
                                    .format(sample_name))
                                continue

                            log.debug('Loading {0}'.format(sample_name))

                            sample.count = self.file_results
                            sample.published = True
                            sample.save()

                        batch.count = \
                            Sample.objects.filter(batch=batch).count()
                        batch.save()
                except Exception:
                    transaction.rollback()
                    sample.delete()
                    traceback.print_exc()
                    sys.exit(1)

                transaction.commit()

            file_time = time.time() - file_t0
            log.debug('Sample time:\t{0:n} seconds'.format(int(file_time)))
            log.debug('Variants:\t{0:n}'.format(self.file_variants))
            log.debug('Effects:\t{0:n}'.format(self.file_effects))
            log.debug('Results:\t{0:n}'.format(self.file_results))

            # Update total counts
            self.total_samples += 1
            self.total_variants += self.file_variants
            self.total_effects += self.file_effects
            self.total_results += self.file_results

            # If something funny happens here, do let it halt the
            # process
            try:
                sampleload = SampleLoad(
                    sample=sample, process_time=file_time,
                    variants=self.file_variants, effects=self.file_effects,
                    results=self.file_results)
                sampleload.process_time_norm = \
                    sampleload.get_process_time_norm()
                sampleload.save()
            except Exception:
                pass

        log.debug('Total time:\t{0:n} seconds'.format(
            int(time.time() - total_t0)))
        log.debug('Samples:\t{0:n}'.format(self.total_samples))
        log.debug('Variants:\t{0:n}'.format(self.total_variants))
        log.debug('Effects:\t{0:n}'.format(self.total_effects))
        log.debug('Results:\t{0:n}'.format(self.total_results))
        log.debug('Avg. Results/Sample:\t{0:n}'.format(
            int(self.total_results / self.total_samples)))

    # Helper methods to return lightweight instances with just their primary
    # key. These are all fixed sets, therefore this should error out if the
    # intended value is not found.
    def get_chromosome(self, value):
        if not value:
            return
        if not hasattr(self, 'chromosomes'):
            self.chromosomes = dict(
                Chromosome.objects.values_list('value', 'pk'))
        return Chromosome(pk=self.chromosomes[value])

    def get_effect(self, value):
        if not value:
            return
        if not hasattr(self, 'effects'):
            self.effects = dict(Effect.objects.values_list('value', 'pk'))
        return Effect(pk=self.effects[value])

    def get_functional_class(self, value):
        if not value:
            return
        if not hasattr(self, 'functional_classes'):
            self.functional_classes = dict(
                FunctionalClass.objects.values_list('value', 'pk'))
        return FunctionalClass(pk=self.functional_classes[value])

    def get_variant_type(self, value):
        if not value:
            return
        if not hasattr(self, 'variant_types'):
            self.variant_types = dict(
                VariantType.objects.values_list('value', 'pk'))
        return VariantType(pk=self.variant_types[value])

    def get_genotype(self, value):
        if not value:
            return
        if not hasattr(self, 'genotypes'):
            self.genotypes = dict(Genotype.objects.values_list('value', 'pk'))
        return Genotype(pk=self.genotypes[value])
