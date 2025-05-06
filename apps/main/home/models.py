from django.contrib.auth.models import AbstractUser
from django.db import models
from core.models import BaseModel, BaseModelAbstract
from .utils import validate_cpf, remove_cpf_mask
from encrypted_fields.encrypted_fields import *
from encrypted_fields.encrypted_files import *
from utils.choices import *
from django.core.validators import validate_email
from .validators import validate_ascii_username
from django_ckeditor_5.fields import CKEditor5Field
from django_otp.plugins.otp_totp.models import TOTPDevice


class User(BaseModel, AbstractUser):
    username = models.CharField(
        max_length=16,
        unique=True,
        verbose_name="nome de usuário",
        validators=[validate_ascii_username],
        help_text="Use apenas letras e números. Sem espaços ou símbolos."
    )

    email = models.EmailField(
        unique=True,
        verbose_name="email",
        validators=[validate_email]
    )

    avatar = EncryptedImageField(upload_to="avatars", verbose_name="foto de perfil", null=True, blank=True)
    bio = EncryptedTextField(verbose_name='biografia', blank=True, null=True, max_length=500)
    cpf = EncryptedCharField(verbose_name='CPF', max_length=14, blank=True, null=True, validators=[validate_cpf])
    gender = EncryptedCharField(verbose_name='Gênero', max_length=50, choices=GENDER_CHOICES, blank=True, null=True)
    
    is_email_verified = models.BooleanField(default=False)
    is_2fa_enabled = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Remove a máscara do CPF antes de salvar no banco
        if self.cpf:
            self.cpf = remove_cpf_mask(self.cpf)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'


class AddressUser(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    street = EncryptedCharField(max_length=255)
    number = EncryptedCharField(max_length=10, blank=True)  # Adicionado
    complement = EncryptedCharField(max_length=100, blank=True)  # Adicionado
    neighborhood = EncryptedCharField(max_length=100, blank=True)  # Adicionado
    city = EncryptedCharField(max_length=100)
    state = EncryptedCharField(max_length=100)
    postal_code = EncryptedCharField(max_length=20)

    class Meta:
        verbose_name = 'Endereços de Usuários'
        verbose_name_plural = 'Endereços de Usuários'

    def __str__(self):
        return f'{self.street}, {self.number}, {self.complement}, {self.neighborhood}, {self.city}, {self.state}, {self.postal_code}'


class State(BaseModelAbstract):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=2, unique=True)  # uf traduzido como abbreviation

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Estados'
        verbose_name_plural = 'Estados'


class City(BaseModelAbstract):
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Cidades'
        verbose_name_plural = 'Cidades'


class DashboardContent(BaseModel):
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    is_active = models.BooleanField(default=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Dashboard'
        verbose_name_plural = 'Dashboards'

    def __str__(self):
        pt_translation = self.translations.filter(language='pt').first()
        return pt_translation.title if pt_translation else f"Dashboard {self.pk}"


class DashboardContentTranslation(BaseModel):
    LANGUAGES = [
        ('pt', 'Português'),
        ('en', 'English'),
        ('es', 'Español'),
    ]

    dashboard = models.ForeignKey(DashboardContent, on_delete=models.CASCADE, related_name='translations')
    language = models.CharField(max_length=5, choices=LANGUAGES)
    title = models.CharField(max_length=200)
    content = CKEditor5Field('Content', config_name='extends')

    class Meta:
        unique_together = ('dashboard', 'language')
        verbose_name = 'Tradução de Dashboard'
        verbose_name_plural = 'Traduções de Dashboards'

    def __str__(self):
        return f"{self.title} ({self.language})"
    

class SiteLogo(BaseModel):
    name = models.CharField(max_length=100, default="Logo Principal")
    image = models.ImageField(upload_to='logos/')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
