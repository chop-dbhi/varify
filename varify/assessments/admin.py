from django.contrib import admin
from vdw.assessments.models import SangerResult, Pathogenicity, \
    AssessmentCategory, ParentalResult, Assessment


class AssessmentAdmin(admin.ModelAdmin):
    # DO NOT REMOVE 'sample_result' FROM THIS LIST OR THE ADMIN INTERFACE WILL
    # CRASH WHEN TRYING TO EDIT OR CREATE AN Assessment BECAUSE OF THE
    # sample_result FOREIGN KEY LINK!
    readonly_fields = ('sample_result', 'user')
    exclude = ('notes',)

admin.site.register(Pathogenicity)
admin.site.register(AssessmentCategory)
admin.site.register(ParentalResult)
admin.site.register(SangerResult)
admin.site.register(Assessment, AssessmentAdmin)
