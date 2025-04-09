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
    data = LineageStats.top_clans(limit=limit)
    return JsonResponse(data, safe=False)


def top_rich(request):
    limit = int(request.GET.get("limit", 10))
    data = LineageStats.top_adena(limit=limit)
    return JsonResponse(data, safe=False)


def top_online(request):
    limit = int(request.GET.get("limit", 10))
    data = LineageStats.top_online(limit=limit)
    return JsonResponse(data, safe=False)


def top_level(request):
    limit = int(request.GET.get("limit", 10))
    data = LineageStats.top_level(limit=limit)
    return JsonResponse(data, safe=False)


def olympiad_ranking(request):
    data = LineageStats.olympiad_ranking()
    return JsonResponse(data, safe=False)


def olympiad_all_heroes(request):
    data = LineageStats.olympiad_all_heroes()
    return JsonResponse(data, safe=False)


def olympiad_current_heroes(request):
    data = LineageStats.olympiad_current_heroes()
    return JsonResponse(data, safe=False)


def grandboss_status(request):
    data = LineageStats.grandboss_status()
    return JsonResponse(data, safe=False)


def raidboss_status(request):
    data = LineageStats.raidboss_status()
    return JsonResponse(data, safe=False)


def siege(request):
    data = LineageStats.siege()
    return JsonResponse(data, safe=False)


def siege_participants(request, castle_id):
    data = LineageStats.siege_participants(castle_id=castle_id)
    return JsonResponse(data, safe=False)


def boss_jewel_locations(request):
    jewel_ids = request.GET.get("ids", "")
    # Ex: ids=6656,6657,6658
    if not jewel_ids:
        return JsonResponse({"error": "Missing jewel item IDs"}, status=400)
    data = LineageStats.boss_jewel_locations(boss_jewel_ids=jewel_ids)
    return JsonResponse(data, safe=False)
