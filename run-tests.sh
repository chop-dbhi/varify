#!/bin/sh

ARGS="$@"

if [ ! $ARGS ]; then
    ARGS="assessments sample_load_process geneset_form south_tests commands"
fi

DJANGO_SETTINGS_MODULE='tests.settings' PYTHONPATH=. `which django-admin.py` test $ARGS
