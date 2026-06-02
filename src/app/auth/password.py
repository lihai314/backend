"""密码哈希服务，使用 Argon2id 验证和生成密码哈希。"""

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError


class PasswordHashService:
    """封装密码哈希能力，避免业务层直接依赖第三方库细节。"""

    def __init__(self, hasher: PasswordHasher | None = None) -> None:
        self._hasher = hasher or PasswordHasher()

    def hash_password(self, password: str) -> str:
        """为明文密码生成 Argon2id 哈希。"""
        return self._hasher.hash(password)

    def verify_password(self, password: str, password_hash: str) -> bool:
        """验证明文密码是否匹配既有哈希，非法哈希统一视作验证失败。"""
        try:
            return self._hasher.verify(password_hash, password)
        except (InvalidHashError, VerificationError, VerifyMismatchError):
            return False

    def needs_rehash(self, password_hash: str) -> bool:
        """判断既有哈希是否需要按当前参数重新生成。"""
        try:
            return self._hasher.check_needs_rehash(password_hash)
        except InvalidHashError:
            return True


password_hash_service = PasswordHashService()
