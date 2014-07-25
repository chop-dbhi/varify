from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf.urls import patterns, url
from django.http import Http404
from django.views.decorators.cache import never_cache
from django.core.urlresolvers import reverse
from serrano.resources.base import ThrottledResource
from varify import api
from vdw.phenotypes.models import Phenotype
from preserialize.serialize import serialize


class PhenotypeResource(ThrottledResource):
    model = Phenotype

    template = api.templates.Phenotype

    def is_not_found(self, request, response, pk):
        return not self.model.objects.filter(pk=pk).exists()

    @api.cache_resource
    def get(self, request, pk):
        try:
            phenotype = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            raise Http404
        return serialize(phenotype, **self.template)


class PhenotypeSearchResource(ThrottledResource):
    model = Phenotype

    template = api.templates.PhenotypeSearch

    def get(self, request):
        query = request.GET.get('query')
        fuzzy = request.GET.get('fuzzy', 1)
        page = request.GET.get('page', 1)

        phenotypes = self.model.objects.all()

        # Perform search if a query string is supplied
        if query:
            if fuzzy == '0' or fuzzy == 'false':
                phenotypes = phenotypes.filter(term__iexact=query)
            else:
                phenotypes = phenotypes.filter(term__icontains=query)
            phenotypes = phenotypes.distinct()

        # Paginate the results
        paginator = Paginator(phenotypes, api.PAGE_SIZE)

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

        # Post procesing..
        for obj in resp['results']:
            obj['_links'] = {
                'self': {
                    'rel': 'self',
                    'href': reverse('api:phenotypes:phenotype',
                                    kwargs={'pk': obj['id']})
                }
            }

        links = {}
        if page.number != 1:
            links['prev'] = {
                'rel': 'prev',
                'href': "{0}?page={1}".format(reverse('api:phenotypes:search'),
                                              str(page.number - 1))
            }
        if page.number < paginator.num_pages - 1:
            links['next'] = {
                'rel': 'next',
                'href': "{0}?page={1}".format(reverse('api:phenotypes:search'),
                                              str(page.number + 1))
            }
        if links:
            resp['_links'] = links
        return resp


phenotype_resource = never_cache(PhenotypeResource())
phenotype_search_resource = never_cache(PhenotypeSearchResource())

urlpatterns = patterns(
    '',
    url(r'^$', phenotype_search_resource, name='search'),
    url(r'^(?P<pk>\d+)/$', phenotype_resource, name='phenotype'),
)
