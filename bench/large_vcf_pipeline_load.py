import _setenv  # noqa
import sys
import time
import vcf
from memory_profiler import profile
from cStringIO import StringIO
from varify.variants.pipeline.utils import VariantStream
from varify.pipeline.load import batch_stream


def main(cache, cache_size=1000):
    with open(sys.argv[-1]) as source:
        stream = VariantStream(source, use_cache=cache, cache_size=cache_size)

        buff = StringIO()

        count = 0
        while True:
            empty = batch_stream(buff, stream)
            stream.variant_md5s = []
            count += 1
            sys.stdout.write('{0} complete\r'.format(count))
            sys.stdout.flush()
            if empty:
                print
                break


@profile
def baseline():
    count = -1
    with open(sys.argv[-1]) as source:
        for i, line in enumerate(source):
            if i % 1000 == 0:
                count += 1
                sys.stdout.write('{0} complete\r'.format(count))
                sys.stdout.flush()


@profile
def vcf_baseline():
    max_count = 20
    count = -1
    with open(sys.argv[-1]) as source:
        fin = vcf.Reader(source, preserve_order=False)
        for i, line in enumerate(fin):
            if i % 1000 == 0:
                count += 1
                sys.stdout.write('{0} complete\r'.format(count))
                sys.stdout.flush()
                if count == max_count:
                    break


@profile
def main_no_cache():
    main(cache=False)


@profile
def main_with_cache_10():
    main(cache=True, cache_size=10)


@profile
def main_with_cache_100():
    main(cache=True, cache_size=100)


@profile
def main_with_cache_1000():
    main(cache=True, cache_size=1000)


@profile
def main_with_cache_10000():
    main(cache=True, cache_size=10000)


if __name__ == '__main__':
    print
    print 'VARIANT STREAM PERF'
    print '---\n'

    print 'VCF Baseline'
    t0 = time.time()
    vcf_baseline()
    print 'Time:', round(time.time() - t0, 1), 'seconds'

    print 'No cache'
    t0 = time.time()
    main_no_cache()
    print 'Time:', round(time.time() - t0, 1), 'seconds'

    print 'Cache: 10'
    t0 = time.time()
    main_with_cache_10()
    print 'Time:', round(time.time() - t0, 1), 'seconds'

    print 'Cache: 100'
    t0 = time.time()
    main_with_cache_100()
    print 'Time:', round(time.time() - t0, 1), 'seconds'

    print 'Cache: 1000'
    t0 = time.time()
    main_with_cache_1000()
    print 'Time:', round(time.time() - t0, 1), 'seconds'

    print 'Cache: 10000'
    t0 = time.time()
    main_with_cache_10000()
    print 'Time:', round(time.time() - t0, 1), 'seconds'
