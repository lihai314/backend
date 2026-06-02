"""Redis session store 测试。"""

from uuid import uuid4

from app.auth.sessions import RedisSessionStore, SessionTokenService


class FakeRedis:
    """测试用 Redis 替身，只实现 session store 需要的方法。"""

    def __init__(self) -> None:
        self.values: dict[str, str] = {}
        self.ttls: dict[str, int] = {}

    def setex(self, key: str, ttl: int, value: str) -> None:
        self.values[key] = value
        self.ttls[key] = ttl

    def get(self, key: str) -> str | None:
        return self.values.get(key)

    def delete(self, key: str) -> None:
        self.values.pop(key, None)
        self.ttls.pop(key, None)


def test_session_token_service_generates_opaque_token_and_digest() -> None:
    """验证 token 是 opaque 值，摘要稳定且不等于明文。"""
    service = SessionTokenService(token_bytes=16)

    token = service.generate_token()
    digest = service.digest_token(token)

    assert isinstance(token, str)
    assert len(token) > 16
    assert len(digest) == 64
    assert digest != token
    assert service.digest_token(token) == digest


def test_redis_session_store_creates_reads_and_deletes_session() -> None:
    """验证 Redis session store 写入 TTL、读取 user_id 并支持删除。"""
    fake_redis = FakeRedis()
    token_service = SessionTokenService(token_bytes=8)
    store = RedisSessionStore(
        redis=fake_redis,  # type: ignore[arg-type]
        token_service=token_service,
        ttl_seconds=3600,
        key_prefix="test:session:",
    )
    user_id = uuid4()

    token = store.create_session(user_id)
    key = f"test:session:{token_service.digest_token(token)}"
    session = store.get_session(token)

    assert key in fake_redis.values
    assert token not in key
    assert fake_redis.ttls[key] == 3600
    assert session is not None
    assert session.user_id == user_id

    store.delete_session(token)

    assert store.get_session(token) is None


def test_redis_session_store_returns_none_for_invalid_payload() -> None:
    """验证 Redis 中异常内容不会破坏认证流程。"""
    fake_redis = FakeRedis()
    token_service = SessionTokenService(token_bytes=8)
    store = RedisSessionStore(
        redis=fake_redis,  # type: ignore[arg-type]
        token_service=token_service,
        ttl_seconds=3600,
        key_prefix="test:session:",
    )
    token = "broken-token"
    fake_redis.values[f"test:session:{token_service.digest_token(token)}"] = "not-json"

    assert store.get_session(token) is None
