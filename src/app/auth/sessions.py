"""Bearer opaque session token 服务和 Redis session store。"""

from __future__ import annotations

import hashlib
import json
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from redis import Redis

from app.core.config import Settings, get_settings
from app.core.redis import redis_client


@dataclass(frozen=True)
class SessionData:
    """Redis 中保存的最小 session 数据。"""

    user_id: UUID
    created_at: datetime


class SessionTokenService:
    """生成和摘要 opaque bearer token。"""

    def __init__(self, token_bytes: int) -> None:
        self._token_bytes = token_bytes

    def generate_token(self) -> str:
        """生成不可预测的 opaque session token。"""
        return secrets.token_urlsafe(self._token_bytes)

    def digest_token(self, token: str) -> str:
        """对 token 做 SHA-256 摘要，用于 Redis key，避免明文 token 落入 key 空间。"""
        return hashlib.sha256(token.encode("utf-8")).hexdigest()


class RedisSessionStore:
    """基于 Redis TTL 的 session 存储。"""

    def __init__(
        self,
        redis: Redis,
        token_service: SessionTokenService,
        ttl_seconds: int,
        key_prefix: str,
    ) -> None:
        self._redis = redis
        self._token_service = token_service
        self._ttl_seconds = ttl_seconds
        self._key_prefix = key_prefix

    def create_session(self, user_id: UUID) -> str:
        """创建 session，返回只发给客户端一次的 bearer token。"""
        token = self._token_service.generate_token()
        session = SessionData(user_id=user_id, created_at=datetime.now(UTC))
        self._redis.setex(
            self._key_for_token(token),
            self._ttl_seconds,
            json.dumps(
                {
                    "user_id": str(session.user_id),
                    "created_at": session.created_at.isoformat(),
                },
            ),
        )
        return token

    def get_session(self, token: str) -> SessionData | None:
        """读取 session；不存在、过期或内容非法时返回 None。"""
        raw_session = self._redis.get(self._key_for_token(token))
        if raw_session is None:
            return None
        if isinstance(raw_session, bytes):
            raw_session = raw_session.decode("utf-8")

        try:
            payload = json.loads(raw_session)
            return SessionData(
                user_id=UUID(payload["user_id"]),
                created_at=datetime.fromisoformat(payload["created_at"]),
            )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            return None

    def delete_session(self, token: str) -> None:
        """删除 session，用于 logout 退出登录。"""
        self._redis.delete(self._key_for_token(token))

    def _key_for_token(self, token: str) -> str:
        return f"{self._key_prefix}{self._token_service.digest_token(token)}"


def create_session_token_service(settings: Settings | None = None) -> SessionTokenService:
    """创建 session token 服务。"""
    resolved_settings = settings or get_settings()
    return SessionTokenService(token_bytes=resolved_settings.auth_session_token_bytes)


def create_redis_session_store(settings: Settings | None = None) -> RedisSessionStore:
    """创建 Redis session store。"""
    resolved_settings = settings or get_settings()
    return RedisSessionStore(
        redis=redis_client,
        token_service=create_session_token_service(resolved_settings),
        ttl_seconds=resolved_settings.auth_session_ttl_seconds,
        key_prefix=resolved_settings.auth_session_key_prefix,
    )


session_store = create_redis_session_store()
