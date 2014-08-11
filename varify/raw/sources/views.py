from django.shortcuts import render
from vdw.raw.sources.models import Source


def sources(request):
    sources = Source.objects.filter(published=True, archived=False)\
        .select_related('stats')
    return render(request, 'sources/sources.html', {
        'sources': sources,
    })
