"""认证 API 请求与响应模型。"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

USERNAME_PATTERN = r"^[A-Za-z0-9_.-]+$"


class RegisterRequest(BaseModel):
    """注册请求，第一版只接受 username + password。"""

    model_config = ConfigDict(extra="forbid")

    username: str = Field(min_length=3, max_length=64, pattern=USERNAME_PATTERN)
    password: str = Field(min_length=8, max_length=128)
    display_name: str | None = Field(default=None, max_length=120)

    @field_validator("username")
    @classmethod
    def reject_email_like_username(cls, value: str) -> str:
        """拒绝 email 风格 username，避免把 email 作为认证标识。"""
        username = value.strip()
        if "@" in username:
            raise ValueError("username must not be an email")
        return username

    @field_validator("display_name")
    @classmethod
    def normalize_display_name(cls, value: str | None) -> str | None:
        """清理展示名空白，空字符串按未设置处理。"""
        if value is None:
            return None
        display_name = value.strip()
        return display_name or None


class LoginRequest(BaseModel):
    """登录请求。"""

    model_config = ConfigDict(extra="forbid")

    username: str = Field(min_length=3, max_length=64, pattern=USERNAME_PATTERN)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        """清理 username 两端空白。"""
        return value.strip()


class LoginData(BaseModel):
    """登录成功响应数据。"""

    access_token: str
    token_type: Literal["bearer"] = "bearer"
