import os
import logging
from optparse import make_option
from django.core.management.base import BaseCommand

log = logging.getLogger(__name__)


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--path', action='store', dest='path',
                    default='cid/data_service/data/varify.pgsql.tar.gz',
                    help='Specifies the target sql file to load.'),

        make_option('--db', action='store', dest='db', default='varify',
                    help='Specifies the database to load the data to.')
    )

    def _loadDB(self, path, db):
        # Extract the file name
        fileName = path.split("/")[-1]

        # Untar the zip file
        os.system('tar -xvf ' + path + ' -C ' + path.replace(fileName, ""))

        # Load the file into the database
        os.system('psql ' + db + ' < ' + path.replace('.tar.gz', ''))

    def handle(self, *dirs, **options):
        path = options.get('path')
        db = options.get('db')

        self._loadDB(path, db)
