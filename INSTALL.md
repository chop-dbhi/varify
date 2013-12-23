# Installation for RedHat Enterprise Linux Server 6.3

## System Setup

### Yum Development Tools

```bash
sudo yum groupinstall -y 'Development Tools'
```

### devuser

```bash
sudo /usr/sbin/adduser devuser -m
sudo chmod 770 /home/devuser
sudo chmod g+s /home/devuser
sudo mkdir -p /home/devuser/webapps
```

### nginx

```bash
echo '[nginx]
name=nginx repo
baseurl=http://nginx.org/packages/rhel/6/$basearch/
gpgcheck=0
enabled=1' | sudo tee /etc/yum.repos.d/nginx.repo

sudo yum install -y nginx
sudo /etc/init.d/nginx start
sudo /sbin/chkconfig --levels 2345 nginx on
sudo /usr/sbin/usermod -aG devuser nginx
```

#### SSL Certs

Assuming SSL certs are available. Replace the `<...>` variables with
the paths to the appropriate files.

```bash
sudo mkdir -p /etc/nginx/ssl
sudo mv <ssl_cert.pem> <ssl_cert.key> /etc/nginx/ssl

echo 'server {
    listen       443 default ssl;
    server_name  _;

    ssl                         on;
    ssl_certificate             ssl/<ssl_cert.pem>;
    ssl_certificate_key         ssl/<ssl_cert.key>;

    ssl_protocols  SSLv2 SSLv3 TLSv1;
    ssl_ciphers  HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers   on;

    ssl_session_timeout  5m;

    location / {
        root   /usr/share/nginx/html;
        index  index.html index.htm;
    }
}' | sudo tee /etc/nginx/conf.d/ssl.conf
```

#### Add iptables entry

If SSL is used, replace `<PORT>` with 443, otherwise 80.

```bash
sudo iptables -A INPUT -m state --state NEW -m tcp -p tcp --dport <PORT> -j ACCEPT
sudo /sbin/service iptables save
sudo /sbin/service iptables restart
```

### Python

```bash
sudo yum install -y bzip2-devel readline-devel sqlite-devel zlib-devel openssl-devel tk-devel

wget http://python.org/ftp/python/2.7.3/Python-2.7.3.tar.bz2
tar jxf Python-2.7.3.tar.bz2 && cd Python-2.7.3
./configure --enable-shared
make
sudo make altinstall

echo '/usr/local/lib' | sudo tee -a /etc/ld.so.conf
sudo /sbin/ldconfig
```

### Base Packages

```bash
curl http://python-distribute.org/distribute_setup.py | sudo /usr/local/bin/python2.7
curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | sudo /usr/local/bin/python2.7
sudo pip install virtualenv
```

### Supervisor

```bash
sudo pip install supervisor
sudo /usr/sbin/groupadd supervisor

echo '#!/bin/bash
#
# Startup script for the Supervisor server
#
# Tested with Red Hat Enterprise Linux Server release 5.5
#
# chkconfig: 2345 85 15
# description: Supervisor is a client/server system that allows its users to \
#              monitor and control a number of processes on UNIX-like \
#              operating systems.
#
# processname: supervisord
# pidfile: /var/run/supervisord.pid

# Source function library.
. /etc/rc.d/init.d/functions

RETVAL=0
prog="supervisord"
SUPERVISORD=/usr/local/bin/supervisord
CONFIG_FILE=/etc/supervisord.conf
PID_FILE=/var/run/supervisord.pid

start()
{
        echo -n $"Starting $prog: "
        $SUPERVISORD --configuration $CONFIG_FILE --pidfile $PID_FILE && success || failure
        RETVAL=$?
        echo
        return $RETVAL
}

stop()
{
        echo -n $"Stopping $prog: "
        killproc -p $PID_FILE -d 10 $SUPERVISORD
        RETVAL=$?
        echo
}

reload()
{
        echo -n $"Reloading $prog: "
        if [ -n "`pidfileofproc $SUPERVISORD`" ] ; then
            killproc $SUPERVISORD -HUP
        else
            # Fails if the pid file does not exist BEFORE the reload
            failure $"Reloading $prog"
        fi
        sleep 1
        if [ ! -e $PID_FILE ] ; then
            # Fails if the pid file does not exist AFTER the reload
            failure $"Reloading $prog"
        fi
        RETVAL=$?
        echo
}

case "$1" in
        start)
                start
                ;;
        stop)
                stop
                ;;
        restart)
                stop
                start
                ;;
        reload)
                reload
                ;;
        status)
                status -p $PID_FILE $SUPERVISORD
                RETVAL=$?
                ;;
        *)
                echo $"Usage: $0 {start|stop|restart|reload|status}"
                RETVAL=1
esac
exit $RETVAL' | sudo tee /etc/init.d/supervisord

chmod +x /etc/init.d/supervisord
sudo /sbin/chkconfig --add supervisord
sudo /sbin/chkconfig --level 2345 supervisord on

sudo mkdir -p /etc/supervisor.d /var/log/supervisor

echo '[unix_http_server]
file=/tmp/supervisor.sock
chmod=0770
chown=nobody:supervisor

[supervisord]
logfile=/var/log/supervisor/supervisord.log
childlogdir=/var/log/supervisor

[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

[supervisorctl]
serverurl=unix:///tmp/supervisor.sock

[include]
files = /etc/supervisor.d/*.ini' | sudo tee /etc/supervisord.conf
```


### Memcache

```bash
sudo yum install -y memcached
sudo /etc/init.d/memcached start
sudo /sbin/chkconfig --level 2345 memcached on
```

### Ruby

```bash
sudo yum install -y ruby
```

#### Ruby Gems

```bash
wget http://production.cf.rubygems.org/rubygems/rubygems-1.8.24.tgz
tar zxf rubygems-1.8.24.tgz
cd rubygems-1.8.24 && sudo ruby setup.rb
```

#### Gems

```bash
sudo gem install sass bourbon
```

### NodeJS

```bash
wget http://nodejs.org/dist/v0.8.14/node-v0.8.14.tar.gz
tar zxf node-v0.8.14.tar.gz
cd node-v0.8.14
./configure
make
sudo make install
```

#### Node Libraries

```bash
sudo npm install -g coffee-script
```

### PostgreSQL

**It is highly recommended a separate VM is used for hosting the database server.**

```bash
echo '[postgresql]
name=Official PostgreSQL Repo
baseurl=http://yum.postgresql.org/9.2/redhat/rhel-6-x86_64/
gpgcheck=0
enabled=1' | sudo tee /etc/yum.repos.d/postgresql.repo

sudo yum install -y postgresql92 postgresql92-libs postgresql92-devel
sudo /etc/init.d/postgresql-9.2 initdb
sudo /etc/init.d/postgresql-9.2 start
```

_TODO programmatic commands for creating the database and user_

```bash
echo 'export PATH=/usr/pgsql-9.2/bin:$PATH' | sudo tee /etc/profile.d/postgres.sh
```

### Redis

```bash
sudo yum install -y redis
sudo /etc/init.d/redis start
sudo /sbin/chkconfig --levels 2345 redis on
```

### Scala

_This is only required for to perform HGMD ETL._

```bash
echo '[typesafe]
name=Typesafe Rpm Repository
baseurl=http://rpm.typesafe.com/
gpgcheck=0
enabled=1' | sudo tee /etc/yum.repos.d/typesafe.repo

sudo yum install -y scala java-1.7.0-openjdk
```

## Deployment

The simplest way to deploy Varify is to use the supplied `deploy`
[Fabric](http://docs.fabfile.org/en/1.4/index.html) command. Your user on
the remote machine must have permission to perform the various deployment
tasks. This currently includes being in the `devuser` and `supervisor`
Unix groups (these were created above).

Follow the steps below to deploy to a remote host.

#### Clone Varify locally

```bash
git clone https://github.com/cbmi/varify.git
```

#### Install Fabric

This must version 1.4.x since 1.5+ is broken at the time of this writing. _This
can of course be done in a virtual environment as well to not pollute your
system site-packages._

```bash
pip install fabric
```

#### Deploy

Deploy to a particular host such as `production` on a given branch and commit
SHA1 (or tag). The branch is optional, however the commit is not, this is by
design to prevent deploying the wrong commit.

```bash
fab -H <HOST> deploy:<BRANCH>@<COMMIT>
```

## Adding Hosts

The `.fabhosts` file contains target environments which define the deployment
and environment variables such as the hostname, paths, etc. Unless a _new_
host is being added, this file does not need to be modified.

### Config files

There are four files that need to be added to support a new host. Each are
named after the host, e.g. `production`.

- `settings/<HOST>.py`
- `server/nginx/<HOST>.conf`
- `server/uwsgi/<HOST>.ini`
- `server/supervisor/<HOST>.ini`

The `fabfile.py` commands move these files to the specific locations on the
remote host. Read more by running:

```bash
python -c 'import fabfile;help(fabfile)'
```
