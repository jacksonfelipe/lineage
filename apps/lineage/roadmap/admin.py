from django.contrib import admin
from .models import Roadmap, RoadmapTranslation
from core.admin import BaseModelAdmin


class RoadmapAdmin(BaseModelAdmin):
    list_display = ('id', 'get_title', 'status', 'is_published', 'is_private', 'author', 'pub_date')
    list_filter = ('status', 'is_published', 'is_private', 'pub_date')
    search_fields = ('translations__title', 'author__username')
    autocomplete_fields = ['author']
    ordering = ('-pub_date',)

    def get_title(self, obj):
        pt_translation = obj.translations.filter(language='pt').first()
        return pt_translation.title if pt_translation else '-'
    get_title.short_description = 'Título (pt)'


class RoadmapTranslationAdmin(BaseModelAdmin):
    list_display = ('id', 'roadmap', 'language', 'title')
    list_filter = ('language',)
    search_fields = ('title',)
    autocomplete_fields = ['roadmap']


admin.site.register(Roadmap, RoadmapAdmin)
admin.site.register(RoadmapTranslation, RoadmapTranslationAdmin)
