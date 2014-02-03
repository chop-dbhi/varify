import gc
import logging
import time
from optparse import make_option
from django.core.management.base import BaseCommand
from annotations.models import PolyPhen2, Sift, ThousandG, EVS
from varify.variants.models import Variant

log = logging.getLogger(__name__)


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--no-input', '-n', action='store_true', dest='no_input',
                    default=False,
                    help='Prevents displaying interactive prompts'),
    )

    def handle(self, *args, **options):
        no_input = options.get('no_input', False)

        from django.db import connection
        quote = connection.ops.quote_name

        db_table = connection.qualified_name(Variant, compose=True)

        updated = 0
        not_updated = 0
        total_count = 0

        conditions = [
            '{0}.{1} IS NULL'.format(db_table, quote('thousandg_id')),
            '{0}.{1} IS NULL'.format(db_table, quote('polyphen2_id')),
            '{0}.{1} IS NULL'.format(db_table, quote('sift_id')),
            '{0}.{1} IS NULL'.format(db_table, quote('evs_id')),
        ]
        missing = '({0})'.format(' OR '.join(conditions))
        variants = \
            Variant.objects.values('id').extra(where=[missing]).distinct()

        if not no_input:
            count = variants.count()
            resp = raw_input('{:,} variants need annotation. Proceed? [y/n] '
                             .format(count))
            if resp.lower() == 'n':
                log.debug('Annotation cancelled')
                return

        t0 = time.time()
        fields = ['pk', 'thousandg', 'polyphen2', 'sift', 'evs', 'md5']
        for variant in variants.only(*fields).iterator():
            has_changed = False
            md5 = variant.md5

            if variant.thousandg_id is None:
                try:
                    variant.thousandg = \
                        ThousandG.objects.only('pk').get(md5=md5)
                    has_changed = True
                except ThousandG.DoesNotExist:
                    pass

            if variant.polyphen2_id is None:
                try:
                    variant.polyphen2 = \
                        PolyPhen2.objects.only('pk').get(md5=md5)
                    has_changed = True
                except PolyPhen2.DoesNotExist:
                    pass

            if variant.sift_id is None:
                try:
                    variant.sift = Sift.objects.only('pk').get(md5=md5)
                    has_changed = True
                except Sift.DoesNotExist:
                    pass

            if variant.evs_id is None:
                try:
                    variant.evs = EVS.objects.only('pk').get(md5=md5)
                    has_changed = True
                except EVS.DoesNotExist:
                    pass

            total_count += 1
            if has_changed:
                variant.save()
                updated += 1
            else:
                not_updated += 1

            if total_count % 100 == 0:
                gc.collect()

        log.debug('Total time:\t{0} seconds'.format(time.time() - t0))
        log.debug('Updated:\t{0:n}'.format(updated))
        log.debug('Not Updated:\t{0:n}'.format(not_updated))
