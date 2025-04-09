from django.contrib import admin
from .models import PedidoPagamento
from core.admin import BaseModelAdmin


@admin.register(PedidoPagamento)
class PedidoPagamentoAdmin(BaseModelAdmin):
    list_display = ('usuario', 'valor_pago', 'moedas_geradas', 'metodo', 'status', 'data_criacao')
    list_filter = ('status', 'metodo', 'data_criacao')
    search_fields = ('usuario__username', 'metodo')
    readonly_fields = ('usuario', 'valor_pago', 'moedas_geradas', 'metodo', 'data_criacao')

    actions = ['confirmar_pagamentos']

    @admin.action(description='Confirmar pagamentos selecionados')
    def confirmar_pagamentos(self, request, queryset):
        total = 0
        for pedido in queryset:
            if pedido.status != 'CONFIRMADO':
                pedido.confirmar_pagamento()
                total += 1
        self.message_user(request, f"{total} pagamento(s) confirmado(s) com sucesso.")
