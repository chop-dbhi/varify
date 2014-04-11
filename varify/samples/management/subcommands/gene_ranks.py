import json
import logging
import requests
from datetime import datetime
from django.conf import settings
from optparse import make_option
from django.db import transaction, DEFAULT_DB_ALIAS
from django.core.management.base import BaseCommand
from requests.exceptions import SSLError, ConnectionError, RequestException
from varify.samples.models import Sample, ResultScore

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
        if not getattr(settings, 'PHENOTYPE_ENDPOINT', None):
            log.error('PHENOTYPE_ENDPOINT must be defined in settings for '
                      'gene rankings to be updated.')
            return

        if not getattr(settings, 'GENE_RANK_BASE_URL', None):
            log.error('GENE_RANK_BASE_URL must be defined in settings for '
                      'gene rankings to be updated.')
            return

        if (not getattr(settings, 'VARIFY_CERT', None) or
                not getattr(settings, 'VARIFY_KEY', None)):
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
            url = settings.PHENOTYPE_ENDPOINT.format(sample.label)

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
                log.warning(
                    "Could not parse response from {0}, skipping '{1}'."
                    .format(url, sample.label))
                continue

            try:
                phenotype_modified = datetime.strptime(
                    phenotype_data['last_modified'] or '',
                    "%Y-%m-%dT%H:%M:%S.%f")
            except ValueError:
                phenotype_modified = datetime.min
                log.warn("Could not parse 'last_modified' field on phenotype "
                         "data. Using datetime.min so that only unranked "
                         "samples will be ranked. If the 'force' flag was "
                         "used then all samples will be updated despite this "
                         "parsing failure.")

            # If the parsed response doesn't contain any HPO terms then we can
            # skip this sample since we cannot rank genes without HPO terms.
            if not phenotype_data.get('hpoAnnotations'):
                log.warning("Response from phenotype missing HPO Annotations, "
                            "skipping '{0}'.".format(sample.label))
                continue

            if (not force and sample.phenotype_modified and
                    sample.phenotype_modified > phenotype_modified):
                log.debug("Sample '{0}' is already up to date, skipping it."
                          .format(sample.label))
                continue

            # Extract the HPO terms from the data returned from the phenotype
            # endpoint. We need to modify the terms a bit because the phenotype
            # endpoint has terms in the form 'HP_0011263' and the gene ranking
            # enpoint expects them to be of the form 'HP:0011263'.
            hpo_terms = []
            for hpo_annotation in phenotype_data['hpoAnnotations']:
                try:
                    hpo_id = hpo_annotation.get('hpo_id')
                except AttributeError:
                    continue

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
                log.warning('Skipping "{0}" because it has no genes '
                            'associated with it.'.format(sample.label))
                continue

            # Convert genes to a list so it is serializeable in the json.dumps
            # call below when making the request to the ranking service.
            data = {
                'hpo': hpo_terms,
                'genes': [g for g in genes if g]
            }

            try:
                gene_response = requests.post(
                    settings.GENE_RANK_BASE_URL, data=json.dumps(data),
                    headers={'content-type': 'application/json'})
            except Exception:
                log.exception('Error retrieving gene rankings, skipping '
                              'sample "{0}".'.format(sample.label))
                continue

            try:
                gene_data = json.loads(gene_response.content)
            except ValueError:
                log.warning(
                    "Could not parse response from {0}, skipping '{1}'."
                    .format(settings.GENE_RANK_BASE_URL, sample.label))
                continue

            ranked_genes = gene_data['ranked_genes']

            updated_results = 0
            total_results = 0

            for result in sample.results.all():
                total_results += 1

                with transaction.commit_manually(database):
                    try:
                        # Instead of trying to remove None from the returned
                        # values list we just exclude them from the query
                        # itself.
                        genes = result.variant.effects\
                            .exclude(transcript__gene__symbol__isnull=True)\
                            .order_by('effect__impact')\
                            .values_list(
                                'transcript__gene__symbol', flat=True)\
                            .distinct()

                        # If there is no gene on this result or the gene is
                        # not found in the list of ranked genes then skip this
                        # result.
                        if not genes:
                            log.debug("Result with id {0} has no gene, "
                                      "skipping result.".format(result.id))
                            transaction.rollback()
                            continue

                        # Use the first gene from the list since a result can
                        # have more than one gene associated with it, we
                        # return the first gene symbol in the list. This is
                        # the same one that will be shown in the collapsed
                        # gene list on the variant row in the results table.
                        gene = genes[0]

                        # Get the first item in the ranked gene list with a
                        # symbol matching the gene we looked up above for this
                        # result.
                        ranked_gene = None

                        for ranked_gene in ranked_genes:
                            if (ranked_gene.get('symbol', '').lower() ==
                                    gene.lower()):
                                break
                            else:
                                ranked_gene = None

                        if not ranked_gene:
                            log.debug("Could not find '{0}' in ranked gene "
                                      "list, skipping result".format(gene))
                            transaction.rollback()
                            continue

                        try:
                            rs = ResultScore.objects.get(result=result)
                            rs.rank = ranked_gene.get('rank')
                            rs.score = ranked_gene.get('score')
                        except ResultScore.DoesNotExist:
                            rs = ResultScore(
                                result=result,
                                rank=ranked_gene.get('rank'),
                                score=ranked_gene.get('score'))
                        rs.save()

                        updated_results += 1

                    except Exception:
                        log.exception("Error saving gene ranks and scores for "
                                      "sample '{0}'".format(sample.label))
                        transaction.rollback()
                        continue

                    transaction.commit()

            sample.phenotype_modified = datetime.now()
            sample.save()

            log.info("Updated {0} and skipped {1} results in sample '{2}'"
                     .format(updated_results, total_results - updated_results,
                             sample.label))
            updated_samples += 1

        log.info("Updated {0} and skipped {1} samples"
                 .format(updated_samples, total_samples-updated_samples))
