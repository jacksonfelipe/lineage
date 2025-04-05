from django.db import models
from core.models import BaseModel


class FAQ(BaseModel):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_public = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Pergunta Frequente'
        verbose_name_plural = 'Perguntas Frequentes'

        permissions = [
            ("can_view_index", "Can visualization view index"),
        ]

    def __str__(self):
        return self.question
    