from django.db import models
from django.core.exceptions import ValidationError
from utils.protocol import create_protocol

from apps.main.home.models import User
from core.models import BaseModel

from .choices import STATUS_CHOICES, STAGE_CHOICES


class Solicitation(BaseModel):
    protocol = models.CharField(max_length=30, unique=True, editable=False)  # Protocolo
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')  # Status
    client = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='solicitations_client', blank=True, null=True)  # cliente

    def add_participant(self, user):
        """Adiciona um participante à proposta."""
        SolicitationParticipant.objects.get_or_create(solicitation=self, user=user)

    def is_participant(self, user):
        """Verifica se o usuário é um dos participantes da proposta."""
        return SolicitationParticipant.objects.filter(solicitation=self, user=user).exists()

    def save(self, *args, **kwargs):
        if not self.protocol:
            self.protocol = create_protocol()
        super().save(*args, **kwargs)

        if not hasattr(self, 'tasks'):
            self.create_default_tasks()

        SolicitationHistory.objects.create(solicitation=self, action='Credit solicitation created.')

    def create_default_tasks(self):
        stages = [
            ('registration', 'Registration'),
            ('validation', 'Validation (Email/SMS)'),
            ('finalization', 'Finalization'),
        ]

        for index, (stage, description) in enumerate(stages):
            SolicitationTask.objects.create(
                solicitation=self,
                description=description,
                stage=stage,
                sequence=index + 1
            )

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

    def __str__(self):
        return f'History for Solicitation {self.solicitation.protocol} - {self.timestamp}'
    
    class Meta:
        verbose_name = 'Histórico da Solicitação'
        verbose_name_plural = 'Históricos da Solicitação'


class SolicitationTask(BaseModel):
    solicitation = models.ForeignKey(Solicitation, on_delete=models.CASCADE, related_name='solicitation_tasks')  # Proposta de crédito (chave estrangeira)
    description = models.CharField(max_length=255)  # Descrição
    stage = models.CharField(max_length=30, choices=STAGE_CHOICES)  # Etapa (com opções de escolha)
    sequence = models.PositiveIntegerField()  # Sequência
    is_completed = models.BooleanField(default=False)  # Concluída
    due_date = models.DateTimeField(null=True, blank=True)  #

    class Meta:
        ordering = ['sequence']

    def save(self, *args, **kwargs):
        # Verifica se a tarefa atual pode ser marcada como concluída
        if self.is_completed:
            previous_task = (
                SolicitationTask.objects
                .filter(solicitation=self.solicitation, sequence=self.sequence - 1)
                .first()
            )
            if previous_task and not previous_task.is_completed:
                raise ValidationError(
                    f"You cannot complete the task '{self.description}' until the previous task '{previous_task.description}' is completed."
                )
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Task for Solicitation {self.solicitation.protocol} - Stage: {self.stage} - {"Completed" if self.is_completed else "Pending"}'
    
    class Meta:
        verbose_name = 'Tarefa da Solicitação'
        verbose_name_plural = 'Tarefas da Solicitação'
