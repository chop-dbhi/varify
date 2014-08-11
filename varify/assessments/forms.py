from django.forms import ModelForm
from vdw.assessments.models import Assessment


class AssessmentForm(ModelForm):
    class Meta:
        model = Assessment
