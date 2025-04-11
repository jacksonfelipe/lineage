from django.db import models
from apps.main.home.models import User
from apps.lineage.wallet.models import Wallet, TransacaoWallet  # função que atualiza a wallet
from core.models import BaseModel
from .choices import *


class PedidoPagamento(BaseModel):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2)
    moedas_geradas = models.DecimalField(max_digits=10, decimal_places=2)
    metodo = models.CharField(max_length=100)  # Aumentado para comportar nomes mais longos
    status = models.CharField(max_length=20, default='PENDENTE')  # CONFIRMADO, FALHOU...
    data_criacao = models.DateTimeField(auto_now_add=True)

    def confirmar_pagamento(self):
        if self.status != 'CONFIRMADO':
            self.status = 'CONFIRMADO'
            self.save()

            wallet, _ = Wallet.objects.get_or_create(usuario=self.usuario)

            TransacaoWallet.objects.create(
                wallet=wallet,
                tipo='ENTRADA',
                valor=self.moedas_geradas,
                descricao='Compra de moedas via ' + self.metodo,
                origem='Sistema de Pagamento',
                destino='Wallet'
            )

            # Atualiza o saldo da carteira
            wallet.saldo += self.moedas_geradas
            wallet.save()

    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.username} - {self.status}"


class Pagamento(BaseModel):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    transaction_code = models.CharField(max_length=100, null=True, blank=True)
    pedido_pagamento = models.OneToOneField(
        PedidoPagamento, on_delete=models.SET_NULL, null=True, blank=True
    )
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pagamento {self.id} - {self.status}"


class WebhookLog(models.Model):
    tipo = models.CharField(max_length=100)
    data_id = models.CharField(max_length=100)
    payload = models.JSONField()
    recebido_em = models.DateTimeField(auto_now_add=True)
