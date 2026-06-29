import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(name: str = "CareerPilot") -> logging.Logger:
    """Sets up a rotating file logger and a console logger."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, log_level_str, logging.INFO)
    logger.setLevel(level)

    # Formatter for log messages
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Rotating File Handler (max 5MB, keeps 3 backups)
    log_file = "app.log"
    try:
        file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        # Fallback if file writing fails
        logger.warning(f"Could not create file logger: {e}")

    return logger

# Shared logger instance
logger = setup_logger()
