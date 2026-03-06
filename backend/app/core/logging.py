"""Application logging configuration."""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

from app.core.mongodb_logger import MongoDBHandler

LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f"app_{datetime.now().strftime('%Y-%m-%d')}.log")

LOG_FORMAT = (
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s - "
    "[%(filename)s:%(lineno)d] - [%(process)d:%(thread)d]"
)

_current_log_level = LOG_LEVELS.get(os.getenv("LOG_LEVEL", "info"), logging.INFO)


def set_log_level(level: str) -> bool:
    global _current_log_level

    normalized = level.lower()
    if normalized not in LOG_LEVELS:
        return False

    _current_log_level = LOG_LEVELS[normalized]

    for name in logging.root.manager.loggerDict:
        logger_instance = logging.getLogger(name)
        if isinstance(logger_instance, logging.Logger):
            logger_instance.setLevel(_current_log_level)
            for handler in logger_instance.handlers:
                handler.setLevel(_current_log_level)

    return True


def get_log_level() -> str:
    for level_name, level_value in LOG_LEVELS.items():
        if level_value == _current_log_level:
            return level_name
    return "info"


def get_logger(name: str = "app") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(_current_log_level)

    if not logger.handlers:
        formatter = logging.Formatter(LOG_FORMAT)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(_current_log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        file_handler = RotatingFileHandler(LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=5)
        file_handler.setLevel(_current_log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        if not os.getenv("TESTING") and os.getenv("DISABLE_MONGO_LOGGING", "false").lower() != "true":
            try:
                mongodb_handler = MongoDBHandler()
                mongodb_handler.setLevel(logging.INFO)
                mongodb_handler.setFormatter(formatter)
                logger.addHandler(mongodb_handler)
            except Exception as exc:
                print(f"MongoDB logging disabled: {exc}")

    return logger


logger = get_logger()
