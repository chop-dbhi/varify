import os
import glob
import logging
from optparse import make_option
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import DEFAULT_DB_ALIAS
from varify.samples.pipeline.handlers import load_samples

SAMPLE_DIRS = getattr(settings, 'VARIFY_SAMPLE_DIRS', ())

log = logging.getLogger(__file__)


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--database', action='store', dest='database',
                    default=DEFAULT_DB_ALIAS,
                    help='Specifies the target database loading results.'),
        make_option('--max', action='store', dest='max', default=50,
                    type='int',
                    help='Specifies the maximum number of samples to queue.'),
    )

    def _queue(self, dirs, max_count, database, verbosity):
        count = 0
        skipped = 0
        scanned = 0

        # Walk the directory tree of each sample dirs to find all sample
        # directories with a valid MANIFEST file
        for source in dirs:
            log.debug('Scanning source directory: {0}'.format(source))

            for root, dirs, files in os.walk(source):
                if count == max_count:
                    return count, scanned

                if 'MANIFEST' not in files:
                    continue

                manifest_path = os.path.join(root, 'MANIFEST')

                try:
                    load_dict = load_samples(manifest_path, database)
                except Exception:
                    log.exception('error processing manifest {0}'
                                  .format(manifest_path))
                    continue

                if not load_dict:
                    continue

                count += load_dict['created']
                skipped += load_dict['skipped']
                if load_dict['created'] > 0:
                    if verbosity > 1:
                        log.debug('Queued sample: "{0}"'.format(root))
                elif verbosity > 2:
                    if load_dict['created'] == 0:
                        log.debug('Sample already loaded: "{0}"'.format(root))
                    else:
                        log.debug('Sample skipped: "{0}"'.format(root))

                scanned += 1

                # Print along the way since this is the only output for this
                # verbosity level
                if verbosity == 1:
                    log.debug(
                        "Queued {0} samples (max {1}) {2} skipped of {3} "
                        "scanned".format(count, max_count, skipped, scanned))

        return count, scanned

    def handle(self, *dirs, **options):
        database = options.get('database')
        max_count = options.get('max')
        verbosity = int(options.get('verbosity'))

        if not dirs:
            dirs = []
            for _dir in SAMPLE_DIRS:
                dirs.extend(glob.glob(_dir))

        count, scanned = self._queue(dirs, max_count, database, verbosity)

        if verbosity > 1:
            log.debug('Queued {0} samples (max {1}) of {2} scanned'.format(
                count, max_count, scanned))
        else:
            # Add a newline since the verbosity=1 output is written in-place
            # with a carriage return
            print ''
