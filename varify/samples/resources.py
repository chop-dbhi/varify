import functools
import requests
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf.urls import patterns, url
from django.core.cache import cache
from django.http import HttpResponse, Http404
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.views.decorators.cache import never_cache
from django.conf import settings
from preserialize.serialize import serialize
from restlib2 import resources
from serrano.resources.base import ThrottledResource
from varify.variants.resources import VariantResource
from varify import api
from varify.assessments.models import Assessment
from .models import Sample, Result, ResultScore


def sample_posthook(instance, data, request):
    uri = request.build_absolute_uri
    data['_links'] = {
        'self': {
            'rel': 'self',
            'href': uri(reverse('api:samples:sample', args=[instance.pk])),
        },
        'variants': {
            'rel': 'related',
            'href': uri(reverse('api:samples:variants', args=[instance.pk])),
        }
    }

    return data


class SampleResource(ThrottledResource):
    model = Sample

    template = api.templates.Sample

    def is_not_found(self, request, response, pk):
        return not self.model.objects.filter(pk=pk).exists()

    @api.cache_resource
    def get(self, request, pk):
        try:
            sample = self.model.objects.select_related(
                'batch', 'project').get(pk=pk)
        except self.model.DoesNotExist:
            raise Http404

        posthook = functools.partial(sample_posthook, request=request)
        return serialize(sample, posthook=posthook, **self.template)


class SamplesResource(ThrottledResource):
    model = Sample

    template = api.templates.Sample

    def get(self, request):
        samples = self.model.objects.all()
        posthook = functools.partial(sample_posthook, request=request)
        return serialize(samples, posthook=posthook, **self.template)


class NamedSampleResource(ThrottledResource):
    "Resource for looking up a sample by project, batch, and sample name"
    model = Sample

    template = api.templates.Sample

    # Bypass authorization check imposed by Serrano's AUTH_REQUIRED setting
    def __call__(self, *args, **kwargs):
        return resources.Resource.__call__(self, *args, **kwargs)

    def is_not_found(self, request, response, project, batch, sample):
        try:
            instance = self.model.objects.get(project__name=project,
                                              batch__name=batch, name=sample)
        except self.model.DoesNotExist:
            return True

        request.instance = instance
        return False

    def get(self, request, project, batch, sample):
        data = serialize(request.instance, **self.template)
        data['_links'] = {
            'self': {
                'rel': 'self',
                'href': reverse('api:samples:sample',
                                kwargs={'pk': request.instance.pk})
            },
            'variants': {
                'rel': 'related',
                'href': reverse('api:samples:variants',
                                kwargs={'pk': request.instance.pk}),
            }
        }
        return data


class SampleResultsResource(ThrottledResource):
    "Paginated view of results for a sample."
    model = Result

    template = api.templates.SampleResult

    def is_not_found(self, request, response, pk):
        return not Sample.objects.filter(pk=pk).exists()

    def get(self, request, pk):
        page = request.GET.get('page', 1)

        related = ['sample', 'variant', 'variant__chr', 'genotype']
        results = self.model.objects.select_related(*related)\
            .filter(sample__pk=pk)

        # Paginate the results
        paginator = Paginator(results, api.PAGE_SIZE)

        try:
            page = page = paginator.page(page)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)

        resp = {
            'result_count': paginator.count,
            'results': serialize(page.object_list, **self.template),
        }

        # Augment the links
        for obj in resp['results']:
            obj['_links'] = {
                'self': {
                    'rel': 'self',
                    'href': reverse('api:samples:variant',
                                    kwargs={'pk': obj['id']})
                },
                'sample': {
                    'rel': 'related',
                    'href': reverse('api:samples:sample',
                                    kwargs={'pk': obj['sample']['id']})
                },
                'variant': {
                    'rel': 'related',
                    'href': reverse('api:variants:variant',
                                    kwargs={'pk': obj['variant_id']}),
                }
            }
            obj.pop('variant_id')

        links = {}
        if page.number != 1:
            links['prev'] = {
                'rel': 'prev',
                'href': "{0}?page={1}".format(
                    reverse('api:samples:variants', kwargs={'pk': pk}),
                    str(page.number - 1))
            }
        if page.number < paginator.num_pages - 1:
            links['next'] = {
                'rel': 'next',
                'href': "{0}?page={1}".format(
                    reverse('api:samples:variants', kwargs={'pk': pk}),
                    str(page.number + 1))
            }
        if links:
            resp['_links'] = links
        return resp


class SampleResultResource(ThrottledResource):
    model = Result

    template = api.templates.SampleResultVariant

    def is_not_found(self, request, response, pk):
        return not self.model.objects.filter(pk=pk).exists()

    def _cache_data(self, request, pk, key):
        related = ['sample', 'variant', 'genotype', 'score']

        try:
            result = self.model.objects.select_related(*related).get(pk=pk)
        except self.model.DoesNotExist:
            raise Http404

        data = serialize(result, **self.template)

        data['_links'] = {
            'self': {
                'rel': 'self',
                'href': reverse('api:samples:variant',
                                kwargs={'pk': data['id']})
            },
            'sample': {
                'rel': 'related',
                'href': reverse('api:samples:sample',
                                kwargs={'pk': data['sample']['id']})
            },
            'variant': {
                'rel': 'related',
                'href': reverse('api:variants:variant',
                                kwargs={'pk': data['variant_id']}),
            }
        }

        # Integrate the Variant resource data
        data['variant'] = VariantResource.get(request, data['variant_id'])
        data.pop('variant_id')

        try:
            score = ResultScore.objects.get(result=result)
            data['score'] = {
                'score': score.score,
                'rank': score.rank,
            }
        except ResultScore.DoesNotExist:
            pass

        cache.set(key, data, timeout=api.CACHE_TIMEOUT)
        return data

    def get(self, request, pk):
        key = api.cache_key(self.model, pk)
        data = cache.get(key)

        if data is None:
            data = self._cache_data(request, pk, key)

        try:
            assessment = Assessment.objects.get(sample_result=pk,
                                                user=request.user.id)
            data['assessment'] = serialize(assessment,
                                           **api.templates.ResultAssessment)
        except Assessment.DoesNotExist:
            data['assessment'] = {}

        return data


class PhenotypeResource(ThrottledResource):
    def get(self, request, sample_id):
        endpoint = settings.PHENOTYPE_ENDPOINT % sample_id

        try:
            response = requests.get(endpoint, cert=(settings.VARIFY_CERT,
                                    settings.VARIFY_KEY), verify=False)
        except requests.exceptions.SSLError:
            raise PermissionDenied
        except requests.exceptions.ConnectionError:
            return HttpResponse(status=500)
        except requests.exceptions.RequestException:
            raise Http404

        return response.content


sample_resource = never_cache(SampleResource())
samples_resource = never_cache(SamplesResource())
named_sample_resource = never_cache(NamedSampleResource())
sample_results_resource = never_cache(SampleResultsResource())
sample_result_resource = never_cache(SampleResultResource())
phenotype_resource = never_cache(PhenotypeResource())

urlpatterns = patterns(
    '',
    url(r'^$', samples_resource, name='samples'),
    url(r'^(?P<pk>\d+)/$', sample_resource, name='sample'),
    url(r'^(?P<project>.+)/(?P<batch>.+)/(?P<sample>.+)/$',
        named_sample_resource, name='named_sample'),
    url(r'^(?P<pk>\d+)/variants/$', sample_results_resource, name='variants'),
    url(r'^variants/(?P<pk>\d+)/$', sample_result_resource, name='variant'),
    url(r'^(?P<sample_id>.+)/phenotypes/$', phenotype_resource,
        name='phenotype'),
)
