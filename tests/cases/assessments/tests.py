import json
import os
from restlib2.http import codes
from varify.assessments.resources import *  # noqa
from ..base import AuthenticatedBaseTestCase
from django.test.utils import override_settings
from varify.assessments.models import Assessment, Pathogenicity,\
    ParentalResult, AssessmentCategory
from varify.samples.models import Sample, Result
from django.core import management
from django_rq import get_worker
from django.core.cache import cache
from django_rq import get_queue, get_connection
from rq.queue import get_failed_queue

TESTS_DIR = os.path.join(os.path.dirname(__file__), '../..')
SAMPLE_DIRS = [os.path.join(TESTS_DIR, 'samples', 'batch1')]


@override_settings(VARIFY_SAMPLE_DIRS=SAMPLE_DIRS)
class AssessmentResourceTestCase(AuthenticatedBaseTestCase):

    def setUp(self):
        cache.clear()
        get_queue('variants').empty()
        get_queue('default').empty()
        get_failed_queue(get_connection()).empty()

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
        super(AssessmentResourceTestCase, self).setUp()

    # Test the get method of class AssessmentsResources
    def test_get_all(self):
        response = self.client.get('/api/assessments/',
                                   HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, codes.no_content)

    # Test get method with empty assessment
    def test_get_when_empty(self):
        response = self.client.get('/api/assessments/1/',
                                   HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, codes.not_found)

        sample_id = Sample.objects.get(batch__name='batch1', name='NA12891').id
        # Create an assessment, then try another get call
        sample_result = Result.objects.filter(sample_id=sample_id)[0]
        assessment = Assessment(sample_result=sample_result,
                                user=self.user,
                                assessment_category=self.category,
                                sanger_requested=True,
                                pathogenicity=self.pathogenicity,
                                father_result=self.parental_result,
                                mother_result=self.parental_result)
        assessment.save()

        response = self.client.get('/api/assessments/1/',
                                   HTTP_ACCEPT='application/json')

        self.assertEqual(response.status_code, codes.ok)
        self.assertTrue(response.content)

    # Test post method
    def test_post_all(self):
        sample_id = Sample.objects.get(batch__name='batch1', name='NA12891').id
        # First create an assessment object in json format
        sample_result = Result.objects.filter(sample_id=sample_id)[0]
        count_before = Assessment.objects.count()

        # Create a json to pass in
        assessment_obj = {"sample_result": sample_result.id,
                          "user": self.user.id,
                          "assessment_category": self.category.id,
                          "pathogenicity": self.pathogenicity.id,
                          "father_result": self.parental_result.id,
                          "mother_result": self.parental_result.id,
                          "sanger_requested": True, }

        # Testing a regular post
        response = self.client.post('/api/assessments/',
                                    data=json.dumps(assessment_obj),
                                    content_type='application/json',
                                    HTTP_ACCEPT='application/json')
        count_after = Assessment.objects.count()
        # Post should be successful and new object should be added
        self.assertEqual(response.status_code, codes.created)
        self.assertEqual(count_after, count_before+1)

        # Testing post with bad value
        response = self.client.post('/api/assessments/',
                                    data=json.dumps({}),
                                    content_type='application/json',
                                    HTTP_ACCEPT='application/json')
        # Should be unprocessable
        self.assertEqual(response.status_code, codes.unprocessable_entity)

    #  Testing PUT call
    def test_put(self):
        # First create an assessment object
        sample_id = Sample.objects.get(batch__name='batch1', name='NA12891').id

        sample_result = Result.objects.filter(sample_id=sample_id)[0]
        assessment = Assessment(sample_result=sample_result,
                                user=self.user,
                                assessment_category=self.category,
                                sanger_requested=False,
                                pathogenicity=self.pathogenicity,
                                father_result=self.parental_result,
                                mother_result=self.parental_result)
        assessment.save()
        # Get id for the put request and get count
        a_id = str(assessment.id)
        count_before = Assessment.objects.count()

        # Create a new category to change our assessment
        new_category = AssessmentCategory(name='dangerous')
        new_category.save()

        # Make the json object with the same values (except for the category)
        assessment_obj = {"sample_result": assessment.id,
                          "user": assessment.user.id,
                          "assessment_category": new_category.id,
                          "pathogenicity": assessment.pathogenicity.id,
                          "father_result": assessment.father_result.id,
                          "mother_result": assessment.mother_result.id,
                          "sanger_requested": False, }

        # Try to change the assessment object's category field
        response = self.client.put('/api/assessments/{0}/'.format(a_id),
                                   data=json.dumps(assessment_obj),
                                   content_type='application/json',
                                   HTTP_ACCEPT='application/json')
        count_after = Assessment.objects.count()

        # Tests, object should be changed, count should be same
        self.assertEqual(response.status_code, codes.ok)

        # Now retrive the same object
        response = self.client.get('/api/assessments/{0}/'.format(a_id),
                                   HTTP_ACCEPT='application/json')

        # The category should have changed to dangerous
        if 'dangerous' not in response.content:
            raise AssertionError("object changed!")
        # Count should remain the same
        self.assertEquals(count_before, count_after)
