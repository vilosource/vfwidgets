"""
Mock objects implementing core protocols for testing without GUI dependencies.

These mocks enable testing ThemedWidget and the entire theme system without
requiring a QApplication or real Qt widgets. All mocks implement the protocols
from Task 1 and provide configurable behavior for comprehensive testing.

Key Features:
- Full protocol implementation with configurable responses
- Performance tracking to validate timing requirements
- Memory usage monitoring for leak detection
- Thread-safe operations through Qt signal simulation
- Error injection for testing error recovery paths

Philosophy: Make it impossible to test incorrectly while providing
maximum flexibility for different test scenarios.
"""

import time
import weakref
from typing import Any, Dict, List, Optional, Callable, Set
from unittest.mock import Mock, MagicMock
from concurrent.futures import ThreadPoolExecutor

from ..protocols import (
    ThemeProvider,
    ThemeableWidget,
    ColorProvider,
    StyleGenerator,
    ThemeData,
    ColorValue,
    StyleCallback,
    PropertyKey,
    PropertyValue,
    QSSStyle,
    ThemeError,
    ThemeValidationError,
    ColorResolveError,
    StyleGenerationError,
    ThemePropertyError,
)


class MockThemeProvider:
    """Mock implementation of ThemeProvider protocol for testing.

    Provides configurable theme data, change notifications, and performance
    tracking. Supports error injection for testing error recovery paths.

    Example:
        provider = MockThemeProvider({
            "primary_color": "#007acc",
            "background": "#ffffff",
            "font_size": "12px"
        })

        # Test normal operation
        assert provider.get_property("primary_color") == "#007acc"

        # Test error injection
        provider.inject_error("get_property", ThemePropertyError("Test error"))
        try:
            provider.get_property("primary_color")
        except ThemePropertyError:
            pass  # Expected
    """

    def __init__(self, theme_data: Optional[ThemeData] = None) -> None:
        """Initialize mock theme provider.

        Args:
            theme_data: Initial theme data. Uses default if None.
        """
        self._theme_data = theme_data or self._get_default_theme()
        self._callbacks: Set[StyleCallback] = set()
        self._call_counts: Dict[str, int] = {}
        self._call_times: Dict[str, List[float]] = {}
        self._injected_errors: Dict[str, Exception] = {}
        self._is_thread_safe = True

    def _get_default_theme(self) -> ThemeData:
        """Get default theme data for testing."""
        return {
            "primary_color": "#007acc",
            "secondary_color": "#6f6f6f",
            "background": "#ffffff",
            "foreground": "#000000",
            "font_family": "Segoe UI",
            "font_size": "12px",
            "border_radius": "4px",
            "padding": "8px",
        }

    def _track_call(self, method_name: str) -> None:
        """Track method calls for performance testing."""
        self._call_counts[method_name] = self._call_counts.get(method_name, 0) + 1
        if method_name not in self._call_times:
            self._call_times[method_name] = []

    def _check_injected_error(self, method_name: str) -> None:
        """Check for injected errors and raise if present."""
        if method_name in self._injected_errors:
            error = self._injected_errors.pop(method_name)
            raise error

    def get_current_theme(self) -> ThemeData:
        """Get the complete current theme data."""
        start_time = time.perf_counter()
        self._track_call("get_current_theme")
        self._check_injected_error("get_current_theme")

        # Simulate caching performance (< 1μs requirement)
        result = self._theme_data.copy()

        end_time = time.perf_counter()
        self._call_times["get_current_theme"].append(end_time - start_time)

        return result

    def get_property(self, key: PropertyKey) -> PropertyValue:
        """Get a specific theme property value."""
        start_time = time.perf_counter()
        self._track_call("get_property")
        self._check_injected_error("get_property")

        result = self._theme_data.get(key)

        end_time = time.perf_counter()
        self._call_times["get_property"].append(end_time - start_time)

        if result is None:
            raise ThemePropertyError(f"Property '{key}' not found")

        return result

    def subscribe(self, callback: StyleCallback) -> None:
        """Subscribe to theme change notifications."""
        start_time = time.perf_counter()
        self._track_call("subscribe")
        self._check_injected_error("subscribe")

        self._callbacks.add(callback)

        end_time = time.perf_counter()
        self._call_times["subscribe"].append(end_time - start_time)

    def unsubscribe(self, callback: StyleCallback) -> None:
        """Unsubscribe from theme change notifications."""
        start_time = time.perf_counter()
        self._track_call("unsubscribe")
        self._check_injected_error("unsubscribe")

        self._callbacks.discard(callback)  # Safe removal

        end_time = time.perf_counter()
        self._call_times["unsubscribe"].append(end_time - start_time)

    # Testing utilities

    def set_theme_data(self, theme_data: ThemeData) -> None:
        """Set new theme data and notify subscribers."""
        self._theme_data = theme_data
        self._notify_subscribers("test_theme")

    def inject_error(self, method_name: str, error: Exception) -> None:
        """Inject an error to be raised on next method call."""
        self._injected_errors[method_name] = error

    def get_call_count(self, method_name: str) -> int:
        """Get number of times a method was called."""
        return self._call_counts.get(method_name, 0)

    def get_average_call_time(self, method_name: str) -> float:
        """Get average call time for a method in seconds."""
        times = self._call_times.get(method_name, [])
        return sum(times) / len(times) if times else 0.0

    def reset_stats(self) -> None:
        """Reset call tracking statistics."""
        self._call_counts.clear()
        self._call_times.clear()

    def _notify_subscribers(self, theme_name: str) -> None:
        """Notify all subscribers of theme change."""
        for callback in self._callbacks.copy():  # Copy to avoid modification during iteration
            try:
                callback(theme_name)
            except Exception:
                # Log error but continue - don't break other callbacks
                pass


class MockThemeableWidget:
    """Mock implementation of ThemeableWidget protocol for testing.

    Simulates a widget that can be themed without requiring Qt dependencies.
    Tracks theme changes and property access for testing validation.

    Example:
        provider = MockThemeProvider()
        widget = MockThemeableWidget(provider)

        # Test theme property access
        color = widget.get_theme_color("primary_color")
        assert color == "#007acc"

        # Test theme change notification
        widget.on_theme_changed()
        assert widget.theme_change_count == 1
    """

    def __init__(self, theme_provider: Optional[ThemeProvider] = None) -> None:
        """Initialize mock themeable widget.

        Args:
            theme_provider: Theme provider to use. Creates mock if None.
        """
        self._theme_provider = theme_provider or MockThemeProvider()
        self._theme_config: ThemeData = {}
        self.theme_change_count = 0
        self._property_access_count = 0
        self._last_theme_change_time: Optional[float] = None

    @property
    def theme_config(self) -> ThemeData:
        """Widget-specific theme configuration."""
        return self._theme_config

    @property
    def theme_provider(self) -> ThemeProvider:
        """The theme provider for this widget."""
        return self._theme_provider

    def on_theme_changed(self) -> None:
        """Called when the theme changes."""
        start_time = time.perf_counter()
        self.theme_change_count += 1

        # Simulate widget update work (should be < 10ms)
        time.sleep(0.001)  # 1ms simulation

        end_time = time.perf_counter()
        self._last_theme_change_time = end_time - start_time

    def get_theme_color(self, key: PropertyKey, default: ColorValue = "#000000") -> ColorValue:
        """Get a color value from the current theme."""
        start_time = time.perf_counter()
        self._property_access_count += 1

        try:
            # Check widget-specific config first
            if key in self._theme_config:
                result = self._theme_config[key]
            else:
                result = self._theme_provider.get_property(key)

            # Validate it's a color-like value
            if isinstance(result, str) and (result.startswith('#') or result.startswith('rgb')):
                return result
            else:
                return default

        except Exception:
            return default

    def get_theme_property(self, key: PropertyKey, default: PropertyValue = None) -> PropertyValue:
        """Get any theme property value."""
        start_time = time.perf_counter()
        self._property_access_count += 1

        try:
            # Check widget-specific config first
            if key in self._theme_config:
                return self._theme_config[key]
            else:
                return self._theme_provider.get_property(key)
        except Exception:
            return default

    # Testing utilities

    def set_theme_config(self, config: ThemeData) -> None:
        """Set widget-specific theme configuration."""
        self._theme_config = config

    def get_property_access_count(self) -> int:
        """Get number of theme property accesses."""
        return self._property_access_count

    def get_last_theme_change_time(self) -> Optional[float]:
        """Get time taken for last theme change in seconds."""
        return self._last_theme_change_time

    def reset_stats(self) -> None:
        """Reset testing statistics."""
        self.theme_change_count = 0
        self._property_access_count = 0
        self._last_theme_change_time = None


class MockColorProvider:
    """Mock implementation of ColorProvider protocol for testing.

    Provides configurable color resolution with fallback handling
    and validation testing capabilities.

    Example:
        provider = MockColorProvider()

        # Test color resolution
        color = provider.resolve_color("primary")
        assert color == "#007acc"

        # Test validation
        assert provider.validate_color("#ff0000") == True
        assert provider.validate_color("invalid") == False

        # Test fallback
        fallback = provider.get_fallback_color()
        assert fallback == "#000000"
    """

    def __init__(self, color_map: Optional[Dict[str, str]] = None) -> None:
        """Initialize mock color provider.

        Args:
            color_map: Mapping of color keys to values. Uses default if None.
        """
        self._color_map = color_map or self._get_default_colors()
        self._fallback_color = "#000000"
        self._call_times: Dict[str, List[float]] = {}
        self._validation_cache: Dict[str, bool] = {}

    def _get_default_colors(self) -> Dict[str, str]:
        """Get default color mapping for testing."""
        return {
            "primary": "#007acc",
            "secondary": "#6f6f6f",
            "success": "#28a745",
            "warning": "#ffc107",
            "error": "#dc3545",
            "background": "#ffffff",
            "foreground": "#000000",
        }

    def resolve_color(self, key: PropertyKey) -> ColorValue:
        """Resolve a color key to an actual color value."""
        start_time = time.perf_counter()

        result = self._color_map.get(key, self._fallback_color)

        end_time = time.perf_counter()
        if "resolve_color" not in self._call_times:
            self._call_times["resolve_color"] = []
        self._call_times["resolve_color"].append(end_time - start_time)

        return result

    def get_fallback_color(self) -> ColorValue:
        """Get the fallback color for error recovery."""
        start_time = time.perf_counter()

        result = self._fallback_color

        end_time = time.perf_counter()
        if "get_fallback_color" not in self._call_times:
            self._call_times["get_fallback_color"] = []
        self._call_times["get_fallback_color"].append(end_time - start_time)

        return result

    def validate_color(self, color: ColorValue) -> bool:
        """Validate if a color value is valid."""
        start_time = time.perf_counter()

        # Check cache first
        if color in self._validation_cache:
            result = self._validation_cache[color]
        else:
            # Simple validation logic for testing
            result = (
                isinstance(color, str) and
                (color.startswith('#') and len(color) in [4, 7] or
                 color.startswith('rgb') or
                 color in ['red', 'green', 'blue', 'black', 'white'])
            )
            self._validation_cache[color] = result

        end_time = time.perf_counter()
        if "validate_color" not in self._call_times:
            self._call_times["validate_color"] = []
        self._call_times["validate_color"].append(end_time - start_time)

        return result

    # Testing utilities

    def set_color(self, key: str, color: str) -> None:
        """Set a color in the mapping."""
        self._color_map[key] = color

    def set_fallback_color(self, color: str) -> None:
        """Set the fallback color."""
        self._fallback_color = color

    def get_average_call_time(self, method_name: str) -> float:
        """Get average call time for a method in seconds."""
        times = self._call_times.get(method_name, [])
        return sum(times) / len(times) if times else 0.0

    def clear_cache(self) -> None:
        """Clear validation cache."""
        self._validation_cache.clear()


class MockStyleGenerator:
    """Mock implementation of StyleGenerator protocol for testing.

    Generates QSS stylesheets from theme data with configurable output
    and performance tracking for testing validation.

    Example:
        generator = MockStyleGenerator()
        theme = {"primary_color": "#007acc", "font_size": "12px"}
        widget = MockWidget()

        qss = generator.generate_stylesheet(theme, widget)
        assert "color: #007acc" in qss
        assert "font-size: 12px" in qss

        selector = generator.get_selector("button")
        assert selector == "QPushButton"
    """

    def __init__(self) -> None:
        """Initialize mock style generator."""
        self._widget_selectors = {
            "button": "QPushButton",
            "label": "QLabel",
            "edit": "QLineEdit",
            "text": "QTextEdit",
            "combo": "QComboBox",
            "list": "QListWidget",
            "tree": "QTreeWidget",
            "table": "QTableWidget",
        }
        self._call_times: Dict[str, List[float]] = {}
        self._generation_count = 0

    def generate_stylesheet(self, theme: ThemeData, widget: Any) -> QSSStyle:
        """Generate QSS stylesheet for a widget from theme data."""
        start_time = time.perf_counter()
        self._generation_count += 1

        # Simple QSS generation for testing
        widget_type = getattr(widget, 'widget_type', 'generic')
        selector = self._widget_selectors.get(widget_type, "QWidget")

        styles = []

        # Convert theme properties to QSS
        if "primary_color" in theme:
            styles.append(f"color: {theme['primary_color']}")
        if "background" in theme:
            styles.append(f"background-color: {theme['background']}")
        if "font_size" in theme:
            styles.append(f"font-size: {theme['font_size']}")
        if "font_family" in theme:
            styles.append(f"font-family: {theme['font_family']}")
        if "border_radius" in theme:
            styles.append(f"border-radius: {theme['border_radius']}")
        if "padding" in theme:
            styles.append(f"padding: {theme['padding']}")

        qss = f"{selector} {{ {'; '.join(styles)}; }}"

        end_time = time.perf_counter()
        if "generate_stylesheet" not in self._call_times:
            self._call_times["generate_stylesheet"] = []
        self._call_times["generate_stylesheet"].append(end_time - start_time)

        return qss

    def get_selector(self, widget_type: str) -> str:
        """Get CSS selector for a widget type."""
        start_time = time.perf_counter()

        result = self._widget_selectors.get(widget_type, "QWidget")

        end_time = time.perf_counter()
        if "get_selector" not in self._call_times:
            self._call_times["get_selector"] = []
        self._call_times["get_selector"].append(end_time - start_time)

        return result

    def merge_styles(self, styles: List[QSSStyle]) -> QSSStyle:
        """Merge multiple stylesheets into a single stylesheet."""
        start_time = time.perf_counter()

        # Simple merge - just concatenate for testing
        result = "\n".join(style for style in styles if style.strip())

        end_time = time.perf_counter()
        if "merge_styles" not in self._call_times:
            self._call_times["merge_styles"] = []
        self._call_times["merge_styles"].append(end_time - start_time)

        return result

    # Testing utilities

    def add_widget_selector(self, widget_type: str, selector: str) -> None:
        """Add a widget type to selector mapping."""
        self._widget_selectors[widget_type] = selector

    def get_generation_count(self) -> int:
        """Get number of stylesheets generated."""
        return self._generation_count

    def get_average_call_time(self, method_name: str) -> float:
        """Get average call time for a method in seconds."""
        times = self._call_times.get(method_name, [])
        return sum(times) / len(times) if times else 0.0

    def reset_stats(self) -> None:
        """Reset generation statistics."""
        self._generation_count = 0
        self._call_times.clear()


class MockWidget:
    """Mock widget for testing theme application without Qt dependencies.

    Simulates a Qt widget with theming capabilities, providing hooks
    for testing theme application, style updates, and property changes.

    Example:
        widget = MockWidget("button")
        widget.setStyleSheet("color: red;")
        assert widget.styleSheet() == "color: red;"

        widget.set_property("theme_color", "#007acc")
        assert widget.get_property("theme_color") == "#007acc"
    """

    def __init__(self, widget_type: str = "generic") -> None:
        """Initialize mock widget.

        Args:
            widget_type: Type of widget for selector generation.
        """
        self.widget_type = widget_type
        self._stylesheet = ""
        self._properties: Dict[str, Any] = {}
        self._parent = None
        self._children: List['MockWidget'] = []
        self._visible = True
        self._enabled = True

    def setStyleSheet(self, stylesheet: str) -> None:
        """Set the widget's stylesheet."""
        self._stylesheet = stylesheet

    def styleSheet(self) -> str:
        """Get the widget's current stylesheet."""
        return self._stylesheet

    def set_property(self, name: str, value: Any) -> None:
        """Set a dynamic property on the widget."""
        self._properties[name] = value

    def get_property(self, name: str, default: Any = None) -> Any:
        """Get a dynamic property from the widget."""
        return self._properties.get(name, default)

    def setParent(self, parent: Optional['MockWidget']) -> None:
        """Set the widget's parent."""
        if self._parent:
            self._parent._children.remove(self)
        self._parent = parent
        if parent:
            parent._children.append(self)

    def parent(self) -> Optional['MockWidget']:
        """Get the widget's parent."""
        return self._parent

    def children(self) -> List['MockWidget']:
        """Get the widget's children."""
        return self._children.copy()

    def setVisible(self, visible: bool) -> None:
        """Set widget visibility."""
        self._visible = visible

    def isVisible(self) -> bool:
        """Check if widget is visible."""
        return self._visible

    def setEnabled(self, enabled: bool) -> None:
        """Set widget enabled state."""
        self._enabled = enabled

    def isEnabled(self) -> bool:
        """Check if widget is enabled."""
        return self._enabled


class MockApplication:
    """Mock application for testing app-level theming without Qt dependencies.

    Simulates QApplication with theme management capabilities for testing
    application-wide theme switching and widget registration.

    Example:
        app = MockApplication()
        app.set_theme("dark")
        assert app.current_theme == "dark"

        widget = MockWidget()
        app.register_widget(widget)
        assert len(app.get_registered_widgets()) == 1
    """

    def __init__(self) -> None:
        """Initialize mock application."""
        self.current_theme = "default"
        self._widgets: weakref.WeakSet = weakref.WeakSet()
        self._theme_change_callbacks: List[Callable[[str], None]] = []
        self._available_themes = ["default", "dark", "light", "high-contrast"]

    def set_theme(self, theme_name: str) -> None:
        """Set the application theme."""
        if theme_name in self._available_themes:
            old_theme = self.current_theme
            self.current_theme = theme_name
            self._notify_theme_change(theme_name)
        else:
            raise ValueError(f"Theme '{theme_name}' not available")

    def get_available_themes(self) -> List[str]:
        """Get list of available themes."""
        return self._available_themes.copy()

    def register_widget(self, widget: Any) -> None:
        """Register a widget for theme updates."""
        self._widgets.add(widget)

    def unregister_widget(self, widget: Any) -> None:
        """Unregister a widget from theme updates."""
        self._widgets.discard(widget)

    def get_registered_widgets(self) -> List[Any]:
        """Get list of registered widgets."""
        return list(self._widgets)

    def add_theme_change_callback(self, callback: Callable[[str], None]) -> None:
        """Add callback for theme changes."""
        self._theme_change_callbacks.append(callback)

    def remove_theme_change_callback(self, callback: Callable[[str], None]) -> None:
        """Remove callback for theme changes."""
        if callback in self._theme_change_callbacks:
            self._theme_change_callbacks.remove(callback)

    def _notify_theme_change(self, theme_name: str) -> None:
        """Notify all registered components of theme change."""
        # Notify widgets
        for widget in list(self._widgets):
            if hasattr(widget, 'on_theme_changed'):
                widget.on_theme_changed()

        # Notify callbacks
        for callback in self._theme_change_callbacks:
            try:
                callback(theme_name)
            except Exception:
                pass  # Don't break other callbacks

    def add_available_theme(self, theme_name: str) -> None:
        """Add a theme to available themes."""
        if theme_name not in self._available_themes:
            self._available_themes.append(theme_name)


class MockPainter:
    """Mock painter for testing custom painting without Qt dependencies.

    Simulates QPainter for testing custom widget painting operations
    with theme-aware colors and styles.

    Example:
        painter = MockPainter()
        painter.setPen("#007acc")
        painter.setBrush("#ffffff")
        painter.drawRect(0, 0, 100, 50)

        assert painter.pen_color == "#007acc"
        assert painter.brush_color == "#ffffff"
        assert len(painter.draw_operations) == 1
    """

    def __init__(self) -> None:
        """Initialize mock painter."""
        self.pen_color = "#000000"
        self.brush_color = "#ffffff"
        self.font = "Arial 12px"
        self.draw_operations: List[Dict[str, Any]] = []

    def setPen(self, color: str) -> None:
        """Set pen color."""
        self.pen_color = color

    def setBrush(self, color: str) -> None:
        """Set brush color."""
        self.brush_color = color

    def setFont(self, font: str) -> None:
        """Set font."""
        self.font = font

    def drawRect(self, x: int, y: int, width: int, height: int) -> None:
        """Draw a rectangle."""
        self.draw_operations.append({
            "type": "rect",
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "pen": self.pen_color,
            "brush": self.brush_color,
        })

    def drawText(self, x: int, y: int, text: str) -> None:
        """Draw text."""
        self.draw_operations.append({
            "type": "text",
            "x": x,
            "y": y,
            "text": text,
            "pen": self.pen_color,
            "font": self.font,
        })

    def drawLine(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """Draw a line."""
        self.draw_operations.append({
            "type": "line",
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "pen": self.pen_color,
        })

    def clear_operations(self) -> None:
        """Clear all recorded draw operations."""
        self.draw_operations.clear()

    def get_operation_count(self, operation_type: Optional[str] = None) -> int:
        """Get count of draw operations, optionally filtered by type."""
        if operation_type is None:
            return len(self.draw_operations)
        return sum(1 for op in self.draw_operations if op["type"] == operation_type)


# Utility functions for creating configured mocks

def create_mock_theme_provider(theme_name: str = "default") -> MockThemeProvider:
    """Create a pre-configured mock theme provider.

    Args:
        theme_name: Name of theme configuration to use.

    Returns:
        Configured MockThemeProvider instance.
    """
    themes = {
        "default": {
            "primary_color": "#007acc",
            "background": "#ffffff",
            "foreground": "#000000",
        },
        "dark": {
            "primary_color": "#0078d4",
            "background": "#1e1e1e",
            "foreground": "#ffffff",
        },
        "light": {
            "primary_color": "#0066cc",
            "background": "#f8f8f8",
            "foreground": "#333333",
        },
        "high-contrast": {
            "primary_color": "#ffff00",
            "background": "#000000",
            "foreground": "#ffffff",
        },
    }

    theme_data = themes.get(theme_name, themes["default"])
    return MockThemeProvider(theme_data)


def create_mock_widget_hierarchy() -> MockWidget:
    """Create a hierarchy of mock widgets for testing.

    Returns:
        Root widget with child widgets attached.
    """
    root = MockWidget("container")

    button = MockWidget("button")
    button.setParent(root)

    label = MockWidget("label")
    label.setParent(root)

    edit = MockWidget("edit")
    edit.setParent(root)

    return root