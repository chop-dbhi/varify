import re
from varify.raw.management.subcommands.load import LoadCommand
from varify.raw.utils.stream import PGCopyEditor

ccds_exon_id_re = re.compile(r'([\w\d]+\.\d+)_exon_(\d+).*')


class CCDSExonsParser(PGCopyEditor):
    def process_column(self, idx, value):
        # parse CCDS ID and exon number
        if idx == 3:
            return ccds_exon_id_re.search(value).groups()
        return super(CCDSExonsParser, self).process_column(idx, value)


class Command(LoadCommand):

    targets = ['knownGene', 'kgAlias', 'refGene', 'ccdsKgMap', 'ccdsExons',
               'knownToRefSeq']

    qualified_names = {
        'knownGene': '"raw"."ucsc_known_gene"',
        'kgAlias': '"raw"."ucsc_kg_alias"',
        'refGene': '"raw"."ucsc_ref_gene"',
        'ccdsKgMap': '"raw"."ucsc_ccds_kg_map"',
        'ccdsExons': '"raw"."ucsc_ccds_exons"',
        'knownToRefSeq': '"raw"."ucsc_known_to_refseq"',
    }

    drop_sql = {
        'knownGene': 'DROP TABLE IF EXISTS {}',
        'kgAlias': 'DROP TABLE IF EXISTS {}',
        'refGene': 'DROP TABLE IF EXISTS {}',
        'ccdsKgMap': 'DROP TABLE IF EXISTS {}',
        'ccdsExons': 'DROP TABLE IF EXISTS {}',
        'knownToRefSeq': 'DROP TABLE IF EXISTS {}',
    }

    create_sql = {
        'knownGene': '''CREATE TABLE {} (
            "name" varchar(255),
            "chrom" varchar(255),
            "strand" char(1),
            "tx_start" integer,
            "tx_end" integer,
            "cds_start" integer,
            "cds_end" integer,
            "exon_count" integer,
            "exon_starts" text,
            "exon_ends" text,
            "protein_id" varchar(40),
            "align_id" varchar(255)
        )''',

        'kgAlias': '''CREATE TABLE {} (
            "kg_id" varchar(40),
            "alias" varchar(80)
        )''',

        'refGene': '''CREATE TABLE {} (
            "bin" integer,
            "name" varchar(255),
            "chrom" varchar(255),
            "strand" char(1),
            "tx_start" integer,
            "tx_end" integer,
            "cds_start" integer,
            "cds_end" integer,
            "exon_count" integer,
            "exon_starts" text,
            "exon_ends" text,
            "score" integer,
            "name2" varchar(255),
            "cds_start_stat" varchar(10),
            "cds_end_stat" varchar(10),
            "exon_frames" text
        )''',

        'ccdsKgMap': '''CREATE TABLE {} (
            "ccds_id" varchar(32) NOT NULL,
            "gene_id" varchar(255) NOT NULL,
            "chrom" varchar(255) NOT NULL,
            "chrom_start" integer NOT NULL,
            "chrom_end" integer NOT NULL,
            "cds_similarity" float NOT NULL
        )''',

        'ccdsExons': '''CREATE TABLE {} (
            "chrom" varchar(255) NOT NULL,
            "start" int NOT NULL,
            "end" int NOT NULL,
            "ccds_id" varchar(255) NOT NULL,
            "exon_id" int NOT NULL,
            "score" int NOT NULL,
            "strand" varchar(1) NOT NULL
        )''',

        'knownToRefSeq': '''CREATE TABLE {} (
            "name" varchar(255) NOT NULL,
            "value" varchar(255) NOT NULL
        )''',
    }

    help = '\n'.join([
        'Performs the various load steps for various UCSC tables including:',
        '- knownGene [1]',
        '- kgAlias [2]',
        '- refGene [3]',
        '- ccdsKgMap [4]',
        '- exons [5]',
        '- knownToRefSeq [6]',
        '',
        'Available targets include: {0}'.format(', '.join(targets)),
        '',
        '[1]: http://genome.ucsc.edu/cgi-bin/hgTables?hgta_doSchemaDb=hg19&hgta_doSchemaTable=knownGene',   # noqa
        '[2]: http://genome.ucsc.edu/cgi-bin/hgTables?hgta_doSchemaDb=hg19&hgta_doSchemaTable=kgAlias',   # noqa
        '[3]: http://genome.ucsc.edu/cgi-bin/hgTables?hgta_doSchemaDb=hg19&hgta_doSchemaTable=refGene',   # noqa
        '[4]: http://genome.ucsc.edu/cgi-bin/hgTables?hgta_doSchemaDb=hg19&hgta_doSchemaTable=ccdsKgMap',   # noqa
        '[5]: File on variome.. /nas/is1/MFalk/framework/ccds_hg19_exons.bed',
        '[6]: http://genome.ucsc.edu/cgi-bin/hgTables?hgta_doSchemaDb=hg19&hgta_doSchemaTable=knownToRefSeq',   # noqa
    ])

    processors = {
        'ccdsExons': CCDSExonsParser,
    }
