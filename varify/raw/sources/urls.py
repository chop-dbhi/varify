from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'varify.raw.sources.views',
    url(r'^$', 'sources', name='sources'),
)
