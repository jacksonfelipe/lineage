from django.db import models
from core.models import BaseModel
from apps.main.home.models import User


class ChatGroup(BaseModel):
    group_name = models.CharField(max_length=255)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.message[:20]}"

    class Meta:
        verbose_name = 'Histórico dos Atendimentos'
        verbose_name_plural = 'Histórico dos Atendimentos'
