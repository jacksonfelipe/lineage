from django.core.management.base import BaseCommand, CommandError
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Migra arquivos do sistema de arquivos local para o S3'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa em modo de teste sem fazer alterações',
        )
        parser.add_argument(
            '--model',
            type=str,
            help='Migra apenas um modelo específico (ex: apps.lineage.server.models.IndexConfig)',
        )
        parser.add_argument(
            '--field',
            type=str,
            help='Migra apenas um campo específico (ex: imagem_banner)',
        )

    def handle(self, *args, **options):
        if not getattr(settings, 'USE_S3', False):
            raise CommandError('S3 não está habilitado. Configure USE_S3=True no settings.py')

        dry_run = options['dry_run']
        modelo_especifico = options['model']
        campo_especifico = options['field']

        if dry_run:
            self.stdout.write(
                self.style.WARNING('Executando em modo DRY-RUN - nenhuma alteração será feita')
            )

        # Lista de modelos que contêm arquivos
        modelos_com_arquivos = [
            ('apps.lineage.server.models.IndexConfig', 'imagem_banner'),
            ('apps.lineage.server.models.Apoiador', 'imagem'),
            ('apps.lineage.games.models.Prize', 'image'),
            ('apps.lineage.games.models.Item', 'image'),
            ('apps.main.home.models.SiteLogo', 'image'),
            ('apps.main.home.models.Conquista', 'icone'),
            ('apps.lineage.inventory.models.CustomItem', 'imagem'),
            ('apps.main.administrator.models.BackgroundSetting', 'image'),
            ('apps.lineage.roadmap.models.Roadmap', 'image'),
            ('apps.main.news.models.News', 'image'),
            ('apps.main.solicitation.models.SolicitationHistory', 'image'),
        ]

        # Filtra modelos se especificado
        if modelo_especifico:
            modelos_com_arquivos = [
                (m, f) for m, f in modelos_com_arquivos 
                if m == modelo_especifico
            ]
            if not modelos_com_arquivos:
                raise CommandError(f'Modelo {modelo_especifico} não encontrado')

        # Filtra campos se especificado
        if campo_especifico:
            modelos_com_arquivos = [
                (m, f) for m, f in modelos_com_arquivos 
                if f == campo_especifico
            ]
            if not modelos_com_arquivos:
                raise CommandError(f'Campo {campo_especifico} não encontrado')

        total_migrados = 0
        total_erros = 0
        total_ignorados = 0

        for modelo_path, campo_arquivo in modelos_com_arquivos:
            try:
                # Importa o modelo dinamicamente
                app_label, model_name = modelo_path.split('.')[-2:]
                modelo = self._get_model(app_label, model_name)
                
                self.stdout.write(f'\nMigrando {modelo_path}.{campo_arquivo}...')
                
                # Busca objetos com arquivos
                filtro = {f"{campo_arquivo}__isnull": False}
                objetos = modelo.objects.exclude(**filtro).exclude(**{campo_arquivo: ""})
                
                for obj in objetos:
                    try:
                        arquivo_atual = getattr(obj, campo_arquivo)
                        
                        if not arquivo_atual or not arquivo_atual.name:
                            continue
                        
                        # Verifica se já está no S3
                        if arquivo_atual.url.startswith('http'):
                            self.stdout.write(f'  ⚠ {obj} - Já está no S3')
                            total_ignorados += 1
                            continue
                        
                        # Verifica se arquivo existe localmente
                        if not os.path.exists(arquivo_atual.path):
                            self.stdout.write(
                                self.style.WARNING(f'  ⚠ {obj} - Arquivo local não encontrado: {arquivo_atual.path}')
                            )
                            total_ignorados += 1
                            continue
                        
                        if dry_run:
                            self.stdout.write(f'  🔍 {obj} - Seria migrado: {arquivo_atual.name}')
                            total_migrados += 1
                            continue
                        
                        # Lê e migra o arquivo
                        with open(arquivo_atual.path, 'rb') as f:
                            conteudo = f.read()
                        
                        # Salva no S3
                        arquivo_s3 = default_storage.save(arquivo_atual.name, ContentFile(conteudo))
                        
                        # Atualiza o objeto
                        setattr(obj, campo_arquivo, arquivo_s3)
                        obj.save(update_fields=[campo_arquivo])
                        
                        self.stdout.write(
                            self.style.SUCCESS(f'  ✓ {obj} - Migrado: {arquivo_s3}')
                        )
                        total_migrados += 1
                        
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'  ✗ {obj} - Erro: {str(e)}')
                        )
                        total_erros += 1
                        
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Erro ao processar {modelo_path}: {str(e)}')
                )
                total_erros += 1

        # Resumo final
        self.stdout.write('\n' + '='*50)
        self.stdout.write('RESUMO DA MIGRAÇÃO:')
        self.stdout.write(f'Arquivos migrados: {total_migrados}')
        self.stdout.write(f'Arquivos ignorados: {total_ignorados}')
        self.stdout.write(f'Erros: {total_erros}')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('\nMODO DRY-RUN: Nenhuma alteração foi feita')
            )

    def _get_model(self, app_label, model_name):
        """Importa um modelo dinamicamente"""
        from django.apps import apps
        return apps.get_model(app_label, model_name) 
    