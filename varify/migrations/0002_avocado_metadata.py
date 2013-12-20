from south.v2 import DataMigration
from django.core.management import call_command

class Migration(DataMigration):

    depends_on = (
        ('avocado', '0029_auto__add_field_dataview_parent__add_field_dataquery_parent__add_field'),
    )

    def forwards(self, orm):
        "Write your forwards methods here."
        call_command('loaddata', 'avocado_metadata_0001.json')

    def backwards(self, orm):
        "Write your backwards methods here."
        pass

    models = {

    }

    complete_apps = ['varify']
    symmetrical = True
