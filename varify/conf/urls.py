import re
from django.conf.urls.defaults import url, patterns, include
from django.conf import settings
from django.contrib import admin
from django.template.loader import add_to_builtins

add_to_builtins('bootstrapform.templatetags.bootstrap')
add_to_builtins('django.contrib.humanize.templatetags.humanize')
add_to_builtins('avocado.templatetags.avocado_tags')
add_to_builtins('widget_tweaks.templatetags.widget_tweaks')

admin.autodiscover()

urlpatterns = patterns('',
    # Landing page
    url(r'^$', 'varify.views.index', name='index'),

    # News
    url(r'^news/$', 'varify.views.news', name='news'),

    # Includes registration, moderation and authentication
    url(r'', include('varify.accounts.urls')),

    url(r'^', include('varify.samples.urls')),
    url(r'^sources/', include('varify.raw.sources.urls')),

    url(r'^genes/', include('varify.genes.urls')),

    # Cilantro
    url(r'^workspace/$', 'varify.views.app', name='cilantro'),
    url(r'^workspace/(?P<project>.+)/(?P<batch>.+)/(?P<sample>.+)/$', 'varify.views.app', name='cilantro'),
    url(r'^workspace/(?P<project>.+)/(?P<batch>.+)/$', 'varify.views.app',
        name='cilantro'),
    url(r'^', include('cilantro.urls')),

    # Serrano provides the REST API
    url(r'^api/', include('serrano.urls')),

    # Varify and other API
    url(r'^api/', include('varify.api.urls', namespace='api')),

    url(r'^support/$', include('varify.support.urls')),

    # Administrative components
    url(r'^tracking/', include('tracking.urls')),
    url(r'^admin/rq/', include('django_rq_dashboard.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^monitor/', include('sts.urls')),
)

# In production, these two locations must be served up statically
urlpatterns += patterns('django.views.static',
    url(r'^%s(?P<path>.*)$' % re.escape(settings.MEDIA_URL.lstrip('/')),
        'serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^%s(?P<path>.*)$' % re.escape(settings.STATIC_URL.lstrip('/')),
        'serve', {'document_root': settings.STATIC_ROOT}),
)

#Allow testing of 404 and 500 pages in development
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^500/$', 'django.views.defaults.server_error'),
        (r'^404/$', 'django.views.generic.simple.direct_to_template', {'template': '404.html'}),
    )
