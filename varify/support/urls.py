from django.conf.urls.defaults import *

urlpatterns = patterns('varify.support.views',
    url(r'^$', 'form', name='support'),
    url(r'^success/$', 'success', name='support-success'),
)
