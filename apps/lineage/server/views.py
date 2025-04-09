from django.http import JsonResponse
from .querys.query_dreamv3 import LineageStats


def players_online(request):
    data = LineageStats.players_online()
    return JsonResponse(data, safe=False)


def top_pvp(request):
    limit = int(request.GET.get("limit", 10))
    data = LineageStats.top_pvp(limit=limit)
    return JsonResponse(data, safe=False)


def top_pk(request):
    limit = int(request.GET.get("limit", 10))
    data = LineageStats.top_pk(limit=limit)
    return JsonResponse(data, safe=False)


def top_clan(request):
    limit = int(request.GET.get("limit", 10))
    data = LineageStats.top_clan(limit=limit)
    return JsonResponse(data, safe=False)


def top_rich(request):
    limit = int(request.GET.get("limit", 10))
    data = LineageStats.top_rich(limit=limit)
    return JsonResponse(data, safe=False)
