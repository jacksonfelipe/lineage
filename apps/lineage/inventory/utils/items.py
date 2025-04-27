import os
import json
from django.conf import settings
from apps.lineage.inventory.models import CustomItem
from django.core.files.storage import default_storage


def get_itens_json():
    # Carrega itens.json
    itens_path = os.path.join(settings.BASE_DIR, 'utils/data/itens.json')
    with open(itens_path, 'r', encoding='utf-8') as f:
        itens_data = json.load(f)

    # Carregar itens customizados do banco de dados
    custom_items = CustomItem.objects.all()

    # Adiciona os itens customizados no JSON
    for item in custom_items:
        # A chave que será usada no JSON será o ID do item customizado
        itens_data[str(item.id)] = [item.nome, item.imagem.url if item.imagem else f"{settings.STATIC_URL}assets/img/l2/icons/default.jpg"]

    # Atualiza a URL dos itens não customizados
    for item_id, item_info in itens_data.items():
        # Se o item não tiver uma URL personalizada (i.e., não for customizado)
        if not item_info[1]:
            # Construa o caminho completo para o arquivo de imagem
            item_image_path = os.path.join(settings.BASE_DIR, 'static/assets/img/l2/icons/5-{}.jpg'.format(item_id))

            # Verifique se o arquivo de imagem existe
            if default_storage.exists(item_image_path):
                # A imagem existe, então use a URL padrão
                item_info[1] = f"{settings.STATIC_URL}assets/img/l2/icons/5-{item_id}.jpg"
            else:
                # A imagem não existe, então use a imagem default
                item_info[1] = f"{settings.STATIC_URL}assets/img/l2/icons/default.jpg"

    # Retorna o itens_data atualizado
    return itens_data
