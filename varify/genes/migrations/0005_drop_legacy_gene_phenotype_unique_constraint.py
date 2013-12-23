# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        try:
            db.delete_unique('gene_phenotype', ['gene_id', 'phenotype_id'])
        except ValueError:
            # When starting completely fresh, there is no unique constraint on
            # the table on these columns yet so catch that here instead of
            # letting the migration fail.
            pass

    def backwards(self, orm):
        pass

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'avocado.datacontext': {
            'Meta': {'object_name': 'DataContext'},
            'archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'composite': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'_count'"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'json': ('jsonfield.fields.JSONField', [], {'default': '{}', 'null': 'True', 'blank': 'True'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'session': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'session_key': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'datacontext+'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'genes.exon': {
            'Meta': {'object_name': 'Exon', 'db_table': "'exon'"},
            'end': ('django.db.models.fields.IntegerField', [], {}),
            'gene': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['genes.Gene']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {}),
            'start': ('django.db.models.fields.IntegerField', [], {})
        },
        'genes.gene': {
            'Meta': {'object_name': 'Gene', 'db_table': "'gene'"},
            'articles': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['literature.PubMed']", 'db_table': "'gene_pubmed'", 'symmetrical': 'False'}),
            'chr': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['genome.Chromosome']"}),
            'families': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['genes.GeneFamily']", 'symmetrical': 'False', 'blank': 'True'}),
            'hgnc_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'phenotypes': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['phenotypes.Phenotype']", 'through': "orm['genes.GenePhenotype']", 'symmetrical': 'False'}),
            'symbol': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'synonyms': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['genes.Synonym']", 'db_table': "'gene_synonym'", 'symmetrical': 'False'})
        },
        'genes.genefamily': {
            'Meta': {'object_name': 'GeneFamily', 'db_table': "'gene_family'"},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'})
        },
        'genes.genephenotype': {
            'Meta': {'object_name': 'GenePhenotype', 'db_table': "'gene_phenotype'"},
            'gene': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['genes.Gene']"}),
            'hgmd_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phenotype': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['phenotypes.Phenotype']"})
        },
        'genes.geneset': {
            'Meta': {'ordering': "('user', 'name')", 'object_name': 'GeneSet', 'db_table': "'geneset'"},
            'context': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['avocado.DataContext']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'genes': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['genes.Gene']", 'through': "orm['genes.GeneSetObject']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'genes.genesetobject': {
            'Meta': {'object_name': 'GeneSetObject', 'db_table': "'geneset_setobject'"},
            'added': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_set': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['genes.GeneSet']", 'db_column': "'set_id'"}),
            'removed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'set_object': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['genes.Gene']", 'db_column': "'object_id'"})
        },
        'genes.synonym': {
            'Meta': {'object_name': 'Synonym', 'db_table': "'synonym'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        'genes.transcript': {
            'Meta': {'object_name': 'Transcript', 'db_table': "'transcript'"},
            'coding_end': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'coding_end_status': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'coding_start': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'coding_start_status': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'exon_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'exons': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['genes.Exon']", 'db_table': "'transcript_exon'", 'symmetrical': 'False'}),
            'gene': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['genes.Gene']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'refseq_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'start': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'strand': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'})
        },
        'genome.chromosome': {
            'Meta': {'ordering': "['order']", 'object_name': 'Chromosome', 'db_table': "'chromosome'"},
            'code': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '2', 'db_index': 'True'})
        },
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

    complete_apps = ['genes']
