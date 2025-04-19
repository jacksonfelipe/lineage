from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .decorators import require_lineage_connection
from datetime import datetime
from django.utils.timezone import make_aware
from django.utils.timezone import now
from utils.resources import gen_avatar, get_class_name

from utils.dynamic_import import get_query_class  # importa o helper
LineageAccount = get_query_class("LineageAccount")  # carrega a classe certa com base no .env
LineageServices = get_query_class("LineageServices")


@login_required
@require_lineage_connection  # Assumindo que você tem um decorator para verificar a conexão
def account_dashboard(request):
    user_login = request.user.username
    account_data = LineageAccount.check_login_exists(user_login)

    if not account_data or len(account_data) == 0:
        return redirect('server:lineage_register')

    try:
        personagens = LineageServices.find_chars(user_login)
    except Exception as e:
        personagens = []
        messages.warning(request, 'Não foi possível carregar seus personagens agora.')

    account = account_data[0]
    account['status'] = "Ativa" if int(account['accessLevel']) >= 0 else "Bloqueada"

    # Formata data de criação
    created_time = None
    if account.get('created_time'):
        try:
            created_time = make_aware(datetime.strptime(account['created_time'], '%Y-%m-%d %H:%M:%S'))
        except:
            try:
                created_time = make_aware(datetime.fromtimestamp(int(account['created_time'])))
            except:
                created_time = None

    # Status dos personagens
    char_list = []
    for char in personagens:

        # Verificando se o campo 'level' existe antes de acessá-lo
        level = char.get('base_level', '-')

        char_list.append({
            'id': char['obj_Id'],
            'nome': char['char_name'],
            'title': char.get('title', '-'),
            'lastAccess': datetime.fromtimestamp(int(char['lastAccess']) / 1000).strftime('%B %d, %Y às %H:%M') if char.get('lastAccess') else '-',
            'online': 'Online' if char.get('online') else 'Offline',
            'base_class': get_class_name(char['base_class']),
            'subclass1': get_class_name(char['subclass1']) if char.get('subclass1') else '-',
            'subclass2': get_class_name(char['subclass2']) if char.get('subclass2') else '-',
            'subclass3': get_class_name(char['subclass3']) if char.get('subclass3') else '-',
            'level': level,
            'sex': 'Feminino' if char['sex'] else 'Masculino',
            'pvp': char['pvpkills'],
            'pk': char['pkkills'],
            'karma': char['karma'],
            'clan': char.get('clan_name', '-'),
            'ally': char.get('ally_name', '-'),
            'nobless': 'Sim' if char.get('nobless') else 'Não',
            'hero': 'Sim' if char.get('hero_end') and int(char['hero_end']) > int(now().timestamp() * 1000) else 'Não',
            'avatar': gen_avatar(char['base_class'], char['sex'])
        })

    context = {
        'account': account,
        'created_time': created_time.strftime('%B %d, %Y às %H:%M') if created_time else '-',
        'lastIP': account.get('lastIP', '-'),
        'char_count': account.get('chars', 0),
        'characters': char_list,
        'char_count': len(char_list)
    }

    return render(request, 'l2_accounts/dashboard.html', context)


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
