from django.db import models
from apps.main.home.models import User
from core.models import BaseModel
from django.templatetags.static import static
import random
from .choices import *


class Prize(BaseModel):    
    # Campos básicos do prêmio
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='prizes/', null=True, blank=True)
    weight = models.PositiveIntegerField(default=1, help_text="Quanto maior o peso, maior a chance de ser sorteado.")
    
    # Campos adicionais
    item_id = models.IntegerField()
    enchant = models.IntegerField(default=0)
    rarity = models.CharField(max_length=15, choices=RARITY_CHOICES, default='COMUM')
    
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


class Item(BaseModel):
    name = models.CharField(max_length=100)
    enchant = models.IntegerField(default=0)
    item_id = models.IntegerField()
    image = models.ImageField(upload_to='items/')
    description = models.TextField(blank=True)
    rarity = models.CharField(max_length=20, choices=RARITY_CHOICES)
    
    def __str__(self):
        return f"{self.name} ({self.get_rarity_display()})"


class BoxType(BaseModel):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    boosters_amount = models.PositiveIntegerField(default=5)
    
    # Probabilidades por raridade (em %)
    chance_common = models.FloatField(default=60)
    chance_rare = models.FloatField(default=25)
    chance_epic = models.FloatField(default=10)
    chance_legendary = models.FloatField(default=5)

    def __str__(self):
        return self.name

    def get_rarity_by_chance(self):
        roll = random.uniform(0, 100)
        if roll <= self.chance_legendary:
            return 'legendary'
        elif roll <= self.chance_legendary + self.chance_epic:
            return 'epic'
        elif roll <= self.chance_legendary + self.chance_epic + self.chance_rare:
            return 'rare'
        return 'common'


class Box(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    box_type = models.ForeignKey(BoxType, on_delete=models.CASCADE)
    opened = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Box de {self.box_type.name} - {self.user.username}"


class BoxItem(BaseModel):
    box = models.ForeignKey(Box, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    probability = models.FloatField(default=1.0)
    opened = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.item.name} ({'Aberto' if self.opened else 'Fechado'})"
