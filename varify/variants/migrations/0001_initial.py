# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    depends_on = (
        ('genome', '0001_initial'),
        ('literature', '0001_initial'),
        ('phenotypes', '0001_initial'),
        ('genes', '0001_initial'),
    )

    def forwards(self, orm):

        # Adding model 'EffectImpact'
        db.create_table('effect_impact', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('variants', ['EffectImpact'])

        # Adding model 'EffectRegion'
        db.create_table('effect_region', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('variants', ['EffectRegion'])

        # Adding model 'Effect'
        db.create_table('effect', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('impact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['variants.EffectImpact'], null=True, blank=True)),
            ('region', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['variants.EffectRegion'], null=True, blank=True)),
        ))
        db.send_create_signal('variants', ['Effect'])

        # Adding model 'VariantType'
        db.create_table('variant_type', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal('variants', ['VariantType'])

        # Adding model 'Variant'
        db.create_table('variant', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('chr', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['genome.Chromosome'])),
            ('pos', self.gf('django.db.models.fields.IntegerField')()),
            ('ref', self.gf('django.db.models.fields.TextField')(db_index=True)),
            ('alt', self.gf('django.db.models.fields.TextField')(db_index=True)),
            ('md5', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('rsid', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['variants.VariantType'], null=True)),
            ('liftover', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
        ))
        db.send_create_signal('variants', ['Variant'])

        # Adding unique constraint on 'Variant', fields ['chr', 'pos', 'ref', 'alt']
        db.create_unique('variant', ['chr_id', 'pos', 'ref', 'alt'])

        # Adding M2M table for field articles on 'Variant'
        db.create_table('variant_pubmed', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('variant', models.ForeignKey(orm['variants.variant'], null=False)),
            ('pubmed', models.ForeignKey(orm['literature.pubmed'], null=False))
        ))
        db.create_unique('variant_pubmed', ['variant_id', 'pubmed_id'])

        # Adding model 'VariantPhenotype'
        db.create_table('variant_phenotype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('phenotype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['phenotypes.Phenotype'])),
            ('hgmd_id', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('variant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['variants.Variant'])),
        ))
        db.send_create_signal('variants', ['VariantPhenotype'])

        # Adding model 'ThousandG'
        db.create_table('1000g', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('variant', self.gf('django.db.models.fields.related.ForeignKey')(related_name='thousandg', to=orm['variants.Variant'])),
            ('an', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('ac', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('af', self.gf('django.db.models.fields.FloatField')(null=True, db_index=True)),
            ('aa', self.gf('django.db.models.fields.TextField')(null=True)),
            ('amr_af', self.gf('django.db.models.fields.FloatField')(null=True, db_index=True)),
            ('asn_af', self.gf('django.db.models.fields.FloatField')(null=True, db_index=True)),
            ('afr_af', self.gf('django.db.models.fields.FloatField')(null=True, db_index=True)),
            ('eur_af', self.gf('django.db.models.fields.FloatField')(null=True, db_index=True)),
        ))
        db.send_create_signal('variants', ['ThousandG'])

        # Adding model 'EVS'
        db.create_table('evs', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('variant', self.gf('django.db.models.fields.related.ForeignKey')(related_name='evs', to=orm['variants.Variant'])),
            ('ea_ac_ref', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('ea_ac_alt', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('aa_ac_ref', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('aa_ac_alt', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('all_ac_ref', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('all_ac_alt', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('ea_maf', self.gf('django.db.models.fields.FloatField')(null=True, db_index=True)),
            ('aa_maf', self.gf('django.db.models.fields.FloatField')(null=True, db_index=True)),
            ('all_maf', self.gf('django.db.models.fields.FloatField')(null=True, db_index=True)),
            ('clinical_info', self.gf('django.db.models.fields.TextField')(null=True)),
        ))
        db.send_create_signal('variants', ['EVS'])

        # Adding model 'PolyPhen2'
        db.create_table('polyphen2', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('variant', self.gf('django.db.models.fields.related.ForeignKey')(related_name='polyphen2', to=orm['variants.Variant'])),
            ('score', self.gf('django.db.models.fields.FloatField')(null=True, db_index=True)),
            ('refaa', self.gf('django.db.models.fields.CharField')(max_length=2, null=True)),
        ))
        db.send_create_signal('variants', ['PolyPhen2'])

        # Adding model 'Sift'
        db.create_table('sift', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('variant', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sift', to=orm['variants.Variant'])),
            ('score', self.gf('django.db.models.fields.FloatField')(null=True, db_index=True)),
            ('refaa', self.gf('django.db.models.fields.CharField')(max_length=2, null=True)),
            ('varaa', self.gf('django.db.models.fields.CharField')(max_length=2, null=True)),
        ))
        db.send_create_signal('variants', ['Sift'])

        # Adding model 'FunctionalClass'
        db.create_table('variant_functional_class', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('variants', ['FunctionalClass'])

        # Adding model 'VariantEffect'
        db.create_table('variant_effect', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('variant', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='effects', null=True, to=orm['variants.Variant'])),
            ('codon_change', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('amino_acid_change', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('exon', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['genes.Exon'], null=True, blank=True)),
            ('transcript', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['genes.Transcript'], null=True, blank=True)),
            ('gene', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['genes.Gene'], null=True, blank=True)),
            ('effect', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['variants.Effect'], null=True, blank=True)),
            ('functional_class', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['variants.FunctionalClass'], null=True, blank=True)),
        ))
        db.send_create_signal('variants', ['VariantEffect'])


    def backwards(self, orm):

        # Removing unique constraint on 'Variant', fields ['chr', 'pos', 'ref', 'alt']
        db.delete_unique('variant', ['chr_id', 'pos', 'ref', 'alt'])

        # Deleting model 'EffectImpact'
        db.delete_table('effect_impact')

        # Deleting model 'EffectRegion'
        db.delete_table('effect_region')

        # Deleting model 'Effect'
        db.delete_table('effect')

        # Deleting model 'VariantType'
        db.delete_table('variant_type')

        # Deleting model 'Variant'
        db.delete_table('variant')

        # Removing M2M table for field articles on 'Variant'
        db.delete_table('variant_pubmed')

        # Deleting model 'VariantPhenotype'
        db.delete_table('variant_phenotype')

        # Deleting model 'ThousandG'
        db.delete_table('1000g')

        # Deleting model 'EVS'
        db.delete_table('evs')

        # Deleting model 'PolyPhen2'
        db.delete_table('polyphen2')

        # Deleting model 'Sift'
        db.delete_table('sift')

        # Deleting model 'FunctionalClass'
        db.delete_table('variant_functional_class')

        # Deleting model 'VariantEffect'
        db.delete_table('variant_effect')


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
            'aa_ac_alt': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'aa_ac_ref': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'aa_maf': ('django.db.models.fields.FloatField', [], {'null': 'True', 'db_index': 'True'}),
            'all_ac_alt': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'all_ac_ref': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'all_maf': ('django.db.models.fields.FloatField', [], {'null': 'True', 'db_index': 'True'}),
            'clinical_info': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'ea_ac_alt': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'ea_ac_ref': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'ea_maf': ('django.db.models.fields.FloatField', [], {'null': 'True', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
