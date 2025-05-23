from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext_lazy as _, get_language
from django.views.generic import ListView, DetailView, TemplateView
from django.utils import translation
from django.db.models import Prefetch
from .models import (
    WikiPage, WikiPageTranslation,
    WikiSection, WikiSectionTranslation,
    WikiUpdate, WikiUpdateTranslation,
    WikiEvent, WikiEventTranslation,
    WikiRate, WikiRateTranslation,
    WikiFeature, WikiFeatureTranslation,
    WikiGeneral, WikiRaid, WikiAssistance,
    WikiGeneralTranslation, WikiRaidTranslation, WikiAssistanceTranslation
)


class WikiPagesMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language()
        
        # Get all active pages with translations
        pages = WikiPage.objects.filter(
            is_active=True,
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiPageTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        ).order_by('order')
        
        # Add pages to context
        context['pages'] = [
            {
                'page': page,
                'translation': page._translation[0] if page._translation else None
            }
            for page in pages
        ]
        
        return context


class WikiHomeView(WikiPagesMixin, ListView):
    model = WikiPage
    template_name = 'wiki/home.html'
    context_object_name = 'pages'

    def get_queryset(self):
        return WikiPage.objects.filter(is_active=True).order_by('order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['updates'] = WikiUpdate.objects.filter(is_active=True).order_by('-release_date')[:5]
        context['events'] = WikiEvent.objects.filter(is_active=True).order_by('-created_at')[:5]
        context['rates'] = WikiRate.objects.filter(is_active=True)
        context['features'] = WikiFeature.objects.filter(is_active=True)
        return context


class WikiGeneralListView(WikiPagesMixin, ListView):
    model = WikiGeneral
    template_name = 'wiki/general.html'
    context_object_name = 'generals'

    def get_queryset(self):
        return WikiGeneral.objects.filter(is_active=True).order_by('order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('General Information')
        return context


class WikiGeneralDetailView(WikiPagesMixin, DetailView):
    model = WikiGeneral
    template_name = 'wiki/general.html'
    context_object_name = 'general'

    def get_queryset(self):
        return WikiGeneral.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.get_general_type_display()
        return context


class WikiRaidListView(WikiPagesMixin, ListView):
    model = WikiRaid
    template_name = 'wiki/raids.html'
    context_object_name = 'raids'

    def get_queryset(self):
        return WikiRaid.objects.filter(is_active=True).order_by('raid_type', 'level', 'order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Raids')
        return context


class WikiRaidDetailView(WikiPagesMixin, DetailView):
    model = WikiRaid
    template_name = 'wiki/raids.html'
    context_object_name = 'raid'

    def get_queryset(self):
        return WikiRaid.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.get_raid_type_display()
        return context


class WikiAssistanceListView(WikiPagesMixin, ListView):
    model = WikiAssistance
    template_name = 'wiki/assistance.html'
    context_object_name = 'assistances'

    def get_queryset(self):
        return WikiAssistance.objects.filter(is_active=True).order_by('assistance_type', 'order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Assistance')
        return context


class WikiAssistanceDetailView(WikiPagesMixin, DetailView):
    model = WikiAssistance
    template_name = 'wiki/assistance.html'
    context_object_name = 'assistance'

    def get_queryset(self):
        return WikiAssistance.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.get_assistance_type_display()
        return context


class WikiGeneralView(WikiPagesMixin, TemplateView):
    template_name = 'wiki/general.html'

    def get_queryset(self):
        language = get_language()
        return WikiGeneral.objects.filter(
            is_active=True,
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiGeneralTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language()
        
        # Get all general information types
        general_types = [
            'about', 'rules', 'commands', 'classes', 'races',
            'noblesse', 'subclass', 'hero', 'clan', 'siege',
            'olympiad', 'castle', 'fortress', 'territory', 'other'
        ]
        
        for general_type in general_types:
            # Get general information for each type
            generals = WikiGeneral.objects.filter(
                is_active=True,
                general_type=general_type,
                translations__language=language
            ).prefetch_related(
                Prefetch(
                    'translations',
                    queryset=WikiGeneralTranslation.objects.filter(language=language),
                    to_attr='_translation'
                )
            ).order_by('order')
            
            # Add to context with proper key (without _info suffix)
            context[general_type] = [
                {
                    'general': general,
                    'translation': general._translation[0] if general._translation else None
                }
                for general in generals
            ]
        
        # Add title to context
        context['title'] = _('General Information')
        
        return context


class WikiRatesView(WikiPagesMixin, TemplateView):
    template_name = 'wiki/rates.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language()
        
        # Get all rate types
        exp_rates = WikiRate.objects.filter(
            is_active=True,
            rate_type='exp',
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiRateTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        drop_rates = WikiRate.objects.filter(
            is_active=True,
            rate_type='drop',
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiRateTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        adena_rates = WikiRate.objects.filter(
            is_active=True,
            rate_type='adena',
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiRateTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        spoil_rates = WikiRate.objects.filter(
            is_active=True,
            rate_type='spoil',
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiRateTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        quest_rates = WikiRate.objects.filter(
            is_active=True,
            rate_type='quest',
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiRateTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        # Add all rates to context
        context.update({
            'exp_rates': [
                {
                    'rate': rate,
                    'translation': rate._translation[0] if rate._translation else None
                }
                for rate in exp_rates
            ],
            'drop_rates': [
                {
                    'rate': rate,
                    'translation': rate._translation[0] if rate._translation else None
                }
                for rate in drop_rates
            ],
            'adena_rates': [
                {
                    'rate': rate,
                    'translation': rate._translation[0] if rate._translation else None
                }
                for rate in adena_rates
            ],
            'spoil_rates': [
                {
                    'rate': rate,
                    'translation': rate._translation[0] if rate._translation else None
                }
                for rate in spoil_rates
            ],
            'quest_rates': [
                {
                    'rate': rate,
                    'translation': rate._translation[0] if rate._translation else None
                }
                for rate in quest_rates
            ]
        })
        
        return context


class WikiRaidsView(WikiPagesMixin, TemplateView):
    template_name = 'wiki/raids.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language()
        
        # Debug: Print all raids without filters
        all_raids = WikiRaid.objects.all()
        active_raids = WikiRaid.objects.filter(is_active=True)
        raids_with_translations = WikiRaid.objects.filter(translations__language=language)
        
        # Debug: Print all raid types
        raid_types = WikiRaid.objects.values_list('raid_type', flat=True).distinct()
        
        # Get boss raids with debug info
        boss_raids = WikiRaid.objects.filter(
            is_active=True,
            raid_type='boss'
        ).prefetch_related(
            'translations'
        ).order_by('level', 'order')
        
        # Get epic raids
        epic_raids = WikiRaid.objects.filter(
            is_active=True,
            raid_type='epic'
        ).prefetch_related(
            'translations'
        ).order_by('level', 'order')
        
        # Get world raids
        world_raids = WikiRaid.objects.filter(
            is_active=True,
            raid_type='world'
        ).prefetch_related(
            'translations'
        ).order_by('level', 'order')
        
        # Get siege raids
        siege_raids = WikiRaid.objects.filter(
            is_active=True,
            raid_type='siege'
        ).prefetch_related(
            'translations'
        ).order_by('level', 'order')
        
        # Get other raids
        other_raids = WikiRaid.objects.filter(
            is_active=True,
            raid_type='other'
        ).prefetch_related(
            'translations'
        ).order_by('level', 'order')
        
        # Helper function to get translation
        def get_translation(raid):
            return raid.translations.filter(language=language).first()
        
        # Add all raids to context with proper structure
        context.update({
            'boss_raids': [
                {
                    'raid': raid,
                    'translation': get_translation(raid)
                }
                for raid in boss_raids
            ],
            'epic_raids': [
                {
                    'raid': raid,
                    'translation': get_translation(raid)
                }
                for raid in epic_raids
            ],
            'world_raids': [
                {
                    'raid': raid,
                    'translation': get_translation(raid)
                }
                for raid in world_raids
            ],
            'siege_raids': [
                {
                    'raid': raid,
                    'translation': get_translation(raid)
                }
                for raid in siege_raids
            ],
            'other_raids': [
                {
                    'raid': raid,
                    'translation': get_translation(raid)
                }
                for raid in other_raids
            ]
        })
        
        return context


class WikiAssistanceView(WikiPagesMixin, TemplateView):
    template_name = 'wiki/assistance.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language()
        
        # Get guides and guilds
        guides = WikiAssistance.objects.filter(
            is_active=True,
            assistance_type='guide',
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiAssistanceTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        # Get tutorials
        tutorials = WikiAssistance.objects.filter(
            is_active=True,
            assistance_type='tutorial',
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiAssistanceTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        # Get FAQs
        faqs = WikiAssistance.objects.filter(
            is_active=True,
            assistance_type='faq',
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiAssistanceTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        # Get technical support
        technical_support = WikiAssistance.objects.filter(
            is_active=True,
            assistance_type='support',
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiAssistanceTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        # Get other assistance types
        other_assistance = WikiAssistance.objects.filter(
            is_active=True,
            assistance_type='other',
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiAssistanceTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        # Add all assistance to context
        context.update({
            'guides': [
                {
                    'assistance': assistance,
                    'translation': assistance._translation[0] if assistance._translation else None
                }
                for assistance in guides
            ],
            'tutorials': [
                {
                    'assistance': assistance,
                    'translation': assistance._translation[0] if assistance._translation else None
                }
                for assistance in tutorials
            ],
            'faqs': [
                {
                    'assistance': assistance,
                    'translation': assistance._translation[0] if assistance._translation else None
                }
                for assistance in faqs
            ],
            'technical_support': [
                {
                    'assistance': assistance,
                    'translation': assistance._translation[0] if assistance._translation else None
                }
                for assistance in technical_support
            ],
            'other_assistance': [
                {
                    'assistance': assistance,
                    'translation': assistance._translation[0] if assistance._translation else None
                }
                for assistance in other_assistance
            ]
        })
        
        return context


class WikiEventsView(WikiPagesMixin, ListView):
    template_name = 'wiki/events.html'
    context_object_name = 'events'

    def get_queryset(self):
        language = get_language()
        return WikiEvent.objects.filter(
            is_active=True,
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiEventTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language()
        
        # Get regular events
        regular_events = WikiEvent.objects.filter(
            is_active=True,
            event_type='regular',
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiEventTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        # Get special events
        special_events = WikiEvent.objects.filter(
            is_active=True,
            event_type='special',
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiEventTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        # Add events to context
        context.update({
            'regular_events': [
                {
                    'event': event,
                    'translation': event._translation[0] if event._translation else None
                }
                for event in regular_events
            ],
            'special_events': [
                {
                    'event': event,
                    'translation': event._translation[0] if event._translation else None
                }
                for event in special_events
            ]
        })
        
        return context


class WikiUpdatesView(WikiPagesMixin, ListView):
    template_name = 'wiki/updates.html'
    context_object_name = 'updates'

    def get_queryset(self):
        language = get_language()
        return WikiUpdate.objects.filter(
            is_active=True,
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiUpdateTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add updates with translations to context
        context['updates'] = [
            {
                'update': update,
                'translation': update._translation[0] if update._translation else None
            }
            for update in self.get_queryset()
        ]
        
        return context


class WikiFeaturesView(WikiPagesMixin, TemplateView):
    template_name = 'wiki/features.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language()
        
        # Get all feature types
        custom_features = WikiFeature.objects.filter(
            is_active=True,
            feature_type='custom',
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiFeatureTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        gameplay_features = WikiFeature.objects.filter(
            is_active=True,
            feature_type='gameplay',
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiFeatureTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        qol_features = WikiFeature.objects.filter(
            is_active=True,
            feature_type='qol',
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiFeatureTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        vip_features = WikiFeature.objects.filter(
            is_active=True,
            feature_type='vip',
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiFeatureTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        anti_cheat_features = WikiFeature.objects.filter(
            is_active=True,
            feature_type='anticheat',
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiFeatureTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        community_features = WikiFeature.objects.filter(
            is_active=True,
            feature_type='community',
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiFeatureTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        # Add all features to context
        context.update({
            'custom_features': [
                {
                    'feature': feature,
                    'translation': feature._translation[0] if feature._translation else None
                }
                for feature in custom_features
            ],
            'gameplay_features': [
                {
                    'feature': feature,
                    'translation': feature._translation[0] if feature._translation else None
                }
                for feature in gameplay_features
            ],
            'qol_features': [
                {
                    'feature': feature,
                    'translation': feature._translation[0] if feature._translation else None
                }
                for feature in qol_features
            ],
            'vip_features': [
                {
                    'feature': feature,
                    'translation': feature._translation[0] if feature._translation else None
                }
                for feature in vip_features
            ],
            'anti_cheat_features': [
                {
                    'feature': feature,
                    'translation': feature._translation[0] if feature._translation else None
                }
                for feature in anti_cheat_features
            ],
            'community_features': [
                {
                    'feature': feature,
                    'translation': feature._translation[0] if feature._translation else None
                }
                for feature in community_features
            ]
        })
        
        return context


class WikiPageDetailView(WikiPagesMixin, DetailView):
    template_name = 'wiki/page.html'
    model = WikiPage
    context_object_name = 'page'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        language = get_language()
        return WikiPage.objects.filter(
            is_active=True,
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiPageTranslation.objects.filter(language=language),
                to_attr='_translation'
            ),
            Prefetch(
                'sections',
                queryset=WikiSection.objects.filter(is_active=True).prefetch_related(
                    Prefetch(
                        'translations',
                        queryset=WikiSectionTranslation.objects.filter(language=language),
                        to_attr='_translation'
                    )
                )
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add page translation to context
        context['page'] = {
            'page': self.object,
            'translation': self.object._translation[0] if self.object._translation else None
        }
        
        # Add sections with translations to context
        context['sections'] = [
            {
                'section': section,
                'translation': section._translation[0] if section._translation else None
            }
            for section in self.object.sections.all()
        ]
        
        return context


class WikiSectionDetailView(WikiPagesMixin, DetailView):
    template_name = 'wiki/section.html'
    model = WikiSection
    context_object_name = 'section'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        language = get_language()
        return WikiSection.objects.filter(
            is_active=True,
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiSectionTranslation.objects.filter(language=language),
                to_attr='_translation'
            ),
            Prefetch(
                'page',
                queryset=WikiPage.objects.filter(is_active=True).prefetch_related(
                    Prefetch(
                        'translations',
                        queryset=WikiPageTranslation.objects.filter(language=language),
                        to_attr='_translation'
                    )
                )
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add section translation to context
        context['section'] = {
            'section': self.object,
            'translation': self.object._translation[0] if self.object._translation else None
        }
        
        # Add page with translation to context
        context['page'] = {
            'page': self.object.page,
            'translation': self.object.page._translation[0] if self.object.page._translation else None
        }
        
        return context
