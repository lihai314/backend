"""日志配置模块，基于 dictConfig 实现结构化日志初始化。"""

import logging
from logging.config import dictConfig
from typing import Any

# 日志格式：时间 级别 [日志器名称] 消息
LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"


def configure_logging(log_level: str = "INFO") -> None:
    """配置标准日志系统，支持控制台输出与 uvicorn 日志器集成。"""
    level = log_level.upper()
    config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": LOG_FORMAT,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
        },
        "root": {
            "level": level,
            "handlers": ["console"],
        },
        "loggers": {
            "uvicorn": {
                "level": level,
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.error": {
                "level": level,
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": level,
                "handlers": ["console"],
                "propagate": False,
            },
        },
    }
    dictConfig(config)
    logging.getLogger(__name__).debug("Logging configured with level %s", level)
