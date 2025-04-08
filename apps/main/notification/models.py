from django.db import models
from core.models import BaseModel
from django.conf import settings
from encrypted_fields.encrypted_fields import *
from encrypted_fields.encrypted_files import *
from utils.choices import *


class Notification(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = EncryptedCharField(max_length=255)
    viewed = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.message[:50]}..."


class PublicNotificationView(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    viewed = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Visualização de Notificação Pública'
        verbose_name_plural = 'Visualizações de Notificações Públicas'
