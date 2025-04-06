from django.contrib import admin
from .models import News
from core.admin import BaseModelAdmin
from .forms import NewsForm
import html
from django.utils.html import strip_tags
from django.template.defaultfilters import truncatewords


class NewsAdmin(BaseModelAdmin):
    form = NewsForm
    list_display = ('title', 'author', 'pub_date', 'is_published', 'is_private')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('is_published', 'is_private')
    exclude = ('author', 'summary')

    def save_model(self, request, obj, form, change):
        if not change or not obj.author:
            obj.author = request.user

        if obj.content:
            plain_text = strip_tags(obj.content)
            decoded_text = html.unescape(plain_text)
            obj.summary = truncatewords(decoded_text, 30)

        super().save_model(request, obj, form, change)


admin.site.register(News, NewsAdmin)
