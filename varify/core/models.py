from django.db import models
from django.db.models import fields
from south.modelsinspector import add_introspection_rules


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


class BigAutoField(fields.AutoField):
    # ONLY PostgreSQL is supported (MySQL, Oracle & SQLite are NOT supported)
    def db_type(self, connection):
        if 'mysql' in connection.__class__.__module__:
            return 'bigint AUTO_INCREMENT'
        elif 'oracle' in connection.__class__.__module__:
            return 'NUMBER(19)'
        elif 'postgres' in connection.__class__.__module__:
            return 'bigserial'
        elif 'sqlite3' in connection.__class__.__modeule__:
            return 'integer'
        else:
            raise NotImplemented
        return super(BigAutoField, self).db_type(connection)

add_introspection_rules([], ["^varify\.core\.models\.BigAutoField"])