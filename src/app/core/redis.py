"""Redis 客户端基础设施，提供同步 Redis 连接工厂。"""

from redis import Redis

from app.core.config import get_settings


def create_redis_client() -> Redis:
    """基于应用配置创建 Redis 客户端，响应统一解码为字符串。"""
    return Redis.from_url(get_settings().redis_url, decode_responses=True)


redis_client = create_redis_client()
