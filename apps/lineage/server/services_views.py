from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _

from utils.dynamic_import import get_query_class  

LineageServices = get_query_class("LineageServices")


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
    return render(request, "services/change_nickname.html")


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
    return render(request, "services/change_sex.html")


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
    return render(request, "services/unstuck.html")
