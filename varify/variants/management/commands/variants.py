from varify.management.commands import Subcommander


class Command(Subcommander):
    app_name = 'variants'

    subcommands = {
        'load': 'load',
        'reload-snpeff': 'reload_snpeff',
    }
