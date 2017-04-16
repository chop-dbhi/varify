from avocado.export import registry
from ._vcf import VcfExporter

registry.register(VcfExporter, 'vcf')
