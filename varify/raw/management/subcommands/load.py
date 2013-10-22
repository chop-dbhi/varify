import os
import sys
import shlex
import traceback
from collections import OrderedDict
from ConfigParser import ConfigParser
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.db import connections, transaction, DEFAULT_DB_ALIAS
from varify.raw.utils.stream import PGCopyEditor


class LoadCommand(BaseCommand):

    requires_model_validation = False

    # a list of 'targets' which act as unique identifiers to tables and
    # manifest entries
    targets = []

    # schema.table
    qualified_names = {}

    # CREATE TABLE {} ( ... )
    create_sql = {}

    default_processor = PGCopyEditor

    processors = {}

    option_list = BaseCommand.option_list + (
        make_option('--database', action='store', dest='database',
            default=DEFAULT_DB_ALIAS, help='Nominates a database to print the '
                'SQL for.  Defaults to the "default" database.'),
        make_option('-s', '--source', action='store', dest='source',
            default='.', help='Specifies the directory containing the '
                'MANIFEST and raw data files.'),
        make_option('-d', '--drop', action='store_true', default=False,
            help='Only perform the DROP TABLE operation'),
        make_option('-c', '--create', action='store_true', default=False,
            help='Only perform the CREATE TABLE operation'),
        make_option('-l', '--load', action='store_true', default=False,
            help='Only perform the data loading (into the existing tables)')
    )

    def drop_tables(self, cursor, targets):
        print('Dropping tables...')
        for target in targets:
            try:
                self.drop_table(cursor, target, targets[target][1])
                print('- {}'.format(target))
            except Exception:
                traceback.print_exc()
                print('----')
                print('Error dropping {}, rolling back..'.format(target))
                transaction.rollback()
                sys.exit(1)

    def create_tables(self, cursor, targets):
        print('Creating tables...')
        for target in targets:
            try:
                self.create_table(cursor, target, targets[target][1])
                print('- {}'.format(target))
            except Exception:
                traceback.print_exc()
                print('----')
                print('Error creating {}, rolling back'.format(target))
                transaction.rollbak()
                sys.exit(1)

    def load_tables(self, cursor, targets):
        print('Loading tables...')
        for target in targets:
            files, options = targets[target]
            try:
                self.load_files(cursor, target, files, options)
                print('- {}'.format(target))
            except Exception:
                traceback.print_exc()
                print('----')
                print('Error loading {}, rolling back'.format(target))
                transaction.rollback()
                sys.exit(1)

    def drop_table(self, cursor, target, options):
        "Drops the target table."
        sql = 'DROP TABLE IF EXISTS {}'
        cursor.execute(sql.format(self.qualified_names[target]))

    def create_table(self, cursor, target, options):
        "Creates the target table."
        cursor.execute(self.create_sql[target].format(self.qualified_names[target]))

    def load_files(self, cursor, target, files, options):
        "Loads multiple files into the target table."
        for fname in files:
            self.load_file(cursor, target, fname, options)

    def load_file(self, cursor, target, fname, options):
        "Parses and loads a single file into the target table."
        with open(fname) as fin:
            log.debug("opening {0} in {1} load_file".format(fname,__name__))
            encoding = options.get('encoding', 'utf-8')
            if target in self.processors:
                reader = self.processors[target](fin, encoding=encoding)
            else:
                reader = self.default_processor(fin, encoding=encoding)
            columns = getattr(reader, 'output_columns', None)
            for _ in xrange(int(options.get('skip-lines', 0))):
                fin.readline()
            cursor.copy_from(reader, self.qualified_names[target], columns=columns)

    def handle(self, **options):
        if not self.targets:
            print('No targets defined. Nothing to do.')
            return

        source = options.get('source')
        drop = options.get('drop')
        create = options.get('create')
        load = options.get('load')
        using = options.get('database')
        connection = connections[using]
        cursor = connection.cursor()

        # If no operation is supplied, assume all operations
        if not (drop or create or load):
            drop = create = load = True

        # Perform checks ahead of time to prevent failing in an
        # inconsistent state
        if not os.path.exists(os.path.join(source, 'MANIFEST')):
            raise CommandError('No MANIFEST in the source directory: {}'.format(source))

        targets = OrderedDict()
        parser = ConfigParser()
        parser.read([os.path.join(source, 'MANIFEST')])

        for target in parser.sections():
            if target not in self.targets:
                print('Unknown target "{}", skipping...'.format(target))
                continue

            options = dict(parser.items(target))

            files = []
            for fn in shlex.split(options['files']):
                path = os.path.join(source, fn)
                if not os.path.exists(path):
                    raise CommandError('No file named {} exists'.format(fn))
                files.append(path)
            targets[target] = (files, options)

        if not targets:
            print('No targets defined in MANIFEST. Nothing to do.')
            return

        # Manually commit along the way
        with transaction.commit_manually(using=using):
            if drop:
                self.drop_tables(cursor, targets)

            if create:
                self.create_tables(cursor, targets)

            if load:
                self.load_tables(cursor, targets)

            transaction.commit()
