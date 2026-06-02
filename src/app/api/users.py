"""当前用户 API。"""

from typing import Annotated

from fastapi import APIRouter, Depends
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
from app.core.exceptions import UnauthorizedException
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.users import ChangePasswordRequest, UpdateProfileRequest, UserData

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=ApiResponse[UserData])
def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> ApiResponse[UserData]:
    """获取当前登录用户。"""
    return ApiResponse(code=ErrorCode.OK, message="ok", data=UserData.model_validate(current_user))


@router.patch("/me", response_model=ApiResponse[UserData])
def update_me(
    payload: UpdateProfileRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ApiResponse[UserData]:
    """更新当前用户资料；第一版只允许修改 display_name。"""
    current_user.display_name = payload.display_name
    db.commit()
    db.refresh(current_user)

    return ApiResponse(code=ErrorCode.OK, message="ok", data=UserData.model_validate(current_user))


@router.post("/me/actions/change-password", response_model=ApiResponse[None])
def change_password(
    payload: ChangePasswordRequest,
    token: Annotated[str, Depends(get_bearer_token)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    password_service: Annotated[PasswordHashService, Depends(get_password_hash_service)],
    store: Annotated[RedisSessionStore, Depends(get_session_store)],
) -> ApiResponse[None]:
    """修改当前用户密码；成功后删除当前 session，客户端需要重新登录。"""
    if not password_service.verify_password(payload.current_password, current_user.password_hash):
        raise UnauthorizedException("Invalid current password")

    current_user.password_hash = password_service.hash_password(payload.new_password)
    db.commit()
    store.delete_session(token)

    return ApiResponse(code=ErrorCode.OK, message="ok", data=None)
