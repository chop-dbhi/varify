import vcf
import logging

log = logging.getLogger(__name__)


class StreamEditor(object):
    indices = None

    output_columns = None

    def __init__(self, fin, indices=None, indel='\t', outdel=None,
                 encoding='utf-8'):
        self.fin = fin

        # Input delimiter, output delimiter, default to the same output
        # delimiter if none is defined.
        self.indel = indel
        if outdel is None:
            outdel = indel
        self.outdel = outdel

        # The first iteration will populate the indices if not defined
        self.indices = indices or self.indices

        # Encoding of the input file
        self.encoding = encoding

    def process_column(self, idx, value):
        "Process a single column."
        if value is not None:
            value = str(value).decode(self.encoding)
        return value

    def process_line(self, line):
        "Process a single complete line."
        cleaned = []
        columns = line.split(self.indel)
        # Populate indices if not defined
        if not self.indices:
            self.indices = range(len(columns))
        for i in self.indices:
            # Support turning an in col into multiple out cols
            out = self.process_column(i, columns[i])
            if isinstance(out, (list, tuple)):
                cleaned.extend(out)
            else:
                cleaned.append(out)
        return self.outdel.join(cleaned) + '\n'

    def read(self, size=-1):
        "Reads up to size bytes, but always completes the last line."
        buf = self.fin.read(size)
        if not buf:
            return ''
        lines = buf.splitlines()
        # Read the rest of the last line if necessary
        if not buf.endswith('\n'):
            last = lines.pop()
            partial = self.fin.readline()
            lines.append(last + partial)
        # Process the lines, concatenate them
        lines = [self.process_line(line.rstrip('\n')) for line in lines]
        return ''.join(lines)

    def readline(self, size=-1):
        "The size is ignored since a complete line must be read."
        line = self.fin.readline()
        if not line:
            return ''
        return self.process_line(line.rstrip('\n'))


NULL_VALUES = ('.', '', 'null', 'NA', 'N/A', 'NONE')


class VCFStreamEditor(StreamEditor):
    vcf_fields = []

    info_fields = []

    def __init__(self, *args, **kwargs):
        super(VCFStreamEditor, self).__init__(*args, **kwargs)
        self.reader = vcf.VCFReader(self.fin)

    def _clean_value(self, value):
        if isinstance(value, (tuple, list)):
            return ','.join([str(x) for x in value if x is not None])
        if value is not None:
            value = str(value)
            if value in NULL_VALUES:
                value = None
        return value

    def process_column(self, key, value):
        value = self._clean_value(value)
        return super(VCFStreamEditor, self).process_column(key, value)

    def process_line(self, record):
        "Process a single record. This assumes only a single sample output."
        cleaned = []

        for key in self.vcf_fields:
            out = self.process_column(key, getattr(record, key))
            if isinstance(out, (list, tuple)):
                cleaned.extend(out)
            else:
                cleaned.append(out)

        for key in self.info_fields:
            out = self.process_column(key, record.INFO.get(key, None))
            if isinstance(out, (list, tuple)):
                cleaned.extend(out)
            else:
                cleaned.append(out)

        return cleaned

    def read(self, size=-1):
        """Read `size` bytes from the reader relative to the parsed output.
        This is generally acceptable in practice since VCF lines are
        condensed, but if the output line <<< record, this means the actual
        memory used will be much greater than `size`.
        """
        lines = []
        parsed_size = 0

        while True:
            line = self.readline()
            if not line:
                break
            lines.append(line)
            parsed_size += len(line)
            if size and size > 0 and parsed_size >= size:
                break

        return ''.join(lines)

    def readline(self, size=-1):
        "Ignore the `size` since a complete line must be processed."
        try:
            record = next(self.reader)
            return self.outdel.join(self.process_line(record)) + '\n'
        except StopIteration:
            return ''


class PGCopyEditor(StreamEditor):
    """Ensures NoneTypes are represented as the standard \N string and tabs
    are used as the default delimiter for the output.
    """
    def __init__(self, *args, **kwargs):
        super(PGCopyEditor, self).__init__(*args, **kwargs)
        self.null = kwargs.get('null', '\\N')

    def process_column(self, idx, value):
        value = super(PGCopyEditor, self).process_column(idx, value)
        if value is None:
            value = self.null
        return value


class VCFPGCopyEditor(VCFStreamEditor):
    def __init__(self, *args, **kwargs):
        super(VCFPGCopyEditor, self).__init__(*args, **kwargs)
        self.null = kwargs.get('null', '\\N')

    def process_column(self, key, value):
        value = super(VCFPGCopyEditor, self).process_column(key, value)
        if value is None:
            value = self.null
        return value
