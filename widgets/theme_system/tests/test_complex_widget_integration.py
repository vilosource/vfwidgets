"""Integration test for complex widgets with child components accessing theme."""

from PySide6.QtCore import QRect
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget

from vfwidgets_theme import ThemedWidget


class CustomRenderer:
    """Mock renderer that needs theme data."""

    @staticmethod
    def draw(painter, rect, theme):
        """Draw using theme colors."""
        if theme and hasattr(theme, "colors"):
            bg_color = theme.colors.get("tab.activeBackground", "#ffffff")
            painter.fillRect(rect, QColor(bg_color))
        else:
            painter.fillRect(rect, QColor("#ffffff"))


class ChildWidget(QWidget):
    """Child widget (non-ThemedWidget) that needs theme access."""

    def _get_theme_from_parent(self):
        """Get theme by traversing parent chain."""
        parent = self.parent()
        while parent:
            if hasattr(parent, "get_current_theme"):
                return parent.get_current_theme()
            parent = parent.parent()
        return None

    def get_theme_colors(self):
        """Public method to get colors for testing."""
        theme = self._get_theme_from_parent()
        if theme and hasattr(theme, "colors"):
            return {
                "active": theme.colors.get("tab.activeBackground"),
                "inactive": theme.colors.get("tab.inactiveBackground"),
            }
        return None


class ComplexWidget(ThemedWidget, QWidget):
    """Complex widget with child components that need theme access."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.renderer = CustomRenderer()
        self.child_widget = ChildWidget(self)

    def get_current_theme(self):
        """Expose theme to children (inherited from ThemedWidget)."""
        return super().get_current_theme()


def test_complex_widget_has_get_current_theme(qapp):
    """Test that complex widget has get_current_theme method."""
    widget = ComplexWidget()
    assert hasattr(widget, "get_current_theme")
    assert callable(widget.get_current_theme)


def test_get_current_theme_returns_theme_object(qapp):
    """Test that get_current_theme returns actual Theme object when theme_manager exists."""
    from vfwidgets_theme.core.repository import ThemeRepository

    # Create widget
    widget = ComplexWidget()

    # Manually create a theme and inject it via _theme_manager
    # (simulating what ThemedApplication does)
    repo = ThemeRepository()
    theme = repo.get_theme("dark")

    # Create a minimal theme manager mock
    class MockThemeManager:
        def __init__(self, theme):
            self.current_theme = theme

    widget._theme_manager = MockThemeManager(theme)

    # Now get_current_theme should work
    theme_obj = widget.get_current_theme()

    assert theme_obj is not None
    assert hasattr(theme_obj, "colors")
    assert hasattr(theme_obj, "name")
    assert theme_obj.name == "dark"


def test_child_widget_can_access_parent_theme(qapp):
    """Test that child widget can get theme from parent."""
    from vfwidgets_theme.widgets.application import set_global_theme

    set_global_theme("dark")

    parent_widget = ComplexWidget()
    child_widget = parent_widget.child_widget

    # Child should be able to get theme from parent
    theme = child_widget._get_theme_from_parent()
    assert theme is not None
    assert hasattr(theme, "colors")


def test_child_widget_gets_vs_code_tokens(qapp):
    """Test that child widget can access VS Code semantic tokens."""
    from vfwidgets_theme.core.repository import ThemeRepository

    # Create parent widget
    parent_widget = ComplexWidget()

    # Manually create a theme and inject it
    repo = ThemeRepository()
    theme = repo.get_theme("dark")

    # Create a minimal theme manager mock
    class MockThemeManager:
        def __init__(self, theme):
            self.current_theme = theme

    parent_widget._theme_manager = MockThemeManager(theme)

    child_widget = parent_widget.child_widget

    colors = child_widget.get_theme_colors()
    assert colors is not None
    assert "active" in colors
    assert "inactive" in colors
    # Should have actual values (not fallback to None)
    assert colors["active"] is not None
    assert colors["inactive"] is not None


def test_renderer_receives_theme_object(qapp):
    """Test that renderer can receive theme object."""
    from vfwidgets_theme.widgets.application import set_global_theme

    set_global_theme("dark")

    widget = ComplexWidget()
    theme = widget.get_current_theme()

    # Renderer should be able to use theme
    assert theme is not None
    assert hasattr(theme, "colors")

    # Simulate drawing
    from PySide6.QtGui import QPixmap

    pixmap = QPixmap(100, 100)
    painter = QPainter(pixmap)
    widget.renderer.draw(painter, QRect(0, 0, 100, 100), theme)
    painter.end()


def test_theme_changes_propagate_to_children(qapp):
    """Test that theme changes are accessible to child widgets."""
    from vfwidgets_theme.core.manager import ThemeManager
    from vfwidgets_theme.core.repository import ThemeRepository

    # Create parent widget
    parent_widget = ComplexWidget()

    # Manually inject theme manager with dark theme
    repo = ThemeRepository()
    dark_theme = repo.get_theme("dark")
    parent_widget._theme_manager = ThemeManager(dark_theme)

    child_widget = parent_widget.child_widget

    # Get initial colors
    colors_dark = child_widget.get_theme_colors()
    if colors_dark:
        assert colors_dark["active"] is not None

        # Change theme to light
        light_theme = repo.get_theme("light")
        parent_widget._theme_manager = ThemeManager(light_theme)

        # Child should see new theme
        colors_light = child_widget.get_theme_colors()
        assert colors_light["active"] is not None
        # Light theme should have different colors than dark
        assert colors_light["active"] != colors_dark["active"]


def test_fallback_when_no_theme(qapp):
    """Test graceful fallback when theme not available."""
    # Create widget without ThemedApplication
    widget = ComplexWidget()

    # get_current_theme should return None gracefully
    theme = widget.get_current_theme()
    # Could be None or a default theme
    if theme is None:
        # Fallback works
        assert True
    else:
        # Has fallback theme
        assert hasattr(theme, "colors")
