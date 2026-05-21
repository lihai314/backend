import logging

from app.core.config import Settings
from app.core.logging import configure_logging


def test_settings_defines_default_log_level(monkeypatch: pytest.MonkeyPatch) -> None:
    """ 测试 settings 模块定义了默认的日志级别 """
    monkeypatch.delenv("LOG_LEVEL", raising=False)  
    settings = Settings()
    assert settings.log_level == "INFO"


def test_configure_logging_uses_standard_logging() -> None:
    """ 测试 configure_logging 函数使用了标准的日志配置 """
    root_logger = logging.getLogger()
    original_handlers = root_logger.handlers[:]
    original_level = root_logger.level

    try:
        configure_logging("DEBUG")

        assert root_logger.level == logging.DEBUG
        assert any(isinstance(handler, logging.StreamHandler) for handler in root_logger.handlers)
    finally:
        root_logger.handlers = original_handlers
        root_logger.setLevel(original_level)
