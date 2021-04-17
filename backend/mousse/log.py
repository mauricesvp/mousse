"""
Mousse logging.

mauricesvp 2021
"""
import logging


def setup_logger(name: str) -> logging.Logger:
    """Set the logger up."""
    formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    )

    file_handler = logging.FileHandler(filename="mousse.log")
    stderr_handler = logging.StreamHandler()
    file_handler.setFormatter(formatter)
    stderr_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(stderr_handler)
    return logger
