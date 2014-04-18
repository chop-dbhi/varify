import hashlib


def record_is_valid(record):
    "Checks if a record is valid for processing."

    # No random contigs
    if record.CHROM.startswith('GL'):
        return False

    # Skip results with a read depth < 5. If no read depth is specified then
    # we have no choice but to consider this record as being valid.
    if 'DP' in record.INFO and record.INFO['DP'] < 5:
        return False

    return True


def file_md5(filename, block_size=2**16):
    md5 = hashlib.md5()
    with open(filename, 'rb') as fin:
        while True:
            data = fin.read(block_size)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()
