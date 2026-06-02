"""当前用户认证依赖，供后续 API 端点复用。"""

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth.sessions import RedisSessionStore, session_store
from app.core.exceptions import UnauthorizedException
from app.db.session import get_db
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


def get_session_store() -> RedisSessionStore:
    """提供 session store 依赖，方便测试覆盖。"""
    return session_store


def get_bearer_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> str:
    """从 Authorization: Bearer 中提取 token。"""
    if credentials is None or credentials.scheme.lower() != "bearer" or not credentials.credentials:
        raise UnauthorizedException("Missing bearer token")
    return credentials.credentials


def get_current_user(
    token: Annotated[str, Depends(get_bearer_token)],
    db: Annotated[Session, Depends(get_db)],
    store: Annotated[RedisSessionStore, Depends(get_session_store)],
) -> User:
    """根据 bearer token 加载当前用户，token 无效或用户不可用时返回 401。"""
    session = store.get_session(token)
    if session is None:
        raise UnauthorizedException("Invalid or expired session")

    user = db.get(User, session.user_id)
    if user is None or not user.is_active:
        raise UnauthorizedException("Invalid or expired session")

    return user
