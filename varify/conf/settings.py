import os
import json
from base import *
import dj_database_url

curdir = os.path.dirname(os.path.abspath(__file__))
project_settings = json.loads(open(os.path.join(curdir, '../../.project_config.json'), 'r').read())['project_settings']

environment = get_env_variable('APP_ENV')

if environment not in project_settings.keys():
    error_msg = "Settings for {0} environment not found in project configuration.".format(environment)
    raise ImproperlyConfigured(error_msg)

# Check here to see if db details exist in env
LINKED_DB_IP = os.environ.get('DB_PORT_5432_TCP_ADDR')
# Check here to see if memcache details exist in env
LINKED_MEMCACHE = os.environ.get('MC_PORT_11211_TCP_ADDR')

if LINKED_DB_IP:
    DATABASES = {
        'default': dj_database_url.parse('postgresql://docker:docker@{0}:5432/varify'.format(LINKED_DB_IP)),
        'portal': dj_database_url.parse(project_settings[environment]['databases']['portal']),
    }
else:
    DATABASES = {
        'default': dj_database_url.parse(project_settings[environment]['databases']['default']),
        'portal': dj_database_url.parse(project_settings[environment]['databases']['portal']),
    }


if LINKED_MEMCACHE:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': '{0}:11211'.format(LINKED_MEMCACHE),
            'KEY_PREFIX': 'varify',
            'VERSION': 1,
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
        }
    }

EMAIL_PORT = project_settings[environment]['django']['EMAIL_PORT']

EMAIL_SUBJECT_PREFIX = '[brand_new Local] '

DEBUG = project_settings[environment]['django']['DEBUG']

FORCE_SCRIPT_NAME = project_settings[environment]['django']['FORCE_SCRIPT_NAME']

SECRET_KEY = project_settings[environment]['django']['SECRET_KEY']

# eHB Integration

SERVICE_CLIENT_SETTINGS = project_settings[environment]['django']['SERVICE_CLIENT_SETTINGS'],

PROTOCOL_PROPS = project_settings[environment]['django']['PROTOCOL_PROPS']
