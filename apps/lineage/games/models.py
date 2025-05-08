from django.db import models
from apps.main.home.models import User
from core.models import BaseModel
from django.templatetags.static import static
from .choices import *


class Prize(BaseModel):    
    # Campos básicos do prêmio
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='prizes/', null=True, blank=True)
    weight = models.PositiveIntegerField(default=1, help_text="Quanto maior o peso, maior a chance de ser sorteado.")
    
    # Campos adicionais
    item_id = models.IntegerField()
    enchant = models.IntegerField(default=0)
    rarity = models.CharField(max_length=8, choices=RARITY_CHOICES, default='COMUM')
    
    # Método para retornar a URL da imagem
    def get_image_url(self):
        return self.image.url if self.image else static("roulette/images/default.png")

    def __str__(self):
        return f'{self.name} ({self.rarity})'


class SpinHistory(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prize = models.ForeignKey(Prize, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} won {self.prize.name}'


class Bag(BaseModel):
    user = models.OneToOneField(User, related_name='bag', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bag de {self.user.username}"


class BagItem(BaseModel):
    bag = models.ForeignKey(Bag, related_name='items', on_delete=models.CASCADE)
    item_id = models.IntegerField()
    item_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=1)
    enchant = models.IntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('bag', 'item_id', 'enchant')

    def __str__(self):
        return f"{self.item_name} +{self.enchant} x{self.quantity} (Bag)"
