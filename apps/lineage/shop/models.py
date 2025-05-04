from django.db import models
from django.utils import timezone
from apps.main.home.models import User
from core.models import BaseModel
from apps.lineage.server.models import Apoiador


class ShopItem(BaseModel):
    nome = models.CharField(max_length=100)
    item_id = models.PositiveIntegerField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade = models.PositiveIntegerField(default=1)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nome} ({self.quantidade}x) — R${self.preco}"


class PromotionCode(BaseModel):
    codigo = models.CharField(max_length=50, unique=True)
    desconto_percentual = models.DecimalField(max_digits=5, decimal_places=2)
    ativo = models.BooleanField(default=True)
    validade = models.DateTimeField(null=True, blank=True)
    apoiador = models.ForeignKey('server.Apoiador', null=True, blank=True, on_delete=models.SET_NULL)

    def is_valido(self):
        if not self.ativo:
            return False
        if self.validade and timezone.now() > self.validade:
            return False
        return True

    def __str__(self):
        return f"{self.codigo} — {self.desconto_percentual}%"


class ShopPackage(BaseModel):
    nome = models.CharField(max_length=100)
    preco_total = models.DecimalField(max_digits=10, decimal_places=2)
    itens = models.ManyToManyField(ShopItem, through='ShopPackageItem')
    ativo = models.BooleanField(default=True)
    promocao = models.ForeignKey(
        PromotionCode, null=True, blank=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return f"{self.nome} — R${self.preco_total}"


class ShopPackageItem(BaseModel):
    pacote = models.ForeignKey(ShopPackage, on_delete=models.CASCADE)
    item = models.ForeignKey(ShopItem, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.pacote.nome} — {self.item.nome} x{self.quantidade}"


class Cart(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    itens = models.ManyToManyField(ShopItem, through='CartItem')
    pacotes = models.ManyToManyField(ShopPackage, through='CartPackage')
    promocao_aplicada = models.ForeignKey(PromotionCode, null=True, blank=True, on_delete=models.SET_NULL)

    def calcular_total(self):
        total = sum(ci.item.preco * ci.quantidade for ci in self.cartitem_set.all())
        total += sum(cp.pacote.preco_total * cp.quantidade for cp in self.cartpackage_set.all())
        if self.promocao_aplicada and self.promocao_aplicada.is_valido():
            total *= (1 - (self.promocao_aplicada.desconto_percentual / 100))
        return total

    def limpar(self):
        self.itens.clear()
        self.pacotes.clear()
        self.promocao_aplicada = None
        self.save()

    def __str__(self):
        return f"Carrinho de {self.user.username}"


class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    item = models.ForeignKey(ShopItem, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantidade}x {self.item.nome} (Carrinho de {self.cart.user.username})"


class CartPackage(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    pacote = models.ForeignKey(ShopPackage, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantidade}x {self.pacote.nome} (Carrinho de {self.cart.user.username})"


class ShopPurchase(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    character_name = models.CharField(max_length=100)
    total_pago = models.DecimalField(max_digits=10, decimal_places=2)
    promocao_aplicada = models.ForeignKey(PromotionCode, null=True, blank=True, on_delete=models.SET_NULL)
    apoiador = models.ForeignKey(Apoiador, null=True, blank=True, on_delete=models.SET_NULL)
    data_compra = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Se houver promoção, tenta vincular ao apoiador automaticamente
        if self.promocao_aplicada and self.promocao_aplicada.apoiador:
            self.apoiador = self.promocao_aplicada.apoiador
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Compra de {self.user.username} — R${self.total_pago} — {self.data_compra.strftime('%d/%m/%Y %H:%M')}"
