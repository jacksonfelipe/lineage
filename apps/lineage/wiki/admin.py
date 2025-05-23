from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    WikiPage, WikiPageTranslation,
    WikiSection, WikiSectionTranslation,
    WikiUpdate, WikiUpdateTranslation,
    WikiEvent, WikiEventTranslation,
    WikiRate, WikiRateTranslation,
    WikiFeature, WikiFeatureTranslation,
    WikiGeneral, WikiGeneralTranslation,
    WikiRaid, WikiRaidTranslation,
    WikiAssistance, WikiAssistanceTranslation,
)
from core.admin import BaseModelAdmin


class TranslationInline(admin.StackedInline):
    extra = 1


class WikiPageTranslationInline(TranslationInline):
    model = WikiPageTranslation


@admin.register(WikiPage)
class WikiPageAdmin(BaseModelAdmin):
    list_display = ('get_title', 'slug', 'order', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('translations__title', 'translations__content')
    ordering = ('order', 'id')
    inlines = [WikiPageTranslationInline]

    def get_title(self, obj):
        pt_translation = obj.translations.filter(language='pt').first()
        return pt_translation.title if pt_translation else '-'
    get_title.short_description = _('Title')


class WikiSectionTranslationInline(TranslationInline):
    model = WikiSectionTranslation


@admin.register(WikiSection)
class WikiSectionAdmin(BaseModelAdmin):
    list_display = ('get_title', 'page', 'section_type', 'order', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'page', 'section_type', 'created_at', 'updated_at')
    search_fields = ('translations__title', 'translations__content', 'translations__subtitle', 'translations__description')
    ordering = ('page', 'order', 'id')
    inlines = [WikiSectionTranslationInline]

    def get_title(self, obj):
        pt_translation = obj.translations.filter(language='pt').first()
        return pt_translation.title if pt_translation else '-'
    get_title.short_description = _('Title')


class WikiUpdateTranslationInline(TranslationInline):
    model = WikiUpdateTranslation


@admin.register(WikiUpdate)
class WikiUpdateAdmin(BaseModelAdmin):
    list_display = ('version', 'release_date', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'release_date', 'created_at', 'updated_at')
    search_fields = ('version', 'translations__content')
    ordering = ('-release_date', '-version')
    inlines = [WikiUpdateTranslationInline]


class WikiEventTranslationInline(TranslationInline):
    model = WikiEventTranslation


@admin.register(WikiEvent)
class WikiEventAdmin(BaseModelAdmin):
    list_display = ('get_title', 'event_type', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'event_type', 'created_at', 'updated_at')
    search_fields = (
        'translations__title',
        'translations__description',
        'translations__requirements',
        'translations__rewards'
    )
    ordering = ('event_type', 'id')
    inlines = [WikiEventTranslationInline]

    def get_title(self, obj):
        pt_translation = obj.translations.filter(language='pt').first()
        return pt_translation.title if pt_translation else '-'
    get_title.short_description = _('Title')


class WikiRateTranslationInline(TranslationInline):
    model = WikiRateTranslation


@admin.register(WikiRate)
class WikiRateAdmin(BaseModelAdmin):
    list_display = ('rate_type', 'value', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'rate_type')
    search_fields = ('rate_type', 'translations__title', 'translations__content')
    ordering = ('rate_type', '-created_at')
    inlines = [WikiRateTranslationInline]


class WikiFeatureTranslationInline(TranslationInline):
    model = WikiFeatureTranslation


@admin.register(WikiFeature)
class WikiFeatureAdmin(BaseModelAdmin):
    list_display = ('feature_type', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'feature_type')
    search_fields = ('feature_type', 'translations__title', 'translations__content')
    ordering = ('feature_type', '-created_at')
    inlines = [WikiFeatureTranslationInline]


class WikiGeneralTranslationInline(TranslationInline):
    model = WikiGeneralTranslation


@admin.register(WikiGeneral)
class WikiGeneralAdmin(BaseModelAdmin):
    list_display = ('general_type', 'order', 'is_active')
    list_filter = ('is_active', 'general_type')
    search_fields = ('translations__title', 'translations__content')
    ordering = ['order', 'general_type']
    inlines = [WikiGeneralTranslationInline]


class WikiRaidTranslationInline(TranslationInline):
    model = WikiRaidTranslation


@admin.register(WikiRaid)
class WikiRaidAdmin(BaseModelAdmin):
    list_display = ('raid_type', 'level', 'order', 'is_active')
    list_filter = ('is_active', 'raid_type', 'level')
    search_fields = ('translations__title', 'translations__content', 'translations__location')
    ordering = ['raid_type', 'level', 'order']
    inlines = [WikiRaidTranslationInline]


class WikiAssistanceTranslationInline(TranslationInline):
    model = WikiAssistanceTranslation


@admin.register(WikiAssistance)
class WikiAssistanceAdmin(BaseModelAdmin):
    list_display = ('assistance_type', 'order', 'is_active')
    list_filter = ('is_active', 'assistance_type')
    search_fields = ('translations__title', 'translations__content', 'translations__category')
    ordering = ['assistance_type', 'order']
    inlines = [WikiAssistanceTranslationInline]
