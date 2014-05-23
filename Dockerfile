# Harvest

# Use the base docker container
from reslnops01.research.chop.edu:5000/harvest_minimal

MAINTAINER Le Mar Davidson "davidsonl2@email.chop.edu"

# Scala needed for DataExpress scripts
RUN apt-get update -qq
RUN apt-get install -y openjdk-6-jre libjansi-java
RUN curl -O http://www.scala-lang.org/files/archive/scala-2.9.3.deb
RUN dpkg -i scala-2.9.3.deb
RUN apt-get update
RUN apt-get install -y scala

RUN apt-get update -qq --fix-missing
RUN apt-get install -y curl python-dev python-setuptools supervisor git-core libpq-dev libldap2-dev libsasl2-dev openssl memcached  build-essential libssl-dev redis-server ruby rubygems libxml2-dev libxslt1-dev  zlib1g-dev wget

RUN (cd /tmp && git clone https://github.com/joyent/node.git)
RUN (cd /tmp/node && git checkout v0.10.26 && ./configure && make && make install)
RUN (apt-get install -y npm)
RUN (npm install -g coffee-script)
RUN (gem install sass)

# Python dependencies

RUN /opt/ve/harvest-app/bin/pip install django==1.5.5
RUN /opt/ve/harvest-app/bin/pip install south==0.8.2
RUN /opt/ve/harvest-app/bin/pip install python-memcached==1.48
RUN /opt/ve/harvest-app/bin/pip install coverage
RUN /opt/ve/harvest-app/bin/pip install django-siteauth==0.9b1
RUN /opt/ve/harvest-app/bin/pip install raven==3.3.9
RUN /opt/ve/harvest-app/bin/pip install uwsgi
RUN /opt/ve/harvest-app/bin/pip install rq==0.3.8
RUN /opt/ve/harvest-app/bin/pip install django-rq==0.5.1
RUN /opt/ve/harvest-app/bin/pip install rq-dashboard==0.3.1
RUN /opt/ve/harvest-app/bin/pip install django-rq-dashboard
RUN /opt/ve/harvest-app/bin/pip install dj-database-url==0.2.2
RUN /opt/ve/harvest-app/bin/pip install south==0.8.4
RUN /opt/ve/harvest-app/bin/pip install fabric==1.8.0
RUN /opt/ve/harvest-app/bin/pip install uWSGI
RUN /opt/ve/harvest-app/bin/pip install restlib2==0.3.9
RUN /opt/ve/harvest-app/bin/pip install python-etcd==0.3.0
RUN /opt/ve/harvest-app/bin/pip install psycopg2==2.5.1
RUN /opt/ve/harvest-app/bin/pip install python-ldap==2.4.13
RUN /opt/ve/harvest-app/bin/pip install pycrypto==2.3
RUN /opt/ve/harvest-app/bin/pip install avocado==2.3.0
RUN /opt/ve/harvest-app/bin/pip install serrano==2.3.0
RUN /opt/ve/harvest-app/bin/pip install modeltree==1.1.7
RUN /opt/ve/harvest-app/bin/pip install django-haystack==2.0
RUN /opt/ve/harvest-app/bin/pip install python-memcached==1.53
RUN /opt/ve/harvest-app/bin/pip install django_extensions
RUN /opt/ve/harvest-app/bin/pip install django-siteauth==0.9b1
RUN /opt/ve/harvest-app/bin/pip install whoosh==2.5
RUN /opt/ve/harvest-app/bin/pip install Markdown
RUN /opt/ve/harvest-app/bin/pip install pycap
RUN /opt/ve/harvest-app/bin/pip install csvkit

# Add the application files
ADD . /opt/apps/harvest-app

# Ensure all python requirements are met
ENV APP_NAME varify
RUN /opt/ve/harvest-app/bin/pip install -r /opt/apps/harvest-app/requirements.txt --use-mirrors

# Add customer start script for continuous deployment/override default
ADD continuous_integration/.docker/scripts/start.sh /usr/local/bin/start

RUN chmod +x /usr/local/bin/start

EXPOSE 8000
