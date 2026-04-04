import logging
import os

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def get_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    request_handler = logging.FileHandler(os.path.join(LOG_DIR, "requests.log"), encoding="utf-8")
    request_handler.setLevel(logging.INFO)
    request_handler.setFormatter(formatter)

    error_handler = logging.FileHandler(os.path.join(LOG_DIR, "errors.log"), encoding="utf-8")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(request_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)

    return logger