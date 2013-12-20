# Varify Development

[![Build Status](https://travis-ci.org/cbmi/varify.png?branch=master)](https://travis-ci.org/cbmi/varify) [![Coverage Status](https://coveralls.io/repos/cbmi/varify/badge.png)](https://coveralls.io/r/cbmi/varify)

## Need some help?
Join our chat room and speak with our dev team: http://www.hipchat.com/gZcKr0p3y

__NOTE:__ Varify, as it currently stands, is in beta form and is currently undergoing a transition to the latest version of Harvest([Cilantro](https://github.com/cbmi/cilantro/), [Avocado](https://github.com/cbmi/avocado/), and [Serrano](https://github.com/cbmi/serrano/)). Continue to use the master branch if you wish to work with Varify in the mean time. The Harvest transition is happening in the `harvest` branch if you want to follow along there but there.

## Dependencies

Listed are the download links to each dependency, however most OSes have a
package manager or binaries that can be easily installed. Most of the below
links describe alternate download and install methods.

On Mac OS X, [Homebrew](http://mxcl.github.com/homebrew/) is the recommended
way to install most of these of these libraries.

- [Python 2.6+](http://python.org/download/releases/2.6.9/)
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
```
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

`local_settings.py` is intentionally not versioned (via `.gitignore`). It should
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

## Pipeline

The following describes the steps to execute the loading pipeline, the performance of the pipeline, and the process behind it.

### Executing the Load Pipeline

### Retrieving Test Data

We have provided a [set of test data](https://github.com/cbmi/varify-demo-data) to use to test the load pipeline or use as sample data when first standing up your Varify instance. To use the test data, run the commands below.

```bash
wget https://github.com/cbmi/varify-demo-data/archive/0.1.tar.gz -O varify-demo-data-0.1.tar.gz
tar -zxf varify-demo-data-0.1.tar.gz
gunzip varify-demo-data-0.1/CEU.trio.2010_03.genotypes.annotated.vcf.gz
```

At this point, the VCF and MANIFEST in the `varify-demo-data-0.1` directory are ready for loading in the pipeline. You can use the `varify-demo-data-0.1` directory as the argument to the `samples queue` command in the _Queue Samples_ step below if you want to just load this test data.

#### Tmux (optional)

Since the pipeline can take a while to load large collections(see Performance section below), you may want to consider following the Tmux steps to attach/detach to/from the load process.

[Tmux](http://robots.thoughtbot.com/post/2641409235/a-tmux-crash-course) is like [screen](http://www.gnu.org/software/screen/), just newer. It is useful for detaching/reattaching sessions with long running processes.

**New Session**

```bash
tmux
```

**Existing Session**

```bash
tmux attach -t 0 # first session
```

### Activate Environment

```bash
source bin/activate
```

#### Define RQ_QUEUES

For this example, we will assume you have `redis-server` running on `localhost:6379` against the database with index 0. If you have redis running elsewhere simply update the settings below with the address info and DB you wish to use. Open your `local_settings.py` file and add the following setting:

```python
RQ_QUEUES = {
    'default': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
    },
    'samples': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
    },
    'variants': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
    },
}
```

#### Queue Samples

Optionally specify a directory, otherwise it will recursively scan all directories defined in the `VARIFY_SAMPLE_DIRS` setting in the Varify project.

```bash
./bin/manage.py samples queue [directory]
```

#### Kick Off Workers

You can technically start as many of each type for loading data in parallel, but this may cause undesired database contention which could actually slow down the loading process. A single worker for `variants` is generally preferred and two or three are suitable for the `default` type.

```bash
./bin/manage.py rqworker variants &
./bin/manage.py rqworker default &
```

Note, these workers will run forever, if there is only a single sample being loaded, the `--burst` argument can be used to terminate the worker when there are no more items left in the queue.

#### Post-Load

After the batch of samples have been loaded, a two more commands need to be executed to update the annotations and cohort frequencies. These are performed _post-load_ for performance reasons.

```bash
./bin/manage.py variants load --evs --1000g --sift --polyphen2 > variants.load.txt 2>&1 &
./bin/manage.py samples allele-freqs > samples.allele-freqs.txt 2>&1 &
```

### Performance

- File size: 610 MB
- Variant count: 1,794,055

#### Baseline

Iteration over flat file (no parsing) with batch counting (every 1000)

- Time: 80 seconds
- Memory: 0

#### Baseline VCF

Iteration over VCF parsed file using PyVCF

- Time: 41 minutes (extrapolated)
- Memory: 246 KB

### Parallelized Queue/Worker Process

#### Summary of Workflow

1. Fill Queue
2. Spawn Worker(s)
3. Consume Job(s)
    - Validate Input
    - (work)
    - Validate Output
    - Commit

#### Parallelism Constraints

The COPY command is a single statement which means the data being loaded is
all or nothing. If multiple samples are being loaded in parallel, it is likely
they will have overlapping variants.

To prevent integrity errors, workers will need to consult one or more
centralized caches to check if the current variant has been _addressed_
already. If this is the case, the variant will be skipped by the worker.

This incurs a second issue in that downstream jobs that depend on the existence
of some data that does not yet exist because another worker has not yet
committed it's data. In this case, non-matches will be queued up in the
`deferred` queue that can be run at a later time, after the `default` queue
is empty or in parallel with the `default` queue.
