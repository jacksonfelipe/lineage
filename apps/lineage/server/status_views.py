from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _

import json, os, time
from django.conf import settings

from datetime import datetime, timedelta
from django.utils.timesince import timesince
from apps.lineage.server.database import LineageDB

from utils.dynamic_import import get_query_class  # importa o helper
LineageStats = get_query_class("LineageStats")  # carrega a classe certa com base no .env


@login_required
def siege_ranking_view(request):

    db = LineageDB()
    if db.is_connected():

        castles = LineageStats.siege()

        for castle in castles:
            participants = LineageStats.siege_participants(castle["id"])
            castle["attackers"] = [p for p in participants if p["type"] == "0"]
            castle["defenders"] = [p for p in participants if p["type"] == "1"]

            # adiciona caminho da imagem baseado no nome
            castle["image_path"] = f"assets/img/castles/{castle['name'].lower()}.jpg"

            # adiciona valores default traduzidos se vazio
            castle["clan_name"] = castle["clan_name"] or _("No Owner")
            castle["char_name"] = castle["char_name"] or _("No Leader")
            castle["ally_name"] = castle["ally_name"] or _("No Alliance")
            timestamp_s = castle["sdate"] / 1000
            castle["sdate"] = datetime.fromtimestamp(timestamp_s)

    else:
        castles = list()

    return render(request, "status/siege_ranking.html", {"castles": castles})


@login_required
def olympiad_ranking_view(request):
    # Obtém o ranking de olimpíada
    result = LineageStats.olympiad_ranking()
    return render(request, 'status/olympiad_ranking.html', {'ranking': result})


@login_required
def olympiad_all_heroes_view(request):
    # Obtém todos os heróis da olimpíada
    heroes = LineageStats.olympiad_all_heroes()
    return render(request, 'status/olympiad_all_heroes.html', {'heroes': heroes})


@login_required
def olympiad_current_heroes_view(request):
    # Obtém os heróis atuais da olimpíada
    current_heroes = LineageStats.olympiad_current_heroes()
    return render(request, 'status/olympiad_current_heroes.html', {'current_heroes': current_heroes})


@login_required
def boss_jewel_locations_view(request):

    db = LineageDB()
    if db.is_connected():

        boss_jewel_ids = [6656, 6657, 6658, 6659, 6660, 6661, 8191]
        jewel_locations = LineageStats.boss_jewel_locations(boss_jewel_ids)

        # Caminho para o itens.json
        itens_path = os.path.join(settings.BASE_DIR, 'utils/data/itens.json')
        with open(itens_path, 'r', encoding='utf-8') as f:
            itens_data = json.load(f)

        # Substituir item_id pelo item_name
        for loc in jewel_locations:
            item_id_str = str(loc['item_id'])
            item_name = itens_data.get(item_id_str, ["Desconhecido"])[0]
            loc['item_name'] = item_name

    else:
        jewel_locations = list()

    return render(request, 'status/boss_jewel_locations.html', {'jewel_locations': jewel_locations})


@login_required
def grandboss_status_view(request):

    db = LineageDB()
    if db.is_connected():

        grandboss_status = LineageStats.grandboss_status()

        # Carregar o JSON de bosses
        bosses_path = os.path.join(settings.BASE_DIR, 'utils/data/bosses.json')
        with open(bosses_path, 'r', encoding='utf-8') as f:
            bosses_data = json.load(f)

        bosses_index = {str(boss['id']): boss for boss in bosses_data['data']}

        # Enriquecer os dados
        for boss in grandboss_status:
            boss_id_str = str(boss['boss_id'])
            boss_info = bosses_index.get(boss_id_str, {"name": "Desconhecido", "level": "-"})

            boss['name'] = boss_info['name']
            boss['level'] = boss_info['level']

            # Ajuste no fuso horário (considerando o GMT)
            gmt_offset = float(settings.GMT_OFFSET)  # Certifique-se de que o GMT_OFFSET está configurado corretamente no settings
            respawn_timestamp = boss['respawn'] / 1000  # Converter de milissegundos para segundos
            current_time = time.time()

            # Ajustar o respawn considerando o fuso horário
            respawn_datetime = datetime.fromtimestamp(respawn_timestamp) - timedelta(hours=gmt_offset)
            respawn_human = respawn_datetime.strftime('%d/%m/%Y %H:%M')

            # Humanizar o tempo de respawn
            boss['respawn_human'] = respawn_human

            # Verificar se o boss está vivo ou morto
            if boss['respawn'] > 0:
                boss['status'] = "Morto"
            else:
                boss['status'] = "Vivo"
                boss['respawn_human'] = '-'  # Quando vivo, o respawn é '-'

    else:
        grandboss_status = list()

    return render(request, 'status/grandboss_status.html', {'bosses': grandboss_status})
