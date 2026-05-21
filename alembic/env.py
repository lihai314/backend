"""Alembic 数据库迁移环境配置，负责管理连接、迁移上下文和执行策略。"""

from __future__ import annotations

import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# 将项目源码目录加入 sys.path，确保迁移脚本可导入项目模块
ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from app.core.config import get_settings  # noqa: E402
from app.db.base import Base  # noqa: E402

config = context.config

# 加载 Alembic 日志配置
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 迁移目标元数据来自 SQLAlchemy Base 模型
target_metadata = Base.metadata


# 从项目配置中获取数据库连接 URL
def get_database_url() -> str:
    """从应用配置读取数据库连接 URL。"""
    return get_settings().database_url


# 离线模式下执行迁移（无需数据库连接，仅生成 SQL 脚本）
def run_migrations_offline() -> None:
    """离线模式生成 SQL 迁移脚本片段，不连接数据库执行。"""
    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# 在线模式下执行迁移（直连数据库执行 DDL）
def run_migrations_online() -> None:
    """在线模式执行数据库迁移，直连数据库执行 DDL 操作。"""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_database_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
