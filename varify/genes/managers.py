from django.db import models, IntegrityError


class GeneManager(models.Manager):
    def find(self, symbol, chrom=None, create=False):
        """
        Find a gene based on the symbol or disambiguate using synonyms.
        If no gene is found, if the create is True, a new instance will be
        created with that symbol.
        """
        queryset = self.get_query_set()

        # Filter by chromosome if one is specified
        if chrom:
            queryset = queryset.filter(chr=chrom)

        # Look for direct match
        matches = queryset.filter(symbol__iexact=symbol)

        try:
            return matches[0]
        except IndexError:
            pass

        # Attempt to disambiguate, only if this is the only synonym may it be
        # associated
        potential = list(
            queryset.filter(synonyms__label__iexact=symbol).distinct())

        if len(potential) == 1:
            return potential[0]

        # Only if there are no matches should we create a new record,
        # otherwise the synonym war will continue
        if create and len(potential) == 0:
            instance = self.model(chr=chrom, symbol=symbol)
            try:
                instance.save()
            except IntegrityError:
                instance = queryset.get(chr=chrom, symbol=symbol)
            return instance
