from django.shortcuts import render
from functools import wraps
from .models import ApiEndpointToggle


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
