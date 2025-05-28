from django import template
from django.conf import settings
import random

register = template.Library()

@register.simple_tag
def apoiador_image_url(apoiador):
    if apoiador.imagem:
        return apoiador.imagem.url
    else:
        # Escolhe uma imagem padrão aleatória entre 1 e 5
        random_number = random.randint(1, 5)
        return f"{settings.STATIC_URL}assets/img/apoiadores/apoio{random_number}.png" 