"""密码哈希服务测试。"""

from argon2 import PasswordHasher

from app.auth.password import PasswordHashService


def create_fast_password_service() -> PasswordHashService:
    """创建低成本 Argon2id hasher，降低单元测试耗时。"""
    hasher = PasswordHasher(time_cost=1, memory_cost=1024, parallelism=1)
    return PasswordHashService(hasher)


def test_hash_password_uses_argon2id_and_verifies_password() -> None:
    """验证密码能生成 Argon2id 哈希并被正确校验。"""
    service = create_fast_password_service()

    password_hash = service.hash_password("correct horse battery staple")

    assert password_hash.startswith("$argon2id$")
    assert service.verify_password("correct horse battery staple", password_hash) is True
    assert service.verify_password("wrong password", password_hash) is False


def test_verify_password_treats_invalid_hash_as_failure() -> None:
    """验证非法哈希不会向外抛出底层异常。"""
    service = create_fast_password_service()

    assert service.verify_password("password", "not-a-valid-hash") is False
    assert service.needs_rehash("not-a-valid-hash") is True
