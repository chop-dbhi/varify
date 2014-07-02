import django_rq
import logging
import os
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'varify.conf.settings')

from django.core import management

log = logging.getLogger('recalculate_gene_ranks')

# We don't want this job to run forever so limit to this many attempts and
# if the queue is still not empty just give up.
MAX_ATTEMPTS = 100
# Time in seconds between polling the queue for the current count
POLL_DELAY = 300

queue = django_rq.get_queue('default')

attempts = 0

while attempts < MAX_ATTEMPTS:
    attempts += 1
    if queue.is_empty:
        management.call_command('samples', 'gene-ranks')
        log.debug('gene ranks updated')
        break
    log.debug('queue not empty, waiting {0} seconds'.format(POLL_DELAY))
    time.sleep(POLL_DELAY)
else:
    # Max attempts, log and exit
    log.error('Maximum attempts ({0}) made when trying to update gene ranks.'
              .format(MAX_ATTEMPTS))
