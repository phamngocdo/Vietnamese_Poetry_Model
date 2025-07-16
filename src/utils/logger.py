import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

DEFAULT_LOG_PATH = os.getenv("LOG_PATH", "logs")
DEFAULT_LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

def setup_logger(name: str = "app_logger", log_path: str = DEFAULT_LOG_PATH, log_level: str = DEFAULT_LOG_LEVEL):
    """
    Sets up a logger with both console and rotating file handlers.

    Args:
        name (str): Name of the logger.
        log_path (str): Directory where log files will be stored.
        log_level (str): Logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL).

    Returns:
        logging.Logger: Configured logger instance.
    """
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    log_filename = os.path.join(log_path, f"{datetime.now().strftime('%Y-%m-%d')}.log")

    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    file_handler = RotatingFileHandler(log_filename, maxBytes=5 * 1024 * 1024, backupCount=5) # 5 MB per file, keep 5 backups
    file_handler.setLevel(log_level)

    formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - %(name)s - %(message)s")
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

logger = setup_logger()

def log_info(message: str):
    logger.info(message)

def log_warning(message: str):
    logger.warning(message)

def log_error(message: str):
    logger.error(message, exc_info=True)

def log_debug(message: str):
    logger.debug(message)