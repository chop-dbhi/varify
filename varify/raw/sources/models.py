from django.db import models


class Source(models.Model):
    name = models.CharField(max_length=200)
    version = models.CharField(max_length=30, null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    website = models.TextField(blank=True)
    download_url = models.TextField(blank=True)

    published = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta(object):
        db_table = 'source'
        ordering = ['name']

    def __unicode__(self):
        if self.version:
            return u'{0} (v{1})'.format(self.name, self.version.lstrip('v'))
        if self.release_date:
            return u'{0} ({1})'.format(
                self.name, self.release_date.strftime('%Y-%m-%d'))
        return u'{0}'.format(self.name)


class Stat(models.Model):
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    source = models.ForeignKey(Source, related_name='stats')

    class Meta(object):
        db_table = 'source_stat'
