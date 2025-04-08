from django.shortcuts import render
from django.http import Http404, JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required, login_required
from django.templatetags.static import static

from apps.main.notification.models import Notification
from apps.main.news.models import News
from apps.main.solicitation.models import Solicitation, SolicitationParticipant

from .models import *


@staff_member_required
def get_latest_news(request):
    news = News.objects.filter(is_published=True).order_by('-pub_date')[:5]
    data = list(news.values('title', 'slug', 'content', 'pub_date'))
    return JsonResponse(data, safe=False)


@staff_member_required
def get_latest_notifications(request):
    notifications = Notification.objects.order_by('-created_at')[:5]
    data = list(notifications.values('notification_type', 'message'))
    return JsonResponse(data, safe=False)


@login_required
def chat_room(request, group_name):
    # Tenta encontrar a solicitação ou proposta com o protocolo correspondente
    solicitation = None
    type_chat = None

    try:
        # Primeiro tenta buscar em CreditSolicitation
        solicitation = Solicitation.objects.get(protocol=group_name)
        # Verificar se o usuário é participante da solicitação
        is_participant = SolicitationParticipant.objects.filter(solicitation=solicitation, user=request.user).exists()
        type_chat = "Solicitação"

    except Solicitation.DoesNotExist:
        # Se não for encontrado em nenhum dos dois, lança um erro 404
        raise Http404(f"Protocolo {group_name} não encontrado.")

    # Se o usuário não for participante, retorna erro 404
    if not is_participant:
        raise Http404("Você não tem permissão para acessar esta sala de chat.")

    # Tentar carregar a URL do avatar do usuário
    try:
        custom_imagem = '/decrypted-file/home/user/avatar/'
        avatar_url = custom_imagem + str(request.user.uuid) + '/'
    except (ValueError, AttributeError):
        avatar_url = static('assets/img/team/generic_user.png')

    if solicitation.user is not None:
        solicitation_name = str(solicitation.user.username).upper() + ' - ' + str(solicitation.user.email)
    else:
        solicitation_name = "Solicitação sem usuário..."

    # Carregar mensagens anteriores
    messages = ChatGroup.objects.filter(group_name=group_name).order_by('timestamp')

    solicitation_context = 'do Usuário:'

    return render(request, 'pages/group.html', {
        'group_name': group_name,
        'avatar_url': avatar_url,
        'username': request.user.username,
        'messages': messages,
        'solicitation': solicitation_name,
        'solicitation_context': solicitation_context,
        'type_chat': type_chat,
    })


@login_required
def error_chat(request):
    return render(request, 'errors/access_denied.html', {
        'message': 'Você não tem permissão para acessar esta sala de chat.'
    })
