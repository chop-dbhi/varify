#!/bin/sh

ARGS="$@"

if [ ! $ARGS ]; then
    ARGS="varify sample_load_process geneset_form south_tests"
fi

DJANGO_SETTINGS_MODULE='tests.settings' PYTHONPATH=. `which django-admin.py` test $ARGS
