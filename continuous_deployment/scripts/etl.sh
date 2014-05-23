#!/bin/bash

export PATH=/opt/ve/harvest-app/bin/:$PATH
cd /opt/apps/harvest-app/ && /opt/ve/harvest-app/bin/fab get_configuration:noinput=True
cd /opt/apps/harvest-app/ && /opt/ve/harvest-app/bin/python bin/manage.py etl $APP_ENV
