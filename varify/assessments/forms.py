from django.forms import ModelForm
from .models import Assessment


class AssessmentForm(ModelForm):
    class Meta:
        model = Assessment
