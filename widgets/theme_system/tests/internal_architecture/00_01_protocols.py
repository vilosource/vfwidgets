"""
Working example demonstrating VFWidgets Theme System protocols.

This example shows how the protocols enable clean architecture through
dependency injection, allowing for easy testing with mocks and separation
of concerns. This is the foundation that makes ThemedWidget simple.

Key Demonstrations:
1. How protocols define clean interfaces
2. How dependency injection works
3. How to implement protocol conforming classes
4. How to test with mocks
5. How protocols enable the "ThemedWidget is THE way" philosophy

Run this example to see protocols in action.
"""

# Add the source path for imports
import os
import sys
from typing import Any, List
from unittest.mock import Mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from vfwidgets_theme.protocols import (
    ColorProvider,
    ColorValue,
    PropertyKey,
    PropertyValue,
    QSSStyle,
    StyleCallback,
    ThemeData,
    ThemeProvider,
)


# Example 1: Simple ThemeProvider implementation
class SimpleThemeProvider:
    """Example implementation of ThemeProvider protocol.

    This shows how protocols enable different theme sources:
    - File-based themes
    - Database themes
    - Network themes
    - In-memory themes (this example)
    """

    def __init__(self, theme_data: ThemeData):
        self._theme_data = theme_data
        self._callbacks: List[StyleCallback] = []

    def get_current_theme(self) -> ThemeData:
        """Get the complete current theme data."""
        return self._theme_data.copy()

    def get_property(self, key: PropertyKey) -> PropertyValue:
        """Get a specific theme property value."""
        return self._theme_data.get(key)

    def subscribe(self, callback: StyleCallback) -> None:
        """Subscribe to theme change notifications."""
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def unsubscribe(self, callback: StyleCallback) -> None:
        """Unsubscribe from theme change notifications."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def set_theme(self, theme_data: ThemeData) -> None:
        """Update theme and notify subscribers (not in protocol, but useful)."""
        old_theme = self._theme_data
        self._theme_data = theme_data

        # Notify all subscribers (would use Qt signals in real implementation)
        for callback in self._callbacks:
            callback("theme_changed")


# Example 2: Simple ColorProvider implementation
class SimpleColorProvider:
    """Example implementation of ColorProvider protocol.

    Shows intelligent color resolution with fallbacks.
    """

    def __init__(self, theme_provider: ThemeProvider):
        self._theme_provider = theme_provider
        self._color_mappings = {
            "primary": "primary_color",
            "secondary": "secondary_color",
            "error": "error_color",
            "warning": "warning_color",
            "success": "success_color",
        }

    def resolve_color(self, key: PropertyKey) -> ColorValue:
        """Resolve a color key to an actual color value."""
        # Try direct property lookup first
        color = self._theme_provider.get_property(key)
        if color:
            return str(color)

        # Try mapped lookup
        mapped_key = self._color_mappings.get(key)
        if mapped_key:
            color = self._theme_provider.get_property(mapped_key)
            if color:
                return str(color)

        # Return fallback
        return self.get_fallback_color()

    def get_fallback_color(self) -> ColorValue:
        """Get the fallback color for error recovery."""
        return "#000000"  # Black as safe fallback

    def validate_color(self, color: ColorValue) -> bool:
        """Validate if a color value is valid."""
        # Simple validation - in real implementation would be more thorough
        if not isinstance(color, str):
            return False

        # Check hex colors
        if color.startswith("#"):
            if len(color) == 7:  # #RRGGBB
                try:
                    int(color[1:], 16)
                    return True
                except ValueError:
                    return False
            elif len(color) == 4:  # #RGB
                try:
                    int(color[1:], 16)
                    return True
                except ValueError:
                    return False

        # Check RGB colors (simplified)
        if color.startswith("rgb("):
            return True

        # Check named colors (simplified)
        named_colors = {"black", "white", "red", "green", "blue", "yellow", "cyan", "magenta"}
        if color.lower() in named_colors:
            return True

        return False


# Example 3: Simple StyleGenerator implementation
class SimpleStyleGenerator:
    """Example implementation of StyleGenerator protocol.

    Shows QSS generation with proper error handling.
    """

    def __init__(self, color_provider: ColorProvider):
        self._color_provider = color_provider
        self._selector_map = {
            "button": "QPushButton",
            "label": "QLabel",
            "edit": "QLineEdit",
            "widget": "QWidget",
        }

    def generate_stylesheet(self, theme: ThemeData, widget: Any) -> QSSStyle:
        """Generate QSS stylesheet for a widget from theme data."""
        try:
            # Get widget type - in real implementation would inspect widget
            widget_type = getattr(widget, "widget_type", "widget")
            selector = self.get_selector(widget_type)

            styles = []

            # Background color
            if "background" in theme:
                bg_color = self._color_provider.resolve_color("background")
                if self._color_provider.validate_color(bg_color):
                    styles.append(f"background-color: {bg_color};")

            # Text color
            if "foreground" in theme:
                fg_color = self._color_provider.resolve_color("foreground")
                if self._color_provider.validate_color(fg_color):
                    styles.append(f"color: {fg_color};")

            # Border
            if "border_color" in theme:
                border_color = self._color_provider.resolve_color("border_color")
                if self._color_provider.validate_color(border_color):
                    styles.append(f"border: 1px solid {border_color};")

            # Font size
            if "font_size" in theme:
                font_size = theme.get("font_size", 12)
                styles.append(f"font-size: {font_size}px;")

            # Combine into QSS
            if styles:
                style_content = " ".join(styles)
                return f"{selector} {{ {style_content} }}"
            else:
                return ""  # Minimal fallback

        except Exception as e:
            # Error recovery - return minimal safe stylesheet
            print(f"Style generation error: {e}")
            return f"{self.get_selector('widget')} {{ background-color: white; color: black; }}"

    def get_selector(self, widget_type: str) -> str:
        """Get CSS selector for a widget type."""
        return self._selector_map.get(widget_type, "QWidget")

    def merge_styles(self, styles: List[QSSStyle]) -> QSSStyle:
        """Merge multiple stylesheets into a single stylesheet."""
        # Simple concatenation - real implementation would be smarter
        return "\n".join(style for style in styles if style.strip())


# Example 4: Mock widget showing ThemeableWidget usage
class ExampleWidget:
    """Example widget demonstrating ThemeableWidget protocol usage.

    This shows how widgets will use the protocols when ThemedWidget
    is implemented. ThemedWidget will hide this complexity.
    """

    def __init__(self, theme_provider: ThemeProvider, color_provider: ColorProvider):
        self._theme_provider = theme_provider
        self._color_provider = color_provider
        self._theme_config = {}
        self.widget_type = "button"  # For style generation

        # Subscribe to theme changes
        self._theme_provider.subscribe(self._on_theme_change_callback)

    @property
    def theme_config(self) -> ThemeData:
        """Widget-specific theme configuration."""
        return self._theme_config.copy()

    @property
    def theme_provider(self) -> ThemeProvider:
        """The theme provider for this widget."""
        return self._theme_provider

    def on_theme_changed(self) -> None:
        """Called when the theme changes."""
        print("Widget updating appearance for new theme...")
        # In real widget, this would update the UI
        bg_color = self.get_theme_color("background", "#ffffff")
        fg_color = self.get_theme_color("foreground", "#000000")
        print(f"  Background: {bg_color}")
        print(f"  Foreground: {fg_color}")

    def get_theme_color(self, key: PropertyKey, default: ColorValue = "#000000") -> ColorValue:
        """Get a color value from the current theme."""
        try:
            color = self._color_provider.resolve_color(key)
            if self._color_provider.validate_color(color):
                return color
            else:
                return default
        except Exception:
            return default

    def get_theme_property(self, key: PropertyKey, default: PropertyValue = None) -> PropertyValue:
        """Get any theme property value."""
        try:
            return self._theme_provider.get_property(key) or default
        except Exception:
            return default

    def _on_theme_change_callback(self, theme_name: str) -> None:
        """Internal callback for theme changes."""
        self.on_theme_changed()


def demonstrate_protocols():
    """Main demonstration of protocols in action."""
    print("=== VFWidgets Theme System Protocol Demonstration ===\n")

    # 1. Create a theme
    dark_theme = {
        "background": "#2b2b2b",
        "foreground": "#ffffff",
        "primary_color": "#007acc",
        "secondary_color": "#6c757d",
        "error_color": "#dc3545",
        "border_color": "#404040",
        "font_size": 12,
    }

    print("1. Creating theme provider with dark theme...")
    theme_provider = SimpleThemeProvider(dark_theme)
    print(f"   Theme has {len(theme_provider.get_current_theme())} properties")

    # 2. Create color provider
    print("\n2. Creating color provider...")
    color_provider = SimpleColorProvider(theme_provider)

    # Test color resolution
    primary = color_provider.resolve_color("primary")
    print(f"   Primary color resolved to: {primary}")

    unknown = color_provider.resolve_color("unknown_color")
    print(f"   Unknown color resolved to fallback: {unknown}")

    # 3. Create style generator
    print("\n3. Creating style generator...")
    style_generator = SimpleStyleGenerator(color_provider)

    # 4. Create example widget
    print("\n4. Creating example widget...")
    widget = ExampleWidget(theme_provider, color_provider)

    # 5. Generate stylesheet
    print("\n5. Generating stylesheet for widget...")
    stylesheet = style_generator.generate_stylesheet(dark_theme, widget)
    print(f"   Generated QSS:\n   {stylesheet}")

    # 6. Demonstrate theme switching
    print("\n6. Switching to light theme...")
    light_theme = {
        "background": "#ffffff",
        "foreground": "#000000",
        "primary_color": "#0066cc",
        "secondary_color": "#6c757d",
        "error_color": "#cc0000",
        "border_color": "#cccccc",
        "font_size": 14,
    }

    theme_provider.set_theme(light_theme)

    # Generate new stylesheet
    print("\n7. Generating new stylesheet...")
    new_stylesheet = style_generator.generate_stylesheet(light_theme, widget)
    print(f"   Updated QSS:\n   {new_stylesheet}")

    # 8. Demonstrate error recovery
    print("\n8. Demonstrating error recovery...")
    broken_theme = {
        "background": "invalid_color",
        "foreground": None,
        "font_size": "not_a_number",
    }

    safe_stylesheet = style_generator.generate_stylesheet(broken_theme, widget)
    print(f"   Safe fallback QSS:\n   {safe_stylesheet}")

    print("\n=== Protocol Demonstration Complete ===")


def demonstrate_dependency_injection():
    """Demonstrate how protocols enable dependency injection and testing."""
    print("\n=== Dependency Injection & Testing Demonstration ===\n")

    # 1. Using real implementations
    print("1. Using real implementations...")
    theme = {"primary_color": "#007acc", "background": "#2b2b2b"}
    real_provider = SimpleThemeProvider(theme)
    real_color_provider = SimpleColorProvider(real_provider)

    widget = ExampleWidget(real_provider, real_color_provider)
    color = widget.get_theme_color("primary")
    print(f"   Real implementation - primary color: {color}")

    # 2. Using mocks for testing
    print("\n2. Using mocks for testing...")
    mock_theme_provider = Mock()
    mock_theme_provider.get_property.return_value = "#ff0000"
    mock_theme_provider.subscribe.return_value = None

    mock_color_provider = Mock()
    mock_color_provider.resolve_color.return_value = "#ff0000"
    mock_color_provider.validate_color.return_value = True

    test_widget = ExampleWidget(mock_theme_provider, mock_color_provider)
    test_color = test_widget.get_theme_color("primary")
    print(f"   Mock implementation - primary color: {test_color}")

    # Verify mock was called
    mock_color_provider.resolve_color.assert_called_with("primary")
    print("   Mock verification passed!")

    print("\n=== Dependency Injection Complete ===")


if __name__ == "__main__":
    try:
        demonstrate_protocols()
        demonstrate_dependency_injection()

        print("\n🎉 All protocol examples completed successfully!")
        print("\nThis demonstrates how protocols enable:")
        print("- Clean architecture through dependency injection")
        print("- Easy testing with mocks")
        print("- Separation of concerns")
        print("- The foundation for ThemedWidget's simple API")

    except Exception as e:
        print(f"❌ Example failed: {e}")
        sys.exit(1)
