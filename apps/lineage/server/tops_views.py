from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.lineage.server.utils.crest import attach_crests_to_clans
from apps.lineage.server.database import LineageDB

from utils.dynamic_import import get_query_class  # importa o helper
LineageStats = get_query_class("LineageStats")  # carrega a classe certa com base no .env


@login_required
def top_pvp_view(request):
    db = LineageDB()
    result = LineageStats.top_pvp(limit=20) if db.is_connected() else []
    result = attach_crests_to_clans(result)
    return render(request, 'tops/top_pvp.html', {'players': result})


@login_required
def top_pk_view(request):
    db = LineageDB()
    result = LineageStats.top_pk(limit=20) if db.is_connected() else []
    result = attach_crests_to_clans(result)
    return render(request, 'tops/top_pk.html', {'players': result})


@login_required
def top_adena_view(request):
    db = LineageDB()
    result = LineageStats.top_adena(limit=20) if db.is_connected() else []
    result = attach_crests_to_clans(result)
    return render(request, 'tops/top_adena.html', {'players': result})


@login_required
def top_clans_view(request):
    db = LineageDB()
    clanes = LineageStats.top_clans(limit=20) if db.is_connected() else []
    clanes = attach_crests_to_clans(clanes)
    return render(request, 'tops/top_clans.html', {'clans': clanes})


@login_required
def top_level_view(request):
    db = LineageDB()
    result = LineageStats.top_level(limit=20) if db.is_connected() else []
    result = attach_crests_to_clans(result)
    return render(request, 'tops/top_level.html', {'players': result})


def top_online_view(request):
    db = LineageDB()
    result = LineageStats.top_online(limit=20) if db.is_connected() else []
    result = attach_crests_to_clans(result)
    return render(request, 'tops/top_online.html', {"ranking": result})
