import httpretty
import logging
import re
from django.core import management
from django.test import TestCase
from django.test.utils import override_settings
from requests.exceptions import ConnectionError, RequestException, SSLError
from vdw.samples.management.subcommands import gene_ranks
from vdw.samples.models import Sample, Result, ResultScore
from ....models import MockHandler


@override_settings(VARIFY_AUTO_CREATE_COHORT=False, VARIFY_CERT='cert.pem',
                   VARIFY_KEY='key.pem')
class GeneRanksTestCase(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        """
        Setup a mock log handler for cataloging log messages generated during
        the run of this individual test."
        """

        logger = logging.getLogger(gene_ranks.__name__)
        self.mock_handler = MockHandler()
        logger.addHandler(self.mock_handler)

    def mock_ssl_error(self, request, uri, headers):
        """
        Mocks the occurrence of an SSLError when accessing an endpoint.
        """

        raise SSLError

    def mock_connection_error(self, request, uri, headers):
        """
        Mocks the occurrence of a ConnectionError when accessing an endpoint.
        """

        raise ConnectionError

    def mock_request_exception(self, request, uri, headers):
        """
        Mocks the occurrence of a RequestException when accessing an endpoint.
        """

        raise RequestException

    def mock_unparseable_terms(self, request, uri, headers):
        """
        Mocks a partially valid response from the phenotype endpoint. In this
        case, the hpoAnnotations key is present but the value is a collection
        of hpo terms rather than a collection of objects of the form:
            {
                "hpo_id": "HP_0000407",
                "name": "Sensorineural hearing impairment",
                "priority": null
            }
        """

        json = """{
            "last_modified": "2014-02-27T16:48:39.743363",
            "hpoAnnotations": ["HPO:1", "HPO:2"]
        }"""

        return (200, headers, json)

    def mock_malformed_gene_rank(self, request, uri, headers):
        """
        Mocks a partially valid gene rank endpoint response where a score and
        a rank is not of the correct type.
        """

        json = """{
            "ranked_genes": [
                {
                    "symbol": "CD160",
                    "score": 3.196735916182328,
                    "rank": 1
                },
                {
                    "symbol": "PEX11B",
                    "score": "BAD_SCORE",
                    "rank": 2
                },
                {
                    "symbol": "HFE2",
                    "score": 0.615416141739313,
                    "rank": "BAD_RANK"
                }
            ],
            "unranked_genes": [
                "LINC00875",
                "GPR89A",
                "CD160",
                "POLR3C",
                "NBPF12",
                "SEC22B",
                "NOTCH2NL",
                "GNRHR2",
                "LOC100288142",
                "PDE4DIP",
                "LOC100130000",
                "LOC728875",
                "NUDT17",
                "PIAS3",
                "RNF115",
                "NBPF10",
                "NBPF9",
                "FLJ39739",
                "None",
                "LIX1L",
                "PDZK1",
                "ITGA10",
                "TXNIP",
                "ANKRD34A",
                "LINC00623",
                "POLR3GL",
                "ANKRD35"
            ],
            "hpo_valid": [
                "HP:0000407",
                "HP:0001263",
                "HP:0000175"
            ],
            "hpo_invalid": [ ]
        }"""

        return (200, headers, json)

    def mock_gene_rank(self, request, uri, headers):
        """
        Mocks an actual, valid response as seen from the live gene rank
        endpoint. This response should be fully parseable and understood
        by the gene ranking command code.
        """

        json = """{
            "ranked_genes": [
                {
                    "symbol": "RBM8A",
                    "score": 3.196735916182328,
                    "rank": 1
                },
                {
                    "symbol": "PEX11B",
                    "score": 2.967686462072098,
                    "rank": 2
                },
                {
                    "symbol": "HFE2",
                    "score": 0.615416141739313,
                    "rank": 3
                }
            ],
            "unranked_genes": [
                "LINC00875",
                "GPR89A",
                "CD160",
                "POLR3C",
                "NBPF12",
                "SEC22B",
                "NOTCH2NL",
                "GNRHR2",
                "LOC100288142",
                "PDE4DIP",
                "LOC100130000",
                "LOC728875",
                "NUDT17",
                "PIAS3",
                "RNF115",
                "NBPF10",
                "NBPF9",
                "FLJ39739",
                "None",
                "LIX1L",
                "PDZK1",
                "ITGA10",
                "TXNIP",
                "ANKRD34A",
                "LINC00623",
                "POLR3GL",
                "ANKRD35"
            ],
            "hpo_valid": [
                "HP:0000407",
                "HP:0001263",
                "HP:0000175"
            ],
            "hpo_invalid": [ ]
        }"""

        return (200, headers, json)

    def mock_phenotype(self, request, uri, headers):
        """
        Mocks an actual, valid response as seen from the live phenotype
        endpoint. This response should be fully parseable and understood
        completely by the gene ranking code.
        """
        json = """{
            "birth_day": null,
            "birth_hc": null,
            "birth_length": null,
            "birth_month": null,
            "birth_weight": null,
            "birth_year": null,
            "confirmedDiagnoses": [],
            "created": "2014-02-14T12:06:30.657",
            "gest_days": null,
            "gest_weeks": null,
            "hpoAnnotations": [
                {
                    "hpo_id": "HP_0000407",
                    "name": "Sensorineural hearing impairment",
                    "priority": null
                },
                {
                    "hpo_id": "HP_0001263",
                    "name": "Global developmental delay",
                    "priority": null
                },
                {
                    "hpo_id": "HP_0000175",
                    "name": "Cleft palate",
                    "priority": null
                },
                {
                    "hpo_id": "",
                    "name": "Empty term",
                    "priority": null
                }
            ],
            "last_modified": "2014-03-01T09:41:13.719",
            "notes": [
                {
                    "note": ""
                }
            ],
            "ruledOutDiagnoses": [],
            "sex": null,
            "suspectedDiagnoses": []
        }"""

        return (200, headers, json)

    def register_patches(self):
        """
        Registers all the shared(or potentially common) uri patches to
        intercept requests from the individual tests. Any test-specific
        patches can be applied within the test so they don't conflict with
        other tests.
        """

        httpretty.register_uri(
            httpretty.GET,
            re.compile("http://localhost/api/tests/connection_error/(.*)/"),
            body=self.mock_connection_error)
        httpretty.register_uri(
            httpretty.GET,
            re.compile("http://localhost/api/tests/request_exception/(.*)/"),
            body=self.mock_request_exception)
        httpretty.register_uri(
            httpretty.GET,
            re.compile("http://localhost/api/tests/ssl_error/(.*)/"),
            body=self.mock_ssl_error)
        httpretty.register_uri(
            httpretty.GET,
            re.compile("http://localhost/api/tests/unparseable_data/(.*)/"),
            body="UNPARSEABLE RESPONSE BODY, JSON EXPECTED")
        httpretty.register_uri(
            httpretty.GET,
            re.compile("http://localhost/api/tests/unparseable_date/(.*)/"),
            body='{"last_modified": "half past noon"}',
            content_type="application/json")
        httpretty.register_uri(
            httpretty.GET,
            re.compile("http://localhost/api/tests/unparseable_terms/(.*)/"),
            body=self.mock_unparseable_terms,
            content_type="application/json")
        httpretty.register_uri(
            httpretty.GET,
            re.compile("http://localhost/api/tests/phenotype/(.*)/"),
            body=self.mock_phenotype,
            content_type="application/json")
        httpretty.register_uri(
            httpretty.POST,
            "http://localhost/api/tests/gene_rank_exception",
            body=self.mock_request_exception)
        httpretty.register_uri(
            httpretty.POST,
            "http://localhost/api/tests/gene_rank",
            body=self.mock_gene_rank)
        httpretty.register_uri(
            httpretty.POST,
            "http://localhost/api/tests/malformed_gene_rank",
            body=self.mock_malformed_gene_rank)

    def test_missing_settings(self):
        error_log_count = len(self.mock_handler.messages['error'])

        with self.settings(PHENOTYPE_ENDPOINT=None):
            management.call_command('samples', 'gene-ranks')
            self.assertEqual(error_log_count + 1,
                             len(self.mock_handler.messages['error']))

        with self.settings(PHENOTYPE_ENDPOINT='api/tests/phenotype',
                           GENE_RANK_BASE_URL=None):
            management.call_command('samples', 'gene-ranks')
            self.assertEqual(error_log_count + 2,
                             len(self.mock_handler.messages['error']))

        with self.settings(PHENOTYPE_ENDPOINT='api/tests/phenotype',
                           GENE_RANK_BASE_URL='api/tests/gene_rank',
                           VARIFY_CERT=None):
            management.call_command('samples', 'gene-ranks')
            self.assertEqual(error_log_count + 3,
                             len(self.mock_handler.messages['error']))

        with self.settings(PHENOTYPE_ENDPOINT='api/tests/phenotype',
                           GENE_RANK_BASE_URL='api/tests/gene_rank',
                           VARIFY_KEY=None):
            management.call_command('samples', 'gene-ranks')
            self.assertEqual(error_log_count + 4,
                             len(self.mock_handler.messages['error']))

        self.assertEqual(ResultScore.objects.count(), 0)

    @httpretty.activate
    def test_url_and_data_errors(self):
        self.register_patches()

        # Use a sample we now is present but account for all the possible
        # error results from the real endpoint by using mock error resources.
        with self.settings(PHENOTYPE_ENDPOINT='http://localhost/api/tests/connection_error/%s/',    # noqa
                           GENE_RANK_BASE_URL='api/tests/gene_rank'):
            management.call_command('samples', 'gene-ranks', 'NA12878')

            self.assertTrue(self.mock_handler.messages['error'])
            self.assertTrue("A ConnectionError occurred" in
                            self.mock_handler.messages['error'][-1])

        with self.settings(PHENOTYPE_ENDPOINT='http://localhost/api/tests/request_exception/%s/',   # noqa
                           GENE_RANK_BASE_URL='api/tests/gene_rank'):
            management.call_command('samples', 'gene-ranks', 'NA12878')

            self.assertTrue(self.mock_handler.messages['error'])
            self.assertTrue("The sample has no phenotype data associated" in
                            self.mock_handler.messages['error'][-1])

        with self.settings(PHENOTYPE_ENDPOINT='http://localhost/api/tests/ssl_error/%s/',   # noqa
                           GENE_RANK_BASE_URL='api/tests/gene_rank'):
            management.call_command('samples', 'gene-ranks', 'NA12878')

            self.assertTrue(self.mock_handler.messages['error'])
            self.assertTrue("An SSLError occurred" in
                            self.mock_handler.messages['error'][-1])

        with self.settings(PHENOTYPE_ENDPOINT='http://localhost/api/tests/unparseable_data/%s/',    # noqa
                           GENE_RANK_BASE_URL='api/tests/gene_rank'):
            management.call_command('samples', 'gene-ranks', 'NA12878')

            self.assertTrue(self.mock_handler.messages['warning'])
            self.assertTrue("Could not parse response" in
                            self.mock_handler.messages['warning'][-1])

        with self.settings(PHENOTYPE_ENDPOINT='http://localhost/api/tests/unparseable_date/%s/',    # noqa
                           GENE_RANK_BASE_URL='api/tests/gene_rank'):
            management.call_command('samples', 'gene-ranks', 'NA12878')

            self.assertTrue(self.mock_handler.messages['warning'])
            self.assertTrue("Could not parse 'last_modified'" in
                            self.mock_handler.messages['warning'][-2])
            self.assertTrue("Response from phenotype missing HPO Annotations"
                            in self.mock_handler.messages['warning'][-1])

        with self.settings(PHENOTYPE_ENDPOINT='http://localhost/api/tests/unparseable_terms/%s/',   # noqa
                           GENE_RANK_BASE_URL='api/tests/gene_rank'):
            management.call_command('samples', 'gene-ranks', 'NA12878')

            self.assertTrue(self.mock_handler.messages['warning'])
            self.assertTrue("because it has no HPO terms" in
                            self.mock_handler.messages['warning'][-1])

        with self.settings(PHENOTYPE_ENDPOINT='http://localhost/api/tests/phenotype/%s/',           # noqa
                           GENE_RANK_BASE_URL='http://localhost/api/tests/gene_rank_exception'):    # noqa
            management.call_command('samples', 'gene-ranks', 'NA12878')

            self.assertTrue(self.mock_handler.messages['error'])
            self.assertTrue('Error retrieving gene rankings' in
                            self.mock_handler.messages['error'][-1])

        # We still shouldn't have any ResultScores as we've been nothing but a
        # failure to this point.
        self.assertEqual(ResultScore.objects.count(), 0)

    @httpretty.activate
    def test_load(self):
        self.register_patches()

        initial_score_count = ResultScore.objects.count()
        # Assert that all the samples we expect to be in the DB are there
        self.assertSequenceEqual(
            Sample.objects.all().values_list('label', flat=True),
            ['NA12878', 'NA12891', 'VPseq004-P-A'])

        with self.settings(PHENOTYPE_ENDPOINT='http://localhost/api/tests/phenotype/%s/',   # noqa
                           GENE_RANK_BASE_URL='http://localhost/api/tests/gene_rank'):      # noqa
            management.call_command('samples', 'gene-ranks', 'FAKE')

            # There should be info log messages and the last one should be a
            # report that 0 samples were loaded and 0 were skipped meaning
            # that we didn't do anything because the sample label we passed in
            # was bogus.
            self.assertTrue(self.mock_handler.messages['info'])
            self.assertEqual(self.mock_handler.messages['info'][-1],
                             "Updated 0 and skipped 0 samples")

            self.assertEqual(ResultScore.objects.count(), initial_score_count)

            management.call_command('samples', 'gene-ranks')

            # We should be error free. A few samples will have been skipped but
            # nothing should have caused an error.
            self.assertFalse(self.mock_handler.messages['error'])

            # Make sure the samples were updated by checking the log
            # and verifying the timestamps.
            self.assertTrue(self.mock_handler.messages['info'])
            self.assertEqual(self.mock_handler.messages['info'][-1],
                             "Updated 3 and skipped 0 samples")
            self.assertTrue(Sample.objects.filter(
                phenotype_modified__isnull=False).count(), 3)

            # We are not doing a varification of the ranker here, all we care
            # about is that there were scores added.
            self.assertGreater(ResultScore.objects.count(),
                               initial_score_count)
            initial_score_count = ResultScore.objects.count()

            # Calling the gene-rank command again should skip all of the
            # samples because they were just updated and the newer phenotyope
            # modified time should cause them to be skipped.
            management.call_command('samples', 'gene-ranks')
            self.assertEqual(self.mock_handler.messages['info'][-1],
                             "Updated 0 and skipped 3 samples")

            # No new result scores should be created when the samples are
            # not updated.
            self.assertEqual(ResultScore.objects.count(), initial_score_count)

            # Now, check to make sure that the force flag works by forcing
            # reloading of the samples that we just confirmed get skipped
            # because they are already up-to-date.
            management.call_command('samples', 'gene-ranks', force=True)
            self.assertEqual(self.mock_handler.messages['info'][-1],
                             "Updated 3 and skipped 0 samples")

            # No new result scores should be created when the samples are
            # updated(given the same mock data as the initial scoring).
            self.assertEqual(ResultScore.objects.count(), initial_score_count)

        with self.settings(PHENOTYPE_ENDPOINT='http://localhost/api/tests/phenotype/%s/',           # noqa
                           GENE_RANK_BASE_URL='http://localhost/api/tests/malformed_gene_rank'):    # noqa
            initial_score_count = ResultScore.objects.count()

            # Force update to guarantee that all samples are updated regardless
            # of timestamps and just use a single sample here to save time.
            management.call_command('samples', 'gene-ranks', 'VPseq004-P-A',
                                    force=True)

            # There should be errors that occurred when trying to save result
            # scores with poorly typed scores and ranks so check for those
            # first before making sure the results were updated.
            self.assertTrue(self.mock_handler.messages['error'])
            self.assertTrue("Error saving gene ranks and scores " in
                            self.mock_handler.messages['error'][-1])

            # We know that the gene CD160 appears in 4 results but shares 3
            # results with the ranked genes loaded in the previous step so we
            # expect 1 new result scores in this case since we are only loading
            # 1 samples here.
            self.assertTrue(ResultScore.objects.count(),
                            initial_score_count + 1)

        with self.settings(PHENOTYPE_ENDPOINT='http://localhost/api/tests/phenotype/%s/',   # noqa
                           GENE_RANK_BASE_URL='http://localhost/api/tests/gene_rank'):      # noqa
            # Delete all the results for a sample(which means it has no genes)
            # and make sure that the sample is skipped.
            Result.objects.filter(sample__label='VPseq004-P-A').delete()

            management.call_command('samples', 'gene-ranks', 'VPseq004-P-A',
                                    force=True)

            self.assertTrue(self.mock_handler.messages['warning'])
            self.assertTrue('because it has no genes associated' in
                            self.mock_handler.messages['warning'][-1])
