from django.db import models
from core.models import BaseModel
from django.core.exceptions import ValidationError


class ApiEndpointToggle(BaseModel):
    players_online = models.BooleanField(default=True)
    top_pvp = models.BooleanField(default=True)
    top_pk = models.BooleanField(default=True)
    top_clan = models.BooleanField(default=True)
    top_rich = models.BooleanField(default=True)
    top_online = models.BooleanField(default=True)
    top_level = models.BooleanField(default=True)
    olympiad_ranking = models.BooleanField(default=True)
    olympiad_all_heroes = models.BooleanField(default=True)
    olympiad_current_heroes = models.BooleanField(default=True)
    grandboss_status = models.BooleanField(default=True)
    raidboss_status = models.BooleanField(default=True)
    siege = models.BooleanField(default=True)
    siege_participants = models.BooleanField(default=True)
    boss_jewel_locations = models.BooleanField(default=True)

    class Meta:
        verbose_name = "API Endpoint Toggle"
        verbose_name_plural = "API Endpoint Toggles"

    def __str__(self):
        return "API Endpoint Configuration"


class IndexConfig(BaseModel):
    # Nome do servidor
    nome_servidor = models.CharField(max_length=100, default="Lineage 2 PDL")

    # Descrição do servidor
    descricao_servidor = models.CharField(max_length=255, blank=True, default="Onde Lendas Nascem, Heróis Lutam e a Glória É Eterna.")

    # Links importantes
    link_patch = models.URLField(default="https://pdl.denky.dev.br/")
    link_cliente = models.URLField(default="https://pdl.denky.dev.br/")
    link_discord = models.URLField(default="https://pdl.denky.dev.br/")

    # Trailer
    trailer_video_id = models.CharField(max_length=100, blank=True, default="CsNutvmrHIA?si=2lF1z1jPFkf8uGJB")

    # Texto de jogadores online
    jogadores_online_texto = models.CharField(max_length=255, blank=True, default="jogadores online Agora")

    # Imagem do banner
    imagem_banner = models.ImageField(upload_to='banners/', blank=True, null=True)

    class Meta:
        verbose_name = "Configuração da Index"
        verbose_name_plural = "Configuração da Index"

    def save(self, *args, **kwargs):
        if not self.pk:  # Se não estiver sendo atualizado (novo objeto)
            if IndexConfig.objects.exists():
                raise ValidationError("Só pode existir um registro de configuração do servidor.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome_servidor


class IndexConfigTranslation(BaseModel):
    LANGUAGES = [
        ('pt', 'Português'),
        ('en', 'English'),
        ('es', 'Español'),
    ]

    config = models.ForeignKey(IndexConfig, on_delete=models.CASCADE, related_name='translations')
    language = models.CharField(max_length=5, choices=LANGUAGES)
    nome_servidor = models.CharField(max_length=100)
    descricao_servidor = models.CharField(max_length=255, blank=True)
    jogadores_online_texto = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ('config', 'language')
        verbose_name = 'Tradução da Configuração da Index'
        verbose_name_plural = 'Traduções da Configuração da Index'

    def __str__(self):
        return f"{self.nome_servidor} ({self.language})"


class ServicePrice(BaseModel):
    SERVICO_CHOICES = [
        ('CHANGE_NICKNAME', 'Alterar Nickname'),
        ('CHANGE_SEX', 'Alterar Sexo'),
    ]

    servico = models.CharField(max_length=30, choices=SERVICO_CHOICES, unique=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2, default=10.00)

    def __str__(self):
        return f"{self.get_servico_display()} - R${self.preco}"

    @classmethod
    def create_default(cls):
        # Verifica se já existe um registro. Se não, cria o registro com o preço padrão.
        if not cls.objects.exists():
            cls.objects.create(servico='CHANGE_NICKNAME', preco=10.00)
            cls.objects.create(servico='CHANGE_SEX', preco=10.00)


class ActiveAdenaExchangeItem(BaseModel):
    item_type = models.PositiveIntegerField(help_text="ID do item de troca de Adena")
    value_item = models.PositiveIntegerField(default=1_000_000, help_text="Valor que cada item representa em Adena")
    active = models.BooleanField(default=False, help_text="Marcar como ativo para ser utilizado no cálculo")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Item de Troca de Adena Ativo"
        verbose_name_plural = "Itens de Troca de Adena Ativos"

    def __str__(self):
        status = "Ativo" if self.active else "Inativo"
        return f"Item {self.item_type} - {status}"
