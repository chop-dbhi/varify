import hashlib
from varify.raw.management.subcommands.load import LoadCommand
from varify.raw.utils.stream import PGCopyEditor


class SIFTProcessor(PGCopyEditor):
    def __init__(self, *args, **kwargs):
        kwargs['indices'] = (0, 1, 3, 4, 5, 6, 7)
        super(SIFTProcessor, self).__init__(*args, **kwargs)

    def process_column(self, idx, value):
        # Incrementally build up the tokens for calculating the MD5
        if idx == 0:
            self.md5_toks = [value]
        if idx in (1, 3):
            self.md5_toks.append(value)
        if idx == 4:
            self.md5_toks.append(value)
            return [value, hashlib.md5('|'.join(self.md5_toks)).hexdigest()]
        return super(SIFTProcessor, self).process_column(idx, value)


class Command(LoadCommand):
    targets = ['sift']

    qualified_names = {
        'sift': '"raw"."sift"',
    }

    drop_sql = {
        'sift': 'DROP TABLE IF EXISTS {}',
    }

    create_sql = {
        'sift': '''CREATE TABLE {} (
            "chr" text NOT NULL,
            "pos" integer NOT NULL,
            "ref" text NOT NULL,
            "alt" text NOT NULL,
            "md5" varchar(32) NOT NULL,
            "score" double precision,
            "refaa" varchar(2),
            "varaa" varchar(2)
        )''',
    }

    processors = {
        'sift': SIFTProcessor,
    }
