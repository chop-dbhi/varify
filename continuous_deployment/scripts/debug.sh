#!/bin/bash

. /opt/ve/harvest-app/bin/activate
cd /opt/apps/harvest-app/

fab get_configuration:noinput=True
python bin/manage.py syncdb --noinput
python bin/manage.py migrate --noinput
python bin/manage.py loaddata fixtures/test_auth.json
python bin/manage.py collectstatic --noinput

supervisord -c /opt/supervisor_run.conf -n
