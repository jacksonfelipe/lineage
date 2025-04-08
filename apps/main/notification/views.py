from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Notification, PublicNotificationView
from django.contrib.auth.decorators import permission_required
from django.db.models import Q


@login_required
def get_notifications(request):
    # Notificações privadas do usuário (exclui staff se user não for staff/superuser)
    user_notifications = Notification.objects.filter(
        user=request.user,
        viewed=False
    ).exclude(
        notification_type='staff'
    ).order_by('-created_at')

    if request.user.is_staff or request.user.is_superuser:
        # Se for staff/superuser, incluir também notificações staff pra ele
        staff_notifications = Notification.objects.filter(
            user=request.user,
            notification_type='staff',
            viewed=False
        ).order_by('-created_at')
        user_notifications = user_notifications | staff_notifications

    # Notificações públicas
    public_notifications = Notification.objects.filter(user=None).order_by('-created_at')

    # Filtra notificações públicas staff apenas para usuários staff/superusers
    if not (request.user.is_staff or request.user.is_superuser):
        public_notifications = public_notifications.exclude(notification_type='staff')

    # Visualizações públicas
    public_notifications_viewed = PublicNotificationView.objects.filter(user=request.user, viewed=True)
    public_notifications_viewed_ids = [pnv.notification.id for pnv in public_notifications_viewed]

    notifications_list = []

    # Notificações privadas
    for notification in user_notifications:
        notifications_list.append({
            'id': notification.id,
            'message': notification.message,
            'type': notification.notification_type,
            'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'viewed': notification.viewed,
            'detail_url': reverse('notification:notification_detail', args=[notification.id])
        })

    # Notificações públicas
    for notification in public_notifications:
        if notification.id not in public_notifications_viewed_ids:
            notifications_list.append({
                'id': notification.id,
                'message': notification.message,
                'type': notification.notification_type,
                'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'viewed': False,
                'detail_url': reverse('notification:notification_detail', args=[notification.id])
            })

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

    # Proteção: usuário comum tentando acessar notificação staff
    if notification.notification_type == 'staff' and not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'error': 'Você não tem permissão para ver esta notificação.'}, status=403)

    data = {
        'type': notification.notification_type,
        'message': notification.message,
        'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S')
    }

    if notification.user == request.user:
        notification.viewed = True
        notification.save()

    elif notification.user is None:
        # Verifica se já existe visualização pública
        public_notification_view = PublicNotificationView.objects.filter(
            user=request.user,
            notification=notification
        ).first()

        if not public_notification_view:
            PublicNotificationView.objects.create(
                user=request.user,
                notification=notification,
                viewed=True
            )

    else:
        # Caso o usuário tente acessar notificação privada de outro usuário
        return JsonResponse({'error': 'Você não tem permissão para ver esta notificação.'}, status=403)

    return JsonResponse(data)


@login_required
def all_notifications(request):
    user = request.user

    # Filtra notificações privadas do usuário
    private_notifications = Notification.objects.filter(
        user=user
    ).order_by('-created_at')

    # Se o usuário não é staff/superuser, removemos notificações staff
    if not (user.is_staff or user.is_superuser):
        private_notifications = private_notifications.exclude(notification_type='staff')

    # Notificações públicas (user=None)
    public_notifications = Notification.objects.filter(user=None).order_by('-created_at')

    # Se não for staff/superuser, não verá as públicas tipo 'staff'
    if not (user.is_staff or user.is_superuser):
        public_notifications = public_notifications.exclude(notification_type='staff')

    # Ver quais públicas já foram visualizadas
    public_notifications_viewed = PublicNotificationView.objects.filter(user=user)
    public_notifications_viewed_ids = {pnv.notification_id for pnv in public_notifications_viewed}

    # Marcar na instância se a notificação pública foi visualizada ou não
    for notification in public_notifications:
        notification.viewed = notification.id in public_notifications_viewed_ids

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
