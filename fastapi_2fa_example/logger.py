from logging import Formatter, Logger, StreamHandler, getLogger

from fastapi_2fa_example.config import settings


def setup_logger() -> Logger:
    """Setup the logger configuration."""

    logger = getLogger("fastapi_2fa_example")
    log_level = settings.LOG_LEVEL.value
    logger.setLevel(log_level)

    handler = StreamHandler()
    handler.setFormatter(Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(handler)

    logger.debug(f"Logger initialized with level {log_level}")
    return logger


logger = setup_logger()
