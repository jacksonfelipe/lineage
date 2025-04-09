import os
import pymysql
import threading
import time
from dotenv import load_dotenv
from typing import Any, Dict, Tuple, List, Optional


load_dotenv()


class LineageDB:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(LineageDB, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.connection = None
        self.cache: Dict[Tuple[str, Tuple[Any, ...]], Tuple[List[Dict], float]] = {}
        self.cache_ttl = 60  # segundos
        self.connect()
        self._initialized = True

    def connect(self):
        try:
            self.connection = pymysql.connect(
                host=os.getenv('LINEAGE_DB_HOST'),
                user=os.getenv('LINEAGE_DB_USER'),
                password=os.getenv('LINEAGE_DB_PASSWORD'),
                database=os.getenv('LINEAGE_DB_NAME'),
                port=int(os.getenv('LINEAGE_DB_PORT', 3306)),
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True
            )
            print("✅ Conexão com o banco Lineage estabelecida com sucesso!")
        except pymysql.MySQLError as e:
            print(f"❌ Falha ao conectar ao banco Lineage: {e}")
            self.connection = None

    def _ensure_connection(self):
        if self.connection is None or not self.connection.open:
            print("🔄 Reestabelecendo conexão com o banco...")
            self.connect()

    def _get_cache(self, query: str, params: Tuple) -> Optional[List[Dict]]:
        key = (query, params)
        result = self.cache.get(key)
        if result:
            data, timestamp = result
            if time.time() - timestamp < self.cache_ttl:
                print("⚡ Consulta retornada do cache")
                return data
            else:
                del self.cache[key]
        return None

    def _set_cache(self, query: str, params: Tuple, data: List[Dict]):
        self.cache[(query, params)] = (data, time.time())

    # --- SELECT com cache opcional ---
    def select(self, query: str, params: Tuple = (), use_cache: bool = False) -> List[Dict]:
        if use_cache:
            cached = self._get_cache(query, params)
            if cached is not None:
                return cached

        self._ensure_connection()
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchall()
                if use_cache:
                    self._set_cache(query, params, result)
                return result
        except pymysql.MySQLError as e:
            print(f"❌ Erro no SELECT: {e}")
            return []

    # --- INSERT que retorna lastrowid ---
    def insert(self, query: str, params: Tuple = ()) -> Optional[int]:
        self._ensure_connection()
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.lastrowid
        except pymysql.MySQLError as e:
            print(f"❌ Erro no INSERT: {e}")
            return None

    # --- UPDATE que retorna número de linhas afetadas ---
    def update(self, query: str, params: Tuple = ()) -> int:
        self._ensure_connection()
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.rowcount
        except pymysql.MySQLError as e:
            print(f"❌ Erro no UPDATE: {e}")
            return 0

    # --- DELETE que retorna número de linhas afetadas ---
    def delete(self, query: str, params: Tuple = ()) -> int:
        self._ensure_connection()
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.rowcount
        except pymysql.MySQLError as e:
            print(f"❌ Erro no DELETE: {e}")
            return 0

    # --- Execução genérica sem retorno (DDL por exemplo) ---
    def execute_raw(self, query: str, params: Tuple = ()) -> bool:
        self._ensure_connection()
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                return True
        except pymysql.MySQLError as e:
            print(f"❌ Erro ao executar comando: {e}")
            return False

    # --- Cache e conexão ---
    def clear_cache(self):
        self.cache.clear()

    def close(self):
        if self.connection and self.connection.open:
            self.connection.close()
            print("🔌 Conexão com o banco Lineage encerrada.")


# --- Exemplo de uso da classe LineageDB ---

# from lineage_db import LineageDB  # se estiver em outro arquivo

# Instanciar o banco
# db = LineageDB()

# SELECT com cache
# players = db.select("SELECT * FROM characters WHERE level > %s", (50,), use_cache=True)
# print(players)

# INSERT e obter ID inserido
# new_id = db.insert("INSERT INTO accounts (login, password) VALUES (%s, %s)", ("novo_user", "1234"))
# print(f"ID da nova conta: {new_id}")

# UPDATE e verificar quantas linhas foram alteradas
# rows = db.update("UPDATE characters SET level = level + 1 WHERE char_name = %s", ("Player1",))
# print(f"Linhas atualizadas: {rows}")

# DELETE e verificar quantas linhas foram removidas
# deleted = db.delete("DELETE FROM items WHERE item_id = %s", (12345,))
# print(f"Itens deletados: {deleted}")

# Executar comando genérico (sem retorno)
# sucesso = db.execute_raw("CREATE TABLE IF NOT EXISTS teste (id INT PRIMARY KEY)")
# print(f"Tabela criada? {'Sim' if sucesso else 'Não'}")

# Encerrar a conexão manualmente (opcional)
# db.close()
