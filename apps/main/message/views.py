from django.shortcuts import render, redirect
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required
from .models import Friendship, Chat, Message
from apps.main.home.models import User
from django.db.models import Q

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json
from django.http import Http404
from django.utils import timezone
from django.core.cache import cache

from apps.main.notification.tasks import create_notification


import logging
logger = logging.getLogger('django')


@login_required()
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


@login_required
def send_friend_request(request, user_id):
    friend = User.objects.get(id=user_id)

    # Verifica se já são amigos
    if Friendship.objects.filter(user=request.user, friend=friend, accepted=True).exists():
        return redirect('message:friends_list')  # Já são amigos

    # Verifica se um pedido de amizade já foi enviado
    if Friendship.objects.filter(user=request.user, friend=friend, accepted=False).exists():
        return redirect('message:friends_list')  # Pedido já enviado

    # Verifica se o amigo já enviou um pedido de amizade para o usuário
    if Friendship.objects.filter(user=friend, friend=request.user, accepted=False).exists():
        return redirect('message:friends_list')  # Amigo já enviou um pedido pendente

    # Cria um novo pedido de amizade
    Friendship.objects.create(user=request.user, friend=friend)

    try:
        message = f"{request.user.username} enviou um pedido de amizade."
        create_notification.delay(user_id, False, message)
    except Exception as e:
        logger.error(f"Erro ao criar notificação: {str(e)}")

    return redirect('message:friends_list')


@login_required
def accept_friend_request(request, friendship_id):
    friendship = Friendship.objects.get(id=friendship_id)

    # Aceita a amizade
    friendship.accepted = True
    friendship.save()

    # Cria a relação bidirecional
    Friendship.objects.get_or_create(user=friendship.friend, friend=friendship.user, accepted=True)

    return redirect('message:friends_list')


@login_required
def reject_friend_request(request, friendship_id):
    friendship = Friendship.objects.get(id=friendship_id)
    friendship.delete()  # Remove a solicitação de amizade
    return redirect('message:friends_list')


@login_required
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


@login_required
def friends_list(request):
    # Amigos aceitos
    accepted_friendships = Friendship.objects.filter(user=request.user, accepted=True)
    
    # Solicitações de amizade pendentes recebidas
    pending_friend_requests = Friendship.objects.filter(friend=request.user, accepted=False)
    
    # Solicitações de amizade enviadas
    sent_friend_requests = Friendship.objects.filter(user=request.user, accepted=False)
    
    # Obtém todos os usuários, exceto o usuário logado, os amigos já aceitos, e aqueles com quem há solicitações pendentes
    users = User.objects.exclude(
        id=request.user.id
    ).exclude(
        id__in=accepted_friendships.values_list('friend_id', flat=True)
    ).exclude(
        id__in=sent_friend_requests.values_list('friend_id', flat=True)
    ).exclude(
        id__in=pending_friend_requests.values_list('user_id', flat=True)
    )

    return render(request, 'pages/friends.html', {
        'accepted_friendships': accepted_friendships,
        'pending_friend_requests': pending_friend_requests,
        'users': users,
        'segment': 'friend-list',
        'parent': 'message',
    })


def create_or_get_chat(user, friend):
    # Tenta encontrar um chat existente entre os dois usuários
    user1, user2 = sorted([user, friend], key=lambda u: u.id)

    # Tente obter ou criar o chat
    chat, created = Chat.objects.get_or_create(
        user1=user1,
        user2=user2
    )

    # Se o chat não foi encontrado, pode ser que o inverso esteja presente
    if not created:
        try:
            chat = Chat.objects.get(user1=user1, user2=user2)
        except Chat.DoesNotExist:
            chat = None  # Se não encontrar, chat permanece None

    if chat is None:
        chat = Chat.objects.create(user1=user1, user2=user2)

    return chat


@login_required
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


@login_required
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


@login_required
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


@login_required
def set_user_active(request):
    user = request.user
    if user.is_authenticated:
        # Armazena o timestamp da última atividade do usuário
        cache.set(f"user_activity_{user.id}", timezone.now(), timeout=300)  # 300 segundos = 5 minutos
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=403)


@login_required
def check_user_activity(request, user_id):
    last_activity = cache.get(f"user_activity_{user_id}")
    if last_activity:
        is_online = (timezone.now() - last_activity).total_seconds() < 300  # Checa se a última atividade foi nos últimos 5 minutos
        return JsonResponse({'is_online': is_online})
    return JsonResponse({'is_online': False})
