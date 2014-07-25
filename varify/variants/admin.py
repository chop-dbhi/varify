from django.contrib import admin
from vdw.variants.models import VariantType, EffectImpact, EffectRegion, \
    Effect, FunctionalClass


class LexiconAdmin(admin.ModelAdmin):
    fields = ['label', 'value', 'code', 'order']
    list_display = ['pk'] + fields
    list_editable = fields


class EffectAdmin(LexiconAdmin):
    fields = ['label', 'value', 'code', 'order', 'impact', 'region']
    list_display = ['pk'] + fields
    list_editable = fields


admin.site.register(VariantType, LexiconAdmin)
admin.site.register(EffectImpact, LexiconAdmin)
admin.site.register(EffectRegion, LexiconAdmin)
admin.site.register(Effect, EffectAdmin)
admin.site.register(FunctionalClass, LexiconAdmin)
