from django.db import connection
from django.db.models.signals import post_migrate
from django.dispatch import receiver
import os

from django.db.models.signals import post_save
from django.contrib.auth.models import User
from .models import PerfilGamer, Conquista


@receiver(post_migrate)
def populate_initial_data(sender, **kwargs):
    if sender.name == 'apps.main.home':  # Verifica se o aplicativo é o seu
        # Caminho para os arquivos SQL
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        state_sql_file = os.path.join(base_dir, 'home/sql', 'home_state.sql')
        city_sql_file = os.path.join(base_dir, 'home/sql', 'home_city.sql')

        with connection.cursor() as cursor:
            # Verifica se a tabela State está vazia e popula se necessário
            cursor.execute("SELECT COUNT(*) FROM home_state;")
            if cursor.fetchone()[0] == 0:
                with open(state_sql_file, 'r', encoding='utf-8') as file:  # Adiciona encoding='utf-8'
                    sql = file.read()
                    cursor.execute(sql)

            # Verifica se a tabela City está vazia e popula se necessário
            cursor.execute("SELECT COUNT(*) FROM home_city;")
            if cursor.fetchone()[0] == 0:
                with open(city_sql_file, 'r', encoding='utf-8') as file:  # Adiciona encoding='utf-8'
                    sql = file.read()
                    cursor.execute(sql)


@receiver(post_save, sender=User)
def criar_perfil_gamer(sender, instance, created, **kwargs):
    if created:
        PerfilGamer.objects.create(user=instance)


@receiver(post_migrate)
def criar_conquistas_iniciais(sender, **kwargs):
    # Cria as conquistas iniciais, caso não existam
    conquistas = [
        {'codigo': 'primeiro_login', 'nome': 'Primeiro Login', 'descricao': 'Realizou o primeiro login no sistema'},
        {'codigo': '10_leiloes', 'nome': '10 Leilões', 'descricao': 'Criou 10 leilões no sistema'},
        {'codigo': 'primeira_solicitacao', 'nome': 'Primeira Solicitação', 'descricao': 'Fez sua primeira solicitação'},
        {'codigo': 'avatar_editado', 'nome': 'Avatar Editado', 'descricao': 'Editou seu avatar pela primeira vez'},
        {'codigo': 'endereco_cadastrado', 'nome': 'Endereço Cadastrado', 'descricao': 'Cadastrou seu endereço'},
        {'codigo': 'email_verificado', 'nome': 'Email Verificado', 'descricao': 'Verificou seu e-mail'},
        {'codigo': '2fa_ativado', 'nome': '2FA Ativado', 'descricao': 'Ativou a autenticação de dois fatores (2FA)'},
        {'codigo': 'idioma_trocado', 'nome': 'Idioma Trocado', 'descricao': 'Alterou o idioma do perfil'},
        {'codigo': 'primeiro_amigo', 'nome': 'Primeiro Amigo', 'descricao': 'Fez seu primeiro pedido de amizade'},
        {'codigo': 'primeiro_amigo_aceito', 'nome': 'Primeiro Amigo Aceito', 'descricao': 'Aceitou seu primeiro pedido de amizade'},
        {'codigo': 'primeira_compra', 'nome': 'Primeira Compra', 'descricao': 'Realizou sua primeira compra na loja'},
        {'codigo': 'primeiro_lance', 'nome': 'Primeiro Lance', 'descricao': 'Realizou seu primeiro lance em um leilão'},
        {'codigo': 'primeiro_cupom', 'nome': 'Primeiro Cupom', 'descricao': 'Aplicou um código promocional pela primeira vez'},
        {'codigo': 'primeiro_pedido_pagamento', 'nome': 'Primeira Contribuição', 'descricao': 'Iniciou sua primeira contribuição para o servidor'},
        {'codigo': 'primeiro_pagamento_concluido', 'nome': 'Patrocinador Oficial', 'descricao': 'Realizou seu primeiro apoio financeiro ao servidor'},
        {'codigo': 'primeira_transferencia_para_o_jogo', 'nome': 'Mestre da Economia', 'descricao': 'Realizou sua primeira transferência de moedas para o personagem no servidor'},
        {'codigo': 'primeira_transferencia_para_jogador', 'nome': 'Aliado Generoso', 'descricao': 'Enviou moedas para outro jogador pela primeira vez'},
        {'codigo': 'primeira_retirada_item', 'nome': 'Caçador de Tesouros', 'descricao': 'Retirou seu primeiro item do jogo para o inventário online'},
        {'codigo': 'primeira_insercao_item', 'nome': 'De Volta à Batalha', 'descricao': 'Inseriu um item do inventário online no servidor pela primeira vez'},
        {'codigo': 'primeira_troca_itens', 'nome': 'Comerciante Astuto', 'descricao': 'Realizou sua primeira troca de item entre personagens'},
        {'codigo': 'nivel_10', 'nome': 'Veterano Iniciante', 'descricao': 'Alcançou o nível 10 no sistema'},
        {'codigo': '50_lances', 'nome': 'Lanceador Experiente', 'descricao': 'Realizou 50 lances em leilões'},
        {'codigo': 'primeiro_vencedor_leilao', 'nome': 'Vencedor de Leilão', 'descricao': 'Venceu seu primeiro leilão'},
        {'codigo': '1000_xp', 'nome': 'Mestre da Experiência', 'descricao': 'Acumulou 1000 pontos de experiência'},
        {'codigo': '100_transacoes', 'nome': 'Mestre das Transações', 'descricao': 'Realizou 100 transações na carteira'},
        {'codigo': 'primeiro_bonus', 'nome': 'Bônus Recebido', 'descricao': 'Recebeu seu primeiro bônus de compra'},
        {'codigo': 'nivel_25', 'nome': 'Veterano Avançado', 'descricao': 'Alcançou o nível 25 no sistema'},
        {'codigo': 'primeira_solicitacao_resolvida', 'nome': 'Problema Resolvido', 'descricao': 'Teve sua primeira solicitação de suporte resolvida'},
        {'codigo': 'primeiro_personagem', 'nome': 'Primeiro Personagem', 'descricao': 'Criou seu primeiro personagem no servidor'},
        {'codigo': 'primeiro_clan', 'nome': 'Membro de Clã', 'descricao': 'Entrou em seu primeiro clã'},
        {'codigo': 'primeiro_castle', 'nome': 'Conquistador de Castelo', 'descricao': 'Participou da conquista de um castelo'},
        {'codigo': 'personagem_nivel_50', 'nome': 'Aventureiro Experiente', 'descricao': 'Possui um personagem de nível 50 ou superior'},
        {'codigo': 'personagem_nivel_80', 'nome': 'Guerreiro Veterano', 'descricao': 'Possui um personagem de nível 80 ou superior'},
        {'codigo': 'personagem_nobless', 'nome': 'Noblesse', 'descricao': 'Possui um personagem com status Noblesse'},
        {'codigo': 'personagem_hero', 'nome': 'Herói', 'descricao': 'Possui um personagem com status Hero'},
        {'codigo': 'primeiro_subclass', 'nome': 'Especialista', 'descricao': 'Possui um personagem com subclasse'},
        {'codigo': 'personagem_pvp_100', 'nome': 'PvP Iniciante', 'descricao': 'Possui um personagem com 100 ou mais kills PvP'},
        {'codigo': 'personagem_pvp_500', 'nome': 'PvP Experiente', 'descricao': 'Possui um personagem com 500 ou mais kills PvP'},
        {'codigo': 'personagem_pvp_1000', 'nome': 'PvP Master', 'descricao': 'Possui um personagem com 1000 ou mais kills PvP'},
        {'codigo': 'primeiro_ally', 'nome': 'Membro de Aliança', 'descricao': 'Entrou em sua primeira aliança'},
        {'codigo': 'personagem_online_24h', 'nome': 'Viciado', 'descricao': 'Possui um personagem com 24 horas ou mais de tempo online'},
        {'codigo': 'personagem_online_100h', 'nome': 'Dedicado', 'descricao': 'Possui um personagem com 100 horas ou mais de tempo online'},
        {'codigo': 'personagem_online_500h', 'nome': 'Veterano Online', 'descricao': 'Possui um personagem com 500 horas ou mais de tempo online'},
    ]

    for conquista in conquistas:
        # Se a conquista ainda não existir, cria uma nova
        if not Conquista.objects.filter(codigo=conquista['codigo']).exists():
            Conquista.objects.create(
                codigo=conquista['codigo'],
                nome=conquista['nome'],
                descricao=conquista['descricao']
            )
