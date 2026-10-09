import logging
import sys
from loguru import logger
from src.core.config import settings

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging() -> None:
    logger.remove()

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stdout,
        format=log_format,
        level=settings.LOG_LEVEL.upper(),
        colorize=True,
    )

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    for log_name in ("uvicorn", "uvicorn.error", "uvicorn.access", "sqlalchemy.engine"):
        std_logger = logging.getLogger(log_name)
        std_logger.handlers = [InterceptHandler()]
        std_logger.propagate = False


__all__ = ["logger", "setup_logging"]
