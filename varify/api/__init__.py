from functools import wraps
from django.conf import settings
from django.core.cache import cache
from . import templates     # noqa


PAGE_SIZE = 10

if settings.DEBUG:
    CACHE_TIMEOUT = 1
else:
    # 30 day timeout
    CACHE_TIMEOUT = 60 * 60 * 24 * 30


def cache_key(model, pk):
    "Generates a cache key for a model instance."
    app = model._meta.app_label
    name = model._meta.module_name
    return 'api:{0}:{1}:{2}'.format(app, name, pk)


def cache_resource(func):
    @wraps(func)
    def decorate(self, request, pk, *args, **kwargs):
        # Only cache for primary key specific items
        if not args and not kwargs:
            key = cache_key(self.model, pk)
            data = cache.get(key)
            if data is None:
                data = func(self, request, pk, *args, **kwargs)
                cache.set(key, data, CACHE_TIMEOUT)
            return data
        return func(self, request, pk, *args, **kwargs)
    return decorate
