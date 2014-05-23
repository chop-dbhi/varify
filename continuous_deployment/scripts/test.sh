#!/bin/bash
cd /opt/apps/harvest-app/ && /opt/ve/harvest-app/bin/fab get_configuration:noinput=True
cd /opt/apps/harvest-app/ && /opt/ve/harvest-app/bin/python bin/manage.py syncdb --noinput
cd /opt/apps/harvest-app/ && /opt/ve/harvest-app/bin/python bin/manage.py migrate --noinput
cd /opt/apps/harvest-app/ && /opt/ve/harvest-app/bin/python bin/manage.py collectstatic --noinput
/opt/apps/harvest-app/run-tests.sh
