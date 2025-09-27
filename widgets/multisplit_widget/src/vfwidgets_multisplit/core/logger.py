"""Logging configuration for MultiSplit widget.

Provides detailed tracing of operations for debugging.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output."""

    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    BOLD = '\033[1m'

    def format(self, record):
        """Format log record with colors."""
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{self.BOLD}{levelname}{self.RESET}"

        # Add color to message based on level
        if levelname in self.COLORS:
            record.msg = f"{self.COLORS[levelname]}{record.msg}{self.RESET}"

        return super().format(record)


def setup_logging(
    level: str = "DEBUG",
    log_file: Optional[Path] = None,
    console: bool = True,
    detailed: bool = True
) -> logging.Logger:
    """Set up logging for MultiSplit widget.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file path for log output
        console: Whether to log to console
        detailed: Whether to include detailed format

    Returns:
        Configured logger
    """
    logger = logging.getLogger("multisplit")
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Detailed format for debugging
    if detailed:
        format_str = (
            "[%(asctime)s] %(levelname)-8s | %(name)s.%(funcName)s:%(lineno)d | "
            "%(message)s"
        )
        date_format = "%H:%M:%S.%f"[:-3]  # Include milliseconds
    else:
        format_str = "%(levelname)s: %(message)s"
        date_format = "%H:%M:%S"

    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)

        if sys.stdout.isatty():  # Use colors if terminal
            console_formatter = ColoredFormatter(format_str, datefmt=date_format)
        else:
            console_formatter = logging.Formatter(format_str, datefmt=date_format)

        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    # File handler
    if log_file:
        file_handler = logging.FileHandler(log_file, mode='a')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(format_str, datefmt=date_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


# Create default logger
logger = setup_logging(level="INFO", detailed=True)


def log_split_operation(target_pane_id, widget_id, position, ratio):
    """Log detailed split operation information."""
    logger.info("=" * 60)
    logger.info("SPLIT OPERATION STARTED")
    logger.info(f"  Target Pane: {target_pane_id}")
    logger.info(f"  New Widget: {widget_id}")
    logger.info(f"  Position: {position}")
    logger.info(f"  Ratio: {ratio}")
    logger.info("=" * 60)


def log_tree_structure(root, title="Tree Structure"):
    """Log the current tree structure."""
    from .nodes import LeafNode, SplitNode

    logger.debug(f"\n{title}:")
    logger.debug("-" * 40)

    def log_node(node, indent=0):
        prefix = "  " * indent
        if isinstance(node, LeafNode):
            logger.debug(f"{prefix}Leaf[{node.pane_id}]: widget={node.widget_id}")
        elif isinstance(node, SplitNode):
            logger.debug(f"{prefix}Split[{node.node_id}]: {node.orientation.value}, "
                        f"ratios={[f'{r:.2f}' for r in node.ratios]}")
            for child in node.children:
                log_node(child, indent + 1)

    if root:
        log_node(root)
    else:
        logger.debug("  (empty)")
    logger.debug("-" * 40)


def log_widget_creation(widget_id, pane_id, widget_type):
    """Log widget creation."""
    logger.info(f"WIDGET CREATED: {widget_type.__name__} for {widget_id} in pane {pane_id}")


def log_focus_change(old_id, new_id):
    """Log focus change."""
    logger.debug(f"Focus changed: {old_id} -> {new_id}")


def log_command_execution(command_desc, success):
    """Log command execution result."""
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"Command [{command_desc}]: {status}")


def log_validation_result(operation, result):
    """Log validation result."""
    if result.is_valid:
        logger.debug(f"Validation [{operation}]: PASSED")
    else:
        logger.warning(f"Validation [{operation}]: FAILED")
        for error in result.errors:
            logger.warning(f"  - {error}")
        for warning in result.warnings:
            logger.info(f"  ! {warning}")


def log_reconciliation(diff_result):
    """Log reconciliation differences."""
    if diff_result.has_changes():
        logger.debug("Reconciliation changes:")
        if diff_result.added:
            logger.debug(f"  Added: {diff_result.added}")
        if diff_result.removed:
            logger.debug(f"  Removed: {diff_result.removed}")
        if diff_result.modified:
            logger.debug(f"  Modified: {diff_result.modified}")
        if diff_result.moved:
            logger.debug(f"  Moved: {diff_result.moved}")
    else:
        logger.debug("Reconciliation: no changes")


class OperationTracer:
    """Context manager for tracing operations."""

    def __init__(self, operation_name: str, **kwargs):
        """Initialize tracer.

        Args:
            operation_name: Name of operation to trace
            **kwargs: Additional context to log
        """
        self.operation_name = operation_name
        self.context = kwargs
        self.start_time = None

    def __enter__(self):
        """Start tracing."""
        self.start_time = datetime.now()
        logger.debug(f">>> {self.operation_name} START")
        if self.context:
            for key, value in self.context.items():
                logger.debug(f"    {key}: {value}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End tracing."""
        duration = (datetime.now() - self.start_time).total_seconds() * 1000

        if exc_type:
            logger.error(f"<<< {self.operation_name} FAILED ({duration:.2f}ms)")
            logger.error(f"    Exception: {exc_type.__name__}: {exc_val}")
        else:
            logger.debug(f"<<< {self.operation_name} END ({duration:.2f}ms)")

        return False  # Don't suppress exceptions
