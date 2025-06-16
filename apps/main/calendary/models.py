from django.db import models
from django.contrib.auth import get_user_model
from core.models import BaseModel
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


User = get_user_model()


class Event(BaseModel):
    title = models.CharField(max_length=200)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    className = models.CharField(
        max_length=20,
        default='bg-red',
        choices=[
            ('bg-red', 'Vermelho'),
            ('bg-orange', 'Laranja'),
            ('bg-green', 'Verde'),
            ('bg-blue', 'Azul'),
            ('bg-purple', 'Roxo'),
            ('bg-info', 'Info'),
            ('bg-yellow', 'Amarelo'),
            ('bg-secondary', 'Cinza')
        ]
    )

    def clean(self):
        super().clean()
        if self.end_date < self.start_date:
            raise ValidationError(_('A data de término não pode ser anterior à data de início.'))

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
