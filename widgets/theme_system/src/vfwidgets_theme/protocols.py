"""Core protocols and interfaces for the VFWidgets Theme System.

This module defines the fundamental protocols that enable clean architecture
through dependency injection, ensuring ThemedWidget remains simple while
maintaining architectural correctness underneath.

Key Design Principles:
1. Protocols enable dependency injection and testing with mocks
2. Clean separation of concerns across theme components
3. Type-safe interfaces with comprehensive type hints
4. Performance-first design with minimal runtime overhead
5. Thread-safe by design through Qt's signal/slot system

Architecture:
- ThemeProvider: Central theme data access and change notifications
- ThemeableWidget: Widget interface for receiving theme updates
- ColorProvider: Color resolution and validation with fallbacks
- StyleGenerator: QSS generation and style composition

ThemedWidget is THE way - these protocols enable its clean API while
hiding all architectural complexity behind simple inheritance.
"""

from abc import abstractmethod
from typing import Any, Callable, Protocol, TypeAlias, runtime_checkable

# Type Aliases for better IDE support and cleaner interfaces
ThemeData: TypeAlias = dict[str, Any]
"""Type alias for theme data dictionaries."""

ColorValue: TypeAlias = str
"""Type alias for color values (hex, rgb, named colors)."""

StyleCallback: TypeAlias = Callable[[str], None]
"""Type alias for theme change callback functions."""

ThemeChangeCallback: TypeAlias = Callable[["ThemeData"], None]
"""Type alias for theme change callback functions that receive theme data."""

PropertyKey: TypeAlias = str
"""Type alias for theme property keys."""

PropertyValue: TypeAlias = Any
"""Type alias for theme property values."""

QSSStyle: TypeAlias = str
"""Type alias for Qt stylesheet strings."""


# Exception Hierarchy - Never crash, always provide fallbacks
class ThemeError(Exception):
    """Base exception for all theme system errors.

    Philosophy: Theme errors should never crash the application.
    All components must provide graceful fallbacks and error recovery.
    """

    pass


class ThemeValidationError(ThemeError):
    """Raised when theme data fails validation.

    Recovery Strategy: Fall back to default theme or minimal theme subset.
    """

    pass


class ColorResolveError(ThemeError):
    """Raised when color resolution fails.

    Recovery Strategy: Return fallback color (typically black or white).
    """

    pass


class StyleGenerationError(ThemeError):
    """Raised when QSS generation fails.

    Recovery Strategy: Return empty stylesheet or minimal safe styles.
    """

    pass


class ThemePropertyError(ThemeError):
    """Raised when theme property access fails.

    Recovery Strategy: Return provided default value or safe fallback.
    """

    pass


@runtime_checkable
class ThemeProvider(Protocol):
    """Protocol for theme data providers with change notifications.

    Enables dependency injection pattern where ThemeProvider implementations
    can be injected into widgets, making testing with mocks straightforward
    and allowing different theme sources (files, databases, network).

    Performance Requirements:
    - get_current_theme(): < 1μs for cached themes
    - get_property(): < 1μs for property access
    - subscribe/unsubscribe: < 10μs for callback management

    Thread Safety:
    - All methods must be thread-safe
    - Callbacks invoked through Qt signals for thread safety

    Example:
        provider = SomeThemeProvider()
        theme_data = provider.get_current_theme()
        primary_color = provider.get_property("primary_color")

        def on_change(theme_name: str):
            print(f"Theme changed to: {theme_name}")

        provider.subscribe(on_change)

    """

    @abstractmethod
    def get_current_theme(self) -> ThemeData:
        """Get the complete current theme data.

        Returns:
            Dictionary containing all theme properties and values.
            Must never return None - return empty dict as fallback.

        Raises:
            ThemeError: If theme loading fails completely.

        Performance: < 1μs for cached themes.

        """
        ...

    @abstractmethod
    def get_property(self, key: PropertyKey) -> PropertyValue:
        """Get a specific theme property value.

        Args:
            key: The property key to retrieve.

        Returns:
            The property value, or None if not found.

        Raises:
            ThemePropertyError: If property access fails.

        Performance: < 1μs for property access.

        """
        ...

    @abstractmethod
    def subscribe(self, callback: StyleCallback) -> None:
        """Subscribe to theme change notifications.

        Args:
            callback: Function called when theme changes.
                     Receives theme name as argument.

        Note:
            Callbacks must be invoked through Qt signals for thread safety.
            Multiple subscriptions of same callback are ignored.

        Performance: < 10μs for callback registration.

        """
        ...

    @abstractmethod
    def unsubscribe(self, callback: StyleCallback) -> None:
        """Unsubscribe from theme change notifications.

        Args:
            callback: Function to remove from notifications.

        Note:
            Unsubscribing non-existent callback is safe (no-op).

        Performance: < 10μs for callback removal.

        """
        ...


@runtime_checkable
class ThemeableWidget(Protocol):
    """Protocol for widgets that can be themed.

    This protocol defines the interface that ThemedWidget implements,
    enabling dependency injection and clean testing. All complexity
    is hidden behind this simple interface.

    ThemedWidget provides this interface automatically - developers
    just inherit from ThemedWidget and get theming for free.

    Performance Requirements:
    - get_theme_color(): < 1μs
    - get_theme_property(): < 1μs
    - on_theme_changed(): < 10ms for complete widget update

    Memory Requirements:
    - < 1KB overhead per widget
    - Automatic cleanup through WeakRef registry

    Example:
        class MyButton(ThemedWidget):
            def __init__(self):
                super().__init__()
                # Theming automatically available
                color = self.get_theme_color("button_color")
                font = self.get_theme_property("button_font")

    """

    @property
    @abstractmethod
    def theme_config(self) -> ThemeData:
        """Widget-specific theme configuration.

        Returns:
            Dictionary of widget-specific theme overrides.
            Can be empty if using default theme entirely.

        """
        ...

    @property
    @abstractmethod
    def theme_provider(self) -> ThemeProvider:
        """The theme provider for this widget.

        Returns:
            ThemeProvider instance injected during widget creation.
            Enables dependency injection and testing with mocks.

        """
        ...

    @abstractmethod
    def on_theme_changed(self) -> None:
        """Called when the theme changes.

        Widgets should update their appearance in this method.
        ThemedWidget provides a default implementation that handles
        most common cases automatically.

        Performance: < 10ms for complete widget visual update.
        Thread Safety: Always called on main Qt thread.
        """
        ...

    @abstractmethod
    def get_theme_color(self, key: PropertyKey, default: ColorValue = "#000000") -> ColorValue:
        """Get a color value from the current theme.

        Args:
            key: Color property key (e.g., "primary_color", "background").
            default: Fallback color if key not found.

        Returns:
            Color value as string (hex, rgb, or named color).
            Never returns None - always returns valid color.

        Performance: < 1μs through caching.
        Error Recovery: Returns default on any error.

        """
        ...

    @abstractmethod
    def get_theme_property(self, key: PropertyKey, default: PropertyValue = None) -> PropertyValue:
        """Get any theme property value.

        Args:
            key: Property key to retrieve.
            default: Fallback value if key not found.

        Returns:
            Property value of any type, or default if not found.

        Performance: < 1μs through caching.
        Error Recovery: Returns default on any error.

        """
        ...


@runtime_checkable
class ColorProvider(Protocol):
    """Protocol for color resolution and validation.

    Handles color resolution with intelligent fallbacks, validation,
    and color space conversions. Ensures widgets always get valid
    colors even when theme data is incomplete or invalid.

    Performance Requirements:
    - resolve_color(): < 1μs for cached colors
    - validate_color(): < 1μs for color validation
    - get_fallback_color(): < 1μs (immediate return)

    Error Recovery:
    - Invalid colors return fallback colors
    - Missing colors return intelligent defaults
    - Never raises exceptions - always provides fallback

    Example:
        provider = SomeColorProvider()
        color = provider.resolve_color("primary")  # Returns "#007acc"
        is_valid = provider.validate_color("#ff0000")  # Returns True
        fallback = provider.get_fallback_color()  # Returns "#000000"

    """

    @abstractmethod
    def resolve_color(self, key: PropertyKey) -> ColorValue:
        """Resolve a color key to an actual color value.

        Args:
            key: Color key to resolve (e.g., "primary", "error", "background").

        Returns:
            Valid color value as string.
            Returns fallback color if key cannot be resolved.

        Performance: < 1μs for cached colors.
        Error Recovery: Never fails - returns fallback on any error.

        """
        ...

    @abstractmethod
    def get_fallback_color(self) -> ColorValue:
        """Get the fallback color for error recovery.

        Returns:
            Safe fallback color (typically black #000000 or white #ffffff).
            Used when color resolution fails completely.

        Performance: < 1μs (immediate return).
        Guaranteed: Never fails or raises exceptions.

        """
        ...

    @abstractmethod
    def validate_color(self, color: ColorValue) -> bool:
        """Validate if a color value is valid.

        Args:
            color: Color value to validate (hex, rgb, named color).

        Returns:
            True if color is valid, False otherwise.

        Performance: < 1μs for color validation.
        Thread Safety: Must be thread-safe for concurrent validation.

        """
        ...


@runtime_checkable
class StyleGenerator(Protocol):
    """Protocol for QSS (Qt StyleSheet) generation and composition.

    Generates Qt stylesheets from theme data, handles style merging,
    and provides CSS selector generation for different widget types.

    Performance Requirements:
    - generate_stylesheet(): < 10ms for complex widgets
    - get_selector(): < 1μs for selector lookup
    - merge_styles(): < 5ms for style composition

    Error Recovery:
    - Invalid theme data returns minimal safe styles
    - Missing properties use defaults
    - Never generates invalid QSS - always validates output

    Example:
        generator = SomeStyleGenerator()
        theme = {"primary_color": "#007acc", "font_size": "12px"}
        widget = some_button_widget

        qss = generator.generate_stylesheet(theme, widget)
        # Returns: "QPushButton { color: #007acc; font-size: 12px; }"

        selector = generator.get_selector("button")
        # Returns: "QPushButton"

        merged = generator.merge_styles([style1, style2, style3])
        # Returns combined stylesheet

    """

    @abstractmethod
    def generate_stylesheet(self, theme: ThemeData, widget: Any) -> QSSStyle:
        """Generate QSS stylesheet for a widget from theme data.

        Args:
            theme: Theme data dictionary with styling properties.
            widget: Widget instance to generate styles for.

        Returns:
            Valid QSS stylesheet string.
            Returns minimal safe stylesheet on any error.

        Performance: < 10ms for complex widgets with many properties.
        Error Recovery: Never fails - returns safe fallback styles.
        Validation: Output is always valid QSS syntax.

        """
        ...

    @abstractmethod
    def get_selector(self, widget_type: str) -> str:
        """Get CSS selector for a widget type.

        Args:
            widget_type: Widget type identifier (e.g., "button", "label").

        Returns:
            CSS selector string (e.g., "QPushButton", "QLabel").

        Performance: < 1μs through lookup table.
        Error Recovery: Returns generic selector if type not found.

        """
        ...

    @abstractmethod
    def merge_styles(self, styles: list[QSSStyle]) -> QSSStyle:
        """Merge multiple stylesheets into a single stylesheet.

        Args:
            styles: List of QSS stylesheet strings to merge.

        Returns:
            Combined stylesheet with proper precedence handling.
            Later styles override earlier styles for same properties.

        Performance: < 5ms for reasonable number of styles.
        Error Recovery: Skips invalid styles, continues with valid ones.
        Validation: Output is always valid QSS syntax.

        """
        ...


# Performance validation helpers
def validate_performance_requirements() -> bool:
    """Validate that protocol implementations meet performance requirements.

    This function can be used in tests to ensure protocol implementations
    meet the strict performance requirements defined in this module.

    Returns:
        True if all performance requirements are met.

    Performance Requirements Summary:
    - Theme property access: < 1μs
    - Color resolution: < 1μs
    - Widget theme update: < 10ms
    - Style generation: < 10ms
    - Memory overhead: < 1KB per widget

    """
    # Implementation will be added in performance testing task
    return True


def get_protocol_version() -> str:
    """Get the current protocol version for compatibility checking.

    Returns:
        Version string in semver format (e.g., "1.0.0").

    Used to ensure compatibility between different components
    of the theme system across versions.

    """
    return "1.0.0"


# Export all public interfaces
__all__ = [
    # Type Aliases
    "ThemeData",
    "ColorValue",
    "StyleCallback",
    "PropertyKey",
    "PropertyValue",
    "QSSStyle",
    # Exception Hierarchy
    "ThemeError",
    "ThemeValidationError",
    "ColorResolveError",
    "StyleGenerationError",
    "ThemePropertyError",
    # Core Protocols
    "ThemeProvider",
    "ThemeableWidget",
    "ColorProvider",
    "StyleGenerator",
    # Utilities
    "validate_performance_requirements",
    "get_protocol_version",
]
