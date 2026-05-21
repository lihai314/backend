"""健康检查 API，提供服务存活探针端点。"""

from fastapi import APIRouter
from pydantic import BaseModel

from app.schemas.common import ApiResponse

router = APIRouter(tags=["health"])


class HealthStatus(BaseModel):
    """健康检查响应数据结构。"""

    status: str


@router.get("/health", response_model=ApiResponse[HealthStatus])
def health() -> ApiResponse[HealthStatus]:
    """返回服务健康状态，供负载均衡器和容器编排系统进行存活检查。"""
    return ApiResponse(
        code="OK",
        message="ok",
        data=HealthStatus(status="healthy"),
    )
