from django.db import models
from avocado.lexicon.models import Lexicon


class Chromosome(Lexicon):
    label = models.CharField(max_length=2)
    value = models.CharField(max_length=2, db_index=True)

    class Meta(Lexicon.Meta):
        db_table = 'chromosome'


class Genome(models.Model):
    "Human genome builds."
    name = models.CharField(max_length=200)
    version = models.CharField(max_length=100)
    released = models.DateField(null=True)

    class Meta(object):
        db_table = 'genome'


class Genotype(Lexicon):
    label = models.CharField(max_length=20)
    value = models.CharField(max_length=3)

    class Meta(object):
        db_table = 'genotype'
