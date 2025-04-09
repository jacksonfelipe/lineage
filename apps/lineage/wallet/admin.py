from django.contrib import admin
from .models import Wallet, TransacaoWallet
from core.admin import BaseModelAdmin


@admin.register(Wallet)
class WalletAdmin(BaseModelAdmin):
    list_display = ['usuario', 'saldo']

@admin.register(TransacaoWallet)
class TransacaoWalletAdmin(BaseModelAdmin):
    list_display = ['wallet', 'tipo', 'valor', 'descricao', 'data']
    list_filter = ['tipo', 'data']
