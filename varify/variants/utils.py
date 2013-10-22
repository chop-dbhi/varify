import hashlib
from vcf.model import _Record

MD5_ARG_DELIMITER = '|'


def calculate_md5(*args):
    if len(args) == 1 and isinstance(args[0], _Record):
        r = args[0]
        values = [r.CHROM, r.POS, r.REF, ','.join([str(x) for x in r.ALT])]
    elif len(args) == 4:
        values = list(args)
    else:
        raise ValueError('Invalid arguments')
    for i, value in enumerate(values):
        # Position is an int, everything else a string
        if i == 1:
            assert isinstance(value, int) or value.isdigit()
            values[i] = str(value)
        else:
            assert isinstance(value, basestring)
    return hashlib.md5(MD5_ARG_DELIMITER.join(values)).hexdigest()
