import logging
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.db import connections, transaction, DEFAULT_DB_ALIAS, DatabaseError
from varify.assessments.models import Assessment

log = logging.getLogger(__name__)


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--database', action='store', dest='database',
                    default=DEFAULT_DB_ALIAS,
                    help='Specifies the target database to delete the sample '
                         'from.'),
    )

    def handle(self, *args, **options):
        if not args:
            raise CommandError('A sample ID must be specified')

        sample_id = args[0]

        if Assessment.objects.filter(
                sample_result__sample_id=sample_id).exists():
            print("This sample cannot be deleted because it has knowledge "
                  "capture data associated with it. If you are absolutely "
                  "sure you want to delete this sample, manually delete the "
                  "knowledge capture data for this sample and then rerun this "
                  "command.")
            return

        database = options.get('database')
        cursor = connections[database].cursor()

        with transaction.commit_manually(database):
            try:
                # Remove sample from cohorts
                cursor.execute('''
                    DELETE FROM cohort_sample WHERE sample_id = %s
                ''', [sample_id])

                # Remove result scores
                cursor.execute('''
                    DELETE FROM result_score WHERE result_id IN
                        (SELECT id from sample_result WHERE sample_id = %s)
                ''', [sample_id])

                # Remove results of sample
                cursor.execute('''
                    DELETE FROM sample_result WHERE sample_id = %s
                ''', [sample_id])

                # Remove runs from sample
                cursor.execute('''
                    DELETE FROM sample_run WHERE sample_id = %s
                ''', [sample_id])

                # Remove sample manifest
                cursor.execute('''
                    DELETE FROM sample_manifest WHERE sample_id = %s
                ''', [sample_id])

                # Remove sample
                cursor.execute('''
                    DELETE FROM sample WHERE sample.id = %s
                ''', [sample_id])

                transaction.commit()
            except DatabaseError:
                transaction.rollback()
                log.exception("Error occurred while deleting sample")
                raise
