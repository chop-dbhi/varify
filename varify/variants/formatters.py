try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
from avocado.formatters import registry as formatters
from serrano.formatters import HTMLFormatter


class GenomicCoordinate(HTMLFormatter):
    href = 'http://genome.ucsc.edu/cgi-bin/hgTracks?position=chr{chr}%3A{pos}'

    def to_html(self, values, **context):
        href = self.href.format(**values)
        return '<a target=_blank href="{href}">chr{chr}:{pos:,}</a>'.format(
            href=href, **values)
    to_html.process_multiple = True


class dbSNP(HTMLFormatter):
    href = 'http://www.ncbi.nlm.nih.gov/projects/SNP/snp_ref.cgi?rs={0}'

    def to_html(self, rsid, **context):
        if rsid:
            href = self.href.format(rsid[2:])
            return '<a target=_blank href="{href}">{rsid}</a>'.format(
                href=href, rsid=rsid)

    def to_excel(self, rsid, **context):
        if rsid:
            href = self.href.format(rsid[2:])
            return '=HYPERLINK("{href}", "{label}")'.format(
                href=href, label=rsid)
        return ''


class VariantEffect(HTMLFormatter):
    def to_html(self, values, **context):
        return '{0} <span class=muted>({1})</span>'.format(*values.values())

    to_html.process_multiple = True


class AlleleFrequency(HTMLFormatter):
    "To be used with EVS and 1000G"
    def to_html(self, values, **context):
        toks = []
        for key, value in values.items():
            if value in self.html_map:
                tok = self.html_map[value]
            else:
                tok = str(value * 100) + '%'

            if key.lower() == 'af':
                key = 'all'
            else:
                # Most of the key names are foo_af, this is imply trimming
                # off the _af
                key = key.split('_')[0]

            toks.append('<li><small>{0}</small> {1}</li>'.format(
                key.title(), tok))
        return '<ul class=unstyled>{0}</ul>'.format(''.join(toks))

    to_html.process_multiple = True


class SiftFormatter(HTMLFormatter):
    alt_keys = ('Sift Score', 'Sift Prediction')

    def _get_values(self, value):
        from vdw.variants.models import Sift
        return value, Sift.get_prediction(value)

    def to_html(self, value, **context):
        if value is None:
            return self.html_map[value]
        score, prediction = self._get_values(value)
        return '{0} <span class=muted>({1})</span>'.format(prediction, score)

    def to_excel(self, value, **context):
        score, prediction = self._get_values(value)
        return OrderedDict(zip(self.alt_keys, [score, prediction]))

    to_csv = to_excel


class PolyPhen2Formatter(HTMLFormatter):
    alt_keys = ('PolyPhen2 Score', 'PolyPhen2 Prediction')

    def _get_values(self, value):
        from vdw.variants.models import PolyPhen2
        return value, PolyPhen2.get_prediction(value)

    def to_html(self, value, **context):
        if value is None:
            return self.html_map[value]
        score, prediction = self._get_values(value)
        return '{0} <span class=muted>({1})</span>'.format(prediction, score)

    def to_excel(self, value, **context):
        score, prediction = self._get_values(value)
        return OrderedDict(zip(self.alt_keys, [score, prediction]))

    to_csv = to_excel


formatters.register(GenomicCoordinate, 'Genomic Coordinate')
formatters.register(dbSNP, 'dbSNP')
formatters.register(VariantEffect, 'Variant Effect')
formatters.register(AlleleFrequency, 'Allele Frequency')
formatters.register(SiftFormatter, 'Sift')
formatters.register(PolyPhen2Formatter, 'PolyPhen2')
