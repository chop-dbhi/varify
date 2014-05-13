import functools
import logging
import requests
from django.core import management
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf.urls import patterns, url
from django.core.cache import cache
from django.http import HttpResponse, Http404
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.views.decorators.cache import never_cache
from django.conf import settings
from guardian.shortcuts import get_objects_for_user
from preserialize.serialize import serialize
from restlib2 import resources
from restlib2.http import codes
from serrano.resources.base import ThrottledResource
from varify.variants.resources import VariantResource
from varify import api
from varify.assessments.models import Assessment
from .models import Sample, Result, ResultScore, ResultSet

log = logging.getLogger(__name__)


def sample_posthook(instance, data, request):
    uri = request.build_absolute_uri

    data['_links'] = {
        'self': {
            'rel': 'self',
            'href': uri(reverse('api:samples:sample',
                                args=[instance.pk])),
        },
        'variants': {
            'rel': 'related',
            'href': uri(reverse('api:samples:variants',
                                args=[instance.pk])),
        },
        'variant-sets': {
            'rel': 'related',
            'href': uri(reverse('api:samples:variant-sets',
                                args=[instance.pk])),
        }
    }

    return data


class SampleBaseResource(ThrottledResource):
    model = Sample

    template = api.templates.Sample

    def get_queryset(self, request, **kwargs):
        projects = get_objects_for_user(request.user, 'samples.view_project')
        return self.model.objects.select_related('batch', 'project')\
            .filter(project__in=projects)

    def get_object(self, request, pk):
        if not hasattr(request, 'instance'):
            queryset = self.get_queryset(request)

            try:
                instance = queryset.get(pk=pk)
            except self.model.DoesNotExist:
                instance = None

            request.instance = instance

        return request.instance


class SamplesResource(SampleBaseResource):
    def get(self, request):
        samples = self.get_queryset(request)
        posthook = functools.partial(sample_posthook, request=request)
        return serialize(samples, posthook=posthook, **self.template)


class SampleResource(SampleBaseResource):
    def is_not_found(self, request, response, pk):
        return not self.get_object(request, pk=pk)

    @api.cache_resource
    def get(self, request, pk):
        instance = self.get_object(request, pk=pk)
        posthook = functools.partial(sample_posthook, request=request)
        return serialize(instance, posthook=posthook, **self.template)


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
        posthook = functools.partial(sample_posthook, request=request)
        return serialize(request.instance, posthook=posthook, **self.template)


class SampleResultBaseResource(ThrottledResource):
    def is_not_found(self, request, response, pk):
        projects = get_objects_for_user(request.user, 'samples.view_project')
        return not Sample.objects.filter(project__in=projects, pk=pk).exists()


class SampleResultsResource(SampleResultBaseResource):
    "Paginated view of results for a sample."
    model = Result

    template = api.templates.SampleResult

    def get(self, request, pk):
        uri = request.build_absolute_uri
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
                    'href': uri(reverse('api:samples:variant',
                                        kwargs={'pk': obj['id']}))
                },
                'sample': {
                    'rel': 'related',
                    'href': uri(reverse('api:samples:sample',
                                        kwargs={'pk': obj['sample']['id']}))
                },
                'variant': {
                    'rel': 'related',
                    'href': uri(reverse('api:variants:variant',
                                        kwargs={'pk': obj['variant_id']})),
                }
            }
            obj.pop('variant_id')

        links = {
            'self': {
                'rel': 'self',
                'href': uri(reverse('api:samples:variants',
                                    kwargs={'pk': pk})),
            }
        }

        if page.number != 1:
            links['prev'] = {
                'rel': 'prev',
                'href': uri('{0}?page={1}'.format(
                    reverse('api:samples:variants', kwargs={'pk': pk}),
                    str(page.number - 1)))
            }

        if page.number < paginator.num_pages - 1:
            links['next'] = {
                'rel': 'next',
                'href': uri('{0}?page={1}'.format(
                    reverse('api:samples:variants', kwargs={'pk': pk}),
                    str(page.number + 1)))
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
        uri = request.build_absolute_uri
        related = ['sample', 'variant', 'genotype', 'score']

        try:
            result = self.model.objects.select_related(*related).get(pk=pk)
        except self.model.DoesNotExist:
            raise Http404

        data = serialize(result, **self.template)

        data['_links'] = {
            'self': {
                'rel': 'self',
                'href': uri(reverse('api:samples:variant',
                                    kwargs={'pk': data['id']}))
            },
            'sample': {
                'rel': 'related',
                'href': uri(reverse('api:samples:sample',
                                    kwargs={'pk': data['sample']['id']}))
            },
            'variant': {
                'rel': 'related',
                'href': uri(reverse('api:variants:variant',
                                    kwargs={'pk': data['variant_id']})),
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
        recalculate = request.GET.get('recalculate_rankings')

        if recalculate == 'true':
            try:
                management.call_command('samples', 'gene-ranks', sample_id,
                                        force=True)
            except Exception:
                log.exception('Error recalculating gene rankings')
                return self.render(request, {
                    'message': 'Error recalculating gene rankings',
                }, status=codes.server_error)

        endpoint = getattr(settings, 'PHENOTYPE_ENDPOINT', None)

        if not endpoint:
            log.error('PHENOTYPE_ENDPOINT setting could not be found.')
            return self.render(request, '', status=codes.server_error)

        endpoint = endpoint.format(sample_id)

        try:
            response = requests.get(endpoint, cert=(settings.VARIFY_CERT,
                                    settings.VARIFY_KEY), verify=False)
        except requests.exceptions.SSLError:
            raise PermissionDenied
        except requests.exceptions.ConnectionError:
            return self.render(request, '', status=codes.server_error)
        except requests.exceptions.RequestException:
            raise Http404

        # If anything at all goes wrong in the sample lookup or json parsing
        # then just abandon all hope and return the content from the orignal
        # response.
        try:
            sample = Sample.objects.get(label=sample_id)
            data = response.json()
            data['phenotype_modified'] = sample.phenotype_modified
            return data
        except Exception:
            pass

        return response.content


class PedigreeResource(ThrottledResource):
    def get(self, request, year, month, day, name):
        endpoint = getattr(settings, 'PEDIGREE_ENDPOINT', None)

        if not endpoint:
            log.error('PEDIGREE_ENDPOINT setting could not be found.')
            return self.render(request, '', status=codes.server_error)

        endpoint = endpoint.format(year, month, day, name)

        try:
            pedigree_response = requests.get(
                endpoint, cert=(settings.VARIFY_CERT, settings.VARIFY_KEY),
                verify=False)
        except requests.exceptions.SSLError:
            raise PermissionDenied
        except requests.exceptions.ConnectionError:
            return self.render(request, '', status=codes.server_error)
        except requests.exceptions.RequestException:
            raise Http404

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = \
            'attachment; filename="{0}-{1}-{2}-{3}"'.format(
                year, month, day, name)

        response.write(pedigree_response.content)

        return response


class SampleResultSetsResource(ThrottledResource):
    model = ResultSet

    template = api.templates.ResultSet

    def get_queryset(self, request, pk):
        return self.model.objects.filter(sample__pk=pk)

    def get(self, request, pk):
        queryset = self.get_queryset(request, pk)
        return serialize(queryset, **self.template)


class SampleResultSetResource(ThrottledResource):
    model = ResultSet

    template = api.templates.ResultSet

    def get_queryset(self, request):
        return self.model.objects.filter(user=request.user)

    def get_object(self, request, pk):
        if not hasattr(request, 'instance'):
            queryset = self.get_queryset(request)

            try:
                instance = queryset.get(pk=pk)
            except self.model.DoesNotExist:
                instance = None

            request.instance = instance

        return request.instance

    def is_not_found(self, request, response, pk):
        return not self.get_object(request, pk)

    def get(self, request, pk):
        instance = self.get_object(request, pk)
        return serialize(instance, **self.template)


sample_resource = never_cache(SampleResource())
samples_resource = never_cache(SamplesResource())
named_sample_resource = never_cache(NamedSampleResource())

sample_results_resource = never_cache(SampleResultsResource())
sample_result_resource = never_cache(SampleResultResource())

sample_result_sets_resource = never_cache(SampleResultSetsResource())
sample_result_set_resource = never_cache(SampleResultSetResource())

phenotype_resource = never_cache(PhenotypeResource())
pedigree_resource = never_cache(PedigreeResource())

urlpatterns = patterns(
    '',

    url(r'^$',
        samples_resource,
        name='samples'),

    url(r'^(?P<pk>\d+)/$',
        sample_resource,
        name='sample'),

    url(r'^(?P<pk>\d+)/variants/$',
        sample_results_resource,
        name='variants'),

    url(r'^variants/(?P<pk>\d+)/$',
        sample_result_resource,
        name='variant'),

    url(r'^(?P<pk>\d+)/variants/sets/$',
        sample_result_sets_resource,
        name='variant-sets'),

    url(r'^variants/sets/(?P<pk>\d+)/$',
        sample_result_set_resource,
        name='variant-set'),

    url(r'^(?P<sample_id>.+)/phenotypes/$',
        phenotype_resource,
        name='phenotype'),

    url(r'^pedigrees/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<name>.+)$',
        pedigree_resource,
        name='pedigree'),

    # At the bottom to prevent matching on such variable parameters
    url(r'^(?P<project>.+)/(?P<batch>.+)/(?P<sample>.+)/$',
        named_sample_resource,
        name='named_sample'),
)
