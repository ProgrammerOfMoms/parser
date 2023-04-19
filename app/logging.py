import logging
import logging.config
import os
from functools import wraps
from typing import Any, Callable

from app.config import settings


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(levelname)s %(asctime)s %(name)s %(message)s"
        }
    },
    "handlers": {
        "file": {
            "level": settings.LOG_LEVEL,
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, "logs/logs.log"),
            "mode": "w",
            "formatter": "simple"
        },
        "stdout": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "simple"
        }
    },
    "loggers": {
        "root": {
            "handlers": ["file", "stdout"],
            "level": "DEBUG" if settings.DEBUG else "WARNING",
            "propagate": False,
        },
        "sqlalchemy.engine": {
            "propagate": False,
            "handlers": ["file", "stdout"],
            "level": settings.LOG_LEVEL,
        }
    }
}


def setup_logger() -> None:
    """Установить конфиг логгирования."""
    logging.config.dictConfig(LOGGING)


def logged(func: Callable) -> Callable:
    """Декоратор для логгирования входящих и исходящих данных метода"""
    @wraps(func)
    def wrapper(*args: tuple, **kwargs: dict) -> Any:
        logger = logging.getLogger(func.__module__)
        logger.info(f"START METHOD {func.__name__} with args {args} and "
                    f"kwargs {kwargs}")
        try:
            result = func(*args, **kwargs)
        except Exception:
            logger.info(f"END METHOD {func.__name__}")
            raise
        else:
            logger.info(f"END METHOD {func.__name__}, result {result}")
        return result
    return wrapper
