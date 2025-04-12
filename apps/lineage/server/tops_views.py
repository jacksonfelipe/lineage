from django.shortcuts import render
from django.contrib.auth.decorators import login_required

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
    result = LineageStats.top_clans(limit=20)
    return render(request, 'tops/top_clans.html', {'clans': result})


@login_required
def top_level_view(request):
    result = LineageStats.top_level(limit=20)
    return render(request, 'tops/top_level.html', {'players': result})


def top_online_view(request):
    ranking = LineageStats.top_online()
    return render(request, 'tops/top_online.html', {"ranking": ranking})
