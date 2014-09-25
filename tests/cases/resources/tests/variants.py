from restlib2.http import codes
from vdw.genome.models import Chromosome
from vdw.variants.models import Variant, VariantType
from vdw.literature.models import PubMed
from vdw.phenotypes.models import Phenotype
from tests.cases.base import AuthenticatedBaseTestCase


class VariantsResourcesTestCase(AuthenticatedBaseTestCase):
    fixtures = ['initial_variants.json']

    def setUp(self):
        self.pubmed = PubMed.objects.create(pmid=1)
        self.phenotype = Phenotype.objects.create(
            term='Hymocompos', hpo_id=1)
        self.chromo = Chromosome.objects.get(pk=1)
        self.varianttype = VariantType.objects.get(pk=1)

        super(VariantsResourcesTestCase, self).setUp()

    def test_get_empty(self):
        response = self.client.get('/api/variants/999/',
                                   HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, codes.not_found)

    def test_get_all(self):
        new_variant = Variant.objects.create(
            chr=self.chromo,
            pos=1,
            ref='jon',
            alt='ba',
            md5='kid',
            type=self.varianttype,)

        # Now try making a get request with the object's id.
        response = self.client.get('/api/variants/{0}/'.format(new_variant.id),
                                   HTTP_ACCEPT='application/json')

        self.assertEqual(response.status_code, codes.ok)

    def test_get_empty_metrics(self):
        Variant.objects.all().delete()

        response = self.client.get('/api/variants/1/assessment-metrics/',
                                   HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, codes.not_found)

    def test_get_metrics(self):
        new_variant = Variant.objects.create(chr=self.chromo,
                                             pos=1,
                                             ref='jon',
                                             alt='ba',
                                             md5='kid',
                                             type=self.varianttype,)

        response = self.client.get('/api/variants/{0}/assessment-metrics/'.
                                   format(new_variant.id),
                                   HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, codes.ok)
