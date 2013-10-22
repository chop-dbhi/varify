# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Chromosome'
        db.create_table('chromosome', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=2, db_index=True)),
        ))
        db.send_create_signal('genome', ['Chromosome'])

        # Adding model 'Genome'
        db.create_table('genome', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('released', self.gf('django.db.models.fields.DateField')(null=True)),
        ))
        db.send_create_signal('genome', ['Genome'])

        # Adding model 'Genotype'
        db.create_table('genotype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=3)),
        ))
        db.send_create_signal('genome', ['Genotype'])


    def backwards(self, orm):
        
        # Deleting model 'Chromosome'
        db.delete_table('chromosome')

        # Deleting model 'Genome'
        db.delete_table('genome')

        # Deleting model 'Genotype'
        db.delete_table('genotype')


    models = {
        'genome.chromosome': {
            'Meta': {'ordering': "['order']", 'object_name': 'Chromosome', 'db_table': "'chromosome'"},
            'code': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '2', 'db_index': 'True'})
        },
        'genome.genome': {
            'Meta': {'object_name': 'Genome', 'db_table': "'genome'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'released': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'genome.genotype': {
            'Meta': {'object_name': 'Genotype', 'db_table': "'genotype'"},
            'code': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '3'})
        }
    }

    complete_apps = ['genome']
