"""顶层 API 路由聚合，统一挂载所有子路由模块。"""

from fastapi import APIRouter

from app.api.health import router as health_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)
