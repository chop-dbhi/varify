from avocado.query.translators import Translator, registry
from modeltree.tree import trees


class AllowNullsTranslator(Translator):
    """For data sources that only apply to SNPs, this translator ensures only
    SNPs are filtered down and not other types of variants.
    """
    def translate(self, field, roperator, rvalue, tree, **kwargs):
        output = super(AllowNullsTranslator, self).translate(
            field, roperator, rvalue, tree, **kwargs)

        # We are excluding nulls in the case of range, gt, and gte operators.
        # If we did not do this, then null values would be included all the
        # time which would be confusing, especially then they are included
        # for both lt and gt queries as it appears nulls are simultaneously
        # 0 and infinity.
        if roperator not in ('range', 'gt', 'gte'):
            # Create a null condition for this field
            null_condition = trees[tree].query_condition(
                field.field, 'isnull', True)
            # Allow the null condition
            output['query_modifiers']['condition'] |= null_condition

        return output


registry.register(AllowNullsTranslator, 'Allow Nulls')
