import logging
import sys
from optparse import make_option
from django.core.management import call_command
from django.core.management.base import BaseCommand
from varify.variants.models import Variant
from varify.samples.models import Priority

log = logging.getLogger(__name__)


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--force', action='store_true', dest='force_update',
                    default=False,
                    help='Force re-prioritization of existing scores'),
        make_option('--database', action='store', dest='database',
                    default=None, help='Specifies the target database.'),
    )

    def handle(self, *args, **options):
        database = options.get('database')
        if not database:
            log.error('A database must be specified.')
            sys.exit(1)
        force_update = options['force_update']
        count = 0

        if force_update:
            variants = Variant.objects.using(database)
        else:
            variants = Variant.objects.using(database).filter(priority=None)

        for variant in variants.iterator():
            try:
                priority = variant.priority
            except Priority.DoesNotExist:
                priority = Priority(variant=variant)

            priority.score = variant.calculate_priority()
            priority.save(using=database)
            count += 1

        if count:
            log.debug('{0} variants prioritized'.format(count))

        call_command('results stats', database=database)
