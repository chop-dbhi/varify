from varify.raw.management.subcommands.load import LoadCommand


class Command(LoadCommand):

    targets = ['genePhenotypes']

    qualified_names = {
        'genePhenotypes': '"raw"."hpo_gene_phenotypes"',
    }

    drop_sql = {
        'genePhenotypes': 'DROP TABLE IF EXISTS {}',
    }

    create_sql = {
        'genePhenotypes': '''CREATE TABLE {} (
            "entrez_gene_id" integer NOT NULL,
            "entrez_gene_symbol" varchar(20) NOT NULL,
            "hpo_terms" text NOT NULL
        )''',
    }
