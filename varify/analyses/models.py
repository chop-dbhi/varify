from django.db import models
from varify.core.models import TimestampedModel, LabeledModel
from varify.samples.models import Sample


class Analysis(LabeledModel, TimestampedModel):
    OPEN = 'Open'
    PENDING = 'Pending'
    COMPLETE = 'Complete'

    STATUSES = (
        (OPEN, OPEN),
        (PENDING, PENDING),
        (COMPLETE, COMPLETE),
    )

    sample = models.ForeignKey(Sample)
    status = models.CharField(max_length=10, choices=STATUSES, default='Open')
