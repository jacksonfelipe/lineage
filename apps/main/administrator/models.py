from django.db import models
from core.models import BaseModel
from apps.main.home.models import User
from django.core.exceptions import ValidationError
import zipfile, os, json, shutil
from django.conf import settings
from django.utils.text import slugify


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
        if not self.upload:
            return

        upload_file = self.upload.file  # Objeto BytesIO

        if not zipfile.is_zipfile(upload_file):
            raise ValidationError("O arquivo não é um ZIP válido.")

        with zipfile.ZipFile(upload_file, 'r') as zip_ref:
            file_names = zip_ref.namelist()
            print(file_names)

            # Segurança: extensões permitidas
            extensoes_permitidas = ['.html', '.css', '.js', '.json', '.png', '.jpg', '.jpeg', '.svg', '.woff', '.ttf', '.map']

            for member in zip_ref.infolist():
                ext = os.path.splitext(member.filename)[1].lower()
                if ext and ext not in extensoes_permitidas:
                    raise ValidationError(f"Arquivo com extensão não permitida: {ext}")

                extracted_path = os.path.join(settings.BASE_DIR, 'themes/installed', self.slug, member.filename)
                if not os.path.realpath(extracted_path).startswith(
                    os.path.realpath(os.path.join(settings.BASE_DIR, 'themes/installed', self.slug))
                ):
                    raise ValidationError("O tema contém arquivos em caminhos não permitidos.")

            # Procurando por theme.json
            theme_json_path = next(
                (f for f in file_names if f.lower().endswith('theme.json')),
                None
            )
            if not theme_json_path:
                raise ValidationError("O arquivo 'theme.json' não foi encontrado.")

            try:
                with zip_ref.open(theme_json_path) as f:
                    meta = json.load(f)

                obrigatorios = ['name', 'slug']
                for campo in obrigatorios:
                    if campo not in meta:
                        raise ValidationError(f"O campo obrigatório '{campo}' está ausente no theme.json.")

                # Atualiza os dados do tema
                self.nome = meta.get('name', self.nome)
                self.slug = slugify(meta.get('slug', self.slug))
                self.version = meta.get('version', '')
                self.author = meta.get('author', '')
                self.descricao = meta.get('description', '')

                # Caminho do tema
                theme_folder_path = os.path.join(settings.BASE_DIR, 'themes/installed', self.slug)

                # Apaga a pasta existente, se houver
                if os.path.exists(theme_folder_path):
                    shutil.rmtree(theme_folder_path)

                # Cria a nova pasta e extrai
                os.makedirs(theme_folder_path, exist_ok=False)
                zip_ref.extractall(theme_folder_path)

            except json.JSONDecodeError:
                raise ValidationError("Erro ao interpretar o arquivo theme.json. Verifique se o JSON está bem formado.")
            except Exception as e:
                raise ValidationError(f"Erro ao processar o arquivo do tema: {str(e)}")