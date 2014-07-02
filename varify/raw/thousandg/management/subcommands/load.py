from varify.raw.management.subcommands.load import LoadCommand
from varify.raw.utils.stream import VCFPGCopyEditor
from varify.variants.utils import calculate_md5


class ThousandGProcessor(VCFPGCopyEditor):
    vcf_fields = ('CHROM', 'POS', 'REF', 'ALT', 'ID')

    info_fields = ('AN', 'AC', 'AF', 'AA', 'AMR_AF', 'ASN_AF', 'AFR_AF',
                   'EUR_AF')

    # Output column names to match position
    output_columns = ('chr', 'pos', 'ref', 'alt', 'rsid', 'an', 'ac', 'af',
                      'aa', 'amr_af', 'asn_af', 'afr_af', 'eur_af', 'md5')

    def process_line(self, record):
        cleaned = super(ThousandGProcessor, self).process_line(record)
        # Add the MD5
        cleaned.append(calculate_md5(*cleaned[:4]))
        return cleaned


class Command(LoadCommand):
    targets = ['1000g']

    qualified_names = {
        '1000g': '"raw"."1000g"',
    }

    create_sql = {
        '1000g': '''CREATE TABLE {} (
            "chr" text NOT NULL,
            "pos" integer NOT NULL,
            "ref" text NOT NULL,
            "alt" text NOT NULL,
            "md5" varchar(32) NOT NULL,
            "rsid" varchar(30),
            "an" integer,
            "ac" integer,
            "af" double precision,
            "aa" text,
            "amr_af" double precision,
            "asn_af" double precision,
            "afr_af" double precision,
            "eur_af" double precision
        )''',
    }

    processors = {
        '1000g': ThousandGProcessor,
    }
