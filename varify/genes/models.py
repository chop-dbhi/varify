from django.db import models
from django.contrib.auth.models import User
from objectset.models import ObjectSet, SetObject
from varify.literature.models import PubMed
from varify.genome.models import Chromosome
from varify.phenotypes.models import Phenotype, PhenotypeThrough
from .managers import GeneManager


class GeneFamily(models.Model):
    "Gene family tags and descriptions."
    tag = models.CharField(max_length=30, null=True)
    description = models.CharField(max_length=200, null=True)

    class Meta(object):
        db_table = 'gene_family'


class Synonym(models.Model):
    """Model which contains known alternate gene names and symbols for
    the canonical genes. This can be used as an index for search-related
    queries.
    """
    # Call it a label since this may be a symbol, a name or something else
    label = models.CharField(max_length=255, db_index=True)

    class Meta(object):
        db_table = 'synonym'


class Gene(models.Model):
    """Unified gene model. This includes data from multiple sources with
    the appropriate `id` defined to which references the source. If multiple
    sources contain have overlap, the respective `id`s will be filled in.

    The canonical source is HGNC, which approves gene names and symbols, the
    `approved` flag should be set if this is the approved gene name and
    symbol by HGNC.
    """
    chr = models.ForeignKey(Chromosome)
    symbol = models.CharField(max_length=255, db_index=True)
    name = models.TextField('full name', blank=True)
    hgnc_id = models.IntegerField('HGNC ID', null=True, blank=True)

    # Via the HGNC documentation: "Families/groups may be either structural or
    # functional, therefore a gene may belong to more than one family/group"
    families = models.ManyToManyField(GeneFamily, blank=True)

    # Literature
    articles = models.ManyToManyField(PubMed, db_table='gene_pubmed')

    # Synonyms
    synonyms = models.ManyToManyField(Synonym, db_table='gene_synonym')

    # Phenotypes
    phenotypes = models.ManyToManyField(Phenotype, through='GenePhenotype')

    objects = GeneManager()

    class Meta(object):
        db_table = 'gene'

    def __unicode__(self):
        return self.symbol

    def approved(self):
        return self.hgnc_id is not None

    def hgnc_url(self):
        if self.hgnc_id:
            return 'http://www.genenames.org/data/hgnc_data.php?hgnc_id=' + \
                str(self.hgnc_id)


class GenePhenotype(PhenotypeThrough):
    gene = models.ForeignKey(Gene)

    class Meta(object):
        db_table = 'gene_phenotype'


class Exon(models.Model):
    "Gene-specific exon region"
    gene = models.ForeignKey(Gene)
    index = models.IntegerField('exon index')
    start = models.IntegerField('exon start position')
    end = models.IntegerField('exon end position')

    class Meta(object):
        db_table = 'exon'


class Transcript(models.Model):
    "Gene transcripts"
    refseq_id = models.CharField(max_length=100, unique=True)
    strand = models.CharField(max_length=1, null=True, blank=True,
                              help_text='+ or - for strand')
    start = models.IntegerField('transcript start position', null=True,
                                blank=True)
    end = models.IntegerField('transcript end position', null=True, blank=True)
    coding_start = models.IntegerField('coding region start position',
                                       null=True, blank=True)
    coding_end = models.IntegerField('coding region end position', null=True,
                                     blank=True)
    coding_start_status = models.CharField('coding region start status',
                                           max_length=20, null=True,
                                           blank=True)
    coding_end_status = models.CharField('coding region end status',
                                         max_length=20, null=True, blank=True)
    exon_count = models.IntegerField('number of exons', null=True, blank=True)

    gene = models.ForeignKey(Gene, null=True, blank=True)
    exons = models.ManyToManyField(Exon, db_table='transcript_exon')

    class Meta(object):
        db_table = 'transcript'

    def ncbi_url(self):
        return 'http://www.ncbi.nlm.nih.gov/nuccore/' + self.refseq_id


class GeneSet(ObjectSet):
    user = models.ForeignKey(User, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    genes = models.ManyToManyField(Gene, through='GeneSetObject')

    published = models.BooleanField(default=True)

    set_object_rel = 'genes'

    def __unicode__(self):
        return unicode(self.name)

    class Meta(object):
        db_table = 'geneset'
        ordering = ('user', 'name',)


class GeneSetObject(SetObject):
    object_set = models.ForeignKey(GeneSet, db_column='set_id')
    set_object = models.ForeignKey(Gene, db_column='object_id')

    class Meta(object):
        db_table = 'geneset_setobject'
