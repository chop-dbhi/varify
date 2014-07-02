import re
from varify.raw.management.subcommands.load import LoadCommand
from varify.raw.utils.stream import PGCopyEditor

valid_date_re = re.compile('\d{4}-\d{2}-\d{2}')


class HGNCGeneParser(PGCopyEditor):
    def process_column(self, idx, value):
        if not value:
            value = None
        elif idx == 0:
            return value[5:]
        elif idx in (19, 38, 39):
            return value[4:]
        elif idx in (11, 12, 13, 14):
            if valid_date_re.match(value):
                return value
        return super(HGNCGeneParser, self).process_column(idx, value)


class HGNCGeneFamilyParser(PGCopyEditor):
    def __init__(self, *args, **kwargs):
        kwargs['indices'] = [1, 2, 3, 4]
        super(HGNCGeneFamilyParser, self).__init__(*args, **kwargs)


class Command(LoadCommand):
    targets = ['hgnc', 'hgncFamilies']

    qualified_names = {
        'hgnc': '"raw"."hgnc"',
        'hgncFamilies': '"raw"."hgnc_families"',
    }

    drop_sql = {
        'hgnc': 'DROP TABLE IF EXISTS {}',
        'hgncFamilies': 'DROP TABLE IF EXISTS {}',
    }

    create_sql = {
        'hgnc': '''CREATE TABLE {} (
            "hgnc_id" integer NOT NULL PRIMARY KEY,
            "approved_symbol" varchar(255) NOT NULL,
            "approved_name" text NOT NULL,
            "status" varchar(50) NOT NULL,
            "locus_type" varchar(100) NOT NULL,
            "locus_group" varchar(100) NOT NULL,
            "previous_symbols" text,
            "previous_names" text,
            "synonyms" text,
            "name_synonyms" text,
            "chromosome" varchar(255),
            "date_approved" date,
            "date_modified" date,
            "date_symbol_changed" date,
            "date_name_changed" date,
            "accession_numbers" text,
            "enzyme_ids" text,
            "entrez_gene_id" integer,
            "ensembl_gene_id" varchar(50),
            "mgi_id" varchar(50),
            "specialist_database_links" text,
            "specialist_database_ids" text,
            "pubmed_ids" text,
            "refseq_ids" text,
            "gene_family_tag" text,
            "gene_family_description" text,
            "record_type" varchar(50),
            "primary_ids" text,
            "secondary_ids" text,
            "ccds_ids" text,
            "vega_ids" text,
            "locus_specified_databases" text,
            "ncbi_entrez_gene_id" integer,
            "ncbi_omim_id" integer,
            "ncbi_refseq_id" varchar(50),
            "ncbi_uniprot_id" varchar(50),
            "ncbi_ensembl_id" varchar(50),
            "ncbi_ucsc_id" varchar(50),
            "ncbi_mgi_id" integer,
            "ncbi_rgd_id" integer
        )''',

        'hgncFamilies': '''CREATE TABLE {} (
            "tag" varchar(20) NOT NULL,
            "description" varchar(200) NOT NULL,
            "symbol" varchar(20) NOT NULL,
            "hgnc_id" int NOT NULL
        )'''
    }

    processors = {
        'hgnc': HGNCGeneParser,
        'hgncFamilies': HGNCGeneFamilyParser,
    }
