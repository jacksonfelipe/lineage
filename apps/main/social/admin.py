from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Post, Comment, Like, Follow, UserProfile
from core.admin import BaseModelAdmin


@admin.register(Post)
class PostAdmin(BaseModelAdmin):
    list_display = ['author', 'content_preview', 'is_public', 'likes_count', 'comments_count', 'created_at']
    list_filter = ['is_public', 'created_at', 'author']
    search_fields = ['content', 'author__username', 'author__first_name', 'author__last_name']
    readonly_fields = ['likes_count', 'comments_count', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = _('Conteúdo')


@admin.register(Comment)
class CommentAdmin(BaseModelAdmin):
    list_display = ['author', 'post', 'content_preview', 'parent', 'created_at']
    list_filter = ['created_at', 'author', 'post']
    search_fields = ['content', 'author__username', 'post__content']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = _('Conteúdo')


@admin.register(Like)
class LikeAdmin(BaseModelAdmin):
    list_display = ['user', 'post', 'created_at']
    list_filter = ['created_at', 'user', 'post']
    search_fields = ['user__username', 'post__content']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(Follow)
class FollowAdmin(BaseModelAdmin):
    list_display = ['follower', 'following', 'created_at']
    list_filter = ['created_at', 'follower', 'following']
    search_fields = ['follower__username', 'following__username']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(UserProfile)
class UserProfileAdmin(BaseModelAdmin):
    list_display = ['user', 'bio_preview', 'is_private', 'location', 'website']
    list_filter = ['is_private', 'location']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'bio']
    readonly_fields = ['user']
    
    def bio_preview(self, obj):
        return obj.bio[:50] + '...' if obj.bio and len(obj.bio) > 50 else obj.bio
    bio_preview.short_description = _('Biografia')
