from django.db import models
from apps.main.home.models import User
from core.models import BaseModel


class Wallet(BaseModel):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Carteira de {self.usuario.username} - Saldo: R${self.saldo}"


class TransacaoWallet(BaseModel):
    TIPO = [
        ('ENTRADA', 'Entrada'),
        ('SAIDA', 'Saída'),
    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transacoes')
    tipo = models.CharField(max_length=10, choices=TIPO)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.TextField(blank=True)
    data = models.DateTimeField(auto_now_add=True)

    origem = models.CharField(max_length=100, blank=True)  # Ex: "Pix", "Venda"
    destino = models.CharField(max_length=100, blank=True) # Ex: "Fulano", "MercadoPago"

    def __str__(self):
        return f"{self.tipo} de R${self.valor} - {self.data.strftime('%d/%m/%Y %H:%M')}"
