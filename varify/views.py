from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm
from news.models import Article


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
