# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    depends_on = (
        ('avocado', '0034_auto__add_field_datafield_type'),
        ('variants', '0001_initial'),
    )

    def forwards(self, orm):

        # Adding model 'Person'
        db.create_table('person', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('mrn', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('sex', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('proband', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('samples', ['Person'])

        # Adding model 'Relation'
        db.create_table('relation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(related_name='family', to=orm['samples.Person'])),
            ('relative', self.gf('django.db.models.fields.related.ForeignKey')(related_name='relative_of', to=orm['samples.Person'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('generation', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('samples', ['Relation'])

        # Adding model 'Project'
        db.create_table('project', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('samples', ['Project'])

        # Adding model 'Cohort'
        db.create_table('project_cohort', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('investigator', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['samples.Project'])),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('count', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('samples', ['Cohort'])

        # Adding model 'CohortVariant'
        db.create_table('cohort_variant', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('variant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['variants.Variant'])),
            ('cohort', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['samples.Cohort'])),
            ('af', self.gf('django.db.models.fields.FloatField')(null=True, db_index=True)),
        ))
        db.send_create_signal('samples', ['CohortVariant'])

        # Adding unique constraint on 'CohortVariant', fields ['variant', 'cohort']
        db.create_unique('cohort_variant', ['variant_id', 'cohort_id'])

        # Adding model 'Sample'
        db.create_table('sample', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('cohort', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='samples', null=True, to=orm['samples.Cohort'])),
            ('version', self.gf('django.db.models.fields.IntegerField')()),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='samples', null=True, to=orm['samples.Person'])),
            ('count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('bio_sample', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('md5', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('line', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('samples', ['Sample'])

        # Adding unique constraint on 'Sample', fields ['label', 'cohort']
        db.create_unique('sample', ['label', 'cohort_id'])

        # Adding model 'SampleRun'
        db.create_table('sample_run', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('run_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('facility', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('dax_xml', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('genome', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['genome.Genome'], null=True, blank=True)),
            ('sample', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['samples.Sample'])),
        ))
        db.send_create_signal('samples', ['SampleRun'])

        # Adding model 'Result'
        db.create_table('sample_result', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('sample', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['samples.Sample'], null=True, blank=True)),
            ('variant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['variants.Variant'], null=True, blank=True)),
            ('quality', self.gf('django.db.models.fields.FloatField')(db_index=True, null=True, blank=True)),
            ('read_depth', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('genotype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['genome.Genotype'], null=True, blank=True)),
            ('genotype_quality', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('coverage_ref', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('coverage_alt', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('phred_scaled_likelihood', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('in_dbsnp', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('downsampling', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('spanning_deletions', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('mq', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('mq0', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('baseq_rank_sum', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('mq_rank_sum', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('read_pos_rank_sum', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('strand_bias', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('homopolymer_run', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('haplotype_score', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('quality_by_depth', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('fisher_strand', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal('samples', ['Result'])


    def backwards(self, orm):

        # Removing unique constraint on 'Sample', fields ['label', 'cohort']
        db.delete_unique('sample', ['label', 'cohort_id'])

        # Removing unique constraint on 'CohortVariant', fields ['variant', 'cohort']
        db.delete_unique('cohort_variant', ['variant_id', 'cohort_id'])

        # Deleting model 'Person'
        db.delete_table('person')

        # Deleting model 'Relation'
        db.delete_table('relation')

        # Deleting model 'Project'
        db.delete_table('project')

        # Deleting model 'Cohort'
        db.delete_table('project_cohort')

        # Deleting model 'CohortVariant'
        db.delete_table('cohort_variant')

        # Deleting model 'Sample'
        db.delete_table('sample')

        # Deleting model 'SampleRun'
        db.delete_table('sample_run')

        # Deleting model 'Result'
        db.delete_table('sample_result')


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
        },
        'samples.cohort': {
            'Meta': {'object_name': 'Cohort', 'db_table': "'project_cohort'"},
            'count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'investigator': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['samples.Project']"}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'samples.cohortvariant': {
            'Meta': {'unique_together': "(('variant', 'cohort'),)", 'object_name': 'CohortVariant', 'db_table': "'cohort_variant'"},
            'af': ('django.db.models.fields.FloatField', [], {'null': 'True', 'db_index': 'True'}),
            'cohort': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['samples.Cohort']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'variant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['variants.Variant']"})
        },
        'samples.person': {
            'Meta': {'object_name': 'Person', 'db_table': "'person'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'mrn': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'proband': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'relations': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['samples.Person']", 'through': "orm['samples.Relation']", 'symmetrical': 'False'}),
            'sex': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        'samples.project': {
            'Meta': {'object_name': 'Project', 'db_table': "'project'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'samples.relation': {
            'Meta': {'ordering': "('person', '-generation')", 'object_name': 'Relation', 'db_table': "'relation'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'generation': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'family'", 'to': "orm['samples.Person']"}),
            'relative': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'relative_of'", 'to': "orm['samples.Person']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'samples.result': {
            'Meta': {'object_name': 'Result', 'db_table': "'sample_result'"},
            'baseq_rank_sum': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'coverage_alt': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'coverage_ref': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'downsampling': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'fisher_strand': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'genotype': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['genome.Genotype']", 'null': 'True', 'blank': 'True'}),
            'genotype_quality': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'haplotype_score': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'homopolymer_run': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_dbsnp': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'mq': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'mq0': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'mq_rank_sum': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'phred_scaled_likelihood': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'quality': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'quality_by_depth': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'read_depth': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'read_pos_rank_sum': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'sample': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['samples.Sample']", 'null': 'True', 'blank': 'True'}),
            'spanning_deletions': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'strand_bias': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'variant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['variants.Variant']", 'null': 'True', 'blank': 'True'})
        },
        'samples.sample': {
            'Meta': {'unique_together': "(('label', 'cohort'),)", 'object_name': 'Sample', 'db_table': "'sample'"},
            'bio_sample': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'cohort': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'samples'", 'null': 'True', 'to': "orm['samples.Cohort']"}),
            'count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'line': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'md5': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'samples'", 'null': 'True', 'to': "orm['samples.Person']"}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'version': ('django.db.models.fields.IntegerField', [], {})
        },
        'samples.samplerun': {
            'Meta': {'object_name': 'SampleRun', 'db_table': "'sample_run'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'dax_xml': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'facility': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'genome': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['genome.Genome']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'run_time': ('django.db.models.fields.DateTimeField', [], {}),
            'sample': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['samples.Sample']"})
        },
        'variants.variant': {
            'Meta': {'unique_together': "(('chr', 'pos', 'ref', 'alt'),)", 'object_name': 'Variant', 'db_table': "'variant'"},
            'alt': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            'articles': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['literature.PubMed']", 'db_table': "'variant_pubmed'", 'symmetrical': 'False'}),
            'chr': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['genome.Chromosome']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'liftover': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'md5': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'phenotypes': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['phenotypes.Phenotype']", 'through': "orm['variants.VariantPhenotype']", 'symmetrical': 'False'}),
            'pos': ('django.db.models.fields.IntegerField', [], {}),
            'ref': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            'rsid': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['variants.VariantType']", 'null': 'True'})
        },
        'variants.variantphenotype': {
            'Meta': {'object_name': 'VariantPhenotype', 'db_table': "'variant_phenotype'"},
            'hgmd_id': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phenotype': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['phenotypes.Phenotype']"}),
            'variant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['variants.Variant']"})
        },
        'variants.varianttype': {
            'Meta': {'ordering': "['order']", 'object_name': 'VariantType', 'db_table': "'variant_type'"},
            'code': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['samples']
