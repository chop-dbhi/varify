from avocado.formatters import registry as formatters
from serrano.formatters import HTMLFormatter


class Pathogenicity(HTMLFormatter):
    def to_html(self, value, **context):
        from vdw.assessments.models import Pathogenicity

        try:
            pathogenicity = Pathogenicity.objects.get(pk=value)
        except Pathogenicity.DoesNotExist:
            return '<span class="muted">n/a</span>'

        return pathogenicity.name

    def to_excel(self, value, **context):
        from vdw.assessments.models import Pathogenicity

        try:
            pathogenicity = Pathogenicity.objects.get(pk=value)
        except Pathogenicity.DoesNotExist:
            return 'n/a'

        return pathogenicity.name


class AssessmentCategory(HTMLFormatter):
    def to_html(self, value, **context):
        from vdw.assessments.models import AssessmentCategory

        try:
            category = AssessmentCategory.objects.get(pk=value)
        except AssessmentCategory.DoesNotExist:
            return '<span class="muted">n/a</span>'

        return category.name

    def to_excel(self, value, **context):
        from vdw.assessments.models import AssessmentCategory

        try:
            category = AssessmentCategory.objects.get(pk=value)
        except AssessmentCategory.DoesNotExist:
            return 'n/a'

        return category.name

formatters.register(Pathogenicity, 'Pathogenicity')
formatters.register(AssessmentCategory, 'Assessment Category')
