from django.db import models
from core.models import BaseModel
from apps.main.home.models import User
from django.utils.text import slugify
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField


class News(BaseModel):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    content = RichTextUploadingField()
    summary = models.TextField(blank=True)
    image = models.ImageField(upload_to='news', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    pub_date = models.DateTimeField('date published', default=timezone.now)
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
            self.slug = slugify(self.title)
        super(News, self).save(*args, **kwargs)

    def __str__(self):
        return self.title
