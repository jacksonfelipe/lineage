from django.db import models
from core.models import BaseModel
from apps.main.home.models import User


class Friendship(BaseModel):
    user = models.ForeignKey(User, related_name='friends', on_delete=models.CASCADE)
    friend = models.ForeignKey(User, related_name='friend_of', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'friend')  # Garante que a amizade entre dois usuários seja única
        verbose_name = 'Amizade'
        verbose_name_plural = 'Amizade'

    def __str__(self):
        return f"{self.user.username} and {self.friend.username} - {'Accepted' if self.accepted else 'Pending'}"


class Chat(BaseModel):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats_user2')
    last_message = models.TextField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user1', 'user2')
        verbose_name = 'Conversas'
        verbose_name_plural = 'Conversas'

    def __str__(self):
        return f"Chat between {self.user1.username} and {self.user2.username}"


class Message(BaseModel):
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)  # Novo campo para marcar se a mensagem foi lida

    def __str__(self):
        return f"Message from {self.sender.username} at {self.timestamp}"
    
    class Meta:
        verbose_name = 'Histórico das Conversas'
        verbose_name_plural = 'Histórico das Conversas'

    @classmethod
    def mark_as_read(cls, chat_id, user):
        """
        Marca todas as mensagens de um chat como lidas para um determinado usuário,
        exceto as mensagens enviadas pelo próprio usuário.
        """
        cls.objects.filter(chat_id=chat_id, is_read=False).exclude(sender=user).update(is_read=True)
