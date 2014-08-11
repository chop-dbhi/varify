from django.test import TestCase
from varify.genes.forms import GeneSetBulkForm
from vdw.genes.models import Gene, GeneSet
from vdw.genome.models import Chromosome


class GeneSetBulkFormTestCase(TestCase):
    def setUp(self):
        import string
        chr1 = Chromosome(value='1', label='1')
        chr1.save()

        genes = {}
        for char in string.lowercase:
            g = Gene(chr=chr1, symbol=char)
            g.save()
            genes[char] = g

        geneset = GeneSet(name='test')
        geneset.save()
        geneset.bulk([genes[c] for c in 'someday'])

        self.genes = genes
        self.geneset = geneset

    def test_errors(self):
        form = GeneSetBulkForm({})
        self.assertFalse(form.is_valid())
        self.assertTrue('genes' in form.errors)

        form = GeneSetBulkForm({'genes': ''})
        self.assertFalse(form.is_valid())
        self.assertTrue('genes' in form.errors)

        form = GeneSetBulkForm({'genes': '    '})
        self.assertFalse(form.is_valid())
        self.assertTrue('genes' in form.errors)

        form = GeneSetBulkForm({'genes': 'XXXXX'})
        self.assertFalse(form.is_valid())
        self.assertTrue('not found' in form.errors['genes'][0])

        form = GeneSetBulkForm({'genes': 'XXXX'}, instance=self.geneset)
        self.assertFalse(form.is_valid())

    def test_success(self):
        form = GeneSetBulkForm({'name': 'Test', 'genes': 'a'})
        self.assertTrue(form.is_valid())
        instance = form.save()
        self.assertEqual(instance.count, 1)
        self.assertTrue(self.genes['a'] in instance)

        # White-space delimited
        form = GeneSetBulkForm({'name': 'Test', 'genes': 'a\nb c\nd\n  e\n\na\n\n'})
        self.assertTrue(form.is_valid())
        instance = form.save()
        self.assertEqual(instance.count, 5)
        self.assertTrue(all([self.genes[c] in instance for c in 'abcde']))

        form = GeneSetBulkForm({'name': 'Test', 'genes': 'a\nb c\nd\n  e\n\na\n\n'}, instance=self.geneset)
        self.assertTrue(form.is_valid())
        self.assertTrue(all([self.genes[c] in form.cleaned_data['genes'] for c in 'abcde']))
        instance = form.save()
        self.assertEqual(instance, self.geneset)
        self.assertEqual(instance.count, 5)
        self.assertTrue(all([self.genes[c] in instance for c in 'abcde']))

    def test_initial(self):
        form = GeneSetBulkForm(instance=self.geneset)
        self.assertEqual(len(form.initial['genes']), 7)
        form = GeneSetBulkForm(initial={'genes': Gene.objects.filter(symbol__in=['a', 'b', 'e', 'g'])})
        self.assertEqual(len(form.initial['genes']), 4)
