from django.conf.urls import patterns, url
from django.db.models import Q
from django.http import Http404
from django.views.decorators.cache import never_cache
from guardian.shortcuts import get_objects_for_user
from preserialize.serialize import serialize
from serrano.resources.base import ThrottledResource
from varify import api
from varify.samples.models import CohortVariant
from varify.assessments.models import Assessment, Pathogenicity, \
    AssessmentCategory
from .models import Variant


class VariantResource(ThrottledResource):
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

        # Augment resource with cohort-related details (e.g. allele
        # frequencies)
        perms = Q(cohort__user=None, cohort__published=True) | \
            Q(cohort__user=request.user)
        cohort_variants = CohortVariant.objects.filter(perms, variant=variant)\
            .order_by('-cohort__order', 'cohort__name').distinct()

        cohort_list = []
        for cv in cohort_variants:
            cohort_data = serialize(cv, **api.templates.CohortVariant)

            # Find all the samples within this cohort that also contain
            # this variant. If a sample is in the cohort but doesn't contain
            # this variant then there is no benefit to including it.
            samples_with_variant = cv.cohort.samples.filter(
                results__variant=cv.variant)

            cohort_data['samples'] = serialize(samples_with_variant,
                                               **api.templates.SimpleSample)

            cohort_list.append(cohort_data)

        data['cohorts'] = cohort_list

        return data


class VariantAssessmentMetricsResource(ThrottledResource):
    model = Variant

    def is_not_found(self, request, response, pk):
        return not self.model.objects.filter(pk=pk).exists()

    def get(self, request, pk):
        categories = AssessmentCategory.objects.all()
        pathogenicities = Pathogenicity.objects.all()
        assessments = Assessment.objects.select_related('sample_result') \
            .filter(sample_result__variant=pk)

        data = {}

        num_assessments = len(assessments)

        # Easier to check for 0 assessments here than checking for a divide by
        # 0 situation in every loop iteration.
        if num_assessments > 0:
            data['num_assessments'] = num_assessments

            # Create the pathogenic summary excluding pathogenicities with
            # no calls associated with them.
            pathogenicity_data = {}
            for p in pathogenicities:
                filter_results = assessments.filter(pathogenicity=p.id)

                if filter_results.exists():
                    pathogenicity_data[p.name] = self.get_assessment_data(
                        filter_results, num_assessments, request.user.id)

            data['pathogenicities'] = pathogenicity_data

            # Create the assessment category summary excluding categories with
            # no calls associated with them.
            category_data = {}
            for c in categories:
                filter_results = assessments.filter(assessment_category=c.id)

                if filter_results.exists():
                    category_data[c.name] = self.get_assessment_data(
                        filter_results, num_assessments, request.user.id)

            # Handle empty categories since category isn't required
            filter_results = assessments.filter(
                assessment_category__isnull=True)

            if filter_results.exists():
                category_data[''] = self.get_assessment_data(
                    filter_results, num_assessments, request.user.id)

            data['categories'] = category_data

            # Get the list of all the projects the user has access to. We will
            # use this later to make sure that we don't expose the assessment
            # details made via samples this user doesn't have rights to view.
            user_project_ids = \
                get_objects_for_user(request.user, 'samples.view_project') \
                .values_list('pk', flat=True)

            data['assessments'] = []
            for a in assessments:
                a_data = {}
                a_data['id'] = a.pk
                a_data['pathogenicity'] = a.pathogenicity.name
                a_data['category'] = getattr(a.assessment_category, 'name', '')
                a_data['sanger'] = 'Yes' if a.sanger_requested else 'No'
                a_data['mother_result'] = a.mother_result.name
                a_data['father_result'] = a.father_result.name
                a_data['sample'] = {
                    'id': a.sample_result.sample.id,
                    'name': a.sample_result.sample.name,
                }
                a_data['user'] = {
                    'username': a.user.username,
                    'email': a.user.email,
                }

                if a.sample_result.sample.project.id in user_project_ids:
                    a_data['details'] = a.evidence_details

                data['assessments'].append(a_data)

        return {
            'metrics': data,
        }

    def get_assessment_data(self, queryset, total_count, user_id):
        """
        Calculates and sets the following data for the supplied queryset:
            data = {
                'count': <the number of items in the queryset>
                'percentage': <percentage of total_count queryset represents>
                'is_user_call': <true if user made this call, false otherwise>
                'usernames': <set of all usernames who made this call>
            }
        """

        # We need to convert the usernames to strings here because the JSON
        # encoder will choke when serializing this data if the usernames are
        # unicode as they are when we get them back from the distinct call.
        usernames = [str(u) for u in queryset.values_list(
            'user__username', flat=True).distinct()]

        count = queryset.count()
        is_user_call = queryset.filter(user=user_id).exists()

        return {
            'count': count,
            'percentage': count / float(total_count) * 100.0,
            'is_user_call': is_user_call,
            'usernames': usernames,
        }


variant_resource = never_cache(VariantResource())
variant_metrics_resource = never_cache(VariantAssessmentMetricsResource())

urlpatterns = patterns(
    '',
    url(r'^(?P<pk>\d+)/$', variant_resource, name='variant'),
    url(r'^(?P<pk>\d+)/assessment-metrics/$', variant_metrics_resource,
        name='variant_assessment_metrics'),
)
