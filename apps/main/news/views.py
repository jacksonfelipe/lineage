from django.shortcuts import render, get_object_or_404
from .models import News
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required


@login_required
def index(request):
    private_news_list = News.objects.filter(is_published=True, is_private=True).order_by('-pub_date')[:5]
    context = {
        'private_news_list': private_news_list,
        'segment': 'index',
        'parent': 'news',
    }
    return render(request, 'pages/news_index.html', context)


@login_required
def detail(request, slug):
    news = get_object_or_404(News, slug=slug)
    context = {
        'news': news,
        'segment': 'detail',
        'parent': 'news',
        }
    return render(request, 'pages/news_detail.html', context)
