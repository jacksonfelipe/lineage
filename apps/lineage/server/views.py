from django.http import JsonResponse
from .querys.query_dreamv3 import LineageStats
from .decorators import endpoint_enabled
from django.shortcuts import render, redirect
from .models import ApiEndpointToggle
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required


@endpoint_enabled('players_online')
def players_online(request):
    data = LineageStats.players_online()
    return JsonResponse(data, safe=False)


@endpoint_enabled('top_pvp')
def top_pvp(request):
    limit = int(request.GET.get("limit", 10))
    data = LineageStats.top_pvp(limit=limit)
    return JsonResponse(data, safe=False)


@endpoint_enabled('top_pk')
def top_pk(request):
    limit = int(request.GET.get("limit", 10))
    data = LineageStats.top_pk(limit=limit)
    return JsonResponse(data, safe=False)


@endpoint_enabled('top_clan')
def top_clan(request):
    limit = int(request.GET.get("limit", 10))
    data = LineageStats.top_clans(limit=limit)
    return JsonResponse(data, safe=False)


@endpoint_enabled('top_rich')
def top_rich(request):
    limit = int(request.GET.get("limit", 10))
    data = LineageStats.top_adena(limit=limit)
    return JsonResponse(data, safe=False)


@endpoint_enabled('top_online')
def top_online(request):
    limit = int(request.GET.get("limit", 10))
    data = LineageStats.top_online(limit=limit)
    return JsonResponse(data, safe=False)


@endpoint_enabled('top_level')
def top_level(request):
    limit = int(request.GET.get("limit", 10))
    data = LineageStats.top_level(limit=limit)
    return JsonResponse(data, safe=False)


@endpoint_enabled('olympiad_ranking')
def olympiad_ranking(request):
    data = LineageStats.olympiad_ranking()
    return JsonResponse(data, safe=False)


@endpoint_enabled('olympiad_all_heroes')
def olympiad_all_heroes(request):
    data = LineageStats.olympiad_all_heroes()
    return JsonResponse(data, safe=False)


@endpoint_enabled('olympiad_current_heroes')
def olympiad_current_heroes(request):
    data = LineageStats.olympiad_current_heroes()
    return JsonResponse(data, safe=False)


@endpoint_enabled('grandboss_status')
def grandboss_status(request):
    data = LineageStats.grandboss_status()
    return JsonResponse(data, safe=False)


@endpoint_enabled('raidboss_status')
def raidboss_status(request):
    data = LineageStats.raidboss_status()
    return JsonResponse(data, safe=False)


@endpoint_enabled('siege')
def siege(request):
    data = LineageStats.siege()
    return JsonResponse(data, safe=False)


@endpoint_enabled('siege_participants')
def siege_participants(request, castle_id):
    data = LineageStats.siege_participants(castle_id=castle_id)
    return JsonResponse(data, safe=False)


@endpoint_enabled('boss_jewel_locations')
def boss_jewel_locations(request):
    jewel_ids = request.GET.get("ids", "")
    if not jewel_ids:
        return JsonResponse({"error": "Missing jewel item IDs"}, status=400)
    data = LineageStats.boss_jewel_locations(boss_jewel_ids=jewel_ids)
    return JsonResponse(data, safe=False)


@staff_member_required
@require_http_methods(["GET", "POST"])
def api_config_panel(request):
    toggle, _ = ApiEndpointToggle.objects.get_or_create(pk=1)

    # Campos que devem ser ignorados
    ignore_fields = {"id", "uuid", "created_at", "created_by", "updated_at", "updated_by"}

    # Campos booleanos que não estão na lista de ignorados
    fields = [
        field.name for field in ApiEndpointToggle._meta.fields
        if field.get_internal_type() == "BooleanField" and field.name not in ignore_fields
    ]

    if request.method == "POST":
        for field in fields:
            setattr(toggle, field, field in request.POST)
        toggle.save()
        return redirect("server:api_config_panel")

    context = {
        "toggle": toggle,
        "fields": fields,
    }
    return render(request, "pages/api_config_panel.html", context)
