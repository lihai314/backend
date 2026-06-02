"""当前用户认证依赖测试。"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from fastapi.security import HTTPAuthorizationCredentials

from app.auth.dependencies import get_bearer_token, get_current_user
from app.auth.sessions import SessionData
from app.core.exceptions import UnauthorizedException
from app.models.user import User


class FakeSessionStore:
    """测试用 session store。"""

    def __init__(self, session: SessionData | None) -> None:
        self.session = session

    def get_session(self, token: str) -> SessionData | None:
        return self.session


class FakeDb:
    """测试用数据库会话。"""

    def __init__(self, user: User | None) -> None:
        self.user = user
        self.last_lookup: tuple[type[User], UUID] | None = None

    def get(self, model: type[User], user_id: UUID) -> User | None:
        self.last_lookup = (model, user_id)
        return self.user


def test_get_bearer_token_requires_authorization_header() -> None:
    """验证缺少 Bearer token 时返回 401。"""
    with pytest.raises(UnauthorizedException):
        get_bearer_token(None)


def test_get_bearer_token_extracts_token() -> None:
    """验证能从 Bearer 凭证中提取 token。"""
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token-value")

    assert get_bearer_token(credentials) == "token-value"


def test_get_current_user_loads_active_user() -> None:
    """验证有效 session 能加载当前用户。"""
    user_id = uuid4()
    user = User(id=user_id, username="alice", password_hash="hash", is_active=True)
    db = FakeDb(user)
    store = FakeSessionStore(SessionData(user_id=user_id, created_at=datetime.now(UTC)))

    current_user = get_current_user("token-value", db, store)  # type: ignore[arg-type]

    assert current_user is user
    assert db.last_lookup == (User, user_id)


def test_get_current_user_rejects_missing_session() -> None:
    """验证 session 缺失或过期时返回 401。"""
    with pytest.raises(UnauthorizedException):
        get_current_user("token-value", FakeDb(None), FakeSessionStore(None))  # type: ignore[arg-type]


def test_get_current_user_rejects_inactive_user() -> None:
    """验证停用用户即使 session 存在也不能通过认证。"""
    user_id = uuid4()
    user = User(id=user_id, username="alice", password_hash="hash", is_active=False)
    store = FakeSessionStore(SessionData(user_id=user_id, created_at=datetime.now(UTC)))

    with pytest.raises(UnauthorizedException):
        get_current_user("token-value", FakeDb(user), store)  # type: ignore[arg-type]
