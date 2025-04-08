from django.shortcuts import render
from django.http import Http404, JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required, login_required

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
    solicitation = None
    type_chat = None

    try:
        solicitation = Solicitation.objects.get(protocol=group_name)
        is_participant = SolicitationParticipant.objects.filter(
            solicitation=solicitation, user=request.user
        ).exists()
        type_chat = "Solicitação"
    except Solicitation.DoesNotExist:
        raise Http404(f"Protocolo {group_name} não encontrado.")

    # Verifica se o usuário é participante
    if not is_participant:
        raise Http404("Você não tem permissão para acessar esta sala de chat.")

    # Verifica se o status é 'pending'
    if solicitation.status != 'pending':
        return render(request, 'errors/solicitation_closed.html', {
            'solicitation': solicitation,
            'status': solicitation.get_status_display(),  # Exibe 'Aprovado', 'Rejeitado', etc
        })

    try:
        custom_imagem = '/decrypted-file/home/user/avatar/'
        avatar_url = custom_imagem + str(request.user.uuid) + '/'
    except (ValueError, AttributeError):
        avatar_url = '/static/assets/img/team/generic_user.png'

    solicitation_name = (
        str(solicitation.user.username).upper() + ' - ' + str(solicitation.user.email)
        if solicitation.user else "Solicitação sem usuário..."
    )

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
