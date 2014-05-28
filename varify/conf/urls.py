import re
from django.conf.urls.defaults import url, patterns, include
from django.conf import settings
from django.contrib import admin
from django.template.loader import add_to_builtins
from django.views.generic import RedirectView, TemplateView

add_to_builtins('bootstrapform.templatetags.bootstrap')
add_to_builtins('avocado.templatetags.avocado_tags')

admin.autodiscover()

urlpatterns = patterns(
    '',

    # Landing page
    url(r'^$', RedirectView.as_view(url=settings.LOGIN_URL, permanent=True),
        name='landing'),

    # Cilantro Pages
    url(r'^workspace/', TemplateView.as_view(template_name='index.html'),
        name='workspace'),
    url(r'^query/', TemplateView.as_view(template_name='index.html'),
        name='query'),
    url(r'^results/', TemplateView.as_view(template_name='index.html'),
        name='results'),
    url(r'^analysis/', TemplateView.as_view(template_name='index.html'),
        name='analysis'),

    # Required for opening a sample
    url(r'^sample/', TemplateView.as_view(template_name='index.html'),
        name='sample'),

    url(r'^sources/', include('varify.raw.sources.urls')),
    url(r'^genes/', include('varify.genes.urls')),

    # Required for opening a variant set
    url(r'^variant-sets/', TemplateView.as_view(template_name='index.html'),
        name='variant-set'),

    # Serrano provides the REST API
    url(r'^api/', include('serrano.urls')),

    # Varify and other API
    url(r'^api/', include('varify.api.urls', namespace='api')),

    # Includes registration, moderation and authentication
    url(r'^', include('varify.accounts.urls')),

    # Administrative components
    url(r'^admin/', include(admin.site.urls)),
)

# In production, these two locations must be served up statically
urlpatterns += patterns(
    'django.views.static',
    url(r'^%s(?P<path>.*)$' % re.escape(settings.MEDIA_URL.lstrip('/')),
        'serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^%s(?P<path>.*)$' % re.escape(settings.STATIC_URL.lstrip('/')),
        'serve', {'document_root': settings.STATIC_ROOT}),
)

# Allow testing of 404 and 500 pages in development
if settings.DEBUG:
    urlpatterns += patterns(
        '',
        (r'^500/$', 'django.views.defaults.server_error'),
        (r'^404/$', 'django.views.generic.simple.direct_to_template',
         {'template': '404.html'}),
    )
