from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from apps.lineage.server.querys.query_dreamv3 import LineageAccount
from apps.lineage.server.database import LineageDB
from django.shortcuts import render


def lienage_database_is_connected():
    # Verifica conexão com banco do Lineage
    db = LineageDB()
    if not db.is_connected():
        return False
    return True


def account_dashboard(request):
    user_login = request.user.username
    account_data = LineageAccount.check_login_exists(user_login)

    if account_data and isinstance(account_data, list) and len(account_data) > 0:
        account_data = account_data[0]
        account_data['status'] = "Ativa" if int(account_data['accessLevel']) >= 0 else "Bloqueada"
    else:
        account_data = None

    return render(request, 'l2_accounts/dashboard.html', {
        'account': account_data,
    })


@csrf_exempt
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


@csrf_exempt
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
