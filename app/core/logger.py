import os
import logging
from app.config import settings

LOG_DIR = getattr(settings, "LOG_DIR", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(getattr(settings, "LOG_LEVEL", "INFO"))

    # File handler
    fh = logging.FileHandler(os.path.join(LOG_DIR, f"{name}.log"))
    fh.setLevel(getattr(settings, "LOG_LEVEL", "INFO"))

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(getattr(settings, "LOG_LEVEL", "INFO"))

    fmt = getattr(settings, "LOG_FORMAT", "%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    formatter = logging.Formatter(fmt, "%Y-%m-%d %H:%M:%S")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger
