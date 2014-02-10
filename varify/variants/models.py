from django.db import models
from avocado.models import Lexicon
from varify.genome.models import Chromosome
from varify.literature.models import PubMed
from varify.phenotypes.models import Phenotype, PhenotypeThrough
from varify.genes.models import Gene, Exon, Transcript
from .managers import VariantManager
from .utils import calculate_md5


class EffectImpact(Lexicon):
    "Impact of an effect, e.g. high, moderate, low, etc."
    label = models.CharField(max_length=100)
    value = models.CharField(max_length=100)

    class Meta(Lexicon.Meta):
        db_table = 'effect_impact'


class EffectRegion(Lexicon):
    "Region of the genome an effect can affect."
    label = models.CharField(max_length=100)
    value = models.CharField(max_length=100)

    class Meta(Lexicon.Meta):
        db_table = 'effect_region'


class Effect(Lexicon):
    "The effect a variant can have."
    label = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    # http://snpeff.sourceforge.net/faq.html#What_effects_are_predicted?
    description = models.TextField(null=True, blank=True)
    impact = models.ForeignKey(EffectImpact, null=True, blank=True)
    region = models.ForeignKey(EffectRegion, null=True, blank=True)

    class Meta(Lexicon.Meta):
        db_table = 'effect'


class VariantType(Lexicon):
    "Lexicon of genetic variant types."
    label = models.CharField(max_length=20)
    value = models.CharField(max_length=20)

    class Meta(Lexicon.Meta):
        db_table = 'variant_type'


class Variant(models.Model):
    chr = models.ForeignKey(Chromosome)
    pos = models.IntegerField('position')
    ref = models.TextField('reference', db_index=True)
    alt = models.TextField('alternate', db_index=True)
    md5 = models.CharField(max_length=32, editable=False)

    rsid = models.TextField('dbSNP ID', null=True, blank=True)

    # Note, when loading the data via the VCF file, this is value is set for
    # the entire file, e.g. indel or SNP
    type = models.ForeignKey(VariantType, null=True)

    # Track whether this variant has gone through liftover
    liftover = models.NullBooleanField(
        'has been lifted over?', blank=True, editable=False)

    # Literature
    articles = models.ManyToManyField(PubMed, db_table='variant_pubmed')

    # Phenotypes
    phenotypes = models.ManyToManyField(Phenotype, through='VariantPhenotype')

    objects = VariantManager()

    class Meta(object):
        db_table = 'variant'
        unique_together = ('chr', 'pos', 'ref', 'alt')

    def natural_key(self):
        return (self.chr, self.pos, self.ref, self.alt)

    @classmethod
    def calculate_md5(cls, chr, pos, ref, alt):
        return calculate_md5(chr, pos, ref, alt)

    def ncbi_url(self):
        if self.rsid:
            return 'http://www.ncbi.nlm.nih.gov/projects/SNP/snp_ref.cgi?rs={}' + self.rsid[2:]     # noqa


class VariantPhenotype(PhenotypeThrough):
    variant = models.ForeignKey(Variant, related_name='variant_phenotypes')

    class Meta(object):
        db_table = 'variant_phenotype'


class ThousandG(models.Model):
    variant = models.ForeignKey(Variant, related_name='thousandg', unique=True)
    an = models.IntegerField('total allele count', null=True)
    ac = models.IntegerField('alternate allele count', null=True)
    af = models.FloatField('global allele frequency based on AC/AN',
                           null=True, db_index=True)
    aa = models.TextField('ancestral allele', null=True)
    amr_af = models.FloatField('allele frequency for AMR (American)',
                               null=True, db_index=True)
    asn_af = models.FloatField('allele frequency for ASN (Asian)',
                               null=True, db_index=True)
    afr_af = models.FloatField('allele frequency for AFR (African)',
                               null=True, db_index=True)
    eur_af = models.FloatField('allele frequency for EUR (European)',
                               null=True, db_index=True)

    class Meta(object):
        db_table = '1000g'


class EVS(models.Model):
    variant = models.ForeignKey(Variant, related_name='evs', unique=True)
    ea_ac_ref = models.CharField('reference allele count for EUR (European)',
                                 max_length=20, null=True)
    ea_ac_alt = models.CharField('alternate allele count for EUR (European)',
                                 max_length=20, null=True)
    aa_ac_ref = models.CharField('reference allele count for AFR (African)',
                                 max_length=20, null=True)
    aa_ac_alt = models.CharField('alternate allele count for AFR (African)',
                                 max_length=20, null=True)
    all_ac_ref = models.CharField('reference allele count combined',
                                  max_length=20, null=True)
    all_ac_alt = models.CharField('alternate allele count combined',
                                  max_length=20, null=True)
    ea_af = models.FloatField('allele frequency (AF) for EUR (European)',
                              null=True, db_index=True)
    aa_af = models.FloatField('allele frequency (AF) for AFR (African)',
                              null=True, db_index=True)
    all_af = models.FloatField('allele frequency (AF) combined', null=True,
                               db_index=True)
    gts = models.CharField(
        'observed genotypes', max_length=200, null=True,
        help_text='For INDELs, A1, A2, or An refers to the N-th alternate '
                  'allele while R refers to the reference allele.')
    ea_gtc = models.CharField('genotype counts for EUR (European)',
                              max_length=200, null=True)
    aa_gtc = models.CharField('genotype counts for AFR (African)',
                              max_length=200, null=True)
    all_gtc = models.CharField('genotype counts combined', max_length=200,
                               null=True)
    read_depth = models.IntegerField('read depth', null=True)
    clinical_association = models.TextField(null=True)

    class Meta(object):
        db_table = 'evs'


class PolyPhen2(models.Model):
    variant = models.ForeignKey(Variant, related_name='polyphen2')
    score = models.FloatField('PolyPhen2 score', null=True, db_index=True)
    refaa = models.CharField('reference amino acid', max_length=2, null=True)

    class Meta(object):
        db_table = 'polyphen2'

    @classmethod
    def get_prediction(cls, score):
        if score is None:
            return
        if score <= 0.2:
            return 'Benign'
        elif 0.2 < score < 0.85:
            return 'Possibly Damaging'
        elif 0.85 <= score:
            return 'Probably Damaging'

    @property
    def prediction(self):
        return self.get_prediction(self.score)


class Sift(models.Model):
    variant = models.ForeignKey(Variant, related_name='sift')
    score = models.FloatField('SIFT score', null=True, db_index=True)
    refaa = models.CharField('reference amino acid', max_length=2, null=True)
    varaa = models.CharField('alternate amino acid', max_length=2, null=True)

    class Meta(object):
        db_table = 'sift'

    @classmethod
    def get_prediction(cls, score):
        if score is None:
            return
        if score <= 0.5:
            return 'Damaging'
        elif score > 0.5:
            return 'Tolerated'

    @property
    def prediction(self):
        return self.get_prediction(self.score)


class FunctionalClass(Lexicon):
    label = models.CharField(max_length=100)
    value = models.CharField(max_length=100)

    class Meta(Lexicon.Meta):
        db_table = 'variant_functional_class'
        verbose_name_plural = 'functional classes'


class VariantEffect(models.Model):
    "A variant may have one or more effects associated."
    variant = models.ForeignKey(Variant, null=True, blank=True,
                                related_name='effects')

    codon_change = models.TextField(null=True, blank=True)
    amino_acid_change = models.TextField(null=True, blank=True)

    # If the variant falls within a particular exon, exon will be populated. If
    # it does not but applies to a particular gene transcript, transcript will
    # be populated. If neither of these are available, both values will be null
    exon = models.ForeignKey(Exon, null=True, blank=True)
    transcript = models.ForeignKey(Transcript, null=True, blank=True)
    gene = models.ForeignKey(Gene, null=True, blank=True)
    effect = models.ForeignKey(Effect, null=True, blank=True)
    functional_class = models.ForeignKey(FunctionalClass, null=True,
                                         blank=True)

    hgvs_c = models.CharField('HGVS Coding DNA', max_length=200, null=True,
                              blank=True, db_index=True)
    hgvs_p = models.CharField('HGVS Protein', max_length=200, null=True,
                              blank=True, db_index=True)
    segment = models.CharField(max_length=200, null=True, blank=True)

    class Meta(object):
        db_table = 'variant_effect'
