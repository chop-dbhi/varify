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

        database = options.get('database')
        cursor = connections[database].cursor()

        invalid_ids = set(Assessment.objects.filter(
            sample_result__sample_id__in=args).values_list(
            'sample_result__sample_id', flat=True))

        if invalid_ids:
            log.warning("Sample(s) with id '{0}' cannot be deleted "
                        "because they have knowledge capture data "
                        "associated with them. If you are absolutely "
                        "sure you want to delete these samples, "
                        "manually delete the knowledge capture data "
                        "for them and then rerun this command."
                        .format(", ".join([str(id) for id in invalid_ids])))

        valid_ids = [id for id in args if id not in invalid_ids]
        columns = ", ".join(['%s' for id in valid_ids])

        if not valid_ids:
            return

        with transaction.commit_manually(database):
            try:
                # Remove sample from cohorts
                cursor.execute('''
                    DELETE FROM cohort_sample WHERE sample_id IN ({0})
                '''.format(columns), valid_ids)

                # Remove result scores
                cursor.execute('''
                    DELETE FROM result_score WHERE result_id IN
                        (SELECT id from sample_result WHERE sample_id IN ({0}))
                '''.format(columns), valid_ids)

                # Remove results of sample
                cursor.execute('''
                    DELETE FROM sample_result WHERE sample_id IN ({0})
                '''.format(columns), valid_ids)

                # Remove runs from sample
                cursor.execute('''
                    DELETE FROM sample_run WHERE sample_id IN ({0})
                '''.format(columns), valid_ids)

                # Remove sample manifest
                cursor.execute('''
                    DELETE FROM sample_manifest WHERE sample_id IN ({0})
                '''.format(columns), valid_ids)

                # Remove sample
                cursor.execute('''
                    DELETE FROM sample WHERE sample.id IN ({0})
                '''.format(columns), valid_ids)

                transaction.commit()
            except DatabaseError:
                transaction.rollback()
                log.exception("Error occurred while deleting sample(s) with "
                              "id '{0}'".format(valid_ids))
                raise
