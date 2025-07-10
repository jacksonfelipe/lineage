from drf_spectacular.extensions import OpenApiViewExtension
from drf_spectacular.plumbing import build_basic_type, build_parameter_type
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from rest_framework import status
from .serializers import (
    PlayerOnlineSerializer, TopPlayerSerializer, TopClanSerializer,
    OlympiadRankingSerializer, OlympiadHeroSerializer, GrandBossStatusSerializer,
    SiegeSerializer, SiegeParticipantSerializer, BossJewelLocationSerializer
)


class ServerAPISchema:
    """Schema para APIs do servidor Lineage 2"""
    
    @staticmethod
    def players_online_schema():
        return extend_schema(
            summary="Jogadores Online",
            description="Retorna o número de jogadores atualmente online no servidor",
            responses={
                status.HTTP_200_OK: PlayerOnlineSerializer
            },
            tags=["Servidor"]
        )
    
    @staticmethod
    def top_pvp_schema():
        return extend_schema(
            summary="Ranking PvP",
            description="Retorna o ranking dos jogadores com mais PvPs",
            parameters=[
                OpenApiParameter(
                    name="limit",
                    type=int,
                    location=OpenApiParameter.QUERY,
                    description="Número máximo de registros (padrão: 10, máximo: 100)",
                    default=10,
                    examples=[
                        OpenApiExample("10 registros", value=10),
                        OpenApiExample("50 registros", value=50),
                        OpenApiExample("100 registros", value=100),
                    ]
                )
            ],
            responses={
                status.HTTP_200_OK: TopPlayerSerializer(many=True)
            },
            tags=["Servidor"]
        )
    
    @staticmethod
    def top_pk_schema():
        return extend_schema(
            summary="Ranking PK",
            description="Retorna o ranking dos jogadores com mais PKs",
            parameters=[
                OpenApiParameter(
                    name="limit",
                    type=int,
                    location=OpenApiParameter.QUERY,
                    description="Número máximo de registros (padrão: 10, máximo: 100)",
                    default=10,
                    examples=[
                        OpenApiExample("10 registros", value=10),
                        OpenApiExample("50 registros", value=50),
                        OpenApiExample("100 registros", value=100),
                    ]
                )
            ],
            responses={
                status.HTTP_200_OK: TopPlayerSerializer(many=True)
            },
            tags=["Servidor"]
        )
    
    @staticmethod
    def top_rich_schema():
        return extend_schema(
            summary="Ranking de Riqueza",
            description="Retorna o ranking dos jogadores mais ricos (Adena)",
            parameters=[
                OpenApiParameter(
                    name="limit",
                    type=int,
                    location=OpenApiParameter.QUERY,
                    description="Número máximo de registros (padrão: 10, máximo: 100)",
                    default=10,
                    examples=[
                        OpenApiExample("10 registros", value=10),
                        OpenApiExample("50 registros", value=50),
                        OpenApiExample("100 registros", value=100),
                    ]
                )
            ],
            responses={
                status.HTTP_200_OK: TopPlayerSerializer(many=True)
            },
            tags=["Servidor"]
        )
    
    @staticmethod
    def top_online_schema():
        return extend_schema(
            summary="Ranking de Tempo Online",
            description="Retorna o ranking dos jogadores com mais tempo online",
            parameters=[
                OpenApiParameter(
                    name="limit",
                    type=int,
                    location=OpenApiParameter.QUERY,
                    description="Número máximo de registros (padrão: 10, máximo: 100)",
                    default=10,
                    examples=[
                        OpenApiExample("10 registros", value=10),
                        OpenApiExample("50 registros", value=50),
                        OpenApiExample("100 registros", value=100),
                    ]
                )
            ],
            responses={
                status.HTTP_200_OK: TopPlayerSerializer(many=True)
            },
            tags=["Servidor"]
        )
    
    @staticmethod
    def top_level_schema():
        return extend_schema(
            summary="Ranking de Nível",
            description="Retorna o ranking dos jogadores com maior nível",
            parameters=[
                OpenApiParameter(
                    name="limit",
                    type=int,
                    location=OpenApiParameter.QUERY,
                    description="Número máximo de registros (padrão: 10, máximo: 100)",
                    default=10,
                    examples=[
                        OpenApiExample("10 registros", value=10),
                        OpenApiExample("50 registros", value=50),
                        OpenApiExample("100 registros", value=100),
                    ]
                )
            ],
            responses={
                status.HTTP_200_OK: TopPlayerSerializer(many=True)
            },
            tags=["Servidor"]
        )
    
    @staticmethod
    def top_clan_schema():
        return extend_schema(
            summary="Ranking de Clãs",
            description="Retorna o ranking dos clãs mais poderosos",
            parameters=[
                OpenApiParameter(
                    name="limit",
                    type=int,
                    location=OpenApiParameter.QUERY,
                    description="Número máximo de registros (padrão: 10, máximo: 100)",
                    default=10
                )
            ],
            responses={
                status.HTTP_200_OK: TopClanSerializer(many=True)
            },
            tags=["Servidor"]
        )
    
    @staticmethod
    def olympiad_ranking_schema():
        return extend_schema(
            summary="Ranking da Olimpíada",
            description="Retorna o ranking atual da Olimpíada",
            responses={
                status.HTTP_200_OK: OlympiadRankingSerializer(many=True)
            },
            tags=["Olimpíada"]
        )
    
    @staticmethod
    def olympiad_heroes_schema(endpoint_name, description):
        return extend_schema(
            summary=f"Heróis da Olimpíada - {endpoint_name}",
            description=description,
            responses={
                status.HTTP_200_OK: OlympiadHeroSerializer(many=True)
            },
            tags=["Olimpíada"]
        )
    
    @staticmethod
    def grandboss_status_schema():
        return extend_schema(
            summary="Status dos Grand Bosses",
            description="Retorna o status atual dos Grand Bosses",
            responses={
                status.HTTP_200_OK: GrandBossStatusSerializer(many=True)
            },
            tags=["Bosses"]
        )
    
    @staticmethod
    def siege_schema():
        return extend_schema(
            summary="Status dos Cercos",
            description="Retorna o status atual dos castelos e cercos",
            responses={
                status.HTTP_200_OK: SiegeSerializer(many=True)
            },
            tags=["Cercos"]
        )
    
    @staticmethod
    def siege_participants_schema():
        return extend_schema(
            summary="Participantes do Cerco",
            description="Retorna os clãs participantes de um cerco específico",
            parameters=[
                OpenApiParameter(
                    name="castle_id",
                    type=int,
                    location=OpenApiParameter.PATH,
                    description="ID do castelo (1-9)",
                    examples=[
                        OpenApiExample("Castelo Aden", value=1),
                        OpenApiExample("Castelo Dion", value=2),
                        OpenApiExample("Castelo Giran", value=3),
                    ]
                )
            ],
            responses={
                status.HTTP_200_OK: SiegeParticipantSerializer(many=True)
            },
            tags=["Cercos"]
        )
    
    @staticmethod
    def boss_jewel_locations_schema():
        return extend_schema(
            summary="Localizações dos Boss Jewels",
            description="Retorna as localizações dos Boss Jewels",
            parameters=[
                OpenApiParameter(
                    name="ids",
                    type=str,
                    location=OpenApiParameter.QUERY,
                    description="IDs dos jewels separados por vírgula",
                    required=True,
                    examples=[
                        OpenApiExample("Jewel 6656", value="6656"),
                        OpenApiExample("Múltiplos jewels", value="6656,6657,6658"),
                    ]
                )
            ],
            responses={
                status.HTTP_200_OK: BossJewelLocationSerializer(many=True)
            },
            tags=["Bosses"]
        ) 