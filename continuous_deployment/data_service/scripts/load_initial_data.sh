export SAMPLE_DATA_URL=https://github.com/cbmi/varify-demo-data/archive/0.1.tar.gz
export LANG=en_US.UTF-8

#cp /opt/apps/harvest-app/headless_tests/data_setup/initial_data.json /opt/apps/harvest-app/
cd /opt/apps/harvest-app && DJANGO_SETTINGS_MODULE=varify.conf.settings /opt/ve/harvest-app/bin/python /bin/manage.py syncdb
cd /opt/apps/harvest-app && DJANGO_SETTINGS_MODULE=varify.conf.settings /opt/ve/harvest-app/bin/python /bin/manage.py migrate
cd /opt/apps/harvest-app && DJANGO_SETTINGS_MODULE=varify.conf.settings /opt/ve/harvest-app/bin/python -c "from django.db import DEFAULT_DB_ALIAS as database; from django.contrib.auth.models import User; User.objects.db_manager(database).create_superuser('test','your@email.address.com','CHANGEME')"
cd /opt/apps/harvest-app && DJANGO_SETTINGS_MODULE=varify.conf.settings ./bin/manage.py variants load --evs --1000g --sift --polyphen2 > variants.load.txt 2>&1 &
cd /opt/apps/harvest-app && DJANGO_SETTINGS_MODULE=varify.conf.settings ./bin/manage.py samples allele-freqs > samples.allele-freqs.txt 2>&1 &

cd /opt/apps/harvest-app/continuous_deployment/data_service/data/ && wget $SAMPLE_DATA_URL -O varify-demo-data-0.1.tar.gz
cd /opt/apps/harvest-app/continuous_deployment/data_service/data/ && tar -xvf varify-demo-data-0.1.tar.gz -C varify-demo-data-0.1
cd /opt/apps/harvest-app && DJANGO_SETTINGS_MODULE=varify.conf.settings ./bin/manage.py samples queue continuous_deployment/data_service/data/varify-demo-data-0.1
