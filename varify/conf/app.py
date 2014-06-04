import os

# Import global settings to make it easier to extend settings.
from django.conf.global_settings import *

# Import the project module to calculate directories relative to the module
# location.
PROJECT_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../..')

# List all Django apps here. Note that standard Python libraries should not
# be added to this list since Django will not recognize them as apps anyway.
# An app is really only an "app" if a `models` module or package is defined.
# Read more about projects vs. apps here:
# https://docs.djangoproject.com/en/1.3/intro/tutorial01/#creating-models
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.markup',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    'varify',

    'varify.raw',
    'varify.raw.sources',

    'varify.assessments',
    'varify.genome',
    'varify.genes',
    'varify.variants',
    'varify.phenotypes',
    'varify.samples',
    'varify.literature',

    'varify.support',

    'varify.pipeline',

    'varify',
    'varify.chop',

    'sts',
    'haystack',
    'south',
    'registration',
    'siteauth',
    'tracking',
    'bootstrapform',
    'widget_tweaks',
    'django_rq',
    'django_rq_dashboard',

    'serrano',
    'avocado',
    'avocado.events',
    'avocado.export',
    'modeltree',
    'guardian',
    'reversion',
)

#
# ADMINISTRATIVE
#

# Admins receive any error messages by email if DEBUG is False
ADMINS = (
    ('Don Naegely', 'naegelyd@email.chop.edu')
)

# Managers receive broken link emails if SEND_BROKEN_LINK_EMAILS is True
MANAGERS = ADMINS

# List of IP addresses which will show debug comments
INTERNAL_IPS = ('127.0.0.1', '::1')

DEBUG = True
TEMPLATE_DEBUG = DEBUG


#
# DATABASES
# Each database can be specified here, but passwords should be in a separate
# file that is not versioned. Use ``local_settings.py``.
#

DATABASES = {}

# Database routers can useful for delegating database operations transparently
# to different databases depending on what data is being acted on. For Harvest
# instances that make use of an existing database, it is typically never
# desirable to create all the Harvest application tables in this database, but
# rather have a separate database for this purpose. That way the "data"
# database does not need to be changed.
DATABASE_ROUTERS = {}


#
# LOCALITY
#

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = None

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = False


#
# STATIC AND MEDIA
# The application's static files should be placed in the STATIC_ROOT in
# addition to other static files found in third-party apps. The MEDIA_ROOT
# is intended for user uploaded files.
#

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, '_site/media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_PATH, '_site/static')

# URL prefix for static files.
# Bust the cache whenenver new versions occur. By reading the latest commit id
# and using it in the static url path, we will force client browsers to pull
# new versions of JS, CSS, and HTML files. When a new version is pulled down
# and the server is restarted, this STATIC_URL path will change to include
# the new commit id which will invalidate the cached static files on the
# client-side on the next request. If the commit id cannot be read for
# whatever reason, the "unix time"(since epoch) is used to invalidate the
# client-side cache.
fp = os.path.join(
    os.path.dirname(__file__), '..', '..', '.git', 'refs', 'heads', 'master')
cache_id = ""
if os.path.exists(fp):
    f = open(fp, 'r')
    cache_id = str(f.read()).strip()[0:10]

if cache_id == "":
    # If we can't get the commit id then use the "unix time"
    #   http://en.wikipedia.org/wiki/Unix_time
    cache_id = int(time.mktime(datetime.datetime.now().timetuple()))

STATIC_URL = '/static/{}/'.format(cache_id)

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
# Put strings here, like "/home/html/static" or "C:/www/django/static".
# Always use forward slashes, even on Windows.
# Don't forget to use absolute paths, not relative paths.
STATICFILES_DIRS = ()

#
# TEMPLATES
#

# Project level templates and template directories that override
# third-party app templates.
TEMPLATE_DIRS = ()

# Context processors are simply functions that return a dict which augments the
# template context.
TEMPLATE_CONTEXT_PROCESSORS += (
    'django.core.context_processors.request',
    'varify.context_processors.static',
    'varify.context_processors.alamut',
)


#
# URLS
#

# FORCE_SCRIPT_NAME overrides the interpreted 'SCRIPT_NAME' provided by the
# web server. since the URLs below are used for various purposes outside of
# the WSGI application (static and media files), these need to be updated to
# reflect this discrepancy.
FORCE_SCRIPT_NAME = ''

ROOT_URLCONF = 'varify.conf.urls'

LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'
LOGIN_REDIRECT_URL = '/workspace/'

ALAMUT_URL = 'http://localhost:10000'

# For non-publicly accessible applications, the siteauth app can be used to
# restrict access site-wide.
SITEAUTH_ACCESS_ORDER = 'allow/deny'

SITEAUTH_ALLOW_URLS = (
    r'^$',
    r'^log(in|out)/',
    r'^password/reset/',
    r'^(static|support|register|verify)/',
    r'^api/samples/(?P<project>.+)/(?P<batch>.+)/(?P<sample>.+)/$',
    r'^api/chop/results/mrn/$',
)

#
# MIDDLEWARE
#

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'tracking.middleware.VisitorTrackingMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'siteauth.middleware.SiteAuthenticationMiddleware',
    'serrano.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'reversion.middleware.RevisionMiddleware',
)


#
# EMAIL
#

SUPPORT_EMAIL = 'cbmisupport@email.chop.edu'
DEFAULT_FROM_EMAIL = 'cbmisupport@email.chop.edu'
EMAIL_SUBJECT_PREFIX = '[Varify] '


#
# LOGGING
#

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


#
# CACHE
#

# For production environments, the memcached backend is highly recommended
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'KEY_PREFIX': 'varify',
        'VERSION': 1,
    },
    'varify.pipeline': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'KEY_PREFIX': 'varify.pipeline',
        'VERSION': 1,
    }
}

# Default cache seconds for a resource, use the `cache_page` decorator to
# change the amount of time for a given resource.
CACHE_MIDDLEWARE_SECONDS = 60

# This is not necessary to set if the above `KEY_PREFIX` value is set since
# the `KEY_PREFIX` namespaces all cache set by this application
CACHE_MIDDLEWARE_KEY_PREFIX = ''


#
# AUTHENTICATION
#

# Two additional auth backends for email-based (rather than username)
# and LDAP-based authentication. To use the LDAP authentication, the
# rematining LDAP settings (see below) must be defined.
AUTHENTICATION_BACKENDS = (
    'varify.backends.LdapBackend',
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
)

# LDAP Authentication Backend -- LDAP['PREBINDPW'] and LDAP['SERVER_URI']
# must be defined in local_settings.py since they are sensitive settings.
LDAP = {
    'DEBUG': False,
    'PREBINDDN': 'cn=Version Control,ou=AdminUsers,ou=Res,dc=research,dc=chop,dc=edu',
    'SEARCHDN': 'dc=chop,dc=edu',
    'SEARCH_FILTER': 'sAMAccountName=%s',
}

# django-registration
REGISTRATION_ACTIVATION_DAYS = 0
REGISTRATION_MODERATION = True
REGISTRATION_BACKENDS = {
    'default': 'accounts.backends.DefaultBackend',
}


#
# SESSIONS AND COOKIES
#

CSRF_COOKIE_NAME = 'varify_csrftoken'

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_COOKIE_AGE = 60 * 60 # 1 hour
SESSION_COOKIE_NAME = 'varify_sessionid'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = False


#
# OTHER PROJECT SETTINGS
#

USE_ETAGS = False

SEND_BROKEN_LINK_EMAILS = False
IGNORABLE_404_URLS = (
    r'robots\.txt$',
    r'favicon\.ico$',
)


#
# VARIOUS APP SETTINGS
#

# The primary key of the ``Site`` object for the Sites Framework
SITE_ID = 1

TRACK_ANONYMOUS_USERS = False
TRACK_PAGEVIEWS = False
TRACK_IGNORE_URLS = (
    r'^(static|media|admin|tracking)/',
)

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__), '../../whoosh.index'),
    }
}

# For django-guardian
ANONYMOUS_USER_ID = -1

MODELTREES = {
    'default': {
        'model': 'samples.result',
        'excluded_models': ['auth.user', 'avocado.datacontext'],
        'required_routes': [{
            'target': 'genes.gene',
            'source': 'genes.transcript',
        }, {
            'target': 'samples.cohort',
            'source': 'samples.cohortvariant',
        }, {
            'source': 'genes.gene',
            'target': 'genes.genephenotype',
        }, {
            'target': 'samples.cohortvariant',
            'source': 'variants.variant',
        }],
        'excluded_routes': [{
            'target': 'genes.gene',
            'source': 'literature.pubmed',
            'symmetrical': True,
        }],
    },
}

AVOCADO = {
    'METADATA_MIGRATION_APP': 'varify',
}


VARIFY_SAMPLE_DIRS = ()


CHOP_REDCAP_API_ENDPOINT = 'https://tiu.research.chop.edu/redcap/redcap/api/'

#
# SOLVEBIO SETTINGS (django_solvebio)
# SolveBio integration is optional (see README.md for more info).

try:
    __import__('solvebio')
except ImportError:
    pass
else:
    INSTALLED_APPS += ('solvebio.contrib.django_solvebio', )


# Get your API key from https://www.solvebio.com/account
SOLVEBIO_API_KEY = os.environ.get('SOLVEBIO_API_KEY', None)

# You can optionally bypass DB lookups by hardcoding aliases.
# The dict key is the alias and the value may be an ID or
# full dataset name. [OPTIONAL]
SOLVEBIO_DATASET_ALIASES = {
    'clinvar': 'ClinVar/0.0.2/ClinVar'
}
