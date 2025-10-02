"""Theme property descriptors for clean, type-safe theme access.

This module provides property descriptors that enable clean, type-safe access
to theme properties without using getattr() or dict lookups. Descriptors
follow Python's descriptor protocol for proper class and instance behavior.

Key Features:
- Type-safe theme property access
- Read-only properties (theme values can't be modified via properties)
- Smart defaults from ColorTokenRegistry
- QColor and QFont conversion for specialized properties
- IDE autocomplete support when used with Tokens constants

Usage:
    from vfwidgets_theme import Tokens
    from vfwidgets_theme.widgets.properties import ThemeProperty, ColorProperty

    class MyWidget(ThemedWidget, QWidget):
        # Simple property access
        bg = ThemeProperty(Tokens.COLORS_BACKGROUND, default='#ffffff')

        # Type-safe color property (returns QColor)
        fg_color = ColorProperty(Tokens.COLORS_FOREGROUND, default='#000000')

        def paintEvent(self, event):
            # Clean access - no getattr needed!
            painter.fillRect(self.rect(), self.fg_color)

Architecture:
- ThemeProperty: Base descriptor implementing descriptor protocol
- ColorProperty: Specialized for color values (returns QColor)
- FontProperty: Specialized for font values (returns QFont)

All properties are READ-ONLY - theme values are managed by the theme system,
not by individual widgets.
"""

from typing import Any, Optional

from PySide6.QtGui import QColor, QFont

# Import foundation modules
from ..errors import PropertyNotFoundError
from ..logging import get_debug_logger

logger = get_debug_logger(__name__)


class ThemeProperty:
    """Base property descriptor for type-safe theme property access.

    Implements Python's descriptor protocol to provide clean, attribute-style
    access to theme properties. Properties are read-only and automatically
    resolve theme values through the widget's theme system.

    The descriptor protocol methods:
    - __set_name__: Called when descriptor is bound to a class attribute
    - __get__: Called when property is accessed from instance or class
    - __set__: Called when attempting to set property (raises AttributeError)

    Usage:
        class MyWidget(ThemedWidget, QWidget):
            bg = ThemeProperty('colors.background', default='#ffffff')
            fg = ThemeProperty('colors.foreground', default='#000000')

            def paintEvent(self, event):
                # Clean access:
                color = QColor(self.bg)  # Gets theme value automatically

    Args:
        token: Theme token path (e.g., 'colors.background')
        default: Default value if theme value not found

    Attributes:
        token: The theme token path this property maps to
        default: Default value returned when theme value unavailable
        _attr_name: Attribute name (set by __set_name__)

    """

    def __init__(self, token: str, default: Optional[Any] = None):
        """Initialize theme property descriptor.

        Args:
            token: Theme token path (e.g., 'colors.background')
            default: Default value if theme value not found

        """
        self.token = token
        self.default = default
        self._attr_name: Optional[str] = None

    def __set_name__(self, owner, name: str):
        """Store attribute name when descriptor is bound to class.

        This is called automatically by Python when the class is created:

            class MyWidget(ThemedWidget):
                bg = ThemeProperty('colors.background')  # __set_name__ called here

        Args:
            owner: The class that owns this descriptor
            name: The attribute name (e.g., 'bg')

        """
        self._attr_name = name
        logger.debug(f"ThemeProperty '{name}' bound to {owner.__name__} with token '{self.token}'")

    def __get__(self, obj, objtype=None):
        """Get property value from theme system.

        Called when property is accessed:
        - From class: Returns the descriptor itself (for introspection)
        - From instance: Returns theme value via widget's theme system

        Args:
            obj: The instance accessing the property (None if accessed from class)
            objtype: The class type

        Returns:
            - Descriptor itself if accessed from class
            - Theme value if accessed from instance
            - Default value if theme value not available

        """
        # Access from class (e.g., MyWidget.bg) returns descriptor
        if obj is None:
            return self

        # Access from instance - get theme value
        try:
            # Check if widget has theme properties manager
            if hasattr(obj, '_theme_properties'):
                # Get value through theme properties manager
                value = obj._theme_properties.get_property(self.token, self.default)
                return value

            # Fallback: try legacy theme access
            if hasattr(obj, 'theme'):
                value = obj.theme.get(self.token, self.default)
                return value

            # No theme system available - return default
            logger.debug(
                f"Widget has no theme system, returning default for '{self._attr_name}'"
            )
            return self.default

        except PropertyNotFoundError:
            logger.debug(
                f"Property '{self.token}' not found in theme, returning default: {self.default}"
            )
            return self.default
        except Exception as e:
            logger.error(f"Error getting theme property '{self.token}': {e}")
            return self.default

    def __set__(self, obj, value):
        """Prevent setting theme properties (read-only).

        Theme properties are read-only because theme values are managed
        by the theme system, not by individual widgets.

        Args:
            obj: The instance
            value: The value attempting to be set

        Raises:
            AttributeError: Always (properties are read-only)

        """
        raise AttributeError(
            f"Theme property '{self._attr_name}' is read-only. "
            f"Theme values are managed by the theme system and cannot be set directly. "
            f"To customize widget styling, use theme_config or create a custom theme."
        )


class ColorProperty(ThemeProperty):
    """Property descriptor for color values that returns QColor instances.

    Specialized ThemeProperty that automatically converts color strings
    to QColor instances. Supports hex colors, rgb(), rgba(), and named colors.

    Usage:
        class MyWidget(ThemedWidget, QWidget):
            bg_color = ColorProperty('colors.background', default='#ffffff')
            fg_color = ColorProperty('colors.foreground', default='#000000')

            def paintEvent(self, event):
                # Returns QColor instance:
                painter.fillRect(self.rect(), self.bg_color)  # No QColor() needed!

    Args:
        token: Theme token path for color
        default: Default color value (hex string or color name)

    """

    def __init__(self, token: str, default: str = '#000000'):
        """Initialize color property descriptor.

        Args:
            token: Theme token path for color (e.g., 'colors.background')
            default: Default color value as hex string (e.g., '#ffffff')

        """
        super().__init__(token, default)

    def __get__(self, obj, objtype=None):
        """Get color value as QColor instance.

        Returns:
            - ColorProperty descriptor if accessed from class
            - QColor instance if accessed from instance
            - QColor(default) if theme value not available

        """
        # Access from class returns descriptor
        if obj is None:
            return self

        # Get color string from parent implementation
        color_string = super().__get__(obj, objtype)

        # Convert to QColor
        if color_string is None:
            color_string = self.default

        try:
            # Create QColor from string
            color = QColor(color_string)

            # Validate color
            if not color.isValid():
                logger.warning(
                    f"Invalid color '{color_string}' for property '{self._attr_name}', "
                    f"using default: {self.default}"
                )
                color = QColor(self.default)

            return color

        except Exception as e:
            logger.error(
                f"Error converting color '{color_string}' to QColor for '{self._attr_name}': {e}"
            )
            return QColor(self.default)


class FontProperty(ThemeProperty):
    """Property descriptor for font values that returns QFont instances.

    Specialized ThemeProperty that automatically converts font specifications
    to QFont instances. Supports various font string formats.

    Font string formats:
    - Family only: 'Arial'
    - Family with size: 'Arial, 12px'
    - CSS-style: 'Arial, sans-serif, 12px'

    Usage:
        class MyEditor(ThemedWidget, QTextEdit):
            editor_font = FontProperty('text.font', default='Consolas, 10px')

            def __init__(self):
                super().__init__()
                # Returns QFont instance:
                self.setFont(self.editor_font)  # No QFont() needed!

    Args:
        token: Theme token path for font
        default: Default font specification string

    """

    def __init__(self, token: str, default: str = 'Arial, 12px'):
        """Initialize font property descriptor.

        Args:
            token: Theme token path for font (e.g., 'text.font')
            default: Default font specification (e.g., 'Arial, 12px')

        """
        super().__init__(token, default)

    def __get__(self, obj, objtype=None):
        """Get font value as QFont instance.

        Returns:
            - FontProperty descriptor if accessed from class
            - QFont instance if accessed from instance
            - QFont(default) if theme value not available

        """
        # Access from class returns descriptor
        if obj is None:
            return self

        # Get font string from parent implementation
        font_string = super().__get__(obj, objtype)

        # Convert to QFont
        if font_string is None:
            font_string = self.default

        try:
            # Parse font string and create QFont
            font = self._parse_font_string(font_string)
            return font

        except Exception as e:
            logger.error(
                f"Error converting font '{font_string}' to QFont for '{self._attr_name}': {e}"
            )
            # Return default font
            return self._parse_font_string(self.default)

    def _parse_font_string(self, font_string: str) -> QFont:
        """Parse font specification string to QFont.

        Supports formats:
        - 'Arial' -> Arial, 12px (default size)
        - 'Arial, 12px' -> Arial, 12pt
        - 'Arial, sans-serif, 12px' -> Arial, 12pt

        Args:
            font_string: Font specification string

        Returns:
            QFont instance

        """
        try:
            # Split by comma
            parts = [p.strip() for p in font_string.split(',')]

            family = 'Arial'  # Default
            size = 12  # Default size in points

            # Extract family (first part)
            if parts:
                family = parts[0]

            # Extract size (look for number with 'px' or 'pt')
            for part in parts:
                part_lower = part.lower()
                if 'px' in part_lower or 'pt' in part_lower:
                    # Extract numeric part
                    size_str = ''.join(c for c in part if c.isdigit() or c == '.')
                    if size_str:
                        size = int(float(size_str))
                        break

            # Create QFont
            font = QFont(family, size)
            return font

        except Exception as e:
            logger.error(f"Error parsing font string '{font_string}': {e}")
            # Return safe default
            return QFont('Arial', 12)


__all__ = [
    'ThemeProperty',
    'ColorProperty',
    'FontProperty',
]
