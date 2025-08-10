from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.contrib import messages
from django.utils.translation import gettext as _
from apps.main.social.models import ContentFilter, Report, ModerationLog
from django.contrib.auth import get_user_model

User = get_user_model()


class ContentFilterMiddleware(MiddlewareMixin):
    """
    Middleware para bloqueios críticos de conteúdo (auto_delete)
    Outros filtros são processados pelos signals após criação
    """
    
    def process_request(self, request):
        """Processa a requisição antes da view"""
        # Apenas para requisições POST que criam conteúdo
        if request.method == 'POST':
            # Verificar se é criação de post ou comentário
            if any(path in request.path for path in ['/social/feed/', '/social/post/create/', '/social/post/']):
                # Verificar filtros de bloqueio crítico
                return self._check_critical_filters(request)
        return None
    
    def _check_critical_filters(self, request):
        """Verifica apenas filtros críticos que bloqueiam criação (auto_delete)"""
        try:
            # Obter apenas filtros de bloqueio crítico
            critical_filters = ContentFilter.objects.filter(
                is_active=True, 
                action='auto_delete'
            )
            
            if not critical_filters.exists():
                return None
            
            # Verificar se há dados POST
            if not request.POST:
                return None
            
            # Extrair conteúdo para verificação
            content = request.POST.get('content') or request.POST.get('comment_content')
            if not content:
                return None
            
            # Verificar filtros críticos
            for content_filter in critical_filters:
                if content_filter.matches_content(content):
                    # Bloquear criação imediatamente
                    return JsonResponse({
                        'error': _('Conteúdo bloqueado por violar nossas diretrizes'),
                        'filter_name': content_filter.name
                    }, status=400)
                
        except Exception as e:
            print(f"Erro ao verificar filtros críticos: {e}")
        
        return None


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
