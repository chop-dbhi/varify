from varify.raw.management.subcommands.load import LoadCommand
from varify.raw.utils.stream import VCFPGCopyEditor
from varify.variants.utils import calculate_md5


class EVSProcessor(VCFPGCopyEditor):
    output_columns = ('chr', 'pos', 'ref', 'alt', 'rsid', 'ea_ac_alt',
                      'ea_ac_ref', 'aa_ac_alt', 'aa_ac_ref', 'all_ac_alt',
                      'all_ac_ref', 'ea_maf', 'aa_maf', 'all_maf', 'gts',
                      'ea_gtc', 'aa_gtc', 'all_gtc', 'read_depth',
                      'clinical_association', 'md5')

    vcf_fields = ('CHROM', 'POS', 'REF', 'ALT', 'ID')

    info_fields = ('EA_AC', 'AA_AC', 'TAC', 'MAF', 'GTS', 'EA_GTC', 'AA_GTC',
                   'GTC', 'DP', 'CA')

    def process_column(self, key, value):
        # *AC => allele counts. The format is "alt,ref"
        if key in ('EA_AC', 'AA_AC', 'TAC'):
            value = value.split(',')
            value = [','.join(value[:-1]), value[-1]]
            return value
        # MAF => allele frequencies. The format is 'EA,AA,All'
        if key == 'MAF':
            return value.split(',')
        return super(EVSProcessor, self).process_column(key, value)

    def process_line(self, record):
        cleaned = super(EVSProcessor, self).process_line(record)
        # Add the MD5
        cleaned.append(calculate_md5(*cleaned[:4]))
        return cleaned


class Command(LoadCommand):
    """Loader for raw EVS data.

    Website: http://evs.gs.washington.edu/EVS/
    """
    targets = ['evs']

    qualified_names = {
        'evs': '"raw"."evs"',
    }

    create_sql = {
        'evs': '''CREATE TABLE {} (
            "chr" text NOT NULL,
            "pos" integer NOT NULL,
            "alt" text NOT NULL,
            "ref" text NOT NULL,
            "md5" varchar(32) NOT NULL,
            "rsid" varchar(30),
            "ea_ac_ref" varchar(20),
            "ea_ac_alt" varchar(20),
            "aa_ac_ref" varchar(20),
            "aa_ac_alt" varchar(20),
            "all_ac_ref" varchar(20),
            "all_ac_alt" varchar(20),
            "ea_maf" double precision,
            "aa_maf" double precision,
            "all_maf" double precision,
            "gts" varchar(200),
            "ea_gtc" varchar(200),
            "aa_gtc" varchar(200),
            "all_gtc" varchar(200),
            "read_depth" integer,
            "clinical_association" text
        )''',
    }

    processors = {
        'evs': EVSProcessor,
    }
