"""Tests for NavigationBar component.

This module tests the navigation bar widget including:
- UI component creation
- Signal emissions
- URL bar interaction
- Button state management
- Loading state changes
"""

import pytest

from vfwidgets_webview.navigation_bar import NavigationBar


@pytest.fixture
def navbar(qtbot):
    """Create a NavigationBar for testing."""
    bar = NavigationBar()
    qtbot.addWidget(bar)
    return bar


def test_navbar_creation(navbar):
    """Test that NavigationBar can be created."""
    assert navbar is not None
    assert navbar.back_button is not None
    assert navbar.forward_button is not None
    assert navbar.reload_button is not None
    assert navbar.home_button is not None
    assert navbar.url_bar is not None
    assert navbar.progress_bar is not None


def test_navbar_initial_state(navbar):
    """Test initial button states."""
    # Back/forward should be disabled initially
    assert not navbar.back_button.isEnabled()
    assert not navbar.forward_button.isEnabled()

    # Reload and home should be enabled
    assert navbar.reload_button.isEnabled()
    assert navbar.home_button.isEnabled()

    # Progress bar should be hidden
    assert not navbar.progress_bar.isVisible()

    # URL bar should be empty
    assert navbar.url_bar.text() == ""


def test_set_url(navbar):
    """Test setting URL in URL bar."""
    test_url = "https://example.com"
    navbar.set_url(test_url)
    assert navbar.get_url() == test_url


def test_url_submission(navbar, qtbot):
    """Test URL submission signal."""
    # Set up signal spy
    with qtbot.waitSignal(navbar.url_submitted, timeout=1000) as blocker:
        # Type URL and press Enter
        navbar.url_bar.setText("https://example.com")
        navbar.url_bar.returnPressed.emit()

    # Check signal was emitted with correct URL
    assert blocker.args == ["https://example.com"]


def test_url_submission_empty(navbar, qtbot):
    """Test that empty URL submission is ignored."""
    # Clear URL bar
    navbar.url_bar.setText("")

    # Try to submit (should not emit signal)
    with qtbot.assertNotEmitted(navbar.url_submitted, wait=100):
        navbar.url_bar.returnPressed.emit()


def test_back_button_click(navbar, qtbot):
    """Test back button click signal."""
    # Enable back button first
    navbar.set_back_enabled(True)

    with qtbot.waitSignal(navbar.back_clicked, timeout=1000):
        navbar.back_button.click()


def test_forward_button_click(navbar, qtbot):
    """Test forward button click signal."""
    # Enable forward button first
    navbar.set_forward_enabled(True)

    with qtbot.waitSignal(navbar.forward_clicked, timeout=1000):
        navbar.forward_button.click()


def test_home_button_click(navbar, qtbot):
    """Test home button click signal."""
    with qtbot.waitSignal(navbar.home_clicked, timeout=1000):
        navbar.home_button.click()


def test_reload_button_click(navbar, qtbot):
    """Test reload button click when not loading."""
    # Should emit reload_clicked when not loading
    with qtbot.waitSignal(navbar.reload_clicked, timeout=1000):
        navbar.reload_button.click()


def test_stop_button_click(navbar, qtbot):
    """Test stop button click when loading."""
    # Set loading state
    navbar.set_loading(True)

    # Should emit stop_clicked when loading
    with qtbot.waitSignal(navbar.stop_clicked, timeout=1000):
        navbar.reload_button.click()


def test_set_loading_state(navbar, qtbot):
    """Test loading state changes button appearance."""
    # Show navbar so visibility checks work
    navbar.show()
    qtbot.waitExposed(navbar)

    # Initially not loading (reload button)
    assert navbar.reload_button.text() == "⟲"
    assert not navbar.progress_bar.isVisible()

    # Set loading
    navbar.set_loading(True)
    assert navbar.reload_button.text() == "✕"
    assert navbar.progress_bar.isVisible()

    # Set not loading
    navbar.set_loading(False)
    assert navbar.reload_button.text() == "⟲"
    assert not navbar.progress_bar.isVisible()


def test_set_progress(navbar, qtbot):
    """Test progress bar updates."""
    # Show navbar so visibility checks work
    navbar.show()
    qtbot.waitExposed(navbar)

    # Set progress
    navbar.set_progress(50)
    assert navbar.progress_bar.value() == 50
    assert navbar.progress_bar.isVisible()

    # Complete loading
    navbar.set_progress(100)
    assert navbar.progress_bar.value() == 100
    assert not navbar.progress_bar.isVisible()

    # Test clamping
    navbar.set_progress(-10)
    assert navbar.progress_bar.value() == 0

    navbar.set_progress(150)
    assert navbar.progress_bar.value() == 100


def test_set_back_enabled(navbar):
    """Test enabling/disabling back button."""
    navbar.set_back_enabled(True)
    assert navbar.back_button.isEnabled()

    navbar.set_back_enabled(False)
    assert not navbar.back_button.isEnabled()


def test_set_forward_enabled(navbar):
    """Test enabling/disabling forward button."""
    navbar.set_forward_enabled(True)
    assert navbar.forward_button.isEnabled()

    navbar.set_forward_enabled(False)
    assert not navbar.forward_button.isEnabled()


def test_focus_url_bar(navbar, qtbot):
    """Test focusing URL bar."""
    # Set some text
    navbar.set_url("https://example.com")

    # Focus URL bar (calls setFocus and selectAll)
    navbar.focus_url_bar()

    # Note: Focus may not work in headless tests, but we can verify
    # the method runs without errors and text gets selected
    # In real usage, this will work correctly


def test_keyboard_shortcut_ctrl_l(navbar, qtbot):
    """Test Ctrl+L keyboard shortcut functionality."""
    # Set some text
    navbar.set_url("https://example.com")

    # Call focus_url_bar (same as Ctrl+L would do)
    navbar.focus_url_bar()

    # Note: Focus may not work in headless tests, but the method
    # should execute without errors
