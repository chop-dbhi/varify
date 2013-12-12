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
                    help='Specifies the target database to delete the proect '
                         'from.'),
        make_option('--remove-metrics', action='store', dest='remove-metrics',
                    default=False, help='Forces the removal of metrics on '
                    'samples, this only applies to production')
    )

    def handle(self, *args, **options):
        if not args:
            raise CommandError('A project ID must be specified')

        project_id = args[0]

        # If any of the samples within the project contain knowledge capture
        # data then refuse to delete the project and notify the user why.
        if Assessment.objects.filter(
                sample_result__sample__project_id=project_id).exists():
            print("This project cannot be deleted because it has knowledge "
                  "capture data associated with samples it contains. If you "
                  "are absolutely sure you want to delete this project, "
                  "manually delete the knowledge capture data on this "
                  "project's samples and then rerun this command.")
            return

        database = options.get('database')
        remove_metrics = options.get('remove-metrics')
        cursor = connections[database].cursor()

        with transaction.commit_manually(database):
            try:
                # Remove all variants in cohorts associated with the project
                cursor.execute('''
                    DELETE FROM cohort_variant WHERE cohort_id IN (
                        SELECT cohort.id FROM cohort INNER JOIN project ON
                            (cohort.project_id = project.id)
                            WHERE project.id = %s
                    )
                ''', [project_id])

                # Remove samples in cohorts associated with the project
                cursor.execute('''
                    DELETE FROM cohort_sample WHERE sample_id IN (
                        SELECT sample.id FROM sample INNER JOIN project ON
                            (sample.project_id = project.id)
                            WHERE project.id = %s
                    )
                ''', [project_id])

                # Remove all cohorts associated with the project
                cursor.execute('''
                    DELETE FROM cohort WHERE project_id = %s
                ''', [project_id])

                # Remove metrics on samples, this only applies to production
                if remove_metrics:
                    cursor.execute('''
                        DELETE FROM metrics_sample_load WHERE sample_id IN (
                            SELECT sample.id FROM sample INNER JOIN project ON
                                (sample.project_id = project.id)
                                WHERE project.id = %s
                        )
                    ''', [project_id])

                # Remove results of samples
                cursor.execute('''
                    DELETE FROM sample_result WHERE sample_id IN (
                        SELECT sample.id FROM sample INNER JOIN project ON
                            (sample.project_id = project.id)
                            WHERE project.id = %s
                    )
                ''', [project_id])

                # Remove runs of samples
                cursor.execute('''
                    DELETE FROM sample_run WHERE sample_id IN (
                        SELECT sample.id FROM sample INNER JOIN project ON
                            (sample.project_id = project.id)
                            WHERE project.id = %s
                    )
                ''', [project_id])

                # Remove sample manifest
                cursor.execute('''
                    DELETE FROM sample_manifest WHERE sample_id IN (
                        SELECT sample.id FROM sample INNER JOIN project ON
                            (sample.project_id = project.id)
                            WHERE project.id = %s
                    )
                ''', [project_id])

                # Remove samples
                cursor.execute('''
                    DELETE FROM sample WHERE project_id = %s
                ''', [project_id])

                # Remove batches
                cursor.execute('''
                    DELETE FROM batch WHERE project_id = %s
                ''', [project_id])

                # Remove the project
                cursor.execute('''
                    DELETE FROM project WHERE id = %s
                ''', [project_id])

                transaction.commit()
            except DatabaseError:
                transaction.rollback()
                log.exception("Error occurred while deleting project")
                raise
