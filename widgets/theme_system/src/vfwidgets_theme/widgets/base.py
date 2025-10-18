"""ThemedWidget - The primary API for themed widgets.

This module contains ThemedWidget, the main user-facing class that provides
simple inheritance-based theming. This is THE way developers should create
themed widgets.

Key Classes:
- ThemedWidget: The primary API - simple inheritance provides complete theming
- ThemedWidgetMeta: Metaclass for processing theme configuration

Design Philosophy:
"ThemedWidget provides clean architecture as THE way. Simple API,
correct implementation, no compromises."

ThemedWidget must:
- Be simple to use (just inherit from it)
- Hide all architectural complexity
- Provide automatic theme registration
- Handle memory management transparently
- Work correctly in multi-threaded environments
- Never crash due to theming issues
- Provide excellent performance

Task 9 Implementation Features:
- Automatic widget registration with WeakRef cleanup
- Dynamic theme property access with caching
- Thread-safe operations using threading infrastructure
- Error recovery with graceful fallbacks
- Lifecycle management with proper cleanup
- Performance optimization meeting all requirements
"""

import threading
import uuid
import weakref
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Optional

try:
    from PySide6.QtCore import QObject, QTimer, Signal
    from PySide6.QtGui import QCloseEvent, QPalette
    from PySide6.QtWidgets import QWidget

    QT_AVAILABLE = True
except ImportError:
    # Fallback for testing without Qt
    QT_AVAILABLE = False

    class QWidget:
        def __init__(self, parent=None):
            self._parent = parent

        def parent(self):
            return self._parent

        def setStyleSheet(self, stylesheet):
            pass

        def setMinimumSize(self, width, height):
            pass

        def setWindowTitle(self, title):
            pass

        def show(self):
            pass

        def update(self):
            pass

        def closeEvent(self, event):
            pass

    class QObject:
        pass

    class Signal:
        def __init__(self, *args):
            self._callbacks = []

        def emit(self, *args):
            for callback in self._callbacks:
                callback(*args)

        def connect(self, callback):
            self._callbacks.append(callback)

    pyqtSignal = Signal

    class QTimer:
        def __init__(self):
            pass

    class QPalette:
        pass

    class QCloseEvent:
        pass


# Import foundation modules
from ..core.manager import ThemeManager
from ..core.theme import Theme
from ..core.token_types import TokenType
from ..errors import PropertyNotFoundError, ThemeError, get_global_error_recovery_manager
from ..lifecycle import LifecycleManager
from ..logging import get_debug_logger
from ..threading import ThreadSafeThemeManager

if TYPE_CHECKING:
    pass

logger = get_debug_logger(__name__)


@dataclass
class ThemePropertyDescriptor:
    """Descriptor for theme property access with caching."""

    property_path: str
    cache_key: Optional[str] = None
    default_value: Any = None
    _cache: dict[str, Any] = field(default_factory=dict)
    _lock: threading.RLock = field(default_factory=threading.RLock)

    def __set_name__(self, owner, name):
        """Set the cache key when descriptor is bound to class."""
        self.cache_key = f"{owner.__name__}.{name}"

    def __get__(self, obj, objtype=None):
        """Get property value with caching."""
        if obj is None:
            return self

        with self._lock:
            # Check cache first
            cache_key = f"{id(obj)}.{self.property_path}"
            if cache_key in self._cache:
                return self._cache[cache_key]

            try:
                # Get value from theme system
                value = obj._get_theme_property(self.property_path, self.default_value)

                # Cache the value
                self._cache[cache_key] = value
                return value

            except Exception as e:
                logger.error(f"Error getting theme property {self.property_path}: {e}")
                return self.default_value

    def __set__(self, obj, value):
        """Set property value and invalidate cache."""
        with self._lock:
            try:
                # Set the value
                obj._set_theme_property(self.property_path, value)

                # Invalidate cache
                cache_key = f"{id(obj)}.{self.property_path}"
                if cache_key in self._cache:
                    del self._cache[cache_key]

            except Exception as e:
                logger.error(f"Error setting theme property {self.property_path}: {e}")

    def invalidate_cache(self, obj):
        """Invalidate cache for specific object."""
        with self._lock:
            cache_key = f"{id(obj)}.{self.property_path}"
            if cache_key in self._cache:
                del self._cache[cache_key]


class ThemePropertiesManager:
    """Manager for theme property access with caching and performance optimization."""

    def __init__(self, widget: "ThemedWidget"):
        self._widget = weakref.ref(widget)
        self._cache: dict[str, Any] = {}
        self._lock = threading.RLock()
        self._cache_hits = 0
        self._cache_misses = 0

    @property
    def cache_hit_rate(self) -> float:
        """Get cache hit rate for performance monitoring."""
        total = self._cache_hits + self._cache_misses
        return self._cache_hits / total if total > 0 else 0.0

    def get_property(self, property_name: str, default_value: Any = None) -> Any:
        """Get theme property with caching."""
        widget = self._widget()
        if widget is None:
            return default_value

        with self._lock:
            # Check cache first
            if property_name in self._cache:
                self._cache_hits += 1
                return self._cache[property_name]

            self._cache_misses += 1

            try:
                # Get from theme system
                theme_manager = widget._theme_manager
                if not theme_manager:
                    return default_value

                # Look up the property path from theme_config
                property_path = property_name
                if hasattr(widget, "_theme_config") and property_name in widget._theme_config:
                    property_path = widget._theme_config[property_name]

                # ✅ NEW: Use ThemeManager.resolve_token() instead of direct navigation
                # Infer token type from property name (heuristic)
                token_type = self._infer_token_type(property_name, property_path)

                # Resolve using unified API (with override support!)
                value = theme_manager.resolve_token(
                    property_path,
                    token_type,
                    fallback=default_value
                )

                if value is not None:
                    # Cache the value
                    self._cache[property_name] = value
                    return value

                return default_value

            except PropertyNotFoundError:
                return default_value
            except Exception as e:
                logger.error(f"Error getting theme property {property_path}: {e}")
                return default_value

    def set_property(self, property_path: str, value: Any) -> None:
        """Set theme property and invalidate cache."""
        widget = self._widget()
        if widget is None:
            return

        with self._lock:
            try:
                # Set the property (this would typically create a custom theme)
                # For now, just store it locally
                self._cache[property_path] = value

                # Notify widget of change
                widget._on_property_changed(property_path, value)

            except Exception as e:
                logger.error(f"Error setting theme property {property_path}: {e}")

    def _infer_token_type(self, property_name: str, property_path: str) -> TokenType:
        """Infer token type from property name or path.

        Uses heuristics to determine what type of token is being requested
        based on naming patterns in the property name or path.

        Args:
            property_name: Name from widget's theme_config
            property_path: Token path (e.g., "editor.background")

        Returns:
            TokenType enum value

        """
        name_lower = property_name.lower()
        path_lower = property_path.lower()

        # Check for color indicators
        if any(word in name_lower or word in path_lower for word in [
            "color", "background", "foreground", "bg", "fg", "border"
        ]):
            return TokenType.COLOR

        # Check for font indicators
        if "font" in name_lower or "font" in path_lower:
            if "size" in name_lower or "size" in path_lower:
                return TokenType.FONT_SIZE
            return TokenType.FONT

        # Check for size indicators
        if any(word in name_lower for word in ["width", "height", "size"]):
            return TokenType.SIZE

        # Check for spacing indicators
        if any(word in name_lower for word in ["padding", "margin", "spacing", "gap"]):
            return TokenType.SPACING

        # Check for opacity indicators
        if any(word in name_lower for word in ["opacity", "alpha"]):
            return TokenType.OPACITY

        # Check for radius indicators
        if "radius" in name_lower:
            return TokenType.RADIUS

        # Default to OTHER
        return TokenType.OTHER

    def _resolve_property_path(self, theme: Theme, property_path: str) -> Any:
        """Resolve dot-separated property path in theme.

        DEPRECATED: This method is kept for backward compatibility but
        is no longer used internally. New code should use
        ThemeManager.resolve_token() instead.

        """
        try:
            # Split path and navigate through theme data
            parts = property_path.split(".")
            current = theme

            for part in parts:
                if hasattr(current, part):
                    current = getattr(current, part)
                elif isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    # Try theme-specific resolution
                    if hasattr(theme, "resolve_property"):
                        return theme.resolve_property(property_path)
                    return None

            return current

        except Exception as e:
            logger.error(f"Error resolving property path {property_path}: {e}")
            return None

    def invalidate_cache(self) -> None:
        """Invalidate all cached properties."""
        with self._lock:
            self._cache.clear()

    def get_statistics(self) -> dict[str, Any]:
        """Get cache statistics for performance monitoring."""
        return {
            "cache_size": len(self._cache),
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "hit_rate": self.cache_hit_rate,
        }


class ThemeAccess:
    """Dynamic theme property access object with smart defaults.

    Provides intuitive defaults for common theme properties when not found:
    - Colors: Safe fallback colors (readable in any theme)
    - Fonts: System default fonts
    - Numbers: Sensible UI defaults (sizes, spacing, etc.)
    """

    # Smart defaults for common property patterns
    _SMART_DEFAULTS = {
        # Colors
        "background": "#ffffff",
        "foreground": "#000000",
        "color": "#000000",
        "text": "#000000",
        "border": "#cccccc",
        "hover": "#e0e0e0",
        "active": "#d0d0d0",
        "disabled": "#a0a0a0",
        "accent": "#0078d4",
        "primary": "#0078d4",
        "secondary": "#6c757d",
        "error": "#dc3545",
        "warning": "#ffc107",
        "success": "#28a745",
        "info": "#17a2b8",
        # Fonts
        "font": "Arial, sans-serif",
        "font_family": "Arial, sans-serif",
        "font_size": "12px",
        # Dimensions
        "padding": "8px",
        "margin": "8px",
        "border_width": "1px",
        "border_radius": "4px",
        "spacing": "8px",
        # Opacity
        "opacity": "1.0",
        "alpha": "1.0",
    }

    def __init__(self, widget: "ThemedWidget"):
        self._widget = weakref.ref(widget)

    def _get_smart_default(self, name: str) -> Any:
        """Get smart default for property name."""
        # Direct match
        if name in self._SMART_DEFAULTS:
            return self._SMART_DEFAULTS[name]

        # Pattern matching for property names
        name_lower = name.lower()

        # Color properties
        if any(word in name_lower for word in ["color", "background", "foreground", "bg", "fg"]):
            if "error" in name_lower or "danger" in name_lower:
                return self._SMART_DEFAULTS["error"]
            elif "warning" in name_lower:
                return self._SMART_DEFAULTS["warning"]
            elif "success" in name_lower:
                return self._SMART_DEFAULTS["success"]
            elif "info" in name_lower:
                return self._SMART_DEFAULTS["info"]
            elif "background" in name_lower or "bg" in name_lower:
                return self._SMART_DEFAULTS["background"]
            elif "foreground" in name_lower or "fg" in name_lower or "text" in name_lower:
                return self._SMART_DEFAULTS["foreground"]
            else:
                return self._SMART_DEFAULTS["color"]

        # Font properties
        if "font" in name_lower:
            if "size" in name_lower:
                return self._SMART_DEFAULTS["font_size"]
            else:
                return self._SMART_DEFAULTS["font"]

        # Dimension properties
        if any(word in name_lower for word in ["padding", "margin", "spacing"]):
            return self._SMART_DEFAULTS["padding"]

        if "border" in name_lower:
            if "radius" in name_lower:
                return self._SMART_DEFAULTS["border_radius"]
            elif "width" in name_lower:
                return self._SMART_DEFAULTS["border_width"]
            else:
                return self._SMART_DEFAULTS["border"]

        # Opacity properties
        if any(word in name_lower for word in ["opacity", "alpha"]):
            return self._SMART_DEFAULTS["opacity"]

        # No smart default found
        return None

    def __getattr__(self, name: str) -> Any:
        """Dynamic property access with smart defaults."""
        widget = self._widget()
        if widget is None:
            return self._get_smart_default(name)

        value = widget._theme_properties.get_property(name)
        if value is None:
            # Try smart default
            return self._get_smart_default(name)
        return value

    def __setattr__(self, name: str, value: Any) -> None:
        """Dynamic property setting."""
        if name.startswith("_"):
            super().__setattr__(name, value)
            return

        widget = self._widget()
        if widget is not None:
            widget._theme_properties.set_property(name, value)

    def __getitem__(self, key: str) -> Any:
        """Dictionary-style access."""
        return self.__getattr__(key)

    def get(self, key: str, default: Any = None) -> Any:
        """Get with default value."""
        widget = self._widget()
        if widget is None:
            return default if default is not None else self._get_smart_default(key)

        value = widget._theme_properties.get_property(key)
        if value is None:
            # Try smart default, then provided default
            smart_default = self._get_smart_default(key)
            return smart_default if smart_default is not None else default
        return value


class ThemedWidgetMeta(type(QWidget)):
    """Metaclass for ThemedWidget to process theme configuration."""

    def __new__(mcs, name, bases, namespace, **kwargs):
        """Process theme_config during class creation."""
        cls = super().__new__(mcs, name, bases, namespace)

        # Merge theme_config from base classes
        merged_config = {}

        # Collect configs from base classes
        for base in reversed(bases):
            if hasattr(base, "_merged_theme_config"):
                merged_config.update(base._merged_theme_config)

        # Add current class config
        if "theme_config" in namespace:
            merged_config.update(namespace["theme_config"])

        # Set merged config
        cls._merged_theme_config = merged_config

        return cls


class ThemedWidget(metaclass=ThemedWidgetMeta):
    """The primary API for creating themed widgets.

    ThemedWidget provides simple inheritance that automatically gives widgets:
    - Complete theming capabilities
    - Automatic theme registration and cleanup
    - Thread-safe theme updates
    - Memory leak prevention
    - Error recovery and fallback themes
    - High-performance property access with caching

    Usage:
        class MyWidget(ThemedWidget, QWidget):
            theme_config = {
                'bg': 'window.background',
                'fg': 'window.foreground',
                'accent': 'accent.primary'
            }

            def on_theme_changed(self):
                # Called automatically when theme changes
                self.update()

            def paintEvent(self, event):
                painter = QPainter(self)
                painter.fillRect(self.rect(), QColor(self.theme.bg))

    All complexity is hidden behind this simple interface. Developers get
    bulletproof theming without any configuration or setup.

    IMPORTANT: ThemedWidget must come FIRST in multiple inheritance:
        Correct:   class MyWidget(ThemedWidget, QWidget)
        Correct:   class MyWindow(ThemedWidget, QMainWindow)
        Incorrect: class MyWidget(QWidget, ThemedWidget)
    """

    # Default theme configuration
    theme_config = {
        "background": "window.background",
        "color": "window.foreground",
        "font": "text.font",
    }

    # Qt signals for theme updates
    if QT_AVAILABLE:
        theme_changed = Signal(str)  # Emitted when theme changes
        theme_applied = Signal()  # Emitted when theme is applied to this widget
        property_changed = Signal(str, object, object)  # property, old_value, new_value
    else:
        # Mock signals for testing
        theme_changed = None
        theme_applied = None
        property_changed = None

    def __init__(self, parent: Optional["QWidget"] = None, **kwargs):
        """Initialize themed widget with automatic setup.

        All complexity is hidden here:
        - Widget registration with memory management
        - Theme system initialization
        - Signal/slot connections
        - Error recovery setup
        """
        # Validate inheritance order - ThemedWidget must come BEFORE Qt base classes
        self._validate_inheritance_order()

        # Call parent __init__ with proper arguments
        # This handles the Qt widget initialization
        super().__init__(parent, **kwargs)

        # Generate unique widget ID
        self._widget_id = str(uuid.uuid4())

        # Initialize managers (dependency injection)
        self._theme_manager: Optional[ThemeManager] = None
        self._lifecycle_manager: Optional[LifecycleManager] = None
        self._thread_manager: Optional[ThreadSafeThemeManager] = None

        # Initialize theme properties manager
        self._theme_properties = ThemePropertiesManager(self)

        # Theme access object
        self.theme = ThemeAccess(self)

        # Widget state
        self._current_theme_name: Optional[str] = None
        self._is_theme_registered = False
        self._is_theme_system_ready = False
        self._property_cache_enabled = True
        self._theme_applied = False  # Track if theme has been applied (for Polish event)

        # Merge theme config from class hierarchy
        self._theme_config = getattr(
            self.__class__, "_merged_theme_config", self.theme_config.copy()
        )

        # Performance tracking
        self._theme_update_count = 0
        self._last_theme_update = 0.0

        # Set up the widget
        self._initialize_theme_system()

        logger.debug(f"ThemedWidget created: {type(self).__name__} (ID: {self._widget_id})")

    def _initialize_theme_system(self) -> None:
        """Initialize the theme system for this widget.

        This method handles all the complexity:
        1. Dependency injection of all theme system components
        2. Widget registration with automatic cleanup
        3. Signal/slot connection for theme updates
        4. Error recovery setup
        5. Performance optimization setup
        """
        try:
            # Get singleton instance of ThemeManager
            self._theme_manager = ThemeManager.get_instance()
            # Optional components (not singletons)
            self._lifecycle_manager = None  # Will be created if needed
            self._thread_manager = None  # Will be created if needed

            # Register widget with shared registry from ThemeManager
            if self._theme_manager and hasattr(self._theme_manager, "_widget_registry"):
                registry = self._theme_manager._widget_registry
                registry.register_widget(self)
                self._is_theme_registered = True
            else:
                self._is_theme_registered = False

            # Register for theme change notifications
            # Connect to the application's theme_changed signal if available
            try:
                from .application import ThemedApplication

                app = ThemedApplication.instance()
                if app:
                    app.theme_changed.connect(self._on_global_theme_changed)
            except Exception as e:
                logger.debug(f"Could not connect to application theme signal: {e}")

            # Set initial theme
            if self._theme_manager:
                current_theme = self._theme_manager.current_theme
                if current_theme:
                    self._current_theme_name = current_theme.name

            # Mark as ready
            self._is_theme_system_ready = True

            # Defer theme application slightly to allow async widgets to initialize
            # QTimer.singleShot(0) defers to next event loop iteration
            # This fixes race condition for async widgets like QWebEngineView
            QTimer.singleShot(0, self._apply_deferred_theme)

            logger.debug(f"Theme system initialized for widget {self._widget_id}")

        except Exception as e:
            logger.error(f"Error initializing theme system: {e}")
            # Graceful degradation - widget still works without theming
            self._is_theme_system_ready = False

            # Use error recovery system
            error_manager = get_global_error_recovery_manager()
            error_manager.handle_error(
                ThemeError(f"Theme system initialization failed: {e}"),
                operation="initialize_theme_system",
                context={"widget_type": type(self).__name__, "widget_id": self._widget_id},
            )

    def _apply_deferred_theme(self) -> None:
        """Apply theme in deferred manner (called via QTimer.singleShot).

        This method is called on the next event loop iteration after widget construction,
        which gives async widgets (like QWebEngineView) time to initialize.

        For synchronous widgets, this is nearly immediate.
        For async widgets, this provides the necessary initialization window.
        """
        if not self._theme_applied:
            logger.debug(f"Applying deferred theme for {type(self).__name__}")
            self._apply_theme_update()
            self._validate_styling_applied()

            # Call user-defined theme change handler if it exists
            if hasattr(self, "on_theme_changed") and callable(self.on_theme_changed):
                try:
                    self.on_theme_changed()
                except Exception as e:
                    logger.error(f"Error in initial theme handler call: {e}")

            self._theme_applied = True

    def _get_theme_property(self, property_path: str, default_value: Any = None) -> Any:
        """Get theme property through the properties manager."""
        return self._theme_properties.get_property(property_path, default_value)

    def _set_theme_property(self, property_path: str, value: Any) -> None:
        """Set theme property through the properties manager."""
        self._theme_properties.set_property(property_path, value)

    def _on_property_changed(self, property_name: str, new_value: Any) -> None:
        """Handle property change notifications."""
        try:
            # Emit property change signal
            self.property_changed.emit(property_name, None, new_value)

            # Update widget appearance
            self._apply_theme_update()

        except Exception as e:
            logger.error(f"Error handling property change: {e}")

    def _on_global_theme_changed(self, theme_name: str) -> None:
        """Handle theme change signal from application.

        Args:
            theme_name: Name of the new theme

        """
        try:
            if not self._is_theme_system_ready:
                return

            # Update current theme name
            self._current_theme_name = theme_name

            # Invalidate property cache
            self._theme_properties.invalidate_cache()

            # Apply theme update (regenerate and apply stylesheet)
            self._apply_theme_update()

            # Call the public on_theme_changed method
            self.on_theme_changed()

        except Exception as e:
            logger.error(f"Error handling theme change: {e}")

    def _on_theme_changed(self, theme: Theme) -> None:
        """Handle global theme changes.

        This method is automatically connected to theme change signals
        and ensures this widget updates when the global theme changes.
        """
        try:
            if not self._is_theme_system_ready:
                return

            # Update current theme name
            self._current_theme_name = theme.name

            # Invalidate property cache
            self._theme_properties.invalidate_cache()

            # Apply theme update
            self._apply_theme_update()

            # Call user-defined handler if it exists
            if hasattr(self, "on_theme_changed") and callable(self.on_theme_changed):
                try:
                    self.on_theme_changed()
                except Exception as e:
                    logger.error(f"Error in user theme change handler: {e}")

            # Emit signals
            self.theme_changed.emit(theme.name)
            self.theme_applied.emit()

            # Update performance tracking
            import time

            self._theme_update_count += 1
            self._last_theme_update = time.time()

            logger.debug(f"Theme changed to '{theme.name}' for widget {self._widget_id}")

        except Exception as e:
            logger.error(f"Error handling theme change: {e}")
            # Use error recovery
            error_manager = get_global_error_recovery_manager()
            error_manager.handle_error(
                ThemeError(f"Theme change handling failed: {e}"),
                context={"widget_id": self._widget_id, "theme": theme.name if theme else "unknown"},
            )

    def _apply_theme_update(self) -> None:
        """Apply theme updates to the widget."""
        try:
            if not self._is_theme_system_ready:
                return

            # Generate and apply stylesheet
            stylesheet = self._generate_stylesheet()
            if stylesheet:
                self.setStyleSheet(stylesheet)

            # Generate and apply palette (NEW: QPalette integration)
            palette = self._generate_palette()
            if palette:
                self.setPalette(palette)
                # Apply palette to all child widgets recursively
                self._apply_palette_to_children(palette)

            # Force repaint
            if hasattr(self, "update"):
                self.update()

        except Exception as e:
            logger.error(f"Error applying theme update: {e}")

    def _generate_stylesheet(self) -> str:
        """Generate Qt stylesheet based on current theme.

        Uses StylesheetGenerator to create comprehensive stylesheets that cascade
        to all child widgets. Subclasses can override _generate_custom_stylesheet()
        to add custom styling on top of the base theme.

        Returns:
            Complete Qt stylesheet string

        """
        try:
            if not self._is_theme_system_ready:
                return ""

            # Check if this widget has opted out of theming
            if self.property("vftheme_disable"):
                return ""

            # Get current theme
            if not self._theme_manager or not self._theme_manager.current_theme:
                return ""

            theme = self._theme_manager.current_theme

            # Use StylesheetGenerator for comprehensive styling
            from .stylesheet_generator import StylesheetGenerator

            generator = StylesheetGenerator(theme, self.__class__.__name__)
            base_stylesheet = generator.generate_comprehensive_stylesheet()

            # Allow subclasses to add custom styling
            custom_stylesheet = self._generate_custom_stylesheet()

            # Combine base + custom
            if custom_stylesheet:
                return base_stylesheet + "\n\n" + custom_stylesheet
            else:
                return base_stylesheet

        except Exception as e:
            logger.error(f"Error generating stylesheet: {e}")
            # Fallback to minimal styling
            try:
                bg = self.theme.get_color("colors.background", "#ffffff")
                fg = self.theme.get_color("colors.foreground", "#000000")
                return f"{self.__class__.__name__} {{ background-color: {bg}; color: {fg}; }}"
            except Exception:
                return ""

    def _generate_custom_stylesheet(self) -> str:
        """Generate custom stylesheet for this widget.

        Subclasses can override this method to add custom styling beyond
        the base theme. The custom stylesheet is appended to the base stylesheet.

        Example:
            class MyEditor(ThemedWidget, QTextEdit):
                theme_config = {
                    "bg": "editor.background",
                    "fg": "editor.foreground",
                }

                def _generate_custom_stylesheet(self) -> str:
                    return f'''
                        QTextEdit {{
                            background-color: {self.theme.bg};
                            color: {self.theme.fg};
                            border: 2px solid red;
                        }}
                    '''

        Returns:
            Custom stylesheet string (empty string if no custom styling)

        """
        return ""

    def _generate_palette(self) -> Optional[QPalette]:
        """Generate Qt palette based on current theme.

        Uses PaletteGenerator to create comprehensive QPalette that handles
        color roles QSS cannot control (alternating rows, selections, etc.).
        Subclasses can override _generate_custom_palette() to customize.

        Returns:
            Complete Qt QPalette or None if theme not ready

        """
        try:
            if not self._is_theme_system_ready:
                return None

            # Check if this widget has opted out of theming
            if self.property("vftheme_disable"):
                return None

            # Get current theme
            if not self._theme_manager or not self._theme_manager.current_theme:
                return None

            theme = self._theme_manager.current_theme

            # Use PaletteGenerator for automatic palette generation
            from .palette_generator import PaletteGenerator

            generator = PaletteGenerator(theme)
            base_palette = generator.generate_palette()

            # Allow subclasses to customize palette
            custom_palette = self._generate_custom_palette()
            if custom_palette:
                # Merge custom palette into base palette
                # Custom colors override base colors
                return custom_palette
            else:
                return base_palette

        except Exception as e:
            logger.error(f"Error generating palette: {e}")
            return None

    def _generate_custom_palette(self) -> Optional[QPalette]:
        """Generate custom palette for this widget.

        Subclasses can override this method to customize palette colors beyond
        the base theme. The custom palette replaces the base palette.

        Example:
            class MyListView(ThemedWidget, QListView):
                def _generate_custom_palette(self) -> QPalette:
                    palette = QPalette()
                    # Custom alternating row colors
                    palette.setColor(QPalette.Base, QColor('#1a1a1a'))
                    palette.setColor(QPalette.AlternateBase, QColor('#2a2a2a'))
                    return palette

        Returns:
            Custom QPalette or None to use automatic palette

        """
        return None

    def _apply_palette_to_children(self, palette: QPalette) -> None:
        """Apply palette recursively to all child widgets.

        Qt doesn't automatically propagate palette to children, so we need to
        explicitly set it on all child widgets for proper theming.

        Args:
            palette: QPalette to apply to children

        """
        try:
            if not hasattr(self, 'children'):
                return

            for child in self.children():
                if hasattr(child, 'setPalette'):
                    child.setPalette(palette)
                    # Recursively apply to grandchildren
                    if hasattr(child, 'children'):
                        for grandchild in child.children():
                            if hasattr(grandchild, 'setPalette'):
                                grandchild.setPalette(palette)
        except Exception as e:
            logger.debug(f"Error applying palette to children: {e}")

    @property
    def theme_name(self) -> Optional[str]:
        """Get current theme name."""
        return self._current_theme_name

    def get_current_theme(self):
        """Get the current theme object.

        Returns the actual Theme object from the theme manager, or None if:
        - Theme system is not initialized
        - No theme is currently set

        Use this method to:
        - Pass theme to child components
        - Access theme in custom renderers/painters
        - Get theme data for non-ThemedWidget children

        Returns:
            Theme object with .colors dict and .name, or None

        Example:
            def paintEvent(self, event):
                theme = self.get_current_theme()
                if theme:
                    color = theme.colors.get('myColor', '#default')
                    self.renderer.draw(painter, theme)

        """
        if hasattr(self, "_theme_manager") and self._theme_manager:
            return self._theme_manager.current_theme
        return None

    @property
    def is_theme_ready(self) -> bool:
        """Check if theme system is ready."""
        return self._is_theme_system_ready

    @property
    def theme_statistics(self) -> dict[str, Any]:
        """Get theme-related statistics for monitoring."""
        stats = {
            "widget_id": self._widget_id,
            "theme_name": self._current_theme_name,
            "is_registered": self._is_theme_registered,
            "is_ready": self._is_theme_system_ready,
            "update_count": self._theme_update_count,
            "last_update": self._last_theme_update,
        }

        # Add property manager statistics
        if self._theme_properties:
            stats.update(self._theme_properties.get_statistics())

        return stats

    def debug_styling_status(self) -> str:
        """Get debug information about widget styling status.

        Returns a formatted string showing:
        - Whether stylesheet is applied
        - Stylesheet length
        - Theme name
        - Whether theme system is ready

        Useful for debugging theme issues.

        Example:
            widget = ThemedMainWindow()
            print(widget.debug_styling_status())

        """
        lines = [
            f"Widget: {self.__class__.__name__}",
            f"Widget ID: {self._widget_id}",
            f"Theme System Ready: {self._is_theme_system_ready}",
            f"Current Theme: {self._current_theme_name}",
            f"Registered: {self._is_theme_registered}",
        ]

        try:
            stylesheet = self.styleSheet()
            lines.append(f"Stylesheet Length: {len(stylesheet)} chars")

            if len(stylesheet) == 0:
                lines.append("⚠️  WARNING: No stylesheet applied!")
            elif len(stylesheet) < 100:
                lines.append("⚠️  WARNING: Stylesheet suspiciously short!")
            else:
                lines.append("✅ Stylesheet applied successfully")

        except Exception as e:
            lines.append(f"❌ Error getting stylesheet: {e}")

        return "\n".join(lines)

    def on_theme_changed(self) -> None:
        """Override this method to handle theme changes.

        This method is called automatically when the theme changes.
        Default implementation does nothing - override in subclasses.
        """
        pass  # Default implementation - user can override

    def _validate_styling_applied(self) -> None:
        """Validate that stylesheet was applied to this widget.

        This is a development-time safety check to catch issues like:
        - Stylesheet generation not being called
        - Empty stylesheets being generated
        - Theme system not properly initialized

        Issues a warning (not an error) since the widget should still function,
        just without theming.
        """
        try:
            # Only validate if theme system is ready and not opted out
            if not self._is_theme_system_ready:
                return

            if self.property("vftheme_disable"):
                return

            # Check if stylesheet was applied
            stylesheet = self.styleSheet()

            # Warning if stylesheet is empty or suspiciously short
            if len(stylesheet) == 0:
                logger.warning(
                    f"ThemedWidget {self.__class__.__name__} has no stylesheet applied! "
                    f"Widget will use Qt defaults instead of theme styling. "
                    f"This usually indicates a bug in the theme system."
                )
            elif len(stylesheet) < 100:
                logger.warning(
                    f"ThemedWidget {self.__class__.__name__} has suspiciously short stylesheet "
                    f"({len(stylesheet)} chars). Expected comprehensive theming (several KB). "
                    f"Theme may not be fully applied."
                )
            else:
                # Success - stylesheet looks reasonable
                logger.debug(
                    f"Styling validated for {self.__class__.__name__}: "
                    f"{len(stylesheet)} char stylesheet applied"
                )

        except Exception as e:
            logger.debug(f"Could not validate styling (non-critical): {e}")

    def _validate_inheritance_order(self) -> None:
        """Validate that ThemedWidget comes before Qt base classes in inheritance.

        This prevents the common mistake of:
            class MyWidget(QWidget, ThemedWidget)  # ❌ Wrong order

        Instead of the correct:
            class MyWidget(ThemedWidget, QWidget)  # ✅ Correct order

        Raises:
            TypeError: If inheritance order is incorrect

        """
        # Get Method Resolution Order (MRO) for this class
        mro = type(self).__mro__

        # Find positions of ThemedWidget and QWidget in MRO
        themed_widget_index = None
        qt_widget_index = None
        qt_widget_class_name = None

        for i, cls in enumerate(mro):
            if cls.__name__ == "ThemedWidget":
                themed_widget_index = i
            elif cls.__name__ in (
                "QWidget",
                "QMainWindow",
                "QDialog",
                "QFrame",
                "QLabel",
                "QPushButton",
                "QTextEdit",
                "QListWidget",
                "QTableWidget",
            ):
                if qt_widget_index is None:  # Only check the first Qt widget found
                    qt_widget_index = i
                    qt_widget_class_name = cls.__name__

        # If both are present and Qt widget comes before ThemedWidget, that's an error
        if (
            themed_widget_index is not None
            and qt_widget_index is not None
            and qt_widget_index < themed_widget_index
        ):
            class_name = type(self).__name__
            error_msg = (
                f"\n"
                f"❌ Incorrect inheritance order detected in class '{class_name}'\n"
                f"\n"
                f"ThemedWidget must come BEFORE Qt base classes in the inheritance list.\n"
                f"\n"
                f"Current (incorrect) order:\n"
                f"  class {class_name}({qt_widget_class_name}, ThemedWidget, ...)  # ❌ Wrong!\n"
                f"\n"
                f"Correct order:\n"
                f"  class {class_name}(ThemedWidget, {qt_widget_class_name}, ...)  # ✅ Correct!\n"
                f"\n"
                f"Why? ThemedWidget needs to initialize before Qt widgets to properly set up\n"
                f"the theming system. Python's MRO (Method Resolution Order) requires this.\n"
                f"\n"
                f"Quick fix: Just move ThemedWidget to the left in your class definition.\n"
            )
            raise TypeError(error_msg)

    def _cleanup_theme(self) -> None:
        """Clean up theme resources."""
        try:
            if self._is_theme_registered:
                # Disconnect signals
                if self._theme_manager:
                    try:
                        self._theme_manager.theme_changed.disconnect(self._on_theme_changed)
                    except Exception:
                        pass  # May already be disconnected

                # Unregister from registry
                if self._theme_manager and hasattr(self._theme_manager, "_widget_registry"):
                    registry = self._theme_manager._widget_registry
                    registry.unregister_widget(self._widget_id)

                self._is_theme_registered = False

            # Clear references
            self._theme_manager = None
            self._lifecycle_manager = None
            self._thread_manager = None

            # Clear cache
            if self._theme_properties:
                self._theme_properties.invalidate_cache()

            logger.debug(f"Theme cleanup completed for widget {self._widget_id}")

        except Exception as e:
            logger.error(f"Error during theme cleanup: {e}")

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle widget close event."""
        try:
            # Clean up theme resources before closing
            self._cleanup_theme()

            # Call parent implementation
            super().closeEvent(event)

        except Exception as e:
            logger.error(f"Error in closeEvent: {e}")
            super().closeEvent(event)

    def __del__(self) -> None:
        """Automatic cleanup when widget is destroyed.

        This ensures no memory leaks occur when widgets are garbage collected.
        """
        try:
            self._cleanup_theme()
        except Exception:
            # Ignore errors during destruction to prevent crashes
            pass


# Utility function for creating themed widgets
def create_themed_widget(
    widget_class: type, theme_name: Optional[str] = None, parent: Optional[QWidget] = None, **kwargs
) -> ThemedWidget:
    """Create themed widgets.

    This provides an alternative to inheritance for creating themed widgets.

    Args:
        widget_class: Class to create (must inherit from ThemedWidget)
        theme_name: Optional theme to apply immediately
        parent: Parent widget
        **kwargs: Additional arguments for widget constructor

    Returns:
        Configured themed widget instance

    """
    try:
        # Create the widget
        widget = widget_class(parent=parent, **kwargs)

        # Apply specific theme if requested
        if theme_name and hasattr(widget, "_theme_manager") and widget._theme_manager:
            try:
                widget._theme_manager.set_theme(theme_name)
            except Exception as e:
                logger.warning(f"Could not apply theme '{theme_name}': {e}")

        logger.debug(f"Created themed widget: {widget_class.__name__}")
        return widget

    except Exception as e:
        logger.error(f"Error creating themed widget: {e}")
        # Return basic widget as fallback
        return widget_class(parent=parent, **kwargs)


__all__ = [
    "ThemedWidget",
    "ThemedWidgetMeta",
    "ThemePropertyDescriptor",
    "ThemePropertiesManager",
    "ThemeAccess",
    "create_themed_widget",
]
