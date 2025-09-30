"""
Logging infrastructure for VFWidgets Theme System.

Provides structured logging with performance tracking, debug modes,
and theme-specific formatting. All logging is designed to be
non-intrusive with minimal performance impact.

Philosophy:
- Logging should never affect application performance
- Debug information should be comprehensive but optional
- Performance logging helps identify bottlenecks
- Structured logs enable better monitoring and debugging

Performance Requirements:
- Log call overhead: < 10μs when logging disabled
- Structured logging: < 100μs per log entry
- Performance logging: < 50μs for measurements
- Thread-safe logging operations

Architecture:
- ThemeLogger: Structured logging with theme context
- Performance logging for slow operations
- Debug mode with detailed information
- Integration with standard Python logging
"""

import logging
import time
import threading
import sys
from typing import Any, Dict, Optional, Callable, Union
from datetime import datetime, timezone
from contextlib import contextmanager


class ThemeLogger:
    """Theme-specific logger with structured logging support.

    Provides structured logging with theme context, performance tracking,
    and debug modes. Integrates with standard Python logging while adding
    theme-specific functionality.

    Performance Requirements:
    - Log call: < 10μs when disabled
    - Structured log: < 100μs when enabled
    - Thread-safe operation

    Example:
        logger = ThemeLogger("widget_manager")
        logger.info("Theme applied", extra={
            "theme_name": "dark-mode",
            "widget_count": 5,
            "duration_ms": 45.2
        })
    """

    def __init__(self, component_name: str, debug: bool = False):
        self.component_name = component_name
        self.debug_enabled = debug
        self._lock = threading.RLock()

        # Create logger with theme-specific name
        self.logger = logging.getLogger(f"vftheme.{component_name}")

        # Configure logger if not already configured
        if not self.logger.handlers:
            self._configure_logger()

    def _configure_logger(self) -> None:
        """Configure the logger with appropriate formatting."""
        # Set level based on debug mode
        level = logging.DEBUG if self.debug_enabled else logging.INFO
        self.logger.setLevel(level)

        # Create formatter for structured logging
        formatter = ThemeLogFormatter()

        # Create handler if none exists
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        # Prevent propagation to root logger to avoid duplicate messages
        self.logger.propagate = False

    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log debug message with optional structured data.

        Args:
            message: Debug message.
            extra: Additional structured data.
        """
        if self.debug_enabled:
            self._log(logging.DEBUG, message, extra)

    def info(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log info message with optional structured data.

        Args:
            message: Info message.
            extra: Additional structured data.
        """
        self._log(logging.INFO, message, extra)

    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log warning message with optional structured data.

        Args:
            message: Warning message.
            extra: Additional structured data.
        """
        self._log(logging.WARNING, message, extra)

    def error(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log error message with optional structured data.

        Args:
            message: Error message.
            extra: Additional structured data.
        """
        self._log(logging.ERROR, message, extra)

    def _log(self, level: int, message: str, extra: Optional[Dict[str, Any]]) -> None:
        """Internal logging method with theme context.

        Args:
            level: Logging level.
            message: Log message.
            extra: Additional structured data.
        """
        if self.logger.isEnabledFor(level):
            # Add theme context to extra data
            log_extra = {
                "theme_component": self.component_name,
                "theme_timestamp": datetime.now(timezone.utc).isoformat(),
                "theme_thread_id": threading.get_ident(),
            }

            if extra:
                # Avoid overwriting standard LogRecord attributes
                for key, value in extra.items():
                    if key not in {'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename', 'module', 'lineno', 'funcName', 'created', 'msecs', 'relativeCreated', 'thread', 'threadName', 'processName', 'process', 'message'}:
                        log_extra[key] = value

            self.logger.log(level, message, extra=log_extra)

    @contextmanager
    def performance_context(self, operation: str):
        """Context manager for performance logging.

        Args:
            operation: Name of the operation being measured.

        Example:
            with logger.performance_context("theme_switch"):
                apply_theme_to_widgets()
        """
        start_time = time.perf_counter()
        try:
            yield
        finally:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000

            # Log if operation was slow
            if duration_ms > 50:  # Configurable threshold
                self.warning(f"Slow operation: {operation}", extra={
                    "operation": operation,
                    "duration_ms": duration_ms,
                    "performance_warning": True
                })
            elif self.debug_enabled:
                self.debug(f"Operation completed: {operation}", extra={
                    "operation": operation,
                    "duration_ms": duration_ms
                })

    def measure_time(self, operation: str) -> Callable:
        """Decorator for measuring function execution time.

        Args:
            operation: Name of the operation being measured.

        Example:
            @logger.measure_time("widget_creation")
            def create_themed_widget():
                pass
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                with self.performance_context(operation):
                    return func(*args, **kwargs)
            return wrapper
        return decorator


class ThemeLogFormatter(logging.Formatter):
    """Custom formatter for theme system logs.

    Provides structured formatting with theme-specific information
    and performance data visualization.
    """

    def __init__(self):
        # Base format with timestamp and level
        base_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        super().__init__(base_format, datefmt="%H:%M:%S")

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with theme-specific enhancements.

        Args:
            record: Log record to format.

        Returns:
            Formatted log string.
        """
        # Get base formatted message
        formatted = super().format(record)

        # Add structured data if present
        if hasattr(record, 'component'):
            component_info = f" [{record.component}]"
            formatted = formatted.replace(record.name, record.name + component_info)

        # Add performance information
        if hasattr(record, 'duration_ms'):
            duration = record.duration_ms
            if duration > 100:
                perf_indicator = f" ⚠️ {duration:.1f}ms"
            elif duration > 50:
                perf_indicator = f" ⏱️ {duration:.1f}ms"
            else:
                perf_indicator = f" {duration:.1f}ms"
            formatted += perf_indicator

        # Add operation context
        if hasattr(record, 'operation'):
            formatted += f" ({record.operation})"

        # Add theme context
        if hasattr(record, 'theme_name'):
            formatted += f" theme={record.theme_name}"

        return formatted


# Global logger registry
_logger_registry: Dict[str, ThemeLogger] = {}
_registry_lock = threading.Lock()


def create_theme_logger(component_name: str, debug: bool = False) -> ThemeLogger:
    """Create or get a theme logger for a component.

    Args:
        component_name: Name of the component (e.g., "widget_manager").
        debug: Whether to enable debug logging.

    Returns:
        ThemeLogger instance for the component.

    Performance: < 50μs for logger creation/retrieval.
    """
    with _registry_lock:
        logger_key = f"{component_name}:{debug}"

        if logger_key not in _logger_registry:
            _logger_registry[logger_key] = ThemeLogger(component_name, debug)

        return _logger_registry[logger_key]


def get_performance_logger() -> ThemeLogger:
    """Get the dedicated performance logger.

    Returns:
        ThemeLogger instance configured for performance monitoring.
    """
    return create_theme_logger("performance", debug=False)


def get_debug_logger(component_name: str) -> ThemeLogger:
    """Get a debug logger for a component.

    Args:
        component_name: Name of the component.

    Returns:
        ThemeLogger instance with debug logging enabled.
    """
    return create_theme_logger(component_name, debug=True)


# Convenience functions for common logging scenarios
def log_theme_error(logger: ThemeLogger, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """Log a theme error with structured context.

    Args:
        logger: Logger instance to use.
        error: Exception that occurred.
        context: Additional context about the error.
    """
    error_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
    }

    if context:
        error_data.update(context)

    # Add error-specific attributes if available
    if hasattr(error, 'theme_name'):
        error_data['theme_name'] = error.theme_name
    if hasattr(error, 'property_key'):
        error_data['property_key'] = error.property_key
    if hasattr(error, 'file_path'):
        error_data['file_path'] = error.file_path

    logger.error(f"Theme error: {type(error).__name__}", extra=error_data)


def log_performance_warning(message: str, duration_ms: float, operation: Optional[str] = None) -> None:
    """Log a performance warning for slow operations.

    Args:
        message: Warning message.
        duration_ms: Operation duration in milliseconds.
        operation: Optional operation name.
    """
    perf_logger = get_performance_logger()

    extra_data = {
        "duration_ms": duration_ms,
        "performance_warning": True
    }

    if operation:
        extra_data["operation"] = operation

    perf_logger.warning(message, extra=extra_data)


def log_theme_switch(theme_name: str, widget_count: int, duration_ms: float) -> None:
    """Log a theme switch operation.

    Args:
        theme_name: Name of the theme being switched to.
        widget_count: Number of widgets affected.
        duration_ms: Switch duration in milliseconds.
    """
    logger = create_theme_logger("theme_switch")

    logger.info(f"Theme switched to '{theme_name}'", extra={
        "theme_name": theme_name,
        "widget_count": widget_count,
        "duration_ms": duration_ms,
        "operation": "theme_switch"
    })


def log_widget_themed(widget_type: str, theme_properties: int, duration_ms: float) -> None:
    """Log widget theming operation.

    Args:
        widget_type: Type of widget themed.
        theme_properties: Number of theme properties applied.
        duration_ms: Theming duration in milliseconds.
    """
    logger = create_theme_logger("widget_theming")

    logger.debug(f"Widget themed: {widget_type}", extra={
        "widget_type": widget_type,
        "theme_properties": theme_properties,
        "duration_ms": duration_ms,
        "operation": "widget_theming"
    })


# Performance measurement utilities
class PerformanceTracker:
    """Performance tracking for theme operations.

    Provides detailed performance metrics for theme system operations
    with minimal overhead when not in use.

    Example:
        tracker = PerformanceTracker()
        with tracker.measure("theme_load"):
            load_theme_file()
        print(tracker.get_stats())
    """

    def __init__(self):
        self._measurements: Dict[str, list] = {}
        self._lock = threading.RLock()

    @contextmanager
    def measure(self, operation: str):
        """Measure operation duration.

        Args:
            operation: Name of the operation.
        """
        start_time = time.perf_counter()
        try:
            yield
        finally:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000

            with self._lock:
                if operation not in self._measurements:
                    self._measurements[operation] = []
                self._measurements[operation].append(duration_ms)

    def get_stats(self) -> Dict[str, Dict[str, float]]:
        """Get performance statistics.

        Returns:
            Dictionary with performance stats for each operation.
        """
        with self._lock:
            stats = {}
            for operation, measurements in self._measurements.items():
                if measurements:
                    stats[operation] = {
                        "count": len(measurements),
                        "avg_ms": sum(measurements) / len(measurements),
                        "min_ms": min(measurements),
                        "max_ms": max(measurements),
                        "total_ms": sum(measurements)
                    }
            return stats

    def reset(self) -> None:
        """Reset all measurements."""
        with self._lock:
            self._measurements.clear()


# Global performance tracker
_global_performance_tracker: Optional[PerformanceTracker] = None
_tracker_lock = threading.Lock()


def get_global_performance_tracker() -> PerformanceTracker:
    """Get the global performance tracker.

    Returns:
        Global PerformanceTracker instance (thread-safe singleton).
    """
    global _global_performance_tracker

    if _global_performance_tracker is None:
        with _tracker_lock:
            if _global_performance_tracker is None:
                _global_performance_tracker = PerformanceTracker()

    return _global_performance_tracker


def reset_logging_system() -> None:
    """Reset the logging system (for testing).

    Note:
        This clears all loggers and trackers. Use only for testing.
    """
    global _logger_registry, _global_performance_tracker

    with _registry_lock:
        _logger_registry.clear()

    with _tracker_lock:
        _global_performance_tracker = None


# Configure root theme logger
def configure_theme_logging(level: int = logging.INFO, format_string: Optional[str] = None) -> None:
    """Configure global theme logging settings.

    Args:
        level: Logging level for all theme loggers.
        format_string: Custom format string (optional).
    """
    root_logger = logging.getLogger("vftheme")
    root_logger.setLevel(level)

    # Clear existing handlers
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)

    # Add new handler with custom format
    handler = logging.StreamHandler(sys.stdout)
    if format_string:
        formatter = logging.Formatter(format_string)
    else:
        formatter = ThemeLogFormatter()

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    root_logger.propagate = False


# Export all public interfaces
__all__ = [
    # Core logging classes
    "ThemeLogger",
    "ThemeLogFormatter",

    # Logger creation functions
    "create_theme_logger",
    "get_performance_logger",
    "get_debug_logger",

    # Convenience logging functions
    "log_theme_error",
    "log_performance_warning",
    "log_theme_switch",
    "log_widget_themed",

    # Performance tracking
    "PerformanceTracker",
    "get_global_performance_tracker",

    # Configuration
    "configure_theme_logging",
    "reset_logging_system",
]