"""
Extended exception hierarchy and error recovery system for VFWidgets Theme System.

This module provides comprehensive error handling that ensures applications
NEVER crash due to theme issues. All errors have appropriate fallbacks and
recovery mechanisms with performance < 1ms overhead.

Philosophy:
- Theme errors should be transparent to end users
- Applications should continue running even with corrupted themes
- Graceful degradation is preferred over complete failure
- All errors are logged for developers but don't disrupt user experience

Architecture:
- Extended exception hierarchy for specific error types
- ErrorRecoveryManager for centralized error handling
- Silent recovery with comprehensive logging
- User notification only for critical system issues

Performance Requirements:
- Error handling overhead: < 1ms
- Fallback resolution: < 100μs
- Zero memory leaks in error paths
- Thread-safe error handling
"""

import logging
import threading
import time
from typing import Any, Dict, Optional, Callable, Union
from weakref import WeakSet

# Import base ThemeError from protocols
from .protocols import ThemeError


# Extended Exception Hierarchy
class ThemeNotFoundError(ThemeError):
    """Raised when a requested theme doesn't exist.

    Recovery Strategy: Fall back to default theme or minimal theme.

    Example:
        try:
            theme = provider.load_theme("missing-theme")
        except ThemeNotFoundError:
            theme = get_fallback_theme()
    """

    def __init__(self, theme_name: str, message: Optional[str] = None):
        self.theme_name = theme_name
        if message is None:
            message = f"Theme '{theme_name}' not found"
        super().__init__(message)


class ThemeLoadError(ThemeError):
    """Raised when theme file is corrupted or cannot be loaded.

    Recovery Strategy: Fall back to minimal theme and log detailed error.

    Example:
        try:
            theme_data = json.load(theme_file)
        except (JSONDecodeError, IOError) as e:
            raise ThemeLoadError(f"Failed to load theme: {e}")
    """

    def __init__(self, message: str, file_path: Optional[str] = None, original_error: Optional[Exception] = None):
        self.file_path = file_path
        self.original_error = original_error
        super().__init__(message)


class PropertyNotFoundError(ThemeError):
    """Raised when theme property is missing.

    Recovery Strategy: Return provided default value or safe fallback.

    Example:
        try:
            color = theme["colors"]["primary"]
        except KeyError:
            raise PropertyNotFoundError("primary", "colors.primary")
    """

    def __init__(self, property_key: str, full_path: Optional[str] = None):
        self.property_key = property_key
        self.full_path = full_path or property_key
        message = f"Property '{self.full_path}' not found in theme"
        super().__init__(message)


class InvalidThemeFormatError(ThemeError):
    """Raised when theme data has invalid format or structure.

    Recovery Strategy: Fix invalid data and continue with partial theme.

    Example:
        if not isinstance(theme_data, dict):
            raise InvalidThemeFormatError("Theme data must be a dictionary")
    """

    def __init__(self, message: str, invalid_data: Optional[Any] = None):
        self.invalid_data = invalid_data
        super().__init__(message)


class ThemeSystemNotInitializedError(ThemeError):
    """Raised when using themes before system initialization.

    Recovery Strategy: Initialize with minimal configuration and continue.

    Example:
        if not self._initialized:
            raise ThemeSystemNotInitializedError()
    """

    def __init__(self, message: Optional[str] = None):
        if message is None:
            message = "Theme system not initialized. Call initialize_theme_system() first."
        super().__init__(message)


class ThemeApplicationError(ThemeError):
    """Raised when theme application to widgets fails.

    Recovery Strategy: Fall back to minimal theme and continue operation.

    Example:
        try:
            apply_theme_to_widget(widget, theme)
        except ThemeApplicationError:
            apply_minimal_theme_to_widget(widget)
    """

    def __init__(self, widget_type: str, theme_name: str, message: Optional[str] = None):
        self.widget_type = widget_type
        self.theme_name = theme_name
        super().__init__(message or f"Failed to apply theme '{theme_name}' to widget '{widget_type}'")


class ThemeValidationError(ThemeError):
    """Raised when theme validation fails.

    Recovery Strategy: Use theme with valid parts and defaults for invalid parts.

    Example:
        try:
            validate_theme(theme)
        except ThemeValidationError as e:
            theme = sanitize_theme(theme, e.validation_errors)
    """

    def __init__(self, theme_name: str, validation_errors: list, message: Optional[str] = None):
        self.theme_name = theme_name
        self.validation_errors = validation_errors
        super().__init__(message or f"Theme '{theme_name}' validation failed: {len(validation_errors)} errors")


class ThemeNotificationError(ThemeError):
    """Raised when theme change notification fails.

    Recovery Strategy: Continue with theme change, log notification failure.

    Example:
        try:
            notify_theme_change(theme)
        except ThemeNotificationError:
            log_warning("Theme notification failed, continuing...")
    """

    def __init__(self, notification_type: str, message: Optional[str] = None):
        self.notification_type = notification_type
        super().__init__(message or f"Theme notification failed: {notification_type}")


# Error Recovery Manager
class ErrorRecoveryManager:
    """Centralized error recovery and fallback management.

    Provides consistent error handling across the theme system with
    automatic fallbacks, logging, and graceful degradation.

    Performance Requirements:
    - recover_from_error(): < 1ms
    - apply_graceful_degradation(): < 5ms
    - Thread-safe operation
    - Zero memory leaks

    Example:
        recovery_manager = ErrorRecoveryManager()

        try:
            theme = load_theme("custom")
        except ThemeLoadError as e:
            theme = recovery_manager.recover_from_error(
                e, operation="load_theme"
            )
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._error_counts: Dict[str, int] = {}
        self._last_error_time: Dict[str, float] = {}
        self._notification_callbacks: WeakSet = WeakSet()

        # Import fallback functions (avoid circular imports)
        self._fallback_functions = None
        self._logger = None

    def _ensure_dependencies(self):
        """Lazy load dependencies to avoid circular imports."""
        if self._fallback_functions is None:
            from . import fallbacks
            from . import logging as theme_logging

            self._fallback_functions = {
                'get_fallback_theme': fallbacks.get_fallback_theme,
                'get_fallback_color': fallbacks.get_fallback_color,
                'get_fallback_property': fallbacks.get_fallback_property,
            }
            self._logger = theme_logging.create_theme_logger("error_recovery")

    def recover_from_error(
        self,
        error: ThemeError,
        operation: str,
        context: Optional[Dict[str, Any]] = None,
        fallback_data: Optional[Any] = None,
        notify_user: bool = False,
        log_error: bool = True
    ) -> Any:
        """Recover from a theme error with appropriate fallback.

        Args:
            error: The theme error that occurred.
            operation: The operation that failed (for logging).
            context: Additional context about the error.
            fallback_data: Custom fallback data to use.
            notify_user: Whether to notify user of critical error.
            log_error: Whether to log the error.

        Returns:
            Appropriate fallback value based on error type.

        Performance: < 1ms for error recovery.
        """
        self._ensure_dependencies()

        with self._lock:
            # Track error frequency
            error_key = f"{type(error).__name__}:{operation}"
            self._error_counts[error_key] = self._error_counts.get(error_key, 0) + 1
            self._last_error_time[error_key] = time.time()

            # Log error if requested
            if log_error and self._logger:
                self._log_error(error, operation, context)

            # Notify user for critical errors
            if notify_user and isinstance(error, ThemeSystemNotInitializedError):
                self._notify_critical_error(error, operation)

            # Return appropriate fallback based on error type
            return self._get_fallback_for_error(error, operation, context, fallback_data)

    def _get_fallback_for_error(
        self,
        error: ThemeError,
        operation: str,
        context: Optional[Dict[str, Any]],
        fallback_data: Optional[Any]
    ) -> Any:
        """Get appropriate fallback value for specific error type."""
        if fallback_data is not None:
            return fallback_data

        if isinstance(error, (ThemeNotFoundError, ThemeLoadError, ThemeSystemNotInitializedError)):
            # Return minimal theme for theme-level errors
            return self._fallback_functions['get_fallback_theme']()

        elif isinstance(error, PropertyNotFoundError):
            # Return fallback property value
            if context and 'property_key' in context:
                return self._fallback_functions['get_fallback_property'](
                    context['property_key']
                )
            return None

        elif isinstance(error, InvalidThemeFormatError):
            # Return corrected theme data
            return self.apply_graceful_degradation(
                getattr(error, 'invalid_data', {}), operation
            )

        else:
            # Generic fallback for unknown errors
            return self._fallback_functions['get_fallback_theme']()

    def apply_graceful_degradation(self, theme_data: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """Apply graceful degradation to partially invalid theme data.

        Args:
            theme_data: Theme data that may be partially invalid.
            operation: The operation being performed.

        Returns:
            Corrected theme data with fallbacks for invalid parts.

        Performance: < 5ms for theme validation and correction.
        """
        if not isinstance(theme_data, dict):
            return self._fallback_functions['get_fallback_theme']()

        corrected_theme = theme_data.copy()

        # Ensure required sections exist
        if 'colors' not in corrected_theme:
            corrected_theme['colors'] = {}

        if 'fonts' not in corrected_theme:
            corrected_theme['fonts'] = {}

        if 'spacing' not in corrected_theme:
            corrected_theme['spacing'] = {}

        # Validate and fix colors
        self._fix_colors(corrected_theme['colors'])

        # Validate and fix fonts
        self._fix_fonts(corrected_theme['fonts'])

        # Validate and fix spacing
        self._fix_spacing(corrected_theme['spacing'])

        return corrected_theme

    def _fix_colors(self, colors: Dict[str, Any]) -> None:
        """Fix invalid color values in place."""
        required_colors = ['primary', 'background', 'text', 'border']

        for color_key in required_colors:
            if color_key not in colors or not self._is_valid_color(colors[color_key]):
                colors[color_key] = self._fallback_functions['get_fallback_color'](color_key)

    def _fix_fonts(self, fonts: Dict[str, Any]) -> None:
        """Fix invalid font values in place."""
        if 'default' not in fonts or not isinstance(fonts['default'], str):
            fonts['default'] = "Arial, sans-serif"

        if 'size' not in fonts or not isinstance(fonts['size'], (int, str)):
            fonts['size'] = 12

    def _fix_spacing(self, spacing: Dict[str, Any]) -> None:
        """Fix invalid spacing values in place."""
        if 'default' not in spacing or not isinstance(spacing['default'], (int, float)):
            spacing['default'] = 8

    def _is_valid_color(self, color: Any) -> bool:
        """Check if color value is valid."""
        if not isinstance(color, str):
            return False

        # Check hex colors
        if color.startswith('#'):
            return len(color) in [4, 7] and all(c in '0123456789abcdefABCDEF' for c in color[1:])

        # Check rgb/rgba colors
        if color.startswith(('rgb(', 'rgba(')):
            return True  # Basic check - could be more thorough

        # Check named colors (basic list)
        named_colors = {'red', 'green', 'blue', 'black', 'white', 'gray', 'yellow', 'orange', 'purple'}
        return color.lower() in named_colors

    def _log_error(self, error: ThemeError, operation: str, context: Optional[Dict[str, Any]]) -> None:
        """Log error with structured information."""
        log_data = {
            'error_type': type(error).__name__,
            'operation': operation,
            'message': str(error),
            'context': context or {}
        }

        # Add error-specific data
        if hasattr(error, 'theme_name'):
            log_data['theme_name'] = error.theme_name
        if hasattr(error, 'property_key'):
            log_data['property_key'] = error.property_key
        if hasattr(error, 'file_path'):
            log_data['file_path'] = error.file_path

        self._logger.warning(f"Theme error recovered: {error}", extra=log_data)

    def _notify_critical_error(self, error: ThemeError, operation: str) -> None:
        """Notify user of critical error that affects functionality."""
        # Call registered notification callbacks
        for callback in list(self._notification_callbacks):
            try:
                callback(error, operation)
            except Exception:
                # Don't let notification failures affect error recovery
                pass

    def register_notification_callback(self, callback: Callable[[ThemeError, str], None]) -> None:
        """Register callback for critical error notifications.

        Args:
            callback: Function called for critical errors.
                     Receives (error, operation) as arguments.
        """
        self._notification_callbacks.add(callback)

    def get_error_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get error statistics for monitoring and debugging.

        Returns:
            Dictionary with error counts and timing information.
        """
        with self._lock:
            stats = {}
            for error_key, count in self._error_counts.items():
                error_type, operation = error_key.split(':', 1)
                stats[error_key] = {
                    'error_type': error_type,
                    'operation': operation,
                    'count': count,
                    'last_occurrence': self._last_error_time.get(error_key, 0)
                }
            return stats

    def reset_error_statistics(self) -> None:
        """Reset error statistics (useful for testing)."""
        with self._lock:
            self._error_counts.clear()
            self._last_error_time.clear()

    def handle_error(self, error: Exception, operation: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """Handle any error (not just ThemeError) with appropriate fallback.

        This method is called by ThemedApplication for generic error handling.

        Args:
            error: The error that occurred (any Exception type).
            operation: The operation that failed (for logging).
            context: Additional context about the error.

        Returns:
            Appropriate fallback value or re-raises if not a theme error.
        """
        if isinstance(error, ThemeError):
            # Use existing recovery mechanism for theme errors
            return self.recover_from_error(
                error, operation, context,
                notify_user=False, log_error=True
            )
        else:
            # For non-theme errors, log and re-raise
            self._ensure_dependencies()
            if self._logger:
                self._logger.error(f"Non-theme error in {operation}: {error}")
            raise error


# Global error recovery manager instance
_global_recovery_manager: Optional[ErrorRecoveryManager] = None
_recovery_lock = threading.Lock()


def create_error_recovery_manager() -> ErrorRecoveryManager:
    """Create a new error recovery manager instance.

    Returns:
        New ErrorRecoveryManager instance for handling theme errors.
    """
    return ErrorRecoveryManager()


def get_global_error_recovery_manager() -> ErrorRecoveryManager:
    """Get the global error recovery manager instance.

    Returns:
        Global ErrorRecoveryManager instance (created if needed).
        Thread-safe singleton access.
    """
    global _global_recovery_manager

    if _global_recovery_manager is None:
        with _recovery_lock:
            if _global_recovery_manager is None:
                _global_recovery_manager = ErrorRecoveryManager()

    return _global_recovery_manager


def reset_global_error_recovery_manager() -> None:
    """Reset the global error recovery manager (for testing)."""
    global _global_recovery_manager
    with _recovery_lock:
        _global_recovery_manager = None


# Convenience function for user notifications
def notify_user(error: ThemeError, operation: str) -> None:
    """Default user notification function for critical errors.

    Args:
        error: The critical error that occurred.
        operation: The operation that failed.

    Note:
        This is a placeholder implementation. Real applications should
        integrate with their UI notification system.
    """
    # In a real application, this would show a toast notification,
    # status bar message, or other appropriate UI feedback
    print(f"Theme System Warning: {type(error).__name__} in {operation}")


# Export all public interfaces
__all__ = [
    # Exception hierarchy
    "ThemeError",  # Re-export from protocols
    "ThemeNotFoundError",
    "ThemeLoadError",
    "PropertyNotFoundError",
    "InvalidThemeFormatError",
    "ThemeSystemNotInitializedError",

    # Error recovery
    "ErrorRecoveryManager",
    "create_error_recovery_manager",
    "get_global_error_recovery_manager",
    "reset_global_error_recovery_manager",

    # Utilities
    "notify_user",
]