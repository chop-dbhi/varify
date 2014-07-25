from django.contrib import admin
from vdw.genes.models import GeneSet


class GeneSetAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'name', 'published', 'count', 'user')
    list_editable = ('published',)
    list_filter = ('published', 'user')

    fields = ('name', 'user', 'count', 'published')
    readonly_fields = ('count',)


admin.site.register(GeneSet, GeneSetAdmin)
