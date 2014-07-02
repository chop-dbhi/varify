from avocado.query.translators import Translator, registry
from modeltree.tree import trees


class AllowMissingRecord(Translator):
    """
    HGMD is the only source of data for the variant-phenotype assocations.
    This leads to a nuance in what it means to "not be in HGMD". By default,
    Avocado adds a second condition to ensure the ID is also not null if the
    field itself is nullable (to exclude missing records). However because
    records _only_ exist if there is an HGMD ID, this behavior is confusing.

    This translator overrides this behavior and adds an OR to allow for no
    records if querying for an explicit NULL.
    """
    def translate(self, field, roperator, rvalue, tree, **kwargs):
        output = super(AllowMissingRecord, self).translate(
            field, roperator, rvalue, tree, **kwargs)
        cleaned_data = output['cleaned_data']

        if (cleaned_data['operator'].lookup == 'isnull'
                and cleaned_data['value']):
            # Create a null condition for this field
            null_condition = trees[tree].query_condition(
                field.model._meta.pk, 'isnull', True)
            # Allow the null condition
            output['query_modifiers']['condition'] = null_condition
        return output


registry.register(AllowMissingRecord, 'Allow Missing Record')
