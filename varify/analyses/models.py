from django.db import models
from varify.core.models import TimestampedModel, LabeledModel
from varify.samples.models import Sample


class Analysis(LabeledModel, TimestampedModel):
    STATUSES = (
        ('Open', 'Open'),
        ('Pending', 'Pending'),
        ('Complete', 'Complete'),
    )

    sample = models.ForeignKey(Sample)
    status = models.CharField(max_length=10, choices=STATUSES, default='Open')
