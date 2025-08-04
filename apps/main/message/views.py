from django.shortcuts import render, redirect
from apps.main.home.decorator import conditional_otp_required
from .models import Friendship, Chat, Message
from apps.main.home.models import User
from django.db.models import Q

from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from django.http import Http404
from django.utils import timezone
from django.core.cache import cache

from utils.notifications import send_notification
from django.urls import reverse

from apps.main.home.models import PerfilGamer, ConquistaUsuario
from django.contrib import messages

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.vary import vary_on_cookie

import json
import logging
logger = logging.getLogger(__name__)


def create_or_get_chat(user, friend):
    user1, user2 = sorted([user, friend], key=lambda u: u.id)

    chat, created = Chat.objects.get_or_create(user1=user1, user2=user2)

    return chat


@conditional_otp_required
def message(request):
    accepted_friendships = Friendship.objects.filter(user=request.user, accepted=True)
    
    if request.user.avatar:
        user_uuid = request.user.uuid
    else:
        user_uuid = None

    context = {
        'segment': 'index',
        'parent': 'message',
        'accepted_friendships': accepted_friendships,
        'user_uuid': user_uuid,
        'username': request.user.username,
    }
    return render(request, 'pages/chat.html', context)


@conditional_otp_required
def send_friend_request(request, user_id):
    friend = User.objects.get(id=user_id)

    # Verifica se já são amigos
    if Friendship.objects.filter(user=request.user, friend=friend, accepted=True).exists():
        return redirect('message:friends_list')

    # Verifica se um pedido de amizade já foi enviado
    if Friendship.objects.filter(user=request.user, friend=friend, accepted=False).exists():
        return redirect('message:friends_list')

    # Verifica se o amigo já enviou um pedido de amizade para o usuário
    if Friendship.objects.filter(user=friend, friend=request.user, accepted=False).exists():
        return redirect('message:friends_list')

    # Cria um novo pedido de amizade
    Friendship.objects.create(user=request.user, friend=friend)

    # Ganha XP e verifica conquista
    if request.user.is_authenticated:
        perfil = PerfilGamer.objects.get(user=request.user)

        # Só dá XP se for o primeiro pedido de amizade
        if not ConquistaUsuario.objects.filter(usuario=request.user, conquista__codigo='primeiro_amigo').exists():
            perfil.adicionar_xp(30)
            messages.success(request, "Você enviou seu primeiro pedido de amizade! +30 XP")

    try:
        message = f"{request.user.username} enviou um pedido de amizade."
        send_notification(
            user=friend,
            notification_type='user',
            message=message,
            created_by=request.user,
            link=reverse('message:friends_list')
        )
    except Exception as e:
        logger.error(f"Erro ao criar notificação: {str(e)}")

    return redirect('message:friends_list')


@conditional_otp_required
def accept_friend_request(request, friendship_id):
    friendship = Friendship.objects.get(id=friendship_id)

    # Aceita a amizade
    friendship.accepted = True
    friendship.save()

    # Cria a relação bidirecional
    Friendship.objects.get_or_create(user=friendship.friend, friend=friendship.user, accepted=True)

    # Ganha XP e verifica conquistas
    if request.user.is_authenticated:
        perfil = PerfilGamer.objects.get(user=request.user)

        # Só dá XP se for o primeiro pedido de amizade aceito
        if not ConquistaUsuario.objects.filter(usuario=request.user, conquista__codigo='primeiro_amigo_aceito').exists():
            perfil.adicionar_xp(40)
            messages.success(request, "Você aceitou seu primeiro pedido de amizade! +40 XP")

    return redirect('message:friends_list')


@conditional_otp_required
def reject_friend_request(request, friendship_id):
    friendship = Friendship.objects.get(id=friendship_id)
    friendship.delete()  # Remove a solicitação de amizade
    return redirect('message:friends_list')


@conditional_otp_required
def cancel_friend_request(request, friendship_id):
    """
    Cancela uma solicitação de amizade enviada pelo usuário
    """
    try:
        friendship = Friendship.objects.get(
            id=friendship_id,
            user=request.user,  # Apenas o usuário que enviou pode cancelar
            accepted=False
        )
        friendship.delete()
        messages.success(request, "Solicitação de amizade cancelada com sucesso.")
    except Friendship.DoesNotExist:
        messages.error(request, "Solicitação de amizade não encontrada.")
    
    return redirect('message:friends_list')


@conditional_otp_required
def remove_friend(request, friendship_id):
    try:
        # Obtém a amizade
        friendship = Friendship.objects.get(id=friendship_id)

        # Verifica se o usuário é parte da amizade
        if friendship.user == request.user or friendship.friend == request.user:
            # Remove a amizade para ambos os lados
            friendship.delete()  # Remove a amizade

            # Remove a amizade bidirecional
            Friendship.objects.filter(
                (Q(user=friendship.friend) & Q(friend=friendship.user)) |
                (Q(user=friendship.user) & Q(friend=friendship.friend))
            ).delete()

    except Friendship.DoesNotExist:
        pass  # Caso não exista, não faz nada

    return redirect('message:friends_list')


@conditional_otp_required
@vary_on_cookie
def friends_list(request):
    """
    View otimizada para lista de amigos com paginação e filtros
    """
    # Parâmetros de paginação e filtros
    page = request.GET.get('page', 1)
    search_query = request.GET.get('search', '').strip()
    friends_per_page = 20  # Limite de amigos por página
    users_per_page = 30    # Limite de usuários por página
    
    # Amigos aceitos - otimizado com select_related
    accepted_friendships = Friendship.objects.filter(
        user=request.user, 
        accepted=True
    ).select_related('friend')
    
    # Solicitações de amizade pendentes recebidas
    pending_friend_requests = Friendship.objects.filter(
        friend=request.user, 
        accepted=False
    ).select_related('user')
    
    # Solicitações de amizade enviadas
    sent_friend_requests = Friendship.objects.filter(
        user=request.user, 
        accepted=False
    ).select_related('friend')
    
    # Query base para usuários disponíveis
    users_queryset = User.objects.exclude(id=request.user.id)
    
    # Excluir usuários que já são amigos ou têm solicitações pendentes
    excluded_user_ids = set()
    
    # IDs de amigos aceitos
    excluded_user_ids.update(
        accepted_friendships.values_list('friend_id', flat=True)
    )
    
    # IDs de solicitações enviadas
    excluded_user_ids.update(
        sent_friend_requests.values_list('friend_id', flat=True)
    )
    
    # IDs de solicitações recebidas
    excluded_user_ids.update(
        pending_friend_requests.values_list('user_id', flat=True)
    )
    
    users_queryset = users_queryset.exclude(id__in=excluded_user_ids)
    
    # Aplicar filtro de busca se fornecido
    if search_query:
        users_queryset = users_queryset.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Ordenar por nome de usuário
    users_queryset = users_queryset.order_by('username')
    
    # Paginação para usuários disponíveis
    users_paginator = Paginator(users_queryset, users_per_page)
    
    try:
        users_page = users_paginator.page(page)
    except PageNotAnInteger:
        users_page = users_paginator.page(1)
    except EmptyPage:
        users_page = users_paginator.page(users_paginator.num_pages)
    
    # Paginação para amigos aceitos (se houver muitos)
    if accepted_friendships.count() > friends_per_page:
        friends_paginator = Paginator(accepted_friendships, friends_per_page)
        friends_page = request.GET.get('friends_page', 1)
        try:
            accepted_friendships = friends_paginator.page(friends_page)
        except (PageNotAnInteger, EmptyPage):
            accepted_friendships = friends_paginator.page(1)
    
    # Paginação para solicitações pendentes (se houver muitas)
    pending_per_page = 10
    if pending_friend_requests.count() > pending_per_page:
        pending_paginator = Paginator(pending_friend_requests, pending_per_page)
        pending_page = request.GET.get('pending_page', 1)
        try:
            pending_friend_requests = pending_paginator.page(pending_page)
        except (PageNotAnInteger, EmptyPage):
            pending_friend_requests = pending_paginator.page(1)
    
    # Estatísticas para o template
    # Contar total antes da paginação
    total_pending = Friendship.objects.filter(friend=request.user, accepted=False).count()
    total_sent = Friendship.objects.filter(user=request.user, accepted=False).count()
    
    stats = {
        'total_friends': accepted_friendships.count() if not hasattr(accepted_friendships, 'paginator') else accepted_friendships.paginator.count,
        'total_pending_requests': total_pending,
        'total_sent_requests': total_sent,
        'total_available_users': users_paginator.count,
        'search_query': search_query,
    }
    
    context = {
        'accepted_friendships': accepted_friendships,
        'pending_friend_requests': pending_friend_requests,
        'sent_friend_requests': sent_friend_requests,
        'users': users_page,
        'stats': stats,
        'segment': 'friend-list',
        'parent': 'message',
    }
    
    return render(request, 'pages/friends.html', context)


@conditional_otp_required
def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message_text = data.get('message')
        friend_id = data.get('friend_id')

        if not message_text or len(message_text) > 500:  # Exemplo de validação
            return JsonResponse({'success': False, 'error': 'Mensagem inválida.'}, status=400)

        friend = get_object_or_404(User, id=friend_id)
        chat = create_or_get_chat(request.user, friend)

        message = Message.objects.create(chat=chat, text=message_text, sender=request.user)

        return JsonResponse({'success': True, 'message': message.text, 'timestamp': message.timestamp})

    return JsonResponse({'success': False, 'error': 'Método não permitido.'}, status=405)


@conditional_otp_required
def load_messages(request, friend_id):
    try:
        friend = get_object_or_404(User, id=friend_id)
        chat = create_or_get_chat(request.user, friend)

        # Verificar se existem mensagens não lidas antes de marcá-las como lidas
        unread_messages_count = chat.messages.filter(sender=friend, is_read=False).count()
        has_unread_messages = unread_messages_count > 0

        # Marcar as mensagens não lidas como lidas
        chat.messages.filter(sender=friend, is_read=False).update(is_read=True)

        value_limit = 500  # limita a quantidade de mensagens retornadas (caso a conversa seja muito grande)
        messages = chat.messages.all().select_related('sender').order_by('timestamp')[:value_limit].values('text', 'timestamp', 'sender__username', 'is_read', 'sender__uuid', 'sender__avatar')
        default_image = '/static/assets/img/team/generic_user.png'
        custom_imagem = '/decrypted-file/home/user/avatar/'

        formatted_messages = [
            {
                'text': msg['text'],
                'sender': {'username': msg['sender__username'], "avatar_url": default_image if msg['sender__avatar'] is None else custom_imagem + str(msg['sender__uuid']) + '/'},
                'timestamp': msg['timestamp'],
                'is_read': msg['is_read']
            }
            for msg in messages
        ]

        return JsonResponse({
            'success': True, 
            'messages': formatted_messages,
            'has_unread_messages': has_unread_messages  # Retorna se há novas mensagens não lidas
        }, status=200)

    except Http404 as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=404)
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': 'Ocorreu um erro inesperado.'}, status=400)


@conditional_otp_required
def get_unread_count(request):
    # Obtenha todos os amigos aceitos
    friendships = Friendship.objects.filter(user=request.user, accepted=True).values('friend')

    # Crie um dicionário para armazenar as contagens de mensagens não lidas por amigo
    unread_counts = {}
    
    for friendship in friendships:
        friend_id = friendship['friend']
        user1, user2 = sorted([request.user.id, friend_id])
        
        # Conte as mensagens não lidas que o amigo enviou para o usuário,
        # excluindo mensagens enviadas pelo próprio usuário
        unread_count = Message.objects.filter(
            chat__user1=user1,  # O remetente
            chat__user2=user2,  # O destinatário
            is_read=False,
            sender=friend_id  # Somente mensagens do amigo
        ).count()

        unread_counts[friend_id] = unread_count

    return JsonResponse({'unread_counts': unread_counts}, status=200)


@conditional_otp_required
def set_user_active(request):
    user = request.user
    if user.is_authenticated:
        # Armazena o timestamp da última atividade do usuário
        cache.set(f"user_activity_{user.id}", timezone.now(), timeout=300)  # 300 segundos = 5 minutos
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


@conditional_otp_required
def check_user_activity(request, user_id):
    last_activity = cache.get(f"user_activity_{user_id}")
    if last_activity:
        is_online = (timezone.now() - last_activity).total_seconds() < 300  # Checa se a última atividade foi nos últimos 5 minutos
        return JsonResponse({'is_online': is_online})
    return JsonResponse({'is_online': False})


@conditional_otp_required
def search_users_ajax(request):
    """
    View AJAX para busca de usuários em tempo real
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    search_query = request.GET.get('q', '').strip()
    page = request.GET.get('page', 1)
    
    if not search_query or len(search_query) < 2:
        return JsonResponse({'users': [], 'has_next': False, 'total': 0})
    
    # Buscar usuários que não são amigos nem têm solicitações pendentes
    excluded_user_ids = set()
    
    # IDs de amigos aceitos
    accepted_friendships = Friendship.objects.filter(
        user=request.user, 
        accepted=True
    ).values_list('friend_id', flat=True)
    excluded_user_ids.update(accepted_friendships)
    
    # IDs de solicitações enviadas
    sent_requests = Friendship.objects.filter(
        user=request.user, 
        accepted=False
    ).values_list('friend_id', flat=True)
    excluded_user_ids.update(sent_requests)
    
    # IDs de solicitações recebidas
    received_requests = Friendship.objects.filter(
        friend=request.user, 
        accepted=False
    ).values_list('user_id', flat=True)
    excluded_user_ids.update(received_requests)
    
    # Query de busca
    users_queryset = User.objects.exclude(
        id=request.user.id
    ).exclude(
        id__in=excluded_user_ids
    ).filter(
        Q(username__icontains=search_query) |
        Q(first_name__icontains=search_query) |
        Q(last_name__icontains=search_query) |
        Q(email__icontains=search_query)
    ).order_by('username')[:10]  # Limitar a 10 resultados
    
    # Serializar resultados
    users_data = []
    for user in users_queryset:
        users_data.append({
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name or '',
            'last_name': user.last_name or '',
            'email': user.email,
            'has_avatar': bool(user.avatar),
            'uuid': str(user.uuid) if user.uuid else None,
        })
    
    return JsonResponse({
        'users': users_data,
        'total': len(users_data),
        'query': search_query
    })


@conditional_otp_required
def get_friends_stats(request):
    """
    View AJAX para obter estatísticas de amigos
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    # Contar amigos aceitos
    total_friends = Friendship.objects.filter(
        user=request.user, 
        accepted=True
    ).count()
    
    # Contar solicitações pendentes recebidas
    total_pending_requests = Friendship.objects.filter(
        friend=request.user, 
        accepted=False
    ).count()
    
    # Contar solicitações enviadas
    total_sent_requests = Friendship.objects.filter(
        user=request.user, 
        accepted=False
    ).count()
    
    return JsonResponse({
        'total_friends': total_friends,
        'total_pending_requests': total_pending_requests,
        'total_sent_requests': total_sent_requests,
    })
