"""认证配置测试。"""

from app.core.config import Settings


def test_auth_settings_define_session_defaults() -> None:
    """验证认证基础配置默认值。"""
    settings = Settings()

    assert settings.auth_session_ttl_seconds == 60 * 60 * 24 * 7
    assert settings.auth_session_key_prefix == "auth:session:"
    assert settings.auth_session_token_bytes == 32
