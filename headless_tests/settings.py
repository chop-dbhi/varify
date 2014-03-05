from global_settings import  INSTALLED_APPS
import os, sys

#This is configured for varify project.  Replace varify with 
#specific/correct project name and if neccessary remove 
#varify loading setup

# Uncomment to put the application in non-debug mode. This is useful
# for testing error handling and messages.
DEBUG = True
TEMPLATE_DEBUG = DEBUG

# Override this to match the application endpoint

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': 'localhost',
    },
}

# Non-restricted email port for development, run in a terminal:
# python -m smtpd -n -c DebuggingServer localhost:1025
EMAIL_SUBJECT_PREFIX = '[<Project Name> Headless Testing] '

# This is used as a "seed" for various hashing algorithms. This must be set to
# a very long random string (40+ characters)
SECRET_KEY = '1234536yskkshkka9937745204981921jhkkakis992763yhahha'


# Sentry is collating the error messages..
ADMINS = (
    ('FirstName LastName ', 'put@your_email_address.com'),
)

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
}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': './headless_tests/test/log/project.log',
        },
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'avocado': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'serrano': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'varify': {
            'handlers': ['console','file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        './varify/samples/management/subcommands/queue.pyc': {
	    'handlers': ['console','file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'rq.worker': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
            
VARIFY_SAMPLE_DIRS = (
    './headless_tests/data_setup/samples',
)
