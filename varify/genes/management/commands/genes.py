from varify.management.commands import Subcommander


class Command(Subcommander):
    app_name = 'genes'

    subcommands = {
        'load': 'load',
    }
