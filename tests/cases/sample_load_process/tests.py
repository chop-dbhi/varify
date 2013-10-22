import os
from django.db.models import Max
from django.test import TestCase, TransactionTestCase
from django.core import management
from django.core.cache import cache
from django.test.utils import override_settings
from django_rq import get_worker, get_queue, get_connection
from rq.queue import get_failed_queue
from sts.models import System
from varify.chop.models import SampleQc
from varify.samples.models import Project, Batch, Cohort, Sample, SampleManifest, Result
from varify.variants.models import Variant, VariantEffect, Sift, PolyPhen2, ThousandG, EVS
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
        # Immediately validates and creates a sample
        management.call_command('samples', 'queue')

        # Synchronously work on queue
        worker1 = get_worker('variants')
        worker2 = get_worker('default')

        # Ensure sample-related entries are created..
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(Batch.objects.count(), 4)
        self.assertEqual(Sample.objects.count(), 15)

        # World and project cohort..
        self.assertEqual(Cohort.objects.count(), 2)

        # Nothing published yet..
        self.assertEqual(Sample.objects.filter(published=False).count(), 15)
        self.assertEqual(Cohort.objects.filter(count=0, published=False).count(), 2)
        self.assertEqual(Batch.objects.filter(count=0, published=False).count(), 4)

        # Manifests are stored
        self.assertEqual(SampleManifest.objects.count(), 15)
        for manifest in SampleManifest.objects.all():
            self.assertNotEqual(manifest.content, '')
            self.assertFalse(manifest.content_has_changed())

        # Work on variants...
        worker1.work(burst=True)

        self.assertEqual(Variant.objects.count(), 674)

        # Work on effects...
        worker2.work(burst=True)

        self.assertEqual(Gene.objects.count(), 104)
        self.assertEqual(Transcript.objects.count(), 255)
        self.assertEqual(VariantEffect.objects.count(), 1418)

        self.assertEqual(Sift.objects.count(), 0)
        self.assertEqual(PolyPhen2.objects.count(), 0)
        self.assertEqual(ThousandG.objects.count(), 0)
        self.assertEqual(EVS.objects.count(), 0)

        # Results loaded..
        self.assertEqual(Result.objects.count(), 3436)

        # Batches are now published..
        self.assertEqual(Batch.objects.filter(published=True).count(), 3)

        # QC loaded..
        self.assertEqual(SampleQc.objects.count(), 1)

        # Ensure the counts are accurate for each sample..
        for pk, count in [(1, 289), (2, 281), (3, 268), (4, 295), (5, 296), (6, 293), (7, 264), (8, 289), (9, 264), (10, 293), (11, 289), (12, 315)]:
            sample = Sample.objects.get(pk=pk)
            self.assertTrue(sample.published)
            self.assertEqual(sample.count, count)

        # Batches are created with the samples, but are unpublished
        for pk, count in [(1, 5), (2, 3), (3, 4)]:
            batch = Batch.objects.get(pk=pk)
            self.assertTrue(batch.published)
            self.assertEqual(batch.count, count)

        # Ensure the state changes were logged..
        system = System.get(Sample.objects.all()[0])
        self.assertEqual(len(system), 3)


class SnpeffReloadTest(QueueTestCase):
    def test(self):
        "Load a single VCF, reload the snpEff data using the same VCF."
        management.call_command('samples', 'queue', os.path.join(SAMPLE_DIRS[0], 'batch1/sample1'))

        # Synchronously work on queue
        worker1 = get_worker('variants')
        worker2 = get_worker('default')
        worker1.work(burst=True)
        worker2.work(burst=True)

        self.assertEqual(VariantEffect.objects.count(), 614)
        self.assertEqual(VariantEffect.objects.aggregate(max_id=Max('id'))['max_id'], 614)

        management.call_command('variants', 'reload-snpeff', os.path.join(SAMPLE_DIRS[0], 'batch1/sample1/results.vcf'))

        # Ensure data was actually reloaded, check the auto-incremented key
        self.assertEqual(VariantEffect.objects.count(), 614)
        self.assertEqual(VariantEffect.objects.aggregate(max_id=Max('id'))['max_id'], 614 * 2)
