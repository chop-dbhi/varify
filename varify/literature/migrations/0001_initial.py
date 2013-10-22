# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'PubMed'
        db.create_table('pubmed', (
            ('pmid', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
        ))
        db.send_create_signal('literature', ['PubMed'])


    def backwards(self, orm):
        
        # Deleting model 'PubMed'
        db.delete_table('pubmed')


    models = {
        'literature.pubmed': {
            'Meta': {'object_name': 'PubMed', 'db_table': "'pubmed'"},
            'pmid': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['literature']
