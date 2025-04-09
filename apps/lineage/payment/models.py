from django.db import models
from apps.main.home.models import User
from apps.lineage.wallet.models import Wallet, TransacaoWallet  # função que atualiza a wallet
from core.models import BaseModel


class PedidoPagamento(BaseModel):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2)
    moedas_geradas = models.DecimalField(max_digits=10, decimal_places=2)
    metodo = models.CharField(max_length=50)  # ex: 'Pix', 'MercadoPago'
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
