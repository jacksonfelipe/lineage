from django.contrib import admin
from .models import Wallet, TransacaoWallet, TransacaoBonus, CoinConfig, CoinPurchaseBonus
from core.admin import BaseModelAdmin


@admin.register(Wallet)
class WalletAdmin(BaseModelAdmin):
    list_display = ['usuario', 'saldo', 'saldo_bonus']


@admin.register(TransacaoWallet)
class TransacaoWalletAdmin(BaseModelAdmin):
    list_display = ['wallet', 'tipo', 'valor', 'descricao', 'data']
    list_filter = ['tipo', 'data']


@admin.register(TransacaoBonus)
class TransacaoBonusAdmin(BaseModelAdmin):
    list_display = ['wallet', 'tipo', 'valor', 'descricao', 'data']
    list_filter = ['tipo', 'data']


@admin.register(CoinConfig)
class CoinConfigAdmin(BaseModelAdmin):
    list_display = ('nome', 'coin_id', 'multiplicador', 'ativa')
    list_filter = ('ativa',)


@admin.register(CoinPurchaseBonus)
class CoinPurchaseBonusAdmin(BaseModelAdmin):
    list_display = ('descricao', 'valor_minimo', 'valor_maximo', 'bonus_percentual', 'ativo', 'ordem')
    list_filter = ('ativo', 'bonus_percentual')
    list_editable = ('ativo', 'ordem')
    search_fields = ('descricao',)
    ordering = ('ordem', 'valor_minimo')
    
    fieldsets = (
        ('Configuração Básica', {
            'fields': ('descricao', 'ativo', 'ordem')
        }),
        ('Faixa de Valores', {
            'fields': ('valor_minimo', 'valor_maximo'),
            'description': 'Configure a faixa de valores para aplicar o bônus'
        }),
        ('Bônus', {
            'fields': ('bonus_percentual',),
            'description': 'Percentual de bônus a ser aplicado'
        }),
    )
