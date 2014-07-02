import logging
from optparse import make_option
from django.db import models, transaction
from django.db.models import loading
from django.conf import settings
from django.db import connections, DEFAULT_DB_ALIAS
from django.db.utils import DatabaseError
from django.core.management.base import NoArgsCommand
from django.template.defaultfilters import filesizeformat

log = logging.getLogger(__name__)


class Command(NoArgsCommand):
    help = 'Prints the calculated data size of each table on disk.'

    option_list = NoArgsCommand.option_list + (
        make_option('--database', action='store', dest='database',
                    default=DEFAULT_DB_ALIAS,
                    help='Nominates a database to print the '
                         'SQL for.  Defaults to the "default" database.'),
        make_option('-s', action='store_true', dest='suffix',
                    help='Prints human-readable sizes with the approiate '
                         'suffix.'),
    )

    def handle_noargs(self, **options):
        using = options.get('database')
        suffix = options.get('suffix')
        db_name = settings.DATABASES[using]['NAME']
        cursor = connections[using].cursor()
        loading.cache._populate()

        sizes = []
        with transaction.commit_on_success(using):
            for name, app in loading.cache.app_store.items():
                for model in models.get_models(app):
                    opts = model._meta
                    # Some tables may not yet be created in the database, so
                    # this statement will fail
                    try:
                        cursor.execute("SELECT pg_total_relation_size('{0}')"
                                       .format(opts.db_table))
                        sizes.append((cursor.fetchone()[0], opts.module_name))
                    except DatabaseError:
                        transaction.rollback()
        for size, name in sorted(sizes):
            if suffix:
                size = filesizeformat(size)
            log.debug('{0}\t{1}'.format(size, name))
        if suffix:
            cursor.execute("SELECT pg_size_pretty(pg_database_size('{0}'))"
                           .format(db_name))
        else:
            cursor.execute("SELECT pg_database_size('{0}')".format(db_name))
        log.debug('{0}\tTOTAL'.format(cursor.fetchone()[0]))
