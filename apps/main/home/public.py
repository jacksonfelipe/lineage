from django.shortcuts import render, get_object_or_404
from django.http import Http404
from apps.main.faq.models import FAQ
from apps.main.news.models import News


def public_news_list(request):
    latest_news_list = News.objects.filter(is_published=True, is_private=False).order_by('-pub_date')[:5]

    context = dict()
    context['latest_news_list'] = latest_news_list

    return render(request, 'pages/public_news_index.html', context)


def public_news_detail(request, slug):
    news = get_object_or_404(News, slug=slug)
    if news.is_private and not request.user.is_authenticated:
        raise Http404("Notícia privada não está disponível.")
    
    context = dict()
    context['news'] = news

    return render(request, 'pages/public_news_detail.html', context)


def public_faq_list(request):
    public_faqs = FAQ.objects.filter(is_public=True)

    context = dict()
    context['public_faqs'] = public_faqs

    return render(request, 'pages/public_faq.html', context)
