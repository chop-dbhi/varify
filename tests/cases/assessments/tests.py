import json
import os
from restlib2.http import codes
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

        management.call_command('samples', 'queue')

        worker1 = get_worker('variants')
        worker2 = get_worker('default')

        worker1.work(burst=True)
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

    def test_get_all(self):
        response = self.client.get('/api/assessments/',
                                   HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, codes.no_content)

    def test_get_when_empty(self):
        response = self.client.get('/api/assessments/1/',
                                   HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, codes.not_found)

        sample_id = Sample.objects.values_list('id', flat=True)[0]
        sample_result = Result.objects.filter(sample_id=sample_id)[0]
        assessment = Assessment(sample_result=sample_result, user=self.user,
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

    def test_post(self):
        sample_id = Sample.objects.values_list('id', flat=True)[0]
        sample_result = Result.objects.filter(sample_id=sample_id)[0]
        count_before = Assessment.objects.count()

        assessment_obj = {
            'sample_result': sample_result.id,
            'user': self.user.id,
            'assessment_category': self.category.id,
            'pathogenicity': self.pathogenicity.id,
            'father_result': self.parental_result.id,
            'mother_result': self.parental_result.id,
            'sanger_requested': True,
        }

        response = self.client.post('/api/assessments/',
                                    data=json.dumps(assessment_obj),
                                    content_type='application/json',
                                    HTTP_ACCEPT='application/json')
        # Post should be successful and new object should be added
        self.assertEqual(response.status_code, codes.created)
        self.assertEqual(Assessment.objects.count(), count_before + 1)

        # Testing post with bad value
        response = self.client.post('/api/assessments/',
                                    data=json.dumps({}),
                                    content_type='application/json',
                                    HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, codes.unprocessable_entity)

    def test_put(self):
        sample_id = Sample.objects.values_list('id', flat=True)[0]
        sample_result = Result.objects.filter(sample_id=sample_id)[0]
        assessment = Assessment(sample_result=sample_result,
                                user=self.user,
                                assessment_category=self.category,
                                sanger_requested=False,
                                pathogenicity=self.pathogenicity,
                                father_result=self.parental_result,
                                mother_result=self.parental_result)
        assessment.save()

        # Create a new category to change our assessment
        new_category = AssessmentCategory(name='dangerous')
        new_category.save()

        assessment_obj = {
            'sample_result': assessment.sample_result.id,
            'user': assessment.user.id,
            'assessment_category': new_category.id,
            'pathogenicity': assessment.pathogenicity.id,
            'father_result': assessment.father_result.id,
            'mother_result': assessment.mother_result.id,
            'sanger_requested': assessment.sanger_requested,
        }

        # Try to change the assessment object's category field
        response = self.client.put(
            '/api/assessments/{0}/'.format(assessment.id),
            data=json.dumps(assessment_obj), content_type='application/json',
            HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, codes.ok)

        # Confirm that the category changed
        assessment = Assessment.objects.get(id=assessment.id)
        self.assertEqual(assessment.assessment_category.name, 'dangerous')

        # Make sure an incomplete form causes an error
        response = self.client.put(
            '/api/assessments/{0}/'.format(assessment.id),
            data=json.dumps({'user': assessment.user.id}),
            content_type='application/json',
            HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, codes.unprocessable_entity)
