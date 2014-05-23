#!/bin/bash

# Going to need to provide etcd address here to bootstrap
cd /opt/apps/harvest-app/ && /opt/ve/harvest-app/bin/fab get_configuration:noinput=True
cd /opt/apps/harvest-app/ && /opt/ve/harvest-app/bin/python bin/manage.py syncdb --noinput
cd /opt/apps/harvest-app/ && /opt/ve/harvest-app/bin/python bin/manage.py migrate --noinput
cd /opt/apps/harvest-app/ && /opt/ve/harvest-app/bin/python bin/manage.py collectstatic --noinput
supervisord -c /opt/supervisor_run.conf -n
