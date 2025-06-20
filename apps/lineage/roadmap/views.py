from django.shortcuts import render, get_object_or_404
from .models import Roadmap, RoadmapTranslation
from django.utils.translation import get_language

def index(request):
    # Exibe apenas itens publicados, não privados, e tradução em português
    language = 'pt'
    roadmaps = (
        Roadmap.objects.filter(is_published=True, is_private=False)
        .order_by('pub_date')
    )
    # Para cada roadmap, pega a tradução em português
    items = []
    for roadmap in roadmaps:
        translation = roadmap.translations.filter(language=language).first()
        if translation:
            items.append({
                'roadmap': roadmap,
                'translation': translation,
            })
    return render(request, 'pages/roadmap_index.html', {'items': items, 'segment': 'roadmap'})


def detail(request, slug):
    language = 'pt'
    roadmap = get_object_or_404(Roadmap, slug=slug, is_published=True, is_private=False)
    translation = roadmap.translations.filter(language=language).first()
    return render(request, 'pages/roadmap_detail.html', {
        'roadmap': roadmap,
        'translation': translation,
    })
