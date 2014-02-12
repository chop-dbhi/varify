import logging
import tempfile
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
from optparse import make_option
from django.db import transaction, connections, DEFAULT_DB_ALIAS
from django.core.management.base import BaseCommand
from varify.variants.models import EVS, Sift, ThousandG, PolyPhen2

log = logging.getLogger(__name__)


def _write_tmp(cursor, row_handler=lambda x: x):
    tmp = tempfile.NamedTemporaryFile()
    count = 0

    while True:
        rows = cursor.fetchmany(100)
        if not rows:
            break

        for row in rows:
            row = row_handler(row)
            cleaned = [str(x) if x is not None else '\N' for x in row]
            tmp.write('\t'.join(cleaned) + '\n')
            count += 1

        tmp.flush()
    tmp.seek(0)

    return tmp, count


class Command(BaseCommand):
    """
    Cleans and loads genes from various sources into a uniform set of tables.
    """
    option_list = BaseCommand.option_list + (
        make_option('--database', action='store', dest='database',
                    default=DEFAULT_DB_ALIAS,
                    help='Nominates a database to print the SQL for. Defaults '
                         'to the "default" database.'),
        make_option('--sift', action='store_true', default=False,
                    help='Reload SIFT annotations'),
        make_option('--polyphen2', action='store_true', default=False,
                    help='Reload PolyPhen2 annotations'),
        make_option('--1000g', action='store_true', default=False,
                    help='Reload 1000g annotations'),
        make_option('--evs', action='store_true', default=False,
                    help='Reload EVS annotations'),
        make_option('--truncate', action='store_true', default=False,
                    help='Truncate tables before reloading'),
    )

    def load_1000g(self, cursor, truncate=False):
        db_table = ThousandG._meta.db_table

        if truncate:
            cursor.execute('TRUNCATE "{0}"'.format(db_table))
            log.debug('Truncated table "{0}"'.format(db_table))

        cursor.execute('''
            SELECT DISTINCT ON (variant.id) variant.id, r.an, r.ac, r.af,
                r.aa, r.amr_af, r.asn_af, r.afr_af, r.eur_af
            FROM "variant"
                INNER JOIN "raw"."1000g" r ON ("variant".md5 = r."md5")
                LEFT OUTER JOIN "1000g" ON
                    ("1000g"."variant_id" = "variant"."id")
            WHERE "1000g"."id" IS NULL
            ORDER BY variant.id
        ''')

        tmp, count = _write_tmp(cursor)
        cursor.copy_from(
            tmp, '"1000g"', columns=['variant_id', 'an', 'ac', 'af', 'aa',
                                     'amr_af', 'asn_af', 'afr_af', 'eur_af'])
        tmp.close()
        return count

    load_1000g.short_name = '1000g'

    def load_evs(self, cursor, truncate=False):
        db_table = EVS._meta.db_table

        if truncate:
            cursor.execute('TRUNCATE "{0}"'.format(db_table))
            log.debug('Truncated table "{0}"'.format(db_table))

        # MAFs are divided by 100 since they are percentages to begin with
        cursor.execute('''
            SELECT DISTINCT ON (variant.id) variant.id, r.ea_ac_ref,
                r.ea_ac_alt, r.aa_ac_ref, r.aa_ac_alt, r.all_ac_ref,
                r.all_ac_alt, r.ea_maf / 100.0, r.aa_maf / 100.0,
                r.all_maf / 100.0, r.gts, r.ea_gtc, r.aa_gtc, r.all_gtc,
                r.clinical_association
            FROM "variant"
                INNER JOIN "raw"."evs" r ON ("variant".md5 = r."md5")
                LEFT OUTER JOIN "evs" ON ("evs"."variant_id" = "variant"."id")
            WHERE "evs"."id" IS NULL
            ORDER BY variant.id
        ''')

        # Note, *_af are actually minor allele frequencies by default.
        # The handler checks to see if the reference count is less than
        # the alternate and sets the AF if the reference count is less than
        # the alternate
        columns = ['variant_id', 'ea_ac_ref', 'ea_ac_alt', 'aa_ac_ref',
                   'aa_ac_alt', 'all_ac_ref', 'all_ac_alt', 'ea_af', 'aa_af',
                   'all_af', 'gts', 'ea_gtc', 'aa_gtc', 'all_gtc',
                   'clinical_association']

        def compare_counts(ref, alt):
            "Compares allele counts and handles heterozygotes."
            ref = int(ref)
            for _alt in alt.split(','):
                if ref < int(_alt):
                    return True
            return False

        def row_handler(row):
            record = OrderedDict(zip(columns, row))

            # All
            if compare_counts(record['all_ac_ref'], record['all_ac_alt']):
                record['all_af'] = 1 - record['all_af']

            # European
            if compare_counts(record['ea_ac_ref'], record['ea_ac_alt']):
                record['ea_af'] = 1 - record['ea_af']

            # African American
            if compare_counts(record['aa_ac_ref'], record['aa_ac_alt']):
                record['aa_af'] = 1 - record['aa_af']

            return record.values()

        tmp, count = _write_tmp(cursor, row_handler)
        cursor.copy_from(tmp, 'evs', columns=columns)
        tmp.close()
        return count

    load_evs.short_name = 'EVS'

    def load_polyphen2(self, cursor, truncate=False):
        db_table = PolyPhen2._meta.db_table

        if truncate:
            cursor.execute('TRUNCATE "{0}"'.format(db_table))
            log.debug('Truncated table "{0}"'.format(db_table))

        cursor.execute('''
            SELECT variant.id, r.score, r.refaa
            FROM "variant"
                INNER JOIN "raw"."polyphen2" r ON ("variant".md5 = r."md5")
                LEFT OUTER JOIN "polyphen2" ON
                    ("polyphen2"."variant_id" = "variant"."id")
            WHERE "polyphen2"."id" IS NULL
        ''')

        tmp, count = _write_tmp(cursor)
        cursor.copy_from(tmp, 'polyphen2',
                         columns=['variant_id', 'score', 'refaa'])
        tmp.close()
        return count

    load_polyphen2.short_name = 'PolyPhen2'

    def load_sift(self, cursor, truncate=False):
        db_table = Sift._meta.db_table

        if truncate:
            cursor.execute('TRUNCATE "{0}"'.format(db_table))
            log.debug('Truncated table "{0}"'.format(db_table))

        cursor.execute('''
            SELECT variant.id, r.score, r.refaa, r.varaa
            FROM "variant"
                INNER JOIN "raw"."sift" r ON ("variant".md5 = r."md5")
                LEFT OUTER JOIN "sift" ON
                    ("sift"."variant_id" = "variant"."id")
            WHERE "sift"."id" IS NULL
        ''')

        tmp, count = _write_tmp(cursor)
        cursor.copy_from(tmp, 'sift',
                         columns=['variant_id', 'score', 'refaa', 'varaa'])
        tmp.close()
        return count

    load_sift.short_name = 'SIFT'

    def handle(self, *args, **options):
        using = options.get('database')

        load_1000g = self.load_1000g if options.get('1000g') else None
        load_polyphen2 = \
            self.load_polyphen2 if options.get('polyphen2') else None
        load_evs = self.load_evs if options.get('evs') else None
        load_sift = self.load_sift if options.get('sift') else None
        truncate = options.get('truncate')

        cursor = connections[using].cursor()

        for handler in (load_1000g, load_polyphen2, load_evs, load_sift):
            if not handler:
                continue

            with transaction.commit_manually(using):
                try:
                    log.debug('Loading {0}...'.format(handler.short_name))
                    count = handler(cursor, truncate)
                    log.debug('{0} rows copied'.format(count))
                    transaction.commit()
                except Exception, e:
                    transaction.rollback()
                    log.exception(e.message)
