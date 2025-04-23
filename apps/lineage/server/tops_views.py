import base64

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from utils.crests import CrestHandler
from apps.lineage.server.database import LineageDB

from utils.dynamic_import import get_query_class  # importa o helper
LineageStats = get_query_class("LineageStats")  # carrega a classe certa com base no .env


@login_required
def top_pvp_view(request):
    result = LineageStats.top_pvp(limit=20)  # ou quantos quiser
    return render(request, 'tops/top_pvp.html', {'players': result})


@login_required
def top_pk_view(request):
    result = LineageStats.top_pk(limit=20)
    return render(request, 'tops/top_pk.html', {'players': result})


@login_required
def top_adena_view(request):
    result = LineageStats.top_adena(limit=20)
    return render(request, 'tops/top_adena.html', {'players': result})


@login_required
def top_clans_view(request):

    db = LineageDB()
    if db.is_connected():

        clanes = LineageStats.top_clans(limit=20)

        # Pega os IDs dos clãs para pegar os crests
        clan_ids = [clan.get('clan_id') for clan in clanes if 'clan_id' in clan]
        ally_ids = [clan.get('ally_id') for clan in clanes if 'ally_id' in clan]

        # Pega as crests para os clãs
        crests = LineageStats.get_crests(clan_ids) or {}
        ally_crests = LineageStats.get_crests(ally_ids, type='ally') or {}

        # Processa as imagens dos crests
        crest_handler = CrestHandler()

        for clan in clanes:
                crest_id = clan.get('clan_id')

                # Verifique se o crest existe
                # Ajusta a forma de acessar o crest
                crest_blob = None
                for crest in crests:
                    if crest.get('clan_id') == crest_id:
                        crest_blob = crest.get('crest')
                        break

                # Para o caso do clã ter um crest
                if crest_blob:
                    # Cria a imagem do crest do clã e converte para base64
                    image_bytes = crest_handler.make_image(crest_blob, crest_id, 'clan', show_image=True)

                    # Rewind the BytesIO to the beginning before encoding
                    image_bytes.seek(0)  # Coloca o ponteiro de volta ao início
                    crest_image_base64 = base64.b64encode(image_bytes.read()).decode('utf-8')
                    clan['clan_crest_image_base64'] = crest_image_base64
                else:
                    # Caso não haja crest do clã, cria uma imagem vazia
                    empty_image_bytes = crest_handler.make_empty_image('clan')

                    # Rewind the BytesIO to the beginning before encoding
                    empty_image_bytes.seek(0)  # Coloca o ponteiro de volta ao início
                    crest_image_base64 = base64.b64encode(empty_image_bytes.read()).decode('utf-8')
                    clan['clan_crest_image_base64'] = crest_image_base64

                # Se houver ally_id, processa a imagem da aliança também
                ally_crest_blob = None
                if clan.get('ally_id'):
                    for crest in ally_crests:
                        if crest.get('ally_id') == clan.get('ally_id'):
                            ally_crest_blob = crest.get('crest')
                            break

                    if ally_crest_blob:
                        # Cria a imagem do crest da aliança e converte para base64
                        ally_image_bytes = crest_handler.make_image(ally_crest_blob, crest_id, 'ally', show_image=True)

                        # Rewind the BytesIO to the beginning before encoding
                        ally_image_bytes.seek(0)  # Coloca o ponteiro de volta ao início
                        ally_crest_image_base64 = base64.b64encode(ally_image_bytes.read()).decode('utf-8')
                        clan['ally_crest_image_base64'] = ally_crest_image_base64
                    else:
                        # Caso não haja crest da aliança, cria uma imagem vazia
                        empty_ally_image_bytes = crest_handler.make_empty_image('ally')

                        # Rewind the BytesIO to the beginning before encoding
                        empty_ally_image_bytes.seek(0)  # Coloca o ponteiro de volta ao início
                        ally_crest_image_base64 = base64.b64encode(empty_ally_image_bytes.read()).decode('utf-8')
                        clan['ally_crest_image_base64'] = ally_crest_image_base64
    else:
        clanes = list()

    return render(request, 'tops/top_clans.html', {'clans': clanes})


@login_required
def top_level_view(request):
    result = LineageStats.top_level(limit=20)
    return render(request, 'tops/top_level.html', {'players': result})


def top_online_view(request):
    ranking = LineageStats.top_online()
    return render(request, 'tops/top_online.html', {"ranking": ranking})
