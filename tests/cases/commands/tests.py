import httpretty
import logging
import os
import re
from django.contrib.auth.models import User
from django.core import management
from django.test import TestCase
from django.test.utils import override_settings
from django_rq import get_worker
from requests.exceptions import ConnectionError, RequestException, SSLError
from varify.assessments.models import Assessment, Pathogenicity, \
    ParentalResult, AssessmentCategory
from varify.samples.models import Sample, CohortSample, Result, SampleRun, \
    SampleManifest, Project, Cohort, Batch, CohortVariant, ResultScore
from varify.samples.management.subcommands import gene_ranks
from ..sample_load_process.tests import QueueTestCase
from ...models import MockHandler

TESTS_DIR = os.path.join(os.path.dirname(__file__), '../..')
SAMPLE_DIRS = [os.path.join(TESTS_DIR, 'samples', 'batch1')]


@override_settings(VARIFY_AUTO_CREATE_COHORT=False)
class GeneRanksTestCase(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        # Setup a mock handler
        logger = logging.getLogger(gene_ranks.__name__)
        self.mock_handler = MockHandler()
        logger.addHandler(self.mock_handler)

    def mock_ssl_error(self, request, uri, headers):
        raise SSLError

    def mock_connection_error(self, request, uri, headers):
        raise ConnectionError

    def mock_request_exception(self, request, uri, headers):
        raise RequestException

    def mock_unparseable_terms(self, request, uri, headers):
        json = """{
            "last_modified": "2014-02-27T16:48:39.743363",
            "hpoAnnotations": ["HPO:1", "HPO:2"]
        }"""

        return (200, headers, json)

    def test_missing_settings(self):
        error_log_count = len(self.mock_handler.messages['error'])

        with self.settings(PHENOTYPE_ENDPOINT=None):
            management.call_command('samples', 'gene-ranks')
            self.assertEqual(error_log_count + 1,
                             len(self.mock_handler.messages['error']))

        with self.settings(GENE_RANK_BASE_URL=None):
            management.call_command('samples', 'gene-ranks')
            self.assertEqual(error_log_count + 2,
                             len(self.mock_handler.messages['error']))

        with self.settings(VARIFY_CERT=None):
            management.call_command('samples', 'gene-ranks')
            self.assertEqual(error_log_count + 3,
                             len(self.mock_handler.messages['error']))

        with self.settings(VARIFY_KEY=None):
            management.call_command('samples', 'gene-ranks')
            self.assertEqual(error_log_count + 4,
                             len(self.mock_handler.messages['error']))

        self.assertEqual(ResultScore.objects.count(), 0)

    @httpretty.activate
    def test_url_and_data_errors(self):
        # Setup patches for the mock error responses
        httpretty.register_uri(
            httpretty.GET,
            re.compile("http://localhost/api/tests/connection_error/(.*)/"),
            body=self.mock_connection_error)
        httpretty.register_uri(
            httpretty.GET,
            re.compile("http://localhost/api/tests/request_exception/(.*)/"),
            body=self.mock_request_exception)
        httpretty.register_uri(
            httpretty.GET,
            re.compile("http://localhost/api/tests/ssl_error/(.*)/"),
            body=self.mock_ssl_error)
        httpretty.register_uri(
            httpretty.GET,
            re.compile("http://localhost/api/tests/unparseable_data/(.*)/"),
            body="UNPARSEABLE RESPONSE BODY, JSON EXPECTED")
        httpretty.register_uri(
            httpretty.GET,
            re.compile("http://localhost/api/tests/unparseable_date/(.*)/"),
            body='{"last_modified": "half past noon"}',
            content_type="application/json")
        httpretty.register_uri(
            httpretty.GET,
            re.compile("http://localhost/api/tests/unparseable_terms/(.*)/"),
            body=self.mock_unparseable_terms,
            content_type="application/json")

        # Use a sample we now is present but account for all the possible
        # error results from the real endpoint by using mock error resources.
        with self.settings(PHENOTYPE_ENDPOINT=
                           'http://localhost/api/tests/connection_error/%s/'):
            management.call_command('samples', 'gene-ranks', 'NA12878')

            self.assertTrue(self.mock_handler.messages['error'])
            self.assertTrue("A ConnectionError occurred" in
                            self.mock_handler.messages['error'][-1])

        with self.settings(PHENOTYPE_ENDPOINT=
                           'http://localhost/api/tests/request_exception/%s/'):
            management.call_command('samples', 'gene-ranks', 'NA12878')

            self.assertTrue(self.mock_handler.messages['error'])
            self.assertTrue("The sample has no phenotype data associated" in
                            self.mock_handler.messages['error'][-1])

        with self.settings(PHENOTYPE_ENDPOINT=
                           'http://localhost/api/tests/ssl_error/%s/'):
            management.call_command('samples', 'gene-ranks', 'NA12878')

            self.assertTrue(self.mock_handler.messages['error'])
            self.assertTrue("An SSLError occurred" in
                            self.mock_handler.messages['error'][-1])

        with self.settings(PHENOTYPE_ENDPOINT=
                           'http://localhost/api/tests/unparseable_data/%s/'):
            management.call_command('samples', 'gene-ranks', 'NA12878')

            self.assertTrue(self.mock_handler.messages['error'])
            self.assertTrue("Could not parse response" in
                            self.mock_handler.messages['error'][-1])

        with self.settings(PHENOTYPE_ENDPOINT=
                           'http://localhost/api/tests/unparseable_date/%s/'):
            management.call_command('samples', 'gene-ranks', 'NA12878')

            self.assertTrue(self.mock_handler.messages['warning'])
            self.assertTrue("Could not parse 'last_modified'" in
                            self.mock_handler.messages['warning'][-1])
            self.assertTrue(self.mock_handler.messages['error'])
            self.assertTrue("Response from phenotype missing HPO Annotations"
                            in self.mock_handler.messages['error'][-1])

        with self.settings(PHENOTYPE_ENDPOINT=
                           'http://localhost/api/tests/unparseable_terms/%s/'):
            management.call_command('samples', 'gene-ranks', 'NA12878')

            self.assertTrue(self.mock_handler.messages['warning'])
            self.assertTrue("because it has no HPO terms" in
                            self.mock_handler.messages['warning'][-1])

        # We still shouldn't have any ResultScores as we've been nothing but a
        # failure to this point.
        self.assertEqual(ResultScore.objects.count(), 0)

    def test_load(self):
        # Assert that all the samples we expect to be in the DB are there
        self.assertSequenceEqual(
            Sample.objects.all().values_list('label', flat=True),
            ['NA12878', 'NA12891', 'VPseq004-P-A'])

        management.call_command('samples', 'gene-ranks', 'FAKE')

        # There should be info log messages and the last one should be a
        # report that 0 samples were loaded and 0 were skipped meaning that we
        # didn't do anything because the sample label we passed in was bogus.
        self.assertTrue(self.mock_handler.messages['info'])
        self.assertEqual(self.mock_handler.messages['info'][-1],
                         "Updated 0 and skipped 0 samples")

        self.assertEqual(ResultScore.objects.count(), 0)


@override_settings(VARIFY_SAMPLE_DIRS=SAMPLE_DIRS)
class DeleteTestCase(QueueTestCase):
    def setUp(self):
        super(DeleteTestCase, self).setUp()

        # Immediately validates and creates a sample
        management.call_command('samples', 'queue')

        # Synchronously work on queue
        worker1 = get_worker('variants')
        worker2 = get_worker('default')

        # Work on variants...
        worker1.work(burst=True)

        # Work on effects...
        worker2.work(burst=True)

        # Create and record some data that will be used to create knowledge
        # capture assessments later on.
        self.pathogenicity = Pathogenicity(name='pathogenic')
        self.pathogenicity.save()
        self.parental_result = ParentalResult(name='heterozygous')
        self.parental_result.save()
        self.category = AssessmentCategory(name='other')
        self.category.save()
        self.user = User.objects.all()[0]

    def test_delete(self):
        sample_id = Sample.objects.get(batch__name='batch1', name='NA12891').id

        # Associate some knowledge capture with a sample result for the sample
        # we are trying to delete.
        sample_result = Result.objects.filter(sample_id=sample_id)[0]
        assessment = Assessment(sample_result=sample_result, user=self.user,
                                assessment_category=self.category,
                                sanger_requested=True,
                                pathogenicity=self.pathogenicity,
                                father_result=self.parental_result,
                                mother_result=self.parental_result)
        assessment.save()

        # Since there is an assessment on the sample it should not be deleted
        # by the delete-sample command.
        pre_delete_sample_count = Sample.objects.count()
        management.call_command('samples', 'delete-sample', sample_id)
        self.assertEqual(pre_delete_sample_count, Sample.objects.count())

        # Delete the assessment so that the next delete-sample command issuance
        # will result in the removal of the sample and associated elements.
        Assessment.objects.filter(id=assessment.id).delete()

        # Get the count of all the items we expect to delete with the keys
        # being the table we are deleting from the value being the count we
        # expect to remove.
        sample_counts = {
            'cohort_sample':
            CohortSample.objects.filter(set_object__id=sample_id).count(),
            'sample_result':
            Result.objects.filter(sample__id=sample_id).count(),
            'sample_run':
            SampleRun.objects.filter(sample__id=sample_id).count(),
            'sample_manifest':
            SampleManifest.objects.filter(sample__id=sample_id).count(),
        }

        # Get the initial count of the tables we will be deleting from with
        # the keys being the table we are deleting from and the values being
        # the number of rows initially in the table before the delete command.
        counts = {
            'cohort_sample': CohortSample.objects.count(),
            'sample_result': Result.objects.count(),
            'sample_run': SampleRun.objects.count(),
            'sample_manifest': SampleManifest.objects.count(),
            'sample': Sample.objects.count()
        }

        management.call_command('samples', 'delete-sample', sample_id)

        # Make sure that all the counts after the delete match the initial
        # count less the expected number of deletions.
        self.assertEqual(
            counts['cohort_sample'] - sample_counts['cohort_sample'],
            CohortSample.objects.count())
        self.assertEqual(
            counts['sample_result'] - sample_counts['sample_result'],
            Result.objects.count())
        self.assertEqual(counts['sample_run'] - sample_counts['sample_run'],
                         SampleRun.objects.count())
        self.assertEqual(
            counts['sample_manifest'] - sample_counts['sample_manifest'],
            SampleManifest.objects.count())
        self.assertEqual(counts['sample'] - 1, Sample.objects.count())

        # Check the project delete method here instead of in a new test to
        # prevent a reload of the data from happening.
        project_id = Project.objects.all()[0].id

        # Associate some knowledge capture with a sample result for a sample
        # within the project we are trying to delete.
        sample_result = Result.objects.filter(sample__project_id=project_id)[0]
        assessment = Assessment(sample_result=sample_result, user=self.user,
                                assessment_category=self.category,
                                sanger_requested=True,
                                pathogenicity=self.pathogenicity,
                                father_result=self.parental_result,
                                mother_result=self.parental_result)
        assessment.save()

        # Since there is an assessment on a sample in the project, the project
        # and all samples in it should not be deleted by the delete-project
        # command.
        pre_delete_sample_count = Sample.objects.count()
        pre_delete_project_count = Project.objects.count()
        management.call_command('samples', 'delete-project', project_id)
        self.assertEqual(pre_delete_sample_count, Sample.objects.count())
        self.assertEqual(pre_delete_project_count, Project.objects.count())

        # Delete the assessment so that the next delete-project command
        # issuance will result in the removal of the project and associated
        # elements.
        Assessment.objects.filter(id=assessment.id).delete()

        management.call_command('samples', 'delete-project', project_id)

        # Check that deleting the project cleared out all the rest of
        # the samples and their data.
        self.assertEqual(0, CohortVariant.objects.count())
        self.assertEqual(0, CohortSample.objects.count())
        # We expect 1 cohort remaining because there is a 'World' cohort that
        # is not associated with any project.
        self.assertEqual(1, Cohort.objects.count())
        self.assertEqual(0, Result.objects.count())
        self.assertEqual(0, SampleRun.objects.count())
        self.assertEqual(0, SampleManifest.objects.count())
        self.assertEqual(0, Sample.objects.count())
        self.assertEqual(0, Batch.objects.count())
        self.assertEqual(0, Project.objects.count())
