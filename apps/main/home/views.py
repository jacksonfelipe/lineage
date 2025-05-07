from .models import *
import requests
import json
import base64
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.conf import settings
from django.utils.translation import get_language

from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView, PasswordResetConfirmView
from .forms import (UserProfileForm, AddressUserForm, RegistrationForm, LoginForm, 
                    UserPasswordResetForm, UserPasswordChangeForm, UserSetPasswordForm, AvatarForm)

from django.shortcuts import render, redirect
from apps.main.home.decorator import conditional_otp_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth import logout
from utils.notifications import send_notification
import logging

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.core.mail import send_mail
from django.contrib import messages
from django.utils.translation import activate
from django.http import HttpResponseRedirect
from utils.crests import CrestHandler

from apps.lineage.server.models import IndexConfig, Apoiador
from django.utils import translation
from utils.render_theme_page import render_theme_page

from apps.lineage.wallet.models import Wallet
from apps.lineage.inventory.models import Inventory
from apps.lineage.auction.models import Auction

from django.contrib.auth import get_user_model
from django.contrib.auth import login

from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp import login as otp_login

import pyotp
from .resource.twofa import gerar_qr_png
from .utils import verificar_conquistas

from utils.dynamic_import import get_query_class  # importa o helper
LineageStats = get_query_class("LineageStats")  # carrega a classe certa com base no .env


logger = logging.getLogger(__name__)


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
    # Pega os clãs mais bem posicionados
    clanes = LineageStats.top_clans(limit=10) or []

    # Pega os IDs dos clãs para pegar os crests
    clan_ids = [clan.get('clan_id') for clan in clanes if 'clan_id' in clan]
    ally_ids = [clan.get('ally_id') for clan in clanes if 'ally_id' in clan]

    # Pega as crests para os clãs
    crests = LineageStats.get_crests(clan_ids) or {}
    ally_crests = LineageStats.get_crests(ally_ids, type='ally') or {}

    # Processa as imagens dos crests
    crest_handler = CrestHandler()

    for clan in clanes:
        crest_id = clan.get('clan_id')

        # Verifique se o crest existe
        # Ajusta a forma de acessar o crest
        crest_blob = None
        for crest in crests:
            if crest.get('clan_id') == crest_id:
                crest_blob = crest.get('crest')
                break

        # Para o caso do clã ter um crest
        if crest_blob:
            # Cria a imagem do crest do clã e converte para base64
            image_bytes = crest_handler.make_image(crest_blob, crest_id, 'clan', show_image=True)

            # Rewind the BytesIO to the beginning before encoding
            image_bytes.seek(0)  # Coloca o ponteiro de volta ao início
            crest_image_base64 = base64.b64encode(image_bytes.read()).decode('utf-8')
            clan['clan_crest_image_base64'] = crest_image_base64
        else:
            # Caso não haja crest do clã, cria uma imagem vazia
            empty_image_bytes = crest_handler.make_empty_image('clan')

            # Rewind the BytesIO to the beginning before encoding
            empty_image_bytes.seek(0)  # Coloca o ponteiro de volta ao início
            crest_image_base64 = base64.b64encode(empty_image_bytes.read()).decode('utf-8')
            clan['clan_crest_image_base64'] = crest_image_base64

        # Se houver ally_id, processa a imagem da aliança também
        ally_crest_blob = None
        if clan.get('ally_id'):
            for crest in ally_crests:
                if crest.get('ally_id') == clan.get('ally_id'):
                    ally_crest_blob = crest.get('crest')
                    break

            if ally_crest_blob:
                # Cria a imagem do crest da aliança e converte para base64
                ally_image_bytes = crest_handler.make_image(ally_crest_blob, crest_id, 'ally', show_image=True)

                # Rewind the BytesIO to the beginning before encoding
                ally_image_bytes.seek(0)  # Coloca o ponteiro de volta ao início
                ally_crest_image_base64 = base64.b64encode(ally_image_bytes.read()).decode('utf-8')
                clan['ally_crest_image_base64'] = ally_crest_image_base64
            else:
                # Caso não haja crest da aliança, cria uma imagem vazia
                empty_ally_image_bytes = crest_handler.make_empty_image('ally')

                # Rewind the BytesIO to the beginning before encoding
                empty_ally_image_bytes.seek(0)  # Coloca o ponteiro de volta ao início
                ally_crest_image_base64 = base64.b64encode(empty_ally_image_bytes.read()).decode('utf-8')
                clan['ally_crest_image_base64'] = ally_crest_image_base64

    # Pega os jogadores online
    online = LineageStats.players_online() or []

    # Pega a configuração do índice (ex: nome do servidor)
    config = IndexConfig.objects.first()

    # Contagem de jogadores online
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

    # Buscar apoiadores ativos e aprovados
    apoiadores = Apoiador.objects.filter(ativo=True, status='aprovado')

    context = {
        'clanes': clanes,  # Passando os clãs com as imagens de crest
        'classes_info': classes_info,
        'online': online_count,
        'configuracao': config,
        'nome_servidor': nome_servidor,
        'descricao_servidor': descricao_servidor,
        'jogadores_online_texto': jogadores_online_texto,
        'apoiadores': apoiadores,
    }

    return render_theme_page(request, 'public', 'index.html', context)


def custom_400_view(request, exception):
    return render(request, 'errors/400.html', status=400)


def custom_404_view(request, exception):
    return render(request, 'errors/404.html', status=404)


def custom_500_view(request):
    return render(request, 'errors/500.html', status=500)


@conditional_otp_required
def profile(request):
    context = {
        'segment': 'profile',
        'parent': 'home',
    }
    return render(request, 'pages/profile.html', context)


@conditional_otp_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redireciona para a página de perfil do usuário
    else:
        form = UserProfileForm(instance=request.user)
    
    context = {
        'segment': 'edit-profile',
        'parent': 'home',
        'form': form
    }
    
    return render(request, 'pages/edit_profile.html', context)


@conditional_otp_required
def edit_avatar(request):
    if request.method == 'POST' and request.FILES.get('avatar'):
        form = AvatarForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()

            # Adiciona XP ao perfil
            perfil = PerfilGamer.objects.get(user=request.user)
            perfil.adicionar_xp(20)  # Pode ajustar a quantidade conforme desejar

            # Verifica conquistas
            conquistas_desbloqueadas = verificar_conquistas(request)
            if conquistas_desbloqueadas:
                for conquista in conquistas_desbloqueadas:
                    messages.success(request, f"🏆 Você desbloqueou a conquista: {conquista.nome}!")

            messages.success(request, "Avatar atualizado com sucesso! Você ganhou 20 XP.")
            return redirect('profile')
    else:
        form = AvatarForm(instance=request.user)

    return render(request, 'pages/edit_avatar.html', {'form': form})


@conditional_otp_required
def add_or_edit_address(request):
    # Verifica se o usuário já tem um endereço
    address = AddressUser.objects.filter(user=request.user).first()

    if request.method == 'POST':
        form = AddressUserForm(request.POST, instance=address)
        if form.is_valid():
            new_address = form.save(commit=False)
            new_address.user = request.user
            new_address.save()

            # Dá XP por cadastrar ou atualizar o endereço
            perfil = PerfilGamer.objects.get(user=request.user)
            perfil.adicionar_xp(30)  # Altere o valor conforme achar adequado

            # Verifica conquistas
            conquistas_desbloqueadas = verificar_conquistas(request)
            if conquistas_desbloqueadas:
                for conquista in conquistas_desbloqueadas:
                    messages.success(request, f"🏆 Conquista desbloqueada: {conquista.nome}!")

            messages.success(request, "Endereço salvo com sucesso! Você ganhou 30 XP.")
            return redirect('profile')
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
            user.save()

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            verification_link = request.build_absolute_uri(
                reverse('verificar_email', args=[uid, token])
            )

            try:
                send_mail(
                    subject='Verifique seu e-mail',
                    message=f'Olá {user.username}, clique no link para verificar sua conta: {verification_link}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            except Exception as e:
                logger.error(f"Erro ao enviar email: {str(e)}")

            try:
                send_notification(
                    user=None,
                    notification_type='staff',
                    message=f'Usuário {user.username} de email {user.email} cadastrado com sucesso!',
                    created_by=None
                )
            except Exception as e:
                logger.error(f"Erro ao criar notificação: {str(e)}")

            return redirect('registration_success')
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
        user = form.get_user()

        # Verifica se o usuário tem 2FA configurado
        totp_device = TOTPDevice.objects.filter(user=user, confirmed=True).first()

        if totp_device:
            # Salva o user_id temporariamente na sessão para validar o TOTP depois
            self.request.session['pre_2fa_user_id'] = user.pk
            # Salva o estado da requisição para processar a verificação do OTP
            return redirect('verify_2fa')  # Redireciona para a view de verificação do token

        # Se não tiver 2FA configurado, faz o login normalmente
        login(self.request, user)
        return redirect(self.get_success_url())
       

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
        # Apenas atualiza a senha sem mexer em outros campos do modelo
        form.user.set_password(form.cleaned_data['new_password1'])
        form.user.save(update_fields=["password"])  # Evita save completo que pode tentar mexer no avatar
        print("Password has been reset!")
        return super(PasswordResetConfirmView, self).form_valid(form)

    def form_invalid(self, form):
        print("Password reset failed!")
        return super().form_invalid(form)
    

def lock(request):
    return render(request, 'accounts_custom/lock.html')


@conditional_otp_required
def dashboard(request):
    if request.user.is_authenticated:
        language = translation.get_language()
        dashboard = DashboardContent.objects.filter(is_active=True).first()

        translation_obj = None
        if dashboard:
            translation_obj = dashboard.translations.filter(language=language).first() or dashboard.translations.filter(language='pt').first()

        wallet = Wallet.objects.filter(usuario=request.user).first()
        inventories = Inventory.objects.filter(user=request.user)

        # Verificar se o usuário é um apoiador
        try:
            apoiador = Apoiador.objects.get(user=request.user)
            is_apoiador = True
            image = apoiador.imagem.url if apoiador.imagem else None
            status = apoiador.status
        except Apoiador.DoesNotExist:
            is_apoiador = False
            image = None
            status = None

        # Contagem de leilões do usuário
        leiloes_user = Auction.objects.filter(seller=request.user).count()

        perfil, _ = PerfilGamer.objects.get_or_create(user=request.user)
        ganhou_bonus = False
        if perfil.pode_receber_bonus_diario():
            ganhou_bonus = perfil.receber_bonus_diario()

        conquistas = verificar_conquistas(request)

        context = {
            'segment': 'dashboard',
            'dashboard': dashboard,
            'translation': translation_obj,
            'wallet': wallet,
            'inventories': inventories,
            'is_apoiador': is_apoiador,
            'image': image,
            'status': status,
            'leiloes_user': leiloes_user,
            'perfil': perfil,
            'ganhou_bonus': ganhou_bonus,
            'xp_percent': int((perfil.xp / perfil.xp_para_proximo_nivel()) * 100),
            'conquistas': conquistas,
        }
        return render(request, 'dashboard_custom/dashboard.html', context)
    else:
        return redirect('/')


def terms_view(request):
    context = {
        "last_updated": datetime.today().strftime("%d/%m/%Y"),
    }
    return render_theme_page(request, 'public', 'terms.html', context)


def verificar_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError):
        user = None

    if user and default_token_generator.check_token(user, token):
        if not user.is_email_verified:
            user.is_email_verified = True
            user.save(update_fields=['is_email_verified'])

            # Adiciona XP
            perfil = PerfilGamer.objects.get(user=user)
            perfil.adicionar_xp(40)  # valor de XP por verificar e-mail

            # Verifica conquistas
            conquistas_desbloqueadas = verificar_conquistas(request)

            # Opcional: Armazena mensagem para exibir no template
            context = {
                'sucesso': True,
                'conquistas': conquistas_desbloqueadas,
                'xp': 40,
            }
        else:
            # Já verificado anteriormente
            context = {'ja_verificado': True}
    else:
        context = {'erro': True}

    return render_theme_page(request, 'public', 'email_verificado.html', context)


@conditional_otp_required
def reenviar_verificacao_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)

            if user.is_email_verified:
                messages.info(request, 'Seu email já está verificado.')
                return redirect('dashboard')

            # Gera novo link
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            verification_link = request.build_absolute_uri(
                reverse('verificar_email', args=[uid, token])
            )

            # Envia o e-mail
            try:
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
            except Exception as e:
                logger.error(f"Erro ao enviar email: {str(e)}")

                messages.success(request, 'Um novo e-mail de verificação foi enviado.')
            else:
                messages.error(request, 'O envio de e-mail está desativado no momento.')

            return redirect('dashboard')

        except User.DoesNotExist:
            messages.error(request, 'Nenhuma conta foi encontrada com este e-mail.')

    return render(request, 'verify/reenviar_verificacao.html')


def custom_set_language(request):
    if request.method == 'POST':
        lang_code = request.POST.get('language')
        next_url = request.POST.get('next', '/')

        if lang_code:
            response = HttpResponseRedirect(next_url)
            response.set_cookie('django_language', lang_code)
            activate(lang_code)

            # Verifica se o usuário já trocou de idioma antes
            if request.user.is_authenticated:
                perfil = PerfilGamer.objects.get(user=request.user)
                
                # Usa uma conquista para marcar se já fez isso antes
                if not ConquistaUsuario.objects.filter(usuario=request.user, conquista__codigo='idioma_trocado').exists():
                    perfil.adicionar_xp(20)  # XP por trocar idioma
                    conquistas = verificar_conquistas(request)
                    for conquista in conquistas:
                        messages.success(request, f"🏆 Conquista desbloqueada: {conquista.nome}")
                    messages.success(request, "Idioma alterado com sucesso! Você ganhou 20 XP.")

            return response

    return redirect('/')


def registration_success_view(request):
    return render(request, 'accounts_custom/registration_success.html')


def verify_2fa_view(request):
    if request.method == 'POST':
        user_id = request.session.get('pre_2fa_user_id')
        if not user_id:
            return redirect('login')

        User = get_user_model()
        user = User.objects.get(pk=user_id)
        token = request.POST.get('token')
        device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
        
        if device:
            if device.verify_token(token):
                request.user = user  # necessário para otp_login
                otp_login(request, device)  # <- isto marca o 2FA como verificado
                login(request, user)        # autentica o usuário na sessão Django
                del request.session['pre_2fa_user_id']
                return redirect('dashboard')
            else:
                return render(request, 'accounts_custom/verify-2fa.html', {'error': 'Código inválido.'})
        else:
            return render(request, 'accounts_custom/verify-2fa.html', {'error': 'Dispositivo 2FA não configurado ou não confirmado.'})
    
    return render(request, 'accounts_custom/verify-2fa.html')


@conditional_otp_required
def ativar_2fa(request):
    user = request.user

    # Verifica se já existe um dispositivo 2FA confirmado
    if TOTPDevice.objects.filter(user=user, confirmed=True).exists():
        messages.info(request, "A autenticação em 2 etapas já está ativada.")
        return redirect('dashboard')

    # Cria ou reutiliza um dispositivo ainda não confirmado
    device, _ = TOTPDevice.objects.get_or_create(user=user, confirmed=False)

    # Converte a chave hex para base32 (como o pyotp espera)
    base32_key = base64.b32encode(bytes.fromhex(device.key)).decode('utf-8')

    # Gera o QR Code em PNG (base64) para exibir na página
    qr_png = gerar_qr_png(user.email, base32_key)

    if request.method == "POST":
        token = request.POST.get("token")
        totp = pyotp.TOTP(base32_key)

        if totp.verify(token):
            device.confirmed = True
            device.save()

            user.is_2fa_enabled = True
            user.save()

            # Dá XP pela ativação
            perfil = PerfilGamer.objects.get(user=user)
            perfil.adicionar_xp(60)

            # Verifica conquistas
            conquistas_desbloqueadas = verificar_conquistas(request)
            for conquista in conquistas_desbloqueadas:
                messages.success(request, f"🏆 Conquista desbloqueada: {conquista.nome}!")

            messages.success(request, "Autenticação em 2 etapas ativada com sucesso! Você ganhou 60 XP.")
            return redirect('dashboard')
        else:
            messages.error(request, "Código inválido. Tente novamente.")

    return render(request, 'accounts_custom/ativar-2fa.html', {
        'qr_png': qr_png,
        'otp_secret': base32_key,
    })


@conditional_otp_required
def desativar_2fa(request):
    user = request.user

    if request.method != "POST":
        messages.warning(request, "Requisição inválida.")
        return redirect('administrator:security_settings')

    # Remove dispositivos TOTP confirmados
    devices = TOTPDevice.objects.filter(user=user, confirmed=True)
    if not devices.exists():
        messages.info(request, "Você não possui autenticação em duas etapas ativada.")
        return redirect('administrator:security_settings')

    devices.delete()

    # Atualiza o campo de status no usuário, se houver
    if hasattr(user, 'is_2fa_enabled'):
        user.is_2fa_enabled = False
        user.save()

    messages.success(request, "Autenticação em duas etapas desativada com sucesso.")
    return redirect('administrator:security_settings')
