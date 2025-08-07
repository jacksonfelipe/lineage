from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import (
    Post, Comment, Like, Follow, UserProfile, 
    Share, Hashtag, PostHashtag, CommentLike
)
from core.admin import BaseModelAdmin


@admin.register(Post)
class PostAdmin(BaseModelAdmin):
    list_display = [
        'author', 'content_preview', 'is_public', 'is_pinned', 
        'likes_count', 'comments_count', 'views_count', 'shares_count', 'created_at'
    ]
    list_filter = [
        'is_public', 'is_pinned', 'is_edited', 'created_at', 'author'
    ]
    search_fields = [
        'content', 'author__username', 'author__first_name', 'author__last_name'
    ]
    readonly_fields = [
        'likes_count', 'comments_count', 'views_count', 'shares_count', 
        'created_at', 'updated_at', 'edited_at', 'engagement_rate'
    ]
    date_hierarchy = 'created_at'
    fieldsets = (
        (_('Informações Básicas'), {
            'fields': ('author', 'content', 'is_public', 'is_pinned')
        }),
        (_('Mídia'), {
            'fields': ('image', 'video', 'link', 'link_title', 'link_description', 'link_image'),
            'classes': ('collapse',)
        }),
        (_('Estatísticas'), {
            'fields': ('likes_count', 'comments_count', 'views_count', 'shares_count', 'engagement_rate'),
            'classes': ('collapse',)
        }),
        (_('Metadados'), {
            'fields': ('created_at', 'updated_at', 'is_edited', 'edited_at'),
            'classes': ('collapse',)
        }),
    )
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = _('Conteúdo')
    
    def engagement_rate(self, obj):
        return f"{obj.engagement_rate:.1f}%"
    engagement_rate.short_description = _('Taxa de Engajamento')


@admin.register(Comment)
class CommentAdmin(BaseModelAdmin):
    list_display = [
        'author', 'post', 'content_preview', 'parent', 
        'likes_count', 'is_edited', 'created_at'
    ]
    list_filter = [
        'created_at', 'is_edited', 'author', 'post'
    ]
    search_fields = [
        'content', 'author__username', 'post__content'
    ]
    readonly_fields = [
        'likes_count', 'created_at', 'is_edited', 'edited_at'
    ]
    date_hierarchy = 'created_at'
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = _('Conteúdo')


@admin.register(CommentLike)
class CommentLikeAdmin(BaseModelAdmin):
    list_display = ['user', 'comment', 'created_at']
    list_filter = ['created_at', 'user', 'comment__post']
    search_fields = [
        'user__username', 'comment__content', 'comment__post__content'
    ]
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(Like)
class LikeAdmin(BaseModelAdmin):
    list_display = ['user', 'post', 'reaction_type', 'created_at']
    list_filter = [
        'reaction_type', 'created_at', 'user', 'post'
    ]
    search_fields = [
        'user__username', 'post__content'
    ]
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(Share)
class ShareAdmin(BaseModelAdmin):
    list_display = [
        'user', 'original_post', 'comment_preview', 'created_at'
    ]
    list_filter = ['created_at', 'user', 'original_post__author']
    search_fields = [
        'user__username', 'original_post__content', 'comment'
    ]
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    def comment_preview(self, obj):
        return obj.comment[:50] + '...' if obj.comment and len(obj.comment) > 50 else obj.comment
    comment_preview.short_description = _('Comentário')


@admin.register(Follow)
class FollowAdmin(BaseModelAdmin):
    list_display = [
        'follower', 'following', 'notifications_enabled', 'created_at'
    ]
    list_filter = [
        'notifications_enabled', 'created_at', 'follower', 'following'
    ]
    search_fields = [
        'follower__username', 'following__username'
    ]
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(UserProfile)
class UserProfileAdmin(BaseModelAdmin):
    list_display = [
        'user', 'bio_preview', 'is_private', 'location', 
        'total_posts', 'total_likes_received', 'created_at'
    ]
    list_filter = [
        'is_private', 'show_email', 'show_phone', 'allow_messages', 
        'gender', 'location'
    ]
    search_fields = [
        'user__username', 'user__first_name', 'user__last_name', 
        'bio', 'location', 'interests'
    ]
    readonly_fields = [
        'user', 'total_posts', 'total_likes_received', 'total_comments_received'
    ]
    fieldsets = (
        (_('Informações Básicas'), {
            'fields': ('user', 'bio', 'location', 'birth_date', 'gender', 'phone')
        }),
        (_('Mídia'), {
            'fields': ('avatar', 'cover_image'),
            'classes': ('collapse',)
        }),
        (_('Links'), {
            'fields': ('website', 'social_links'),
            'classes': ('collapse',)
        }),
        (_('Interesses'), {
            'fields': ('interests',),
            'classes': ('collapse',)
        }),
        (_('Privacidade'), {
            'fields': ('is_private', 'show_email', 'show_phone', 'allow_messages')
        }),
        (_('Estatísticas'), {
            'fields': ('total_posts', 'total_likes_received', 'total_comments_received'),
            'classes': ('collapse',)
        }),
    )
    
    def bio_preview(self, obj):
        return obj.bio[:50] + '...' if obj.bio and len(obj.bio) > 50 else obj.bio
    bio_preview.short_description = _('Biografia')


@admin.register(Hashtag)
class HashtagAdmin(BaseModelAdmin):
    list_display = [
        'name', 'description_preview', 'posts_count', 'created_at'
    ]
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['posts_count', 'created_at']
    date_hierarchy = 'created_at'
    
    def description_preview(self, obj):
        return obj.description[:100] + '...' if obj.description and len(obj.description) > 100 else obj.description
    description_preview.short_description = _('Descrição')


@admin.register(PostHashtag)
class PostHashtagAdmin(BaseModelAdmin):
    list_display = ['post', 'hashtag', 'created_at']
    list_filter = ['created_at', 'hashtag', 'post__author']
    search_fields = [
        'post__content', 'hashtag__name'
    ]
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


# Configurações do admin
admin.site.site_header = _('Administração da Rede Social')
admin.site.site_title = _('Rede Social Admin')
admin.site.index_title = _('Gerenciamento da Rede Social')
