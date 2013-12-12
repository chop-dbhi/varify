import json
from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm
from news.models import Article
from guardian.shortcuts import get_objects_for_user
from cilantro.models import UserPreferences
from varify.samples.models import Sample


def app(request, project=None, batch=None, sample=None):
    if hasattr(request, 'user') and request.user.is_authenticated():
        kwargs = {'user': request.user}
    else:
        kwargs = {'session_key': request.session.session_key}

    obj, created = UserPreferences.objects.get_or_create(**kwargs)
    preferences = obj.json
    preferences['id'] = obj.pk

    selectedProband = {}
    if project and batch:
        selectedProband['project'] = project
        selectedProband['batch'] = batch
        selectedProband['sample'] = sample

    projects = get_objects_for_user(request.user, 'samples.view_project')

    queryset = Sample.objects.select_related('batch', 'project')\
        .filter(published=True, batch__published=True, project__in=projects)\
        .values_list('pk', 'label', 'batch__name', 'project__name')\
        .order_by('project', 'batch', 'label')

    samples = []
    keys = ['id', 'sample', 'batch', 'project']
    for row in queryset:
        samples.append(dict(zip(keys, row)))

    return render(request, 'cilantro/index.html', {
        'user_preferences': json.dumps(preferences),
        'samples': json.dumps(samples),
        'selected_proband': json.dumps(selectedProband),
    })


def index(request):
    "Index/splash page"
    articles = Article.objects.filter(published=True)\
        .values('title', 'slug', 'created', 'summary')[:3]
    form = AuthenticationForm()
    return render(request, 'index.html', {
        'form': form,
        'articles': articles,
    })


def news(request):
    articles = Article.objects.filter(published=True)
    return render(request, 'news/list.html', {
        'articles': articles,
    })
