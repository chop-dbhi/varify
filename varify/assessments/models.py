from django.db import models
from django.contrib.auth.models import User
from varify.samples.models import Result
from varify.core.models import TimestampedModel
import reversion


class Pathogenicity(models.Model):
    name = models.CharField(max_length=200, unique=True)

    class Meta(object):
        db_table = 'pathogenicity'
        verbose_name_plural = 'pathogenicities'

    def __unicode__(self):
        return self.name


class AssessmentCategory(models.Model):
    name = models.CharField(max_length=200, unique=True)

    class Meta(object):
        db_table = 'assessment_category'
        verbose_name_plural = 'assessment categories'

    def __unicode__(self):
        return self.name


class ParentalResult(models.Model):
    name = models.CharField(max_length=200, unique=True)

    class Meta(object):
        db_table = 'parental_result'

    def __unicode__(self):
        return self.name


class SangerResult(models.Model):
    confirmed = models.BooleanField()

    class Meta(object):
        db_table = 'sanger_result'


class Assessment(TimestampedModel):
    evidence_details = models.TextField(null=True, blank=True)
    sanger_requested = models.BooleanField()

    assessment_category = models.ForeignKey(AssessmentCategory)
    father_result = models.ForeignKey(ParentalResult, related_name='father')
    mother_result = models.ForeignKey(ParentalResult, related_name='mother')
    pathogenicity = models.ForeignKey(Pathogenicity)
    sample_result = models.ForeignKey(Result)
    sanger_result = models.ForeignKey(SangerResult, null=True, blank=True)
    user = models.ForeignKey(User)

    class Meta(object):
        db_table = 'assessment'
        unique_together = ('sample_result', 'user')


reversion.register(Pathogenicity)
reversion.register(AssessmentCategory)
reversion.register(ParentalResult)
reversion.register(SangerResult)
reversion.register(Assessment,
                   follow=["assessment_category", "father_result",
                           "mother_result", "pathogenicity", "sanger_result"])
