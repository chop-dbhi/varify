from django.contrib import admin
from vdw.raw.sources.models import Source, Stat


class StatInline(admin.TabularInline):
    model = Stat


class SourceAdmin(admin.ModelAdmin):
    inlines = [StatInline]
    list_display = ['name', 'version', 'release_date', 'published', 'archived']
    list_filter = ['published', 'archived', 'name']
    list_editable = ['published', 'archived']
    ordering = ['archived', '-published', 'name']
    save_as = True


admin.site.register(Source, SourceAdmin)
