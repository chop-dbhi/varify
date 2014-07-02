# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
from avocado.models import DataField

class Migration(DataMigration):

    depends_on = (
        ('avocado', '0001_initial'),
    )

    def forwards(self, orm):
        "Write your forwards methods here."
        fields = DataField.objects.filter(app_name='phenotype')
        fields.update(app_name='phenotypes')


    def backwards(self, orm):
        "Write your backwards methods here."
        fields = DataField.objects.filter(app_name='phenotypes')
        fields.update(app_name='phenotype')

    models = {
        'literature.pubmed': {
            'Meta': {'object_name': 'PubMed', 'db_table': "'pubmed'"},
            'pmid': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'})
        },
        'phenotypes.phenotype': {
            'Meta': {'object_name': 'Phenotype', 'db_table': "'phenotype'"},
            'articles': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['literature.PubMed']", 'symmetrical': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'hpo_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'term': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '1000'})
        }
    }

    complete_apps = ['phenotypes']
