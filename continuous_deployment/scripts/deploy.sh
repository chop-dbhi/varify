#!/bin/bash

cd /opt/apps/harvest-app/src/bin && /opt/ve/harvest-app/bin/python manage.py syncdb --noinput
mkdir /opt/apps/harvest-app/src/static
cd /opt/apps/harvest-app/src/bin && /opt/ve/harvest-app/bin/python manage.py collectstatic --noinput
supervisord -c /opt/supervisor_deploy.conf -n
