"""Centralized logging configuration for the entire project.

Call ``configure_logging()`` once at the entry point.
"""

import logging


def configure_logging(level: int = logging.INFO) -> None:
    """Configure root logger format and level.

    Args:
        level: Logging level (default: ``logging.INFO``).
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
