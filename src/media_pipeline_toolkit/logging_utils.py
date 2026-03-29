"""
Logging configuration and utilities.
"""
import logging
import sys


def setup_logging(level: int = logging.INFO) -> None:
    """
    Configures standard console logging for the toolkit.
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )


def get_logger(name: str) -> logging.Logger:
    """
    Returns a logger instance for the given module name.
    """
    return logging.getLogger(name)

