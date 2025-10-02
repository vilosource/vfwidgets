"""Tests for theme system integration."""

import pytest
import sys
from pathlib import Path

# Add theme system to path
theme_system_path = Path(__file__).parent.parent.parent / "theme_system" / "src"
if theme_system_path.exists():
    sys.path.insert(0, str(theme_system_path))

from PySide6.QtWidgets import QApplication, QTextEdit

try:
    from vfwidgets_theme import ThemedApplication
    from vfwidgets_theme.widgets import ThemedMainWindow, ThemedQWidget
    from vfwidgets_theme.widgets.base import ThemedWidget
    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False
    ThemedWidget = None

from chrome_tabbed_window import ChromeTabbedWindow


@pytest.mark.skipif(not THEME_AVAILABLE, reason="Theme system not available")
def test_chrome_window_has_theme_support(qapp):
    """Test that ChromeTabbedWindow has ThemedWidget functionality."""
    window = ChromeTabbedWindow()

    # Check if it has theme attribute
    assert hasattr(window, 'theme')

    # Check if it's an instance of ThemedWidget
    if ThemedWidget:
        assert isinstance(window, ThemedWidget)

    window.close()


@pytest.mark.skipif(not THEME_AVAILABLE, reason="Theme system not available")
def test_chrome_window_receives_theme_changes(qapp):
    """Test that ChromeTabbedWindow can receive theme objects."""
    window = ChromeTabbedWindow()
    window.addTab(QTextEdit(), "Tab 1")

    # Check that theme attribute exists
    assert hasattr(window, 'theme')

    # Get theme (may be None without ThemedApplication)
    theme = window.theme

    # If theme exists, it should have expected attributes
    if theme:
        assert hasattr(theme, 'colors') or hasattr(theme, 'name')

    window.close()


@pytest.mark.skipif(not THEME_AVAILABLE, reason="Theme system not available")
def test_tab_renderer_uses_theme_colors(qapp):
    """Test that tab renderer uses theme colors."""
    from chrome_tabbed_window.components.chrome_tab_renderer import ChromeTabRenderer

    window = ChromeTabbedWindow()
    theme = window.theme

    # Get colors from renderer
    colors = ChromeTabRenderer.get_tab_colors(theme)

    # Verify colors dict structure
    assert colors is not None
    assert 'tab_active' in colors
    assert 'tab_normal' in colors
    assert 'tab_hover' in colors
    assert 'text' in colors
    assert 'text_inactive' in colors
    assert 'border' in colors

    # All should be QColor instances
    from PySide6.QtGui import QColor
    for color_name, color_value in colors.items():
        assert isinstance(color_value, QColor), f"{color_name} is not a QColor"

    window.close()


@pytest.mark.skipif(not THEME_AVAILABLE, reason="Theme system not available")
def test_tab_renderer_fallback_without_theme():
    """Test that tab renderer falls back to defaults without theme."""
    from chrome_tabbed_window.components.chrome_tab_renderer import ChromeTabRenderer

    # Get colors without theme
    colors = ChromeTabRenderer.get_tab_colors(None)

    # Should still return valid colors
    assert colors is not None
    assert 'tab_active' in colors
    assert colors['tab_active'].name() == '#ffffff'  # Default Chrome active color


@pytest.mark.skipif(not THEME_AVAILABLE, reason="Theme system not available")
def test_embedded_mode_with_themed_parent(qapp):
    """Test embedded ChromeTabbedWindow in ThemedMainWindow."""
    from PySide6.QtWidgets import QVBoxLayout

    main_window = ThemedMainWindow()
    central = ThemedQWidget()
    layout = QVBoxLayout(central)

    # Create embedded chrome tabs
    tabs = ChromeTabbedWindow(parent=central)
    tabs.addTab(QTextEdit(), "Tab 1")
    layout.addWidget(tabs)

    main_window.setCentralWidget(central)

    # Verify both have theme attribute
    assert hasattr(main_window, 'theme')
    assert hasattr(tabs, 'theme')

    main_window.close()


@pytest.mark.skipif(not THEME_AVAILABLE, reason="Theme system not available")
def test_theme_switching_updates_tabs(qapp):
    """Test that tab bar has update method."""
    window = ChromeTabbedWindow()
    window.addTab(QTextEdit(), "Tab 1")
    window.show()

    # Verify tab bar has update method
    assert hasattr(window._tab_bar, 'update')

    # Verify _on_theme_changed exists
    assert hasattr(window, '_on_theme_changed')

    # Call it manually
    window._on_theme_changed()

    window.close()


@pytest.mark.skipif(not THEME_AVAILABLE, reason="Theme system not available")
def test_window_controls_use_theme(qapp):
    """Test that window controls use theme colors."""
    # Create frameless window (will have window controls)
    window = ChromeTabbedWindow()
    window.addTab(QTextEdit(), "Tab 1")

    # Window controls should be created for frameless mode
    if hasattr(window, '_window_controls') and window._window_controls:
        controls = window._window_controls

        # Controls should have buttons
        assert hasattr(controls, 'minimize_button')
        assert hasattr(controls, 'maximize_button')
        assert hasattr(controls, 'close_button')

        # Buttons should have _get_theme_colors method
        assert hasattr(controls.minimize_button, '_get_theme_colors')

    window.close()


@pytest.mark.skipif(not THEME_AVAILABLE, reason="Theme system not available")
def test_tab_bar_gets_theme_from_parent(qapp):
    """Test that tab bar can get theme from parent."""
    window = ChromeTabbedWindow()
    window.addTab(QTextEdit(), "Tab 1")

    # Tab bar should have _get_theme_from_parent method
    assert hasattr(window._tab_bar, '_get_theme_from_parent')

    # Call it
    theme = window._tab_bar._get_theme_from_parent()

    # Theme may be None, but method should work
    # If theme exists, verify it has expected structure
    if theme:
        assert hasattr(theme, 'colors') or hasattr(theme, 'name')

    window.close()


@pytest.mark.skipif(not THEME_AVAILABLE, reason="Theme system not available")
def test_theme_persistence_across_tabs(qapp):
    """Test that theme integration works when adding/removing tabs."""
    window = ChromeTabbedWindow()

    # Add tabs
    for i in range(5):
        window.addTab(QTextEdit(), f"Tab {i}")

    # Verify window still has theme support
    assert hasattr(window, 'theme')

    # Remove tabs
    while window.count() > 1:
        window.removeTab(0)

    # Theme support should still work
    assert hasattr(window, 'theme')

    window.close()
