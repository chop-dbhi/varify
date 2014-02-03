import logging
import time
from optparse import make_option
from django.db import transaction, DEFAULT_DB_ALIAS, DatabaseError
from django.db.models import F, Q
from django.core.management.base import BaseCommand
from varify.samples.models import Cohort

log = logging.getLogger(__name__)


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--database', action='store', dest='database',
                    default=DEFAULT_DB_ALIAS,
                    help='Specifies the target database to load results.'),
        make_option('--force', action='store_true', dest='force',
                    default=False,
                    help='Forces recomputation of all cohort allele '
                         'frequencies')
    )

    def handle(self, **options):
        database = options.get('database')

        if options.get('force'):
            cohorts = list(Cohort.objects.all())
        else:
            cohorts = list(Cohort.objects.filter(
                Q(allele_freq_modified=None) |
                Q(modified__gt=F('allele_freq_modified'))))

        log.debug('Computing for {0} cohorts'.format(len(cohorts)))

        for cohort in cohorts:
            log.debug('"{0}" ({1} samples)...'.format(cohort, cohort.count))

            t0 = time.time()
            with transaction.commit_manually(database):
                try:
                    cohort.compute_allele_frequencies(database)
                    log.debug('done in {0}s\n'.format(int(time.time() - t0)))
                    transaction.commit()
                except DatabaseError, e:
                    transaction.rollback()
                    log.exception(e)
