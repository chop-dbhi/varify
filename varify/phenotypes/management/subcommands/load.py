import re
import sys
import logging
from optparse import make_option
from django.db import transaction, connections, DEFAULT_DB_ALIAS
from django.core.management.base import BaseCommand
from varify.genome.models import Chromosome
from varify.genes.models import Gene, GenePhenotype
from varify.literature.models import PubMed
from varify.phenotypes.models import Phenotype
from varify.variants.models import Variant, VariantPhenotype


log = logging.getLogger(__name__)


class Command(BaseCommand):
    """Cleans and loads phenotype terms from various sources into a uniform
    set of tables.
    """
    option_list = BaseCommand.option_list + (
        make_option('--database', action='store', dest='database',
            default=DEFAULT_DB_ALIAS, help='Nominates a database to print the '
                'SQL for.  Defaults to the "default" database.'),
        make_option('--hpo', action='store_true', default=False,
            help='Reload HPO phenotypes'),
        make_option('--hgmd-snp', action='store_true', default=False,
            help='Load HGMD phenotypes and associations for SNPs.'),
    )

    def load_hpo(self, cursor):
        keys = ['gene_id', 'hpo_terms']

        # Fetch, parse and load only genes that cleanly map to the gene table.
        # Attempting to join against the synonym table may lead to ambiguity
        # as to which approved gene is the correct one.
        cursor.execute('''
            SELECT "gene"."id", "hpo_terms"
            FROM "raw"."hpo_gene_phenotypes"
                LEFT OUTER JOIN "gene" ON ("entrez_gene_symbol" = "gene"."symbol")
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

                hpo_terms = [hpo_term_re.match(term).groups() for term in source_record['hpo_terms'].split(';')]
                for term, hpo_id in hpo_terms:
                    # Write term as new
                    if hpo_id not in phenotype_ids:
                        phenotype_ids[hpo_id] = phenotype_counter
                        phenotype_fout.write('\t'.join([str(phenotype_counter), term, '\\N', hpo_id]) + '\n')
                        phenotype_counter += 1
                    gene_phenotype_fout.write('\t'.join([str(gene_phenotype_counter), str(source_record['gene_id']), str(phenotype_ids[hpo_id])]) + '\n')
                    gene_phenotype_counter += 1

        phenotype_fout.flush()
        gene_phenotype_fout.flush()

        phenotype_fout.seek(0)
        gene_phenotype_fout.seek(0)

        phenotype_fout.readline()
        gene_phenotype_fout.readline()

        cursor.copy_from(phenotype_fout, 'phenotype', columns=phenotype_header_keys)
        cursor.copy_from(gene_phenotype_fout, 'gene_phenotype')

        return phenotype_counter
    load_hpo.short_name = 'HPO'


    def load_hgmd_snp(self, cursor, using=None):
        cursor.execute('''
            select distinct
                cl.acc_num as hgmd_id,
                c.value as chr,
                c.id as chr_id,
                v.id as variant_id,
                trim(both from cl.disease) as phenotype,
                ph.id as phenotype_id,
                cl.gene as gene,
                g.id as gene_id,
                cl.pmid as pubmed,
                pm.pmid as pubmed_id
            from (
                select m.acc_num, m.disease, m.gene, m.pmid, c.chromosome, c."coordSTART" as pos
                    from raw.hgmd_mutation m inner join raw.hgmd_hg19_coords c on (m.acc_num = c.acc_num)
            ) cl
                left outer join chromosome c on (cl.chromosome = c.value)
                left outer join variant v on (c.id = v.chr_id and cl.pos = v.pos)
                left outer join variant_type vt on (v.type_id = vt.id)
                left outer join phenotype ph on (lower(trim(both from regexp_replace(cl.disease, '\s*\?$', ''))) = lower(ph.term))
                left outer join pubmed pm on (cl.pmid::varchar = pm.pmid::varchar)
                left outer join gene g on (cl.gene::text = g.symbol::text)
                left outer join variant_phenotype vp on (vp.variant_id = v.id)
            where vt.value = 'SNP'
                and cl.disease not like '%%?'
                and v.id is not null and g.id is not null
            order by c.id
        ''')

        keys = ['hgmd_id', 'chr', 'chr_id', 'variant_id',
            'phenotype', 'phenotype_id', 'gene', 'gene_id',
            'pubmed', 'pubmed_id']

        count = 0
        new_pubmed_map = {}
        new_phenotype_map = {}

        chrs = dict(Chromosome.objects.values_list('value', 'id'))

        while True:
            rows = cursor.fetchmany(100)
            if not rows:
                break

            for row in rows:
                record = dict(zip(keys, row))

                # Get or create a pubmed record
                if record['pubmed_id']:
                    pubmed = PubMed(pmid=record['pubmed_id'])
                    pubmed._state.db = using
                # Some records have a bogus PMID. Only proces the valid ones.
                elif type(record['pubmed']) is int or record['pubmed'].isdigit():
                    pmid = int(record['pubmed'])
                    if pmid in new_pubmed_map:
                        pubmed = new_pubmed_map[pmid]
                    else:
                        pubmed = PubMed(pmid=pmid)
                        pubmed.save()
                        new_pubmed_map[pmid] = pubmed
                else:
                    pubmed = None

                # Get or create a the phenotype, associate the HGMD id with
                if record['phenotype_id']:
                    phenotype = Phenotype(pk=record['phenotype_id'])
                    phenotype._state.db = using
                else:
                    term = record['phenotype']
                    # Check newly added objects
                    if term in new_phenotype_map:
                        phenotype = new_phenotype_map[term]
                    else:
                        phenotype = Phenotype(term=record['phenotype'])
                        phenotype.save()
                        new_phenotype_map[term] = phenotype

                _chr = Chromosome(pk=chrs[record['chr']])
                _chr._state.db = using

                if record['gene_id']:
                    gene = Gene(pk=record['gene_id'])
                    gene._state.db = using

                    try:
                        gp = GenePhenotype.objects.get(gene=gene, phenotype=phenotype)
                    except GenePhenotype.DoesNotExist:
                        gp = GenePhenotype(gene=gene, phenotype=phenotype)
                    gp.hgmd_id = record['hgmd_id']
                    gp.save()
                else:
                    gene = None

                if record['variant_id']:
                    variant = Variant(pk=record['variant_id'])
                    variant._state.db = using

                    try:
                        vp = VariantPhenotype.objects.get(variant=variant, phenotype=phenotype)
                    except VariantPhenotype.DoesNotExist:
                        vp = VariantPhenotype(variant=variant, phenotype=phenotype)
                    vp.hgmd_id = record['hgmd_id']
                    vp.save()
                else:
                    variant = None

                if pubmed:
                    phenotype.articles.add(pubmed)
                    if variant:
                        variant.articles.add(pubmed)
                    if gene:
                        gene.articles.add(pubmed)

                count += 1

            sys.stdout.write('{0}\r'.format(count))
            sys.stdout.flush()

        return count
    load_hgmd_snp.short_name = 'HGMD SNP'


    def handle(self, *args, **options):
        using = options.get('database')
        load_hpo = self.load_hpo if options.get('hpo') else None
        load_hgmd_snp = self.load_hgmd_snp if options.get('hgmd_snp') else None

        connection = connections[using]
        cursor = connection.cursor()

        for handler in (load_hpo, load_hgmd_snp):
            if not handler:
                continue

            with transaction.commit_manually(using):
                try:
                    print 'Loading {0}...'.format(handler.short_name),
                    sys.stdout.flush()
                    count = handler(cursor, using)
                    print '{0} rows copied'.format(count)
                    transaction.commit()
                except Exception, e:
                    print 'FAIL'
                    transaction.rollback()
                    log.exception(e.message)
