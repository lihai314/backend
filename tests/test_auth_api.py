"""认证 API 接口测试。"""

from collections.abc import Generator
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import pytest
from argon2 import PasswordHasher
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.dependencies import get_password_hash_service, get_session_store
from app.auth.password import PasswordHashService
from app.auth.sessions import SessionData
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import User


class FakeSessionStore:
    """测试用 session store。"""

    def __init__(self) -> None:
        self.sessions: dict[str, SessionData] = {}
        self.deleted_tokens: list[str] = []
        self._next_token = 1

    def create_session(self, user_id: UUID) -> str:
        token = f"token-{self._next_token}"
        self._next_token += 1
        self.sessions[token] = SessionData(user_id=user_id, created_at=datetime.now(UTC))
        return token

    def get_session(self, token: str) -> SessionData | None:
        return self.sessions.get(token)

    def delete_session(self, token: str) -> None:
        self.deleted_tokens.append(token)
        self.sessions.pop(token, None)


@pytest.fixture()
def password_service() -> PasswordHashService:
    """创建低成本密码哈希服务，降低接口测试耗时。"""
    hasher = PasswordHasher(time_cost=1, memory_cost=1024, parallelism=1)
    return PasswordHashService(hasher)


@pytest.fixture()
def session_store() -> FakeSessionStore:
    """创建测试 session store。"""
    return FakeSessionStore()


@pytest.fixture()
def db_session_factory() -> Generator[sessionmaker[Session], None, None]:
    """创建 SQLite 内存库会话工厂。"""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker[Session](autocommit=False, autoflush=False, bind=engine)

    try:
        yield factory
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture()
def client(
    db_session_factory: sessionmaker[Session],
    password_service: PasswordHashService,
    session_store: FakeSessionStore,
) -> Generator[TestClient, None, None]:
    """创建替换 DB、密码服务和 session store 的测试客户端。"""

    def override_get_db() -> Generator[Session, None, None]:
        db = db_session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_password_hash_service] = lambda: password_service
    app.dependency_overrides[get_session_store] = lambda: session_store

    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def register_user(client: TestClient, username: str = "alice") -> dict[str, Any]:
    """通过注册接口创建用户。"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "password": "correct-password",
            "display_name": "Alice",
        },
    )
    assert response.status_code == 201
    return response.json()


def login_user(
    client: TestClient, username: str = "alice", password: str = "correct-password"
) -> str:
    """通过登录接口获取 token。"""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200
    return str(response.json()["data"]["access_token"])


def auth_headers(token: str) -> dict[str, str]:
    """构造 Bearer 认证请求头。"""
    return {"Authorization": f"Bearer {token}"}


def test_register_creates_user_without_auto_login(
    client: TestClient,
    db_session_factory: sessionmaker[Session],
    password_service: PasswordHashService,
) -> None:
    """验证注册创建用户但不返回 token。"""
    body = register_user(client)

    assert body["code"] == "OK"
    assert body["message"] == "ok"
    assert body["data"]["username"] == "alice"
    assert body["data"]["display_name"] == "Alice"
    assert "access_token" not in body["data"]

    with db_session_factory() as db:
        user = db.scalar(select(User).where(User.username == "alice"))
        assert user is not None
        assert user.password_hash != "correct-password"
        assert password_service.verify_password("correct-password", user.password_hash) is True


def test_register_rejects_duplicate_username(client: TestClient) -> None:
    """验证重复 username 返回 409。"""
    register_user(client)

    response = client.post(
        "/api/v1/auth/register",
        json={"username": "alice", "password": "another-password"},
    )

    assert response.status_code == 409
    assert response.json()["code"] == "CONFLICT"


def test_register_rejects_email_like_username(client: TestClient) -> None:
    """验证第一版不接受 email 风格 username。"""
    response = client.post(
        "/api/v1/auth/register",
        json={"username": "alice@example.com", "password": "correct-password"},
    )

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"


def test_login_returns_bearer_token(
    client: TestClient,
    session_store: FakeSessionStore,
) -> None:
    """验证登录返回 opaque bearer token，并写入 session store。"""
    register_user(client)

    response = client.post(
        "/api/v1/auth/login",
        json={"username": "alice", "password": "correct-password"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"] == {"access_token": "token-1", "token_type": "bearer"}
    assert "token-1" in session_store.sessions


def test_login_rejects_invalid_password(client: TestClient) -> None:
    """验证密码错误返回 401。"""
    register_user(client)

    response = client.post(
        "/api/v1/auth/login",
        json={"username": "alice", "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHORIZED"


def test_logout_deletes_current_session(
    client: TestClient,
    session_store: FakeSessionStore,
) -> None:
    """验证 logout 只删除当前登录 session。"""
    register_user(client)
    token = login_user(client)

    response = client.post("/api/v1/auth/logout", headers=auth_headers(token))

    assert response.status_code == 200
    assert response.json() == {"code": "OK", "message": "ok", "data": None}
    assert token in session_store.deleted_tokens
    assert token not in session_store.sessions

    me_response = client.get("/api/v1/users/me", headers=auth_headers(token))
    assert me_response.status_code == 401


def test_get_me_returns_current_user(client: TestClient) -> None:
    """验证 users/me 返回当前登录用户。"""
    register_user(client)
    token = login_user(client)

    response = client.get("/api/v1/users/me", headers=auth_headers(token))

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["username"] == "alice"
    assert data["display_name"] == "Alice"


def test_get_me_requires_authentication(client: TestClient) -> None:
    """验证 users/me 未登录返回 401。"""
    response = client.get("/api/v1/users/me")

    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHORIZED"


def test_update_me_only_allows_display_name(client: TestClient) -> None:
    """验证当前用户资料只能修改 display_name。"""
    register_user(client)
    token = login_user(client)

    response = client.patch(
        "/api/v1/users/me",
        headers=auth_headers(token),
        json={"display_name": "Alice Updated"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["display_name"] == "Alice Updated"

    forbidden_response = client.patch(
        "/api/v1/users/me",
        headers=auth_headers(token),
        json={"username": "bob"},
    )
    assert forbidden_response.status_code == 422


def test_change_password_deletes_current_session_and_requires_relogin(
    client: TestClient,
    session_store: FakeSessionStore,
) -> None:
    """验证修改密码成功后删除当前 session，客户端需要重新登录。"""
    register_user(client)
    token = login_user(client)

    response = client.post(
        "/api/v1/users/me/actions/change-password",
        headers=auth_headers(token),
        json={
            "current_password": "correct-password",
            "new_password": "new-correct-password",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"code": "OK", "message": "ok", "data": None}
    assert token in session_store.deleted_tokens
    assert token not in session_store.sessions

    old_session_response = client.get("/api/v1/users/me", headers=auth_headers(token))
    assert old_session_response.status_code == 401

    old_password_response = client.post(
        "/api/v1/auth/login",
        json={"username": "alice", "password": "correct-password"},
    )
    assert old_password_response.status_code == 401

    new_token = login_user(client, password="new-correct-password")
    assert new_token == "token-2"


def test_change_password_rejects_invalid_current_password(client: TestClient) -> None:
    """验证当前密码错误时不能修改密码。"""
    register_user(client)
    token = login_user(client)

    response = client.post(
        "/api/v1/users/me/actions/change-password",
        headers=auth_headers(token),
        json={
            "current_password": "wrong-password",
            "new_password": "new-correct-password",
        },
    )

    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHORIZED"
