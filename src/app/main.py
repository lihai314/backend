"""应用工厂模块，负责创建并配置 FastAPI 应用实例。"""

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exception_handlers import register_exception_handlers
from app.core.logging import configure_logging


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例，依次完成配置加载、日志初始化、异常处理器注册和路由挂载。"""
    settings = get_settings()
    configure_logging(settings.log_level)
    application = FastAPI(
        title="Backend API",
        description="Backend service API",
        version="0.1.0",
    )
    register_exception_handlers(application)
    application.include_router(api_router)
    return application


app = create_app()
