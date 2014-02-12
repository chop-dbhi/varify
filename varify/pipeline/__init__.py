from django.conf import settings
from avocado.core.loader import autodiscover
from .utils import Channel, job, ManifestReader     # noqa

PIPELINE_CACHE_ALIAS = \
    getattr(settings, 'VARIFY_PIPELINE_CACHE_ALIAS', 'varify.pipeline')

# Creates a pipeline component registry. `pipeline` modules or packages in
# apps that are _installed_ will be autoloaded which enables auto-registering
# components to the pipeline.
autodiscover('pipeline')
