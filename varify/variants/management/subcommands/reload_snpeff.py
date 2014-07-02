import logging
from optparse import make_option
from django.db import transaction, connections, DEFAULT_DB_ALIAS
from django.core.management.base import BaseCommand
from varify.variants.models import Transcript, VariantEffect
from varify.variants.pipeline.utils import EffectStream
from varify.pipeline.load import pgcopy_batch

log = logging.getLogger(__name__)


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--database', action='store', dest='database',
                    default=DEFAULT_DB_ALIAS,
                    help='Nominates a database to print the SQL for. Defaults '
                         'to the "default" database.'),

        make_option('--transcripts', action='store_true', default=False,
                    help='Causes the transcript table to be truncated prior '
                         'to reloading.'),

        make_option('--stdout', action='store_true', default=False,
                    help='Writes the stream to stdout rather than to the '
                         'database'),
    )

    def handle(self, path, **options):
        database = options.get('database')
        transripts = options.get('transripts')
        stdout = options.get('stdout')

        with open(path) as fin:
            stream = EffectStream(fin, skip_existing=False)

            if stdout:
                while True:
                    line = stream.readline()
                    if line == '':
                        break
                    log.debug(line)
            else:
                cursor = connections[database].cursor()

                with transaction.commit_manually(database):
                    try:
                        cursor.execute('TRUNCATE {0}'.format(
                            VariantEffect._meta.db_table))
                        if transripts:
                            cursor.execute('TRUNCATE {0} CASCADE'.format(
                                Transcript._meta.db_table))
                        columns = stream.output_columns
                        db_table = VariantEffect._meta.db_table
                        pgcopy_batch(stream, db_table, columns, cursor,
                                     database)

                        transaction.commit(database)
                    except Exception as e:
                        transaction.rollback(database)
                        log.exception(e)
                        raise
