import json
from restlib2.http import codes
from vdw.genes.models import Gene
from tests.cases.base import AuthenticatedBaseTestCase


class GeneResourceTestCase(AuthenticatedBaseTestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.gene = Gene.objects.get(pk=3)
        super(GeneResourceTestCase, self).setUp()

    def test_get_empty(self):
        # Test get call with bad value.
        response = self.client.get('/api/genes/999/',
                                   HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, codes.not_found)

    def test_get_gene(self):
        response = self.client.get('/api/genes/{0}/'.format(self.gene.id),
                                   HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, codes.ok)
        self.assertTrue(response.content)

        response = self.client.get('/api/genes/',
                                   HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, codes.ok)
        self.assertTrue(response.content)
        resp_obj = json.loads(response.content)
        self.assertEqual(resp_obj['result_count'],
                         Gene.objects.count())

        Gene.objects.all().delete()
        response = self.client.get('/api/genes/',
                                   HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, codes.ok)
        resp_obj = json.loads(response.content)
        self.assertEqual(resp_obj['result_count'], 0)
