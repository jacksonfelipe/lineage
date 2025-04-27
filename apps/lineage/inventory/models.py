from django.db import models
from apps.main.home.models import User
from core.models import BaseModel


class Inventory(BaseModel):
    user = models.ForeignKey(User, related_name='inventories', on_delete=models.CASCADE)
    account_name = models.CharField(max_length=100)
    character_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.character_name} ({self.account_name})"


class InventoryItem(BaseModel):
    inventory = models.ForeignKey(Inventory, related_name='items', on_delete=models.CASCADE)
    item_id = models.IntegerField()  # ID do item no banco do Lineage
    item_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=1)
    enchant = models.IntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('inventory', 'item_id')  # Garantir que o item seja único no inventário

    def __str__(self):
        return f"{self.item_name} x{self.quantity}"


class BlockedServerItem(BaseModel):
    item_id = models.PositiveIntegerField(unique=True, help_text="ID do item bloqueado")
    reason = models.CharField(max_length=255, blank=True, help_text="Motivo do bloqueio (opcional)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Item Bloqueado para Retirada"
        verbose_name_plural = "Itens Bloqueados para Retirada"

    def __str__(self):
        return f"Item ID: {self.item_id} - {self.reason if self.reason else 'Sem motivo específico'}"


class CustomItem(BaseModel):
    nome = models.CharField(max_length=255, unique=True)  # Nome do item
    imagem = models.ImageField(upload_to='itens_customizados/', null=True, blank=True)  # Imagem do item

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Item Customizado'
        verbose_name_plural = 'Itens Customizados'
