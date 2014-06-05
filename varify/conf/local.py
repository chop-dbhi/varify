import os
import json
from base import *
import dj_database_url

curdir = os.path.dirname(os.path.abspath(__file__))
project_settings = json.loads(open(os.path.join(curdir, '../../.project_config.json'), 'r').read())['project_settings']

DATABASES = {
    'default': dj_database_url.parse(project_settings['local']['databases']['default']),
}

EMAIL_PORT = project_settings['local']['django']['EMAIL_PORT']

EMAIL_SUBJECT_PREFIX = '[brand_new Local] '

DEBUG = project_settings['local']['django']['DEBUG']

FORCE_SCRIPT_NAME = project_settings['local']['django']['FORCE_SCRIPT_NAME']

SECRET_KEY = project_settings['local']['django']['SECRET_KEY']

# eHB Integration

SERVICE_CLIENT_SETTINGS = project_settings['local']['django']['SERVICE_CLIENT_SETTINGS'],

PROTOCOL_PROPS = project_settings['local']['django']['PROTOCOL_PROPS']
