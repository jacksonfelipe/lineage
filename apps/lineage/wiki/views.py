from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, DetailView, TemplateView
from django.utils import translation
from .models import (
    WikiPage, WikiPageTranslation,
    WikiSection, WikiSectionTranslation,
    WikiUpdate, WikiUpdateTranslation,
    WikiEvent, WikiEventTranslation,
    WikiRate, WikiRateTranslation,
    WikiFeature, WikiFeatureTranslation
)


class WikiHomeView(TemplateView):
    template_name = 'wiki/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pages'] = WikiPage.objects.filter(is_active=True).prefetch_related('translations')
        return context


class WikiGeneralView(TemplateView):
    template_name = 'wiki/general.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['server_info'] = WikiPage.objects.filter(slug='server-info', is_active=True).prefetch_related('translations', 'sections__translations')
        context['features'] = WikiPage.objects.filter(slug='features', is_active=True).prefetch_related('translations', 'sections__translations')
        context['getting_started'] = WikiPage.objects.filter(slug='getting-started', is_active=True).prefetch_related('translations', 'sections__translations')
        context['guidelines'] = WikiPage.objects.filter(slug='guidelines', is_active=True).prefetch_related('translations', 'sections__translations')
        context['support'] = WikiPage.objects.filter(slug='support', is_active=True).prefetch_related('translations', 'sections__translations')
        return context


class WikiRatesView(TemplateView):
    template_name = 'wiki/rates.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exp_rates'] = WikiRate.objects.filter(rate_type='exp', is_active=True).prefetch_related('translations')
        context['drop_rates'] = WikiRate.objects.filter(rate_type='drop', is_active=True).prefetch_related('translations')
        context['adena_rates'] = WikiRate.objects.filter(rate_type='adena', is_active=True).prefetch_related('translations')
        context['spoil_rates'] = WikiRate.objects.filter(rate_type='spoil', is_active=True).prefetch_related('translations')
        context['quest_rates'] = WikiRate.objects.filter(rate_type='quest', is_active=True).prefetch_related('translations')
        return context


class WikiRaidsView(TemplateView):
    template_name = 'wiki/raids.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['raids'] = WikiPage.objects.filter(slug__startswith='raid-', is_active=True).prefetch_related('translations', 'sections__translations')
        context['schedules'] = WikiPage.objects.filter(slug__startswith='schedule-', is_active=True).prefetch_related('translations', 'sections__translations')
        return context


class WikiAssistanceView(TemplateView):
    template_name = 'wiki/assistance.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['issues'] = WikiPage.objects.filter(slug__startswith='issue-', is_active=True).prefetch_related('translations', 'sections__translations')
        context['faqs'] = WikiPage.objects.filter(slug__startswith='faq-', is_active=True).prefetch_related('translations', 'sections__translations')
        return context


class WikiEventsView(ListView):
    template_name = 'wiki/events.html'
    model = WikiEvent
    context_object_name = 'events'

    def get_queryset(self):
        return WikiEvent.objects.filter(is_active=True).prefetch_related('translations')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['regular_events'] = self.get_queryset().filter(event_type='regular')
        context['special_events'] = self.get_queryset().filter(event_type='special')
        return context


class WikiUpdatesView(ListView):
    template_name = 'wiki/updates.html'
    model = WikiUpdate
    context_object_name = 'updates'

    def get_queryset(self):
        return WikiUpdate.objects.filter(is_active=True).prefetch_related('translations')


class WikiFeaturesView(TemplateView):
    template_name = 'wiki/features.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['custom_features'] = WikiFeature.objects.filter(feature_type='custom', is_active=True).prefetch_related('translations')
        context['gameplay_features'] = WikiFeature.objects.filter(feature_type='gameplay', is_active=True).prefetch_related('translations')
        context['qol_features'] = WikiFeature.objects.filter(feature_type='qol', is_active=True).prefetch_related('translations')
        context['vip_features'] = WikiFeature.objects.filter(feature_type='vip', is_active=True).prefetch_related('translations')
        context['anti_cheat_features'] = WikiFeature.objects.filter(feature_type='anticheat', is_active=True).prefetch_related('translations')
        context['community_features'] = WikiFeature.objects.filter(feature_type='community', is_active=True).prefetch_related('translations')
        return context


class WikiPageDetailView(DetailView):
    template_name = 'wiki/page.html'
    model = WikiPage
    context_object_name = 'page'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return WikiPage.objects.filter(is_active=True).prefetch_related('translations', 'sections__translations')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sections'] = self.object.sections.filter(is_active=True).prefetch_related('translations')
        return context


class WikiSectionDetailView(DetailView):
    template_name = 'wiki/section.html'
    model = WikiSection
    context_object_name = 'section'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        return WikiSection.objects.filter(is_active=True).prefetch_related('translations', 'page__translations')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = self.object.page
        return context
