from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from .forms import GeneSetBulkForm
from vdw.genes.models import GeneSet


def geneset_form(request, pk=None):
    if request.user.has_perm('genes.change_geneset'):
        genesets = GeneSet.objects.all()
        geneset = get_object_or_404(GeneSet, pk=pk) if pk else None
    else:
        genesets = GeneSet.objects.filter(user=request.user)
        geneset = get_object_or_404(
            GeneSet, pk=pk, user=request.user) if pk else None

    if request.method == 'POST':
        form = GeneSetBulkForm(request.POST, initial={'user': request.user},
                               instance=geneset)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('genesets'))
    else:
        form = GeneSetBulkForm(instance=geneset)

    return render(request, 'genes/geneset-form.html', {
        'form': form,
        'geneset': geneset,
        'genesets': genesets,
    })


def geneset_delete(request, pk):
    if request.user.has_perm('genes.change_geneset'):
        geneset = get_object_or_404(GeneSet, pk=pk)
    else:
        geneset = get_object_or_404(GeneSet, pk=pk, user=request.user)

    geneset.delete()

    return HttpResponseRedirect(reverse('genesets'))
