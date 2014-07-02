import _setenv  # noqa
from varify.variants.models import Variant

ITERATIONS = 1
MAX_COUNTS = [pow(10, 2), pow(10, 3), pow(10, 4), pow(10, 5)]


def memcache_bench(max_count):
    from django.core.cache import get_cache
    cache = get_cache('varify.pipeline')
    variants = Variant.objects.values_list('md5', 'id')[:max_count]
    for md5, pk in variants:
        cache.set(md5, pk)


def memory_bench(max_count):
    dict(Variant.objects.values_list('md5', 'id')[:max_count])


if __name__ == '__main__':
    import timeit

    print
    print 'VARIANT IN-MEMORY DICT VS. MEMCACHE'
    print '---\n'

    for max_count in MAX_COUNTS:
        count = len(Variant.objects.values('pk')[:max_count])

        print 'N: {0}'.format(count)

        t1 = min(timeit.repeat('memory_bench({0})'.format(count),
                 setup='from __main__ import memory_bench', number=ITERATIONS))

        print 'In-memory dict:', t1

        t2 = min(timeit.repeat('memcache_bench({0})'.format(count),
                 setup='from __main__ import memcache_bench',
                 number=ITERATIONS))
        print 'Memcache:', t2

        print 'Diff:', round(t2 / t1, 1), 'x'

        print

        if count < max_count:
            print('Exiting: count less than max_count')
            break
