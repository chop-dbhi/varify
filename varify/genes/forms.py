from django import forms
from django.db import transaction
from django.db.models.query import QuerySet
from vdw.genes.models import GeneSet, Gene


class GeneSetField(forms.Field):
    widget = forms.Textarea

    def to_python(self, value):
        if not value:
            return

        # Clean the set and remove duplicates
        names = set([x.strip() for x in value.split()])

        if not names:
            return

        queryset = Gene.objects.filter(symbol__in=names).distinct()
        genes = dict(queryset.values_list('symbol', 'pk'))

        if len(names) != len(genes):
            unknown = [n for n in names if n not in genes]
            raise forms.ValidationError(
                'The following genes were not found: {0}'
                .format(', '.join(sorted(unknown))))

        return queryset

    def prepare_value(self, data):
        if data is None or isinstance(data, basestring):
            return data or ''
        if isinstance(data, QuerySet):
            data = data.values_list('symbol', flat=True)
        return '\n'.join(data)


class GeneSetBulkForm(forms.ModelForm):
    name = forms.CharField(required=True)
    genes = GeneSetField()

    def __init__(self, *args, **kwargs):
        super(GeneSetBulkForm, self).__init__(*args, **kwargs)
        if self.instance.pk and 'genes' not in self.initial:
            self.initial['genes'] = \
                self.instance.genes.values_list('symbol', flat=True)

    @transaction.commit_on_success
    def save(self, commit=True):
        if self.instance and self.instance.pk:
            self.is_new = False
        else:
            self.is_new = True
        # Save the instance prior to creating the gene list
        instance = super(GeneSetBulkForm, self).save(commit=commit)
        if commit:
            self.save_m2m()
        return instance

    def save_m2m(self):
        if self.is_new:
            self.instance.bulk(self.cleaned_data.get('genes'))
        else:
            self.instance.replace(self.cleaned_data.get('genes'))

    class Meta(object):
        model = GeneSet
        fields = ('name', 'user')
