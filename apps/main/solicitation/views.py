from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404, render
from django.views import View
from .models import Solicitation, SolicitationParticipant
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin


class SolicitationDashboardView(LoginRequiredMixin, View):
    def get(self, request, protocol):
        # Obtém a proposta de crédito pelo protocolo
        solicitation = get_object_or_404(Solicitation, protocol=protocol)

        # Obtém os participantes associados à solicitação
        participants = SolicitationParticipant.objects.filter(solicitation=solicitation)

        # Passa a proposta para o contexto
        context = {
            'solicitation': solicitation,
            'participants': participants,
        }

        return render(request, 'pages/solicitation_dashboard.html', context)


class SolicitationListView(LoginRequiredMixin, ListView):
    model = Solicitation
    template_name = 'pages/solicitation_list.html'  # Substitua pelo seu caminho de template
    context_object_name = 'solicitations'  # Nome da variável que conterá as solicitações no template
    paginate_by = 10  # Número de itens por página

    def get_queryset(self):
        # Aqui você pode adicionar filtros se necessário
        return Solicitation.objects.all()
