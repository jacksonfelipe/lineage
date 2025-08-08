from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.contrib import messages
from django.utils.translation import gettext as _
from apps.main.social.models import ContentFilter, Report, ModerationLog
from django.contrib.auth import get_user_model

User = get_user_model()


class ContentFilterMiddleware(MiddlewareMixin):
    """
    Middleware para aplicar filtros de conteúdo automaticamente
    """
    
    def process_request(self, request):
        """Processa a requisição antes da view"""
        # Apenas para requisições POST que criam conteúdo
        if request.method == 'POST':
            # Verificar se é criação de post ou comentário
            if any(path in request.path for path in ['/social/feed/', '/social/post/create/', '/social/post/']):
                # Armazenar dados da requisição para processamento posterior
                request._content_to_filter = True
        return None
    
    def process_response(self, request, response):
        """Processa a resposta após a view"""
        # Verificar se há conteúdo para filtrar
        if hasattr(request, '_content_to_filter') and request._content_to_filter:
            # Aplicar filtros se necessário
            self._apply_content_filters(request)
        
        return response
    
    def _apply_content_filters(self, request):
        """Aplica filtros de conteúdo"""
        try:
            # Obter filtros ativos
            active_filters = ContentFilter.objects.filter(is_active=True)
            
            if not active_filters.exists():
                return
            
            # Verificar se há dados POST
            if not request.POST:
                return
            
            # Extrair conteúdo para verificação
            content_to_check = []
            
            # Verificar posts
            if 'content' in request.POST:
                content_to_check.append({
                    'type': 'post',
                    'content': request.POST.get('content', ''),
                    'id': None  # Será definido após criação
                })
            
            # Verificar comentários
            if 'comment_content' in request.POST:
                content_to_check.append({
                    'type': 'comment',
                    'content': request.POST.get('comment_content', ''),
                    'id': None
                })
            
            # Aplicar filtros
            for content_item in content_to_check:
                self._check_content_against_filters(content_item, request)
                
        except Exception as e:
            # Log do erro, mas não interromper o fluxo
            print(f"Erro ao aplicar filtros de conteúdo: {e}")
    
    def _check_content_against_filters(self, content_item, request):
        """Verifica conteúdo contra filtros ativos"""
        content = content_item['content']
        content_type = content_item['type']
        
        # Obter filtros relevantes
        filters = ContentFilter.objects.filter(is_active=True)
        
        if content_type == 'post':
            filters = filters.filter(apply_to_posts=True)
        elif content_type == 'comment':
            filters = filters.filter(apply_to_comments=True)
        
        for content_filter in filters:
            if content_filter.matches_content(content):
                # Aplicar ação do filtro
                self._apply_filter_action(content_filter, content, content_type, request)
    
    def _apply_filter_action(self, content_filter, content, content_type, request):
        """Aplica a ação do filtro"""
        try:
            if content_filter.action == 'flag':
                # Criar denúncia automática
                Report.objects.create(
                    reporter=request.user if request.user.is_authenticated else None,
                    report_type='spam' if content_filter.filter_type == 'spam_pattern' else 'inappropriate',
                    description=f"Conteúdo filtrado automaticamente: {content_filter.name}",
                    status='pending',
                    priority='medium'
                )
                
                # Log da ação
                ModerationLog.log_action(
                    moderator=None,  # Sistema
                    action_type='filter_triggered',
                    target_type=content_type,
                    target_id=0,  # Será atualizado quando o conteúdo for criado
                    description=f"Filtro '{content_filter.name}' acionado",
                    details=f"Conteúdo: {content[:100]}...",
                    request=request
                )
                
                # Notificar usuário
                if request.user.is_authenticated:
                    messages.warning(
                        request, 
                        _('Seu conteúdo foi marcado para revisão por nossos filtros automáticos.')
                    )
            
            elif content_filter.action == 'auto_hide':
                # Marcar para ocultação (será aplicado após criação)
                if request.user.is_authenticated:
                    messages.info(
                        request, 
                        _('Seu conteúdo foi ocultado automaticamente devido aos nossos filtros.')
                    )
            
            elif content_filter.action == 'auto_delete':
                # Bloquear criação
                if request.user.is_authenticated:
                    messages.error(
                        request, 
                        _('Seu conteúdo foi bloqueado por violar nossas diretrizes.')
                    )
                
                # Retornar erro para impedir criação
                return JsonResponse({
                    'error': _('Conteúdo bloqueado por filtros automáticos'),
                    'filter_name': content_filter.name
                }, status=400)
            
            elif content_filter.action == 'notify_moderator':
                # Notificar moderadores (implementar sistema de notificações)
                pass
                
        except Exception as e:
            print(f"Erro ao aplicar ação do filtro: {e}")


class SpamProtectionMiddleware(MiddlewareMixin):
    """
    Middleware para proteção contra spam
    """
    
    def process_request(self, request):
        """Verifica sinais de spam na requisição"""
        if request.method == 'POST':
            # Verificar se é criação de conteúdo
            if any(path in request.path for path in ['/social/feed/', '/social/post/create/']):
                if self._is_spam_request(request):
                    return JsonResponse({
                        'error': _('Atividade suspeita detectada. Tente novamente em alguns minutos.')
                    }, status=429)
        return None
    
    def _is_spam_request(self, request):
        """Verifica se a requisição parece ser spam"""
        # Verificar frequência de posts (implementar cache/rate limiting)
        if request.user.is_authenticated:
            # Verificar se o usuário fez muitos posts recentemente
            from django.utils import timezone
            from datetime import timedelta
            from apps.main.social.models import Post
            
            recent_posts = Post.objects.filter(
                author=request.user,
                created_at__gte=timezone.now() - timedelta(minutes=5)
            ).count()
            
            if recent_posts > 5:  # Mais de 5 posts em 5 minutos
                return True
        
        # Verificar conteúdo suspeito
        if request.POST:
            content = request.POST.get('content', '')
            
            # Padrões de spam
            spam_patterns = [
                r'\b(buy|sell|cheap|discount|free|money|earn|rich)\b',
                r'\b(viagra|cialis|casino|poker|lottery)\b',
                r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                r'\b(click here|visit now|limited time|act now)\b',
            ]
            
            import re
            for pattern in spam_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    return True
        
        return False
