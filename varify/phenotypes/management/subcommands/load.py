import re
import logging
from optparse import make_option
from django.db import transaction, connections, DEFAULT_DB_ALIAS
from django.core.management.base import BaseCommand
from varify.genes.models import Gene, GenePhenotype
from varify.literature.models import PubMed
from varify.phenotypes.models import Phenotype
from varify.variants.models import Variant, VariantPhenotype

BATCH_SIZE = 1000

log = logging.getLogger(__name__)


def load_hgmd_phenotypes(label, keys, cursor, using):
    count = 0
    total = 0

    # Local storage for new instances
    pmids = {}
    phenotypes = {}

    while True:
        rows = cursor.fetchmany(100)
        if not rows:
            break

        for row in rows:
            record = dict(zip(keys, row))

            pubmed = gene = variant = None
            new_phenotype = saved = False

            # PubMed IDs
            if record['pubmed_id']:
                pubmed = PubMed(pk=record['pubmed_id'])
                pubmed._state.db = using
            # Some records have a bogus PMID. Only proces the valid ones.
            elif type(record['pubmed']) is int or record['pubmed'].isdigit():
                pmid = int(record['pubmed'])
                if pmid in pmids:
                    pubmed = PubMed(pk=pmids[pmid])
                    pubmed._state.db = using
                else:
                    pubmed = PubMed(pmid=pmid)
                    pubmed.save()
                    pmids[pmid] = pubmed.pk

            # Phenotypes
            if record['phenotype_id']:
                phenotype = Phenotype(pk=record['phenotype_id'])
                phenotype._state.db = using
            else:
                new_phenotype = True
                term = record['phenotype']
                if term in phenotypes:
                    phenotype = Phenotype(pk=phenotypes[term])
                    phenotype._state.db = using
                else:
                    phenotype = Phenotype(term=term)
                    phenotype.save()
                    phenotypes[term] = phenotype.pk

            # Variants
            variant = Variant(pk=record['variant_id'])
            variant._state.db = using
            if new_phenotype or not VariantPhenotype.objects\
                    .filter(variant=variant, phenotype=phenotype,
                            hgmd_id=record['hgmd_id']).exists():
                vp = VariantPhenotype(variant=variant, phenotype=phenotype,
                                      hgmd_id=record['hgmd_id'])
                vp.save()
                saved = True

            # Genes
            if record['gene_id']:
                gene = Gene(pk=record['gene_id'])
                gene._state.db = using

                if new_phenotype or not GenePhenotype.objects\
                        .filter(gene=gene, phenotype=phenotype,
                                hgmd_id=record['hgmd_id']).exists():
                    gp = GenePhenotype(gene=gene, phenotype=phenotype,
                                       hgmd_id=record['hgmd_id'])
                    gp.save()
                    saved = True

            # Associate articles with other objects
            if pubmed:
                phenotype.articles.add(pubmed)
                if variant:
                    variant.articles.add(pubmed)
                if gene:
                    gene.articles.add(pubmed)

            total += 1
            if saved:
                count += 1

                if count % BATCH_SIZE == 0:
                    transaction.commit()

        log.debug('Loading {0}...{1}/{2}'.format(label, count, total))

    # Print a newline for the terminal prompt
    print


class Command(BaseCommand):
    """Cleans and loads phenotype terms from various sources into a uniform
    set of tables.
    """
    option_list = BaseCommand.option_list + (
        make_option('--database', action='store', dest='database',
                    default=DEFAULT_DB_ALIAS, help='Nominates a database to '
                    'print the SQL for.  Defaults to the "default" database.'),
        make_option('--hpo', action='store_true', default=False,
                    help='Reload HPO phenotypes'),
        make_option('--hgmd-snp', action='store_true', default=False,
                    help='Load HGMD phenotypes and associations for SNPs.'),
        make_option('--hgmd-indel', action='store_true', default=False,
                    help='Load HGMD phenotypes and associations for INDELs.'),
    )

    def load_hpo(self, cursor, using):
        keys = ['gene_id', 'hpo_terms']

        # Fetch, parse and load only genes that cleanly map to the gene table.
        # Attempting to join against the synonym table may lead to ambiguity
        # as to which approved gene is the correct one.
        cursor.execute('''
            SELECT "gene"."id", "hpo_terms"
            FROM "raw"."hpo_gene_phenotypes"
                LEFT OUTER JOIN "gene"
                    ON ("entrez_gene_symbol" = "gene"."symbol")
            WHERE "gene"."symbol" IS NOT NULL
        ''')

        phenotype_counter = 1
        gene_phenotype_counter = 1

        phenotype_fout = open('phenotype.txt', 'w+')
        gene_phenotype_fout = open('gene_phenotype.txt', 'w+')

        phenotype_header_keys = ['id', 'term', 'description', 'hpo_id']
        gene_phenotype_header_keys = ['id', 'gene_id', 'phenotype_id']

        phenotype_fout.write('\t'.join(phenotype_header_keys) + '\n')
        gene_phenotype_fout.write('\t'.join(gene_phenotype_header_keys) + '\n')

        phenotype_ids = {}

        hpo_term_re = re.compile('(.*?)\(HP:(\d+)\)$')

        while True:
            rows = cursor.fetchmany(100)
            if not rows:
                break

            for row in rows:
                source_record = dict(zip(keys, row))

                hpo_terms = [hpo_term_re.match(term).groups()
                             for term in source_record['hpo_terms'].split(';')]
                for term, hpo_id in hpo_terms:
                    # Write term as new
                    if hpo_id not in phenotype_ids:
                        phenotype_ids[hpo_id] = phenotype_counter
                        phenotype_fout.write('\t'.join([str(phenotype_counter),
                                             term, '\\N', hpo_id]) + '\n')
                        phenotype_counter += 1
                    gene_phenotype_fout.write('\t'.join([
                        str(gene_phenotype_counter),
                        str(source_record['gene_id']),
                        str(phenotype_ids[hpo_id])
                    ]) + '\n')
                    gene_phenotype_counter += 1

        phenotype_fout.flush()
        gene_phenotype_fout.flush()

        phenotype_fout.seek(0)
        gene_phenotype_fout.seek(0)

        phenotype_fout.readline()
        gene_phenotype_fout.readline()

        cursor.copy_from(phenotype_fout, 'phenotype',
                         columns=phenotype_header_keys)
        cursor.copy_from(gene_phenotype_fout, 'gene_phenotype')

        return phenotype_counter

    load_hpo.short_name = 'HPO'

    def load_hgmd_snp(self, cursor, using=None):
        cursor.execute('''
            select
                hgmd.acc_num,
                variant.id,
                hgmd.disease,
                phenotype.id,
                gene.id as gene_id,
                pubmed.pmid,
                hgmd.pmid
            from (
                select
                    v.id,
                    substr(ve.hgvs_c, 3) as hgvs,
                    c.value as chr,
                    t.refseq_id
                from variant_effect ve
                    inner join transcript t on (ve.transcript_id = t.id)
                    inner join variant v on (ve.variant_id = v.id)
                    inner join chromosome c on (v.chr_id = c.id)
                    inner join variant_type vt on (v.type_id = vt.id)
                where vt.value = 'SNP'
                    and ve.hgvs_c is not null
            ) variant inner join
            (
                select
                    mut.acc_num,
                    trim(both from regexp_replace(mut.disease, '\s*\?$', '')) as disease, # noqa
                    _mut.hgvs,
                    mut.gene,
                    mut.pmid,
                    _mut."refCORE" || '.' || _mut."refVER"::text as refseq_id
                from raw.hgmd_mutation mut
                    inner join raw.hgmd_mutnomen _mut
                        on (mut.acc_num = _mut.acc_num)
                    inner join raw.hgmd_hg19_coords hg19
                        on (mut.acc_num = hg19.acc_num)
                where _mut.hgvs is not null
            ) hgmd on (hgmd.refseq_id = variant.refseq_id
                       and hgmd.hgvs = variant.hgvs)
            left outer join gene on (hgmd.gene = gene.symbol)
            left outer join pubmed on (hgmd.pmid = pubmed.pmid::text)
            left outer join phenotype on (hgmd.disease = phenotype.term)
        ''')

        keys = ['hgmd_id', 'variant_id', 'phenotype', 'phenotype_id',
                'gene_id', 'pubmed_id', 'pubmed']

        load_hgmd_phenotypes('HGMD SNP', keys, cursor, using)

    load_hgmd_snp.short_name = 'HGMD SNP'

    def load_hgmd_indel(self, cursor, using=None):
        # The local variant has some overlap with with the HGMD indel
        # the greater of the two lengths for alt and ref must be used
        # Note, Postgres 9.2 has introduces int8range and && operator which
        # simplifies this logic.
        cursor.execute('''
            select
                HGMD.hgmd_id,
                V.id,
                HGMD.disease,
                phenotype.id,
                gene.id,
                pubmed.pmid,
                HGMD.pmid
            from (
                select
                    v.id,
                    c.value as chr,
                    pos as start,
                    pos + greatest(length(ref), length(alt)) as end
                from variant v
                    inner join chromosome c on (v.chr_id = c.id)
                    inner join variant_type vt on (v.type_id = vt.id)
                where vt.value = 'INDEL'
            ) V inner join
            (
                select
                    m.acc_num as hgmd_id,
                    trim(both from regexp_replace(m.disease, '\s*\?$', ''))
                        as disease,
                    m.gene,
                    m.pmid,
                    c.chromosome as chr,
                    c."coordSTART" as start,
                    c."coordEND" as end
                from raw.hgmd_indel m
                    inner join raw.hgmd_hg19_coords c
                        on (m.acc_num = c.acc_num)
                where m.disease not like '%%?'
            ) HGMD on (V.chr = HGMD.chr and (
                -- overlap
                (V.start <= HGMD.end and V.end >= HGMD.end)
                -- overlap
                or (HGMD.start <= V.end and HGMD.end >= V.end)
                -- V contained in HGMD
                or (V.start >= HGMD.start and V.end <= HGMD.end)
                -- HGMD contain in V
                or (HGMD.start >= V.start and HGMD.end <= V.end)
            ))
            left outer join gene on (HGMD.gene = gene.symbol)
            left outer join pubmed on (HGMD.pmid = pubmed.pmid::text)
            left outer join phenotype
                on (lower(HGMD.disease) = lower(phenotype.term))
        ''')

        keys = ['hgmd_id', 'variant_id', 'phenotype', 'phenotype_id',
                'gene_id', 'pubmed_id', 'pubmed']

        load_hgmd_phenotypes('HGMD INDEL', keys, cursor, using)

    load_hgmd_indel.short_name = 'HGMD INDEL'

    def handle(self, *args, **options):
        using = options.get('database')
        load_hpo = self.load_hpo \
            if options.get('hpo') else None
        load_hgmd_snp = self.load_hgmd_snp \
            if options.get('hgmd_snp') else None
        load_hgmd_indel = self.load_hgmd_indel \
            if options.get('hgmd_indel') else None

        connection = connections[using]
        cursor = connection.cursor()

        for handler in (load_hpo, load_hgmd_snp, load_hgmd_indel):
            if not handler:
                continue

            with transaction.commit_manually(using):
                try:
                    handler(cursor, using)
                    transaction.commit()
                except Exception:
                    transaction.rollback()
                    log.exception(
                        'Failed to load {0}'.format(handler.short_name))
