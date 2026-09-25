"""Central logging configuration for the Crossmith engine.

The desktop UI tails ~/.crossmith/logs/engine.log for its live build-log
panel, so the log line format here is a stable contract, not just cosmetic.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

LOG_DIR = Path.home() / ".crossmith" / "logs"


def configure_logging(*, level: int = logging.INFO, log_to_file: bool = True) -> logging.Logger:
    """Configure and return the root 'crossmith' logger.

    Safe to call more than once — handlers are never duplicated, so every
    module can just call this and get the same configured logger back.
    """
    logger = logging.getLogger("crossmith")
    if logger.handlers:
        return logger

    logger.setLevel(level)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler(stream=sys.stdout)
    console.setFormatter(formatter)
    logger.addHandler(console)

    if log_to_file:
        try:
            LOG_DIR.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(LOG_DIR / "engine.log", encoding="utf-8")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except OSError:
            logger.warning("Could not open log file in %s, console-only logging", LOG_DIR)

    return logger
