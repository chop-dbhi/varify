import sys
import time
import logging
from optparse import make_option
from django.db import transaction, DEFAULT_DB_ALIAS, DatabaseError
from django.db.models import F, Q
from django.core.management.base import BaseCommand
from varify.samples.models import Cohort

log = logging.getLogger(__name__)


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--database', action='store', dest='database',
            default=DEFAULT_DB_ALIAS, help='Specifies the target database to load results.'),
        make_option('--force', action='store_true', dest='force',
            default=False, help='Forces recomputation of all cohort allele frequencies')
    )

    def handle(self, **options):
        database = options.get('database')

        if options.get('force'):
            cohorts = list(Cohort.objects.all())
        else:
            cohorts = list(Cohort.objects.filter(Q(allele_freq_modified=None) | Q(modified__gt=F('allele_freq_modified'))))

        print 'Computing for {} cohorts'.format(len(cohorts))

        for cohort in cohorts:
            sys.stdout.write('"{}" ({} samples)...'.format(cohort, cohort.count))
            sys.stdout.flush()

            t0 = time.time()
            with transaction.commit_manually(database):
                try:
                    cohort.compute_allele_frequencies(database)
                    sys.stdout.write('done in {}s\n'.format(int(time.time() - t0)))
                    transaction.commit()
                except DatabaseError, e:
                    transaction.rollback()
                    log.exception(e)
