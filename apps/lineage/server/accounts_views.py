from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .decorators import require_lineage_connection

from utils.dynamic_import import get_query_class  # importa o helper
LineageAccount = get_query_class("LineageAccount")  # carrega a classe certa com base no .env


@login_required
@require_lineage_connection
def account_dashboard(request):
    user_login = request.user.username
    account_data = LineageAccount.check_login_exists(user_login)

    if not account_data or len(account_data) == 0:
        return redirect('server:lineage_register')  # url que vamos criar abaixo

    account_data = account_data[0]
    account_data['status'] = "Ativa" if int(account_data['accessLevel']) >= 0 else "Bloqueada"

    return render(request, 'l2_accounts/dashboard.html', {
        'account': account_data,
    })


@login_required
@require_lineage_connection
def update_password(request):
    if request.method == "POST":
        senha = request.POST.get("nova_senha")
        confirmar = request.POST.get("confirmar_senha")
        user = request.user.username

        if not senha or not confirmar:
            messages.error(request, "Por favor, preencha todos os campos.")
            return redirect('server:update_password')

        if senha != confirmar:
            messages.error(request, "As senhas não coincidem.")
            return redirect('server:update_password')

        success = LineageAccount.update_password(senha, user)

        if success:
            messages.success(request, "Senha atualizada com sucesso!")
            return redirect('server:account_dashboard')
        else:
            messages.error(request, "Erro ao atualizar senha.")
            return redirect('server:update_password')

    # GET request — exibe o formulário
    return render(request, "l2_accounts/update_password.html")


@login_required
@require_lineage_connection
def register_lineage_account(request):
    user = request.user

    # Verifica se a conta já existe
    existing_account = LineageAccount.check_login_exists(user.username)
    if existing_account and len(existing_account) > 0:
        messages.info(request, "Sua conta Lineage já está criada.")
        return redirect('server:account_dashboard')

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm = request.POST.get('confirm')

        if password != confirm:
            messages.error(request, "As senhas não coincidem.")
            return redirect('server:lineage_register')

        success = LineageAccount.register(
            login=user.username,
            password=password,
            access_level=0,
            email=user.email
        )

        if success:
            messages.success(request, "Conta Lineage criada com sucesso!")
            return redirect('server:account_dashboard')
        else:
            messages.error(request, "Erro ao criar conta.")
            return redirect('server:lineage_register')

    return render(request, 'l2_accounts/register.html', {
        'login': user.username,
        'email': user.email
    })
