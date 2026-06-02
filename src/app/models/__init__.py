"""ORM 模型聚合模块，供应用和 Alembic 显式加载全部模型。"""

from app.models.user import User

__all__ = ["User"]
