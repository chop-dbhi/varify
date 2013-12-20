from django.conf.urls import patterns, url
from django.http import Http404
from django.db.models import Q
from django.views.decorators.cache import never_cache
from preserialize.serialize import serialize
from restlib2 import resources
from varify import api
from varify.samples.models import CohortVariant
from varify.assessments.models import Assessment, Pathogenicity, \
    AssessmentCategory
from .models import Variant


class VariantResource(resources.Resource):
    model = Variant

    template = api.templates.Variant

    # Check if the object exists. The cache should not be relied on since
    # it is not deleted or invalidated when objects are deleted
    def is_not_found(self, request, response, pk):
        return not self.model.objects.filter(pk=pk).exists()

    @classmethod
    @api.cache_resource
    def get(self, request, pk):
        related = ['type', 'chr']
        try:
            variant = self.model.objects.select_related(*related).get(pk=pk)
        except self.model.DoesNotExist:
            raise Http404
        data = serialize(variant, **self.template)

        # Roll up unique set of genes and effects for this variant since
        # this is quite important
        genes = set()
        effects = set()
        for eff in data['effects']:
            effects.add(eff['type'])
            if eff.get('transcript') and eff['transcript'].get('gene'):
                if eff['transcript']['gene']:
                    genes.add(eff['transcript']['gene']['symbol'])

        data['unique_genes'] = sorted(genes)
        data['unique_effects'] = sorted(effects)

        # Augment resource with cohort-related details
        # (e.g. allele frequencies)
        perms = Q(cohort__user=None, cohort__published=True) | \
            Q(cohort__user=request.user)
        cohort_variants = CohortVariant.objects.filter(perms,
            variant=variant).order_by('-cohort__order', 'cohort__name').distinct()
        data['cohorts'] = serialize(cohort_variants,
            **api.templates.CohortVariant)

        return data


class VariantAssessmentMetricsResource(resources.Resource):
    model = Variant

    def is_not_found(self, request, response, pk):
        return not self.model.objects.filter(pk=pk).exists()

    def get(self, request, pk):
        assessments = Assessment.objects.filter(sample_result__variant=pk)
        categories = AssessmentCategory.objects.all()
        pathogenicities = Pathogenicity.objects.all()

        data = {
            'metrics': {},
        }

        num_assessments = len(assessments)

        # Easier to check for 0 assessments here than checking for a divide by
        # 0 situation in every loop iteration.
        if num_assessments > 0:
            for p in pathogenicities:
                for c in categories:
                    key = "{0}: {1}".format(p.name, c.name)

                    filter_results = assessments.filter(
                            pathogenicity=p.id, assessment_category=c.id)

                    count = filter_results.count()
                    is_user_call = filter_results.filter(
                            user=request.user.id).exists()

                    if is_user_call:
                        key = key + "(your assessment)"

                    data['metrics'][key] = {
                        'count': count,
                        'percentage': count / float(num_assessments) * 100.0,
                    }

                # Handle empty categories since category isn't required
                key = p.name
                filter_results = assessments.filter(
                        pathogenicity=p.id, assessment_category__isnull=True)
                count = filter_results.count()
                is_user_call = filter_results.filter(
                        user=request.user.id).exists()

                if is_user_call:
                    key = key + "(your assessment)"
                data['metrics'][key] = {
                    'count': count,
                    'percentage': count / float(num_assessments) * 100.0,
                }

        else:
            for c in categories:
                for p in pathogenicities:
                    key = "{0}: {1}".format(p.name, c.name)
                    data['metrics'][key] = {
                        'count': 0.0,
                        'percentage': 0.0,
                    }

        return data


variant_resource = never_cache(VariantResource())
variant_metrics_resource = never_cache(VariantAssessmentMetricsResource())

urlpatterns = patterns(
    '',
    url(r'^(?P<pk>\d+)/$', variant_resource, name='variant'),
    url(r'^(?P<pk>\d+)/assessment-metrics/$', variant_metrics_resource,
        name='variant_assessment_metrics'),
)
