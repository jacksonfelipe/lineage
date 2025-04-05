from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Notification, PublicNotificationView
from django.contrib.auth.decorators import permission_required


@login_required
def get_notifications(request):

    # Filtra as notificações do usuário atual que ainda não foram visualizadas
    user_notifications = Notification.objects.filter(user=request.user, viewed=False).order_by('-created_at')

    # Busca todas as notificações públicas
    public_notifications = Notification.objects.filter(user=None).order_by('-created_at')
    
    # Obtém as notificações públicas que o usuário visualizou
    public_notifications_viewed = PublicNotificationView.objects.filter(user=request.user, viewed=True)
    public_notifications_viewed_ids = [public_notification_view.notification.id for public_notification_view in public_notifications_viewed]

    # lista que sera retornada no final
    notifications_list = []
    
    # Adicionamos notificações do usuário atual
    for notification in user_notifications:
        notification_data = {
            'id': notification.id,
            'message': notification.message,
            'type': notification.notification_type,
            'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'viewed': notification.viewed,
            # Aqui você gera o URL para a visualização de detalhes da notificação
            'detail_url': reverse('notification:notification_detail', args=[notification.id])
        }
        notifications_list.append(notification_data)
    
    # Adicionamos notificações públicas
    for notification in public_notifications:
        if notification.id in public_notifications_viewed_ids:
            notification_data = {
                'id': notification.id,
                'message': notification.message,
                'type': notification.notification_type,
                'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'viewed': notification.viewed,
            }
            # Adiciona a URL para a página de detalhes da notificação
            notification_data['detail_url'] = reverse('notification:notification_detail', args=[notification.id])
            notifications_list.append(notification_data)
    
    return JsonResponse({'notifications': notifications_list})


@login_required
def mark_all_as_read(request):
    # Marcar todas as notificações privadas como lidas
    Notification.objects.filter(user=request.user, viewed=False).update(viewed=True)
    
    # Buscar todas as notificações públicas que ainda não foram visualizadas pelo usuário
    public_notifications = Notification.objects.filter(user=None)
    
    for notification in public_notifications:
        # Verificar se já existe um registro em PublicNotificationView para esta notificação e usuário
        public_notification_view, created = PublicNotificationView.objects.get_or_create(
            user=request.user, 
            notification=notification
        )
        # Se o registro já existia, atualizar o campo 'viewed' para True
        if not public_notification_view.viewed:
            public_notification_view.viewed = True
            public_notification_view.save()
    
    return JsonResponse({'status': 'ok'})


@login_required
def clear_all_notifications(request):
    Notification.objects.filter(user=request.user).delete()
    return JsonResponse({'status': 'ok'})


@login_required
def notification_detail(request, pk):
    notification = get_object_or_404(Notification, pk=pk)

    data = {
            'type': notification.notification_type,
            'message': notification.message,
            'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S')
           }
    
    if notification.user == request.user:
        notification.viewed = True
        notification.save()
    
    if notification.user == None:
        # Verifica se existe uma marcação de visualização para notificação pública
        public_notification_view = PublicNotificationView.objects.filter(user=request.user, notification=notification).first()
        if not public_notification_view:
            PublicNotificationView.objects.create(user=request.user, notification=notification, viewed=True)
    
    return JsonResponse(data)


@login_required
def all_notifications(request):
    # Busca todas as notificações do usuário
    private_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Busca todas as notificações públicas
    public_notifications = Notification.objects.filter(user=None).order_by('-created_at')
    
    # Obtém as notificações públicas que o usuário visualizou
    public_notifications_viewed = PublicNotificationView.objects.filter(user=request.user)
    public_notifications_viewed_ids = [public_notification_view.notification.id for public_notification_view in public_notifications_viewed]
    
    # Marca as notificações públicas que o usuário visualizou
    for notification in public_notifications:
        if notification.id in public_notifications_viewed_ids:
            notification.viewed = True
        else:
            notification.viewed = False

    context = {
        'private_notifications': private_notifications,
        'public_notifications': public_notifications,
        'segment': 'index',
        'parent': 'notification',
    }
    return render(request, 'pages/notifications.html', context)


@login_required
def confirm_notification_view(request, pk):
    notification = get_object_or_404(Notification, pk=pk)

    if notification.user == request.user:
        notification.viewed = True
        notification.save()
    elif notification.user is None:
        # Verifica se existe uma marcação de visualização para notificação pública
        public_notification_view, created = PublicNotificationView.objects.get_or_create(user=request.user, notification=notification)
        if created:
            public_notification_view.viewed = True
            public_notification_view.save()

    return JsonResponse({'status': 'success'})
