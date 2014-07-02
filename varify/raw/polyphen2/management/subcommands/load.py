import hashlib
from varify.raw.management.subcommands.load import LoadCommand
from varify.raw.utils.stream import PGCopyEditor


class PolyPhen2Processor(PGCopyEditor):
    def __init__(self, *args, **kwargs):
        kwargs['indices'] = (0, 1, 3, 4, 5, 6)
        super(PolyPhen2Processor, self).__init__(*args, **kwargs)

    def process_column(self, idx, value):
        # Incrementally build up the tokens for calculating the MD5
        if idx == 0:
            self.md5_toks = [value]
        if idx in (1, 3):
            self.md5_toks.append(value)
        if idx == 4:
            self.md5_toks.append(value)
            return [value, hashlib.md5('|'.join(self.md5_toks)).hexdigest()]
        return super(PolyPhen2Processor, self).process_column(idx, value)


class Command(LoadCommand):
    targets = ['polyphen2']

    qualified_names = {
        'polyphen2': '"raw"."polyphen2"',
    }

    drop_sql = {
        'polyphen2': 'DROP TABLE IF EXISTS {}',
    }

    create_sql = {
        'polyphen2': '''CREATE TABLE {} (
            "chr" text NOT NULL,
            "pos" integer NOT NULL,
            "ref" text NOT NULL,
            "alt" text NOT NULL,
            "md5" varchar(32) NOT NULL,
            "score" double precision,
            "refaa" varchar(2)
        )''',
    }

    processors = {
        'polyphen2': PolyPhen2Processor,
    }
