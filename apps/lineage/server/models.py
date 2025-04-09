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
    trailer_video_id = models.CharField(max_length=100, blank=True, default="CsNutvmrHIA?si=2lF1z1jPFkf8uGJB")  # Aqui você pode colocar um valor padrão do YouTube ou deixar em branco.

    # Texto de jogadores online
    jogadores_online_texto = models.CharField(max_length=255, blank=True, default="jogadores online Agora")

    # Imagem do banner
    imagem_banner = models.ImageField(upload_to='banners/', blank=True, null=True)

    class Meta:
        verbose_name = "Configuração da Index"
        verbose_name_plural = "Configuração da Index"

    def save(self, *args, **kwargs):
        # Garantir que só existe um único registro
        if not self.pk and IndexConfig.objects.exists():
            raise ValidationError("Só pode existir um registro de configuração do servidor.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome_servidor
