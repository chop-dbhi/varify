from django.conf.urls.defaults import url, patterns, include

registry_urlpatterns = patterns(
    'varify.samples.views',
    url(r'^$', 'registry', name='global-registry'),
    url(r'^projects/(?P<pk>\d+)/$', 'project_registry',
        name='project-registry'),
    url(r'^batches/(?P<pk>\d+)/$', 'batch_registry', name='batch-registry'),
    url(r'^samples/(?P<pk>\d+)/$', 'sample_registry', name='sample-registry'),
)

urlpatterns = patterns(
    'varify.samples.views',
    url(r'^registry/', include(registry_urlpatterns)),
    url(r'^cohorts/$', 'cohort_form', name='cohorts'),
    url(r'^cohorts/(?P<pk>\d+)/$', 'cohort_form', name='cohorts'),
    url(r'^cohorts/(?P<pk>\d+)/delete/$', 'cohort_delete',
        name='cohort-delete'),
)
