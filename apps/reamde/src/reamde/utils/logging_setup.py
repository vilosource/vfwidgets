"""Logging configuration for Reamde application."""

import logging
import sys
from pathlib import Path


def setup_logging(level: int = logging.INFO) -> Path:
    """Configure application logging.

    Sets up two handlers:
    - File handler: Logs everything to ~/.config/reamde/reamde.log
    - Console handler: Only warnings and errors to stderr

    Args:
        level: Logging level for file handler (default: INFO)

    Returns:
        Path to log file

    Example:
        >>> log_file = setup_logging()
        >>> logger = logging.getLogger(__name__)
        >>> logger.info("Application started")
    """
    # Create log directory
    log_dir = Path.home() / ".config" / "reamde"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Log file path
    log_file = log_dir / "reamde.log"

    # Clear any existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(logging.DEBUG)

    # Format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File handler (everything)
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Console handler (warnings and errors only)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Log startup
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("Reamde logging initialized")
    logger.info(f"Log file: {log_file}")
    logger.info("=" * 60)

    return log_file


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Starting process")
    """
    return logging.getLogger(name)
