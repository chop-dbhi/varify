import os
import logging
from optparse import make_option
from django.core.management.base import BaseCommand

log = logging.getLogger(__name__)


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--dump', action='store', dest='path',
                    default=None,
                    help='Specifies the target pgsql.tar.gz file to load.'),

        make_option('--name', action='store', dest='name',
                    default='harvestdb',
                    help='Specifies the name of the database. Default is ' +
                    'harvestdb.'),

        make_option('--user', action='store', dest='user', default=None,
                    help='Specifies the user this database belongs to.')
    )

    def _createDB(self, user, name, dump):
        if user:
            # Create the user
            usr = \
                'psql - c "create user {0} with password \'{1}\';" -U postgres'
            os.system(usr.format(user, user))

            # Create the database and assign it to the user
            crtdb = 'psql -c "create database {0} ' + \
                'with owner {1};\';" -U postgres'
            os.system(crtdb.format(name, user))
        else:
            os.system('createdb {0}'.format(name))

        # Load an sql dump into the database from a pgsql.tar.gz file
        if dump:
            dumpCmd = './bin/manage.py samples load-db --db {0} --path {1}'
            os.system(dumpCmd.format(name, dump))

    def handle(self, *dirs, **options):
        dump = options.get('path')
        name = options.get('name')
        user = options.get('user')

        print dump
        self._createDB(user, name, dump)
