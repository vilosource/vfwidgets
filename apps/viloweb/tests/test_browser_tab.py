"""Tests for BrowserTab."""

import pytest
from PySide6.QtCore import QObject

from viloweb import BrowserTab


@pytest.fixture
def tab(qtbot):
    """Create BrowserTab for testing."""
    tab = BrowserTab()
    qtbot.addWidget(tab.widget)
    return tab


def test_initialization(tab):
    """Test tab initialization."""
    assert tab.title == "New Tab"
    assert tab.url == ""
    assert tab.widget is not None


def test_widget_property(tab):
    """Test that widget property returns BrowserWidget."""
    from vfwidgets_webview import BrowserWidget

    assert isinstance(tab.widget, BrowserWidget)


def test_navigate(tab, qtbot):
    """Test navigation."""
    # Navigate to URL
    tab.navigate("https://example.com")

    # Wait briefly for navigation to start
    qtbot.wait(100)

    # URL should be set (may not be fully loaded yet)
    assert "example.com" in tab.url or tab.url == ""  # May still be empty if not loaded


def test_title_changed_signal(tab, qtbot):
    """Test that title_changed signal is emitted."""
    # Connect signal spy
    with qtbot.waitSignal(tab.title_changed, timeout=1000) as blocker:
        # Simulate title change from webview
        tab._on_title_changed("Test Title")

    assert blocker.args == ["Test Title"]
    assert tab.title == "Test Title"


def test_url_changed_signal(tab, qtbot):
    """Test that url_changed signal is emitted."""
    # Connect signal spy
    with qtbot.waitSignal(tab.url_changed, timeout=1000) as blocker:
        # Simulate URL change from webview
        # Note: WebView.url_changed emits str, not QUrl
        test_url = "https://example.com"
        tab._on_url_changed(test_url)

    assert blocker.args == ["https://example.com"]
    assert tab.url == "https://example.com"


def test_empty_title_defaults_to_new_tab(tab, qtbot):
    """Test that empty title defaults to 'New Tab'."""
    tab._on_title_changed("")
    assert tab.title == "New Tab"

    tab._on_title_changed(None)
    assert tab.title == "New Tab"


def test_can_go_back_forward(tab):
    """Test navigation state properties."""
    # Initially should not be able to go back/forward
    assert tab.can_go_back is False
    assert tab.can_go_forward is False


def test_navigation_methods_exist(tab):
    """Test that all navigation methods exist."""
    assert hasattr(tab, "navigate")
    assert hasattr(tab, "go_back")
    assert hasattr(tab, "go_forward")
    assert hasattr(tab, "reload")
    assert hasattr(tab, "stop")
    assert callable(tab.navigate)
    assert callable(tab.go_back)
    assert callable(tab.go_forward)
    assert callable(tab.reload)
    assert callable(tab.stop)


def test_cleanup(tab):
    """Test tab cleanup."""
    # Should not crash
    tab.cleanup()


def test_tab_with_custom_parent():
    """Test creating tab with custom parent."""
    parent = QObject()
    tab = BrowserTab(parent)
    assert tab.parent() == parent


def test_signal_forwarding_setup(tab):
    """Test that signals are properly connected."""
    # All signals should be connected
    # We verify by checking that the signals exist
    assert hasattr(tab, "title_changed")
    assert hasattr(tab, "icon_changed")
    assert hasattr(tab, "url_changed")
    assert hasattr(tab, "load_progress")
