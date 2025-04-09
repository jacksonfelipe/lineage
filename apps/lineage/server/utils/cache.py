from django.core.cache import cache
import hashlib
import json


def cache_lineage_result(timeout=300):
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Gera uma chave única com base na função + argumentos
            key_base = f"{func.__module__}.{func.__name__}:{json.dumps(args)}:{json.dumps(kwargs)}"
            key = f"lineage_cache:{hashlib.md5(key_base.encode()).hexdigest()}"

            # Tenta pegar do cache
            cached = cache.get(key)
            if cached is not None:
                return cached

            # Se não tiver, executa e armazena no cache
            result = func(*args, **kwargs)
            cache.set(key, result, timeout=timeout)
            return result
        return wrapper
    return decorator
