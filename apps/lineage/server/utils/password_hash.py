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
                import whirlpool
                digest = whirlpool.new(password.encode()).digest()
            else:
                hasher = hashlib.new(self.name)
                hasher.update(password.encode())
                digest = hasher.digest()

            return base64.b64encode(digest).decode()
        except Exception as e:
            self.logger.error(f"{self.name}: encryption error!", exc_info=e)
            raise

    def compare(self, password: str, expected: str) -> bool:
        try:
            return self.encrypt(password).lower() == expected.lower()
        except Exception:
            return False
