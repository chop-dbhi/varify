from django.db import models


class TimestampedModel(models.Model):
    notes = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta(object):
        abstract = True


class LabeledModel(models.Model):
    """A labeled model is simply for differentiating between an editable
    human-readable label and some unique name that should not change. This
    is necessary if other processes are dependent on the name.
    """
    # This is the label for display that can be freely changed without
    # affecting downstream processes such as loading
    label = models.CharField(max_length=100)

    # The fixed name of the project that other processes can depend on
    # such as lookups while loading samples
    name = models.CharField(max_length=100, editable=False)

    class Meta(object):
        abstract = True

    def __unicode__(self):
        return self.label
