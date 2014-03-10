from varify import export

def test_vcf(self):
        exporter = export.VCFExporter(self.concepts)
        buff = exporter.write(self.query)
        #TODO: insert validation of buffer here
        