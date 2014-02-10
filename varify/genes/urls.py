from django.conf.urls.defaults import url, patterns

urlpatterns = patterns(
    'varify.genes.views',
    url(r'^sets/$', 'geneset_form', name='genesets'),
    url(r'^sets/(?P<pk>\d+)/$', 'geneset_form', name='genesets'),
    url(r'^sets/(?P<pk>\d+)/delete/$', 'geneset_delete',
        name='geneset-delete'),
)
