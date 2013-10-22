# Varify Development

## Dependencies

Listed are the download links to each dependency, however most OSes have a
package manager or binaries that can be easily installed. Most of the below
links describe alternate download and install methods.

On Mac OS X, [Homebrew](http://mxcl.github.com/homebrew/) is the recommended
way to install most of these of these libraries.

- [Python 2.7](http://python.org/download/releases/2.7.3/)
- [Ruby 1.8.7+](http://www.ruby-lang.org/en/downloads/)
- [RubyGems 1.3+](http://rubygems.org/pages/download)
- [NodeJS 0.8+](http://nodejs.org/download/)
- [Redis 2.6+](http://redis.io/download)
- [PostgreSQL 9.2+](http://www.postgresql.org/download/)
- [Memcached](http://memcached.org)
- Ruby Sass gem
- Node CoffeeScript module

Install CoffeeScript:

```bash
npm install -g coffee-script
```

Install the Sass gem:

```bash
gem install sass
```

### Deployment Dependencies

Note, the `INSTALL` file contains instructions for setting up a server running
RedHat Enterprise Linux Server 6.3.

- [nginx](http://nginx.org/en/download.html)
- [supervisord](http://supervisord.org)

## Setup & Install

Distribute, Pip and virtualenv are required. To check if you have them:

```bash
which pip easy_install virtualenv
```

If nothing prints out, install the libraries corresponding to the commands
below:

_Watch out for sudo! The root user `$PATH` most likely does not include
`/usr/local/bin`. If you did not install Python through your distro's package
manager, use the absolute path to the new Python binary to prevent installing
the above libraries with the wrong version (like Python 2.4 on CentOS 5),
e.g. `/usr/local/bin/python2.7`._

```bash
curl http://python-distribute.org/distribute_setup.py | python
curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | python
pip install virtualenv
```

Create your virtualenv:

```bash
virtualenv varify-env
cd varify-env
. bin/activate
```

Clone the repo:

```bash
git clone https://github.com/cbmi/varify.git
cd varify
```

Install the requirements:

```bash
pip install -r requirements.txt
```

[Start the postgres server](http://www.postgresql.org/docs/9.2/static/server-start.html). This *may* look something like:
```
initdb /usr/local/var/postgres -E utf8

pg_ctl -D /usr/local/var/postgres -l /usr/local/var/postgres/server.log start
```

Create the varify database, you might first want to make sure you are a user
```
createuser --user postgres -s -r yourusername
createdb varify

```

Start memcached
```bash
memcached -d
```

Start redis
``
redis-server /usr/local/etc/redis.conf
```
If you are on a Mac, you will need to start postfix to allow SMTP:
```
sudo postfix start
```

Initialize the Django and Varify schemas
```
./bin/manage.py syncdb
./bin/manage.py migrate
```

Load the initial data
```
./bin/manage.py loaddata ./varify/fixtures/*
```

Then either start the built-in Django server:

```bash
./bin/manage.py runserver
```

or run a `uwsgi` process:

```bash
uwsgi --ini server/uwsgi/local.ini --protocol http --socket 127.0.0.1:8000 --check-static _site
```

## Makefile Commands

- `build` - builds and initializes all submodules, compiles SCSS and
    CoffeeScript and optimizes JavaScript
- `watch` - watches the CoffeeScript and SCSS files in the background
for changes and automatically recompiles the files
- `unwatch` - stops watching the CoffeeScript and SCSS files
- `sass` - one-time explicit recompilation of SCSS files
- `coffee` - one-time explicit recompilation of CoffeeScript files

## Fabfile Commands

- `deploy:[<branch>@]<commit>` - deploy a specific Git commit or tag


## Local Settings

`local_settings.py` is intentionally not versioned (via .gitignore). It should
contain any environment-specific settings and/or sensitive settings such as
passwords, the `SECRET_KEY` and other information that should not be in version
control. Defining `local_settings.py` is not mandatory but will warn if it does
not exist.

## CoffeeScript & Sass Development

CoffeeScript is lovely. The flow is simple:

- write some CoffeeScript which automatically gets compiled in JavaScript
(by doing `make watch`)
- when ready to test non-`DEBUG` mode, run `make optimize`

The `app.build.js` file will need to be updated to define which modules
should be compiled to single files. It is recommended to take a tiered
approach to reduce overall file size across pages and increase cache potential
for libraries that won't change for a while, for example jQuery.

[Sass](http://sass-lang.com/) is awesome. SCSS is a superset of CSS so you can
use as much or as little SCSS syntax as you want. It is recommended to write
all of your CSS rules as SCSS, since at the very least the Sass minifier can
be taken advantage of.

Execute the following commands to begin watching the static files and
collect the files (using Django's collectstatic command):

```bash
make sass coffee collect watch
```

_Note, the `sass` and `coffee` targets are called first to ensure the compiled
files exist before attempting to collect them._
