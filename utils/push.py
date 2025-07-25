from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def send_push_notification(user, message, link=None, notification_id=None):
    """
    Envia uma notificação push em tempo real via Channels para o usuário informado.
    Não cria notificação no banco, apenas envia via WebSocket.
    """
    if not user:
        return
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user.id}",
        {
            "type": "send_notification",
            "message": message,
            "link": link,
            "notification_id": notification_id,
        }
    ) 