from varify.conf.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'varifydb',
    },
}

INSTALLED_APPS = (
    'tests',
    'tests.cases.assessments',
    'tests.cases.samples',
    'tests.cases.south_tests',
    'tests.cases.geneset_form',
    'tests.cases.export',
    'tests.cases.resources',

    'varify',

    'vdw.assessments',
    'vdw.genes',
    'vdw.genome',
    'vdw.literature',
    'vdw.raw',
    'vdw.raw.sources',
    'vdw.phenotypes',
    'vdw.samples',
    'vdw.variants',

    'south',
    'guardian',
    'django_rq',
    'sts',
    'reversion',

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
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'tests.models.NullHandler'
        },
    },
    'loggers': {
        'vdw': {
            'level': 'DEBUG',
            'handler': 'null',
            'propogate': True
        }
    }
}

SOUTH_TESTS_MIGRATE = False

SECRET_KEY = 'acb123'
