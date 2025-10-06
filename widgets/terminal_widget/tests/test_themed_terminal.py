"""Test suite for themed TerminalWidget integration."""

import pytest
from vfwidgets_terminal import TerminalWidget
from vfwidgets_theme import ThemedApplication


@pytest.fixture(scope="module")
def app():
    """Create ThemedApplication for tests."""
    app = ThemedApplication([])
    app.set_theme("dark")
    yield app
    app.quit()


def test_terminal_widget_creation(app):
    """Test basic terminal creation with theme integration."""
    terminal = TerminalWidget(command="echo", args=["test"])
    assert terminal is not None
    # Should have theme access if ThemedWidget is integrated
    assert hasattr(terminal, "theme")


def test_terminal_widget_theme_config(app):
    """Test terminal has theme configuration."""
    TerminalWidget(command="echo", args=["test"])
    # Should have theme_config class attribute
    assert hasattr(TerminalWidget, "theme_config")
    assert "background" in TerminalWidget.theme_config
    assert "foreground" in TerminalWidget.theme_config
    # Should map to terminal tokens
    assert TerminalWidget.theme_config["background"] == "terminal.background"
    assert TerminalWidget.theme_config["foreground"] == "terminal.foreground"


def test_terminal_widget_theme_access(app):
    """Test theme token access."""
    terminal = TerminalWidget(command="echo", args=["test"])
    # Should have access to terminal theme tokens
    assert terminal.theme.background is not None
    assert terminal.theme.foreground is not None
    # Cursor tokens may return None if not set in theme, just verify access doesn't raise
    _ = terminal.theme.cursor
    _ = terminal.theme.cursorAccent


def test_terminal_widget_ansi_colors(app):
    """Test ANSI color theme tokens."""
    terminal = TerminalWidget(command="echo", args=["test"])
    # Should have all 16 ANSI colors - test access doesn't raise
    # (actual values may be None if not set in theme)
    _ = terminal.theme.black
    _ = terminal.theme.red
    _ = terminal.theme.green
    _ = terminal.theme.brightBlack
    _ = terminal.theme.brightRed
    # Verify they're all accessible via theme_config
    assert "black" in TerminalWidget.theme_config
    assert "brightRed" in TerminalWidget.theme_config


def test_terminal_widget_on_theme_changed(app):
    """Test on_theme_changed method exists."""
    terminal = TerminalWidget(command="echo", args=["test"])
    assert hasattr(terminal, "on_theme_changed")
    # Should be callable
    assert callable(terminal.on_theme_changed)


def test_terminal_widget_set_theme_compat(app):
    """Test backward compatibility with set_theme()."""
    terminal = TerminalWidget(command="echo", args=["test"])
    # Old set_theme() method should still work
    assert hasattr(terminal, "set_theme")
    # Test that it accepts a dict
    custom_theme = {"background": "#000000", "foreground": "#ffffff"}
    # Should not raise (even if terminal isn't connected yet)
    terminal.set_theme(custom_theme)
    assert terminal._user_theme == custom_theme


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
