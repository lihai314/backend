"""数据库基础设施测试，验证 ORM 基类和会话依赖生命周期。"""

from collections.abc import Mapping
from typing import Any

from app.db import session as db_session
from app.db.base import Base


def test_base_exposes_sqlalchemy_metadata() -> None:
    """验证声明式基类暴露 SQLAlchemy metadata。"""
    assert Base.metadata is not None
    assert isinstance(Base.metadata.tables, Mapping)


def test_get_db_yields_session_and_closes_it(monkeypatch: Any) -> None:
    """验证 get_db 依赖会产出会话，并在结束时关闭会话。"""

    class FakeSession:
        closed = False

        def close(self) -> None:
            self.closed = True

    fake_session = FakeSession()

    monkeypatch.setattr(db_session, "SessionLocal", lambda: fake_session)

    generator = db_session.get_db()
    yielded = next(generator)

    assert yielded is fake_session

    try:
        next(generator)
    except StopIteration:
        pass

    assert fake_session.closed is True


def test_session_factory_is_bound_to_configured_engine() -> None:
    """验证 SessionLocal 绑定到模块级数据库引擎。"""
    assert db_session.SessionLocal.kw["bind"] is db_session.engine
    assert db_session.SessionLocal.kw["autocommit"] is False
    assert db_session.SessionLocal.kw["autoflush"] is False
