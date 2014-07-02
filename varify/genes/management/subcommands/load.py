import logging
import re
from optparse import make_option
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
from django.db import connections, DEFAULT_DB_ALIAS
from django.core.management.base import BaseCommand
from varify.genes.models import GeneFamily, Gene, Synonym
from varify.genome.models import Chromosome
from varify.literature.models import PubMed

log = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Cleans and loads genes from various sources into a uniform set of tables.
    """
    option_list = BaseCommand.option_list + (
        make_option('--database', action='store', dest='database',
                    default=DEFAULT_DB_ALIAS,
                    help='Nominates a database to print the SQL for. Defaults '
                         'to the "default" database.'),
        make_option('--genes', action='store_true', default=False,
                    help='Reload genes, synonyms and PubMed IDs from HGNC'),
        make_option('--families', action='store_true', default=False,
                    help='Reload gene families provided by HGNC'),
    )

    def _get_or_create_gene(self, record):
        target = {}

        # Link HGNC id
        target['hgnc_id'] = int(record['hgnc_id'])

        # Parse and map chromosome
        if record['chromosome'] == 'mitochondria':
            target['chr_id'] = self.chromosomes['MT']
        elif ' and ' in record['chromosome']:
            target['chr_id'] = self.chromosomes['XY']
        else:
            match = self.chrom_re.match(record['chromosome'])
            if not match:
                log.warning('unable to match gene chromosome from HGNC',
                            extra={
                                'hgnc_id': record['hgnc_id'],
                                'raw_chr': record['chromosome'],
                            })
                return None, False
            target['chr_id'] = self.chromosomes[match.groups()[0]]

        target['symbol'] = record['approved_symbol'].encode('utf8')
        target['name'] = record['approved_name'].encode('utf8')

        # If the gene already exists by hgnc_id, fetch it. Next check
        # by symbol (in case of a new approved gene) and set the
        # hgnc_id. Fallback to creating a new gene
        try:
            return Gene.objects.get(hgnc_id=target['hgnc_id']), False
        except Gene.DoesNotExist:
            try:
                gene = Gene.objects.get(symbol=target['symbol'])
                gene.hgnc_id = target['hgnc_id']
            except Gene.DoesNotExist:
                gene = Gene(**target)
            gene.save()
            return gene, True

    def _get_or_create_synonym(self, synonym):
        try:
            return Synonym.objects.get(label=synonym), False
        except Synonym.DoesNotExist:
            synonym = Synonym(label=synonym)
            synonym.save()
            return synonym, True

    def _get_or_create_article(self, pmid):
        try:
            return PubMed.objects.get(pmid=pmid), False
        except PubMed.DoesNotExist:
            article = PubMed(pmid=pmid)
            article.save()
            return article, True

    def load_genes(self, cursor):
        # The columns we care about
        keys = ['hgnc_id', 'approved_symbol', 'approved_name',
                'previous_symbols', 'previous_names', 'synonyms',
                'name_synonyms', 'chromosome', 'pubmed_ids']

        cursor.execute('''
            SELECT DISTINCT "hgnc_id", "approved_symbol", "approved_name",
                            "previous_symbols", "previous_names", "synonyms",
                            "name_synonyms", "chromosome", "pubmed_ids"
            FROM "raw"."hgnc"
            WHERE "status" = 'Approved'
                AND "chromosome" != 'reserved'
            ORDER BY "approved_symbol"
        ''')

        self.chromosomes = dict(Chromosome.objects.values_list('value', 'id'))
        self.chrom_re = re.compile(r'^c?([\dXY]{1,2})')

        count = 0
        new_genes = 0
        new_synonyms = 0
        new_articles = 0

        while True:
            rows = cursor.fetchmany(100)
            if not rows:
                break

            for row in rows:
                count += 1
                source_record = OrderedDict(zip(keys, row))

                # Get the gene
                gene, created = self._get_or_create_gene(source_record)

                if not gene:
                    continue

                if created:
                    new_genes += 1

                # Parse alternative symbols and names
                previous_symbols = source_record['previous_symbols'] or ''
                previous_names = source_record['previous_names'] or ''
                synonyms = source_record['synonyms'] or ''
                name_synonyms = source_record['name_synonyms'] or ''

                # Add approved as aliases for ease of querying a single source
                approved = [gene.symbol, gene.name]

                synonyms = ', '.join(
                    [previous_symbols, previous_names, synonyms,
                     name_synonyms]).split(', ') + approved
                for synonym in synonyms:
                    synonym = synonym.strip('" ').encode('utf8')
                    synonym, created = self._get_or_create_synonym(synonym)
                    if created:
                        new_synonyms += 1
                    gene.synonyms.add(synonym)

                # Associate PubMed IDs
                pubmed_ids = source_record['pubmed_ids'] or ''

                for pmid in set(pubmed_ids.split(', ')):
                    try:
                        pmid = int(pmid)
                    except (ValueError, TypeError):
                        continue
                    article, created = self._get_or_create_article(pmid)
                    if created:
                        new_articles += 1
                    gene.articles.add(article)

                log.debug(
                    'scanned: {0}\tgenes: {1}\tsynonyms: {2}\tarticles: {3}'
                    .format(count, new_genes, new_synonyms, new_articles))

    def load_families(self, cursor):
        cursor.execute('''
            SELECT tag, description, gene.id
            FROM raw.hgnc_families
                LEFT OUTER JOIN gene ON (hgnc_families.hgnc_id = gene.hgnc_id)
            ORDER BY tag
        ''')

        keys = ['tag', 'description', 'gene_id']

        families = dict((f.tag, f) for f in GeneFamily.objects.all())

        while True:
            rows = cursor.fetchmany(100)
            if not rows:
                break

            for row in rows:
                record = dict(zip(keys, row))

                if record['tag'] not in families:
                    family = GeneFamily(tag=record['tag'],
                                        description=record['description'])
                    family.save()
                    families[family.tag] = family

                if record['gene_id']:
                    gene = Gene(pk=record['gene_id'])
                    family = families[record['tag']]
                    gene._state.db = family._state.db
                    gene.families.add(family)

    def handle(self, *args, **options):
        using = options.get('database')
        load_genes = options.get('genes')
        load_families = options.get('families')

        connection = connections[using]
        cursor = connection.cursor()

        if not any([load_genes, load_families]):
            log.debug('Nothing to do.')
            return

        if load_genes:
            self.load_genes(cursor)
        if load_families:
            self.load_families(cursor)
