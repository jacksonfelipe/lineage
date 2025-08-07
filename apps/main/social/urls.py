from django.urls import path
from . import views

app_name = 'social'

urlpatterns = [
    # Feed e posts
    path('feed/', views.feed, name='feed'),
    path('my-posts/', views.my_posts, name='my_posts'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    
    # CRUD de posts
    path('post/create/', views.PostCreateView.as_view(), name='post_create'),
    path('post/<int:pk>/edit/', views.PostUpdateView.as_view(), name='post_edit'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    
    # Interações
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('post/<int:post_id>/react/', views.react_to_post, name='react_to_post'),
    path('post/<int:post_id>/share/', views.share_post, name='share_post'),
    path('post/<int:post_id>/pin/', views.pin_post, name='pin_post'),
    path('user/<int:user_id>/follow/', views.follow_user, name='follow_user'),
    path('comment/<int:comment_id>/like/', views.like_comment, name='like_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    
    # Perfis
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('profile/<str:username>/followers/', views.followers_list, name='followers_list'),
    path('profile/<str:username>/following/', views.following_list, name='following_list'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    
    # Busca e hashtags
    path('search/', views.search, name='search'),
    path('hashtag/<str:hashtag_name>/', views.hashtag_detail, name='hashtag_detail'),
]
