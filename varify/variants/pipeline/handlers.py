import os
import logging
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
from django.db import connections, transaction
from varify import db
from varify.variants.models import Variant, VariantEffect, EVS, ThousandG, \
    Sift, PolyPhen2
from varify.pipeline import job, ManifestReader
from varify.pipeline.load import pgcopy_batch
from .utils import VariantStream, EffectStream
from . import VARIANT_CHANNEL

log = logging.getLogger(__name__)


@job(VARIANT_CHANNEL, timeout=60 * 60)
def load_variants(manifest_path, database, **kwargs):
    "Variant loading requires only a VCF file and will never load a duplicate."
    manifest = ManifestReader(manifest_path)

    vcf_info = manifest.section('vcf')

    # No data regarding VCF
    if 'file' not in vcf_info:
        return

    cursor = connections[database].cursor()

    vcf_path = os.path.join(os.path.dirname(manifest_path), vcf_info['file'])

    with open(vcf_path) as fin:
        log.debug("opening {0} in {1}".format(vcf_path, __name__))
        stream = VariantStream(fin)
        columns = stream.output_columns
        db_table = Variant._meta.db_table
        pgcopy_batch(stream, db_table, columns, cursor, database)

    VARIANT_CHANNEL.publish(manifest_path=manifest_path, database=database)


@job(timeout=60 * 60)
def load_effects(manifest_path, database, **kwargs):
    manifest = ManifestReader(manifest_path)

    vcf_info = manifest.section('vcf')

    # No data regarding VCF
    if 'file' not in vcf_info:
        return

    cursor = connections[database].cursor()

    vcf_path = os.path.join(os.path.dirname(manifest_path), vcf_info['file'])

    with open(vcf_path) as fin:
        log.debug("opening {0} in {1} load_effects".format(vcf_path, __name__))
        stream = EffectStream(fin)
        columns = stream.output_columns
        db_table = VariantEffect._meta.db_table
        pgcopy_batch(stream, db_table, columns, cursor, database)


@job
def load_1000g(database, **kwargs):
    if not db.utils.table_exists('1000g', schema='raw'):
        return

    cursor = connections[database].cursor()
    cursor.execute(db.utils.sequence_reset_sql(ThousandG, database))

    with transaction.commit_manually(database):
        try:
            # Get all missing records..
            cursor.execute('''
                INSERT INTO "1000g" (
                    "variant_id", "an", "ac", "af", "aa",
                    "amr_af", "asn_af", "afr_af", "eur_af"
                ) (
                    SELECT variant.id, r.an, r.ac, r.af, r.aa, r.amr_af,
                        r.asn_af, r.afr_af, r.eur_af
                    FROM "variant"
                        INNER JOIN "raw"."1000g" r ON ("variant".md5 = r."md5")
                        LEFT OUTER JOIN "1000g"
                            ON ("1000g"."variant_id" = "variant"."id")
                    WHERE "1000g"."id" IS NULL
                )
            ''')
            transaction.commit()
        except Exception as e:
            transaction.rollback()
            log.exception(e)


@job
def load_sift(database, **kwargs):
    if not db.utils.table_exists('sift', schema='raw'):
        return

    cursor = connections[database].cursor()
    cursor.execute(db.utils.sequence_reset_sql(Sift, database))

    with transaction.commit_manually(database):
        try:
            cursor.execute('''
                INSERT INTO "sift" (
                    "variant_id", "score", "refaa", "varaa"
                ) (
                    SELECT variant.id, r.score, r.refaa, r.varaa
                    FROM "variant"
                        INNER JOIN "raw"."sift" r ON ("variant".md5 = r."md5")
                        LEFT OUTER JOIN "sift"
                            ON ("sift"."variant_id" = "variant"."id")
                    WHERE "sift"."id" IS NULL
                )
            ''')
            transaction.commit()
        except Exception as e:
            transaction.rollback()
            log.exception(e)


@job
def load_polyphen2(database, **kwargs):
    if not db.utils.table_exists('polyphen2', schema='raw'):
        return

    cursor = connections[database].cursor()
    cursor.execute(db.utils.sequence_reset_sql(PolyPhen2, database))

    with transaction.commit_manually(database):
        try:
            cursor.execute('''
                INSERT INTO "polyphen2" (
                    "variant_id", "score", "refaa"
                ) (
                    SELECT variant.id, r.score, r.refaa
                    FROM "variant"
                        INNER JOIN "raw"."polyphen2" r
                            ON ("variant".md5 = r."md5")
                        LEFT OUTER JOIN "polyphen2"
                            ON ("polyphen2"."variant_id" = "variant"."id")
                    WHERE "polyphen2"."id" IS NULL
                )
            ''')
            transaction.commit()
        except Exception as e:
            transaction.rollback()
            log.exception(e)


@job
def load_evs(database, **kwargs):
    if not db.utils.table_exists('evs', schema='raw'):
        return

    cursor = connections[database].cursor()
    cursor.execute(db.utils.sequence_reset_sql(EVS, database))

    with transaction.commit_manually(database):
        try:
            # MAFs are divided by 100 since they are percentages to begin with
            cursor.execute('''
                SELECT variant.id, r.ea_ac_ref, r.ea_ac_alt, r.aa_ac_ref,
                    r.aa_ac_alt, r.all_ac_ref, r.all_ac_alt, r.ea_maf / 100.0,
                    r.aa_maf / 100.0, r.all_maf / 100.0, r.gts, r.ea_gtc,
                    r.aa_gtc, r.all_gtc, r.clinical_association
                FROM "variant"
                    INNER JOIN "raw"."evs" r ON ("variant".md5 = r."md5")
                    LEFT OUTER JOIN "evs"
                        ON ("evs"."variant_id" = "variant"."id")
                WHERE "evs"."id" IS NULL
            ''')

            # Note, *_af are actually minor allele frequencies by default.
            # The handler checks to see if the reference count is less than
            # the alternate and sets the AF if the reference count is less than
            # the alternate
            columns = ['variant_id', 'ea_ac_ref', 'ea_ac_alt', 'aa_ac_ref',
                       'aa_ac_alt', 'all_ac_ref', 'all_ac_alt', 'ea_af',
                       'aa_af', 'all_af', 'gts', 'ea_gtc', 'aa_gtc', 'all_gtc',
                       'clinical_association']

            def compare_counts(ref, alt):
                "Compares allele counts and handles heterozygotes."
                ref = int(ref)
                for _alt in alt.split(','):
                    if ref < int(_alt):
                        return True
                return False

            def handler(row):
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

                cleaned = [str(x) if x is not None else '\N' for x in
                           record.values()]
                return '\t'.join(cleaned) + '\n'

            def streamer(cursor):
                while True:
                    rows = cursor.fetchmany(100)
                    if not rows:
                        break

                    for row in rows:
                        yield handler(row)

            pgcopy_batch(streamer(cursor), EVS._meta.db_table, columns=columns,
                         database=database)

            transaction.commit()
        except Exception as e:
            transaction.rollback()
            log.exception(e)
