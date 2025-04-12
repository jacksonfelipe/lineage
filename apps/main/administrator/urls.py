from django.urls import path

from .views import *

app_name = 'administrator'

urlpatterns = [
  path('chat/<str:group_name>/', chat_room, name='chat_room'),
  path('error/chat/', error_chat, name='error_chat'),
]
