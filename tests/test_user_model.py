"""用户 ORM 模型测试。"""

from app.models.user import User


def test_user_model_defines_expected_table_and_columns() -> None:
    """验证 users 表包含认证基础字段。"""
    table = User.__table__

    assert table.name == "users"
    assert set(table.columns.keys()) == {
        "id",
        "username",
        "password_hash",
        "display_name",
        "is_active",
        "created_at",
        "updated_at",
    }
    assert table.c.username.unique is True
    assert table.c.username.index is True
    assert table.c.username.nullable is False
    assert table.c.password_hash.nullable is False
    assert table.c.is_active.nullable is False
    assert table.c.is_active.server_default is not None
