#from global_settings import LDAP, INSTALLED_APPS

# Uncomment to put the application in non-debug mode. This is useful
# for testing error handling and messages.
DEBUG = False
TEMPLATE_DEBUG = DEBUG

# Override this to match the application endpoint


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'varifydb',
        'USER': 'varify',
        'PASSWORD': 'varify',
        'HOST': 'localhost',
    },
}

# Non-restricted email port for development, run in a terminal:
# python -m smtpd -n -c DebuggingServer localhost:1025
EMAIL_SUBJECT_PREFIX = '[Varify Headless Testing] '

# This is used as a "seed" for various hashing algorithms. This must be set to
# a very long random string (40+ characters)
SECRET_KEY = '1234536yskkshkka9937745204981921jhkkakis992763yhahha'


SITE_ID = 2


# Sentry is collating the error messages..
ADMINS = (
    ('Le Mar Davidson', 'davidsonl2@email.chop.edu'),
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
            
VARIFY_SAMPLE_DIRS = (
    '/home/vagrant/webapps/varify-os/samples/',
)
