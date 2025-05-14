import hashlib
import base64
import logging

class PasswordHash:
    def __init__(self, name):
        self.name = name.lower()
        self.logger = logging.getLogger(__name__)

    def encrypt(self, password: str) -> str:
        try:
            if self.name == 'whirlpool':
                from utils.Whirlpool2000 import Whirlpool2000
                h = Whirlpool2000()
                h.update(password.encode())
                hash_b64 = base64.b64encode(h.digest()).decode()
            else:
                hasher = hashlib.new(self.name)
                hasher.update(password.encode())
                digest = hasher.digest()
                hash_b64 = base64.b64encode(digest).decode()

            return hash_b64
        except Exception as e:
            self.logger.error(f"{self.name}: encryption error!", exc_info=e)
            raise

    def compare(self, password: str, expected: str) -> bool:
        try:
            return self.encrypt(password).lower() == expected.lower()
        except Exception:
            return False
