from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from .models import Auditor
from django.contrib.auth.decorators import permission_required


def auditor_data_view(request):
    try:
        limit = int(request.GET.get('limit', 10))  # Pega o limite da query string, ou usa 10 como padrão
        data = Auditor.objects.all().order_by('-date')[:limit].values(
            'date', 'path', 'total_time', 'python_time', 'db_time',
            'total_queries', 'method', 'user_agent', 'response_status_code'
        )
        return JsonResponse(list(data), safe=False)
    except Exception as e:
        return JsonResponse({'error': 'Erro ao buscar dados de auditoria'}, status=500)


class AuditorPageView(View):
    def get(self, request, *args, **kwargs):
        context = {
            'segment': 'middleware',
            'parent': 'logging',
        }
        return render(request, 'pages/auditor.html', context)
