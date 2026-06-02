"""认证 API，提供注册、登录和退出登录。"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.dependencies import (
    get_bearer_token,
    get_current_user,
    get_password_hash_service,
    get_session_store,
)
from app.auth.password import PasswordHashService
from app.auth.sessions import RedisSessionStore
from app.core.error_codes import ErrorCode
from app.core.exceptions import ConflictException, UnauthorizedException
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginData, LoginRequest, RegisterRequest
from app.schemas.common import ApiResponse
from app.schemas.users import UserData

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=ApiResponse[UserData], status_code=201)
def register(
    payload: RegisterRequest,
    db: Annotated[Session, Depends(get_db)],
    password_service: Annotated[PasswordHashService, Depends(get_password_hash_service)],
) -> ApiResponse[UserData]:
    """注册用户；注册后不自动登录。"""
    existing_user = db.scalar(select(User).where(User.username == payload.username))
    if existing_user is not None:
        raise ConflictException("Username already exists")

    user = User(
        username=payload.username,
        password_hash=password_service.hash_password(payload.password),
        display_name=payload.display_name,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictException("Username already exists") from exc
    db.refresh(user)

    return ApiResponse(code=ErrorCode.OK, message="ok", data=UserData.model_validate(user))


@router.post("/login", response_model=ApiResponse[LoginData])
def login(
    payload: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
    password_service: Annotated[PasswordHashService, Depends(get_password_hash_service)],
    store: Annotated[RedisSessionStore, Depends(get_session_store)],
) -> ApiResponse[LoginData]:
    """使用 username + password 登录，返回 opaque bearer token。"""
    user = db.scalar(select(User).where(User.username == payload.username))
    if user is None or not user.is_active:
        raise UnauthorizedException("Invalid username or password")

    if not password_service.verify_password(payload.password, user.password_hash):
        raise UnauthorizedException("Invalid username or password")

    if password_service.needs_rehash(user.password_hash):
        user.password_hash = password_service.hash_password(payload.password)
        db.commit()

    token = store.create_session(user.id)

    return ApiResponse(code=ErrorCode.OK, message="ok", data=LoginData(access_token=token))


@router.post("/logout", response_model=ApiResponse[None])
def logout(
    token: Annotated[str, Depends(get_bearer_token)],
    current_user: Annotated[User, Depends(get_current_user)],
    store: Annotated[RedisSessionStore, Depends(get_session_store)],
) -> ApiResponse[None]:
    """退出当前登录 session，不删除账号。"""
    _ = current_user
    store.delete_session(token)
    return ApiResponse(code=ErrorCode.OK, message="ok", data=None)
