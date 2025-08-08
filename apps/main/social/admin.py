from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import (
    Post, Comment, Like, Follow, UserProfile, 
    Share, Hashtag, PostHashtag, CommentLike,
    Report, ModerationAction, ContentFilter, ModerationLog
)
from core.admin import BaseModelAdmin
from django.utils import timezone


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
    list_display = ['name', 'posts_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['posts_count', 'created_at', 'updated_at']
    ordering = ['-posts_count', '-created_at']
    
    fieldsets = (
        (_('Informações Básicas'), {
            'fields': ('name', 'description')
        }),
        (_('Estatísticas'), {
            'fields': ('posts_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PostHashtag)
class PostHashtagAdmin(BaseModelAdmin):
    list_display = ['post', 'hashtag', 'created_at']
    list_filter = ['hashtag', 'created_at']
    search_fields = ['post__content', 'hashtag__name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


# ============================================================================
# ADMIN DE MODERAÇÃO
# ============================================================================

@admin.register(Report)
class ReportAdmin(BaseModelAdmin):
    list_display = [
        'get_reported_content_short', 'report_type', 'reporter', 'status', 
        'priority', 'assigned_moderator', 'created_at'
    ]
    list_filter = [
        'report_type', 'status', 'priority', 'created_at', 'assigned_moderator'
    ]
    search_fields = [
        'description', 'reporter__username', 'reported_post__content',
        'reported_comment__content', 'reported_user__username'
    ]
    readonly_fields = [
        'similar_reports_count', 'created_at', 'updated_at', 'resolved_at'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-priority', '-created_at']
    
    fieldsets = (
        (_('Informações da Denúncia'), {
            'fields': ('reporter', 'report_type', 'description', 'status', 'priority')
        }),
        (_('Conteúdo Reportado'), {
            'fields': ('reported_post', 'reported_comment', 'reported_user'),
            'classes': ('collapse',)
        }),
        (_('Moderação'), {
            'fields': ('assigned_moderator', 'moderator_notes', 'resolved_at')
        }),
        (_('Estatísticas'), {
            'fields': ('similar_reports_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['assign_to_moderator', 'mark_as_resolved', 'mark_as_dismissed']
    
    def get_reported_content_short(self, obj):
        content = obj.get_reported_content()
        return content[:50] + '...' if len(content) > 50 else content
    get_reported_content_short.short_description = _('Conteúdo Reportado')
    
    def assign_to_moderator(self, request, queryset):
        """Ação para atribuir denúncias a um moderador"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Buscar moderadores disponíveis
        moderators = User.objects.filter(is_staff=True)
        
        # Atribuir denúncias pendentes
        pending_reports = queryset.filter(status='pending')
        for i, report in enumerate(pending_reports):
            moderator = moderators[i % len(moderators)]
            report.assigned_moderator = moderator
            report.status = 'reviewing'
            report.save()
        
        self.message_user(
            request, 
            f'{pending_reports.count()} denúncias foram atribuídas a moderadores.'
        )
    assign_to_moderator.short_description = _('Atribuir a moderadores')
    
    def mark_as_resolved(self, request, queryset):
        """Marcar denúncias como resolvidas"""
        queryset.update(status='resolved', resolved_at=timezone.now())
        self.message_user(request, f'{queryset.count()} denúncias foram marcadas como resolvidas.')
    mark_as_resolved.short_description = _('Marcar como resolvidas')
    
    def mark_as_dismissed(self, request, queryset):
        """Marcar denúncias como descartadas"""
        queryset.update(status='dismissed')
        self.message_user(request, f'{queryset.count()} denúncias foram descartadas.')
    mark_as_dismissed.short_description = _('Descartar denúncias')


@admin.register(ModerationAction)
class ModerationActionAdmin(BaseModelAdmin):
    list_display = [
        'action_type', 'get_target_description_short', 'moderator', 
        'is_active', 'created_at'
    ]
    list_filter = [
        'action_type', 'is_active', 'suspension_type', 'created_at', 'moderator'
    ]
    search_fields = [
        'reason', 'moderator__username', 'target_post__content',
        'target_comment__content', 'target_user__username'
    ]
    readonly_fields = [
        'suspension_end_date', 'expires_at', 'created_at', 'updated_at'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        (_('Informações da Ação'), {
            'fields': ('moderator', 'action_type', 'reason')
        }),
        (_('Alvo da Ação'), {
            'fields': ('target_post', 'target_comment', 'target_user'),
            'classes': ('collapse',)
        }),
        (_('Suspensão'), {
            'fields': ('suspension_duration', 'suspension_type', 'suspension_end_date'),
            'classes': ('collapse',)
        }),
        (_('Controle'), {
            'fields': ('is_active', 'expires_at', 'notify_user', 'notification_message')
        }),
        (_('Metadados'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['deactivate_actions', 'extend_suspension']
    
    def get_target_description_short(self, obj):
        target = obj.get_target_description()
        return target[:50] + '...' if len(target) > 50 else target
    get_target_description_short.short_description = _('Alvo')
    
    def deactivate_actions(self, request, queryset):
        """Desativar ações de moderação"""
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} ações foram desativadas.')
    deactivate_actions.short_description = _('Desativar ações')
    
    def extend_suspension(self, request, queryset):
        """Estender suspensões"""
        from datetime import timedelta
        
        suspended_actions = queryset.filter(
            action_type__in=['suspend_user', 'restrict_user'],
            is_active=True
        )
        
        for action in suspended_actions:
            if action.suspension_end_date:
                action.suspension_end_date += timedelta(days=7)
                action.expires_at = action.suspension_end_date
                action.save()
        
        self.message_user(
            request, 
            f'Suspensões de {suspended_actions.count()} ações foram estendidas por 7 dias.'
        )
    extend_suspension.short_description = _('Estender suspensões por 7 dias')


@admin.register(ContentFilter)
class ContentFilterAdmin(BaseModelAdmin):
    list_display = [
        'name', 'filter_type', 'action', 'is_active', 'matches_count', 'last_matched'
    ]
    list_filter = [
        'filter_type', 'action', 'is_active', 'case_sensitive', 'created_at'
    ]
    search_fields = ['name', 'pattern', 'description']
    readonly_fields = [
        'matches_count', 'last_matched', 'created_at', 'updated_at'
    ]
    ordering = ['-is_active', 'name']
    
    fieldsets = (
        (_('Informações do Filtro'), {
            'fields': ('name', 'filter_type', 'pattern', 'action', 'description')
        }),
        (_('Configurações'), {
            'fields': ('is_active', 'case_sensitive')
        }),
        (_('Aplicação'), {
            'fields': ('apply_to_posts', 'apply_to_comments', 'apply_to_usernames')
        }),
        (_('Estatísticas'), {
            'fields': ('matches_count', 'last_matched', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_filters', 'deactivate_filters', 'reset_statistics']
    
    def activate_filters(self, request, queryset):
        """Ativar filtros selecionados"""
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} filtros foram ativados.')
    activate_filters.short_description = _('Ativar filtros')
    
    def deactivate_filters(self, request, queryset):
        """Desativar filtros selecionados"""
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} filtros foram desativados.')
    deactivate_filters.short_description = _('Desativar filtros')
    
    def reset_statistics(self, request, queryset):
        """Resetar estatísticas dos filtros"""
        queryset.update(matches_count=0, last_matched=None)
        self.message_user(request, f'Estatísticas de {queryset.count()} filtros foram resetadas.')
    reset_statistics.short_description = _('Resetar estatísticas')


@admin.register(ModerationLog)
class ModerationLogAdmin(BaseModelAdmin):
    list_display = [
        'action_type', 'moderator', 'target_type', 'target_id', 'created_at'
    ]
    list_filter = [
        'action_type', 'target_type', 'created_at', 'moderator'
    ]
    search_fields = [
        'description', 'details', 'moderator__username'
    ]
    readonly_fields = [
        'ip_address', 'user_agent', 'created_at', 'updated_at'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        (_('Informações da Ação'), {
            'fields': ('moderator', 'action_type', 'target_type', 'target_id')
        }),
        (_('Detalhes'), {
            'fields': ('description', 'details')
        }),
        (_('Contexto'), {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        (_('Metadados'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Impedir criação manual de logs"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Impedir edição de logs"""
        return False
    
    actions = ['export_logs']
    
    def export_logs(self, request, queryset):
        """Exportar logs selecionados"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="moderation_logs.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Data', 'Moderador', 'Tipo de Ação', 'Tipo do Alvo', 'ID do Alvo',
            'Descrição', 'Detalhes', 'IP'
        ])
        
        for log in queryset:
            writer.writerow([
                log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                log.moderator.username if log.moderator else 'Sistema',
                log.get_action_type_display(),
                log.target_type,
                log.target_id,
                log.description,
                log.details or '',
                log.ip_address or ''
            ])
        
        return response
    export_logs.short_description = _('Exportar logs selecionados')


# Configurações do admin
admin.site.site_header = _('Administração da Rede Social')
admin.site.site_title = _('Rede Social Admin')
admin.site.index_title = _('Gerenciamento da Rede Social')
