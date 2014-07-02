# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'EVS.gts'
        db.add_column('evs', 'gts', self.gf('django.db.models.fields.CharField')(max_length=200, null=True), keep_default=False)

        # Adding field 'EVS.ea_gtc'
        db.add_column('evs', 'ea_gtc', self.gf('django.db.models.fields.CharField')(max_length=200, null=True), keep_default=False)

        # Adding field 'EVS.aa_gtc'
        db.add_column('evs', 'aa_gtc', self.gf('django.db.models.fields.CharField')(max_length=200, null=True), keep_default=False)

        # Adding field 'EVS.all_gtc'
        db.add_column('evs', 'all_gtc', self.gf('django.db.models.fields.CharField')(max_length=200, null=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'EVS.gts'
        db.delete_column('evs', 'gts')

        # Deleting field 'EVS.ea_gtc'
        db.delete_column('evs', 'ea_gtc')

        # Deleting field 'EVS.aa_gtc'
        db.delete_column('evs', 'aa_gtc')

        # Deleting field 'EVS.all_gtc'
        db.delete_column('evs', 'all_gtc')


    models = {
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
        },
        'variants.effect': {
            'Meta': {'ordering': "['order']", 'object_name': 'Effect', 'db_table': "'effect'"},
            'code': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'impact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['variants.EffectImpact']", 'null': 'True', 'blank': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['variants.EffectRegion']", 'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'variants.effectimpact': {
            'Meta': {'ordering': "['order']", 'object_name': 'EffectImpact', 'db_table': "'effect_impact'"},
            'code': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'variants.effectregion': {
            'Meta': {'ordering': "['order']", 'object_name': 'EffectRegion', 'db_table': "'effect_region'"},
            'code': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'variants.evs': {
            'Meta': {'object_name': 'EVS', 'db_table': "'evs'"},
            'aa_ac_alt': ('django.db.models.fields.IntegerField', [], {'max_length': '20', 'null': 'True'}),
            'aa_ac_ref': ('django.db.models.fields.IntegerField', [], {'max_length': '20', 'null': 'True'}),
            'aa_gtc': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'aa_maf': ('django.db.models.fields.FloatField', [], {'null': 'True', 'db_index': 'True'}),
            'all_ac_alt': ('django.db.models.fields.IntegerField', [], {'max_length': '20', 'null': 'True'}),
            'all_ac_ref': ('django.db.models.fields.IntegerField', [], {'max_length': '20', 'null': 'True'}),
            'all_gtc': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'all_maf': ('django.db.models.fields.FloatField', [], {'null': 'True', 'db_index': 'True'}),
            'clinical_association': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'ea_ac_alt': ('django.db.models.fields.IntegerField', [], {'max_length': '20', 'null': 'True'}),
            'ea_ac_ref': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'ea_gtc': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'ea_maf': ('django.db.models.fields.FloatField', [], {'null': 'True', 'db_index': 'True'}),
            'gts': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'read_depth': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'variant': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'evs'", 'to': "orm['variants.Variant']"})
        },
        'variants.functionalclass': {
            'Meta': {'ordering': "['order']", 'object_name': 'FunctionalClass', 'db_table': "'variant_functional_class'"},
            'code': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'variants.polyphen2': {
            'Meta': {'object_name': 'PolyPhen2', 'db_table': "'polyphen2'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'refaa': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True'}),
            'score': ('django.db.models.fields.FloatField', [], {'null': 'True', 'db_index': 'True'}),
            'variant': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'polyphen2'", 'to': "orm['variants.Variant']"})
        },
        'variants.sift': {
            'Meta': {'object_name': 'Sift', 'db_table': "'sift'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'refaa': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True'}),
            'score': ('django.db.models.fields.FloatField', [], {'null': 'True', 'db_index': 'True'}),
            'varaa': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True'}),
            'variant': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sift'", 'to': "orm['variants.Variant']"})
        },
        'variants.thousandg': {
            'Meta': {'object_name': 'ThousandG', 'db_table': "'1000g'"},
            'aa': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'ac': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'af': ('django.db.models.fields.FloatField', [], {'null': 'True', 'db_index': 'True'}),
            'afr_af': ('django.db.models.fields.FloatField', [], {'null': 'True', 'db_index': 'True'}),
            'amr_af': ('django.db.models.fields.FloatField', [], {'null': 'True', 'db_index': 'True'}),
            'an': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'asn_af': ('django.db.models.fields.FloatField', [], {'null': 'True', 'db_index': 'True'}),
            'eur_af': ('django.db.models.fields.FloatField', [], {'null': 'True', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'variant': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'thousandg'", 'to': "orm['variants.Variant']"})
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
        'variants.varianteffect': {
            'Meta': {'object_name': 'VariantEffect', 'db_table': "'variant_effect'"},
            'amino_acid_change': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'codon_change': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'effect': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['variants.Effect']", 'null': 'True', 'blank': 'True'}),
            'exon': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['genes.Exon']", 'null': 'True', 'blank': 'True'}),
            'functional_class': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['variants.FunctionalClass']", 'null': 'True', 'blank': 'True'}),
            'gene': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['genes.Gene']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'transcript': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['genes.Transcript']", 'null': 'True', 'blank': 'True'}),
            'variant': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'effects'", 'null': 'True', 'to': "orm['variants.Variant']"})
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

    complete_apps = ['variants']
