from django.http import JsonResponse
from .querys.query_dreamv3 import LineageStats
from .decorators import endpoint_enabled, safe_json_response
from django.shortcuts import render, redirect
from .models import ApiEndpointToggle
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required


@endpoint_enabled('players_online')
@safe_json_response
def players_online(request):
    return LineageStats.players_online()


@endpoint_enabled('top_pvp')
@safe_json_response
def top_pvp(request):
    limit = int(request.GET.get("limit", 10))
    return LineageStats.top_pvp(limit=limit)


@endpoint_enabled('top_pk')
@safe_json_response
def top_pk(request):
    limit = int(request.GET.get("limit", 10))
    return LineageStats.top_pk(limit=limit)


@endpoint_enabled('top_clan')
@safe_json_response
def top_clan(request):
    limit = int(request.GET.get("limit", 10))
    return LineageStats.top_clans(limit=limit)


@endpoint_enabled('top_rich')
@safe_json_response
def top_rich(request):
    limit = int(request.GET.get("limit", 10))
    return LineageStats.top_adena(limit=limit)


@endpoint_enabled('top_online')
@safe_json_response
def top_online(request):
    limit = int(request.GET.get("limit", 10))
    return LineageStats.top_online(limit=limit)


@endpoint_enabled('top_level')
@safe_json_response
def top_level(request):
    limit = int(request.GET.get("limit", 10))
    return LineageStats.top_level(limit=limit)


@endpoint_enabled('olympiad_ranking')
@safe_json_response
def olympiad_ranking(request):
    return LineageStats.olympiad_ranking()


@endpoint_enabled('olympiad_all_heroes')
@safe_json_response
def olympiad_all_heroes(request):
    return LineageStats.olympiad_all_heroes()


@endpoint_enabled('olympiad_current_heroes')
@safe_json_response
def olympiad_current_heroes(request):
    return LineageStats.olympiad_current_heroes()


@endpoint_enabled('grandboss_status')
@safe_json_response
def grandboss_status(request):
    return LineageStats.grandboss_status()


@endpoint_enabled('raidboss_status')
@safe_json_response
def raidboss_status(request):
    return LineageStats.raidboss_status()


@endpoint_enabled('siege')
@safe_json_response
def siege(request):
    return LineageStats.siege()


@endpoint_enabled('siege_participants')
@safe_json_response
def siege_participants(request, castle_id):
    if castle_id not in range(1, 10):
        return JsonResponse({'error': 'castle_id deve ser um valor entre 1 e 9'}, status=400)
    return LineageStats.siege_participants(castle_id=castle_id)


@endpoint_enabled('boss_jewel_locations')
@safe_json_response
def boss_jewel_locations(request):
    jewel_ids = request.GET.get("ids", "")
    
    if not jewel_ids:
        return JsonResponse({"error": "Missing jewel item IDs"}, status=400)
    
    try:
        jewel_ids_list = [int(id) for id in jewel_ids.split(',')]
    except ValueError:
        return JsonResponse({"error": "Invalid ID format"}, status=400)
    
    allowed_ids = [6656, 6657, 6658, 6659, 6660, 6661, 8191]
    if not all(id in allowed_ids for id in jewel_ids_list):
        return JsonResponse({"error": "Invalid jewel item ID(s)"}, status=400)
    
    return LineageStats.boss_jewel_locations(boss_jewel_ids=jewel_ids_list)


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
