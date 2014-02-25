import logging
from django.contrib.auth.models import User
from django.conf import settings
from django.db import router, models, transaction, connections, DatabaseError
from sts.contextmanagers import transition
from objectset.models import ObjectSet, SetObject
from varify.core.models import TimestampedModel, LabeledModel
from varify.genome.models import Genome, Genotype
from varify.variants.models import Variant

# The catch all project. If this is None, samples will not be added to
# a default project.
DEFAULT_PROJECT_NAME = getattr(settings, 'DEFAULT_PROJECT_NAME', 'Default')

# Cohort of the entire population of samples. If this is None, samples
# will not be added to a default cohort
DEFAULT_COHORT_NAME = getattr(settings, 'DEFAULT_COHORT_NAME', 'World')

log = logging.getLogger(__name__)


class Person(TimestampedModel):
    "A single person, either the proband or a relative."
    mrn = models.CharField(max_length=50, null=True, blank=True)

    # For pedigree and sex-linked analyses
    sex = models.CharField(max_length=20, null=True, blank=True)

    # Designates whether this person is the proband, i.e. person of
    # interest in the context of variant analysis, e.g. family members
    # are not.
    proband = models.BooleanField(default=False)

    # For trio or general pedigree analysis, this marks an explicit link
    # between the proband and the family member.
    relations = models.ManyToManyField('self', through='Relation',
                                       symmetrical=False)

    class Meta(object):
        db_table = 'person'
        permissions = (
            ('view_person', 'View Person'),
        )

    def __unicode__(self):
        return self.mrn or 'P{0}'.format(str(self.pk).zfill(6))


class Relation(TimestampedModel):
    "A relation between two persons. This enables pedigree analysis."
    person = models.ForeignKey(Person, related_name='family')
    relative = models.ForeignKey(Person, related_name='relative_of')

    # Type of relation, e.g. mother, father, sibling
    type = models.CharField(max_length=20)

    # Generation of `relative` relative to `person` where the generation
    # of `person` is 0, e.g. a parent is 1 and a sibling is 0.
    generation = models.IntegerField(default=0)

    class Meta(object):
        db_table = 'relation'
        ordering = ('person', '-generation')


class Project(LabeledModel, TimestampedModel):
    "High-level organization of cohorts (and samples) within a project."

    class Meta(LabeledModel.Meta):
        db_table = 'project'
        unique_together = ('name',)
        permissions = (
            ('view_project', 'View Project'),
        )


class Batch(LabeledModel, TimestampedModel):
    """A cohort defines a high-level grouping of samples for a particular
    study and/or research question. This is referred to as project-level
    cohort.
    """
    investigator = models.CharField(max_length=100, null=True, blank=True)

    # The project this cohort (and thus samples) are associated with)
    project = models.ForeignKey(Project, related_name='batches')

    # Defines whether this cohort is published. Once at least one sample
    # if loaded, this cohort may become available.
    published = models.BooleanField(default=False)

    # Store the sample count since this does not change
    count = models.IntegerField(default=0)

    class Meta(LabeledModel.Meta):
        db_table = 'batch'
        unique_together = ('project', 'name')
        ordering = ('project', 'label')
        verbose_name_plural = 'batches'
        permissions = (
            ('view_batch', 'View Batch'),
        )


class Sample(LabeledModel, TimestampedModel):
    # Direct reference to project this sample is associated with. Although
    # this is available through `batch`, batches are a function of the loading
    # process, but not necessarily the hierarchy of samples.
    project = models.ForeignKey(Project, related_name='samples')

    # Reference to the cohort this sample is associated with
    batch = models.ForeignKey(Batch, related_name='samples')

    # Version of the sample and downstream results
    version = models.IntegerField()

    # Reference to the person this sample is derived from.
    person = models.ForeignKey(Person, null=True, blank=True,
                               related_name='samples')

    # Store the result count since this does not change
    count = models.IntegerField(default=0)

    # Identifier of the biological sample this data is associated with
    # in the LIMS
    bio_sample = models.IntegerField(null=True, blank=True)

    # The name this sample was given in the VCF file (as opposed to the
    # MANIFEST)
    vcf_colname = models.CharField(max_length=200, null=True, blank=True,
                                   help_text='vcf column sample name')

    # Marks whether this sample is published. Once this sample's results have
    # been fully processed will this flag be true. As a sanity check, there
    # should only ever be one sample published for a single person.
    published = models.BooleanField(default=False)

    # MD5 of the VCF sample file. This provides a sanity check for
    # new files that represent the same sample in case reloads need
    # to happen.
    md5 = models.CharField(max_length=32, null=True, blank=True,
                           editable=False)

    class Meta(LabeledModel.Meta):
        db_table = 'sample'
        unique_together = ('batch', 'name', 'version')
        ordering = ('project', 'batch', 'label')
        permissions = (
            ('view_sample', 'View Sample'),
        )

    def __unicode__(self):
        return self.label


class SampleManifest(TimestampedModel):
    "Discrete attributes from the sample manifest."
    sample = models.OneToOneField(Sample, related_name='manifest')
    # Original path to the manifest file
    #manifest paths cannot be unique since a vcf can contain more than one vcf
    path = models.CharField(max_length=200, unique=False)
    # Cache of the manifest content in case the file no longer exists
    content = models.TextField()

    class Meta(object):
        db_table = 'sample_manifest'

    def __unicode__(self):
        return u'Sample Manifest: {0}'.format(unicode(self.sample))

    def load_content(self, path):
        "Attempts to open the file and read the content."
        log.debug('Opening {0} in {1} load_content'.format(path, __name__))
        with open(path) as fin:
            self.path = path
            self.content = fin.read()

    def content_has_changed(self):
        "Reads the contents from the file and compares with the local copy."

        log.debug('Opening {0} in {1} content_has_changed'
                  .format(self.path, __name__))
        with open(self.path) as fin:
            return fin.read() != self.content


class Cohort(ObjectSet):
    "A Cohort is a logical grouping of samples for some purpose."

    user = models.ForeignKey(User, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)

    # Reference for easier management and delegation of permissions
    # for related users
    project = models.ForeignKey(Project, null=True, blank=True)

    # Reference for easier autocreation
    batch = models.ForeignKey(Batch, null=True, blank=True)

    samples = models.ManyToManyField(Sample, through='CohortSample')

    # Defines whether this cohort is published. This can be used
    # to toggle when this cohort is visible depending on when if
    # the statistics across samples is consistent.
    published = models.BooleanField(default=False)

    autocreated = models.BooleanField(default=False)

    # This is purely for ordering the autocreated cohorts above
    # user-defined cohorts..
    order = models.SmallIntegerField(default=0)

    allele_freq_modified = models.DateTimeField(null=True)

    set_object_rel = 'samples'
    label_field = 'name'

    def __unicode__(self):
        return unicode(self.name)

    class Meta(object):
        db_table = 'cohort'
        ordering = ('-order', 'name')
        permissions = (
            ('view_cohort', 'View Cohort'),
        )

    def compute_allele_frequencies(self, using=None):
        "Computes the allele frequencies across all samples in this cohort."
        if using is None:
            using = router.db_for_write(self.__class__)
        cursor = connections[using].cursor()

        with transition(self, 'Recomputed Allele Frequencies'):
            with transaction.commit_manually(using):
                # TODO update to use model._meta.db_table..
                try:
                    # Raw query to prevent all the overhead of using the
                    # `delete()` method.
                    cursor.execute(
                        'DELETE FROM cohort_variant WHERE cohort_id = %s',
                        [self.id])

                    # Update count on cohort instance
                    cursor.execute('''
                        UPDATE "cohort" SET "count" = (
                            SELECT COUNT(id)
                            FROM "cohort_sample"
                            WHERE "cohort_id" = "cohort"."id"
                        ) WHERE "id" = %s
                    ''', [self.id])

                    # Calculate frequencies for all variants associated with
                    # all samples in this cohort
                    cursor.execute('''
                        INSERT INTO cohort_variant (cohort_id, variant_id, af)
                        (
                            SELECT c.id, r.variant_id,
                                COUNT(r.id) / c."count"::float
                            FROM sample_result r
                                INNER JOIN sample s ON (r.sample_id = s.id)
                                INNER JOIN cohort_sample cs ON
                                    (cs.sample_id = s.id)
                                INNER JOIN cohort c ON (cs.cohort_id = c.id)
                            WHERE c.id = %s
                            GROUP BY c.id, r.variant_id, c."count"
                        )
                    ''', [self.id])
                    transaction.commit()
                except DatabaseError, e:
                    transaction.rollback()
                    log.exception(e)
                    raise


class CohortSample(SetObject):
    object_set = models.ForeignKey(Cohort, db_column='cohort_id')
    set_object = models.ForeignKey(Sample, db_column='sample_id')

    class Meta(SetObject.Meta):
        db_table = 'cohort_sample'


class CohortVariant(models.Model):
    """Cohort-level aggregated data relative to specific variants. This
    currently only includes 'allele frequency' for the given cohort.
    """
    variant = models.ForeignKey(Variant, related_name='cohort_details')
    cohort = models.ForeignKey(Cohort)
    af = models.FloatField(null=True, db_index=True)

    class Meta(object):
        db_table = 'cohort_variant'
        unique_together = ('variant', 'cohort')


class SampleRun(TimestampedModel):
    "Sample run through the pipeline."
    sample = models.ForeignKey(Sample)
    genome = models.ForeignKey(Genome, null=True, blank=True)
    completed = models.DateTimeField(null=True, blank=True)

    class Meta(object):
        db_table = 'sample_run'

    def __unicode__(self):
        return '{0} on {1}'.format(self.sample, self.completed)


class Result(TimestampedModel):
    # Reference to the sample
    sample = models.ForeignKey(Sample, related_name='results')

    # Reference to the unique variant this result is about
    variant = models.ForeignKey(Variant)

    # Genome Analysis Toolkit (GATK) VCF fields
    quality = models.FloatField(null=True, blank=True, db_index=True)

    # DP
    read_depth = models.IntegerField(null=True, blank=True, db_index=True)
    raw_read_depth = models.IntegerField(null=True, blank=True, db_index=True)

    # GATK VCF genotype fields GT
    genotype = models.ForeignKey(Genotype, null=True, blank=True)
    genotype_quality = models.FloatField(null=True, blank=True)

    # Depth of coverage per allele
    coverage_ref = models.IntegerField(null=True, blank=True)
    coverage_alt = models.IntegerField(null=True, blank=True)

    phred_scaled_likelihood = models.TextField(null=True, blank=True)

    in_dbsnp = models.NullBooleanField(blank=True)
    downsampling = models.NullBooleanField(blank=True)
    spanning_deletions = models.FloatField(null=True, blank=True)
    mq = models.FloatField('mapping quality', null=True, blank=True)
    mq0 = models.FloatField('mapping quality zero', null=True, blank=True)
    baseq_rank_sum = models.FloatField('base quality rank sum test',
                                       null=True, blank=True)
    mq_rank_sum = models.FloatField('mapping quality rank sum test',
                                    null=True, blank=True)
    read_pos_rank_sum = models.FloatField(null=True, blank=True)
    strand_bias = models.FloatField(null=True, blank=True)
    homopolymer_run = models.IntegerField(null=True, blank=True)
    haplotype_score = models.FloatField(null=True, blank=True)
    quality_by_depth = models.FloatField(null=True, blank=True)
    fisher_strand = models.FloatField(null=True, blank=True)
    base_counts = models.CharField(max_length=100, null=True, blank=True,
                                   help_text='A,C,G,T base counts')

    class Meta(object):
        db_table = 'sample_result'
        unique_together = ('sample', 'variant')

    @property
    def genotype_value(self):
        if self.genotype:
            genotype = self.genotype.value
            variant = self.variant
            if genotype in ('1/1', '1/2'):
                return variant.alt + '/' + variant.alt
            elif genotype == '0/1':
                return variant.ref + '/' + variant.alt
            elif genotype == '0/0':
                return variant.ref + '/' + variant.alt

    @property
    def base_count_map(self):
        if self.base_counts:
            bases = ('A', 'C', 'G', 'T')
            try:
                counts = [int(x) for x in self.base_counts.split(',')]
                return dict(zip(bases, counts))
            except (TypeError, ValueError) as e:
                log.exception(e)


class ResultScore(TimestampedModel):
    result = models.ForeignKey(Result, related_name='score', unique=True)
    rank = models.IntegerField()
    score = models.FloatField()

    class Meta(object):
        db_table = 'result_score'


# Load signal receivers. This is imported below to prevent circular imports
# with the above models.
from . import receivers     # noqa
