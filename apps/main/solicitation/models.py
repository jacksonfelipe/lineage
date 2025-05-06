from django.db import models
from utils.protocol import create_protocol
from apps.main.home.models import User
from core.models import BaseModel
from .choices import STATUS_CHOICES


class Solicitation(BaseModel):
    protocol = models.CharField(max_length=30, unique=True, editable=False)  # Protocolo
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')  # Status
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='solicitations_user', blank=True, null=True)  # usuário

    def add_participant(self, user):
        """Adiciona um participante à proposta."""
        SolicitationParticipant.objects.get_or_create(solicitation=self, user=user)

    def is_participant(self, user):
        """Verifica se o usuário é um dos participantes da proposta."""
        return SolicitationParticipant.objects.filter(solicitation=self, user=user).exists()

    def save(self, *args, **kwargs):
        is_new = self._state.adding  # Verifica se o objeto está sendo criado
        if not self.protocol:
            self.protocol = create_protocol()
        super().save(*args, **kwargs)

        if is_new and self.user:  # Se a solicitação é nova e o usuário está definido
            SolicitationParticipant.objects.get_or_create(solicitation=self, user=self.user)

        SolicitationHistory.objects.create(solicitation=self, action='Credit solicitation created.')

    def __str__(self):
        return f'Solicitation {self.protocol} - {self.status}'
    
    class Meta:
        verbose_name = 'Solicitação'
        verbose_name_plural = 'Solicitação'
    

class SolicitationParticipant(BaseModel):
    solicitation = models.ForeignKey(Solicitation, on_delete=models.CASCADE, related_name='solicitation_participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='solicitations_users')

    class Meta:
        unique_together = ('solicitation', 'user')

    def __str__(self):
        return f'{self.user.username} - {self.solicitation.protocol}'
    
    class Meta:
        verbose_name = 'Participantes da Solicitação'
        verbose_name_plural = 'Participantes da Solicitação'


class SolicitationHistory(BaseModel):
    solicitation = models.ForeignKey(Solicitation, on_delete=models.CASCADE, related_name='solicitation_history')
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='solicitation_history_images/', null=True, blank=True)  # Adicionando campo de imagem
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # Adicionando o usuário que fez a alteração

    def __str__(self):
        return f'History for Solicitation {self.solicitation.protocol} - {self.timestamp}'

    class Meta:
        verbose_name = 'Histórico da Solicitação'
        verbose_name_plural = 'Históricos da Solicitação'
