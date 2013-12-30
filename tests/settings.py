from varify.conf.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'varifydb',
    },
}

INSTALLED_APPS = (
    'tests.cases.south_tests',
    'tests.cases.geneset_form',
    'tests.cases.sample_load_process',
    'tests.cases.commands',

    'varify',

    'varify.raw',
    'varify.raw.sources',

    'varify.assessments',
    'varify.genome',
    'varify.phenotypes',
    'varify.genes',
    'varify.variants',
    'varify.samples',
    'varify.literature',
    'varify.pipeline',

    'varify.support',

    'south',
    'guardian',
    'django_rq',
    'sts',

    'serrano',
    'avocado',
    'avocado.export',
    'modeltree',

    # built-in Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.markup',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
)

TEST_RUNNER = 'tests.runner.ProfilingTestRunner'
TEST_PROFILE = 'unittest.profile'

RQ_QUEUES = {
    'default': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
    },
    'samples': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
    },
    'variants': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
    },
    'effects': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
    },
    'results': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
    },
}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'rq_console': {
            'format': '%(asctime)s %(message)s',
            'datefmt': '%H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler'
        },
        'rq_console': {
            'level': 'DEBUG',
            'class': 'rq.utils.ColorizingStreamHandler',
            'formatter': 'rq_console',
            'exclude': ['%(asctime)s'],
        }
    },
    'loggers': {
        'varify': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'tests': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'rq.worker': {
            'handlers': ['rq_console'],
            'level': 'DEBUG',
        },
    }
}

SOUTH_TESTS_MIGRATE = False

SECRET_KEY = 'acb123'
