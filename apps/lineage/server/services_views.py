from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _

from utils.dynamic_import import get_query_class  

LineageServices = get_query_class("LineageServices")


@login_required
def find_chars_view(request):
    if request.method == "POST":
        login = request.POST.get("login")
        characters = LineageServices.find_chars(login)
        return render(request, "server/account/find_chars.html", {"characters": characters, "login": login})
    return render(request, "server/account/find_chars.html")


@login_required
def check_char_page(request):
    if request.method == "POST":
        acc = request.POST.get("acc")
        cid = request.POST.get("cid")
        char = LineageServices.check_char(acc, cid)
        return render(request, "server/account/check_char.html", {"char": char})
    return render(request, "server/account/check_char.html")


@login_required
def check_name_exists_page(request):
    if request.method == "POST":
        name = request.POST.get("name")
        char = LineageServices.check_name_exists(name)
        return render(request, "server/account/check_name_exists.html", {"char": char, "name": name})
    return render(request, "server/account/check_name_exists.html")


@login_required
def change_nickname_view(request):
    if request.method == "POST":
        acc = request.POST.get("acc")
        cid = request.POST.get("cid")
        name = request.POST.get("name")
        result = LineageServices.change_nickname(acc, cid, name)
        if result:
            messages.success(request, _("Nickname alterado com sucesso!"))
        else:
            messages.error(request, _("Erro ao alterar nickname."))
        return redirect("server:change_nickname")
    return render(request, "server/account/change_nickname.html")


@login_required
def change_sex_view(request):
    if request.method == "POST":
        acc = request.POST.get("acc")
        cid = request.POST.get("cid")
        sex = request.POST.get("sex")
        result = LineageServices.change_sex(acc, cid, sex)
        if result:
            messages.success(request, _("Sexo alterado com sucesso!"))
        else:
            messages.error(request, _("Erro ao alterar sexo."))
        return redirect("server:change_sex")
    return render(request, "server/account/change_sex.html")


@login_required
def unstuck_view(request):
    if request.method == "POST":
        acc = request.POST.get("acc")
        cid = request.POST.get("cid")
        x = request.POST.get("x")
        y = request.POST.get("y")
        z = request.POST.get("z")
        result = LineageServices.unstuck(acc, cid, x, y, z)
        if result:
            messages.success(request, _("Personagem desbugado com sucesso!"))
        else:
            messages.error(request, _("Erro ao desbugar personagem."))
        return redirect("server:unstuck")
    return render(request, "server/account/unstuck.html")


@login_required
def delete_skills_view(request):
    if request.method == "POST":
        cid = request.POST.get("cid")
        result = LineageServices.delete_skills(cid)
        if result:
            messages.success(request, _("Skills removidas com sucesso!"))
        else:
            messages.error(request, _("Erro ao remover skills."))
        return redirect("server:delete_skills")
    return render(request, "server/account/delete_skills.html")


@login_required
def delete_skills_save_view(request):
    if request.method == "POST":
        cid = request.POST.get("cid")
        result = LineageServices.delete_skills_save(cid)
        if result:
            messages.success(request, _("Skills salvas removidas com sucesso!"))
        else:
            messages.error(request, _("Erro ao remover skills salvas."))
        return redirect("server:delete_skills_save")
    return render(request, "server/account/delete_skills_save.html")


@login_required
def delete_hennas_view(request):
    if request.method == "POST":
        cid = request.POST.get("cid")
        result = LineageServices.delete_hennas(cid)
        if result:
            messages.success(request, _("Henna removida com sucesso!"))
        else:
            messages.error(request, _("Erro ao remover henna."))
        return redirect("server:delete_hennas")
    return render(request, "server/account/delete_hennas.html")


@login_required
def delete_shortcuts_view(request):
    if request.method == "POST":
        cid = request.POST.get("cid")
        result = LineageServices.delete_shortcuts(cid)
        if result:
            messages.success(request, _("Atalhos removidos com sucesso!"))
        else:
            messages.error(request, _("Erro ao remover atalhos."))
        return redirect("server:delete_shortcuts")
    return render(request, "server/account/delete_shortcuts.html")


@login_required
def move_all_paperdoll_view(request):
    if request.method == "POST":
        cid = request.POST.get("cid")
        result = LineageServices.move_all_paperdoll(cid)
        if result:
            messages.success(request, _("Itens movidos para inventário com sucesso!"))
        else:
            messages.error(request, _("Erro ao mover itens."))
        return redirect("server:move_all_paperdoll")
    return render(request, "server/account/move_all_paperdoll.html")


@login_required
def add_skills_view(request):
    if request.method == "POST":
        cid = request.POST.get("cid")
        result = LineageServices.add_skills(cid)
        if result:
            messages.success(request, _("Skills adicionadas com sucesso!"))
        else:
            messages.error(request, _("Erro ao adicionar skills."))
        return redirect("server:add_skills")
    return render(request, "server/account/add_skills.html")


@login_required
def update_class_in_olympiad_view(request):
    if request.method == "POST":
        cid = request.POST.get("cid")
        result = LineageServices.update_class_in_olympiad(cid)
        if result:
            messages.success(request, _("Classe na Olympiad atualizada com sucesso!"))
        else:
            messages.error(request, _("Erro ao atualizar classe na Olympiad."))
        return redirect("server:update_class_in_olympiad")
    return render(request, "server/account/update_class_in_olympiad.html")


@login_required
def update_base_class_view(request):
    if request.method == "POST":
        cid = request.POST.get("cid")
        class_id = request.POST.get("class_id")
        result = LineageServices.update_base_class(cid, class_id)
        if result:
            messages.success(request, _("Classe base atualizada com sucesso!"))
        else:
            messages.error(request, _("Erro ao atualizar classe base."))
        return redirect("server:update_base_class")
    return render(request, "server/account/update_base_class.html")


@login_required
def check_has_class_in_sub_view(request):
    if request.method == "POST":
        cid = request.POST.get("cid")
        class_id = request.POST.get("class_id")
        result = LineageServices.check_has_class_in_sub(cid, class_id)
        context = {"has_class": result, "cid": cid, "class_id": class_id}
        return render(request, "server/account/check_has_class_in_sub.html", context)
    return render(request, "server/account/check_has_class_in_sub.html")
