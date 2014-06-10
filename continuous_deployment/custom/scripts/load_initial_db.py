ENV SAMPLE_DATA_URL https://github.com/cbmi/varify-demo-data/archive/0.1.tar.gz
ENV LANG en_US.UTF-8

RUN (python -c "from django.db import DEFAULT_DB_ALIAS as database; from django.contrib.auth.models import User; User.objects.db_manager(database).create_superuser('username','davidsonl2@email.chop.edu','pw')" )


RUN (cp /opt/apps/harvest-app/headless_tests/data_setup/initial_data.json /opt/apps/harvest-app/)
RUN (cd /opt/apps/harvest-app && ./bin/manage.py syncdb)
RUN (cd /opt/apps/harvest-app && ./bin/manage.py migrate)
RUN (cd /opt/apps/harvest-app && DJANGO_SETTINGS_MODULE=varify.conf.settings ./bin/manage.py variants load --evs --1000g --sift --polyphen2 > variants.load.txt 2>&1 & )
RUN (cd /opt/apps/harvest-app && DJANGO_SETTINGS_MODULE=varify.conf.settings ./bin/manage.py samples allele-freqs > samples.allele-freqs.txt 2>&1 & )
