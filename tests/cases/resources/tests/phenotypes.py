import json
from restlib2.http import codes
from vdw.phenotypes.models import Phenotype
from tests.cases.base import AuthenticatedBaseTestCase


class PhenotypeResourceTestCase(AuthenticatedBaseTestCase):
    def setUp(self):
        # Create a new phenotype objects and store it.
        self.phenotype = Phenotype.objects.create(term='Hyterazygoze')
        super(PhenotypeResourceTestCase, self).setUp()

    def test_get_empty(self):
        response = self.client.get('/api/phenotypes/999/',
                                   HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, codes.not_found)

    def test_get(self):
        response = self.client.get('/api/phenotypes/{0}/'.format(
                                   self.phenotype.id),
                                   HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, codes.ok)
        self.assertTrue(response.content)

        response = self.client.get('/api/phenotypes/',
                                   HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, codes.ok)
        response_obj = json.loads(response.content)

        self.assertEqual(response_obj['result_count'], 1)
