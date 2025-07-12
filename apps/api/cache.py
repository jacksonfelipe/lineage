from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


class APICache:
    """Sistema de cache customizado para a API"""
    
    # Prefixos para diferentes tipos de dados
    CACHE_PREFIXES = {
        'players_online': 'api_online',
        'rankings': 'api_rank',
        'olympiad': 'api_olympiad',
        'bosses': 'api_boss',
        'siege': 'api_siege',
        'search': 'api_search',
        'auction': 'api_auction',
        'server_status': 'api_status',
    }
    
    # Tempos de cache em segundos
    CACHE_TIMES = {
        'players_online': 30,      # 30 segundos
        'rankings': 60,            # 1 minuto
        'olympiad': 300,           # 5 minutos
        'bosses': 60,              # 1 minuto
        'siege': 300,              # 5 minutos
        'search': 600,             # 10 minutos
        'auction': 60,             # 1 minuto
        'server_status': 30,       # 30 segundos
    }
    
    @classmethod
    def get_cache_key(cls, prefix, *args, **kwargs):
        """Gera uma chave de cache única"""
        # Combina todos os argumentos em uma string
        key_parts = [str(arg) for arg in args]
        key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
        key_string = "_".join(key_parts)
        
        # Cria hash da chave para evitar chaves muito longas
        key_hash = hashlib.md5(key_string.encode()).hexdigest()[:8]
        
        return f"{cls.CACHE_PREFIXES.get(prefix, 'api')}_{key_hash}"
    
    @classmethod
    def get(cls, prefix, *args, **kwargs):
        """Obtém dados do cache"""
        cache_key = cls.get_cache_key(prefix, *args, **kwargs)
        data = cache.get(cache_key)
        
        if data is not None:
            logger.debug(f"Cache HIT: {cache_key}")
        else:
            logger.debug(f"Cache MISS: {cache_key}")
        
        return data
    
    @classmethod
    def set(cls, prefix, data, *args, **kwargs):
        """Armazena dados no cache"""
        cache_key = cls.get_cache_key(prefix, *args, **kwargs)
        timeout = cls.CACHE_TIMES.get(prefix, 60)
        
        cache.set(cache_key, data, timeout)
        logger.debug(f"Cache SET: {cache_key} (timeout: {timeout}s)")
        
        return cache_key
    
    @classmethod
    def delete(cls, prefix, *args, **kwargs):
        """Remove dados do cache"""
        cache_key = cls.get_cache_key(prefix, *args, **kwargs)
        cache.delete(cache_key)
        logger.debug(f"Cache DELETE: {cache_key}")
    
    @classmethod
    def clear_prefix(cls, prefix):
        """Limpa todos os dados com um prefixo específico"""
        # Nota: Esta é uma implementação simplificada
        # Em produção, considere usar Redis com pattern matching
        logger.info(f"Cache CLEAR prefix: {prefix}")
    
    @classmethod
    def get_or_set(cls, prefix, callback, *args, **kwargs):
        """Obtém do cache ou executa callback e armazena"""
        data = cls.get(prefix, *args, **kwargs)
        
        if data is None:
            try:
                data = callback()
                cls.set(prefix, data, *args, **kwargs)
            except Exception as e:
                logger.error(f"Error in cache callback: {e}")
                raise
        
        return data


class CacheMiddleware:
    """Middleware para cache de respostas HTTP"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Verifica se a resposta deve ser cachead
        if self.should_cache(request):
            cache_key = self.get_cache_key(request)
            cached_response = cache.get(cache_key)
            
            if cached_response:
                return cached_response
        
        response = self.get_response(request)
        
        # Armazena a resposta no cache se apropriado
        if self.should_cache(request) and response.status_code == 200:
            cache_key = self.get_cache_key(request)
            cache.set(cache_key, response, 300)  # 5 minutos
        
        return response
    
    def should_cache(self, request):
        """Determina se a requisição deve ser cachead"""
        # Cache apenas GET requests para endpoints públicos
        return (
            request.method == 'GET' and
            request.path.startswith('/api/') and
            'auth' not in request.path and
            'user' not in request.path
        )
    
    def get_cache_key(self, request):
        """Gera chave de cache baseada na requisição"""
        # Inclui path, query params e headers relevantes
        key_parts = [
            request.path,
            request.GET.urlencode(),
            request.META.get('HTTP_ACCEPT', ''),
        ]
        key_string = "|".join(key_parts)
        return f"http_cache_{hashlib.md5(key_string.encode()).hexdigest()}"


class CacheStats:
    """Estatísticas de cache"""
    
    @classmethod
    def get_stats(cls):
        """Obtém estatísticas do cache"""
        try:
            # Implementação específica para Redis
            if hasattr(cache, 'client') and hasattr(cache.client, 'info'):
                info = cache.client.info()
                return {
                    'hits': info.get('keyspace_hits', 0),
                    'misses': info.get('keyspace_misses', 0),
                    'memory_used': info.get('used_memory_human', 'N/A'),
                    'connected_clients': info.get('connected_clients', 0),
                }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
        
        return {'error': 'Cache stats not available'}
    
    @classmethod
    def get_hit_rate(cls):
        """Calcula a taxa de hit do cache"""
        stats = cls.get_stats()
        if 'hits' in stats and 'misses' in stats:
            total = stats['hits'] + stats['misses']
            if total > 0:
                return (stats['hits'] / total) * 100
        return 0


# Decorator para cache automático
def cached_response(prefix, timeout=None):
    """Decorator para cache automático de respostas"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extrai request dos argumentos
            request = None
            for arg in args:
                if hasattr(arg, 'method') and hasattr(arg, 'path'):
                    request = arg
                    break
            
            if not request:
                return func(*args, **kwargs)
            
            # Gera chave de cache
            cache_key = APICache.get_cache_key(prefix, request.path, **request.GET.dict())
            
            # Tenta obter do cache
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return cached_data
            
            # Executa função e armazena resultado
            result = func(*args, **kwargs)
            cache_timeout = timeout or APICache.CACHE_TIMES.get(prefix, 60)
            cache.set(cache_key, result, cache_timeout)
            
            return result
        
        return wrapper
    return decorator 