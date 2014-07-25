from guardian.shortcuts import get_objects_for_user
from django.http import Http404, HttpResponseRedirect
from django.db.models import Count
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from vdw.samples.models import Sample, Project, Batch, Cohort
from .forms import CohortForm


def registry(request):
    projects = get_objects_for_user(request.user, 'samples.view_project')

    batch_count = Count('batches', distinct=True)
    sample_count = Count('samples', distinct=True)

    # Distinct count on batch necessary since the join inflates the numbers
    projects = projects.annotate(sample_count=sample_count,
                                 batch_count=batch_count)

    staged_samples = \
        Sample.objects.filter(published=False, project__in=projects) \
        .select_related('batch', 'project')

    return render(request, 'samples/registry.html', {
        'projects': list(projects),
        'staged_samples': list(staged_samples),
    })


def project_registry(request, pk):
    projects = get_objects_for_user(request.user, 'samples.view_project')

    batch_count = Count('batches', distinct=True)
    sample_count = Count('samples', distinct=True)

    # Distinct count on batch necessary since the join inflates the numbers
    try:
        project = projects.annotate(sample_count=sample_count,
                                    batch_count=batch_count).get(pk=pk)
    except Project.DoesNotExist:
        raise Http404

    batches = Batch.objects.filter(project=project) \
        .annotate(sample_count=Count('samples'))

    return render(request, 'samples/project.html', {
        'project': project,
        'batches': batches,
    })


def batch_registry(request, pk):
    projects = get_objects_for_user(request.user, 'samples.view_project')

    sample_count = Count('samples', distinct=True)

    try:
        batch = Batch.objects.annotate(sample_count=sample_count) \
            .filter(project__in=projects).select_related('project').get(pk=pk)
    except Batch.DoesNotExist:
        raise Http404

    samples = Sample.objects.filter(batch=batch)

    return render(request, 'samples/batch.html', {
        'batch': batch,
        'project': batch.project,
        'samples': samples,
    })


def sample_registry(request, pk):
    projects = get_objects_for_user(request.user, 'samples.view_project')

    try:
        sample = Sample.objects.filter(project__in=projects) \
            .select_related('batch', 'project').get(pk=pk)
    except Sample.DoesNotExist:
        raise Http404

    return render(request, 'samples/sample.html', {
        'sample': sample,
        'batch': sample.batch,
        'project': sample.project,
    })


def cohort_form(request, pk=None):
    if request.user.has_perm('samples.change_cohort'):
        cohorts = Cohort.objects.all()
        cohort = get_object_or_404(Cohort, pk=pk) if pk else None
    else:
        cohorts = Cohort.objects.filter(user=request.user)
        cohort = \
            get_object_or_404(Cohort, pk=pk, user=request.user) if pk else None

    # Apply permissions..
    samples = Sample.objects.all()

    if request.method == 'POST':
        form = CohortForm(samples, data=request.POST, instance=cohort,
                          initial={'user': request.user})
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('cohorts'))
    else:
        form = CohortForm(samples, instance=cohort)

    return render(request, 'samples/cohort-form.html', {
        'form': form,
        'cohort': cohort,
        'cohorts': cohorts,
    })


def cohort_delete(request, pk):
    if request.user.has_perm('samples.change_cohort'):
        cohort = get_object_or_404(Cohort, pk=pk)
    else:
        cohort = get_object_or_404(Cohort, pk=pk, user=request.user)

    cohort.delete()

    return HttpResponseRedirect(reverse('cohorts'))
