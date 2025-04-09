from apps.lineage.server.database import LineageDB
from apps.lineage.server.utils.cache import cache_lineage_result

import time
import base64
import hashlib
from apps.lineage.server.database import LineageDB


class LineageStats:

    @staticmethod
    @cache_lineage_result(timeout=300)
    def players_online():
        sql = "SELECT COUNT(*) AS quant FROM characters WHERE online > 0 AND accesslevel = '0'"
        return LineageDB().select(sql, use_cache=True)

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
        return LineageDB().select(sql, use_cache=True)

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
        return LineageDB().select(sql, use_cache=True)

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
        return LineageDB().select(sql, use_cache=True)

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
        return LineageDB().select(sql, use_cache=True)

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
        return LineageDB().select(sql, use_cache=True)


class LineageServices:

    @staticmethod
    @cache_lineage_result
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
        return LineageDB().select(sql)

    @staticmethod
    @cache_lineage_result
    def check_char(acc, cid):
        sql = f"SELECT * FROM characters WHERE obj_id = '{cid}' AND account_name = '{acc}' LIMIT 1"
        return LineageDB().select(sql)

    @staticmethod
    @cache_lineage_result
    def log_service(acc, cid, key, value, price):
        sql = f"""
            INSERT INTO site_log_services (log_account, log_cid, log_key, log_value, log_price, log_date)
            VALUES ('{acc}', '{cid}', '{key}', '{value}', '{price}', NOW())
        """
        return LineageDB().execute(sql)

    @staticmethod
    @cache_lineage_result
    def check_name_exists(name):
        sql = f"SELECT * FROM characters WHERE char_name = '{name}' LIMIT 1"
        return LineageDB().select(sql)

    @staticmethod
    @cache_lineage_result
    def change_nickname(acc, cid, name):
        sql = f"UPDATE characters SET char_name = '{name}' WHERE obj_id = '{cid}' AND account_name = '{acc}' LIMIT 1"
        return LineageDB().execute(sql)

    @staticmethod
    @cache_lineage_result
    def change_sex(acc, cid, sex):
        sql = f"UPDATE characters SET sex = '{sex}' WHERE obj_Id = '{cid}' AND account_name = '{acc}' LIMIT 1"
        return LineageDB().execute(sql)

    @staticmethod
    @cache_lineage_result
    def unstuck(acc, cid, x, y, z):
        sql = f"UPDATE characters SET x = '{x}', y = '{y}', z = '{z}' WHERE obj_id = '{cid}' AND account_name = '{acc}' LIMIT 1"
        return LineageDB().execute(sql)

    @staticmethod
    @cache_lineage_result
    def delete_skills(cid):
        sql = f"DELETE FROM character_skills WHERE charId = '{cid}' AND class_index = '0'"
        return LineageDB().execute(sql)

    @staticmethod
    @cache_lineage_result
    def delete_skills_save(cid):
        sql = f"DELETE FROM character_skills_save WHERE charId = '{cid}' AND class_index = '0'"
        return LineageDB().execute(sql)

    @staticmethod
    @cache_lineage_result
    def delete_hennas(cid):
        sql = f"DELETE FROM character_hennas WHERE charId = '{cid}' AND class_index = '0'"
        return LineageDB().execute(sql)

    @staticmethod
    @cache_lineage_result
    def delete_shortcuts(cid):
        sql = f"DELETE FROM character_shortcuts WHERE charId = '{cid}' AND class_index = '0'"
        return LineageDB().execute(sql)

    @staticmethod
    @cache_lineage_result
    def list_classes_skills(classes):
        sql = f"SELECT skill_id, MAX(level) AS level, nome FROM site_skills_classes WHERE class IN ({classes}) GROUP BY skill_id"
        return LineageDB().select(sql)

    @staticmethod
    @cache_lineage_result
    def add_skills(new_skills_values):
        sql = f"INSERT INTO character_skills VALUES {new_skills_values}"
        return LineageDB().execute(sql)

    @staticmethod
    @cache_lineage_result
    def update_class_in_olympiad(char_class, cid):
        sql = f"UPDATE olympiad_nobles SET class_id = '{char_class}' WHERE char_id = '{cid}'"
        return LineageDB().execute(sql)

    @staticmethod
    @cache_lineage_result
    def update_base_class(char_class, cid, lvl=78, exp=1511275834, race='NONE'):
        sql = f"""
            UPDATE characters SET
                base_class = '{char_class}',
                face = '0',
                hairStyle = '0',
                hairColor = '0'
                {" ,level = '78'" if lvl < 78 else ""}
                {" ,exp = '1511275834'" if exp < 1511275834 else ""}
                {" ,race = '" + race + "'" if race != 'NONE' else ""}
            WHERE charId = '{cid}'
        """
        return LineageDB().execute(sql)

    @staticmethod
    @cache_lineage_result
    def move_all_paperdoll(cid):
        sql = f"UPDATE items SET loc = 'INVENTORY' WHERE owner_id = '{cid}' AND loc = 'PAPERDOLL'"
        return LineageDB().execute(sql)

    @staticmethod
    @cache_lineage_result
    def check_has_class_in_sub(cid, classes):
        sql = f"SELECT * FROM character_subclasses WHERE charId = '{cid}' AND class_id IN ({classes}) LIMIT 1"
        return LineageDB().select(sql)


class LineageAccount:

    @staticmethod
    @cache_lineage_result
    def check_login_exists(login):
        sql = f"SELECT * FROM accounts WHERE login = '{login}' LIMIT 1"
        return LineageDB().select(sql)

    @staticmethod
    @cache_lineage_result
    def check_email_exists(email):
        sql = f"SELECT login, email FROM accounts WHERE email = '{email}'"
        return LineageDB().select(sql)

    @staticmethod
    @cache_lineage_result
    def register(login, password, access_level, email):
        hashed = base64.b64encode(hashlib.sha1(password.encode()).digest()).decode()
        sql = f"""
            INSERT INTO accounts (login, password, accessLevel, email, created_time)
            VALUES ('{login}', '{hashed}', '{access_level}', '{email}', '{int(time.time())}')
        """
        return LineageDB().execute(sql)

    @staticmethod
    @cache_lineage_result
    def update_password(password, login):
        hashed = base64.b64encode(hashlib.sha1(password.encode()).digest()).decode()
        sql = f"""
            UPDATE accounts SET password = '{hashed}'
            WHERE login = '{login}' LIMIT 1
        """
        return LineageDB().execute(sql)

    @staticmethod
    @cache_lineage_result
    def update_password_group(password, logins_list):
        if not logins_list:
            return False
        logins = ','.join([f"'{login}'" for login in logins_list])
        hashed = base64.b64encode(hashlib.sha1(password.encode()).digest()).decode()
        sql = f"""
            UPDATE accounts SET password = '{hashed}'
            WHERE login IN ({logins})
        """
        return LineageDB().execute(sql)

    @staticmethod
    @cache_lineage_result
    def update_access_level(access, login):
        sql = f"""
            UPDATE accounts SET accessLevel = '{access}'
            WHERE login = '{login}' LIMIT 1
        """
        return LineageDB().execute(sql)


class TransferFromWalletToChar:

    @staticmethod
    @cache_lineage_result
    def find_char(account: str, char_name: str):
        query = "SELECT * FROM characters WHERE account_name = %s AND char_name = %s"
        return LineageDB().select(query, (account, char_name))

    @staticmethod
    @cache_lineage_result
    def search_coin(char_name: str, coin_id: int):
        query = """
            SELECT i.* FROM items i
            JOIN characters c ON i.owner_id = c.obj_Id
            WHERE c.char_name = %s AND i.item_id = %s
        """
        return LineageDB().select(query, (char_name, coin_id))

    @staticmethod
    @cache_lineage_result
    def insert_coin(char_name: str, coin_id: int, amount: int):
        db = LineageDB()
        
        # Verifica owner_id
        char_query = "SELECT obj_Id FROM characters WHERE char_name = %s"
        char = db.select(char_query, (char_name,))
        if not char:
            return False

        owner_id = char[0]["obj_Id"]

        # Verifica se o item já existe
        item_query = "SELECT object_id, count FROM items WHERE owner_id = %s AND item_id = %s"
        existing = db.select(item_query, (owner_id, coin_id))

        if existing:
            update_query = "UPDATE items SET count = count + %s WHERE object_id = %s"
            rows = db.update(update_query, (amount, existing[0]['object_id']))
            return rows > 0
        else:
            insert_query = "INSERT INTO items (owner_id, item_id, count) VALUES (%s, %s, %s)"
            new_id = db.insert(insert_query, (owner_id, coin_id, amount))
            return new_id is not None


class TransferFromCharToWallet:

    @staticmethod
    @cache_lineage_result
    def find_char(account, char_id):
        query = """
            SELECT online, char_name FROM characters 
            WHERE account_name = %s AND charId = %s
        """
        return LineageDB.select(query, (account, char_id))

    @staticmethod
    @cache_lineage_result
    def check_ingame_coin(coin_id, char_id):
        query = """
            SELECT count FROM items 
            WHERE owner_id = %s AND item_id = %s AND loc = 'INVENTORY'
        """
        return LineageDB.select(query, (char_id, coin_id))

    @staticmethod
    @cache_lineage_result
    def remove_ingame_coin(coin_id, count, char_id):
        query = """
            UPDATE items 
            SET count = count - %s 
            WHERE owner_id = %s AND item_id = %s AND loc = 'INVENTORY' AND count >= %s
        """
        return LineageDB.execute(query, (count, char_id, coin_id, count))
