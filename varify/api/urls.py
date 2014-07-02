from django.conf.urls import url, patterns, include

urlpatterns = patterns(
    '',
    url(r'^genes/', include('varify.genes.resources',
        namespace='genes')),
    url(r'^phenotypes/', include('varify.phenotypes.resources',
        namespace='phenotypes')),
    url(r'^variants/', include('varify.variants.resources',
        namespace='variants')),
    url(r'^samples/', include('varify.samples.resources',
        namespace='samples')),
    url(r'^assessments/', include('varify.assessments.resources',
        namespace='assessments')),
)
