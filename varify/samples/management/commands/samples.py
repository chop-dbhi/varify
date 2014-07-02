from varify.management.commands import Subcommander


class Command(Subcommander):
    app_name = 'samples'

    subcommands = {
        'allele-freqs': 'allele_freqs',
        'gene-ranks': 'gene_ranks',
        'queue': 'queue',
        'delete-sample': 'delete_sample',
        'delete-project': 'delete_project',
    }
