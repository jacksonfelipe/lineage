from django.shortcuts import render
from functools import wraps
from .models import ApiEndpointToggle
from django.http import JsonResponse


def endpoint_enabled(endpoint_field):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            toggle = ApiEndpointToggle.objects.first()
            if not toggle or not getattr(toggle, endpoint_field, False):
                return render(request, "errors/404.html", status=404)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def safe_json_response(func):
    def wrapper(*args, **kwargs):
        data = func(*args, **kwargs)
        if data is None:
            return JsonResponse({"error": "Falha ao obter dados do banco de dados"}, status=500)
        return JsonResponse(data, safe=False)
    return wrapper
