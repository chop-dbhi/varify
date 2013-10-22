from django.db import models


class PubMed(models.Model):
    pmid = models.IntegerField(primary_key=True)

    class Meta(object):
        db_table = 'pubmed'

    @property
    def pmid_url(self):
        return 'http://www.ncbi.nlm.nih.gov/pubmed/' + str(self.pmid)
