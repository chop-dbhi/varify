from varify.management.commands import Subcommander


class Command(Subcommander):
    app_name = 'samples'

    subcommands = {
        'load': 'load',
        'allele-freqs': 'allele_freqs',
        'queue': 'queue',
        'delete-sample': 'delete_sample',
        'delete-project': 'delete_project',
    }
