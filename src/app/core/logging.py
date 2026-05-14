import logging
from logging.config import dictConfig
from typing import Any

LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"


def configure_logging(log_level: str = "INFO") -> None:
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
