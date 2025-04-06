from django.shortcuts import render, get_object_or_404, redirect
from .models import News
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required
from .forms import NewsForm


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


@login_required
def create_news(request):
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            news = form.save(commit=False)
            news.author = request.user
            news.save()
            return redirect('news:detail', slug=news.slug)
    else:
        form = NewsForm()

    context = {
        'form': form,
        'segment': 'create',
        'parent': 'news',
    }
    return render(request, 'pages/news_create.html', context)
