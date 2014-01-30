# -*- coding: utf-8 -*-
from south.v2 import DataMigration


class Migration(DataMigration):
    depends_on = (
        ('samples', '0001_initial'),
        ('avocado', '0029_auto__add_field_dataview_parent__add_field_dataquery_parent__add_field'),
    )

    def forwards(self, orm):
        "Perform a 'safe' load using Avocado's backup utilities."
        from avocado.core import backup
        backup.safe_load(u'0002_avocado_metadata', backup_path=None,
                         using='default')

    def backwards(self, orm):
        "No backwards migration applicable."
        pass
