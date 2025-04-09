from django.db import models
from core.models import BaseModel


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
