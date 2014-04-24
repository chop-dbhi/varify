from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from vdw.samples.models import Project, Cohort, Batch, Sample, \
    SampleManifest, ResultSet


class ProjectAdmin(GuardedModelAdmin):
    list_display = ('__unicode__', 'label', 'name')
    list_editable = ('label',)

    search_fields = ('label',)

    fields = ('label', 'notes')


class BatchAdmin(GuardedModelAdmin):
    list_display = ('__unicode__', 'label', 'published', 'project', 'count')
    list_editable = ('label', 'published')
    list_filter = ('published', 'project')

    search_fields = ('label', 'project__label')

    fields = ('label', 'project', 'count', 'published', 'notes')
    readonly_fields = ('project', 'count')


class CohortAdmin(GuardedModelAdmin):
    list_display = ('__unicode__', 'name', 'published', 'project', 'batch',
                    'count', 'autocreated', 'user')
    list_editable = ('published',)
    list_filter = ('published', 'project', 'batch', 'autocreated', 'user')

    search_fields = ('name', 'batch__label', 'project__label')

    fields = ('name', 'batch', 'project', 'user', 'count', 'autocreated',
              'published')
    readonly_fields = ('batch', 'project', 'count', 'autocreated')

    ordering = ('project', 'batch', 'user', 'name')


class SampleAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'label', 'published', 'project',
                    'batch', 'count')
    list_editable = ('label', 'published')
    list_filter = ('published', 'project', 'batch')

    search_fields = ('label', 'project__label', 'batch__label')

    fields = ('label', 'batch', 'project', 'count', 'published', 'notes')
    readonly_fields = ('batch', 'project', 'count')


class SampleManifestAdmin(admin.ModelAdmin):
    list_display = ('sample', 'path')
    readonly_fields = ('sample', 'path', 'formatted_content', 'created',
                       'modified')
    fieldsets = (
        (None, {
            'fields': ['sample'],
        }),
        ('File', {
            'fields': ['path', 'formatted_content'],
            'description': 'The indent on the first line is a side effect '
                           'of how the admin site template is structured. The '
                           'actual content does not have an indent.'
        }),
        ('Other', {
            'fields': ['created', 'modified', 'notes'],
        }),
    )

    def formatted_content(self, instance):
        return '<pre>{0}</pre>'.format(instance.content.strip())

    formatted_content.allow_tags = True
    formatted_content.short_description = 'Content'


class ResultSetAdmin(admin.ModelAdmin):
    list_display = ('name', 'sample', 'user')

    fieldsets = (
        (None, {
            'fields': ('name', 'sample', 'user', 'description'),
        }),
    )


admin.site.register(Sample, SampleAdmin)
admin.site.register(SampleManifest, SampleManifestAdmin)
admin.site.register(Cohort, CohortAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Batch, BatchAdmin)
admin.site.register(ResultSet, ResultSetAdmin)
