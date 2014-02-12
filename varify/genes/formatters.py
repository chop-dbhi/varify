from avocado.formatters import registry as formatters
from varify.formatters import HTMLFormatter


class HGNCGene(HTMLFormatter):
    href = 'http://www.genenames.org/data/hgnc_data.php?hgnc_id={}'

    def to_html(self, values, **context):
        if values['hgnc_id']:
            href = self.href.format(values['hgnc_id'])
            return '<a target=_blank href="{href}">{label}</a>'.format(
                href=href, label=values['symbol'])
        return values['symbol']
    to_html.process_multiple = True

    def to_excel(self, values, **context):
        if values['hgnc_id']:
            href = self.href.format(values['hgnc_id'])
            return '=HYPERLINK("{href}", "{label}")'.format(
                href=href, label=values['symbol'])
        return values['symbol']
    to_excel.process_multiple = True


class NCBIGene(HGNCGene):
    href = \
        'http://www.ncbi.nlm.nih.gov/sites/entrez?term={}&cmd=search&db=gene'

    def to_html(self, values, **context):
        if values['symbol']:
            href = self.href.format(values['symbol'])
            return '<a target=_blank href="{href}">{label}</a>'.format(
                href=href, label=values['symbol'])
    to_html.process_multiple = True

    def to_excel(self, values, **context):
        if values['symbol']:
            href = self.href.format(values['symbol'])
            return '=HYPERLINK("{href}", "{label}")'.format(
                href=href, label=values['symbol'])
    to_excel.process_multiple = True


class RefSeqTranscript(HTMLFormatter):
    href = 'http://www.ncbi.nlm.nih.gov/nuccore/{}'

    def to_html(self, value, **context):
        if value:
            href = self.href.format(value)
            return '<a target=_blank href="{href}">{label}</a>'.format(
                href=href, label=value)

    def to_excel(self, value, **context):
        if value:
            href = self.href.format(value)
            return '=HYPERLINK("{href}", "{label}")'.format(
                href=href, label=value)


formatters.register(HGNCGene, 'HGNC Gene')
formatters.register(NCBIGene, 'NCBI Gene')
formatters.register(RefSeqTranscript, 'RefSeq Transcript')
