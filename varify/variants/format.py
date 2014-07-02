from avocado.columns.format import library, AbstractFormatter


class DbsnpUrlFormatter(AbstractFormatter):
    name = 'dbSNP URL'
    base_url = 'http://www.ncbi.nlm.nih.gov/projects/SNP/snp_ref.cgi?rs=%s'

    def html(self, dbsnp_id, **kwargs):
        return '<a href="%s">%s</a>' % (self.base_url % dbsnp_id, dbsnp_id)


class GeneUrlFormatter(AbstractFormatter):
    name = 'Gene URL'
    base_url = \
        'http://www.ncbi.nlm.nih.gov/sites/entrez?term=%s&cmd=search&db=gene'

    def html(self, gene, **kwargs):
        return '<a href="%s">%s</a>' % (self.base_url % gene, gene)


class HgmdUrlFormatter(AbstractFormatter):
    name = 'HGMD URL'
    base_url = 'http://www.ncbi.nlm.nih.gov/pubmed/?term=%s'

    def html(self, disease, hgmd_id, **kwargs):
        if hgmd_id:
            return '<a href="%s">%s</a>' % (self.base_url % hgmd_id, disease)
        return disease


class VariantPositionFormatter(AbstractFormatter):
    def html(self, start, end, **kwargs):
        if start == end or end:
            length = '+%s' % (end - start + 1)
            return u'%s <span class=help>%s</span>' % (start, length)
        return start


class AminoAcidChangeFormatter(AbstractFormatter):
    base_url = 'http://www.ncbi.nlm.nih.gov/nuccore/%s'

    def html(self, aachange, **kwargs):
        if aachange:
            nm, part = aachange.split(':', 1)
            return u'<a href="%s">%s</a> <span class=help>%s</span>' % \
                   (self.base_url % nm, nm, part)


class RatioFormatter(AbstractFormatter):
    def html(self, val, ratio, **kwargs):
        if ratio:
            return u'%d <span class=help>%s%%</span>' % (val, str(ratio))
        return val


class HelpTextFormatter(AbstractFormatter):
    def html(self, val, text, **kwargs):
        return u'%s <span class=help>%s</span>' % (val, text)


class PriorityScore(AbstractFormatter):
    def html(self, score, **kwargs):
        if score is not None:
            return u'{:.2%}'.format(score)


library.register(DbsnpUrlFormatter)
library.register(GeneUrlFormatter)
library.register(HgmdUrlFormatter)
library.register(VariantPositionFormatter)
library.register(AminoAcidChangeFormatter)
library.register(RatioFormatter)
library.register(HelpTextFormatter)
library.register(PriorityScore)
