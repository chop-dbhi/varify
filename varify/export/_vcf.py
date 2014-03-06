import logging
from datetime import datetime
from django.http import HttpResponse
import vcf
from restlib2.http import codes
from avocado.export._base import BaseExporter
from serrano.resources.base import get_request_context
from varify.samples.models import Cohort, CohortVariant, Result, Sample
from varify.assessments.models import Assessment
from django.conf import settings
import os

log = logging.getLogger(__name__)


class VcfExporter(BaseExporter):
    short_name = 'VCF'
    long_name = 'Variant Call Format'

    file_extension = 'vcf'
    content_type = 'text/variant-call-format'

    ci_categories = ['Definitive cause of phenotype',
                     'Possibly linked to clinical indication']
    # We include None in the list here because assessment category is nullable.
    if_categories = ['Immediately medically actionable', 'Childhood onset',
                     'Adult onset', 'Recessive carrier', None]

    pathogenicities = ['Unreviewed', 'Pathogenic', 'Likely pathogenic',
                       'Variant of unknown significance', 'Likely benign',
                       'Benign',
                       'Exclude for technical reasons related to sequencing']

    def write(self, iterable, buff=None, *args, **kwargs):
        header = []
        buff = self.get_file_obj(buff)
        template_path = os.path.join(settings.PROJECT_PATH, 'varify/templates/vcfexport.vcf');
        template_file = open(template_path, "r")
        template_reader = vcf.Reader(template_file)
        writer = vcf.Writer(buff, template_reader)
        template_file.close()
        for i, row_gen in enumerate(self.read(iterable, *args, **kwargs)):
            row = []
            for data in row_gen:
                if i == 0:
                    header.extend(data.keys())
                row.extend(data.values())
            if i == 0:
                writer.writerow(header)
            writer.writerow(row)
        return buff


