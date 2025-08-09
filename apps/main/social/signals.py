from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Post, Comment, ContentFilter, Report, ModerationLog
import re


@receiver(post_save, sender=Post)
def apply_content_filters_to_post(sender, instance, created, **kwargs):
    """Aplica filtros de conteúdo automaticamente quando um post é criado"""
    if not created:
        return
    
    # Obter filtros ativos para posts
    active_filters = ContentFilter.objects.filter(
        is_active=True,
        apply_to_posts=True
    )
    
    if not active_filters.exists():
        return
    
    # Verificar o conteúdo do post
    content_to_check = instance.content
    if not content_to_check:
        return
    
    for content_filter in active_filters:
        if content_filter.matches_content(content_to_check):
            apply_filter_action(content_filter, instance, 'post')


@receiver(post_save, sender=Comment)
def apply_content_filters_to_comment(sender, instance, created, **kwargs):
    """Aplica filtros de conteúdo automaticamente quando um comentário é criado"""
    if not created:
        return
    
    # Obter filtros ativos para comentários
    active_filters = ContentFilter.objects.filter(
        is_active=True,
        apply_to_comments=True
    )
    
    if not active_filters.exists():
        return
    
    # Verificar o conteúdo do comentário
    content_to_check = instance.content
    if not content_to_check:
        return
    
    for content_filter in active_filters:
        if content_filter.matches_content(content_to_check):
            apply_filter_action(content_filter, instance, 'comment')


def apply_filter_action(content_filter, content_instance, content_type):
    """Aplica a ação do filtro ao conteúdo"""
    try:
        # Determinar campos baseados no tipo de conteúdo
        if content_type == 'post':
            content_id = content_instance.id
            author = content_instance.author
        elif content_type == 'comment':
            content_id = content_instance.id
            author = content_instance.author
        else:
            return
        
        # Aplicar ação baseada no tipo
        if content_filter.action == 'flag':
            # Criar denúncia automática
            report = Report.objects.create(
                reporter=None,  # Sistema
                report_type='spam' if 'spam' in content_filter.name.lower() else 'inappropriate',
                description=f"Conteúdo filtrado automaticamente pelo filtro: {content_filter.name}",
                status='pending',
                priority='medium'
            )
            
            # Associar o conteúdo à denúncia
            if content_type == 'post':
                report.reported_post = content_instance
            elif content_type == 'comment':
                report.reported_comment = content_instance
            report.save()
            
            # Log da ação
            ModerationLog.log_action(
                moderator=None,  # Sistema
                action_type='filter_triggered',
                target_type=content_type,
                target_id=content_id,
                description=f"Filtro '{content_filter.name}' acionado - Conteúdo marcado para revisão",
                details=f"Padrão detectado: {content_filter.pattern[:100]}...\nConteúdo: {content_instance.content[:200]}..."
            )
            
        elif content_filter.action == 'auto_hide':
            # Ocultar conteúdo automaticamente
            if content_type == 'post':
                content_instance.is_public = False
                content_instance.save()
            elif content_type == 'comment':
                # Para comentários, podemos implementar um campo is_hidden
                # Por enquanto, deletar o comentário
                content_instance.delete()
                return  # Não continuar processamento se deletado
            
            # Log da ação
            ModerationLog.log_action(
                moderator=None,  # Sistema
                action_type='content_hidden',
                target_type=content_type,
                target_id=content_id,
                description=f"Conteúdo ocultado automaticamente pelo filtro: {content_filter.name}",
                details=f"Padrão detectado: {content_filter.pattern[:100]}...\nConteúdo: {content_instance.content[:200]}..."
            )
            
        elif content_filter.action == 'auto_delete':
            # Deletar conteúdo automaticamente
            content_instance.delete()
            
            # Log da ação (com ID que pode não existir mais)
            ModerationLog.log_action(
                moderator=None,  # Sistema
                action_type='content_deleted',
                target_type=content_type,
                target_id=content_id,
                description=f"Conteúdo deletado automaticamente pelo filtro: {content_filter.name}",
                details=f"Padrão detectado: {content_filter.pattern[:100]}...\nConteúdo: {content_instance.content[:200]}..."
            )
            return  # Não continuar processamento se deletado
            
        elif content_filter.action == 'notify_moderator':
            # Notificar moderadores (criar denúncia com prioridade alta)
            report = Report.objects.create(
                reporter=None,  # Sistema
                report_type='inappropriate',
                description=f"Conteúdo requer revisão manual - Filtro: {content_filter.name}",
                status='pending',
                priority='high'
            )
            
            # Associar o conteúdo à denúncia
            if content_type == 'post':
                report.reported_post = content_instance
            elif content_type == 'comment':
                report.reported_comment = content_instance
            report.save()
            
            # Log da ação
            ModerationLog.log_action(
                moderator=None,  # Sistema
                action_type='report_created',
                target_type=content_type,
                target_id=content_id,
                description=f"Moderadores notificados pelo filtro: {content_filter.name}",
                details=f"Padrão detectado: {content_filter.pattern[:100]}...\nConteúdo: {content_instance.content[:200]}..."
            )
        
        # Atualizar estatísticas do filtro
        content_filter.matches_count += 1
        content_filter.last_matched = timezone.now()
        content_filter.save(update_fields=['matches_count', 'last_matched'])
        
    except Exception as e:
        # Log de erro, mas não falhar a criação do conteúdo
        print(f"Erro ao aplicar filtro de conteúdo: {e}")
        ModerationLog.log_action(
            moderator=None,
            action_type='filter_triggered',
            target_type='system',
            target_id=0,
            description="Erro ao aplicar filtro de conteúdo",
            details=f"Erro: {str(e)}\nFiltro: {content_filter.name}"
        )


def check_spam_patterns(content):
    """Verifica padrões comuns de spam"""
    if not content:
        return False
    
    # Padrões de spam em português e inglês
    spam_patterns = [
        # Palavras de ganho fácil
        r'\b(ganhe|ganhar|dinheiro|fácil|rápido|grátis|free|money|earn|easy)\b',
        r'\b(clique|click|here|aqui|agora|now|urgente|urgent)\b',
        
        # Frases comuns de spam
        r'ganhe? dinheiro',
        r'dinheiro fácil',
        r'renda extra',
        r'trabalhe em casa',
        r'oportunidade única',
        r'limited time',
        r'act now',
        r'click here',
        
        # URLs suspeitas
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
        
        # Múltiplos sinais de exclamação ou interrogação
        r'[!]{3,}',
        r'[?]{3,}',
        
        # Texto em caixa alta excessivo
        r'\b[A-Z]{10,}\b',
    ]
    
    content_lower = content.lower()
    
    for pattern in spam_patterns:
        if re.search(pattern, content_lower, re.IGNORECASE):
            return True
    
    return False