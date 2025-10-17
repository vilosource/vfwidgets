"""Tests for BrowserWidget - the complete browser.

This module tests the full browser widget that combines NavigationBar and WebView.
"""

import pytest

from vfwidgets_webview import BrowserWidget


@pytest.fixture
def browser(qtbot):
    """Create a BrowserWidget for testing."""
    widget = BrowserWidget(home_url="https://test.example.com")
    qtbot.addWidget(widget)
    return widget


def test_browser_creation(browser):
    """Test that BrowserWidget can be created."""
    assert browser is not None
    assert browser.navbar is not None
    assert browser.webview is not None


def test_browser_initial_state(browser):
    """Test initial browser state."""
    # Should have configured home URL
    assert browser._home_url == "https://test.example.com"

    # URL should be empty initially
    assert browser.get_url() == ""

    # Title should be empty or "Untitled"
    title = browser.get_title()
    assert title == "" or title == "Untitled"


def test_browser_navigate(browser, qtbot):
    """Test navigation using browser API."""
    # Use signal spy to verify navigation starts
    with qtbot.waitSignal(browser.load_started, timeout=1000):
        browser.navigate("https://example.com")


def test_browser_home(browser, qtbot):
    """Test home button functionality."""
    # Navigate to home should trigger load_started
    with qtbot.waitSignal(browser.load_started, timeout=1000):
        browser.home()


def test_browser_reload(browser):
    """Test reload functionality."""
    # Reload should not crash even with no page loaded
    browser.reload()


def test_browser_stop(browser):
    """Test stop functionality."""
    # Stop should not crash even with no page loading
    browser.stop()


def test_browser_navigation_api(browser):
    """Test navigation API methods."""
    # These should not crash
    browser.back()
    browser.forward()
    browser.reload()
    browser.stop()


def test_browser_url_bar_focus(browser):
    """Test focusing URL bar."""
    # Should not crash
    browser.focus_url_bar()


def test_browser_set_home_url(browser):
    """Test changing home URL."""
    new_home = "https://new-home.example.com"
    browser.set_home_url(new_home)
    assert browser._home_url == new_home


def test_browser_signals_forwarded(browser, qtbot):
    """Test that webview signals are forwarded to browser."""
    # Track signal emissions
    load_started_count = []
    load_progress_values = []
    load_finished_results = []
    url_changes = []
    title_changes = []

    browser.load_started.connect(lambda: load_started_count.append(True))
    browser.load_progress.connect(lambda p: load_progress_values.append(p))
    browser.load_finished.connect(lambda s: load_finished_results.append(s))
    browser.url_changed.connect(lambda u: url_changes.append(u))
    browser.title_changed.connect(lambda t: title_changes.append(t))

    # Navigate to trigger signals
    browser.navigate("https://example.com")

    # Wait a bit for signals
    qtbot.wait(100)

    # At minimum, load_started should have been emitted
    assert len(load_started_count) > 0


def test_browser_navbar_integration(browser, qtbot):
    """Test that navbar and webview are properly connected."""
    # When navbar URL is submitted, webview should start loading
    with qtbot.waitSignal(browser.load_started, timeout=1000):
        # Simulate user typing URL and pressing Enter
        browser.navbar.url_bar.setText("https://example.com")
        browser.navbar.url_bar.returnPressed.emit()


def test_browser_navbar_buttons(browser, qtbot):
    """Test that navbar buttons trigger correct actions."""
    # Enable buttons (they start disabled)
    browser.navbar.set_back_enabled(True)
    browser.navbar.set_forward_enabled(True)

    # Clicking buttons should not crash
    browser.navbar.back_button.click()
    browser.navbar.forward_button.click()
    browser.navbar.reload_button.click()
    browser.navbar.home_button.click()


def test_browser_layout(browser):
    """Test that browser has correct layout."""
    # Browser should have a layout
    assert browser.layout() is not None

    # Layout should contain navbar and webview
    layout = browser.layout()
    assert layout.count() == 2  # navbar + webview

    # First widget should be navbar
    assert layout.itemAt(0).widget() == browser.navbar

    # Second widget should be webview
    assert layout.itemAt(1).widget() == browser.webview
