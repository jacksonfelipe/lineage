from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404, render
from django.views import View
from .models import CreditSolicitation, SolicitationParticipant
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin


class CreditSolicitationDashboardView(LoginRequiredMixin, View):
    def get(self, request, protocol):
        # Obtém a proposta de crédito pelo protocolo
        solicitation = get_object_or_404(CreditSolicitation, protocol=protocol)

        # Obtém os participantes associados à proposta
        participants = SolicitationParticipant.objects.filter(solicitation=solicitation)

        # Passa a proposta para o contexto
        context = {
            'solicitation': solicitation,
            'participants': participants,
        }

        return render(request, 'pages/credit_solicitation_dashboard.html', context)


class CreditSolicitationListView(LoginRequiredMixin, ListView):
    model = CreditSolicitation
    template_name = 'pages/credit_solicitation_list.html'  # Substitua pelo seu caminho de template
    context_object_name = 'solicitations'  # Nome da variável que conterá as solicitações no template
    paginate_by = 10  # Número de itens por página

    def get_queryset(self):
        # Aqui você pode adicionar filtros se necessário
        return CreditSolicitation.objects.all()
