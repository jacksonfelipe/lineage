from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils.translation import gettext as _
from apps.lineage.wallet.models import Wallet
from apps.lineage.wallet.signals import aplicar_transacao
from .models import ServicePrice

from utils.dynamic_import import get_query_class  
LineageServices = get_query_class("LineageServices")


@login_required
def change_nickname_view(request, char_id):
    try:
        price = ServicePrice.objects.get(servico='CHANGE_NICKNAME').preco
    except ServicePrice.DoesNotExist:
        messages.error(request, _("Preço do serviço não configurado."))
        return redirect("server:account_dashboard")  # Redireciona para a página de dashboard se o preço não estiver configurado
    
    if request.method == "POST":
        acc = request.user.username
        cid = char_id
        name = request.POST.get("name")

        wallet = Wallet.objects.get(usuario=request.user)

        if wallet.saldo < price:
            messages.error(request, _("Saldo insuficiente na carteira."))
            return redirect("server:change_nickname", char_id=char_id)

        result = LineageServices.change_nickname(acc, cid, name)

        if result:
            aplicar_transacao(wallet, "SAIDA", price, descricao="Alteração de Nickname")
            messages.success(request, _("Nickname alterado com sucesso!"))
            return redirect("server:account_dashboard")
        else:
            messages.error(request, _("Erro ao alterar nickname."))

    context = {
        'char_id': char_id,
        'price': price  # Isso agora só será acessado se o serviço estiver configurado
    }
    return render(request, "services/change_nickname.html", context)


@login_required
def change_sex_view(request, char_id):
    try:
        price = ServicePrice.objects.get(servico='CHANGE_SEX').preco
    except ServicePrice.DoesNotExist:
        messages.error(request, _("Preço do serviço não configurado."))
        return redirect("server:account_dashboard")  # Redireciona para outra página
    
    if request.method == "POST":
        acc = request.user.username
        cid = char_id
        sex = request.POST.get("sex")

        wallet = Wallet.objects.get(usuario=request.user)

        if wallet.saldo < price:
            messages.error(request, _("Saldo insuficiente na carteira."))
            return redirect("server:change_sex", char_id=char_id)

        result = LineageServices.change_sex(acc, cid, sex)

        if result:
            aplicar_transacao(wallet, "SAIDA", price, descricao="Alteração de Sexo")
            messages.success(request, _("Sexo alterado com sucesso!"))
            return redirect("server:account_dashboard")
        else:
            messages.error(request, _("Erro ao alterar sexo."))

    context = {
        'char_id': char_id,
        'price': price  # Isso agora só será acessado se o serviço estiver configurado
    }
    return render(request, "services/change_sex.html", context)


@login_required
def unstuck_view(request, char_id):
    if request.method == "POST":
        acc = request.user.username
        cid = char_id
        # posições fixas
        spawn_x = 149999
        spawn_y = 46728
        spawn_z = -3414
        result = LineageServices.unstuck(acc, cid, spawn_x, spawn_y, spawn_z)
        if result:
            messages.success(request, _("Personagem desbugado com sucesso!"))
            return redirect("server:account_dashboard")
        else:
            messages.error(request, _("Erro ao desbugar personagem."))
            return redirect("server:unstuck", char_id=char_id)

    context = {
        'char_id': char_id
    }
    return render(request, "services/unstuck.html", context)


@staff_member_required
def configure_service_prices(request):
    if request.method == "POST":
        # Recuperando ou criando entradas para os serviços
        try:
            change_nickname_price = request.POST.get("change_nickname_price")
            change_sex_price = request.POST.get("change_sex_price")

            # Validação básica para garantir que os valores sejam numéricos
            if not change_nickname_price.isnumeric() or not change_sex_price.isnumeric():
                messages.error(request, _("Os preços precisam ser valores numéricos."))
                return redirect("server:configure_service_prices")

            # Configurando ou atualizando os preços
            ServicePrice.objects.update_or_create(
                servico='CHANGE_NICKNAME',
                defaults={'preco': float(change_nickname_price)}
            )
            ServicePrice.objects.update_or_create(
                servico='CHANGE_SEX',
                defaults={'preco': float(change_sex_price)}
            )

            messages.success(request, _("Preços dos serviços atualizados com sucesso!"))
            return redirect("server:configure_service_prices")
        except Exception as e:
            messages.error(request, _("Erro ao configurar os preços: ") + str(e))
            return redirect("server:configure_service_prices")
    
    # Pegando os preços atuais para exibir no formulário
    try:
        change_nickname_price = ServicePrice.objects.get(servico='CHANGE_NICKNAME').preco
        change_sex_price = ServicePrice.objects.get(servico='CHANGE_SEX').preco
    except ServicePrice.DoesNotExist:
        change_nickname_price = 0
        change_sex_price = 0

    context = {
        'change_nickname_price': change_nickname_price,
        'change_sex_price': change_sex_price,
    }

    return render(request, "services/configure_service_prices.html", context)
