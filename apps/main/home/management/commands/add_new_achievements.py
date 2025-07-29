from django.core.management.base import BaseCommand
from apps.main.home.models import Conquista

class Command(BaseCommand):
    help = 'Adiciona as novas conquistas criativas ao banco de dados'

    def handle(self, *args, **options):
        # Lista das novas conquistas criativas
        novas_conquistas = [
            # Conquistas de Inventário
            {'codigo': 'colecionador_itens', 'nome': 'Colecionador de Itens', 'descricao': 'Possui 10 ou mais itens no inventário'},
            {'codigo': 'mestre_inventario', 'nome': 'Mestre do Inventário', 'descricao': 'Possui 50 ou mais itens no inventário'},
            {'codigo': 'trocador_incansavel', 'nome': 'Trocador Incansável', 'descricao': 'Realizou 10 ou mais trocas de itens'},
            
            # Conquistas de Carteira e Transferências
            {'codigo': 'gerenciador_economico', 'nome': 'Gerenciador Econômico', 'descricao': 'Realizou 20 ou mais transferências para o jogo'},
            {'codigo': 'benfeitor_comunitario', 'nome': 'Benfeitor Comunitário', 'descricao': 'Realizou 10 ou mais transferências para outros jogadores'},
            {'codigo': '250_transacoes', 'nome': 'Mestre das Transações', 'descricao': 'Realizou 250 transações na carteira'},
            {'codigo': '500_transacoes', 'nome': 'Expert das Transações', 'descricao': 'Realizou 500 transações na carteira'},
            
            # Conquistas de Bônus
            {'codigo': 'bonus_diario_7dias', 'nome': 'Fiel ao Bônus', 'descricao': 'Recebeu bônus diário por 7 dias consecutivos'},
            {'codigo': 'bonus_diario_30dias', 'nome': 'Viciado no Bônus', 'descricao': 'Recebeu bônus diário por 30 dias consecutivos'},
            {'codigo': 'bonus_mestre', 'nome': 'Mestre dos Bônus', 'descricao': 'Recebeu 10 ou mais bônus'},
            {'codigo': 'bonus_expert', 'nome': 'Expert dos Bônus', 'descricao': 'Recebeu 25 ou mais bônus'},
            
            # Conquistas de Patrocínio
            {'codigo': 'patrocinador_ouro', 'nome': 'Patrocinador Ouro', 'descricao': 'Realizou 5 ou mais pagamentos aprovados'},
            {'codigo': 'patrocinador_diamante', 'nome': 'Patrocinador Diamante', 'descricao': 'Realizou 10 ou mais pagamentos aprovados'},
            
            # Conquistas de Loja
            {'codigo': 'comprador_frequente', 'nome': 'Comprador Frequente', 'descricao': 'Realizou 5 ou mais compras na loja'},
            {'codigo': 'comprador_vip', 'nome': 'Comprador VIP', 'descricao': 'Realizou 15 ou mais compras na loja'},
            
            # Conquistas de Leilões
            {'codigo': 'leiloeiro_profissional', 'nome': 'Leiloeiro Profissional', 'descricao': 'Criou 25 ou mais leilões'},
            {'codigo': 'leiloeiro_mestre', 'nome': 'Leiloeiro Mestre', 'descricao': 'Criou 50 ou mais leilões'},
            {'codigo': 'lanceador_profissional', 'nome': 'Lanceador Profissional', 'descricao': 'Realizou 100 ou mais lances'},
            {'codigo': 'lanceador_mestre', 'nome': 'Lanceador Mestre', 'descricao': 'Realizou 200 ou mais lances'},
            {'codigo': 'vencedor_serie', 'nome': 'Vencedor em Série', 'descricao': 'Venceu 3 ou mais leilões'},
            {'codigo': 'vencedor_mestre', 'nome': 'Vencedor Mestre', 'descricao': 'Venceu 10 ou mais leilões'},
            
            # Conquistas de Cupons
            {'codigo': 'cupom_mestre', 'nome': 'Mestre dos Cupons', 'descricao': 'Aplicou 5 ou mais cupons promocionais'},
            {'codigo': 'cupom_expert', 'nome': 'Expert dos Cupons', 'descricao': 'Aplicou 15 ou mais cupons promocionais'},
            
            # Conquistas de Suporte
            {'codigo': 'solicitante_frequente', 'nome': 'Solicitante Frequente', 'descricao': 'Abriu 5 ou mais solicitações de suporte'},
            {'codigo': 'solicitante_expert', 'nome': 'Solicitante Expert', 'descricao': 'Abriu 15 ou mais solicitações de suporte'},
            {'codigo': 'resolvedor_problemas', 'nome': 'Resolvedor de Problemas', 'descricao': 'Teve 3 ou mais solicitações resolvidas'},
            {'codigo': 'resolvedor_mestre', 'nome': 'Resolvedor Mestre', 'descricao': 'Teve 10 ou mais solicitações resolvidas'},
            
            # Conquistas de Rede Social
            {'codigo': 'rede_social', 'nome': 'Rede Social', 'descricao': 'Tem 5 ou mais amigos aceitos'},
            {'codigo': 'rede_social_mestre', 'nome': 'Mestre da Rede Social', 'descricao': 'Tem 15 ou mais amigos aceitos'},
            
            # Conquistas de Nível
            {'codigo': 'nivel_50', 'nome': 'Veterano Experiente', 'descricao': 'Alcançou o nível 50 no sistema'},
            {'codigo': 'nivel_75', 'nome': 'Veterano Mestre', 'descricao': 'Alcançou o nível 75 no sistema'},
            {'codigo': 'nivel_100', 'nome': 'Lenda do Sistema', 'descricao': 'Alcançou o nível 100 no sistema'},
            
            # Conquistas de XP
            {'codigo': '5000_xp', 'nome': 'Mestre da Experiência', 'descricao': 'Acumulou 5000 pontos de experiência'},
            {'codigo': '10000_xp', 'nome': 'Lenda da Experiência', 'descricao': 'Acumulou 10000 pontos de experiência'},
        ]

        # Adiciona as novas conquistas
        for conquista in novas_conquistas:
            try:
                # Verifica se a conquista já existe
                if not Conquista.objects.filter(codigo=conquista['codigo']).exists():
                    Conquista.objects.create(
                        codigo=conquista['codigo'],
                        nome=conquista['nome'],
                        descricao=conquista['descricao']
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Conquista "{conquista["nome"]}" criada com sucesso')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️ Conquista "{conquista["nome"]}" já existe')
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Erro ao criar conquista "{conquista["nome"]}": {e}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'🎉 Processo de criação das novas conquistas concluído! Total: {len(novas_conquistas)} conquistas')
        ) 