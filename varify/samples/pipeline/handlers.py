import os
import logging
import sts
import time
import vcf
from django.db import connections, transaction
from sts.contextmanagers import transition
from varify.pipeline import job, ManifestReader
from varify.pipeline.load import pgcopy_batch
from varify.pipeline import checks
from varify.samples.models import Result, Project, Batch, Sample, \
    SampleManifest, DEFAULT_PROJECT_NAME
from . import SAMPLE_CHANNEL
from .utils import ResultStream

log = logging.getLogger(__name__)


@transaction.commit_on_success
def create_sample(sample_name, vcf_colname, batch_name, project_name=None,
                  version=0):
    version = int(version)

    if project_name:
        # Ensure a project is available for the sample
        project, created = Project.objects.get_or_create(
            name__iexact=project_name,
            defaults={'label': project_name, 'name': project_name})
    else:
        project = Project.objects.get(name=DEFAULT_PROJECT_NAME)

    batch, created = Batch.objects.get_or_create(
        name__iexact=batch_name, project=project,
        defaults={'label': batch_name, 'name': batch_name})

    sample, created = Sample.objects.get_or_create(
        name__iexact=sample_name, project=project, batch=batch,
        version=version, defaults={'label': sample_name, 'name': sample_name,
                                   'vcf_colname': vcf_colname})

    return sample, created


def check_sample_section(manifest):
    section = manifest.section('sample')
    #sample itself is no longer a required key
    required_keys = ('batch', 'project', 'version')
    return all([key in section for key in required_keys])


@job(SAMPLE_CHANNEL)
def load_samples(manifest_path, database, **kwargs):
    manifest = ManifestReader(manifest_path)

    # Ensure the sample is marked to be loaded..
    if not manifest.marked_for_load():
        log.info('Sample not marked for load', extra={
            'manifest_path': manifest_path,
        })
        return

    # Ensure the sample section is valid..
    if not check_sample_section(manifest):
        log.info('Manifest sample section is not valid', extra={
            'manifest_path': manifest_path,
        })
        return

    # [sample]
    # project = PCGC
    # batch = OTHER
    # sample = 1-03131
    # version = 1

    sample_info = manifest.section('sample')
    vcf_info = manifest.section('vcf')

    # ignore whatever sample is listed in the manifest and scan the vcf
    # for samples
    vcf_path = os.path.join(os.path.dirname(manifest_path), vcf_info['file'])

    with open(vcf_path) as file_obj:
        log.debug("opening {0} in load_samples".format(vcf_path))
        reader = vcf.Reader(file_obj)
        samples = reader.samples

    if 'sample' in sample_info:
        pretty_names = sample_info['sample'].split(',')
    else:
        pretty_names = samples

    if len(samples) != len(pretty_names):
        log.info('Length of comma-delimited samples field in manifest '
                 'does not match the length of samples in {0}'
                 .format(vcf_info['file']))
        return

    # Create the sample (and batch and project if needed)..
    num_created = 0
    num_skipped = 0

    for pretty_name, vcf_sample in zip(pretty_names, samples):
        log.debug('Trying to create {0} sample record'.format(vcf_sample))
        sample, created = create_sample(sample_name=pretty_name,
                                        vcf_colname=vcf_sample,
                                        batch_name=sample_info['batch'],
                                        project_name=sample_info['project'],
                                        version=sample_info['version'])
        log.debug('{0} created'.format(sample))

        if created:
            num_created += 1
            sts.transition(sample, 'Sample Record Created')
        else:
            num_skipped += 1

        manifest = SampleManifest.objects.filter(sample=sample)
        # Create a manfiest object for the sample if one does not exist
        if created or not manifest.exists():
            sample_manifest = SampleManifest(sample=sample)
            sample_manifest.load_content(manifest_path)
            sample_manifest.save()
            sts.transition(sample, 'Sample Manifest Created')

    # Publish to channel that this manifest is eligible for processing
    # downstream..
    if num_created > 0 or kwargs.get('force', False):
        SAMPLE_CHANNEL.publish(manifest_path=manifest_path, database=database)

    # Returns whether the sample has been created
    load_dict = {'created': num_created, 'skipped': num_skipped}
    return load_dict


@job(timeout=60 * 60)
def load_results(manifest_path, database, **kwargs):
    manifest = ManifestReader(manifest_path)

    if not manifest.marked_for_load():
        log.info('Sample not marked for load', extra={
            'manifest_path': manifest_path,
        })
        return

    # Ensure the sample section is valid..
    if not check_sample_section(manifest):
        log.info('Manifest sample section is not valid', extra={
            'manifest_path': manifest_path,
        })
        return

    sample_info = manifest.section('sample')
    vcf_info = manifest.section('vcf')
    # Ignore whatever sample is listed in the manifest and scan the vcf for
    # samples.
    vcf_path = os.path.join(os.path.dirname(manifest_path), vcf_info['file'])
    with open(vcf_path) as file_obj:
        log.debug("opening {0} in load_samples".format(vcf_path))
        reader = vcf.Reader(file_obj)
        samples = reader.samples
    if 'sample' in sample_info:
        pretty_names = sample_info['sample'].split(',')
    else:
        pretty_names = samples

    for pretty_name, vcf_sample in zip(pretty_names, samples):
        try:
            sample = Sample.objects.get(
                name__iexact=pretty_name,
                batch__name__iexact=sample_info['batch'],
                project__name__iexact=sample_info['project'],
                version=sample_info['version'])
        except Sample.DoesNotExist:
            log.error('Sample does not exist', extra=sample_info)
            return

        #is it already loaded, let's skip for now
        if Result.objects.filter(sample=sample).exists():
            log.debug('{0} exists in results'.format(vcf_sample))
        else:
            log.debug('about to load results for {0}'.format(vcf_sample))

            #STSError: Cannot start transition while already in one.
            successful = False
            while not successful:
                try:
                    with transition(sample, 'Sample Published',
                                    event='Loading Results'):
                        connection = connections[database]
                        cursor = connection.cursor()

                        with open(vcf_path) as fin:
                            stream = ResultStream(fin, sample_id=sample.id,
                                                  vcf_sample=vcf_sample)
                            columns = stream.output_columns
                            db_table = Result._meta.db_table
                            pgcopy_batch(stream, db_table, columns, cursor,
                                         database)

                        # Update result count
                        sample.count = sample.results.count()
                        sample.published = True
                        sample.save()
                        successful = True
                except:
                    log.exception('STS errors')
                    time.sleep(10)

    vcf_info = manifest.section('vcf')

    # Absolute path relative to the MANIFEST directory
    vcf_path = os.path.join(os.path.dirname(manifest_path), vcf_info['file'])

    # Compare expected MD5 (in manifest) to the file MD5
    if 'md5' in vcf_info:
        vcf_md5 = checks.file_md5(vcf_path)

        if vcf_md5 != vcf_info['md5']:
            log.error('VCF file MD5 does not match expected in manifest',
                      extra={'manifest_path': manifest_path})

    # Existing samples by the same name of a previous version are unpublished
    # now that is is ready to be published.
    count = Sample.objects.filter(
        name__iexact=sample.name, project=sample.project, batch=sample.batch,
        version__lt=sample.version).update(published=False)

    if count:
        log.info('{0} previous versions unpublished for {1}'
                 .format(count, sample))
