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

    def execute(self, query: str, params: Tuple = (), use_cache: bool = False) -> List[Dict]:
        if use_cache:
            cached = self._get_cache(query, params)
            if cached is not None:
                return cached

        if self.connection is None or not self.connection.open:
            print("🔄 Reestabelecendo conexão com o banco...")
            self.connect()

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchall()

                if use_cache:
                    self._set_cache(query, params, result)

                return result
        except pymysql.MySQLError as e:
            print(f"❌ Erro ao executar query: {e}")
            return []

    def clear_cache(self):
        self.cache.clear()

    def close(self):
        if self.connection and self.connection.open:
            self.connection.close()
            print("🔌 Conexão com o banco Lineage encerrada.")


# Exemplo de uso:
# db = LineageDB()
# resultado = db.execute("SELECT * FROM characters WHERE account_name = %s", ("Player1",), use_cache=True)
# print(resultado)
