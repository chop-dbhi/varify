from django.core import exceptions
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


class BigIntegerField(fields.IntegerField):
    def db_type(self, connection):
        if 'postgres' in connection.__class__.__module__:
            return 'bigint'
        else:
            raise NotImplemented

    def get_internal_type(self):
        return 'BigIntegerField'

    def to_python(self, value):
        if value is None:
            return value
        try:
            return long(value)
        except (TypeError, ValueError):
            raise exceptions.ValidationError(
                'This value must be a long integer.')


class BigAutoField(fields.AutoField):
    # ONLY PostgreSQL is supported (MySQL, Oracle & SQLite are NOT supported)
    def db_type(self, connection):
        if 'postgres' in connection.__class__.__module__:
            return 'bigserial'
        else:
            raise NotImplemented

    def get_internal_type(self):
        return 'BigAutoField'

    def to_python(self, value):
        if value is None:
            return value
        try:
            return long(value)
        except (TypeError, ValueError):
            raise exceptions.ValidationError(
                'This value must be a long integer.')


class BigForeignKey(fields.related.ForeignKey):
    def db_type(self, connection):
        rel_field = self.rel.get_related_field()
        is_bigauto = isinstance(rel_field, BigAutoField)
        is_bigint = isinstance(rel_field, BigIntegerField)
        matches_type = connection.features.related_fields_match_type
        if (is_bigauto or (not matches_type and is_bigint)):

            return BigIntegerField().db_type(connection)
        return rel_field.db_type(connection)


add_introspection_rules([], ["^varify\.core\.models\.BigIntegerField"])
add_introspection_rules([], ["^varify\.core\.models\.BigAutoField"])
add_introspection_rules([], ["^varify\.core\.models\.BigForeignKey"])
