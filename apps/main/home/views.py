from .models import *
import json
from django.apps import apps
from django.http import HttpResponse
from django.core.paginator import Paginator

from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView, PasswordResetConfirmView
from .forms import UserProfileForm, AddressUserForm, RegistrationForm, LoginForm, UserPasswordResetForm, UserPasswordChangeForm, UserSetPasswordForm

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth import logout
from utils.notifications import send_notification

from apps.lineage.server.querys.query_dreamv3 import LineageStats
from apps.lineage.server.models import IndexConfig


with open('utils/data/index.json', 'r', encoding='utf-8') as file:
        data_index = json.load(file)


def index(request):
    clanes = LineageStats.top_clans(limit=10)
    online = LineageStats.players_online()
    config = IndexConfig.objects.first()
    classes_info = data_index['classes']

    return render(request, 'pages/index.html', {
        'clanes': clanes,
        'classes_info': classes_info,
        'online': online[0]['quant'],
        'configuracao': config
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

        # Verifica se o checkbox dos termos foi marcado
        if not request.POST.get('terms'):
            form.add_error(None, 'Você precisa aceitar os termos e condições para se registrar.')
        elif form.is_valid():
            user = form.save()

            # notificação de criação de conta
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

    context = {'form': form}
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
