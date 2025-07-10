from rest_framework import serializers


class PlayerOnlineSerializer(serializers.Serializer):
    """Serializer para dados de jogadores online"""
    online_count = serializers.IntegerField()
    fake_players = serializers.IntegerField(required=False)
    real_players = serializers.IntegerField(required=False)


class TopPlayerSerializer(serializers.Serializer):
    """Serializer para dados de ranking de jogadores"""
    char_name = serializers.CharField()
    level = serializers.IntegerField()
    clan_name = serializers.CharField(allow_blank=True, allow_null=True)
    pvp_count = serializers.IntegerField(required=False)
    pk_count = serializers.IntegerField(required=False)
    adena = serializers.IntegerField(required=False)
    online_time = serializers.IntegerField(required=False)
    class_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class TopClanSerializer(serializers.Serializer):
    """Serializer para dados de ranking de clãs"""
    clan_name = serializers.CharField()
    leader_name = serializers.CharField()
    level = serializers.IntegerField()
    member_count = serializers.IntegerField()
    reputation = serializers.IntegerField(required=False)


class OlympiadRankingSerializer(serializers.Serializer):
    """Serializer para dados de ranking da Olimpíada"""
    char_name = serializers.CharField()
    class_name = serializers.CharField()
    points = serializers.IntegerField()
    rank = serializers.IntegerField()


class OlympiadHeroSerializer(serializers.Serializer):
    """Serializer para dados de heróis da Olimpíada"""
    char_name = serializers.CharField()
    class_name = serializers.CharField()
    hero_type = serializers.CharField()
    hero_count = serializers.IntegerField()
    hero_date = serializers.DateField(required=False, allow_null=True)


class GrandBossStatusSerializer(serializers.Serializer):
    """Serializer para status dos Grand Bosses"""
    boss_name = serializers.CharField()
    boss_id = serializers.IntegerField()
    is_alive = serializers.BooleanField()
    respawn_time = serializers.DateTimeField(required=False, allow_null=True)
    location = serializers.CharField(required=False, allow_blank=True)


class SiegeSerializer(serializers.Serializer):
    """Serializer para dados de cerco"""
    castle_name = serializers.CharField()
    castle_id = serializers.IntegerField()
    owner_clan = serializers.CharField(allow_blank=True, allow_null=True)
    siege_date = serializers.DateTimeField(required=False, allow_null=True)
    is_under_siege = serializers.BooleanField()


class SiegeParticipantSerializer(serializers.Serializer):
    """Serializer para participantes do cerco"""
    clan_name = serializers.CharField()
    leader_name = serializers.CharField()
    member_count = serializers.IntegerField()
    registration_date = serializers.DateTimeField(required=False, allow_null=True)


class BossJewelLocationSerializer(serializers.Serializer):
    """Serializer para localizações dos Boss Jewels"""
    jewel_id = serializers.IntegerField()
    jewel_name = serializers.CharField()
    location = serializers.CharField()
    coordinates = serializers.CharField(required=False, allow_blank=True)
    respawn_time = serializers.DateTimeField(required=False, allow_null=True) 