from apps.lineage.server.database import LineageDB
from apps.lineage.server.utils.cache import cache_lineage_result


class LineageStats:

    @staticmethod
    @cache_lineage_result(timeout=300)
    def players_online():
        sql = "SELECT COUNT(*) AS quant FROM characters WHERE online > 0 AND accesslevel = '0'"
        return LineageDB.query(sql)

    @staticmethod
    @cache_lineage_result(timeout=300)
    def top_pvp(limit=10):
        sql = f"""
            SELECT C.char_name, C.pvpkills, C.pkkills, C.online, C.onlinetime, D.name AS clan_name
            FROM characters AS C
            LEFT JOIN clan_subpledges AS D ON D.clan_id = C.clanid AND D.type = '0'
            WHERE C.accesslevel = '0'
            ORDER BY pvpkills DESC, pkkills DESC, onlinetime DESC, char_name ASC
            LIMIT {limit}
        """
        return LineageDB.query(sql)

    @staticmethod
    @cache_lineage_result(timeout=300)
    def top_pk(limit=10):
        sql = f"""
            SELECT C.char_name, C.pvpkills, C.pkkills, C.online, C.onlinetime, D.name AS clan_name
            FROM characters AS C
            LEFT JOIN clan_subpledges AS D ON D.clan_id = C.clanid AND D.type = '0'
            WHERE C.accesslevel = '0'
            ORDER BY pkkills DESC, pvpkills DESC, onlinetime DESC, char_name ASC
            LIMIT {limit}
        """
        return LineageDB.query(sql)

    @staticmethod
    @cache_lineage_result(timeout=300)
    def top_online(limit=10):
        sql = f"""
            SELECT C.char_name, C.pvpkills, C.pkkills, C.online, C.onlinetime, D.name AS clan_name
            FROM characters AS C
            LEFT JOIN clan_subpledges AS D ON D.clan_id = C.clanid AND D.type = '0'
            WHERE C.accesslevel = '0'
            ORDER BY onlinetime DESC, pvpkills DESC, pkkills DESC, char_name ASC
            LIMIT {limit}
        """
        return LineageDB.query(sql)

    @staticmethod
    @cache_lineage_result(timeout=300)
    def top_level(limit=10):
        sql = f"""
            SELECT C.char_name, C.pvpkills, C.pkkills, C.online, C.onlinetime, CS.level, D.name AS clan_name
            FROM characters AS C
            LEFT JOIN character_subclasses AS CS ON CS.char_obj_id = C.obj_Id AND CS.isBase = '1'
            LEFT JOIN clan_subpledges AS D ON D.clan_id = C.clanid AND D.type = '0'
            WHERE C.accesslevel = '0'
            ORDER BY level DESC, exp DESC, onlinetime DESC, char_name ASC
            LIMIT {limit}
        """
        return LineageDB.query(sql)

    @staticmethod
    @cache_lineage_result(timeout=300)
    def top_adena(limit=10, adn_billion_item=0):
        part1 = ""
        if adn_billion_item != 0:
            part1 = f"""
                IFNULL((SELECT (SUM(I2.amount) * 1000000000)
                        FROM items AS I2
                        WHERE I2.owner_id = C.obj_Id AND I2.item_type = '{adn_billion_item}'
                        GROUP BY I2.owner_id), 0) +
            """
        sql = f"""
            SELECT 
                C.char_name, 
                C.online, 
                C.onlinetime, 
                CS.level, 
                D.name AS clan_name, 
                (
                    {part1}
                    IFNULL((SELECT SUM(I1.amount)
                            FROM items AS I1
                            WHERE I1.owner_id = C.obj_Id AND I1.item_type = '57'
                            GROUP BY I1.owner_id), 0)
                ) AS adenas
            FROM characters AS C
            LEFT JOIN character_subclasses AS CS ON CS.char_obj_id = C.obj_Id AND CS.isBase = '1'
            LEFT JOIN clan_subpledges AS D ON D.clan_id = C.clanid AND D.type = '0'
            ORDER BY adenas DESC, onlinetime DESC, char_name ASC
            LIMIT {limit}
        """
        return LineageDB.query(sql)
