import functools
import logging
from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse
from django.http import Http404
from django.views.decorators.cache import never_cache
from preserialize.serialize import serialize
from serrano.resources.base import ThrottledResource
from varify import api
from varify.assessments.models import Assessment, Pathogenicity, \
    AssessmentCategory
from .models import Analysis

log = logging.getLogger(__name__)


def analysis_posthook(instance, data, request):
    uri = request.build_absolute_uri

    data['_links'] = {
        'self': {
            'rel': 'self',
            'href': uri(reverse('api:analyses:analysis', args=[instance.pk])),
        },
        'assessments': {
            'rel': 'related',
            'href': uri(reverse('api:analyses:assessments',
                                args=[instance.pk])),
        }
    }

    data['assessment_count'] = instance.assessments.count()

    return data


class AnalysesResource(ThrottledResource):
    model = Analysis

    template = api.templates.Analysis

    def get(self, request):
        analyses = self.model.objects.all()
        posthook = functools.partial(analysis_posthook, request=request)
        return serialize(analyses, posthook=posthook, **self.template)


class AnalysisResource(ThrottledResource):
    model = Analysis

    template = api.templates.Analysis

    def is_not_found(self, request, response, pk):
        return not self.model.objects.filter(pk=pk).exists()

    def get(self, request, pk):
        try:
            analysis = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            raise Http404

        posthook = functools.partial(analysis_posthook, request=request)
        return serialize(analysis, posthook=posthook, **self.template)


class AnalysisAssessmentsResource(ThrottledResource):
    model = Assessment

    template = api.templates.Assessment

    def is_not_found(self, request, response, pk):
        return not Analysis.objects.filter(pk=pk).exists()

    def get(self, request, pk):
        assessments = self.model.objects.filter(analysis__pk=pk)

        pathogenicities = []

        for p in Pathogenicity.objects.all():

            categories = []
            for c in AssessmentCategory.objects.all():

                categoryAssessments = assessments.filter(
                    pathogenicity_id=p.id, assessment_category_id=c.id)
                resultIds = categoryAssessments\
                    .values_list('sample_result_id', flat=True).distinct()

                results = []
                for resultId in resultIds:
                    resultAssessments = list(
                        categoryAssessments.filter(sample_result_id=resultId))

                    results.append({
                        'id': resultId,
                        'assessments': serialize(resultAssessments,
                                                 **self.template)
                    })

                categories.append({
                    'id': c.id,
                    'name': c.name,
                    'results': results,
                })

            pathogenicities.append({
                'id': p.id,
                'name': p.name,
                'categories': categories,
            })

        return pathogenicities


analyses_resource = never_cache(AnalysesResource())
analysis_resource = never_cache(AnalysisResource())
analysis_assessments_resource = never_cache(AnalysisAssessmentsResource())

urlpatterns = patterns(
    '',
    url(r'^$', analyses_resource, name='analyses'),
    url(r'^(?P<pk>\d+)/$', analysis_resource, name='analysis'),
    url(r'^(?P<pk>\d+)/assessments/$', analysis_assessments_resource,
        name='assessments'),
)
