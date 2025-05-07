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
        {'codigo': 'primeiro_amigo_aceito', 'nome': 'Primeiro Amigo Aceito', 'descricao': 'Aceitou seu primeiro pedido de amizade'}
    ]

    for conquista in conquistas:
        # Se a conquista ainda não existir, cria uma nova
        if not Conquista.objects.filter(codigo=conquista['codigo']).exists():
            Conquista.objects.create(
                codigo=conquista['codigo'],
                nome=conquista['nome'],
                descricao=conquista['descricao']
            )
