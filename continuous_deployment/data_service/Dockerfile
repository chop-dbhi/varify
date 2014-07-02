FROM phusion/baseimage
MAINTAINER davidsonl2@email.chop.edu

ENV APP_NAME varify_data_service

# Add the PostgreSQL PGP key to verify their Debian packages.
# It should be the same key as https://www.postgresql.org/media/keys/ACCC4CF8.asc
RUN curl http://apt.postgresql.org/pub/repos/apt/ACCC4CF8.asc | apt-key add -

# Add PostgreSQL's repository. It contains the most recent stable release
#     of PostgreSQL, ``9.3``.
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ precise-pgdg main" > /etc/apt/sources.list.d/pgdg.list

# Update the Ubuntu and PostgreSQL repository indexes
RUN apt-get update

# Install ``python-software-properties``, ``software-properties-common`` and PostgreSQL 9.3
#  There are some warnings (in red) that show up during the build. You can hide
#  them by prefixing each apt-get statement with DEBIAN_FRONTEND=noninteractive
RUN apt-get -y -q install python-software-properties software-properties-common
RUN apt-get -y -q install postgresql-9.3 postgresql-client-9.3 postgresql-contrib-9.3

# Note: The official Debian and Ubuntu images automatically ``apt-get clean``
# after each ``apt-get``

# Adjust PostgreSQL configuration so that remote connections to the
# database are possible.
# TODO: Add pg_hba.conf from static file in repository
ADD configuration/pg_hba.conf /etc/postgresql/9.3/main/pg_hba.conf

# And add ``listen_addresses`` to ``/etc/postgresql/9.3/main/postgresql.conf``
ADD configuration/postgresql.conf /etc/postgresql/9.3/main/postgresql.conf

# Add bootstrap.sql to facilitate bootstrapping commands run at startup
ADD configuration/bootstrap.sql /bootstrap.sql

ADD start.sh /start.sh
RUN chmod 0755 /start.sh

# Expose the PostgreSQL port
EXPOSE 5432

# Add VOLUMEs to allow backup of config, logs and databases
VOLUME  ["/etc/postgresql", "/var/log/postgresql", "/var/lib/postgresql"]

# Set the default command to run when starting the container
CMD ["/start.sh"]
