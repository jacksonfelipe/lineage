from django.db import models
from core.models import BaseModel
from django_ckeditor_5.fields import CKEditor5Field


class FAQ(BaseModel):
    question = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    is_public = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Pergunta Frequente'
        verbose_name_plural = 'Perguntas Frequentes'

        permissions = [
            ("can_view_index", "Can visualization view index"),
        ]

    def __str__(self):
        pt_translation = self.translations.filter(language='pt').first()
        return pt_translation.question if pt_translation else f"FAQ {self.pk}"


class FAQTranslation(BaseModel):
    LANGUAGES = [
        ('pt', 'Português'),
        ('en', 'English'),
        ('es', 'Español'),
    ]

    faq = models.ForeignKey(FAQ, on_delete=models.CASCADE, related_name='translations')
    language = models.CharField(max_length=5, choices=LANGUAGES)
    question = models.CharField(max_length=255)
    answer = CKEditor5Field('Answer', config_name='extends')

    class Meta:
        unique_together = ('faq', 'language')
        verbose_name = 'Tradução de FAQ'
        verbose_name_plural = 'Traduções de FAQ'

    def __str__(self):
        return f"{self.question} ({self.language})"
