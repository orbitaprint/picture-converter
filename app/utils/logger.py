import logging
import os

from config import LOG_DIR, LOG_FILE


def setup_logger():
    if not os.path.isdir(LOG_DIR):
        os.makedirs(LOG_DIR)

    logger = logging.getLogger("picture_converter")
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger


LOGGER = setup_logger()
