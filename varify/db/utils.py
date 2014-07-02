from django.db import connections, DEFAULT_DB_ALIAS
from django.core.management import color


def sequence_reset_sql(model, using=DEFAULT_DB_ALIAS):
    connection = connections[using]
    return connection.ops.sequence_reset_sql(color.no_style(), [model])[0]


def table_exists(table, schema='public', using=DEFAULT_DB_ALIAS):
    connection = connections[using]
    catalog = connection.settings_dict['NAME']
    cursor = connection.cursor()
    cursor.execute('''
        SELECT (1) FROM "information_schema"."tables"
        WHERE "table_catalog" = %s
            AND "table_schema" = %s
            AND "table_name" = %s
    ''', [catalog, schema, table])
    return True if cursor.fetchone() else False
