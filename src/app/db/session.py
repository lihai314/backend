"""数据库会话管理模块，提供引擎创建、会话工厂和依赖注入支持。"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

# 创建数据库引擎，pool_pre_ping 确保每次连接前验证连接有效性
engine = create_engine(get_settings().database_url, pool_pre_ping=True)
# 创建会话工厂，禁用自动提交和自动刷新以精确控制事务边界
SessionLocal = sessionmaker[Session](autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """获取数据库会话的依赖注入生成器，配合 FastAPI Depends 使用，自动管理会话生命周期。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
