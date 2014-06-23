import json
from restlib2.http import codes
from varify.assessments.resources import *  # noqa
from ..base import AuthenticatedBaseTestCase
from varify.phenotypes.models import Phenotype


class PhenotypeResourceTestCase(AuthenticatedBaseTestCase):

    def setUp(self):
        # Create a new phenotype objects and store it
        self.phenotype = Phenotype(term="Hyterazygoze")
        self.phenotype.save()
        super(PhenotypeResourceTestCase, self).setUp()

    def test_get_empty(self):
        response = self.client.get('/api/phenotypes/999/',
                                   HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, codes.not_found)

    def test_get(self):
        # Make a get call again
        response = self.client.get('/api/phenotypes/{0}/'.format(
                                   self.phenotype.id),
                                   HTTP_ACCEPT='application/json')

        # Should be ok and the response should have content
        self.assertEqual(response.status_code, codes.ok)
        self.assertTrue(response.content)

        # Testing phenotype query
        response = self.client.get('/api/phenotypes/',
                                   HTTP_ACCEPT='application/json')
        response_obj = json.loads(response.content)

        # Query should return 1 phenotype and code should be ok
        self.assertEqual(response_obj['result_count'], 1)
        self.assertEqual(response.status_code, codes.ok)
