import json
import logging
import requests
from datetime import datetime
from django.conf import settings
from optparse import make_option
from django.db import transaction, DEFAULT_DB_ALIAS
from django.core.management.base import BaseCommand
from requests.exceptions import SSLError, ConnectionError, RequestException
from varify.samples.models import Sample

log = logging.getLogger(__name__)


class Command(BaseCommand):
    args = '<sample_label sample_label ...>'
    option_list = BaseCommand.option_list + (
        make_option('--database', action='store', dest='database',
                    default=DEFAULT_DB_ALIAS,
                    help='Specifies the target database to load results.'),
        make_option('--force', action='store_true', dest='force',
                    default=False,
                    help='Forces recomputation of all gene rankings')
    )

    def handle(self, *args, **options):
        if not settings.PHENOTYPE_ENDPOINT:
            log.error('PHENOTYPE_ENDPOINT must be defined in settings for '
                      'gene rankings to be updated.')
            return

        if not settings.GENE_RANK_BASE_URL:
            log.error('GENE_RANK_BASE_URL must be defined in settings for '
                      'gene rankings to be updated.')
            return

        if not settings.VARIFY_CERT or not settings.VARIFY_KEY:
            log.error('VARIFY_CERT and VARIFY_KEY must be defined in settings '
                      'for gene rankings to be updated.')
            return

        database = options.get('database')
        force = options.get('force')

        # Construct the cert from the setting to use in requests to the
        # phenotype endpoint.
        cert = (settings.VARIFY_CERT, settings.VARIFY_KEY)

        # We ignore all the samples that aren't published. They aren't visible
        # to the user so we don't bother updating related scores. If there
        # were sample labels supplied as arguments then we limit the rankings
        # updates to those samples, otherwise we process all samples.
        samples = Sample.objects.filter(published=True)

        if args:
            samples = samples.filter(label__in=args)

        updated_samples = 0
        total_samples = 0
        for sample in samples:
            total_samples += 1

            # Construct the URL from the setting and the sample label. The
            # sample label is used to retrieve the phenotype info on the remote
            # endpoint.
            url = settings.PHENOTYPE_ENDPOINT % sample.label

            # Get the phenotype information for this sample. If the
            # phenotype is unavailable then we can skip this sample.
            try:
                response = requests.get(url, cert=cert, verify=False)
            except SSLError:
                log.exception('Skipping sample "{0}". An SSLError occurred '
                              'during phenotype retrieval request.'
                              .format(sample.label))
                continue
            except ConnectionError:
                log.exception('Skipping sample "{0}". A ConnectionError '
                              'occurred during phenotype retrieval request.'
                              .format(sample.label))
                continue
            except RequestException:
                log.exception('Skipping sample "{0}". The sample has no '
                              'phenotype data associated with it'
                              .format(sample.label))
                continue

            try:
                phenotype_data = json.loads(response.content)
            except ValueError:
                log.error("Could not parse response from {0}, skipping '{1}'."
                          .format(url, sample.label))
                continue

            try:
                phenotype_modified = datetime.strptime(
                    phenotype_data['last_modified'], "%Y-%m-%dT%H:%M:%S.%f")
            except ValueError:
                phenotype_modified = datetime.min
                log.warn("Could not parse 'last_modified' field on phenotype "
                         "data. Using datetime.min so that only unranked "
                         "samples will be ranked. If the 'force' flag was "
                         "used then all samples will be updated despite this "
                         "parsing failure.")

            # If the parsed response doesn't contain any HPO terms then we can
            # skip this sample since we cannot rank genes without HPO terms.
            if not phenotype_data.get('hpoAnnotations', []):
                log.error("Response from phenotype missing HPO Annotations, "
                          "skipping '{0}'.".format(sample.label))
                continue

            if (not force and sample.phenotype_modified and
                    sample.phenotype_modified < phenotype_modified):
                log.debug("Sample '{0}' is already up to date, skipping it."
                          .format(sample.label))
                continue

            # Extract the HPO terms from the data returned from the phenotype
            # endpoint. We need to modify the terms a bit because the phenotype
            # endpoint has terms in the form 'HP_0011263' and the gene ranking
            # enpoint expects them to be of the form 'HP:0011263'.
            hpo_terms = []
            for hpo_annotation in phenotype_data['hpoAnnotations']:
                hpo_id = str(hpo_annotation.get('hpo_id', ''))

                if hpo_id:
                    hpo_terms.append(hpo_id.replace('_', ':'))

            # If there are no HPO terms then there will be no rankings so skip
            # this sample to avoid any more computations and requests.
            if not hpo_terms:
                log.warning('Skipping "{0}" because it has no HPO terms '
                            'associated with it.'.format(sample.label))
                continue

            # Compute the unique gene list for the entire sample
            genes = set(sample.results.values_list(
                'variant__effects__transcript__gene__symbol', flat=True))

            # Obviously, if there are no genes then the gene ranking endpoint
            # will have nothing to do so we can safely skip this sample.
            if not genes:
                continue

            # We need to convert the genes to strings because the ranking
            # service is no prepared to handle the unicode format that the
            # gene symbols are in when we retrieve them from the models.
            gene_rank_url = "http://{0}?hpo={1}&genes={2}".format(
                settings.GENE_RANK_BASE_URL, ",".join(hpo_terms),
                ",".join([str(g) for g in genes]))

            try:
                gene_response = requests.get(gene_rank_url)
            except Exception:
                log.exception('Error retrieving gene rankings')
                continue

            gene_data = json.loads(gene_response.content)
            ranked_genes = gene_data['ranked_genes']

            # While all the results should have been updated at the
            # same time, we cannot guarantee that so we check if each
            # is stale or the force flag is on before updating the
            # results gene rank.
            updated_results = 0
            total_results = 0
            for result in sample.results.all():
                total_results += 1

                with transaction.commit_manually(database):
                    try:
                        # Get the gene for this result. Since a result can
                        # have more than one gene associated with it, we
                        # return the first gene symbol in the list. This is
                        # the same one that will be shown in the collapsed
                        # gene list on the variant row in the results table.
                        gene = result.variant.effects.values_list(
                            'transcript__gene__symbol', flat=True)[0]

                        # If there is no gene on this result or the gene is
                        # not found in the list of ranked genes then skip this
                        # result.
                        if not gene:
                            log.debug("Result with id {0} has no gene, "
                                      "skipping result.".format(result.id))
                            transaction.rollback()
                            continue

                        # Get the first item in the ranked gene list with a
                        # symbol matching the gene we looked up above for this
                        # result.
                        ranked_gene = next(
                            (r for r in ranked_genes if
                             r.get('symbol', '').lower() == gene.lower()),
                            None)

                        if not ranked_gene:
                            log.debug("Could not find '{0}' in ranked gene "
                                      "list, skipping result".format(gene))
                            transaction.rollback()
                            continue

                        result.score.rank = ranked_gene.get('rank', None)
                        result.score.score = ranked_gene.get('score', None)
                        result.save()

                        updated_results += 1

                    except Exception:
                        log.exception("Error saving gene ranks and scores for "
                                      "sample '{0}'".format(sample.label))
                        transaction.rollback()

                    transaction.commit()

            sample.phenotype_modified = datetime.now()
            sample.save()

            log.info("Updated {0} and skipped {1} results in sample '{2}'"
                     .format(updated_results, total_results - updated_results,
                             sample.label))
            updated_samples += 1

        log.info("Updated {0} and skipped {1} samples"
                 .format(updated_samples, total_samples-updated_samples))
