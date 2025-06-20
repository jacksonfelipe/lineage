from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Roadmap, RoadmapTranslation


class BaseModelAdmin(ImportExportModelAdmin):
    list_display = ('uuid', 'created_at', 'created_by', 'updated_at', 'updated_by')  # Incluindo o campo uuid
    readonly_fields = ('uuid', 'created_at', 'created_by', 'updated_at', 'updated_by')  # Tornando o campo uuid somente leitura

    def get_readonly_fields(self, request, obj=None):
        # Make fields read-only, but not in forms
        if obj:
            return self.readonly_fields
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if not change:  # Se for um novo objeto
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


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
