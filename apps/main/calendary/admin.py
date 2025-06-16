from django.contrib import admin
from core.admin import BaseModelAdmin
from django.utils.translation import gettext_lazy as _
from .models import Event

@admin.register(Event)
class EventAdmin(BaseModelAdmin):
    list_display = ('id', 'title', 'user', 'start_date', 'end_date', 'created_at', 'updated_at')
    list_filter = ('user', 'start_date', 'end_date', 'created_at')
    search_fields = ('title', 'user__username')
    ordering = ('-created_at',)
