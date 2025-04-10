from django.contrib import admin
from django.utils.html import format_html
from .models import PedidoPagamento, Pagamento
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


@admin.register(Pagamento)
class PagamentoAdmin(BaseModelAdmin):
    list_display = ('id', 'usuario', 'valor', 'status', 'transaction_code', 'pedido_link', 'data_criacao')
    list_filter = ('status', 'data_criacao')
    search_fields = ('usuario__username', 'transaction_code')
    ordering = ('-data_criacao',)
    readonly_fields = ('data_criacao', 'transaction_code')

    fieldsets = (
        (None, {
            'fields': ('usuario', 'valor', 'status', 'transaction_code', 'pedido_pagamento', 'data_criacao')
        }),
    )

    def pedido_link(self, obj):
        if obj.pedido_pagamento:
            return format_html('<a href="/admin/payment/pedidopagamento/{}/change/">Ver Pedido</a>', obj.pedido_pagamento.id)
        return '-'
    pedido_link.short_description = "Pedido"
