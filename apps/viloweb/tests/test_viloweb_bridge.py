"""Tests for ViloWebBridge."""

import pytest
from PySide6.QtCore import QObject

from viloweb import ViloWebBridge


@pytest.fixture
def bridge(qtbot):
    """Create ViloWebBridge for testing."""
    bridge = ViloWebBridge()
    # Note: Bridge is QObject, not QWidget, so we don't add to qtbot
    return bridge


def test_initialization(bridge):
    """Test bridge initialization."""
    assert isinstance(bridge, QObject)


def test_log_from_js(bridge, qtbot):
    """Test logging from JavaScript."""
    # Connect signal spy
    with qtbot.waitSignal(bridge.log_message, timeout=1000) as blocker:
        bridge.log_from_js("info", "Test message")

    assert blocker.args == ["info", "Test message"]


def test_bookmark_requested_signal(bridge, qtbot):
    """Test bookmark request signal."""
    # Connect signal spy
    with qtbot.waitSignal(bridge.bookmark_requested, timeout=1000) as blocker:
        bridge.bookmark_current_page()

    assert blocker.signal_triggered


def test_can_execute_command_allowed(bridge):
    """Test can_execute_command with allowed commands."""
    assert bridge.can_execute_command("bookmark") is True
    assert bridge.can_execute_command("log") is True
    assert bridge.can_execute_command("theme_info") is True


def test_can_execute_command_denied(bridge):
    """Test can_execute_command with disallowed commands."""
    assert bridge.can_execute_command("dangerous_command") is False
    assert bridge.can_execute_command("") is False


def test_get_bridge_version(bridge):
    """Test getting bridge version."""
    version = bridge.get_bridge_version()
    assert isinstance(version, str)
    assert len(version) > 0


def test_get_browser_info(bridge):
    """Test getting browser info."""
    import json

    info_json = bridge.get_browser_info()
    info = json.loads(info_json)

    assert "browser" in info
    assert "version" in info
    assert "engine" in info
    assert "bridge_version" in info

    assert info["browser"] == "ViloWeb"
    assert info["engine"] == "Qt WebEngine"


def test_inject_page_script(bridge):
    """Test script injection request (just logs for MVP)."""
    # Should not crash
    bridge.inject_page_script("test_script")


def test_shutdown(bridge):
    """Test bridge shutdown."""
    # Should not crash
    bridge.shutdown()


def test_bridge_with_custom_parent():
    """Test creating bridge with custom parent."""
    parent = QObject()
    bridge = ViloWebBridge(parent)
    assert bridge.parent() == parent


def test_signals_exist(bridge):
    """Test that all signals exist."""
    assert hasattr(bridge, "bookmark_requested")
    assert hasattr(bridge, "log_message")


def test_slots_exist(bridge):
    """Test that all slot methods exist."""
    assert hasattr(bridge, "log_from_js")
    assert hasattr(bridge, "bookmark_current_page")
    assert hasattr(bridge, "can_execute_command")
    assert hasattr(bridge, "get_bridge_version")
    assert hasattr(bridge, "get_browser_info")
    assert hasattr(bridge, "inject_page_script")

    assert callable(bridge.log_from_js)
    assert callable(bridge.bookmark_current_page)
    assert callable(bridge.can_execute_command)
    assert callable(bridge.get_bridge_version)
    assert callable(bridge.get_browser_info)
    assert callable(bridge.inject_page_script)


def test_log_levels(bridge, qtbot):
    """Test different log levels."""
    levels = ["debug", "info", "warning", "error"]

    for level in levels:
        with qtbot.waitSignal(bridge.log_message, timeout=1000):
            bridge.log_from_js(level, f"Test {level} message")
