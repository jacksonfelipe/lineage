from django.db import models
from core.models import BaseModel
from apps.main.home.models import User
from django.core.exceptions import ValidationError
import zipfile, os, json, shutil
from django.conf import settings


class ChatGroup(BaseModel):
    group_name = models.CharField(max_length=255)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.message[:20]}"

    class Meta:
        verbose_name = 'Histórico dos Atendimentos'
        verbose_name_plural = 'Histórico dos Atendimentos'


class Theme(BaseModel):
    nome = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    descricao = models.TextField(blank=True)
    ativo = models.BooleanField(default=False)

    version = models.CharField(max_length=50, blank=True)
    author = models.CharField(max_length=100, blank=True)

    # Campo de upload para o arquivo ZIP
    upload = models.FileField(upload_to='themes/')

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def clean(self):
        # Valida se apenas um tema está ativo
        if self.ativo:
            active_themes = Theme.objects.filter(ativo=True).exclude(id=self.id)
            if active_themes.exists():
                raise ValidationError("Já existe um tema ativo. Desative o tema atual antes de ativar outro.")

    def save(self, *args, **kwargs):
        if self.ativo:
            # Desativa todos os outros temas ao ativar um novo
            Theme.objects.exclude(id=self.id).update(ativo=False)

        # Chama o processamento do upload, se houver
        if self.upload:
            self.processar_upload()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Tema"
        verbose_name_plural = "Temas"

    def delete(self, *args, **kwargs):
        # Remove o arquivo ZIP
        try:
            if self.upload and self.upload.path and os.path.isfile(self.upload.path):
                print(f"Removendo arquivo: {self.upload.path}")
                os.remove(self.upload.path)
            else:
                print(f"Arquivo não encontrado: {self.upload.path}")
        except Exception as e:
            print(f"Erro ao remover o arquivo: {e}")

        # Remove a pasta extraída do tema
        try:
            if self.slug:
                theme_folder_path = os.path.join(settings.BASE_DIR, 'themes/installed', self.slug)
                if os.path.isdir(theme_folder_path):
                    print(f"Removendo pasta: {theme_folder_path}")
                    shutil.rmtree(theme_folder_path)
                else:
                    print(f"Pasta não encontrada: {theme_folder_path}")
        except Exception as e:
            print(f"Erro ao remover a pasta: {e}")

        # Deleta a instância do banco
        super().delete(*args, **kwargs)

    def clean_upload(self):
        file = self.upload
        if file:
            # Limita o tamanho do arquivo para 10 MB
            if file.size > 10 * 1024 * 1024:
                raise ValidationError("O arquivo é muito grande. Tente um arquivo menor.")
            
            # Verifica se o arquivo é um ZIP válido
            if not zipfile.is_zipfile(file):
                raise ValidationError("O arquivo não é um arquivo ZIP válido.")
        return file

    def processar_upload(self):
        if self.upload:
            # Obter o arquivo enviado no campo upload
            upload_file = self.upload.file  # Acessa o arquivo como objeto BytesIO

            # Verifica se o arquivo ZIP é válido
            with zipfile.ZipFile(upload_file, 'r') as zip_ref:
                # Liste os arquivos dentro do ZIP
                file_names = zip_ref.namelist()
                print(file_names)  # Para fins de depuração, você pode remover isso depois.

                # Variáveis para o caminho do theme.json
                theme_json_path = None

                # Procurando por 'theme.json' em qualquer lugar dentro do ZIP
                for file_name in file_names:
                    if file_name.lower() == 'theme.json':  # Verifique se 'theme.json' existe
                        theme_json_path = file_name
                        break  # Encontre o primeiro match e pare de procurar

                if not theme_json_path:
                    raise ValidationError("Não foi encontrado um arquivo 'theme.json' no ZIP.")

                try:
                    # Lê o theme.json diretamente do arquivo ZIP
                    with zip_ref.open(theme_json_path) as f:
                        meta = json.load(f)

                    # Atualiza os dados do tema com informações do JSON
                    self.nome = meta.get('name', self.nome)
                    self.slug = meta.get('slug', self.slug)
                    self.version = meta.get('version', '')
                    self.author = meta.get('author', '')
                    self.descricao = meta.get('description', '')

                    # Criação da pasta onde o conteúdo do tema será extraído
                    theme_folder_path = os.path.join(settings.BASE_DIR, 'themes/installed', self.slug)

                    # Cria o diretório para armazenar os arquivos do tema, se não existir
                    os.makedirs(theme_folder_path, exist_ok=True)

                    # Extrai os arquivos do ZIP para o diretório específico
                    zip_ref.extractall(theme_folder_path)

                    # Se necessário, você pode adicionar mais lógica para organizar o conteúdo do tema

                except Exception as e:
                    raise ValidationError(f"Erro ao processar o arquivo do tema: {str(e)}")
