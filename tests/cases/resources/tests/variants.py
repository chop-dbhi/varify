from restlib2.http import codes
from varify.assessments.resources import *  # noqa
from ..base import AuthenticatedBaseTestCase
from varify.genome.models import Chromosome
from varify.variants.models import Variant, VariantType
from varify.literature.models import PubMed
from varify.phenotypes.models import Phenotype


class VariantsResourcesTestCase(AuthenticatedBaseTestCase):
    fixtures = ['initial_data.json']

    def setUp(self):
        # Creating objects needed for variant
        self.pubmed = PubMed(pmid=1)
        self.pubmed.save()
        self.phenotype = Phenotype(term='Hymocompos',
                                   hpo_id=1)
        self.phenotype.save()

        # Retrive a Chromosome and varianttype
        self.chromo = Chromosome.objects.get(pk=1)
        self.chromo.save()

        self.varianttype = VariantType.objects.get(pk=1)
        self.varianttype.save()

        super(VariantsResourcesTestCase, self).setUp()

    def test_get_empty(self):
        response = self.client.get('/api/variants/999/',
                                   HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, codes.not_found)

    def test_get_all(self):
        count_before = Variant.objects.count()
        new_variant = Variant(chr=self.chromo,
                              pos=1,
                              ref="jon",
                              alt="ba",
                              md5="kid",
                              type=self.varianttype,)
        new_variant.save()
        count_after = Variant.objects.count()
        # Now try making a get request with the objects id
        response = self.client.get('/api/variants/{0}/'.format(new_variant.id),
                                   HTTP_ACCEPT='application/json')

        # Request should be good and the count should have changed
        self.assertEqual(response.status_code, codes.ok)
        self.assertEqual(count_after, count_before+1)

    def test_get_empty_metrics(self):
        Variant.objects.all().delete()

        # Bad request, should return 404
        response = self.client.get('/api/variants/1/assessment-metrics/',
                                   HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, codes.not_found)

    def test_get_metrics(self):
        # Create a variant object
        new_variant = Variant(chr=self.chromo,
                              pos=1,
                              ref="jon",
                              alt="ba",
                              md5="kid",
                              type=self.varianttype,)
        new_variant.save()

        response = self.client.get('/api/variants/{0}/assessment-metrics/'.
                                   format(new_variant.id),
                                   HTTP_ACCEPT='application/json')
        # Should be ok
        self.assertEqual(response.status_code, codes.ok)
