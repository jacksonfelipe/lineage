from django.db import models
from core.models import BaseModel
from apps.main.home.models import User
from django.utils.text import slugify
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Field


class News(BaseModel):
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    image = models.ImageField(upload_to='news', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    pub_date = models.DateTimeField(_('date published'), default=timezone.now)
    is_published = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Notícia'
        verbose_name_plural = 'Notícias'

        permissions = [
            ("can_view_index", "Can visualization view index"),
            ("can_view_detail", "Can visualization view detail"),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            # slug com base no título em português, se existir
            pt_translation = self.translations.filter(language='pt').first()
            if pt_translation:
                self.slug = slugify(pt_translation.title)
        super(News, self).save(*args, **kwargs)

    def __str__(self):
        pt_translation = self.translations.filter(language='pt').first()
        return pt_translation.title if pt_translation else f"News {self.pk}"


class NewsTranslation(BaseModel):
    LANGUAGES = [
        ('pt', 'Português'),
        ('en', 'English'),
        ('es', 'Español'),
    ]

    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='translations')
    language = models.CharField(max_length=5, choices=LANGUAGES)
    title = models.CharField(max_length=200)
    content = CKEditor5Field('Content', config_name='extends')
    summary = models.TextField(blank=True)

    class Meta:
        unique_together = ('news', 'language')
        verbose_name = 'Tradução de Notícia'
        verbose_name_plural = 'Traduções de Notícias'

    def __str__(self):
        return f"{self.title} ({self.language})"
