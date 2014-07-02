# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Removing unique constraint on 'Sample', fields ['cohort', 'label']
        db.delete_unique('sample', ['cohort_id', 'label'])

        # Adding field 'Cohort.label'
        db.add_column('project_cohort', 'label', self.gf('django.db.models.fields.CharField')(max_length=100, null=True), keep_default=False)

        # Changing field 'Cohort.name'
        db.alter_column('project_cohort', 'name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Removing index on 'Cohort', fields ['name']
        db.delete_index('project_cohort', ['name'])

        # Adding unique constraint on 'Cohort', fields ['project', 'name']
        db.create_unique('project_cohort', ['project_id', 'name'])

        # Adding field 'Project.label'
        db.add_column('project', 'label', self.gf('django.db.models.fields.CharField')(max_length=100, null=True), keep_default=False)

        # Changing field 'Project.name'
        db.alter_column('project', 'name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Adding unique constraint on 'Project', fields ['name']
        db.create_unique('project', ['name'])

        # Adding field 'Sample.name'
        db.add_column('sample', 'name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True), keep_default=False)

        # Changing field 'Sample.label'
        db.alter_column('sample', 'label', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Removing index on 'Sample', fields ['label']
        db.delete_index('sample', ['label'])

        # Adding unique constraint on 'Sample', fields ['cohort', 'name']
        db.create_unique('sample', ['cohort_id', 'name'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Sample', fields ['cohort', 'name']
        db.delete_unique('sample', ['cohort_id', 'name'])

        # Adding index on 'Sample', fields ['label']
        db.create_index('sample', ['label'])

        # Removing unique constraint on 'Project', fields ['name']
        db.delete_unique('project', ['name'])

        # Removing unique constraint on 'Cohort', fields ['project', 'name']
        db.delete_unique('project_cohort', ['project_id', 'name'])

        # Adding index on 'Cohort', fields ['name']
        db.create_index('project_cohort', ['name'])

        # Deleting field 'Cohort.label'
        db.delete_column('project_cohort', 'label')

        # User chose to not deal with backwards NULL issues for 'Cohort.name'
        raise RuntimeError("Cannot reverse this migration. 'Cohort.name' and its values cannot be restored.")

        # Deleting field 'Project.label'
        db.delete_column('project', 'label')

        # User chose to not deal with backwards NULL issues for 'Project.name'
        raise RuntimeError("Cannot reverse this migration. 'Project.name' and its values cannot be restored.")

        # Deleting field 'Sample.name'
        db.delete_column('sample', 'name')

        # User chose to not deal with backwards NULL issues for 'Sample.label'
        raise RuntimeError("Cannot reverse this migration. 'Sample.label' and its values cannot be restored.")

        # Adding unique constraint on 'Sample', fields ['cohort', 'label']
        db.create_unique('sample', ['cohort_id', 'label'])


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
            'Meta': {'unique_together': "(('project', 'name'),)", 'object_name': 'Cohort', 'db_table': "'project_cohort'"},
            'count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'investigator': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
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
            'Meta': {'unique_together': "(('name',),)", 'object_name': 'Project', 'db_table': "'project'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
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
            'Meta': {'unique_together': "(('cohort', 'name'),)", 'object_name': 'Sample', 'db_table': "'sample'"},
            'bio_sample': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'cohort': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'samples'", 'null': 'True', 'to': "orm['samples.Cohort']"}),
            'count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'line': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'md5': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
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
