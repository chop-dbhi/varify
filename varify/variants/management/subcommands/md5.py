from optparse import make_option
from django.db import DEFAULT_DB_ALIAS, connections
from django.core.management.base import BaseCommand
from varify.variants.models import Variant


class Command(BaseCommand):
    help = 'Prints UPDATE SQL statements for updating MD5 values.'

    option_list = BaseCommand.option_list + (
        make_option('--database', action='store', dest='database',
                    default=DEFAULT_DB_ALIAS,
                    help='Nominates a database to print the SQL for. Defaults '
                         'to the "default" database.'),
    )

    output_transaction = True

    def handle(self, *args, **options):
        output = []
        connection = connections[options.get('database')]
        quote = connection.ops.quote_name

        sql = self.style.SQL_KEYWORD('UPDATE') + \
            " {table} " + self.style.SQL_KEYWORD('SET') + \
            " {md5} = md5({chr} || '|' || " + \
            self.style.SQL_KEYWORD('CAST') + \
            "({pos} " + self.style.SQL_KEYWORD('AS') + \
            " {type}) || '|' || {ref} || '|' || {alt}) " + \
            self.style.SQL_KEYWORD('WHERE') + " {md5} " + \
            self.style.SQL_KEYWORD('IS NULL') + ";"

        models = [Variant]

        for model in models:
            opts = model._meta
            params = {
                'table': self.style.SQL_TABLE(
                    connection.qualified_name(model, compose=True)),
                'md5': self.style.SQL_TABLE(
                    quote(opts.get_field_by_name('md5')[0].column)),
                'chr': self.style.SQL_TABLE(
                    quote(opts.get_field_by_name('chr')[0].column)),
                'pos': self.style.SQL_TABLE(
                    quote(opts.get_field_by_name('pos')[0].column)),
                'ref': self.style.SQL_TABLE(
                    quote(opts.get_field_by_name('ref')[0].column)),
                'alt': self.style.SQL_TABLE(
                    quote(opts.get_field_by_name('alt')[0].column)),
                # Get an equivalent text type for the CAST
                'type': opts.get_field_by_name('alt')[0].db_type(connection),
            }
            output.append(sql.format(**params))

        return u'\n'.join(output).encode('utf-8')
