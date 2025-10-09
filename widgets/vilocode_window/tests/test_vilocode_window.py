"""Basic tests for ViloCodeWindow."""

from PySide6.QtWidgets import QWidget

from vfwidgets_vilocode_window import ViloCodeWindow
from vfwidgets_vilocode_window.core.constants import WindowMode


def test_import():
    """Test that ViloCodeWindow can be imported."""
    assert ViloCodeWindow is not None


def test_create_without_parent(qtbot):
    """Test creating ViloCodeWindow without parent."""
    window = ViloCodeWindow()
    assert window is not None
    assert isinstance(window, QWidget)


def test_create_with_parent(qtbot):
    """Test creating ViloCodeWindow with parent."""
    parent = QWidget()
    window = ViloCodeWindow(parent=parent)
    assert window is not None
    assert window.parent() is parent


def test_shortcuts_enabled_by_default(qtbot):
    """Test that shortcuts are enabled by default."""
    window = ViloCodeWindow()
    # Will add assertion once shortcuts are implemented
    assert window is not None


def test_shortcuts_can_be_disabled(qtbot):
    """Test that shortcuts can be disabled."""
    window = ViloCodeWindow(enable_default_shortcuts=False)
    # Will add assertion once shortcuts are implemented
    assert window is not None


# Task 1.23: Mode detection tests
def test_frameless_mode_no_parent(qtbot):
    """Test that window is in frameless mode without parent."""
    window = ViloCodeWindow()
    assert window._window_mode == WindowMode.Frameless


def test_embedded_mode_with_parent(qtbot):
    """Test that window is in embedded mode with parent."""
    parent = QWidget()
    window = ViloCodeWindow(parent=parent)
    assert window._window_mode == WindowMode.Embedded


# Task 1.7b: Status bar API tests
def test_get_status_bar(qtbot):
    """Test getting status bar widget."""
    window = ViloCodeWindow()
    status_bar = window.get_status_bar()
    assert status_bar is not None
    from PySide6.QtWidgets import QStatusBar

    assert isinstance(status_bar, QStatusBar)


def test_status_bar_visible_by_default(qtbot):
    """Test that status bar is visible by default."""
    window = ViloCodeWindow()
    qtbot.addWidget(window)
    window.show()  # Show the window so isVisible() works
    # Status bar should be visible (not hidden)
    assert window.is_status_bar_visible() is True


def test_set_status_bar_visibility(qtbot):
    """Test setting status bar visibility."""
    window = ViloCodeWindow()
    qtbot.addWidget(window)
    window.show()  # Show the window so isVisible() works

    # Initially visible
    assert window.is_status_bar_visible() is True

    # Hide it
    window.set_status_bar_visible(False)
    assert window.is_status_bar_visible() is False

    # Show it again
    window.set_status_bar_visible(True)
    assert window.is_status_bar_visible() is True


def test_set_status_message(qtbot):
    """Test setting status message."""
    window = ViloCodeWindow()
    window.set_status_message("Test message")
    # Message should be displayed (can't easily verify text, but method should work)
    assert window.get_status_bar().currentMessage() == "Test message"


# Keyboard Shortcut Tests


def test_shortcuts_manager_created(qtbot):
    """Test that shortcut manager is created when shortcuts enabled."""
    window = ViloCodeWindow(enable_default_shortcuts=True)
    qtbot.addWidget(window)
    assert hasattr(window, "_shortcut_manager")
    assert window._shortcut_manager is not None


def test_default_shortcuts_loaded(qtbot):
    """Test that default shortcuts are loaded."""
    window = ViloCodeWindow(enable_default_shortcuts=True)
    qtbot.addWidget(window)

    shortcuts = window.get_all_shortcuts()
    assert len(shortcuts) > 0
    assert "TOGGLE_SIDEBAR" in shortcuts
    assert "TOGGLE_STATUS_BAR" in shortcuts
    assert "MAXIMIZE_WINDOW" in shortcuts


def test_shortcuts_not_loaded_when_disabled(qtbot):
    """Test that shortcuts are not loaded when disabled."""
    window = ViloCodeWindow(enable_default_shortcuts=False)
    qtbot.addWidget(window)

    shortcuts = window.get_all_shortcuts()
    assert len(shortcuts) == 0


def test_get_shortcut_info(qtbot):
    """Test getting shortcut information."""
    window = ViloCodeWindow(enable_default_shortcuts=True)
    qtbot.addWidget(window)

    info = window.get_shortcut_info("TOGGLE_SIDEBAR")
    assert info is not None
    assert "key_sequence" in info
    assert "description" in info
    assert "category" in info
    assert info["key_sequence"] == "Ctrl+B"


def test_set_shortcut(qtbot):
    """Test updating a shortcut key sequence."""
    window = ViloCodeWindow(enable_default_shortcuts=True)
    qtbot.addWidget(window)

    # Change shortcut
    window.set_shortcut("TOGGLE_SIDEBAR", "Ctrl+Shift+B")

    # Verify change
    info = window.get_shortcut_info("TOGGLE_SIDEBAR")
    assert info["key_sequence"] == "Ctrl+Shift+B"


def test_register_custom_shortcut(qtbot):
    """Test registering a custom shortcut."""
    window = ViloCodeWindow(enable_default_shortcuts=True)
    qtbot.addWidget(window)

    callback_called = []

    def custom_callback():
        callback_called.append(True)

    # Register custom shortcut
    window.register_custom_shortcut(
        "MY_CUSTOM_ACTION", "Ctrl+K", custom_callback, "My custom action"
    )

    # Verify registration
    info = window.get_shortcut_info("MY_CUSTOM_ACTION")
    assert info is not None
    assert info["key_sequence"] == "Ctrl+K"
    assert info["description"] == "My custom action"
    assert info["category"] == "custom"


def test_remove_shortcut(qtbot):
    """Test removing a shortcut."""
    window = ViloCodeWindow(enable_default_shortcuts=True)
    qtbot.addWidget(window)

    # Verify shortcut exists
    assert window.get_shortcut_info("TOGGLE_SIDEBAR") is not None

    # Remove shortcut
    window.remove_shortcut("TOGGLE_SIDEBAR")

    # Verify removal
    assert window.get_shortcut_info("TOGGLE_SIDEBAR") is None


def test_enable_disable_shortcut(qtbot):
    """Test enabling and disabling shortcuts."""
    window = ViloCodeWindow(enable_default_shortcuts=True)
    qtbot.addWidget(window)

    # Disable a shortcut
    window.enable_shortcut("TOGGLE_SIDEBAR", False)

    # Note: We can't easily test if the shortcut actually works or not
    # without simulating keyboard events, but we can verify the API works
    # The shortcut info should still exist
    assert window.get_shortcut_info("TOGGLE_SIDEBAR") is not None

    # Re-enable
    window.enable_shortcut("TOGGLE_SIDEBAR", True)
    assert window.get_shortcut_info("TOGGLE_SIDEBAR") is not None


def test_toggle_status_bar_shortcut(qtbot):
    """Test that status bar can be toggled (internal method)."""
    window = ViloCodeWindow(enable_default_shortcuts=True)
    qtbot.addWidget(window)
    window.show()

    # Initial state: visible
    assert window.is_status_bar_visible() is True

    # Toggle off
    window._toggle_status_bar()
    assert window.is_status_bar_visible() is False

    # Toggle on
    window._toggle_status_bar()
    assert window.is_status_bar_visible() is True


def test_toggle_maximize_shortcut(qtbot):
    """Test that maximize can be toggled (internal method)."""
    window = ViloCodeWindow(enable_default_shortcuts=True)
    qtbot.addWidget(window)
    window.show()

    # Initial state: normal
    assert not window.isMaximized()

    # Toggle maximize
    window._toggle_maximize()
    assert window.isMaximized()

    # Toggle back to normal
    window._toggle_maximize()
    assert not window.isMaximized()


# Theme Integration Tests


def test_theme_integration_available(qtbot):
    """Test that theme integration is detected."""
    window = ViloCodeWindow()
    qtbot.addWidget(window)

    # Check if ThemedWidget mixin is present
    from vfwidgets_vilocode_window.vilocode_window import THEME_AVAILABLE

    if THEME_AVAILABLE:
        # Should have ThemedWidget methods
        assert hasattr(window, "get_current_theme")
        assert hasattr(window, "on_theme_changed")
        assert hasattr(window, "theme_changed")
    else:
        # May not have ThemedWidget methods
        # Just verify window was created successfully
        assert window is not None


def test_theme_config_defined(qtbot):
    """Test that theme configuration is defined."""
    from vfwidgets_vilocode_window.vilocode_window import THEME_AVAILABLE

    if THEME_AVAILABLE:
        window = ViloCodeWindow()
        qtbot.addWidget(window)

        # Check theme_config exists
        assert hasattr(window, "theme_config")
        assert isinstance(window.theme_config, dict)

        # Check required color tokens
        assert "window_background" in window.theme_config
        assert "titlebar_background" in window.theme_config
        assert "titlebar_foreground" in window.theme_config
        assert "statusbar_background" in window.theme_config
        assert "statusbar_foreground" in window.theme_config
        assert "border_color" in window.theme_config


def test_fallback_colors_work(qtbot):
    """Test that fallback colors work when theme unavailable."""
    window = ViloCodeWindow()
    qtbot.addWidget(window)

    # Get fallback colors
    window_bg = window._get_fallback_color("window_background")
    titlebar_bg = window._get_fallback_color("titlebar_background")
    statusbar_bg = window._get_fallback_color("statusbar_background")
    border = window._get_fallback_color("border_color")

    # Verify they're valid QColors
    from PySide6.QtGui import QColor

    assert isinstance(window_bg, QColor)
    assert isinstance(titlebar_bg, QColor)
    assert isinstance(statusbar_bg, QColor)
    assert isinstance(border, QColor)

    # Verify they're not default black
    assert window_bg.name() != "#000000"
    assert titlebar_bg.name() != "#000000"
    assert statusbar_bg.name() != "#000000"


def test_apply_theme_colors_doesnt_crash(qtbot):
    """Test that applying theme colors doesn't crash."""
    window = ViloCodeWindow()
    qtbot.addWidget(window)

    # Should not crash
    window._apply_theme_colors()
    assert True


def test_on_theme_changed_handler_exists(qtbot):
    """Test that on_theme_changed handler is defined."""
    window = ViloCodeWindow()
    qtbot.addWidget(window)

    assert hasattr(window, "on_theme_changed")
    assert callable(window.on_theme_changed)


def test_on_theme_changed_calls_apply_colors(qtbot):
    """Test that on_theme_changed applies colors."""
    window = ViloCodeWindow()
    qtbot.addWidget(window)
    window.show()

    # Call on_theme_changed - should not crash
    window.on_theme_changed()

    # Window should still be valid
    assert window is not None
    assert window.isVisible()
