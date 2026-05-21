"""SQLAlchemy ORM 模型基类，所有数据库模型应继承此类。"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """声明式模型基类，所有数据库实体模型应直接或间接继承此类。"""

    pass
