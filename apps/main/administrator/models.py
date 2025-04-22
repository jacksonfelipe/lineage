from django.db import models
from core.models import BaseModel
from apps.main.home.models import User
from django.core.exceptions import ValidationError


class ChatGroup(BaseModel):
    group_name = models.CharField(max_length=255)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.message[:20]}"

    class Meta:
        verbose_name = 'Histórico dos Atendimentos'
        verbose_name_plural = 'Histórico dos Atendimentos'


class Theme(BaseModel):
    nome = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    descricao = models.TextField(blank=True)
    ativo = models.BooleanField(default=False)

    version = models.CharField(max_length=50, blank=True)
    author = models.CharField(max_length=100, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.ativo and Theme.objects.filter(ativo=True).exclude(id=self.id).exists():
            raise ValidationError("Já existe um tema ativo. Desative o tema atual antes de ativar outro.")

    def save(self, *args, **kwargs):
        if self.ativo:
            Theme.objects.exclude(id=self.id).update(ativo=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Tema"
        verbose_name_plural = "Temas"
