from avocado.query.translators import Translator, registry
from modeltree.tree import trees


class AllowNullsTranslator(Translator):
    """For data sources that only apply to SNPs, this translator ensures only
    SNPs are filtered down and not other types of variants.
    """
    def translate(self, field, roperator, rvalue, tree, **kwargs):
        output = super(AllowNullsTranslator, self).translate(
            field, roperator, rvalue, tree, **kwargs)
        # Create a null condition for this field
        null_condition = trees[tree].query_condition(
            field.field, 'isnull', True)
        # Allow the null condition
        output['query_modifiers']['condition'] |= null_condition
        return output


registry.register(AllowNullsTranslator, 'Allow Nulls')
