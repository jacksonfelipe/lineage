from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404, render
from django.views import View
from .models import Solicitation, SolicitationParticipant
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .forms import SolicitationForm
from django.contrib import messages
from django.shortcuts import redirect
from utils.notifications import send_notification


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


class SolicitationCreateView(LoginRequiredMixin, CreateView):
    model = Solicitation
    form_class = SolicitationForm
    template_name = 'pages/solicitation_create.html'
    success_url = reverse_lazy('solicitation:solicitation_list')

    def dispatch(self, request, *args, **kwargs):
        if Solicitation.objects.filter(user=request.user, status='pending').exists():
            messages.warning(request, "Você já possui uma solicitação pendente. Aguarde o processamento antes de criar uma nova.")
            return redirect('solicitation:solicitation_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)

        # Envia notificação para os staffs
        send_notification(
            user=None,  # None para broadcast para staff
            notification_type='staff',
            message='Relatório sigiloso disponível.',
            created_by=self.request.user
        )

        return response
