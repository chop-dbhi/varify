from varify.management.commands import Subcommander


class Command(Subcommander):
    app_name = 'phenotypes'

    subcommands = {
        'load': 'load',
    }
