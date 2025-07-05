from django.shortcuts import render
from django.views.generic import TemplateView
from django.utils.translation import gettext_lazy as _
from apps.lineage.server.utils.crest import attach_crests_to_clans
from apps.lineage.server.database import LineageDB
from apps.lineage.server.models import ActiveAdenaExchangeItem
from datetime import datetime

from utils.dynamic_import import get_query_class  # importa o helper
LineageStats = get_query_class("LineageStats")  # carrega a classe certa com base no .env


class TopsBaseView(TemplateView):
    """Base view for tops pages"""
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.get_title()
        return context
    
    def get_title(self):
        return _('Tops')


class TopsHomeView(TopsBaseView):
    template_name = 'tops/home.html'
    
    def get_title(self):
        return _('Tops')


class TopsPvpView(TopsBaseView):
    template_name = 'tops/pvp.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        db = LineageDB()
        result = LineageStats.top_pvp(limit=20) if db.is_connected() else []
        result = attach_crests_to_clans(result)
        context['players'] = result
        return context
    
    def get_title(self):
        return _('Ranking PvP')


class TopsPkView(TopsBaseView):
    template_name = 'tops/pk.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        db = LineageDB()
        result = LineageStats.top_pk(limit=20) if db.is_connected() else []
        result = attach_crests_to_clans(result)
        context['players'] = result
        return context
    
    def get_title(self):
        return _('Ranking PK')


class TopsAdenaView(TopsBaseView):
    template_name = 'tops/adena.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        db = LineageDB()

        adn_billion_item = 0
        value_item = 1000000000

        # Buscar o item ativo
        active_item = ActiveAdenaExchangeItem.objects.filter(active=True).order_by('-created_at').first()
        if active_item:
            adn_billion_item = active_item.item_type
            value_item = active_item.value_item

        if db.is_connected():
            result = LineageStats.top_adena(limit=20, adn_billion_item=adn_billion_item, value_item=value_item)
            result = attach_crests_to_clans(result)
        else:
            result = list()

        context['players'] = result
        return context
    
    def get_title(self):
        return _('Ranking Adena')


class TopsClansView(TopsBaseView):
    template_name = 'tops/clans.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        db = LineageDB()
        clanes = LineageStats.top_clans(limit=20) if db.is_connected() else []
        clanes = attach_crests_to_clans(clanes)
        context['clans'] = clanes
        return context
    
    def get_title(self):
        return _('Ranking Clans')


class TopsLevelView(TopsBaseView):
    template_name = 'tops/level.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        db = LineageDB()
        result = LineageStats.top_level(limit=20) if db.is_connected() else []
        result = attach_crests_to_clans(result)
        context['players'] = result
        return context
    
    def get_title(self):
        return _('Ranking Nível')


class TopsOnlineView(TopsBaseView):
    template_name = 'tops/online.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        db = LineageDB()
        result = LineageStats.top_online(limit=20) if db.is_connected() else []
        result = attach_crests_to_clans(result)
        context['ranking'] = result
        return context
    
    def get_title(self):
        return _('Top Online')


class TopsOlympiadView(TopsBaseView):
    template_name = 'tops/olympiad.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        db = LineageDB()
        result = LineageStats.olympiad_ranking() if db.is_connected() else []
        context['ranking'] = result
        return context
    
    def get_title(self):
        return _('Ranking Olimpíada')


class TopsSiegeView(TopsBaseView):
    template_name = 'tops/siege.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            db = LineageDB()
            if db.is_connected():
                castles = LineageStats.siege()

                for castle in castles:
                    participants = LineageStats.siege_participants(castle["id"])
                    castle["siege_participants"] = participants

                    # adiciona caminho da imagem baseado no nome
                    castle_name_lower = castle['name'].lower()
                    # Mapeamento para garantir que as imagens sejam encontradas
                    castle_image_mapping = {
                        'aden': 'aden',
                        'dion': 'dion',
                        'giran': 'giran',
                        'gludio': 'gludio',
                        'goddard': 'goddard',
                        'innadril': 'innadril',
                        'oren': 'oren',
                        'rune': 'rune',
                        'schuttgart': 'schuttgart'
                    }
                    
                    image_name = castle_image_mapping.get(castle_name_lower, castle_name_lower)
                    castle["image_path"] = f"assets/img/castles/{image_name}.jpg"

                    # adiciona valores default traduzidos se vazio
                    castle["clan_name"] = castle["clan_name"] or _("No Owner")
                    castle["char_name"] = castle["char_name"] or _("No Leader")
                    castle["ally_name"] = castle["ally_name"] or _("No Alliance")

                    # CORREÇÃO AQUI: converte Decimal para float
                    if castle["sdate"]:
                        timestamp_s = float(castle["sdate"]) / 1000
                        castle["siege_date"] = datetime.fromtimestamp(timestamp_s)
                    
                    # Garantir que os participantes tenham valores padrão
                    for participant in castle["siege_participants"]:
                        participant["clan_name"] = participant["clan_name"] or _("Unknown Clan")

                # move para fora do loop para não sobrescrever a cada iteração
                castles = attach_crests_to_clans(castles)
                
                # Aplicar crests aos participantes também
                for castle in castles:
                    if castle.get("siege_participants"):
                        castle["siege_participants"] = attach_crests_to_clans(castle["siege_participants"])
            else:
                castles = list()
        except Exception as e:
            print(f"Erro ao carregar dados do siege: {e}")
            castles = list()

        context['castles'] = castles
        return context
    
    def get_title(self):
        return _('Castle & Siege Ranking')
