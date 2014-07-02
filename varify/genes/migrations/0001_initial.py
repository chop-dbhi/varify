# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    depends_on = (
        ('avocado', '0001_initial'),
        ('genome', '0001_initial'),
        ('phenotypes', '0001_initial'),
        ('literature', '0001_initial'),
    )

    def forwards(self, orm):

        # Adding model 'GeneFamily'
        db.create_table('gene_family', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=30, null=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, null=True)),
        ))
        db.send_create_signal('genes', ['GeneFamily'])

        # Adding model 'Synonym'
        db.create_table('synonym', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
        ))
        db.send_create_signal('genes', ['Synonym'])

        # Adding model 'Gene'
        db.create_table('gene', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('chr', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['genome.Chromosome'])),
            ('symbol', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('name', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('hgnc_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('genes', ['Gene'])

        # Adding M2M table for field families on 'Gene'
        db.create_table('gene_families', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('gene', models.ForeignKey(orm['genes.gene'], null=False)),
            ('genefamily', models.ForeignKey(orm['genes.genefamily'], null=False))
        ))
        db.create_unique('gene_families', ['gene_id', 'genefamily_id'])

        # Adding M2M table for field articles on 'Gene'
        db.create_table('gene_pubmed', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('gene', models.ForeignKey(orm['genes.gene'], null=False)),
            ('pubmed', models.ForeignKey(orm['literature.pubmed'], null=False))
        ))
        db.create_unique('gene_pubmed', ['gene_id', 'pubmed_id'])

        # Adding M2M table for field synonyms on 'Gene'
        db.create_table('gene_synonym', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('gene', models.ForeignKey(orm['genes.gene'], null=False)),
            ('synonym', models.ForeignKey(orm['genes.synonym'], null=False))
        ))
        db.create_unique('gene_synonym', ['gene_id', 'synonym_id'])

        # Adding model 'GenePhenotype'
        db.create_table('gene_phenotype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('phenotype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['phenotypes.Phenotype'])),
            ('hgmd_id', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('gene', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['genes.Gene'])),
        ))
        db.send_create_signal('genes', ['GenePhenotype'])

        # Adding model 'Exon'
        db.create_table('exon', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('gene', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['genes.Gene'])),
            ('index', self.gf('django.db.models.fields.IntegerField')()),
            ('start', self.gf('django.db.models.fields.IntegerField')()),
            ('end', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('genes', ['Exon'])

        # Adding model 'Transcript'
        db.create_table('transcript', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('refseq_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('strand', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('start', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('end', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('coding_start', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('coding_end', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('coding_start_status', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('coding_end_status', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('exon_count', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('gene', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['genes.Gene'], null=True, blank=True)),
        ))
        db.send_create_signal('genes', ['Transcript'])

        # Adding M2M table for field exons on 'Transcript'
        db.create_table('transcript_exon', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('transcript', models.ForeignKey(orm['genes.transcript'], null=False)),
            ('exon', models.ForeignKey(orm['genes.exon'], null=False))
        ))
        db.create_unique('transcript_exon', ['transcript_id', 'exon_id'])

        # Adding model 'GeneSet'
        db.create_table('geneset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('context', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['avocado.DataContext'], unique=True, null=True, blank=True)),
            ('count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
        ))
        db.send_create_signal('genes', ['GeneSet'])

        # Adding model 'GeneSetObject'
        db.create_table('geneset_setobject', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('added', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('removed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('object_set', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['genes.GeneSet'], db_column='set_id')),
            ('set_object', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['genes.Gene'], db_column='object_id')),
        ))
        db.send_create_signal('genes', ['GeneSetObject'])


    def backwards(self, orm):

        # Deleting model 'GeneFamily'
        db.delete_table('gene_family')

        # Deleting model 'Synonym'
        db.delete_table('synonym')

        # Deleting model 'Gene'
        db.delete_table('gene')

        # Removing M2M table for field families on 'Gene'
        db.delete_table('gene_families')

        # Removing M2M table for field articles on 'Gene'
        db.delete_table('gene_pubmed')

        # Removing M2M table for field synonyms on 'Gene'
        db.delete_table('gene_synonym')

        # Deleting model 'GenePhenotype'
        db.delete_table('gene_phenotype')

        # Deleting model 'Exon'
        db.delete_table('exon')

        # Deleting model 'Transcript'
        db.delete_table('transcript')

        # Removing M2M table for field exons on 'Transcript'
        db.delete_table('transcript_exon')

        # Deleting model 'GeneSet'
        db.delete_table('geneset')

        # Deleting model 'GeneSetObject'
        db.delete_table('geneset_setobject')


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
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 11, 13, 15, 30, 13, 480582)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 11, 13, 15, 30, 13, 480368)'}),
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
            'hgmd_id': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phenotype': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['phenotypes.Phenotype']"})
        },
        'genes.geneset': {
            'Meta': {'object_name': 'GeneSet', 'db_table': "'geneset'"},
            'context': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['avocado.DataContext']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'genes': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['genes.Gene']", 'through': "orm['genes.GeneSetObject']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
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
