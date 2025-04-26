import base64

from utils.crests import CrestHandler
from apps.lineage.server.database import LineageDB

from utils.dynamic_import import get_query_class  # importa o helper
LineageStats = get_query_class("LineageStats")  # carrega a classe certa com base no .env


def attach_crests_to_clans(data, clan_key='clan_id', ally_key='ally_id'):
    """
    Adiciona as imagens de crest base64 para cada clã ou personagem (que tenha clan_id).
    Espera uma lista de dicionários.
    """
    if not data:
        return data

    db = LineageDB()
    if not db.is_connected():
        return data

    crest_handler = CrestHandler()

    # Coleta os IDs únicos
    clan_ids = list({item.get(clan_key) for item in data if item.get(clan_key)})
    ally_ids = list({item.get(ally_key) for item in data if item.get(ally_key)})

    # Busca os crests
    crests = LineageStats.get_crests(clan_ids) or {}
    ally_crests = LineageStats.get_crests(ally_ids, type='ally') or {}

    for item in data:
        crest_id = item.get(clan_key)

        # Clã Crest
        crest_blob = next((crest.get('crest') for crest in crests if crest.get('clan_id') == crest_id), None)
        if crest_blob:
            image_bytes = crest_handler.make_image(crest_blob, crest_id, 'clan', show_image=True)
            image_bytes.seek(0)
            item['clan_crest_image_base64'] = base64.b64encode(image_bytes.read()).decode('utf-8')
        else:
            empty_image_bytes = crest_handler.make_empty_image('clan')
            empty_image_bytes.seek(0)
            item['clan_crest_image_base64'] = base64.b64encode(empty_image_bytes.read()).decode('utf-8')

        # Ally Crest
        ally_id = item.get(ally_key)
        ally_crest_blob = next((crest.get('crest') for crest in ally_crests if crest.get('ally_id') == ally_id), None)
        if ally_crest_blob:
            ally_image_bytes = crest_handler.make_image(ally_crest_blob, crest_id, 'ally', show_image=True)
            ally_image_bytes.seek(0)
            item['ally_crest_image_base64'] = base64.b64encode(ally_image_bytes.read()).decode('utf-8')
        else:
            empty_ally_image_bytes = crest_handler.make_empty_image('ally')
            empty_ally_image_bytes.seek(0)
            item['ally_crest_image_base64'] = base64.b64encode(empty_ally_image_bytes.read()).decode('utf-8')

    return data
