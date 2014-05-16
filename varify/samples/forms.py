from django import forms
from django.db import transaction
from vdw.samples.models import Cohort, Sample, ResultSet


class CohortForm(forms.ModelForm):
    name = forms.CharField(required=True)
    samples = forms.ModelMultipleChoiceField(
        queryset=Sample.objects.all(), widget=forms.CheckboxSelectMultiple)

    def __init__(self, queryset=None, *args, **kwargs):
        if kwargs.get('instance', None) and kwargs['instance'].pk:
            kwargs.setdefault('initial', {})
            kwargs['initial']['samples'] = kwargs['instance'].samples.all()

        super(CohortForm, self).__init__(*args, **kwargs)

        if queryset is not None:
            self.fields['samples'].queryset = queryset

    @transaction.commit_on_success
    def save(self, commit=True):
        if self.instance and self.instance.pk:
            self.is_new = False
        else:
            self.is_new = True
        # Save the instance prior to creating the set
        instance = super(CohortForm, self).save(commit=commit)
        if commit:
            self.save_m2m()
        return instance

    def save_m2m(self):
        # Ignore default set functionality of flagging added/removed items
        if not self.is_new:
            self.instance._all_set_objects.delete()
        self.instance.bulk(self.cleaned_data.get('samples'))

    class Meta(object):
        model = Cohort
        fields = ('name', 'user', 'published')


class ResultSetForm(forms.ModelForm):
    class Meta(object):
        model = ResultSet
        exclude = ('results', 'user')
