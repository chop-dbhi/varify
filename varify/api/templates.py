"API resource templates. To be used with django-preserialize."
from copy import deepcopy

# Since this is a Lexicon subclass, the `label` is only used and merged
# into the parent object.
Chromosome = {
    'fields': ['chr'],
    'aliases': {
        'chr': 'label',
    },
    'merge': True,
}


# Flat list of PubMed articles. This can be used with Gene, Phenotype, or
# Variant
Article = {
    'fields': ['pmid'],
    'values_list': True,
}


# Phenotype representation
Phenotype = {
    'related': {
        'articles': Article,
    }
}

# Reference phenotype with minimal information
PhenotypeList = {
    'fields': ['term'],
    'values_list': True,
}

VariantPhenotype = {
    'exclude': ['variant'],
    'related': {
        'phenotype': {
            'fields': ['term', 'hpo_id'],
            'merge': True,
        }
    }
}

PhenotypeSearch = {
    'fields': [':pk', 'term', 'description'],
}


GeneFamily = {
    'fields': ['description'],
    'values_list': True,
}

# Flat list of gene synonyms. This must be used in the context of a Gene
GeneSynonym = {
    'fields': ['label'],
    'values_list': True,
}


GeneTranscript = {
    'fields': ['transcript'],
    'aliases': {
        'transcript': 'refseq_id',
    },
    'values_list': True,
}


# Detailed gene information
Gene = {
    'related': {
        'chr': Chromosome,
        'synonyms': GeneSynonym,
        'transcripts': GeneTranscript,
        'families': GeneFamily,
        'articles': Article,
        'phenotypes': PhenotypeList,
    }
}

# Minimal information for the gene search
GeneSearch = {
    'fields': [':pk', 'symbol', 'name', 'synonyms', 'approved'],
    'related': {
        'synonyms': {
            'fields': ['label'],
            'values_list': True,
        }
    }
}


# Limited gene information to be embedded in a Transcript
TranscriptGene = {
    'exclude': ['synonyms', 'transcripts', 'chr', 'families', 'id', 'name'],
    'related': {
        'chr': Chromosome,
        'articles': Article,
    }
}

# This version of the resource includes the gene this transcript represents
Transcript = {
    'fields': ['transcript', 'gene'],
    'aliases': {
        'transcript': 'refseq_id',
    },
    'related': {
        'gene': TranscriptGene,
    },
}


# Lexicon of types of variants, only the `label` must be used here. This
# is only ever used in the context of a variant, so the name `type` is
# suitable.
VariantType = {
    'fields': ['type'],
    'aliases': {
        'type': 'label',
    },
    'merge': True,
}

# SIFT deleterious prediction and raw score
Sift = {
    'fields': ['score', 'prediction'],
}

# PolyPhen2 deleterious prediction and raw score
PolyPhen2 = {
    'fields': ['score', 'prediction'],
}

# Allele frequencies for various races. This must be used in the context
# of a Variant
ThousandG = {
    'fields': ['all_af', 'amr_af', 'afr_af', 'asn_af', 'eur_af'],
    'aliases': {
        'all_af': 'af',
    }
}

# Allele frequencies for various races. This must be used in the context
# of a Variant
Evs = {
    'fields': ['all_af', 'afr_af', 'eur_af', 'read_depth'],
    'aliases': {
        'eur_af': 'ea_af',
        'afr_af': 'aa_af',
    }
}


# Lexicon, only use the label
EffectRegion = {
    'fields': ['region'],
    'aliases': {
        'region': 'label',
    },
    'merge': True,
}

# Lexicon, only use the label
EffectImpact = {
    'fields': ['impact'],
    'aliases': {
        'impact': 'label',
    },
    'merge': True,
}

# Extended lexicon, who other properties about the effect type
Effect = {
    'fields': ['type', 'impact'],
    'aliases': {
        'type': 'label',
    },
    'related': {
        'impact': EffectImpact,
        'region': EffectRegion,
    },
    'merge': True,
}


# The variant effect has quite a few components. Since it does not include
# Variant, it is assumed to be used in the context of a Variant
VariantEffect = {
    'fields': ['transcript', 'amino_acid_change', 'effect', 'hgvs_c',
               'hgvs_p', 'segment'],
    'related': {
        'transcript': Transcript,
        'functional_class': {
            'fields': ['functional_class'],
            'aliases': {
                'functional_class': 'label',
            },
            'merge': True,
        },
        'effect': Effect
    }
}


# Represents the simplest representation of a Sample, that is, the primary key
# and the Sample name.
SimpleSample = {
    'fields': [':pk', 'name'],
}


# Used to augment the variant resource below. This is separate to
# be able to restrict cohorts for the requesting user
CohortVariant = {
    'fields': ['af', 'cohort'],
    'related': {
        'cohort': {
            'fields': ['name', 'size'],
            'aliases': {
                'size': 'count',
            },
            'merge': True,
        }
    }
}


# Detailed resource for a variant, this should only be used when requesting
# one or a few variants at time (meaning don't pull down 1000).
Variant = {
    'fields': [':pk', 'chr', 'pos', 'ref', 'alt', 'rsid', 'type',
               'effects', '1000g', 'sift', 'evs', 'polyphen2', 'articles',
               'phenotypes'],

    # Map to cleaner names
    'aliases': {
        '1000g': 'thousandg',
        'phenotypes': 'variant_phenotypes',
    },

    'related': {
        'type': VariantType,
        'chr': Chromosome,
        'sift': Sift,
        'thousandg': ThousandG,
        'evs': Evs,
        'polyphen2': PolyPhen2,
        'effects': VariantEffect,
        'articles': Article,
        'variant_phenotypes': VariantPhenotype,
        'cohort_details': CohortVariant,
    }
}


# Project
# Exposes the label
Project = {
    'fields': ['project'],
    'merge': True,
    'aliases': {
        'project': 'label',
    },
}


# Batch
# Exposes the batch and project names and size
Batch = {
    'fields': ['batch'],
    'merge': True,
    'aliases': {
        'batch': 'label',
    },
}


# Sample Resource
# project and batch names are merged into the sample object to
# remove excessive nesting.
Sample = {
    'fields': [':pk', 'batch', 'count', 'created', 'label', 'project'],
    'related': {
        'batch': Batch,
        'project': Project,
    }
}


ResultVariant = {
    'fields': ['variant_id', 'chr', 'pos', 'ref', 'alt'],
    'aliases': {
        'variant_id': 'id',
    },
    'related': {
        'chr': Chromosome,
    },
    'merge': True,
}


Genotype = {
    'fields': ['genotype', 'genotype_description'],
    'aliases': {
        'genotype': 'value',
        'genotype_description': 'label',
    },
    'merge': True,
}


Assessment = {
    'exclude': ['user', 'sample_result', 'notes']
}

ResultAssessment = {
    'fields': ['id', 'assessment_category', 'pathogenicity']
}

SampleResult = {
    'fields': [':pk', ':local', 'genotype_value', 'read_depth_ref',
               'read_depth_alt', 'base_counts'],
    'exclude': ['created', 'modified', 'downsampling', 'fisher_strand',
                'homopolymer_run', 'notes', 'spanning_deletions',
                'strand_bias', 'mq', 'mq0', 'mq_rank_sum',
                'phred_scaled_likelihood', 'read_pos_rank_sum', 'in_dbsnp',
                'coverage_ref', 'coverage_alt'],
    'aliases': {
        'base_counts': 'base_count_map',
        'read_depth_alt': 'coverage_alt',
        'read_depth_ref': 'coverage_ref',
    },
    'related': {
        'variant': ResultVariant,
        'sample': Sample,
        'genotype': Genotype,
    }
}

# This is deviation of the normal SampleResult which only includes
# the variant_id. This is used downstreamed to simply link together
# data from an alternate source.
SampleResultVariant = deepcopy(SampleResult)
SampleResultVariant['related']['variant'] = {
    'fields': ['variant_id'],
    'aliases': {
        'variant_id': 'id',
    },
    'merge': True,
}


SimpleResultSet = {
    'fields': [':local', 'created', 'modified'],
    'exclude': ['user', 'results'],
    'related': {
        'sample': Sample
    }
}

ResultSet = {
    'fields': [':local', 'created', 'modified'],
    'related': {
        'sample': Sample,
        'results': SampleResult
    }
}
