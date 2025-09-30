"""
VFWidgets Theme System

A comprehensive, performance-first theme system for PySide6/Qt applications
built on clean architecture principles.

ThemedWidget is THE way to create themed widgets:
- Simple inheritance provides complete theming capabilities
- Automatic theme registration and memory management
- Thread-safe theme updates through Qt signals
- Zero configuration required for basic usage
- Extensible for advanced customization

Key Components:
- ThemedWidget: The main user-facing widget class (simple inheritance)
- ThemedApplication: Application-level theme management
- Theme protocols: Clean architecture through dependency injection
- Performance-first design: < 100ms theme switching, < 1KB per widget

Example:
    from vfwidgets_theme import ThemedWidget, ThemedApplication

    class MyButton(ThemedWidget):
        def __init__(self):
            super().__init__()
            # Theming automatically available
            self.setStyleSheet(self.get_theme_stylesheet())

    app = ThemedApplication()
    app.set_theme("dark")  # Instant theme switching

Architecture Philosophy:
"ThemedWidget provides clean architecture as THE way. Simple API,
correct implementation, no compromises."

All complexity is hidden behind ThemedWidget while maintaining
bulletproof architecture underneath through dependency injection,
protocols, and clean separation of concerns.
"""

# Import core protocols for advanced usage
from .protocols import (
    # Type aliases for better IDE support
    ThemeData,
    ColorValue,
    StyleCallback,
    PropertyKey,
    PropertyValue,
    QSSStyle,

    # Exception hierarchy for error handling
    ThemeError,
    ThemeValidationError,
    ColorResolveError,
    StyleGenerationError,
    ThemePropertyError,

    # Core protocols for dependency injection
    ThemeProvider,
    ThemeableWidget,
    ColorProvider,
    StyleGenerator,

    # Utility functions
    validate_performance_requirements,
    get_protocol_version,
)

# Import error handling and fallback system
from .errors import (
    # Extended exception hierarchy
    ThemeNotFoundError,
    ThemeLoadError,
    PropertyNotFoundError,
    InvalidThemeFormatError,
    ThemeSystemNotInitializedError,

    # Error recovery system
    ErrorRecoveryManager,
    create_error_recovery_manager,
    get_global_error_recovery_manager,
    notify_user,
)

from .fallbacks import (
    # Core fallback data
    MINIMAL_THEME,

    # Fallback color system
    FallbackColorSystem,
    create_fallback_color_system,
    get_global_fallback_color_system,

    # Convenience functions
    get_fallback_theme,
    get_fallback_color,
    get_fallback_property,
    validate_theme_completeness,
    get_safe_color_palette,
    is_valid_hex_color,
)

from .logging import (
    # Core logging classes
    ThemeLogger,
    create_theme_logger,
    get_performance_logger,
    get_debug_logger,

    # Convenience logging functions
    log_theme_error,
    log_performance_warning,
    log_theme_switch,
    log_widget_themed,

    # Performance tracking
    PerformanceTracker,
    get_global_performance_tracker,

    # Configuration
    configure_theme_logging,
)

# Version information
__version__ = "1.0.0-dev"
__author__ = "VFWidgets Team"
__description__ = "Performance-first theme system for PySide6/Qt applications"

# Primary user-facing imports - THE API
from .widgets import (
    ThemedWidget,
    ThemedApplication,
    create_themed_widget,
    get_themed_application,
    set_global_theme,
    get_global_theme,
    get_global_available_themes,
)

__all__ = [
    # ======================================
    # PRIMARY API - THE way to use theming
    # ======================================
    "ThemedWidget",           # THE way to create themed widgets
    "ThemedApplication",      # THE way to manage themes
    "create_themed_widget",   # Factory for themed widgets
    "create_themed_application",  # Factory for themed application
    "get_global_themed_application",  # Global application access
    "set_global_theme",       # Convenience function for global theming
    "get_global_theme",       # Get current global theme
    "get_global_available_themes",  # List available themes

    # ======================================
    # Version and metadata
    # ======================================
    "__version__",
    "__author__",
    "__description__",

    # ======================================
    # Advanced usage (protocols, errors, etc.)
    # ======================================
    # Type aliases
    "ThemeData",
    "ColorValue",
    "StyleCallback",
    "PropertyKey",
    "PropertyValue",
    "QSSStyle",

    # Exceptions from protocols
    "ThemeError",
    "ThemeValidationError",
    "ColorResolveError",
    "StyleGenerationError",
    "ThemePropertyError",

    # Extended exceptions from errors
    "ThemeNotFoundError",
    "ThemeLoadError",
    "PropertyNotFoundError",
    "InvalidThemeFormatError",
    "ThemeSystemNotInitializedError",

    # Protocols (for advanced usage)
    "ThemeProvider",
    "ThemeableWidget",
    "ColorProvider",
    "StyleGenerator",

    # Error recovery system
    "ErrorRecoveryManager",
    "create_error_recovery_manager",
    "get_global_error_recovery_manager",
    "notify_user",

    # Fallback system
    "MINIMAL_THEME",
    "FallbackColorSystem",
    "create_fallback_color_system",
    "get_global_fallback_color_system",
    "get_fallback_theme",
    "get_fallback_color",
    "get_fallback_property",
    "validate_theme_completeness",
    "get_safe_color_palette",
    "is_valid_hex_color",

    # Logging system
    "ThemeLogger",
    "create_theme_logger",
    "get_performance_logger",
    "get_debug_logger",
    "log_theme_error",
    "log_performance_warning",
    "log_theme_switch",
    "log_widget_themed",
    "PerformanceTracker",
    "get_global_performance_tracker",
    "configure_theme_logging",

    # Utilities
    "validate_performance_requirements",
    "get_protocol_version",
]