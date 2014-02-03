import re
from optparse import make_option
from django.db import models, QName
from django.db import connections, DEFAULT_DB_ALIAS
from django.core.management.base import AppCommand
from django.core.management.color import no_style


def sql_drop_indexes_for_field(model, f, style, connection):
    """
    Return the DROP INDEX SQL statements for a single model field.
    """
    output = []
    cqn = connection.ops.compose_qualified_name
    qname = connection.qualified_name(model)

    # HACK
    create_indexes = \
        connection.creation.sql_indexes_for_field(model, f, no_style())
    for statement in create_indexes:
        name = re.search(r'CREATE INDEX (.*) ON', statement).groups()[0]
        name = cqn(
            QName(schema=qname.schema, table=name, db_format=qname.db_format))
        output.append(style.SQL_KEYWORD(
            'DROP INDEX IF EXISTS') + ' ' + style.SQL_TABLE(name) + ';')
    return output


def sql_drop_indexes_for_model(model, style, connection):
    """
    Returns the DROP INDEX SQL statements for a single model.
    """
    if not model._meta.managed or model._meta.proxy:
        return []
    output = []
    for f in model._meta.local_fields:
        output.extend(sql_drop_indexes_for_field(model, f, style, connection))
    return output


def sql_drop_indexes(app, style, connection):
    output = []
    for model in models.get_models(app):
        output.extend(sql_drop_indexes_for_model(model, style, connection))
    return output


class Command(AppCommand):
    help = ("Prints the DROP INDEX SQL statements for the given app module "
            "name(s).")

    option_list = AppCommand.option_list + (
        make_option('--database', action='store', dest='database',
                    default=DEFAULT_DB_ALIAS,
                    help='Nominates a database to print the SQL for. Defaults '
                         'to the "default" database.'),
    )

    output_transaction = True

    def handle_app(self, app, **options):
        return u'\n'.join(sql_drop_indexes(
            app,
            self.style,
            connections[options.get('database')])).encode('utf-8')
