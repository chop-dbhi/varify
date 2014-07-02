from django.db import models
from varify.literature.models import PubMed


class Phenotype(models.Model):
    term = models.CharField(max_length=1000, unique=True)
    description = models.TextField(null=True, blank=True)
    hpo_id = models.IntegerField(null=True)

    articles = models.ManyToManyField(PubMed)

    class Meta(object):
        db_table = 'phenotype'


class PhenotypeThrough(models.Model):
    phenotype = models.ForeignKey(Phenotype)
    hgmd_id = models.CharField(max_length=30, null=True, blank=True,
                               db_index=True)

    class Meta(object):
        abstract = True
