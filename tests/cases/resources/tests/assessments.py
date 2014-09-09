import json
from restlib2.http import codes
from vdw.assessments.models import Assessment, Pathogenicity,\
    ParentalResult, AssessmentCategory
from vdw.samples.models import Result
from tests.cases.base import AuthenticatedBaseTestCase


class AssessmentResourceTestCase(AuthenticatedBaseTestCase):
    fixtures = ['initial_variants.json']

    def setUp(self):
        self.result = Result.objects.all()[0]
        self.pathogenicity = Pathogenicity.objects.create(name='pathogenic')
        self.parental_result = ParentalResult.objects.create(
            name='heterozygous')
        self.category = AssessmentCategory.objects.create(name='other')
        super(AssessmentResourceTestCase, self).setUp()

    def test_get_empty(self):
        response = self.client.get('/api/assessments/999/',
                                   HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, codes.not_found)

        response = self.client.get('/api/assessments/',
                                   HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, codes.no_content)

    def test_get(self):
        assessment = Assessment.objects.create(
            sample_result=self.result,
            user=self.user,
            assessment_category=self.category,
            sanger_requested=True,
            pathogenicity=self.pathogenicity,
            father_result=self.parental_result,
            mother_result=self.parental_result)

        response = self.client.get(
            '/api/assessments/{0}/'.format(assessment.id),
            HTTP_ACCEPT='application/json')

        self.assertEqual(response.status_code, codes.ok)
        self.assertTrue(response.content)

    def test_post(self):
        count_before = Assessment.objects.count()

        assessment_obj = {
            'sample_result': self.result.id,
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
        # Post should be successful and new object should be added.
        self.assertEqual(response.status_code, codes.created)
        self.assertEqual(Assessment.objects.count(), count_before + 1)

        response = self.client.post('/api/assessments/',
                                    data=json.dumps({}),
                                    content_type='application/json',
                                    HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, codes.unprocessable_entity)

    def test_put(self):
        assessment = Assessment.objects.create(
            sample_result=self.result,
            user=self.user,
            assessment_category=self.category,
            sanger_requested=False,
            pathogenicity=self.pathogenicity,
            father_result=self.parental_result,
            mother_result=self.parental_result)

        # Create a new category to change our assessment.
        new_category = AssessmentCategory.objects.create(name='dangerous')

        assessment_obj = {
            'sample_result': assessment.sample_result.id,
            'user': assessment.user.id,
            'assessment_category': new_category.id,
            'pathogenicity': assessment.pathogenicity.id,
            'father_result': assessment.father_result.id,
            'mother_result': assessment.mother_result.id,
            'sanger_requested': assessment.sanger_requested,
        }

        # Try to change the assessment object's category field.
        response = self.client.put(
            '/api/assessments/{0}/'.format(assessment.id),
            data=json.dumps(assessment_obj), content_type='application/json',
            HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, codes.ok)

        # Confirm that the category changed.
        assessment = Assessment.objects.get(id=assessment.id)
        self.assertEqual(assessment.assessment_category.name, 'dangerous')

        # Make sure an incomplete form causes an error.
        response = self.client.put(
            '/api/assessments/{0}/'.format(assessment.id),
            data=json.dumps({'user': assessment.user.id}),
            content_type='application/json',
            HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, codes.unprocessable_entity)
