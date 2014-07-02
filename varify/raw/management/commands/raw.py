from varify.management.commands import Subcommander


class Command(Subcommander):
    app_name = 'raw'

    subcommands = {
        'evs': 'evs',
        'hgnc': 'hgnc',
        'polyphen2': 'polyphen2',
        'sift': 'sift',
        '1000g': 'thousandg',
        'ucsc': 'ucsc',
        'hpo': 'hpo',
    }

    import_template = 'varify.{app}.{module}.management.subcommands.load'
