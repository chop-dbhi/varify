# Varify Development

[![Build Status](https://travis-ci.org/cbmi/varify.png?branch=master)](https://travis-ci.org/cbmi/varify) [![Coverage Status](https://coveralls.io/repos/cbmi/varify/badge.png)](https://coveralls.io/r/cbmi/varify)

More information on the data models, commands, and loader can be found on the [varify-data-warehouse repository](https://github.com/cbmi/varify-data-warehouse).

## Need some help?
Join our chat room and speak with our dev team: http://www.hipchat.com/gZcKr0p3y

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

Install the Sass gem:

```bash
gem install sass
```

Install the Bourbon gem:

```bash
gem install bourbon
```

### Deployment Dependencies

Note, the `INSTALL` file contains instructions for setting up a server running
RedHat Enterprise Linux Server 6.3.

- [nginx](http://nginx.org/en/download.html)
- [supervisord](http://supervisord.org)


### Optional Dependencies (SolveBio)

SolveBio provides easy integration with external datasets such as ClinVar,
OMIM, dbSNP, and PubMed. It is currently integrated into the variant resource,
and populates a portion of the variant details view in the Varify web client.

**SolveBio is currently in Private Beta,** but Varify users can get access by
[signing up at solvebio.com](https://www.solvebio.com/signup).

To enable SolveBio within Varify, first install the Python package:

```bash
pip install solvebio
```

Then, make sure that the `SOLVEBIO_API_KEY` Django setting is set either
via an environment variable (see `global_settings.py`) or explicitly in your
`local_settings.py`. You can find your API key from your account page on the
SolveBio website.


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

Under Mac OS X 10.8 or later, with XCode 5.1 or later, the following may be necessary in order for pip to install requirements:

```bash
export CFLAGS=-Qunused-arguments
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

## Optional JBrowse Setup

*Note: Varify disables Alamut and JBrowse if nothing is running on settings.ALAMUT_URL and settings.JBROWSE_HOST, respectively. To hide, comment out one or both buttons in varify/static/templates/variant/summary.html.*

Install JBrowse in $project_root/jbrowse

```bash
curl -O http://jbrowse.org/releases/JBrowse-x.x.x.zip (ie 1.11.3)
unzip JBrowse-x.x.x.zip -d jbrowse
cd jbrowse
./setup.sh
```

Download data files (ie BAM, GFF, VCF) to /your/directory/of/files/ and add the following to nginx.conf. This corresponds to the JbrowseResource endpoint defined in varify/samples/resources.py.

```bash
location /files/ {
    alias /your/directory/of/files/;
    internal;
}
```

Run the commands below to load reference sequences and Cosmic track (in that order). This only needs to be done once.

```bash
sudo ./bin/prepare-refseqs.pl --fasta ../files/chr1.fa
...
sudo ./bin/prepare-refseqs.pl --fasta ../files/chrY.fa
sudo ./bin/flatfile-to-json.pl --gff ../files/ALL_COSMIC_POINT_MUTS_v65.gff3 --trackLabel Cosmic --trackType CanvasFeatures
...

Note: Segment large Cosmic GFF files with synchronization marks, a line containing '###', to prevent (really) slow loading. Once a loading script executes, a data directory will exist in $project_root/jbrowse.
```

Run bgzip and tabix (via samtools/htslib) on VCF files

```bash
git clone git://github.com/samtools/samtools.git
bgzip my.vcf
tabix -p vcf my.vcf.gz
```

**Lastly, make sure data files are named correctly!** The batch, sample and version values of the [sample] section of the sample manifest are concatenated and delimited by '_' to create the filename root for the BAM, BAI, VCF, and TBI files in the JBrowse URL. Suffixes are hard-coded '.sorted.mdup.bam','.sorted.mdup.bam.bai','.var_raw.vcf.gz', and '.var_raw.vcf.gz.tbi', respectively.

```bash
[sample]
project = U01
batch = Pseq_batch9
sample = P-Pseq_0019-P-A
version = 1
```

## Makefile Commands

- `build` - builds and initializes all submodules, compiles SCSS and optimizes JavaScript
- `watch` - watches the SCSS files in the background
for changes and automatically recompiles the files
- `unwatch` - stops watching the SCSS files
- `sass` - one-time explicit recompilation of SCSS files

## Fabfile Commands

- `deploy:[<branch>@]<commit>` - deploy a specific Git commit or tag


## Local Settings

`local_settings.py` is intentionally not versioned (via `.gitignore`). It should
contain any environment-specific settings and/or sensitive settings such as
passwords, the `SECRET_KEY` and other information that should not be in version
control. Defining `local_settings.py` is not mandatory but will warn if it does
not exist.

## Sass Development

[Sass](http://sass-lang.com/) is awesome. SCSS is a superset of CSS so you can
use as much or as little SCSS syntax as you want. It is recommended to write
all of your CSS rules as SCSS, since at the very least the Sass minifier can
be taken advantage of.

Execute the following commands to begin watching the static files and
collect the files (using Django's collectstatic command):

```bash
make sass collect watch
```

_Note, the `sass` target is called first to ensure the compiled files exist before attempting to collect them._
