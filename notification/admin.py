# admin.py

from django.contrib import admin
from .models import Notification, PublicNotificationView
from core.admin import BaseModelAdmin


@admin.register(Notification)
class NotificationAdmin(BaseModelAdmin):
    list_display = ('user', 'notification_type', 'message', 'viewed', 'created_at', 'updated_at')
    list_filter = ('notification_type', 'viewed', 'created_at')
    search_fields = ('user__username', 'message')
    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')


@admin.register(PublicNotificationView)
class PublicNotificationViewAdmin(BaseModelAdmin):
    list_display = ('user', 'notification', 'viewed')
    list_filter = ('viewed',)
    search_fields = ('user__username', 'notification__message')
