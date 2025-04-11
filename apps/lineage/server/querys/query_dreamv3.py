from apps.lineage.server.database import LineageDB
from apps.lineage.server.utils.cache import cache_lineage_result

import time
import base64
import hashlib


class LineageStats:

    @staticmethod
    def _run_query(sql, **kwargs):
        return LineageDB().select(sql, use_cache=True, **kwargs)

    @staticmethod
    @cache_lineage_result(timeout=300)
    def players_online():
        sql = "SELECT COUNT(*) AS quant FROM characters WHERE online > 0 AND accesslevel = '0'"
        return LineageStats._run_query(sql)

    @staticmethod
    @cache_lineage_result(timeout=300)
    def top_pvp(limit=10):
        sql = f"""
            SELECT C.char_name, C.pvpkills, C.pkkills, C.online, C.onlinetime, D.name AS clan_name
            FROM characters C
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.type = '0'
            WHERE C.accesslevel = '0'
            ORDER BY pvpkills DESC, pkkills DESC, onlinetime DESC, char_name ASC
            LIMIT {limit}
        """
        return LineageStats._run_query(sql)

    @staticmethod
    @cache_lineage_result(timeout=300)
    def top_pk(limit=10):
        sql = f"""
            SELECT C.char_name, C.pvpkills, C.pkkills, C.online, C.onlinetime, D.name AS clan_name
            FROM characters C
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.type = '0'
            WHERE C.accesslevel = '0'
            ORDER BY pkkills DESC, pvpkills DESC, onlinetime DESC, char_name ASC
            LIMIT {limit}
        """
        return LineageStats._run_query(sql)

    @staticmethod
    @cache_lineage_result(timeout=300)
    def top_online(limit=10):
        sql = f"""
            SELECT C.char_name, C.pvpkills, C.pkkills, C.online, C.onlinetime, D.name AS clan_name
            FROM characters C
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.type = '0'
            WHERE C.accesslevel = '0'
            ORDER BY onlinetime DESC, pvpkills DESC, pkkills DESC, char_name ASC
            LIMIT {limit}
        """
        return LineageStats._run_query(sql)

    @staticmethod
    @cache_lineage_result(timeout=300)
    def top_level(limit=10):
        sql = f"""
            SELECT C.char_name, C.pvpkills, C.pkkills, C.online, C.onlinetime, CS.level, D.name AS clan_name
            FROM characters C
            LEFT JOIN character_subclasses CS ON CS.char_obj_id = C.obj_Id AND CS.isBase = '1'
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.type = '0'
            WHERE C.accesslevel = '0'
            ORDER BY level DESC, exp DESC, onlinetime DESC, char_name ASC
            LIMIT {limit}
        """
        return LineageStats._run_query(sql)

    @staticmethod
    @cache_lineage_result(timeout=300)
    def top_adena(limit=10, adn_billion_item=0, value_item=1000000):
        item_bonus_sql = ""
        if adn_billion_item != 0:
            item_bonus_sql = f"""
                IFNULL((SELECT SUM(I2.amount) * {value_item}
                        FROM items I2
                        WHERE I2.owner_id = C.obj_Id AND I2.item_type = '{adn_billion_item}'
                        GROUP BY I2.owner_id), 0) +
            """

        sql = f"""
            SELECT 
                C.char_name, C.online, C.onlinetime, CS.level, D.name AS clan_name,
                (
                    {item_bonus_sql}
                    IFNULL((SELECT SUM(I1.amount)
                            FROM items I1
                            WHERE I1.owner_id = C.obj_Id AND I1.item_type = '57'
                            GROUP BY I1.owner_id), 0)
                ) AS adenas
            FROM characters C
            LEFT JOIN character_subclasses CS ON CS.char_obj_id = C.obj_Id AND CS.isBase = '1'
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.type = '0'
            ORDER BY adenas DESC, onlinetime DESC, char_name ASC
            LIMIT {limit}
        """
        return LineageStats._run_query(sql)

    @staticmethod
    @cache_lineage_result(timeout=300)
    def top_clans(limit=10):
        sql = f"""
            SELECT D.name AS clan_name, C.clan_level, C.reputation_score, A.ally_name, 
                   P.char_name, 
                   (SELECT COUNT(*) FROM characters WHERE clanid = C.clan_id) AS membros
            FROM clan_data C
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clan_id AND D.type = '0'
            LEFT JOIN ally_data A ON A.ally_id = C.ally_id
            LEFT JOIN characters P ON P.obj_Id = D.leader_id
            ORDER BY C.clan_level DESC, C.reputation_score DESC, membros DESC
            LIMIT {limit}
        """
        return LineageStats._run_query(sql)

    @staticmethod
    @cache_lineage_result(timeout=300)
    def olympiad_ranking():
        sql = """
            SELECT C.char_name, C.online, D.name AS clan_name, CS.class_id AS base, O.points_current AS olympiad_points
            FROM oly_nobles O
            LEFT JOIN characters C ON C.obj_Id = O.char_id
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.type = '0'
            LEFT JOIN character_subclasses CS ON CS.char_obj_id = C.obj_Id AND CS.isBase = '1'
            ORDER BY olympiad_points DESC
        """
        return LineageStats._run_query(sql)

    @staticmethod
    @cache_lineage_result(timeout=300)
    def olympiad_all_heroes():
        sql = """
            SELECT C.char_name, C.online, D.name AS clan_name, A.ally_name, 
                   CS.class_id AS base, H.count
            FROM oly_heroes H
            LEFT JOIN characters C ON C.obj_Id = H.char_id
            LEFT JOIN character_subclasses CS ON CS.char_obj_id = C.obj_Id AND CS.isBase = '1'
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.type = '0'
            LEFT JOIN clan_data CLAN ON CLAN.clan_id = C.clanid
            LEFT JOIN ally_data A ON A.ally_id = CLAN.clan_id
            WHERE H.played > 0 AND H.count > 0
            ORDER BY H.count DESC, base ASC, char_name ASC
        """
        return LineageStats._run_query(sql)

    @staticmethod
    @cache_lineage_result(timeout=300)
    def olympiad_current_heroes():
        sql = """
            SELECT C.char_name, C.online, D.name AS clan_name, A.ally_name, CS.class_id AS base
            FROM oly_heroes H
            LEFT JOIN characters C ON C.obj_Id = H.char_id
            LEFT JOIN character_subclasses CS ON CS.char_obj_id = C.obj_Id AND CS.isBase = '1'
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.type = '0'
            LEFT JOIN clan_data CLAN ON CLAN.clan_id = C.clanid
            LEFT JOIN ally_data A ON A.ally_id = CLAN.clan_id
            WHERE H.played > 0 AND H.count > 0
            ORDER BY base ASC
        """
        return LineageStats._run_query(sql)

    @staticmethod
    @cache_lineage_result(timeout=300)
    def grandboss_status():
        sql = """
            SELECT B.bossId AS boss_id, B.respawnDate AS respawn, N.name, N.level
            FROM epic_boss_spawn B
            INNER JOIN site_bosses N ON N.id = B.bossId
            ORDER BY respawn DESC, level DESC, name ASC
        """
        return LineageStats._run_query(sql)

    @staticmethod
    @cache_lineage_result(timeout=300)
    def raidboss_status():
        sql = """
            SELECT B.id AS boss_id, B.respawn_delay AS respawn, N.name, N.level
            FROM raidboss_status B
            INNER JOIN site_bosses N ON N.id = B.id
            ORDER BY respawn DESC, level DESC, name ASC
        """
        return LineageStats._run_query(sql)

    @staticmethod
    @cache_lineage_result(timeout=300)
    def siege():
        sql = """
            SELECT W.id, W.name, W.siege_date AS sdate, W.treasury AS stax,
                   P.char_name, CS.name AS clan_name, A.ally_name
            FROM castle W
            LEFT JOIN clan_data C ON C.hasCastle = W.id
            LEFT JOIN clan_subpledges CS ON CS.clan_id = C.clan_id AND CS.type = '0'
            LEFT JOIN ally_data A ON A.ally_id = C.ally_id
            LEFT JOIN characters P ON P.obj_Id = CS.leader_id
        """
        return LineageStats._run_query(sql)

    @staticmethod
    @cache_lineage_result(timeout=300)
    def siege_participants(castle_id):
        sql = f"""
            SELECT S.type, C.name AS clan_name
            FROM siege_clans S
            LEFT JOIN clan_subpledges C ON C.clan_id = S.clan_id AND C.type = '0'
            WHERE S.residence_id = '{castle_id}'
        """
        return LineageStats._run_query(sql)

    @staticmethod
    @cache_lineage_result(timeout=300)
    def boss_jewel_locations(boss_jewel_ids):
        ids_tuple = tuple(boss_jewel_ids)
        sql = f"""
            SELECT I.owner_id, I.item_type AS item_id, SUM(I.amount) AS count, 
                   C.char_name, P.name AS clan_name
            FROM items I
            INNER JOIN characters C ON C.obj_Id = I.owner_id
            LEFT JOIN clan_subpledges P ON P.clan_id = C.clanid AND P.type = '0'
            WHERE I.item_type IN {ids_tuple}
            GROUP BY I.owner_id, C.char_name, P.name, I.item_type
            ORDER BY count DESC, C.char_name ASC
        """
        return LineageStats._run_query(sql)


class LineageServices:

    @staticmethod
    @cache_lineage_result(timeout=300)
    def find_chars(login):
        sql = f"""
            SELECT
                C.*, 
                (SELECT S0.class_id FROM character_subclasses AS S0 WHERE S0.char_obj_id = C.obj_Id AND S0.isBase = '1' LIMIT 1) AS base_class,
                (SELECT S1.class_id FROM character_subclasses AS S1 WHERE S1.char_obj_id = C.obj_Id AND S1.isBase = '0' LIMIT 0,1) AS subclass1,
                (SELECT S2.class_id FROM character_subclasses AS S2 WHERE S2.char_obj_id = C.obj_Id AND S2.isBase = '0' LIMIT 1,1) AS subclass2,
                (SELECT S3.class_id FROM character_subclasses AS S3 WHERE S3.char_obj_id = C.obj_Id AND S3.isBase = '0' LIMIT 2,1) AS subclass3,
                CS.name AS clan_name,
                A.ally_name
            FROM characters AS C
            LEFT JOIN clan_data AS CLAN ON CLAN.clan_id = C.clanid
            LEFT JOIN clan_subpledges AS CS ON CS.clan_id = CLAN.clan_id
            LEFT JOIN ally_data AS A ON A.ally_id = CLAN.ally_id
            WHERE C.account_name = '{login}'
            LIMIT 7
        """
        try:
            return LineageDB().select(sql)
        except:
            return None

    @staticmethod
    @cache_lineage_result(timeout=300)
    def check_char(acc, cid):
        sql = f"SELECT * FROM characters WHERE obj_id = '{cid}' AND account_name = '{acc}' LIMIT 1"
        try:
            return LineageDB().select(sql)
        except:
            return None

    @staticmethod
    @cache_lineage_result(timeout=300)
    def check_name_exists(name):
        sql = f"SELECT * FROM characters WHERE char_name = '{name}' LIMIT 1"
        try:
            return LineageDB().select(sql)
        except:
            return None

    @staticmethod
    @cache_lineage_result(timeout=300)
    def change_nickname(acc, cid, name):
        try:
            sql = """
                UPDATE characters
                SET char_name = :name
                WHERE obj_id = :cid AND account_name = :acc
                LIMIT 1
            """
            params = {
                "name": name,
                "cid": cid,
                "acc": acc
            }
            return LineageDB().update(sql, params)
        except Exception as e:
            print(f"Erro ao trocar nickname: {e}")
            return None

    @staticmethod
    @cache_lineage_result(timeout=300)
    def change_sex(acc, cid, sex):
        try:
            sql = """
                UPDATE characters SET sex = :sex
                WHERE obj_Id = :cid AND account_name = :acc
                LIMIT 1
            """
            return LineageDB().update(sql, {"sex": sex, "cid": cid, "acc": acc})
        except Exception as e:
            print(f"Erro ao trocar sexo: {e}")
            return None

    @staticmethod
    @cache_lineage_result(timeout=300)
    def unstuck(acc, cid, x, y, z):
        try:
            sql = """
                UPDATE characters SET x = :x, y = :y, z = :z
                WHERE obj_id = :cid AND account_name = :acc
                LIMIT 1
            """
            return LineageDB().update(sql, {"x": x, "y": y, "z": z, "cid": cid, "acc": acc})
        except Exception as e:
            print(f"Erro ao desbugar personagem: {e}")
            return None

    @staticmethod
    @cache_lineage_result(timeout=300)
    def delete_skills(cid):
        try:
            sql = """
                DELETE FROM character_skills
                WHERE charId = :cid AND class_index = 0
            """
            return LineageDB().update(sql, {"cid": cid})
        except Exception as e:
            print(f"Erro ao deletar skills: {e}")
            return None

    @staticmethod
    @cache_lineage_result(timeout=300)
    def delete_skills_save(cid):
        try:
            sql = """
                DELETE FROM character_skills_save
                WHERE charId = :cid AND class_index = 0
            """
            return LineageDB().update(sql, {"cid": cid})
        except Exception as e:
            print(f"Erro ao deletar skills salvas: {e}")
            return None

    @staticmethod
    @cache_lineage_result(timeout=300)
    def delete_hennas(cid):
        try:
            sql = """
                DELETE FROM character_hennas
                WHERE charId = :cid AND class_index = 0
            """
            return LineageDB().update(sql, {"cid": cid})
        except Exception as e:
            print(f"Erro ao deletar hennas: {e}")
            return None

    @staticmethod
    @cache_lineage_result(timeout=300)
    def delete_shortcuts(cid):
        try:
            sql = """
                DELETE FROM character_shortcuts
                WHERE charId = :cid AND class_index = 0
            """
            return LineageDB().update(sql, {"cid": cid})
        except Exception as e:
            print(f"Erro ao deletar atalhos: {e}")
            return None

    @staticmethod
    @cache_lineage_result(timeout=300)
    def add_skills(new_skills_values):
        try:
            sql = f"INSERT INTO character_skills VALUES {new_skills_values}"
            return LineageDB().update(sql)
        except Exception as e:
            print(f"Erro ao adicionar novas skills: {e}")
            return None

    @staticmethod
    @cache_lineage_result(timeout=300)
    def update_class_in_olympiad(char_class, cid):
        try:
            sql = """
                UPDATE olympiad_nobles
                SET class_id = :class_id
                WHERE char_id = :cid
            """
            return LineageDB().update(sql, {"class_id": char_class, "cid": cid})
        except Exception as e:
            print(f"Erro ao atualizar classe no Olympiad: {e}")
            return None

    @staticmethod
    @cache_lineage_result
    def update_base_class(char_class, cid, lvl=78, exp=1511275834, race='NONE'):
        try:
            updates = [
                "base_class = :char_class",
                "face = 0",
                "hairStyle = 0",
                "hairColor = 0"
            ]
            params = {"char_class": char_class, "cid": cid}

            if lvl < 78:
                updates.append("level = 78")
            if exp < 1511275834:
                updates.append("exp = 1511275834")
            if race != 'NONE':
                updates.append("race = :race")
                params["race"] = race

            sql = f"""
                UPDATE characters
                SET {', '.join(updates)}
                WHERE charId = :cid
            """
            return LineageDB().update(sql, params)
        except Exception as e:
            print(f"Erro ao atualizar base class: {e}")
            return None

    @staticmethod
    @cache_lineage_result(timeout=300)
    def move_all_paperdoll(cid):
        try:
            sql = """
                UPDATE items
                SET loc = 'INVENTORY'
                WHERE owner_id = :cid AND loc = 'PAPERDOLL'
            """
            return LineageDB().update(sql, {"cid": cid})
        except Exception as e:
            print(f"Erro ao mover itens do paperdoll para o inventário: {e}")
            return None

    @staticmethod
    @cache_lineage_result(timeout=300)
    def check_has_class_in_sub(cid, classes):
        sql = f"SELECT * FROM character_subclasses WHERE charId = '{cid}' AND class_id IN ({classes}) LIMIT 1"
        try:
            return LineageDB().select(sql)
        except:
            return None
  

class LineageAccount:

    @staticmethod
    @cache_lineage_result(timeout=300)
    def check_login_exists(login):
        sql = f"SELECT * FROM accounts WHERE login = '{login}' LIMIT 1"
        result = LineageDB().select(sql)
        return result if result is not None else None

    @staticmethod
    @cache_lineage_result(timeout=300)
    def check_email_exists(email):
        sql = f"SELECT login, email FROM accounts WHERE email = '{email}'"
        result = LineageDB().select(sql)
        return result if result is not None else None

    @staticmethod
    @cache_lineage_result(timeout=300)
    def register(login, password, access_level, email):
        try:
            hashed = base64.b64encode(hashlib.sha1(password.encode()).digest()).decode()
            sql = """
                INSERT INTO accounts (login, password, accessLevel, email, created_time)
                VALUES (:login, :password, :access_level, :email, :created_time)
            """
            params = {
                "login": login,
                "password": hashed,
                "access_level": access_level,
                "email": email,
                "created_time": int(time.time())
            }
            LineageDB().insert(sql, params)
            return True
        except Exception as e:
            print(f"Erro ao registrar conta: {e}")
            return None

    @staticmethod
    @cache_lineage_result(timeout=300)
    def update_password(password, login):
        try:
            hashed = base64.b64encode(hashlib.sha1(password.encode()).digest()).decode()
            sql = """
                UPDATE accounts SET password = :password
                WHERE login = :login LIMIT 1
            """
            params = {
                "password": hashed,
                "login": login
            }
            LineageDB().update(sql, params)
            return True
        except Exception as e:
            print(f"Erro ao atualizar senha: {e}")
            return None

    @staticmethod
    @cache_lineage_result(timeout=300)
    def update_password_group(password, logins_list):
        if not logins_list:
            return None
        try:
            hashed = base64.b64encode(hashlib.sha1(password.encode()).digest()).decode()
            # Gerar placeholders únicos para os parâmetros
            placeholders = ", ".join([f":login_{i}" for i in range(len(logins_list))])
            sql = f"""
                UPDATE accounts SET password = :password
                WHERE login IN ({placeholders})
            """
            params = {f"login_{i}": login for i, login in enumerate(logins_list)}
            params["password"] = hashed
            LineageDB().update(sql, params)
            return True
        except Exception as e:
            print(f"Erro ao atualizar senhas em grupo: {e}")
            return None

    @staticmethod
    @cache_lineage_result(timeout=300)
    def update_access_level(access, login):
        try:
            sql = """
                UPDATE accounts SET accessLevel = :access
                WHERE login = :login LIMIT 1
            """
            params = {
                "access": access,
                "login": login
            }
            result = LineageDB().update(sql, params)
            return result if result is not None else None
        except Exception as e:
            print(f"Erro ao atualizar accessLevel: {e}")
            return None


class TransferFromWalletToChar:

    @staticmethod
    @cache_lineage_result(timeout=300)
    def find_char(account: str, char_name: str):
        query = "SELECT * FROM characters WHERE account_name = %s AND char_name = %s"
        result = LineageDB().select(query, (account, char_name))
        return result if result is not None else None

    @staticmethod
    @cache_lineage_result(timeout=300)
    def search_coin(char_name: str, coin_id: int):
        query = """
            SELECT i.* FROM items i
            JOIN characters c ON i.owner_id = c.obj_Id
            WHERE c.char_name = %s AND i.item_id = %s
        """
        result = LineageDB().select(query, (char_name, coin_id))
        return result if result is not None else None

    @staticmethod
    @cache_lineage_result(timeout=300)
    def insert_coin(char_name: str, coin_id: int, amount: int):
        db = LineageDB()

        # Verifica owner_id
        char_query = "SELECT obj_Id FROM characters WHERE char_name = %s"
        char = db.select(char_query, (char_name,))
        if char is None or not char:
            return None

        owner_id = char[0]["obj_Id"]

        # Verifica se o item já existe
        item_query = "SELECT object_id, count FROM items WHERE owner_id = %s AND item_id = %s"
        existing = db.select(item_query, (owner_id, coin_id))
        if existing is None:
            return None

        if existing:
            update_query = "UPDATE items SET count = count + %s WHERE object_id = %s"
            rows = db.update(update_query, (amount, existing[0]['object_id']))
            return rows > 0 if rows is not None else None
        else:
            insert_query = "INSERT INTO items (owner_id, item_id, count) VALUES (%s, %s, %s)"
            new_id = db.insert(insert_query, (owner_id, coin_id, amount))
            return new_id is not None if new_id is not None else None


class TransferFromCharToWallet:

    @staticmethod
    @cache_lineage_result(timeout=300)
    def find_char(account, char_id):
        query = """
            SELECT online, char_name FROM characters 
            WHERE account_name = %s AND charId = %s
        """
        result = LineageDB().select(query, (account, char_id))
        return result if result is not None else None

    @staticmethod
    @cache_lineage_result(timeout=300)
    def check_ingame_coin(coin_id, char_id):
        query = """
            SELECT count FROM items 
            WHERE owner_id = %s AND item_id = %s AND loc = 'INVENTORY'
        """
        result = LineageDB().select(query, (char_id, coin_id))
        return result if result is not None else None

    @staticmethod
    @cache_lineage_result(timeout=300)
    def remove_ingame_coin(coin_id, count, char_id):
        try:
            query = """
                UPDATE items 
                SET count = count - :count 
                WHERE owner_id = :char_id 
                AND item_id = :coin_id 
                AND loc = 'INVENTORY' 
                AND count >= :count
            """
            params = {"count": count, "char_id": char_id, "coin_id": coin_id}
            result = LineageDB().update(query, params)
            return result if result is not None else None
        except Exception as e:
            print(f"Erro ao remover coin do inventário: {e}")
            return None
