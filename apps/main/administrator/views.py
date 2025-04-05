from django.shortcuts import render
from django.http import Http404, JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required, login_required
from django.templatetags.static import static

from apps.main.notification.models import Notification
from apps.main.news.models import News
from apps.main.solicitation.models import CreditSolicitation, SolicitationParticipant

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
        solicitation = CreditSolicitation.objects.get(protocol=group_name)
        # Verificar se o usuário é participante da solicitação
        is_participant = SolicitationParticipant.objects.filter(solicitation=solicitation, user=request.user).exists()
        type_chat = "Solicitação"

    except CreditSolicitation.DoesNotExist:
        # Se não for encontrado em nenhum dos dois, lança um erro 404
        raise Http404(f"Protocolo {group_name} não encontrado.")

    # Se o usuário não for participante, retorna erro 404
    if not is_participant:
        raise Http404("Você não tem permissão para acessar esta sala de chat.")

    # Tentar carregar a URL do avatar do usuário
    try:
        avatar_url = request.user.avatar.url
    except (ValueError, AttributeError):
        avatar_url = static('internal/images/user/GenericAvatar.png')

    # Tentar carregar a URL do avatar do agente
    try:
        agent_avatar = solicitation.agent.avatar.url
    except (ValueError, AttributeError):
        agent_avatar = static('internal/images/user/GenericAvatar.png')

    # Carregar mensagens anteriores
    messages = ChatGroup.objects.filter(group_name=group_name).order_by('timestamp')

    try:
        solicitation_name = solicitation.public_user.name
    except AttributeError:
        solicitation_name = str(solicitation.agent.username).upper() + ' - ' + str(solicitation.agent.email)

    solicitation_context = 'de Crédito do Agente:' if type_chat == 'Proposta' else 'do Cliente:'

    return render(request, 'pages/group.html', {
        'group_name': group_name,
        'avatar_url': avatar_url,
        'username': request.user.username,
        'messages': messages,
        'solicitation': solicitation_name,
        'solicitation_context': solicitation_context,
        'agent_name': 'Sem agente no momento...' if solicitation.agent is None else solicitation.agent.username,
        'agent_avatar': agent_avatar,
        'type_chat': type_chat,
    })


@login_required
def error_chat(request):
    return render(request, 'errors/access_denied.html', {
        'message': 'Você não tem permissão para acessar esta sala de chat.'
    })
