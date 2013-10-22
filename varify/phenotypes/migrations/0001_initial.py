# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    depends_on = (
        ('literature', '0001_initial'),
    )

    def forwards(self, orm):

        # Adding model 'Phenotype'
        db.create_table('phenotype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('term', self.gf('django.db.models.fields.CharField')(unique=True, max_length=1000)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('hpo_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
        ))
        db.send_create_signal('phenotypes', ['Phenotype'])

        # Adding M2M table for field articles on 'Phenotype'
        db.create_table('phenotype_articles', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('phenotype', models.ForeignKey(orm['phenotypes.phenotype'], null=False)),
            ('pubmed', models.ForeignKey(orm['literature.pubmed'], null=False))
        ))
        db.create_unique('phenotype_articles', ['phenotype_id', 'pubmed_id'])


    def backwards(self, orm):

        # Deleting model 'Phenotype'
        db.delete_table('phenotype')

        # Removing M2M table for field articles on 'Phenotype'
        db.delete_table('phenotype_articles')


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
