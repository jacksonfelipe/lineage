from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.main.home.models import User
from core.models import BaseModel
from django.templatetags.static import static
import random
from .choices import *


class Prize(BaseModel):    
    # Campos básicos do prêmio
    name = models.CharField(max_length=255, verbose_name=_("Prize Name"))
    image = models.ImageField(upload_to='prizes/', null=True, blank=True, verbose_name=_("Image"))
    weight = models.PositiveIntegerField(default=1, help_text=_("Quanto maior o peso, maior a chance de ser sorteado."), verbose_name=_("Weight"))
    
    # Campos adicionais
    item_id = models.IntegerField(verbose_name=_("Item ID"))
    enchant = models.IntegerField(default=0, verbose_name=_("Enchant Level"))
    rarity = models.CharField(max_length=15, choices=RARITY_CHOICES, default='COMUM', verbose_name=_("Rarity"))
    
    # Método para retornar a URL da imagem
    def get_image_url(self):
        return self.image.url if self.image else static("roulette/images/default.png")

    def __str__(self):
        return f'{self.name} ({self.rarity})'

    class Meta:
        verbose_name = _("Prize")
        verbose_name_plural = _("Prizes")


class SpinHistory(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("User"))
    prize = models.ForeignKey(Prize, on_delete=models.CASCADE, verbose_name=_("Prize"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    def __str__(self):
        return f'{self.user.username} won {self.prize.name}'

    class Meta:
        verbose_name = _("Spin History")
        verbose_name_plural = _("Spin Histories")


class Bag(BaseModel):
    user = models.OneToOneField(User, related_name='bag', on_delete=models.CASCADE, verbose_name=_("User"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    def __str__(self):
        return f"Bag de {self.user.username}"

    class Meta:
        verbose_name = _("Bag")
        verbose_name_plural = _("Bags")


class BagItem(BaseModel):
    bag = models.ForeignKey(Bag, related_name='items', on_delete=models.CASCADE, verbose_name=_("Bag"))
    item_id = models.IntegerField(verbose_name=_("Item ID"))
    item_name = models.CharField(max_length=100, verbose_name=_("Item Name"))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_("Quantity"))
    enchant = models.IntegerField(default=0, verbose_name=_("Enchant Level"))
    added_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Added At"))

    class Meta:
        unique_together = ('bag', 'item_id', 'enchant')
        verbose_name = _("Bag Item")
        verbose_name_plural = _("Bag Items")

    def __str__(self):
        return f"{self.item_name} +{self.enchant} x{self.quantity} (Bag)"


class Item(BaseModel):
    name = models.CharField(max_length=100, verbose_name=_("Item Name"))
    enchant = models.IntegerField(default=0, verbose_name=_("Enchant Level"))
    item_id = models.IntegerField(verbose_name=_("Item ID"))
    image = models.ImageField(upload_to='items/', verbose_name=_("Image"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    rarity = models.CharField(max_length=20, choices=RARITY_CHOICES, verbose_name=_("Rarity"))
    can_be_populated = models.BooleanField(default=True, verbose_name=_("Can Be Populated"))
    
    def __str__(self):
        return f"{self.name} ({self.get_rarity_display()})"

    class Meta:
        verbose_name = _("Item")
        verbose_name_plural = _("Items")


class BoxType(BaseModel):
    name = models.CharField(max_length=100, verbose_name=_("Box Type Name"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price"))
    boosters_amount = models.PositiveIntegerField(default=5, verbose_name=_("Boosters Amount"))
    
    # Probabilidades por raridade (em %)
    chance_common = models.FloatField(default=60, verbose_name=_("Chance of Common"))
    chance_rare = models.FloatField(default=25, verbose_name=_("Chance of Rare"))
    chance_epic = models.FloatField(default=10, verbose_name=_("Chance of Epic"))
    chance_legendary = models.FloatField(default=5, verbose_name=_("Chance of Legendary"))

    max_epic_items = models.IntegerField(default=0, verbose_name=_("Max Epic Items"))
    max_legendary_items = models.IntegerField(default=0, verbose_name=_("Max Legendary Items"))
    allowed_items = models.ManyToManyField(Item, blank=True, related_name='allowed_in_boxes')

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

    class Meta:
        verbose_name = _("Box Type")
        verbose_name_plural = _("Box Types")


class Box(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("User"))
    box_type = models.ForeignKey(BoxType, on_delete=models.CASCADE, verbose_name=_("Box Type"))
    opened = models.BooleanField(default=False, verbose_name=_("Opened"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    def __str__(self):
        return f"Box de {self.box_type.name} - {self.user.username}"

    class Meta:
        verbose_name = _("Box")
        verbose_name_plural = _("Boxes")


class BoxItem(BaseModel):
    box = models.ForeignKey(Box, on_delete=models.CASCADE, related_name='items', verbose_name=_("Box"))
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name=_("Item"))
    probability = models.FloatField(default=1.0, verbose_name=_("Probability"))
    opened = models.BooleanField(default=False, verbose_name=_("Opened"))

    def __str__(self):
        return f"{self.item.name} ({'Aberto' if self.opened else 'Fechado'})"

    class Meta:
        verbose_name = _("Box Item")
        verbose_name_plural = _("Box Items")


class BoxItemHistory(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='box_item_history', verbose_name=_("User"))
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name=_("Item"))
    box = models.ForeignKey(Box, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Box"))
    rarity = models.CharField(max_length=20, choices=RARITY_CHOICES, verbose_name=_("Rarity"))
    enchant = models.IntegerField(default=0, verbose_name=_("Enchant Level"))
    obtained_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Obtained At"))

    def __str__(self):
        return f"{self.user.username} ganhou {self.item.name} +{self.enchant} [{self.rarity}]"

    class Meta:
        verbose_name = _("Box Item History")
        verbose_name_plural = _("Box Item Histories")


class Recompensa(BaseModel):
    TIPO_CHOICES = [
        ('NIVEL', 'Por Nível'),
        ('CONQUISTA', 'Por Conquista'),
        ('CONQUISTAS_MULTIPLAS', 'Por Quantidade de Conquistas'),
    ]

    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES, verbose_name=_("Tipo de Recompensa"))
    referencia = models.CharField(max_length=100, verbose_name=_("Referência"))  # nível ou código conquista
    item_id = models.IntegerField(verbose_name=_("Item ID"))
    item_name = models.CharField(max_length=100, verbose_name=_("Item Name"))
    enchant = models.IntegerField(default=0, verbose_name=_("Enchant"))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_("Quantidade"))

    class Meta:
        verbose_name = _("Recompensa")
        verbose_name_plural = _("Recompensas")

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.referencia} => {self.item_name} +{self.enchant} x{self.quantity}"
