import logging
import tempfile
from cStringIO import StringIO
from django.db import transaction

log = logging.getLogger(__name__)

DEFAULT_BATCH_SIZE = 1000


def writetmp(stream):
    tmp = tempfile.NamedTemporaryFile()
    while True:
        buff = stream.read(2 ** 16)
        if not buff:
            break
        tmp.write(buff)

    # Flush to disk.. seek to top for COPY
    tmp.flush()
    tmp.seek(0)
    return tmp


def pgcopy(stream, db_table, columns, cursor, database):
    with transaction.commit_on_success(database):
        try:
            cursor.copy_from(stream, db_table, columns=columns)
        except Exception as e:
            log.exception(e)
            raise


def batch_stream(buff, stream, size=DEFAULT_BATCH_SIZE):
    """Writes a batch of `size` lines to `buff`.

    Returns boolean of whether the stream has been exhausted.
    """
    buff.truncate(0)
    for _ in xrange(size):
        if hasattr(stream, 'readline'):
            line = stream.readline()
        else:
            try:
                line = next(stream)
            except StopIteration:
                line = ''

        # No more lines, return the tmp
        if line == '':
            buff.seek(0)
            return True
        buff.write(line)
    buff.seek(0)
    return False


def pgcopy_batch(stream, db_table, columns, cursor, database,
                 batch_size=DEFAULT_BATCH_SIZE):
    buff = StringIO()
    try:
        while True:
            empty = batch_stream(buff, stream, batch_size)
            pgcopy(buff, db_table, columns, cursor, database)
            if empty:
                break
    finally:
        buff.close()
