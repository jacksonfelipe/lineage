from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from utils.dynamic_import import get_query_class  

LineageServices = get_query_class("LineageServices")

@login_required
def check_char_view(request, acc, cid):
    char = LineageServices.check_char(acc, cid)
    return JsonResponse({"char": char})

@login_required
def check_name_exists_view(request):
    name = request.GET.get("name")
    if not name:
        return JsonResponse({"error": "Missing name parameter."}, status=400)
    exists = LineageServices.check_name_exists(name)
    return JsonResponse({"exists": bool(exists)})

@login_required
def change_nickname_api(request):
    if request.method == "POST":
        acc = request.POST.get("acc")
        cid = request.POST.get("cid")
        name = request.POST.get("name")
        result = LineageServices.change_nickname(acc, cid, name)
        return JsonResponse({"success": bool(result)})

@login_required
def change_sex_api(request):
    if request.method == "POST":
        acc = request.POST.get("acc")
        cid = request.POST.get("cid")
        sex = request.POST.get("sex")
        result = LineageServices.change_sex(acc, cid, sex)
        return JsonResponse({"success": bool(result)})

@login_required
def unstuck_api(request):
    if request.method == "POST":
        acc = request.POST.get("acc")
        cid = request.POST.get("cid")
        x, y, z = request.POST.get("x"), request.POST.get("y"), request.POST.get("z")
        result = LineageServices.unstuck(acc, cid, x, y, z)
        return JsonResponse({"success": bool(result)})

@login_required
def delete_skills_api(request, cid):
    result = LineageServices.delete_skills(cid)
    return JsonResponse({"success": bool(result)})

@login_required
def delete_skills_save_api(request, cid):
    result = LineageServices.delete_skills_save(cid)
    return JsonResponse({"success": bool(result)})

@login_required
def delete_hennas_api(request, cid):
    result = LineageServices.delete_hennas(cid)
    return JsonResponse({"success": bool(result)})

@login_required
def delete_shortcuts_api(request, cid):
    result = LineageServices.delete_shortcuts(cid)
    return JsonResponse({"success": bool(result)})

@login_required
def move_all_paperdoll_api(request, cid):
    result = LineageServices.move_all_paperdoll(cid)
    return JsonResponse({"success": bool(result)})

@login_required
def add_skills_api(request):
    if request.method == "POST":
        new_skills_values = request.POST.get("new_skills_values")
        result = LineageServices.add_skills(new_skills_values)
        return JsonResponse({"success": bool(result)})

@login_required
def update_class_in_olympiad_api(request):
    if request.method == "POST":
        char_class = request.POST.get("char_class")
        cid = request.POST.get("cid")
        result = LineageServices.update_class_in_olympiad(char_class, cid)
        return JsonResponse({"success": bool(result)})

@login_required
def update_base_class_api(request):
    if request.method == "POST":
        char_class = request.POST.get("char_class")
        cid = request.POST.get("cid")
        lvl = int(request.POST.get("lvl", 78))
        exp = int(request.POST.get("exp", 1511275834))
        race = request.POST.get("race", 'NONE')
        result = LineageServices.update_base_class(char_class, cid, lvl, exp, race)
        return JsonResponse({"success": bool(result)})

@login_required
def check_has_class_in_sub_api(request):
    cid = request.GET.get("cid")
    classes = request.GET.getlist("classes")
    result = LineageServices.check_has_class_in_sub(cid, classes)
    return JsonResponse({"has_class": bool(result)})
