import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'

from django.core import management

apps = sys.argv[1:]

if not apps:
    apps = [
        'assessments',
        'south_tests',
        'geneset_form',
        'export',
        'resources',
        'samples'
    ]

management.call_command('test', *apps)
