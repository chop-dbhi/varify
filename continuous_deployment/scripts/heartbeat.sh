#!/bin/bash

cd /opt/apps/harvest-app/
GIT_COMMIT=`git rev-parse --short HEAD`
GIT_BRANCH=`git rev-parse --abbrev-ref HEAD`

while true; do
    curl -L http://$ETCD_HOST:4001/v2/keys/applications/$APP_NAME/status/$GIT_BRANCH/$GIT_COMMIT/up -XPUT -d value=true -d ttl=30
    sleep 30
done
