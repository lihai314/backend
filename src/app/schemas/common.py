from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    code: str
    message: str
    data: T | None = None


class PageData(BaseModel, Generic[T]):
    items: list[T]
    page: int
    page_size: int
    total: int
