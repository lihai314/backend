"""应用配置模块，通过环境变量驱动配置加载，支持分层覆盖。"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置模型，所有可配置项通过环境变量或 .env 文件注入。"""

    app_name: str = "backend"
    environment: str = "local"
    log_level: str = "INFO"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/backend"
    redis_url: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """获取配置单例，使用 LRU 缓存保证全局唯一实例。"""
    return Settings()
