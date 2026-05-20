"""通用 Pydantic 数据模型，定义标准响应结构和分页模型。"""

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一 API 响应模型，所有接口响应应以此结构返回。"""

    code: str
    message: str
    data: T | None = None


class PageData(BaseModel, Generic[T]):
    """分页数据模型，用于列表类型接口的通用分页响应。"""

    items: list[T]
    page: int
    page_size: int
    total: int
