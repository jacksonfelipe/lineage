from rest_framework.decorators import api_view, throttle_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle
from rest_framework.generics import GenericAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import datetime
import logging
from drf_spectacular.utils import extend_schema

from .serializers import (
    PlayerOnlineSerializer, TopPlayerSerializer, TopClanSerializer,
    OlympiadRankingSerializer, OlympiadHeroSerializer, GrandBossStatusSerializer,
    SiegeSerializer, SiegeParticipantSerializer, BossJewelLocationSerializer,
    CustomTokenObtainPairSerializer, RefreshTokenSerializer, LoginSerializer,
    UserProfileSerializer, ChangePasswordSerializer, CharacterSerializer,
    ItemSerializer, ClanDetailSerializer, AuctionItemSerializer,
    APIResponseSerializer, ServerStatusSerializer
)

from .schema import ServerAPISchema, AuthAPISchema, UserAPISchema, SearchAPISchema, GameDataAPISchema, ServerStatusAPISchema, APIInfoSchema

from utils.dynamic_import import get_query_class
from apps.lineage.server.decorators import endpoint_enabled
from apps.lineage.server.models import ApiEndpointToggle

# Carrega a classe LineageStats baseada na configuração
LineageStats = get_query_class("LineageStats")


class PublicAPIRateThrottle(AnonRateThrottle):
    """Rate limit para APIs públicas: 30 requisições por minuto"""
    rate = '30/minute'


@endpoint_enabled('players_online')
@ServerAPISchema.players_online_schema()
class PlayersOnlineView(GenericAPIView):
    """View para dados de jogadores online"""
    permission_classes = [AllowAny]
    serializer_class = PlayerOnlineSerializer
    throttle_classes = [PublicAPIRateThrottle]
    queryset = ApiEndpointToggle.objects.none()  # Empty queryset for DRF Spectacular
    
    def get(self, request):
        """
        Retorna o número de jogadores online
        """
        try:
            # Tenta buscar do cache primeiro
            cache_key = 'api_players_online'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                # Se não está em cache, busca dos dados
                data = LineageStats.players_online()
                # Cache por 30 segundos
                cache.set(cache_key, data, 30)
            else:
                data = cached_data
            
            # Verifica se os dados estão no formato esperado
            if not data or not isinstance(data, list) or len(data) == 0:
                return Response(
                    {'error': 'Dados de jogadores online não disponíveis'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            # Extrai o valor da consulta
            online_count = data[0].get('quant', 0) if data else 0
            
            # Prepara os dados para o serializer
            response_data = {
                'online_count': online_count,
                'fake_players': 0,  # Pode ser calculado baseado na configuração
                'real_players': online_count
            }
            
            serializer = self.get_serializer(response_data)
            return Response(serializer.data)
        
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro em players_online: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Erro ao buscar dados de jogadores online: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@endpoint_enabled('top_pvp')
@ServerAPISchema.top_pvp_schema()
class TopPvPView(GenericAPIView):
    """View para ranking PvP"""
    permission_classes = [AllowAny]
    serializer_class = TopPlayerSerializer
    throttle_classes = [PublicAPIRateThrottle]
    queryset = ApiEndpointToggle.objects.none()  # Empty queryset for DRF Spectacular
    
    def get(self, request):
        """
        Retorna o ranking PvP
        """
        try:
            limit = int(request.GET.get("limit", 10))
            limit = min(limit, 100)  # Limita a 100 registros
            
            cache_key = f'api_top_pvp_{limit}'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                data = LineageStats.top_pvp(limit=limit)
                cache.set(cache_key, data, 60)  # Cache por 1 minuto
            else:
                data = cached_data
            
            serializer = self.get_serializer(data, many=True)
            return Response(serializer.data)
        
        except ValueError:
            return Response(
                {'error': 'Parâmetro limit deve ser um número válido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Erro ao buscar ranking PvP'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@endpoint_enabled('top_pk')
@ServerAPISchema.top_pk_schema()
class TopPKView(GenericAPIView):
    """View para ranking PK"""
    permission_classes = [AllowAny]
    serializer_class = TopPlayerSerializer
    throttle_classes = [PublicAPIRateThrottle]
    queryset = ApiEndpointToggle.objects.none()  # Empty queryset for DRF Spectacular
    
    def get(self, request):
        """
        Retorna o ranking PK
        """
        try:
            limit = int(request.GET.get("limit", 10))
            limit = min(limit, 100)
            
            cache_key = f'api_top_pk_{limit}'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                data = LineageStats.top_pk(limit=limit)
                cache.set(cache_key, data, 60)
            else:
                data = cached_data
            
            serializer = self.get_serializer(data, many=True)
            return Response(serializer.data)
        
        except ValueError:
            return Response(
                {'error': 'Parâmetro limit deve ser um número válido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Erro ao buscar ranking PK'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@endpoint_enabled('top_clan')
@ServerAPISchema.top_clan_schema()
class TopClanView(GenericAPIView):
    """View para ranking de clãs"""
    permission_classes = [AllowAny]
    serializer_class = TopClanSerializer
    throttle_classes = [PublicAPIRateThrottle]
    queryset = ApiEndpointToggle.objects.none()  # Empty queryset for DRF Spectacular
    
    def get(self, request):
        """
        Retorna o ranking de clãs
        """
        try:
            limit = int(request.GET.get("limit", 10))
            limit = min(limit, 100)
            
            cache_key = f'api_top_clan_{limit}'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                data = LineageStats.top_clans(limit=limit)
                cache.set(cache_key, data, 60)
            else:
                data = cached_data
            
            # Verifica se os dados estão no formato esperado
            if data is None:
                return Response(
                    {'error': 'Dados de clãs não disponíveis'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            # Processa os dados para garantir compatibilidade com o serializer
            processed_data = []
            for clan in data:
                processed_clan = {
                    'clan_name': clan.get('clan_name', ''),
                    'leader_name': clan.get('char_name', ''),
                    'level': clan.get('clan_level', 0),
                    'member_count': clan.get('membros', 0),
                    'reputation': clan.get('reputation_score', 0)
                }
                processed_data.append(processed_clan)
            
            serializer = self.get_serializer(processed_data, many=True)
            return Response(serializer.data)
        
        except ValueError:
            return Response(
                {'error': 'Parâmetro limit deve ser um número válido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro em top_clan: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Erro ao buscar ranking de clãs: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@endpoint_enabled('top_rich')
@ServerAPISchema.top_rich_schema()
class TopRichView(GenericAPIView):
    """View para ranking de riqueza"""
    permission_classes = [AllowAny]
    serializer_class = TopPlayerSerializer
    throttle_classes = [PublicAPIRateThrottle]
    queryset = ApiEndpointToggle.objects.none()  # Empty queryset for DRF Spectacular
    
    def get(self, request):
        """
        Retorna o ranking de riqueza (Adena)
        """
        try:
            limit = int(request.GET.get("limit", 10))
            limit = min(limit, 100)
            
            cache_key = f'api_top_rich_{limit}'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                data = LineageStats.top_adena(limit=limit)
                cache.set(cache_key, data, 60)
            else:
                data = cached_data
            
            serializer = self.get_serializer(data, many=True)
            return Response(serializer.data)
        
        except ValueError:
            return Response(
                {'error': 'Parâmetro limit deve ser um número válido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Erro ao buscar ranking de riqueza'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@endpoint_enabled('top_online')
@ServerAPISchema.top_online_schema()
class TopOnlineView(GenericAPIView):
    """View para ranking de tempo online"""
    permission_classes = [AllowAny]
    serializer_class = TopPlayerSerializer
    throttle_classes = [PublicAPIRateThrottle]
    queryset = ApiEndpointToggle.objects.none()  # Empty queryset for DRF Spectacular
    
    def get(self, request):
        """
        Retorna o ranking de tempo online
        """
        try:
            limit = int(request.GET.get("limit", 10))
            limit = min(limit, 100)
            
            cache_key = f'api_top_online_{limit}'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                data = LineageStats.top_online(limit=limit)
                cache.set(cache_key, data, 60)
            else:
                data = cached_data
            
            serializer = self.get_serializer(data, many=True)
            return Response(serializer.data)
        
        except ValueError:
            return Response(
                {'error': 'Parâmetro limit deve ser um número válido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Erro ao buscar ranking de tempo online'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@endpoint_enabled('top_level')
@ServerAPISchema.top_level_schema()
class TopLevelView(GenericAPIView):
    """View para ranking de nível"""
    permission_classes = [AllowAny]
    serializer_class = TopPlayerSerializer
    throttle_classes = [PublicAPIRateThrottle]
    queryset = ApiEndpointToggle.objects.none()  # Empty queryset for DRF Spectacular
    
    def get(self, request):
        """
        Retorna o ranking de nível
        """
        try:
            limit = int(request.GET.get("limit", 10))
            limit = min(limit, 100)
            
            cache_key = f'api_top_level_{limit}'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                data = LineageStats.top_level(limit=limit)
                cache.set(cache_key, data, 60)
            else:
                data = cached_data
            
            serializer = self.get_serializer(data, many=True)
            return Response(serializer.data)
        
        except ValueError:
            return Response(
                {'error': 'Parâmetro limit deve ser um número válido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Erro ao buscar ranking de nível'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@endpoint_enabled('olympiad_ranking')
@ServerAPISchema.olympiad_ranking_schema()
class OlympiadRankingView(GenericAPIView):
    """View para ranking da Olimpíada"""
    permission_classes = [AllowAny]
    serializer_class = OlympiadRankingSerializer
    throttle_classes = [PublicAPIRateThrottle]
    queryset = ApiEndpointToggle.objects.none()  # Empty queryset for DRF Spectacular
    
    def get(self, request):
        """
        Retorna o ranking da Olimpíada
        """
        try:
            cache_key = 'api_olympiad_ranking'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                data = LineageStats.olympiad_ranking()
                cache.set(cache_key, data, 300)  # Cache por 5 minutos
            else:
                data = cached_data
            
            # Processa os dados para o formato esperado pelo serializer
            processed_data = []
            for i, player in enumerate(data, 1):
                from utils.resources import get_class_name
                
                processed_player = {
                    'char_name': player.get('char_name', ''),
                    'class_name': get_class_name(player.get('base')) if player.get('base') else '',
                    'points': player.get('olympiad_points', 0),
                    'rank': i
                }
                processed_data.append(processed_player)
            
            serializer = self.get_serializer(processed_data, many=True)
            return Response(serializer.data)
        
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro em olympiad_ranking: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Erro ao buscar ranking da Olimpíada: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@endpoint_enabled('olympiad_all_heroes')
@ServerAPISchema.olympiad_heroes_schema("Todos os Heróis", "Retorna todos os heróis da Olimpíada")
class OlympiadAllHeroesView(GenericAPIView):
    """View para todos os heróis da Olimpíada"""
    permission_classes = [AllowAny]
    serializer_class = OlympiadHeroSerializer
    throttle_classes = [PublicAPIRateThrottle]
    queryset = ApiEndpointToggle.objects.none()  # Empty queryset for DRF Spectacular
    
    def get(self, request):
        """
        Retorna todos os heróis da Olimpíada
        """
        try:
            cache_key = 'api_olympiad_all_heroes'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                data = LineageStats.olympiad_all_heroes()
                cache.set(cache_key, data, 300)
            else:
                data = cached_data
            
            serializer = self.get_serializer(data, many=True)
            return Response(serializer.data)
        
        except Exception as e:
            return Response(
                {'error': 'Erro ao buscar heróis da Olimpíada'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@endpoint_enabled('olympiad_current_heroes')
@ServerAPISchema.olympiad_heroes_schema("Heróis Atuais", "Retorna os heróis atuais da Olimpíada")
class OlympiadCurrentHeroesView(GenericAPIView):
    """View para heróis atuais da Olimpíada"""
    permission_classes = [AllowAny]
    serializer_class = OlympiadHeroSerializer
    throttle_classes = [PublicAPIRateThrottle]
    queryset = ApiEndpointToggle.objects.none()  # Empty queryset for DRF Spectacular
    
    def get(self, request):
        """
        Retorna os heróis atuais da Olimpíada
        """
        try:
            cache_key = 'api_olympiad_current_heroes'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                data = LineageStats.olympiad_current_heroes()
                cache.set(cache_key, data, 300)
            else:
                data = cached_data
            
            serializer = self.get_serializer(data, many=True)
            return Response(serializer.data)
        
        except Exception as e:
            return Response(
                {'error': 'Erro ao buscar heróis atuais da Olimpíada'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@endpoint_enabled('grandboss_status')
@ServerAPISchema.grandboss_status_schema()
class GrandBossStatusView(GenericAPIView):
    """View para status dos Grand Bosses"""
    permission_classes = [AllowAny]
    serializer_class = GrandBossStatusSerializer
    throttle_classes = [PublicAPIRateThrottle]
    queryset = ApiEndpointToggle.objects.none()  # Empty queryset for DRF Spectacular
    
    def get(self, request):
        """
        Retorna o status dos Grand Bosses
        """
        try:
            cache_key = 'api_grandboss_status'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                data = LineageStats.grandboss_status()
                cache.set(cache_key, data, 60)
            else:
                data = cached_data
            
            # Verifica se os dados estão no formato esperado
            if not data or not isinstance(data, list):
                return Response(
                    {'error': 'Dados de status dos Grand Bosses não disponíveis'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            # Processa os dados para o formato esperado pelo serializer
            processed_data = []
            for boss in data:
                boss_id = boss.get('boss_id')
                respawn_time = boss.get('respawn')
                
                # Determina se o boss está vivo baseado no respawn time
                import time
                current_time = time.time()
                is_alive = True
                
                if respawn_time:
                    # Converte para timestamp se necessário
                    if isinstance(respawn_time, str):
                        try:
                            from datetime import datetime
                            respawn_time = datetime.fromisoformat(respawn_time.replace('Z', '+00:00')).timestamp()
                        except:
                            respawn_time = None
                    
                    if respawn_time and respawn_time > current_time:
                        is_alive = False
                
                processed_boss = {
                    'boss_name': f"Boss {boss_id}",  # Pode ser melhorado com um mapeamento
                    'boss_id': boss_id,
                    'is_alive': is_alive,
                    'respawn_time': respawn_time,
                    'location': 'Unknown'  # Pode ser melhorado
                }
                processed_data.append(processed_boss)
            
            serializer = self.get_serializer(processed_data, many=True)
            return Response(serializer.data)
        
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro em grandboss_status: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Erro ao buscar status dos Grand Bosses: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@endpoint_enabled('siege')
@ServerAPISchema.siege_schema()
class SiegeView(GenericAPIView):
    """View para status dos cercos"""
    permission_classes = [AllowAny]
    serializer_class = SiegeSerializer
    throttle_classes = [PublicAPIRateThrottle]
    queryset = ApiEndpointToggle.objects.none()  # Empty queryset for DRF Spectacular
    
    def get(self, request):
        """
        Retorna o status dos cercos
        """
        try:
            cache_key = 'api_siege'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                data = LineageStats.siege()
                cache.set(cache_key, data, 300)
            else:
                data = cached_data
            
            # Processa os dados para o formato esperado pelo serializer
            processed_data = []
            for castle in data:
                # Converte timestamp para datetime se necessário
                siege_date = castle.get('sdate')
                if siege_date:
                    try:
                        # Se for um timestamp em milissegundos, converte para segundos
                        if isinstance(siege_date, (int, float)) and siege_date > 1000000000000:
                            siege_date = siege_date / 1000
                        
                        # Converte para datetime
                        from datetime import datetime
                        siege_date = datetime.fromtimestamp(siege_date)
                    except (ValueError, TypeError, OSError):
                        siege_date = None
                
                processed_castle = {
                    'castle_name': castle.get('name', ''),
                    'castle_id': castle.get('id', 0),
                    'owner_clan': castle.get('clan_name', ''),
                    'siege_date': siege_date,
                    'is_under_siege': bool(castle.get('sdate'))
                }
                processed_data.append(processed_castle)
            
            serializer = self.get_serializer(processed_data, many=True)
            return Response(serializer.data)
        
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro em siege: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Erro ao buscar dados dos cercos: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@endpoint_enabled('siege_participants')
@ServerAPISchema.siege_participants_schema()
class SiegeParticipantsView(GenericAPIView):
    """View para participantes do cerco"""
    permission_classes = [AllowAny]
    serializer_class = SiegeParticipantSerializer
    throttle_classes = [PublicAPIRateThrottle]
    queryset = ApiEndpointToggle.objects.none()  # Empty queryset for DRF Spectacular
    
    def get(self, request, castle_id):
        """
        Retorna os participantes de um cerco específico
        """
        try:
            if castle_id not in range(1, 10):
                return Response(
                    {'error': 'castle_id deve ser um valor entre 1 e 9'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            cache_key = f'api_siege_participants_{castle_id}'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                data = LineageStats.siege_participants(castle_id=castle_id)
                cache.set(cache_key, data, 300)
            else:
                data = cached_data
            
            serializer = self.get_serializer(data, many=True)
            return Response(serializer.data)
        
        except Exception as e:
            return Response(
                {'error': 'Erro ao buscar participantes do cerco'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@endpoint_enabled('boss_jewel_locations')
@ServerAPISchema.boss_jewel_locations_schema()
class BossJewelLocationsView(GenericAPIView):
    """View para localizações dos Boss Jewels"""
    permission_classes = [AllowAny]
    serializer_class = BossJewelLocationSerializer
    throttle_classes = [PublicAPIRateThrottle]
    queryset = ApiEndpointToggle.objects.none()  # Empty queryset for DRF Spectacular
    
    def get(self, request):
        """
        Retorna as localizações dos Boss Jewels
        """
        try:
            jewel_ids = request.GET.get("ids", "")
            
            if not jewel_ids:
                return Response(
                    {"error": "Parâmetro 'ids' é obrigatório"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                jewel_ids_list = [int(id) for id in jewel_ids.split(',')]
            except ValueError:
                return Response(
                    {"error": "Formato de ID inválido"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            allowed_ids = [6656, 6657, 6658, 6659, 6660, 6661, 8191]
            if not all(id in allowed_ids for id in jewel_ids_list):
                return Response(
                    {"error": "ID(s) de jewel inválido(s)"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            cache_key = f'api_boss_jewel_locations_{jewel_ids}'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                data = LineageStats.boss_jewel_locations(boss_jewel_ids=jewel_ids_list)
                cache.set(cache_key, data, 300)
            else:
                data = cached_data
            
            # Processa os dados para o formato esperado pelo serializer
            processed_data = []
            for jewel in data:
                # Mapeia IDs para nomes de jewels
                jewel_names = {
                    6656: "Antharas Jewel",
                    6657: "Valakas Jewel", 
                    6658: "Lindvior Jewel",
                    6659: "Frintezza Jewel",
                    6660: "Baium Jewel",
                    6661: "Queen Ant Jewel",
                    8191: "Core Jewel"
                }
                
                processed_jewel = {
                    'jewel_id': jewel.get('item_id', 0),
                    'jewel_name': jewel_names.get(jewel.get('item_id'), f"Jewel {jewel.get('item_id')}"),
                    'location': f"{jewel.get('char_name', 'Unknown')} ({jewel.get('clan_name', 'No Clan')})",
                    'coordinates': '',  # Não disponível nos dados
                    'respawn_time': None  # Não disponível nos dados
                }
                processed_data.append(processed_jewel)
            
            serializer = self.get_serializer(processed_data, many=True)
            return Response(serializer.data)
        
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro em boss_jewel_locations: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Erro ao buscar localizações dos Boss Jewels: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# =========================== AUTHENTICATION VIEWS ===========================

@AuthAPISchema.login_schema()
class LoginView(TokenObtainPairView):
    """View para login com JWT"""
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            
            # Adiciona informações extras à resposta
            response.data.update({
                'message': 'Login realizado com sucesso',
                'timestamp': timezone.now().isoformat(),
            })
            
            return response
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Erro no login: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Erro ao realizar login'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@AuthAPISchema.refresh_token_schema()
class RefreshTokenView(TokenRefreshView):
    """View para refresh de token JWT"""
    serializer_class = RefreshTokenSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            response.data.update({
                'message': 'Token atualizado com sucesso',
                'timestamp': timezone.now().isoformat(),
            })
            return response
        except Exception as e:
            return Response(
                {'error': 'Token inválido ou expirado'},
                status=status.HTTP_401_UNAUTHORIZED
            )


@AuthAPISchema.logout_schema()
class LogoutView(APIView):
    """View para logout"""
    permission_classes = [IsAuthenticated]
    serializer_class = APIResponseSerializer
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response({
                'message': 'Logout realizado com sucesso',
                'timestamp': timezone.now().isoformat(),
            })
        except Exception as e:
            return Response(
                {'error': 'Erro ao realizar logout'},
                status=status.HTTP_400_BAD_REQUEST
            )


@UserAPISchema.user_profile_schema()
class UserProfileView(APIView):
    """View para perfil do usuário"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
    
    def get(self, request):
        """Retorna o perfil do usuário logado"""
        try:
            serializer = UserProfileSerializer(request.user)
            return Response({
                'success': True,
                'data': serializer.data,
                'timestamp': timezone.now().isoformat(),
            })
        except Exception as e:
            return Response(
                {'error': 'Erro ao buscar perfil do usuário'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request):
        """Atualiza o perfil do usuário"""
        try:
            serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'Perfil atualizado com sucesso',
                    'data': serializer.data,
                    'timestamp': timezone.now().isoformat(),
                })
            return Response(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Erro ao atualizar perfil'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@UserAPISchema.change_password_schema()
class ChangePasswordView(APIView):
    """View para mudança de senha"""
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer
    
    def post(self, request):
        try:
            serializer = ChangePasswordSerializer(data=request.data)
            if serializer.is_valid():
                user = request.user
                if not user.check_password(serializer.validated_data['old_password']):
                    return Response(
                        {'error': 'Senha atual incorreta'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                
                return Response({
                    'success': True,
                    'message': 'Senha alterada com sucesso',
                    'timestamp': timezone.now().isoformat(),
                })
            return Response(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Erro ao alterar senha'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# =========================== GAME VIEWS ===========================

@SearchAPISchema.character_search_schema()
class CharacterSearchView(APIView):
    """View para busca de personagens"""
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIRateThrottle]
    serializer_class = CharacterSerializer
    
    def get(self, request):
        try:
            query = request.GET.get('q', '').strip()
            if not query or len(query) < 2:
                return Response(
                    {'error': 'Query deve ter pelo menos 2 caracteres'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Busca personagens no banco de dados do jogo
            cache_key = f'api_character_search_{query}'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                # Aqui você implementaria a busca real no banco do jogo
                # Por enquanto, retorna dados mock
                data = LineageStats.search_characters(query) if hasattr(LineageStats, 'search_characters') else []
                cache.set(cache_key, data, 300)  # Cache por 5 minutos
            else:
                data = cached_data
            
            serializer = CharacterSerializer(data, many=True)
            return Response({
                'success': True,
                'data': serializer.data,
                'count': len(serializer.data),
                'timestamp': timezone.now().isoformat(),
            })
        except Exception as e:
            return Response(
                {'error': 'Erro ao buscar personagens'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@SearchAPISchema.item_search_schema()
class ItemSearchView(APIView):
    """View para busca de itens"""
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIRateThrottle]
    serializer_class = ItemSerializer
    
    def get(self, request):
        try:
            query = request.GET.get('q', '').strip()
            if not query or len(query) < 2:
                return Response(
                    {'error': 'Query deve ter pelo menos 2 caracteres'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            cache_key = f'api_item_search_{query}'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                # Implementar busca real de itens
                data = LineageStats.search_items(query) if hasattr(LineageStats, 'search_items') else []
                cache.set(cache_key, data, 600)  # Cache por 10 minutos
            else:
                data = cached_data
            
            serializer = ItemSerializer(data, many=True)
            return Response({
                'success': True,
                'data': serializer.data,
                'count': len(serializer.data),
                'timestamp': timezone.now().isoformat(),
            })
        except Exception as e:
            return Response(
                {'error': 'Erro ao buscar itens'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@GameDataAPISchema.clan_detail_schema()
class ClanDetailView(APIView):
    """View para detalhes de clã"""
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIRateThrottle]
    serializer_class = ClanDetailSerializer
    
    def get(self, request, clan_name):
        try:
            cache_key = f'api_clan_detail_{clan_name}'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                # Busca dados do clã
                data = LineageStats.get_clan_details(clan_name) if hasattr(LineageStats, 'get_clan_details') else None
                if data:
                    cache.set(cache_key, data, 300)  # Cache por 5 minutos
            else:
                data = cached_data
            
            if not data:
                return Response(
                    {'error': 'Clã não encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = ClanDetailSerializer(data)
            return Response({
                'success': True,
                'data': serializer.data,
                'timestamp': timezone.now().isoformat(),
            })
        except Exception as e:
            return Response(
                {'error': 'Erro ao buscar dados do clã'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@GameDataAPISchema.auction_items_schema()
class AuctionItemsView(APIView):
    """View para itens do leilão"""
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIRateThrottle]
    serializer_class = AuctionItemSerializer
    
    def get(self, request):
        try:
            limit = int(request.GET.get("limit", 20))
            limit = min(limit, 100)
            
            cache_key = f'api_auction_items_{limit}'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                # Busca itens do leilão
                data = LineageStats.get_auction_items(limit) if hasattr(LineageStats, 'get_auction_items') else []
                cache.set(cache_key, data, 60)  # Cache por 1 minuto
            else:
                data = cached_data
            
            serializer = AuctionItemSerializer(data, many=True)
            return Response({
                'success': True,
                'data': serializer.data,
                'count': len(serializer.data),
                'timestamp': timezone.now().isoformat(),
            })
        except ValueError:
            return Response(
                {'error': 'Parâmetro limit deve ser um número válido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Erro ao buscar itens do leilão'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# =========================== USER DASHBOARD VIEWS ===========================

@UserAPISchema.user_dashboard_schema()
class UserDashboardView(APIView):
    """View para dashboard do usuário"""
    permission_classes = [IsAuthenticated]
    serializer_class = APIResponseSerializer
    
    def get(self, request):
        try:
            user = request.user
            
            # Busca dados do usuário no jogo
            game_data = LineageStats.get_user_stats(user.username) if hasattr(LineageStats, 'get_user_stats') else {}
            
            dashboard_data = {
                'user_info': {
                    'username': user.username,
                    'email': user.email,
                    'date_joined': user.date_joined,
                    'last_login': user.last_login,
                },
                'game_stats': game_data,
                'server_status': {
                    'online': True,
                    'players_online': LineageStats.players_online()[0].get('quant', 0) if LineageStats.players_online() else 0,
                }
            }
            
            return Response({
                'success': True,
                'data': dashboard_data,
                'timestamp': timezone.now().isoformat(),
            })
        except Exception as e:
            return Response(
                {'error': 'Erro ao buscar dados do dashboard'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@UserAPISchema.user_stats_schema()
class UserStatsView(APIView):
    """View para estatísticas do usuário"""
    permission_classes = [IsAuthenticated]
    serializer_class = APIResponseSerializer
    
    def get(self, request):
        try:
            user = request.user
            
            # Busca estatísticas do usuário
            stats_data = LineageStats.get_user_detailed_stats(user.username) if hasattr(LineageStats, 'get_user_detailed_stats') else {}
            
            return Response({
                'success': True,
                'data': stats_data,
                'timestamp': timezone.now().isoformat(),
            })
        except Exception as e:
            return Response(
                {'error': 'Erro ao buscar estatísticas do usuário'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# =========================== SERVER STATUS VIEWS ===========================

@ServerStatusAPISchema.server_status_schema()
class ServerStatusView(APIView):
    """View para status do servidor"""
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIRateThrottle]
    serializer_class = ServerStatusSerializer
    
    def get(self, request):
        try:
            # Verifica status do servidor
            game_server_status = LineageStats.check_server_status() if hasattr(LineageStats, 'check_server_status') else True
            
            status_data = {
                'server_name': getattr(settings, 'PROJECT_TITLE', 'Lineage 2 Server'),
                'status': 'online' if game_server_status else 'offline',
                'players_online': LineageStats.players_online()[0].get('quant', 0) if LineageStats.players_online() else 0,
                'max_players': 1000,  # Configurável
                'uptime': '24h 30m',  # Implementar cálculo real
                'last_update': timezone.now(),
                'version': getattr(settings, 'VERSION', '1.0.0'),
                'maintenance_mode': False,
            }
            
            serializer = ServerStatusSerializer(status_data)
            return Response({
                'success': True,
                'data': serializer.data,
                'timestamp': timezone.now().isoformat(),
            })
        except Exception as e:
            return Response(
                {'error': 'Erro ao verificar status do servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# =========================== API INFO VIEWS ===========================

@APIInfoSchema.api_info_schema()
class APIInfoView(APIView):
    """View para informações da API"""
    permission_classes = [AllowAny]
    serializer_class = APIResponseSerializer
    
    def get(self, request):
        try:
            api_info = {
                'name': 'Lineage 2 API',
                'version': getattr(settings, 'VERSION', '1.0.0'),
                'description': 'API pública para servidores de Lineage 2',
                'documentation': '/api/v1/schema/swagger/',
                'endpoints': {
                    'public': [
                        '/api/v1/server/status/',
                        '/api/v1/server/players-online/',
                        '/api/v1/search/character/',
                        '/api/v1/search/item/',
                        '/api/v1/clan/{name}/',
                        '/api/v1/auction/items/',
                    ],
                    'authenticated': [
                        '/api/v1/auth/login/',
                        '/api/v1/auth/refresh/',
                        '/api/v1/auth/logout/',
                        '/api/v1/user/profile/',
                        '/api/v1/user/dashboard/',
                        '/api/v1/user/stats/',
                    ]
                },
                'rate_limits': {
                    'anonymous': '30/minute',
                    'authenticated': '100/minute'
                }
            }
            
            return Response({
                'success': True,
                'data': api_info,
                'timestamp': timezone.now().isoformat(),
            })
        except Exception as e:
            return Response(
                {'error': 'Erro ao buscar informações da API'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
