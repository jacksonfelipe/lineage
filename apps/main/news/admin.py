from django.contrib import admin
from .models import News
from core.admin import BaseModelAdmin


class NewsAdmin(BaseModelAdmin):
    list_display = ('title', 'author', 'pub_date', 'is_published', 'is_private')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('is_published', 'is_private')

admin.site.register(News, NewsAdmin)
