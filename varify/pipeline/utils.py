import logging
import ConfigParser
from functools import wraps
from django.dispatch import Signal
from rq.decorators import job as _rq_job
from django_rq.queues import get_queue

log = logging.getLogger(__name__)


class ManifestReader(object):
    def __init__(self, path):
        self.path = path
        self.config = ConfigParser.ConfigParser()
        try:
            self.config.read([path])
        except ConfigParser.MissingSectionHeaderError:
            log.warning('Empty manifest file', extra={
                'path': self.path,
            })

    def option(self, section, option, default=None):
        if self.config.has_option(section, option):
            return self.config.get(section, option)
        log.warning('No manifest option: {0}.{1}'.format(section, option),
                    extra={'path': self.path})
        return default

    def has_section(self, section):
        return self.config.has_section(section)

    def section(self, section):
        if self.config.has_section(section):
            return dict(self.config.items(section))
        log.warning('No manifest section: {0}'.format(section), extra={
            'path': self.path,
        })
        return {}

    def marked_for_load(self):
        load = self.option('general', 'load')
        return load is not None and load.lower() == 'true'


class _job(_rq_job):
    def __call__(self, f):
        super(_job, self).__call__(f)

        # Function that acts as the receiver for channels
        @wraps(f)
        def receive(signal, sender, **kwargs):
            f.delay(**kwargs)

        @wraps(f)
        def watch(channel):
            channel.subscribe(receive)

        f.receive = receive
        f.watch = watch

        return f


# Taken from django-rq code base to utilize custom _job decorator class
def job(func_or_queue=None, connection=None, *args, **kwargs):
    """
    The same as RQ's job decorator, but it works automatically works out
    the ``connection`` argument from RQ_QUEUES.

    And also, it allows simplified ``@job`` syntax to put job into
    default queue.
    """
    if callable(func_or_queue):
        func = func_or_queue
        queue = 'default'
    else:
        func = None
        queue = func_or_queue or 'default'

    if not isinstance(queue, basestring):
        queue = unicode(queue)

    try:
        queue = get_queue(queue)
        if connection is None:
            connection = queue.connection
    except KeyError:
        pass

    decorator = _job(queue, connection=connection, *args, **kwargs)
    if func:
        return decorator(func)
    return decorator


class Channel(object):
    def __init__(self, name, providing_args):
        self.name = name
        self.signal = Signal(providing_args=providing_args)

    def __str__(self):
        return str(self.name)

    def __unicode__(self):
        return unicode(self.name)

    def __repr__(self):
        return '<Channel: {0}>'.format(self.name)

    def publish(self, **kwargs):
        "Publishes to the channel which notifies all connected handlers."
        log.debug('Publish to {0}'.format(self))
        self.signal.send(sender=self.name, **kwargs)

    def subscribe(self, receiver):
        "Subscribes an external handler to this channel."
        log.debug('{0}.{1} subscribe to {2}'
                  .format(receiver.__module__, receiver.__name__, self))
        self.signal.connect(receiver)
