import os
import time
import threading
from typing import Any, Dict, Tuple, List, Optional
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine import Engine, Result


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

        self.engine: Optional[Engine] = None
        self.cache: Dict[Tuple[str, Tuple[Any, ...]], Tuple[List[Dict], float]] = {}
        self.cache_ttl = 60  # segundos
        self._connect()
        self._initialized = True

    def _connect(self):
        try:
            user = os.getenv("LINEAGE_DB_USER")
            password = os.getenv("LINEAGE_DB_PASSWORD")
            host = os.getenv("LINEAGE_DB_HOST")
            port = os.getenv("LINEAGE_DB_PORT", "3306")
            dbname = os.getenv("LINEAGE_DB_NAME")

            url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}"
            self.engine = create_engine(url, echo=False, pool_pre_ping=True)
            print("✅ Conectado ao banco Lineage com SQLAlchemy")
        except Exception as e:
            print(f"❌ Falha ao conectar ao banco Lineage: {e}")
            self.engine = None

    def _get_cache(self, query: str, params: Tuple) -> Optional[List[Dict]]:
        key = (query, params)
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_ttl:
                print("⚡ Consulta retornada do cache")
                return data
            else:
                del self.cache[key]
        return None

    def _set_cache(self, query: str, params: Tuple, data: List[Dict]):
        self.cache[(query, params)] = (data, time.time())

    def _safe_execute(self, query: str, params: Dict[str, Any]) -> Optional[Result]:
        if not self.engine:
            print("⚠️ Sem conexão com o banco")
            return None
        try:
            with self.engine.connect() as conn:
                stmt = text(query)
                return conn.execute(stmt, params)
        except SQLAlchemyError as e:
            print(f"❌ Erro na execução: {e}")
            return None

    def select(self, query: str, params: Dict[str, Any] = {}, use_cache: bool = False) -> Optional[List[Dict]]:
        param_tuple = tuple(sorted(params.items()))
        if use_cache:
            cached = self._get_cache(query, param_tuple)
            if cached is not None:
                return cached

        result = self._safe_execute(query, params)
        if result is None:
            return None
        rows = result.mappings().all()
        if use_cache:
            self._set_cache(query, param_tuple, rows)
        return rows

    def insert(self, query: str, params: Dict[str, Any] = {}) -> Optional[int]:
        result = self._safe_execute(query, params)
        if result is None:
            return None
        return result.lastrowid

    def update(self, query: str, params: Dict[str, Any] = {}) -> Optional[int]:
        result = self._safe_execute(query, params)
        if result is None:
            return None
        return result.rowcount

    def delete(self, query: str, params: Dict[str, Any] = {}) -> Optional[int]:
        result = self._safe_execute(query, params)
        if result is None:
            return None
        return result.rowcount

    def execute_raw(self, query: str, params: Dict[str, Any] = {}) -> bool:
        result = self._safe_execute(query, params)
        return result is not None

    def clear_cache(self):
        self.cache.clear()
