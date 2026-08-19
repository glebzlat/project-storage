import logging

from project_storage.core.config import settings


def setup_logging():
    log_levels = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "crit": logging.CRITICAL
    }

    log_level = log_levels[settings.LOG_LEVEL]

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s"
    )
