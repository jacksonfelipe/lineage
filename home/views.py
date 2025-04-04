from .models import *
from django.apps import apps
from django.http import HttpResponse
from django.core.paginator import Paginator

from .forms import UserProfileForm, AddressUserForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth import logout


def index(request):

    # Page from the theme 
    return render(request, 'pages/index.html')


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
