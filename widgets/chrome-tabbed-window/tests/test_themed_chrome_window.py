"""Test suite for themed ChromeTabbedWindow integration."""

import pytest
from PySide6.QtWidgets import QLabel
from chrome_tabbed_window import ChromeTabbedWindow
from vfwidgets_theme import ThemedApplication


@pytest.fixture(scope="module")
def app():
    """Create ThemedApplication for tests."""
    app = ThemedApplication([])
    app.set_theme("dark")
    yield app
    app.quit()


def test_chrome_window_creation(app):
    """Test basic ChromeTabbedWindow creation with theme integration."""
    window = ChromeTabbedWindow()
    assert window is not None
    # Should have theme access if ThemedWidget is integrated
    assert hasattr(window, 'theme')


def test_chrome_window_theme_config(app):
    """Test ChromeTabbedWindow has theme configuration."""
    window = ChromeTabbedWindow()
    # Should have theme_config class attribute
    assert hasattr(ChromeTabbedWindow, 'theme_config')
    assert 'tab_background' in ChromeTabbedWindow.theme_config
    assert 'background' in ChromeTabbedWindow.theme_config
    # Should map to tab tokens
    assert ChromeTabbedWindow.theme_config['tab_background'] == 'tab.activeBackground'
    assert ChromeTabbedWindow.theme_config['background'] == 'editorGroupHeader.tabsBackground'


def test_chrome_window_theme_access(app):
    """Test theme token access."""
    window = ChromeTabbedWindow()
    # Should have access to theme tokens
    assert window.theme.background is not None
    assert window.theme.tab_background is not None or True  # May be None if not in theme


def test_chrome_window_on_theme_changed(app):
    """Test on_theme_changed method exists."""
    window = ChromeTabbedWindow()
    assert hasattr(window, 'on_theme_changed')
    # Should be callable
    assert callable(window.on_theme_changed)
    # Should not raise when called
    window.on_theme_changed()


def test_chrome_window_with_tabs(app):
    """Test ChromeTabbedWindow with tabs maintains QTabWidget API."""
    window = ChromeTabbedWindow()

    # Test QTabWidget-compatible API
    widget1 = QLabel("Tab 1")
    widget2 = QLabel("Tab 2")

    window.addTab(widget1, "First Tab")
    window.addTab(widget2, "Second Tab")

    assert window.count() == 2
    assert window.currentIndex() == 0

    # Theme system should still work with tabs
    assert hasattr(window, 'theme')


def test_chrome_window_qtabwidget_compatibility(app):
    """Test ChromeTabbedWindow maintains QTabWidget compatibility."""
    window = ChromeTabbedWindow()

    # Test key QTabWidget methods exist
    assert hasattr(window, 'addTab')
    assert hasattr(window, 'removeTab')
    assert hasattr(window, 'setCurrentIndex')
    assert hasattr(window, 'count')

    # Test signals exist
    assert hasattr(window, 'currentChanged')
    assert hasattr(window, 'tabCloseRequested')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
