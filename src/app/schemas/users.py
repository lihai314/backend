"""用户 API 请求与响应模型。"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserData(BaseModel):
    """对外返回的当前用户数据。"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    display_name: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UpdateProfileRequest(BaseModel):
    """更新当前用户资料，第一版只允许修改 display_name。"""

    model_config = ConfigDict(extra="forbid")

    display_name: str | None = Field(default=None, max_length=120)

    @field_validator("display_name")
    @classmethod
    def normalize_display_name(cls, value: str | None) -> str | None:
        """清理展示名空白，空字符串按未设置处理。"""
        if value is None:
            return None
        display_name = value.strip()
        return display_name or None


class ChangePasswordRequest(BaseModel):
    """修改密码请求。"""

    model_config = ConfigDict(extra="forbid")

    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)
