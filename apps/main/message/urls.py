from django.urls import path
from .views import *


app_name = 'message'


urlpatterns = [
    path('app/message/index/', message, name='index'),
    path('app/message/send_friend_request/<int:user_id>/', send_friend_request, name='send_friend_request'),
    path('app/message/accept_friend_request/<int:friendship_id>/', accept_friend_request, name='accept_friend_request'),
    path('app/message/reject_friend_request/<int:friendship_id>/', reject_friend_request, name='reject_friend_request'),
    path('app/message/remove_friend/<int:friendship_id>/', remove_friend, name='remove_friend'),
    path('app/message/friends_list/', friends_list, name='friends_list'),

    path('app/api/send-message/', send_message, name='send_message'),
    path('app/api/load-messages/<int:friend_id>/', load_messages, name='load_messages'),
    path('app/api/get_unread_count/', get_unread_count, name='unread_count'),
    path('app/api/set-user-active/', set_user_active, name='set_user_active'),
    path('app/api/check-user-activity/<int:user_id>/', check_user_activity, name='check_user_activity'),
]
