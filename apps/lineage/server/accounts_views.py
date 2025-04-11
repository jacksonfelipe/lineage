from django.http import JsonResponse
from apps.lineage.server.querys.query_dreamv3 import LineageAccount
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .decorators import require_lineage_connection


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
def my_account(request):
    user = request.user.username
    result = LineageAccount.check_login_exists(user)

    if not result or not isinstance(result, list) or len(result) == 0:
        return JsonResponse({"error": "Conta não encontrada"}, status=404)

    account = result[0]  # acessa o primeiro item da lista

    return JsonResponse({
        "login": account['login'],
        "email": account['email'],
        "accessLevel": account['accessLevel'],
        "status": "Ativa" if int(account['accessLevel']) >= 0 else "Bloqueada"
    })


@login_required
@require_lineage_connection
def update_password(request):
    import json
    body = json.loads(request.body)
    password = body.get('password')
    user = request.user.username  # ou outro identificador

    if not password:
        return JsonResponse({"message": "Senha inválida"}, status=400)

    success = LineageAccount.update_password(password, user)
    if success:
        return JsonResponse({"message": "Senha atualizada com sucesso!"})
    return JsonResponse({"message": "Erro ao atualizar senha"}, status=500)


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
