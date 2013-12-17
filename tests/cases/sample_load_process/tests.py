import os
from django.db.models import Max
from django.test import TestCase, TransactionTestCase
from django.core import management
from django.core.cache import cache
from django.test.utils import override_settings
from django_rq import get_worker, get_queue, get_connection
from rq.queue import get_failed_queue
from sts.models import System
from varify.samples.models import Project, Batch, Cohort, Sample, \
    SampleManifest, Result
from varify.variants.models import Variant, VariantEffect, Sift, PolyPhen2, \
    ThousandG, EVS
from varify.variants.pipeline.utils import VariantCache
from varify.genes.models import Transcript, Gene

TESTS_DIR = os.path.join(os.path.dirname(__file__), '../..')
SAMPLE_DIRS = [os.path.join(TESTS_DIR, 'samples')]


class QueueTestCase(TransactionTestCase):
    def setUp(self):
        cache.clear()
        get_queue('variants').empty()
        get_queue('default').empty()
        get_failed_queue(get_connection()).empty()


class VariantCacheTestCase(TestCase):
    def setUp(self):
        self.vcache = VariantCache()
        self.vcache._cache.clear()

    def test(self):
        # Not in there..
        self.assertFalse('1234' in self.vcache)
        # ..but stores a placholder
        self.assertTrue('1234' in self.vcache)


@override_settings(VARIFY_SAMPLE_DIRS=SAMPLE_DIRS)
class SampleLoadTestCase(QueueTestCase):
    def test_pipeline(self):
        expected_counts = {
            'batches': 2,
            'cohorts': 2,
            'genes': 65,
            'projects': 1,
            'results_per_sample': [
                {
                    'batch': 'batch1',
                    'sample': 'NA12891',
                    'count': 1963,
                },
                {
                    'batch': 'batch1',
                    'sample': 'NA12892',
                    'count': 1963,
                },
                {
                    'batch': 'batch1',
                    'sample': 'NA12878',
                    'count': 1963,
                },
                {
                    'batch': 'batch2',
                    'sample': 'NA12891',
                    'count': 2094,
                },
                {
                    'batch': 'batch2',
                    'sample': 'NA12892',
                    'count': 2094,
                },
                {
                    'batch': 'batch2',
                    'sample': 'NA12878',
                    'count': 2094,
                },
            ],
            'samples': 6,
            'transcripts': 108,
            'variant_effects': 8788,
            'variants': 4057,
            'samples_per_batch': [(1, 3), (2, 3)],
        }
        expected_counts['results'] = \
            sum([x['count'] for x in expected_counts['results_per_sample']])

        # Immediately validates and creates a sample
        management.call_command('samples', 'queue')

        # Synchronously work on queue
        worker1 = get_worker('variants')
        worker2 = get_worker('default')

        # Ensure sample-related entries are created..
        self.assertEqual(Project.objects.count(), expected_counts['projects'])
        self.assertEqual(Batch.objects.count(), expected_counts['batches'])
        self.assertEqual(Sample.objects.count(), expected_counts['samples'])

        # World and project cohort..
        self.assertEqual(Cohort.objects.count(), expected_counts['cohorts'])

        # Nothing published yet..
        self.assertEqual(Sample.objects.filter(published=False).count(),
                         expected_counts['samples'])
        self.assertEqual(
            Cohort.objects.filter(count=0, published=False).count(),
            expected_counts['cohorts'])
        self.assertEqual(
            Batch.objects.filter(count=0, published=False).count(),
            expected_counts['batches'])

        # Manifests are stored
        self.assertEqual(SampleManifest.objects.count(),
                         expected_counts['samples'])
        for manifest in SampleManifest.objects.all():
            self.assertNotEqual(manifest.content, '')
            self.assertFalse(manifest.content_has_changed())

        # Work on variants...
        worker1.work(burst=True)

        self.assertEqual(Variant.objects.count(), expected_counts['variants'])

        # Work on effects...
        worker2.work(burst=True)

        self.assertEqual(Gene.objects.count(), expected_counts['genes'])
        self.assertEqual(Transcript.objects.count(),
                         expected_counts['transcripts'])
        self.assertEqual(VariantEffect.objects.count(),
                         expected_counts['variant_effects'])

        self.assertEqual(Sift.objects.count(), 0)
        self.assertEqual(PolyPhen2.objects.count(), 0)
        self.assertEqual(ThousandG.objects.count(), 0)
        self.assertEqual(EVS.objects.count(), 0)

        # Results loaded..
        self.assertEqual(Result.objects.count(), expected_counts['results'])

        # Batches are now published..
        self.assertEqual(Batch.objects.filter(published=True).count(),
                         expected_counts['batches'])

        # Ensure the counts are accurate for each sample..
        for ec in expected_counts['results_per_sample']:
            sample = Sample.objects.get(name=ec['sample'],
                                        batch__name=ec['batch'])
            self.assertTrue(sample.published)
            self.assertEqual(sample.count, ec['count'])

        # Batches are created with the samples, but are unpublished
        for pk, count in expected_counts['samples_per_batch']:
            batch = Batch.objects.get(pk=pk)
            self.assertTrue(batch.published)
            self.assertEqual(batch.count, count)

        # Ensure the state changes were logged..
        system = System.get(Sample.objects.all()[0])
        self.assertEqual(len(system), 3)


class SnpeffReloadTest(QueueTestCase):
    def test(self):
        "Load a single VCF, reload the snpEff data using the same VCF."
        management.call_command('samples', 'queue',
                                os.path.join(SAMPLE_DIRS[0], 'batch1/locus_1'))

        # Synchronously work on queue
        worker1 = get_worker('variants')
        worker2 = get_worker('default')
        worker1.work(burst=True)
        worker2.work(burst=True)

        expected_variant_effects_count = 5426

        self.assertEqual(VariantEffect.objects.count(),
                         expected_variant_effects_count)
        self.assertEqual(
            VariantEffect.objects.aggregate(max_id=Max('id'))['max_id'],
            expected_variant_effects_count)

        management.call_command('variants', 'reload-snpeff',
                                os.path.join(SAMPLE_DIRS[0],
                                             'batch1/locus_1/locus_1.vcf'))

        # Ensure data was actually reloaded, check the auto-incremented key
        self.assertEqual(VariantEffect.objects.count(),
                         expected_variant_effects_count)

        # Since we reloaded, we should now have double the number of expected
        # results, thus the 2 * operation in the assertion below.
        self.assertEqual(
            VariantEffect.objects.aggregate(max_id=Max('id'))['max_id'],
            2 * expected_variant_effects_count)
