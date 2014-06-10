from __future__ import print_function, with_statement
import os
import sys
import stat
import json
import etcd
from functools import wraps
from fabric.api import *
from fabric.colors import red, yellow, white, green
from fabric.contrib.console import confirm
from fabric.contrib.files import exists


__doc__ = """\
Help Doc
"""

# A few setup steps and environment checks
curdir = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.join(curdir, '.project_config.json')

etcd_host = ""
registry_host = ""
registry_port = ""

try:
    project_config = json.loads(open(config_file, 'r').read())
except:
    project_config = {
        "etcd_host": etcd_host
    }

hidden_output = []

try:
    venv_wrap_path = os.environ['WORKON_HOME']
except KeyError:
    venv_wrap_path = None

if venv_wrap_path and os.path.exists(os.path.join(venv_wrap_path, 'varify')):
    full_env_path = os.path.join(venv_wrap_path, 'varify')
else:
    full_env_path = os.path.abspath('..')
    venv_wrap_path = None

def get_hosts_settings():
    # TODO: Will probably have to retain this to support legacy deploy.

    # Load all the host settings
    try:
        hosts = json.loads(open(config_file).read())['hosts']
    except KeyError:
        abort(red('Error: No host settings are defined in the project configuration'))
    # Pop the default settings

    # Pre-populated defaults
    # for host in hosts:
    #     base = base_settings.copy()
    #     base.update(default_settings)
    #     print(hosts)
    #     base.update(hosts[host])
    #     hosts[host] = base

    return hosts

# ** Decorators
def virtualenv(path, venv_wrap):
    "Wraps a function and prefixes the call with the virtualenv active."
    if path is None:
        activate = None
    else:
        activate = os.path.join(path, 'bin/activate')

    def decorator(func):
        @wraps(func)
        def inner(*args, **kwargs):
            if venv_wrap:
                with prefix('source /usr/local/bin/virtualenvwrapper.sh'):
                    with prefix('workon {0}'.format('varify')):
                        return func(*args, **kwargs)
            elif path is not None and venv is None:
                with prefix('source {0}'.format(activate)):
                    return func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        return inner
    return decorator

def host_context(func):
    "Sets the context of the setting to the current host"
    @wraps(func)
    def decorator(*args, **kwargs):
        hosts = get_hosts_settings()
        with settings(**hosts[env.host]):
            return func(*args, **kwargs)
    return decorator

# ---------------------------------------------------------------
# Configuration Commands
# ---------------------------------------------------------------

def set_configuration(noinput=False):
    '''
    Takes the settings in .project_config.json file and writes them to the
    appropriate etcd endpoint for this application.

    ab set_configuration:noinput=True will not prompt for confirmation
    '''
    client = etcd.Client(host=project_config['etcd_host'])
    config = json.loads(open('.project_config.json', 'r').read())

    if noinput or confirm("Are you sure you want to upload your local settings?"):
        client.write('/applications/varify/configuration', json.dumps(config))


def get_configuration(noinput=False):
    '''
    Retrieves the applications settings from etcd and generates a local settings file.

    fab get_configuration:noinput=True will not prompt for confirmation
    '''
    client = etcd.Client(host=project_config['etcd_host'])
    try:
        etcd_config = client.read('/applications/varify/configuration')
    except KeyError:
        abort(red('Error: No host settings found on etcd'))

    configuration = json.loads(etcd_config.value)
    if configuration == {}:
        print(red('Empty configuration found. Aborting'))
        sys.exit(1)

    # Establish the configuration locally
    if noinput or confirm('Are you sure you want to overwrite your local settings?'):
        f = open('.project_config.json', 'w')
        f.write(json.dumps(configuration, indent=4, sort_keys=True))
        f.close()

# ---------------------------------------------------------------
# Docker Commands
# ---------------------------------------------------------------
# TODO:
# - Continuous Integration. Automatic provisioning of services


def build_container(noinput=False):
    # Check git status to make sure our build hash matches our git commit
    #index_status = local('git status --porcelain', capture=True)
    #if index_status != '':
     #   abort('Please commit or stash any changes to git before building your container')

    try:
        get_configuration(noinput)
    except:
        if not confirm('Unable to retrieve configuration. Would you like to attempt to build this container with locally available settings?'):
            sys.exit(1)
    git_hash = local('git rev-parse --short HEAD', capture=True)
    git_branch = local('git rev-parse --abbrev-ref HEAD', capture=True)

    local('docker build -t varify-{0}:{1} .'.format(git_branch, git_hash))

def test_container():
    git_hash = local('git rev-parse --short HEAD', capture=True)
    git_branch = local('git rev-parse --abbrev-ref HEAD', capture=True)
    local('docker run -i -t -e APP_ENV=test varify-{0}:{1} test'.format(git_branch, git_hash))

def build_and_test():
    build_container(noinput=True)
    test_container()

# Remote Deployment Commands

def pull_repo():
    local('docker pull {0}/varify-{1}'.format(project_config['docker_registry'], git_branch))

def push_to_repo():
    git_hash = local('git rev-parse --short HEAD', capture=True)
    git_branch = local('git rev-parse --abbrev-ref HEAD', capture=True)

    try:
        with hide('output'):
            local("docker inspect --format='{{{{.id}}}}' varify-{0}:{1}".format(git_branch, git_hash))
    except:
        if confirm('Could not find most most recent container. Would you like to build it?'):
            build_container()

    local('docker tag varify-{0}:{1} {2}/varify-{0}:{1}'.format(git_branch, git_hash, project_config['docker_registry']))
    local('docker tag varify-{0}:{1} {2}/varify-{0}:latest'.format(git_branch, git_hash, project_config['docker_registry']))
    local('docker push {0}/varify-{1}'.format(project_config['docker_registry'], git_branch))
    local('docker rmi -f {0}/varify-{1}:{2}'.format(project_config['docker_registry'], git_branch, git_hash))

@host_context
def deploy(commit='latest'):

    run('docker pull {0}/varify-{1}:{2}'.format(project_config['docker_registry'], env.git_branch, commit))
    container = run('docker run -d -p :8000 -e APP_ENV={0} {1}/varify-{2}:{3} start'.format(
        env.host,
        project_config['docker_registry'],
        env.git_branch,
        commit)
    )
    port = run("docker inspect --format='{{{{range $p, $conf := .NetworkSettings.Ports}}}}{{{{(index $conf 0).HostPort}}}} {{{{end}}}}' {0}".format(container))
    commit_msg = local('git --no-pager log --oneline -1', capture = True)
    auth_token = project_config['hipchat']['auth_token']
    deploy_msg = 'varify-{0}:{1} now deployed at http://{2}:{3} <a href="http://{2}:{3}">Open</a> <a href="http://{4}:4001/v2/keys/applications/varify/status">Status</a> -- {5}'.format(env.git_branch, commit, env.host_string, port, project_config['etcd_host'], commit_msg)

    # Notifications
    local('curl -d "room_id=529405&from=deployservice&color=yellow" --data-urlencode message="{deploy_msg}" https://cbmi.hipchat.com/v1/rooms/message?auth_token={auth_token}'.format(
        deploy_msg=deploy_msg,
        auth_token=auth_token
    ))

    client = etcd.Client(host=project_config['etcd_host'])
    client.write('/applications/varify/status/{0}/latest_commit'.format(env.git_branch), commit)
    client.write('/applications/varify/status/{0}/latest_deploy'.format(env.git_branch), 'http://{0}:{1}'.format(env.host_string, port))

    print(green('Now Running at http://{0}:{1}'.format(env.host_string, port)))

@host_context
def setup_env():
    "Sets up the initial environment."
    parent, project = os.path.split(env.path)
    if not exists(parent):
        run('mkdir -p {}}'.format(parent))

    with cd(parent):
        if not exists(project):
            run('git clone {repo_url} {project}'.format(project=project, **env))
            with cd(project):
                run('git checkout {git_branch}'.format(**env))
                run('git pull origin {git_branch}'.format(**env))
        else:
            with cd(project):
                run('git checkout {git_branch}'.format(**env))
                run('git pull origin {git_branch}'.format(**env))

# ---------------------------------------------------------------
# Template Bootstrap Hooks
# ---------------------------------------------------------------

@virtualenv(full_env_path, venv_wrap_path)
def harvest_bootstrap():
    # Handle Settings Configuration
    # TODO:
    # Perhaps at this point we go out to etcd and
    # find the relavent DB connection settings if
    # they exist then we use those here... otherwise
    # we fall back to the default sqlite stuff

    print('Setup default configuration file')
    with hide(*hidden_output):
        local('mv .project_config.json.sample .project_config.json')

    print('Make test script executable')
    mode = stat.S_IMODE(os.stat('run-tests.sh').st_mode)
    executable = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    os.chmod('run-tests.sh', mode | executable)

    # Sync DB
    print(green('- Creating SQLiteDB.'))
    with hide(*hidden_output):
        local('./bin/manage.py syncdb --settings=varify.conf.local')

    # Collect Static
    print(green('- Collecting Static Files'))
    with hide(*hidden_output):
        local('./bin/manage.py collectstatic --noinput --settings=varify.conf.local')

    # Migrations
    print(green('- Run Migrations'))
    with hide(*hidden_output):
        local('./bin/manage.py migrate --noinput --settings=varify.conf.local')

# ---------------------------------------------------------------
# Testing and Continuous Integration Commands
# ---------------------------------------------------------------

def check_for_config(noinput):
    if 'project_settings' not in project_config.keys():
        if noinput or confirm(red("No configuration found. Would you like to download this applications configuration?")):
            get_configuration(noinput=True)

def check_for_pg(database):
    '''
    Check the current Docker host for an existing instance of the specified
    database. If found returns the container ID.
    '''
    with hide('output', 'running', 'warnings'), settings(warn_only=True):
        res = local("docker ps -a | awk '/{0}/ {{ print $1 }}'".format(database), capture=True)
        if res:
            return res.split("\n")
        else:
            return None


def check_for_mc():
    '''
    Check the current Docker host for an existing instance of memcache. If
    found returns the container ID.
    '''
    with hide('output', 'running', 'warnings'), settings(warn_only=True):
        res = local("docker ps | awk '/memcache/ { print $1 }'", capture=True)
        if res:
            print(green('Found Memcache running at {0}'.format(res)))
            return res.split("\n")
        else:
            return None

def test_setup(noinput=False):
    '''
    Examine the project for a proper configuration file.

    Examine the existing environment for Harvest app's service dependencies
    (Memcache, and Postgres). If they do not exists create them as containers,
    build the application container and apply ETL command from the application
    to the Postgres DB.

    After the data load is complete, attach the application to the Postgres
    container and to Memcache. Apply normal bootstrapping procedures (syncdb,
    migrations, collectstatic) and load fixture container test user "cbmi" with
    default password "changeme"
    '''

    DB_CONTAINER_NAME = 'varify_test_db'

    check_for_config(noinput)

    dbs = check_for_pg(DB_CONTAINER_NAME)

    if dbs:
        if noinput or confirm(yellow('It looks like you might already have an instance running on this machine. Do you want to stop and remove the existing containers?')):
            with hide('output', 'running'):
                print(red('Stopping and removing associated Harvest application containers.'))
                local("docker ps -a | awk '/(varify_test:|varify_test_db)/ { print $1 }' | xargs docker stop")
                local("docker ps -a | awk '/(varify_test:|varify_test_db)/ { print $1 }' | xargs docker rm")

    mc = check_for_mc()

    if not mc:
        with hide('output', 'running'):
            print(green('Starting Memcached Container...'))
            local("docker run -d --name memcache ehazlett/memcached")

    with hide('output', 'running', 'warnings'):
        # Spin up a fresh Postgres instance:
        print(green('Starting Postgres Container...'))
        pg_container = local('docker run -p :5432 -d --name varify_test_db {0}:{1}/postgresql', capture=True).format(registry_host,registry_port)
        port = local("docker inspect --format='{{{{range $p, $conf := .NetworkSettings.Ports}}}}{{{{(index $conf 0).HostPort}}}} {{{{end}}}}' {0}".format(pg_container), capture=True)
        time.sleep(2)
        # Create DB and User in fresh DB
        print(green('Prepare Postgres DB...'))
        local('export PGPASSWORD=docker && createdb -h localhost -p {port} -U docker varify'.format(port=port))
        conn = psycopg2.connect(host='localhost', port=port, user='docker', password='docker', database='postgres')
        conn.cursor().execute("create user varify with password 'docker'; ")
        conn.commit()
        conn.close()
        # Build the Application Container to facilitate ETL:
        print(green('Building Application Container...'))
        local('docker build -t varify_test .')
        # Run ETL on attached Postgres DB
        print(green('Start ETL on attached DB'))
        local('docker run --link varify_test_db:db -e APP_ENV=test --name varify_etl varify_test etl')
        # Wait for ETL process to finish
        local('docker wait varify_etl')
        print(green('ETL Complete.'))
        local('docker rm varify_etl')
        # Start the application container
        print(green('Start Application Container...'))
        varify = local('docker run -d --link varify_test_db:db --link memcache:mc -p :8000 -e APP_ENV=test --name varify_test_app varify_test debug', capture=True)
        varify_port = local("docker inspect --format='{{{{range $p, $conf := .NetworkSettings.Ports}}}}{{{{(index $conf 0).HostPort}}}} {{{{end}}}}' {0}".format(varify), capture=True)

    # Sleep to give syncdb and migrations time to run.
    time.sleep(10)
    print(red('\n***\nvarify Test Instance now running on: http://{0}:{1}'.format(socket.gethostname(), varify_port)))

def ci_setup(noinput=False):
    "Copy down the production varify database to a fresh postgres container."
    # TODO
    # - Make sure configuration file exists.

    DB_CONTAINER_NAME = 'varify_ci_pg'

    check_for_config(noinput)

    dbs = check_for_pg(DB_CONTAINER_NAME)

    if dbs:
        if noinput or confirm(yellow('It looks like you might already have an instance running on this machine. Do you want to stop and remove the existing containers?')):
            with hide('output', 'running'):
                print(red('Stopping and removing associated Harvest application containers.'))
                local("docker ps -a | awk '/(varify_test:|varify_test_db)/ { print $1 }' | xargs docker stop")
                local("docker ps -a | awk '/(varify_test:|varify_test_db)/ { print $1 }' | xargs docker rm")


    # Spin up a fresh postgres instance:
    with hide('output', 'running', 'warnings'):
        print(green('Starting Postgres Container...'))
        pg_container = local('docker run -p :5432 -d --name varify_ci_db {0}:{1}/postgresql', capture=True).format(registry_host,registry_port)
        port = local("docker inspect --format='{{{{range $p, $conf := .NetworkSettings.Ports}}}}{{{{(index $conf 0).HostPort}}}} {{{{end}}}}' {0}".format(pg_container), capture=True)
        time.sleep(2)
        print(green('Dump Production DB...'))
        db = parse_db(project_config['project_settings']['production']['databases']['default'])
        local('export PGPASSWORD={password} && pg_dump -h {host} -U {user} -Fc {database} > tmp.dump'.format(**db))
        time.sleep(2)
        print(green('Prepare Postgres DB...'))
        local('export PGPASSWORD=docker && createdb -h localhost -p {port} -U docker varify'.format(port=port))
        conn = psycopg2.connect(host='localhost', port=port, user='docker', password='docker', database='postgres')
        conn.cursor().execute("create user varify with password 'docker'; ")
        conn.commit()
        conn.close()
        print(green('Restoring Backup to Container...'))
        local('export PGPASSWORD=docker && pg_restore -h localhost -p {port} -U docker -d varify tmp.dump'.format(port=port))
        local('rm tmp.dump')
        print(green('Building Application Container...'))
        local('docker build -t varify_test .')
        print(green('Start Application Container...'))
        varify = local('docker run -d --link varify_ci_db:db -p :8000 -e APP_ENV=ci --name varify_ci varify start', capture=True)
        varify_port = local("docker inspect --format='{{{{range $p, $conf := .NetworkSettings.Ports}}}}{{{{(index $conf 0).HostPort}}}} {{{{end}}}}' {0}".format(varify), capture=True)

    print(red('\n***\nvarify Production Clone now running on: http://localhost:{0}'.format(varify_port)))
