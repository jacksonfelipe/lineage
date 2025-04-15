from .models import *
import requests
import json
import os
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.conf import settings
from django.utils.translation import get_language

from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView, PasswordResetConfirmView
from .forms import UserProfileForm, AddressUserForm, RegistrationForm, LoginForm, UserPasswordResetForm, UserPasswordChangeForm, UserSetPasswordForm

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth import logout
from utils.notifications import send_notification

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.core.mail import send_mail
from django.contrib import messages
from django.utils.translation import activate
from django.http import HttpResponseRedirect

from apps.lineage.server.models import IndexConfig

from utils.dynamic_import import get_query_class  # importa o helper
LineageStats = get_query_class("LineageStats")  # carrega a classe certa com base no .env


with open('utils/data/index.json', 'r', encoding='utf-8') as file:
        data_index = json.load(file)


def verificar_hcaptcha(token):
    secret = settings.HCAPTCHA_SECRET_KEY
    data = {
        'response': token,
        'secret': secret,
    }
    r = requests.post('https://hcaptcha.com/siteverify', data=data)
    return r.json().get('success', False)


def index(request):
    clanes = LineageStats.top_clans(limit=10) or []
    online = LineageStats.players_online() or []
    config = IndexConfig.objects.first()

    online_count = online[0]['quant'] if online and isinstance(online, list) and 'quant' in online[0] else 0
    current_lang = get_language()

    # Pega a tradução configurada
    translation = None
    if config:
        translation = config.translations.filter(language=current_lang).first()

    # Caso não exista o registro de configuração ou tradução, usa valores padrões
    nome_servidor = "Lineage 2 PDL"  # Valor padrão
    descricao_servidor = "Onde Lendas Nascem, Heróis Lutam e a Glória É Eterna."  # Valor padrão
    jogadores_online_texto = "Jogadores online Agora"  # Valor padrão

    if config:
        # Verifica se a tradução existe, senão usa os valores do config
        nome_servidor = translation.nome_servidor if translation else config.nome_servidor
        descricao_servidor = translation.descricao_servidor if translation else config.descricao_servidor
        jogadores_online_texto = translation.jogadores_online_texto if translation else config.jogadores_online_texto

    # Classes info (ajustando a descrição conforme a linguagem)
    classes_info = []
    for c in data_index.get('classes', []):
        descricao = c['descricao'].get(current_lang, c['descricao'].get('pt'))  # fallback para 'pt'
        classes_info.append({
            'name': c['name'],
            'descricao': descricao
        })

    return render(request, 'pages/index.html', {
        'clanes': clanes,
        'classes_info': classes_info,
        'online': online_count,
        'configuracao': config,
        'nome_servidor': nome_servidor,
        'descricao_servidor': descricao_servidor,
        'jogadores_online_texto': jogadores_online_texto
    })


def custom_400_view(request, exception):
    return render(request, 'errors/400.html', status=400)


def custom_404_view(request, exception):
    return render(request, 'errors/404.html', status=404)


def custom_500_view(request):
    return render(request, 'errors/500.html', status=500)


@login_required
def profile(request):
    context = {
        'segment': 'profile',
        'parent': 'home',
    }
    return render(request, 'pages/profile.html', context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirecione para a página de perfil do usuário
    else:
        form = UserProfileForm(instance=request.user)
    context = {
        'segment': 'edit-profile',
        'parent': 'home',
        'form': form
    }
    return render(request, 'pages/edit_profile.html', context)


@login_required
def add_or_edit_address(request):
    # Verifica se o usuário já tem um endereço
    address = AddressUser.objects.filter(user=request.user).first()

    if request.method == 'POST':
        form = AddressUserForm(request.POST, instance=address)
        if form.is_valid():
            new_address = form.save(commit=False)
            new_address.user = request.user
            new_address.save()
            return redirect('profile')  # Redireciona para a página de perfil
    else:
        form = AddressUserForm(instance=address)

    context = {
        'segment': 'address',
        'parent': 'home',
        'form': form
    }

    return render(request, 'pages/address_form.html', context)


def empty_view(request):
    return HttpResponse(status=404)


@staff_member_required
def log_info_dashboard(request):
    log_file_path = 'logs/info.log'  # Caminho para o arquivo de log
    logs_per_page = 20  # Quantidade de logs por página

    try:
        with open(log_file_path, 'r') as log_file:
            logs = log_file.readlines()
    except FileNotFoundError:
        logs = ['Arquivo de log não encontrado. Verifique a configuração.']

    paginator = Paginator(logs, logs_per_page)
    page_number = request.GET.get('page')
    page_logs = paginator.get_page(page_number)
    context = {
        'segment': 'logs',
        'parent': 'system',
        'page_logs': page_logs
    }

    return render(request, 'pages/logs.html', context)

@staff_member_required
def log_error_dashboard(request):
    log_file_path = 'logs/error.log'  # Caminho para o arquivo de log
    logs_per_page = 20  # Quantidade de logs por página

    try:
        with open(log_file_path, 'r') as log_file:
            logs = log_file.readlines()
    except FileNotFoundError:
        logs = ['Arquivo de log não encontrado. Verifique a configuração.']

    paginator = Paginator(logs, logs_per_page)
    page_number = request.GET.get('page')
    page_logs = paginator.get_page(page_number)
    context = {
        'segment': 'logs',
        'parent': 'system',
        'page_logs': page_logs
    }

    return render(request, 'pages/logs.html', context)


def logout_view(request):
  logout(request)
  return redirect('/')


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        hcaptcha_token = request.POST.get('h-captcha-response')
        hcaptcha_ok = verificar_hcaptcha(hcaptcha_token)

        # Verifica termos + captcha + formulário
        if not request.POST.get('terms'):
            form.add_error(None, 'Você precisa aceitar os termos e condições para se registrar.')

        elif not hcaptcha_ok:
            form.add_error(None, 'Verificação do hCaptcha falhou. Tente novamente.')

        elif form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.is_verified = False
            user.save()

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            verification_link = request.build_absolute_uri(
                reverse('verificar_email', args=[uid, token])
            )

            send_mail(
                subject='Verifique seu e-mail',
                message=f'Olá {user.username}, clique no link para verificar sua conta: {verification_link}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

            send_notification(
                user=None,
                notification_type='staff',
                message=f'Usuário {user.username} de email {user.email} cadastrado com sucesso!',
                created_by=None
            )

            return redirect('/accounts/login/')
        else:
            print("Registration failed!")
    else:
        form = RegistrationForm()

    context = {'form': form, 'hcaptcha_site_key': settings.HCAPTCHA_SITE_KEY}
    return render(request, 'accounts_custom/sign-up.html', context)


class UserLoginView(LoginView):
    form_class = LoginForm
    template_name = 'accounts_custom/sign-in.html'

    def form_valid(self, form):
        print("Login successful!")
        return super().form_valid(form)

    def form_invalid(self, form):
        print("Login failed!")
        return super().form_invalid(form)
    

class UserPasswordChangeView(PasswordChangeView):
    template_name = 'accounts_custom/password-change.html'
    form_class = UserPasswordChangeForm

    def form_valid(self, form):
        print("Password changed successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        print("Password change failed!")
        return super().form_invalid(form)
    

class UserPasswordResetView(PasswordResetView):
    template_name = 'accounts_custom/forgot-password.html'
    form_class = UserPasswordResetForm

    def form_valid(self, form):
        print("Password reset email sent!")
        return super().form_valid(form)

    def form_invalid(self, form):
        print("Failed to send password reset email!")
        return super().form_invalid(form)
    

class UserPasswrodResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts_custom/reset-password.html'
    form_class = UserSetPasswordForm

    def form_valid(self, form):
        print("Password has been reset!")
        return super().form_valid(form)

    def form_invalid(self, form):
        print("Password reset failed!")
        return super().form_invalid(form)
    

def lock(request):
    return render(request, 'accounts_custom/lock.html')


@login_required
def dashboard(request):
    if request.user.is_authenticated:
        context = {
            'segment': 'dashboard'
        }
        return render(request, 'dashboard_custom/dashboard.html', context)
    else:
        return redirect('/')


def terms_view(request):
    return render(request, "pages/terms.html", {
        "server_name": "PDL",  # ou qualquer nome que quiser
        "last_updated": datetime.today().strftime("%d/%m/%Y"),
    })


def verificar_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_verified = True
        user.save(update_fields=['is_verified'])
        return render(request, 'verify/email_verificado.html')
    return render(request, 'verify/email_verificado.html', {'erro': True})


@login_required
def reenviar_verificacao_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)

            if user.is_verified:
                messages.info(request, 'Sua conta já está verificada.')
                return redirect('login')

            # Gera novo link
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            verification_link = request.build_absolute_uri(
                reverse('verificar_email', args=[uid, token])
            )

            # Envia o e-mail
            if getattr(settings, 'CONFIG_EMAIL_ENABLE', False):
                send_mail(
                    subject='Reenvio de verificação de e-mail',
                    message=(
                        f'Olá {user.username},\n\n'
                        f'Aqui está seu novo link de verificação:\n\n{verification_link}\n\n'
                        'Se você não solicitou isso, ignore este e-mail.'
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )

                messages.success(request, 'Um novo e-mail de verificação foi enviado.')
            else:
                messages.error(request, 'O envio de e-mail está desativado no momento.')

            return redirect('login')

        except User.DoesNotExist:
            messages.error(request, 'Nenhuma conta foi encontrada com este e-mail.')

    return render(request, 'accounts_custom/reenviar_verificacao.html')


@login_required
def custom_set_language(request):
    if request.method == 'POST':
        lang_code = request.POST.get('language')
        next_url = request.POST.get('next', '/')
        
        if lang_code:
            response = HttpResponseRedirect(next_url)
            response.set_cookie('django_language', lang_code)
            activate(lang_code)
            return response

    return redirect('/')
