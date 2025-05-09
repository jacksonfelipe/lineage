from django.shortcuts import render
from django.db.models import Sum
from apps.lineage.inventory.models import InventoryLog
from django.utils.timezone import now, timedelta
import json
from decimal import Decimal
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def relatorio_movimentacoes_inventario(request):
    dias = 15
    data_inicio = now() - timedelta(days=dias)

    logs = InventoryLog.objects.filter(timestamp__gte=data_inicio)

    # Agrupamento por dia
    agrupado_por_dia = (
        logs.extra(select={'dia': "DATE(timestamp)"}).
        values('dia', 'acao').
        annotate(total=Sum('quantity')).
        order_by('dia')
    )

    dias_labels = sorted(set(log['dia'] for log in agrupado_por_dia))
    acoes = ['RETIROU_DO_JOGO', 'INSERIU_NO_JOGO', 'TROCA_ENTRE_PERSONAGENS', 'RECEBEU_TROCA', 'BAG_PARA_INVENTARIO']

    dados_por_acao = {acao: [0] * len(dias_labels) for acao in acoes}

    for log in agrupado_por_dia:
        dia = log['dia']
        idx = dias_labels.index(dia)
        acao = log['acao']
        if acao in dados_por_acao:
            dados_por_acao[acao][idx] = int(log['total'])

    total_retirado = sum(dados_por_acao['RETIROU_DO_JOGO'])
    total_inserido = sum(dados_por_acao['INSERIU_NO_JOGO'])
    total_troca = sum(dados_por_acao['TROCA_ENTRE_PERSONAGENS'])
    total_recebido = sum(dados_por_acao['RECEBEU_TROCA'])
    total_bag_para_inventario = sum(dados_por_acao['BAG_PARA_INVENTARIO'])

    contexto = {
        'labels': json.dumps(dias_labels),
        'total_retirado': total_retirado,
        'total_inserido': total_inserido,
        'total_troca': total_troca,
        'total_recebido': total_recebido,
        'total_bag_para_inventario': total_bag_para_inventario,
    }

    return render(request, 'reports/relatorio_movimentacoes_inventario.html', contexto)
