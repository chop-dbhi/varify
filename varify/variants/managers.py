from django.db.models import Manager


class VariantManager(Manager):
    def get_by_natural_key(self, chr, pos, ref, alt):
        return self.get(chr=chr, pos=pos, ref=ref, alt=alt)
