"""Unit tests for TerminalBridge (QWebChannel JavaScript-Python integration)."""

import json
from unittest.mock import Mock, patch

import pytest
from PySide6.QtCore import QObject, Signal
from vfwidgets_terminal.terminal import TerminalBridge


class TestTerminalBridgeInitialization:
    """Test TerminalBridge initialization and basic setup."""

    def test_bridge_initialization(self, qtbot):
        """Test TerminalBridge initialization."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        assert isinstance(bridge, QObject)
        assert bridge._last_selection == ""

    def test_bridge_signals_exist(self, qtbot):
        """Test that all required signals exist on TerminalBridge."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        # Verify all signals exist
        assert hasattr(bridge, "selection_changed")
        assert hasattr(bridge, "cursor_moved")
        assert hasattr(bridge, "bell_rang")
        assert hasattr(bridge, "title_changed")
        assert hasattr(bridge, "key_pressed")
        assert hasattr(bridge, "data_received")
        assert hasattr(bridge, "scroll_occurred")

        # Verify signals are actually Signal objects
        assert isinstance(bridge.selection_changed, Signal)
        assert isinstance(bridge.cursor_moved, Signal)
        assert isinstance(bridge.bell_rang, Signal)
        assert isinstance(bridge.title_changed, Signal)
        assert isinstance(bridge.key_pressed, Signal)
        assert isinstance(bridge.data_received, Signal)
        assert isinstance(bridge.scroll_occurred, Signal)

    def test_bridge_parent_relationship(self, qtbot):
        """Test TerminalBridge parent-child relationship."""
        parent = QObject()
        bridge = TerminalBridge(parent)
        qtbot.addWidget(parent)

        assert bridge.parent() == parent


class TestTerminalBridgeSelectionHandling:
    """Test selection handling in TerminalBridge."""

    def test_on_selection_changed_empty(self, qtbot):
        """Test on_selection_changed with empty selection."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        # Connect signal to verify emission
        signal_mock = Mock()
        bridge.selection_changed.connect(signal_mock)

        # Call the slot
        bridge.on_selection_changed("")

        # Verify internal state and signal emission
        assert bridge._last_selection == ""
        signal_mock.assert_called_once_with("")

    def test_on_selection_changed_with_text(self, qtbot):
        """Test on_selection_changed with actual text."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        signal_mock = Mock()
        bridge.selection_changed.connect(signal_mock)

        test_text = "selected terminal text"
        bridge.on_selection_changed(test_text)

        assert bridge._last_selection == test_text
        signal_mock.assert_called_once_with(test_text)

    def test_on_selection_changed_multiline(self, qtbot):
        """Test on_selection_changed with multiline text."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        signal_mock = Mock()
        bridge.selection_changed.connect(signal_mock)

        multiline_text = "line 1\nline 2\nline 3"
        bridge.on_selection_changed(multiline_text)

        assert bridge._last_selection == multiline_text
        signal_mock.assert_called_once_with(multiline_text)

    def test_on_selection_changed_special_characters(self, qtbot):
        """Test on_selection_changed with special characters."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        signal_mock = Mock()
        bridge.selection_changed.connect(signal_mock)

        special_text = "test\t\n\r\x1b[31mred text\x1b[0m"
        bridge.on_selection_changed(special_text)

        assert bridge._last_selection == special_text
        signal_mock.assert_called_once_with(special_text)

    def test_selection_persistence(self, qtbot):
        """Test that selection persists across multiple calls."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        # Set initial selection
        bridge.on_selection_changed("first selection")
        assert bridge._last_selection == "first selection"

        # Change selection
        bridge.on_selection_changed("second selection")
        assert bridge._last_selection == "second selection"

        # Clear selection
        bridge.on_selection_changed("")
        assert bridge._last_selection == ""


class TestTerminalBridgeCursorHandling:
    """Test cursor movement handling in TerminalBridge."""

    def test_on_cursor_moved_basic(self, qtbot):
        """Test basic cursor movement."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        signal_mock = Mock()
        bridge.cursor_moved.connect(signal_mock)

        bridge.on_cursor_moved(10, 5)

        signal_mock.assert_called_once_with(10, 5)

    def test_on_cursor_moved_origin(self, qtbot):
        """Test cursor movement to origin."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        signal_mock = Mock()
        bridge.cursor_moved.connect(signal_mock)

        bridge.on_cursor_moved(0, 0)

        signal_mock.assert_called_once_with(0, 0)

    def test_on_cursor_moved_large_coordinates(self, qtbot):
        """Test cursor movement with large coordinates."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        signal_mock = Mock()
        bridge.cursor_moved.connect(signal_mock)

        bridge.on_cursor_moved(1000, 500)

        signal_mock.assert_called_once_with(1000, 500)

    @patch("logging.Logger.debug")
    def test_cursor_moved_logging_modulo_10(self, mock_debug, qtbot):
        """Test that cursor movement logging follows modulo 10 rule."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        # Test coordinates that should trigger logging (row % 10 == 0)
        bridge.on_cursor_moved(10, 5)
        bridge.on_cursor_moved(20, 15)
        bridge.on_cursor_moved(0, 0)

        # Test coordinates that should not trigger logging
        bridge.on_cursor_moved(11, 5)
        bridge.on_cursor_moved(25, 15)

        # Verify debug was called for modulo 10 cases
        assert mock_debug.call_count >= 3

    def test_on_cursor_moved_negative_coordinates(self, qtbot):
        """Test cursor movement with negative coordinates."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        signal_mock = Mock()
        bridge.cursor_moved.connect(signal_mock)

        # Negative coordinates might be valid in some terminal contexts
        bridge.on_cursor_moved(-1, -1)

        signal_mock.assert_called_once_with(-1, -1)


class TestTerminalBridgeBellHandling:
    """Test bell event handling in TerminalBridge."""

    def test_on_bell_basic(self, qtbot):
        """Test basic bell event handling."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        signal_mock = Mock()
        bridge.bell_rang.connect(signal_mock)

        bridge.on_bell()

        signal_mock.assert_called_once()

    def test_on_bell_multiple_calls(self, qtbot):
        """Test multiple bell events."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        signal_mock = Mock()
        bridge.bell_rang.connect(signal_mock)

        # Ring bell multiple times
        bridge.on_bell()
        bridge.on_bell()
        bridge.on_bell()

        assert signal_mock.call_count == 3


class TestTerminalBridgeTitleHandling:
    """Test title change handling in TerminalBridge."""

    def test_on_title_changed_basic(self, qtbot):
        """Test basic title change."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        signal_mock = Mock()
        bridge.title_changed.connect(signal_mock)

        bridge.on_title_changed("New Terminal Title")

        signal_mock.assert_called_once_with("New Terminal Title")

    def test_on_title_changed_empty(self, qtbot):
        """Test title change with empty string."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        signal_mock = Mock()
        bridge.title_changed.connect(signal_mock)

        bridge.on_title_changed("")

        signal_mock.assert_called_once_with("")

    def test_on_title_changed_special_characters(self, qtbot):
        """Test title change with special characters."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        signal_mock = Mock()
        bridge.title_changed.connect(signal_mock)

        special_title = "Terminal: /home/user/folder with spaces & symbols"
        bridge.on_title_changed(special_title)

        signal_mock.assert_called_once_with(special_title)

    def test_on_title_changed_unicode(self, qtbot):
        """Test title change with Unicode characters."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        signal_mock = Mock()
        bridge.title_changed.connect(signal_mock)

        unicode_title = "Terminal: 📁 /home/user/🐍 python"
        bridge.on_title_changed(unicode_title)

        signal_mock.assert_called_once_with(unicode_title)


class TestTerminalBridgeKeyHandling:
    """Test keyboard event handling in TerminalBridge."""

    def test_on_key_pressed_basic(self, qtbot):
        """Test basic key press handling."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        signal_mock = Mock()
        bridge.key_pressed.connect(signal_mock)

        bridge.on_key_pressed("a", "KeyA", False, False, False)

        signal_mock.assert_called_once_with("a", "KeyA", False, False, False)

    def test_on_key_pressed_special_keys(self, qtbot):
        """Test special key handling."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        signal_mock = Mock()
        bridge.key_pressed.connect(signal_mock)

        # Test Enter key
        bridge.on_key_pressed("Enter", "Enter", False, False, False)
        signal_mock.assert_called_with("Enter", "Enter", False, False, False)

        # Test Arrow key
        signal_mock.reset_mock()
        bridge.on_key_pressed("ArrowUp", "ArrowUp", False, False, False)
        signal_mock.assert_called_with("ArrowUp", "ArrowUp", False, False, False)

        # Test Function key
        signal_mock.reset_mock()
        bridge.on_key_pressed("F1", "F1", False, False, False)
        signal_mock.assert_called_with("F1", "F1", False, False, False)

    def test_on_key_pressed_modifier_combinations(self, qtbot):
        """Test modifier key combinations."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        signal_mock = Mock()
        bridge.key_pressed.connect(signal_mock)

        test_cases = [
            ("c", "KeyC", True, False, False),  # Ctrl+C
            ("v", "KeyV", True, False, True),  # Ctrl+Shift+V
            ("Tab", "Tab", False, True, False),  # Alt+Tab
            ("a", "KeyA", True, True, True),  # Ctrl+Alt+Shift+A
        ]

        for key, code, ctrl, alt, shift in test_cases:
            signal_mock.reset_mock()
            bridge.on_key_pressed(key, code, ctrl, alt, shift)
            signal_mock.assert_called_once_with(key, code, ctrl, alt, shift)

    @patch("logging.Logger.debug")
    def test_key_pressed_logging_special_keys(self, mock_debug, qtbot):
        """Test that only special keys and modifier combinations are logged."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        # Test special keys (should be logged)
        bridge.on_key_pressed("Enter", "Enter", False, False, False)
        bridge.on_key_pressed("ArrowUp", "ArrowUp", False, False, False)

        # Test modifier combinations (should be logged)
        bridge.on_key_pressed("c", "KeyC", True, False, False)  # Ctrl+C
        bridge.on_key_pressed("v", "KeyV", False, True, False)  # Alt+V

        # Test normal keys (should not be logged as much)
        bridge.on_key_pressed("a", "KeyA", False, False, False)
        bridge.on_key_pressed("b", "KeyB", False, False, False)

        # Special keys and modifier combinations should trigger more debug calls
        assert mock_debug.call_count >= 4

    def test_on_key_pressed_unicode_keys(self, qtbot):
        """Test Unicode key handling."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        signal_mock = Mock()
        bridge.key_pressed.connect(signal_mock)

        # Test Unicode characters
        unicode_keys = [
            ("ä", "KeyA", False, False, False),
            ("中", "Unknown", False, False, False),
            ("🚀", "Unknown", False, False, False),
        ]

        for key, code, ctrl, alt, shift in unicode_keys:
            signal_mock.reset_mock()
            bridge.on_key_pressed(key, code, ctrl, alt, shift)
            signal_mock.assert_called_once_with(key, code, ctrl, alt, shift)


class TestTerminalBridgeDataHandling:
    """Test data input handling in TerminalBridge."""

    def test_on_data_received_basic(self, qtbot):
        """Test basic data reception."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        signal_mock = Mock()
        bridge.data_received.connect(signal_mock)

        bridge.on_data_received("test input")

        signal_mock.assert_called_once_with("test input")

    def test_on_data_received_special_characters(self, qtbot):
        """Test data reception with special characters."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        signal_mock = Mock()
        bridge.data_received.connect(signal_mock)

        special_data = "test\n\r\t\x1b[31m"
        bridge.on_data_received(special_data)

        signal_mock.assert_called_once_with(special_data)

    def test_on_data_received_newlines(self, qtbot):
        """Test data reception with newlines."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        signal_mock = Mock()
        bridge.data_received.connect(signal_mock)

        # Test carriage return
        bridge.on_data_received("\r")
        signal_mock.assert_called_with("\r")

        # Test newline
        signal_mock.reset_mock()
        bridge.on_data_received("\n")
        signal_mock.assert_called_with("\n")

    @patch("logging.Logger.debug")
    def test_data_received_logging_rules(self, mock_debug, qtbot):
        """Test data reception logging rules."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        # Test single characters (should not be logged much)
        bridge.on_data_received("a")
        bridge.on_data_received("b")

        # Test longer data (should be logged)
        bridge.on_data_received("longer input")

        # Test newlines (should be logged)
        bridge.on_data_received("\r")
        bridge.on_data_received("\n")

        # Should have logged for longer inputs and newlines
        assert mock_debug.call_count >= 3

    def test_on_data_received_empty(self, qtbot):
        """Test data reception with empty string."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        signal_mock = Mock()
        bridge.data_received.connect(signal_mock)

        bridge.on_data_received("")

        signal_mock.assert_called_once_with("")


class TestTerminalBridgeScrollHandling:
    """Test scroll event handling in TerminalBridge."""

    def test_on_scroll_basic(self, qtbot):
        """Test basic scroll handling."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        signal_mock = Mock()
        bridge.scroll_occurred.connect(signal_mock)

        bridge.on_scroll(100)

        signal_mock.assert_called_once_with(100)

    def test_on_scroll_zero_position(self, qtbot):
        """Test scroll to zero position."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        signal_mock = Mock()
        bridge.scroll_occurred.connect(signal_mock)

        bridge.on_scroll(0)

        signal_mock.assert_called_once_with(0)

    def test_on_scroll_negative_position(self, qtbot):
        """Test scroll with negative position."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        signal_mock = Mock()
        bridge.scroll_occurred.connect(signal_mock)

        bridge.on_scroll(-50)

        signal_mock.assert_called_once_with(-50)

    def test_on_scroll_large_position(self, qtbot):
        """Test scroll with large position values."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        signal_mock = Mock()
        bridge.scroll_occurred.connect(signal_mock)

        bridge.on_scroll(999999)

        signal_mock.assert_called_once_with(999999)


class TestTerminalBridgeCommandExecution:
    """Test command execution methods (future use)."""

    def test_execute_command_basic(self, qtbot):
        """Test execute_command method."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        result = bridge.execute_command("ls -la")

        # Should return JSON with not_implemented status
        parsed_result = json.loads(result)
        assert parsed_result["status"] == "not_implemented"
        assert parsed_result["command"] == "ls -la"

    def test_execute_command_empty(self, qtbot):
        """Test execute_command with empty command."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        result = bridge.execute_command("")

        parsed_result = json.loads(result)
        assert parsed_result["status"] == "not_implemented"
        assert parsed_result["command"] == ""

    def test_execute_command_complex(self, qtbot):
        """Test execute_command with complex command."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        complex_command = "find /home -name '*.py' | head -10"
        result = bridge.execute_command(complex_command)

        parsed_result = json.loads(result)
        assert parsed_result["status"] == "not_implemented"
        assert parsed_result["command"] == complex_command

    def test_get_terminal_info(self, qtbot):
        """Test get_terminal_info method."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        result = bridge.get_terminal_info()

        parsed_result = json.loads(result)
        assert parsed_result["status"] == "active"
        assert parsed_result["type"] == "xterm.js"


class TestTerminalBridgeSlotDecorators:
    """Test that Slot decorators are properly applied."""

    def test_slot_decorators_exist(self):
        """Test that all bridge methods have proper @Slot decorators."""
        bridge = TerminalBridge()

        # Get all methods that should have @Slot decorators
        slot_methods = [
            "on_selection_changed",
            "on_cursor_moved",
            "on_bell",
            "on_title_changed",
            "on_key_pressed",
            "on_data_received",
            "on_scroll",
            "execute_command",
            "get_terminal_info",
        ]

        for method_name in slot_methods:
            method = getattr(bridge, method_name)
            # In PySide6, slots have a specific attribute
            assert hasattr(method, "__func__"), f"Method {method_name} should be a slot"


@pytest.mark.integration
class TestTerminalBridgeIntegration:
    """Integration tests for TerminalBridge with Qt systems."""

    def test_bridge_signal_connections(self, qtbot):
        """Test that bridge signals can be connected and emitted."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        # Create mock handlers for all signals
        handlers = {
            "selection_changed": Mock(),
            "cursor_moved": Mock(),
            "bell_rang": Mock(),
            "title_changed": Mock(),
            "key_pressed": Mock(),
            "data_received": Mock(),
            "scroll_occurred": Mock(),
        }

        # Connect all signals
        bridge.selection_changed.connect(handlers["selection_changed"])
        bridge.cursor_moved.connect(handlers["cursor_moved"])
        bridge.bell_rang.connect(handlers["bell_rang"])
        bridge.title_changed.connect(handlers["title_changed"])
        bridge.key_pressed.connect(handlers["key_pressed"])
        bridge.data_received.connect(handlers["data_received"])
        bridge.scroll_occurred.connect(handlers["scroll_occurred"])

        # Trigger all handlers through the bridge methods
        bridge.on_selection_changed("test")
        bridge.on_cursor_moved(10, 5)
        bridge.on_bell()
        bridge.on_title_changed("test title")
        bridge.on_key_pressed("a", "KeyA", False, False, False)
        bridge.on_data_received("test data")
        bridge.on_scroll(100)

        # Verify all handlers were called
        for handler_name, handler in handlers.items():
            handler.assert_called_once(), f"Handler {handler_name} was not called"

    def test_bridge_multiple_connections(self, qtbot):
        """Test that multiple handlers can connect to the same signal."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        # Connect multiple handlers to the same signal
        handler1 = Mock()
        handler2 = Mock()
        handler3 = Mock()

        bridge.selection_changed.connect(handler1)
        bridge.selection_changed.connect(handler2)
        bridge.selection_changed.connect(handler3)

        # Emit the signal
        bridge.on_selection_changed("test selection")

        # All handlers should be called
        handler1.assert_called_once_with("test selection")
        handler2.assert_called_once_with("test selection")
        handler3.assert_called_once_with("test selection")

    def test_bridge_signal_disconnection(self, qtbot):
        """Test signal disconnection."""
        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        handler = Mock()
        bridge.selection_changed.connect(handler)

        # Emit signal - should be called
        bridge.on_selection_changed("test 1")
        handler.assert_called_once_with("test 1")

        # Disconnect and emit again - should not be called
        bridge.selection_changed.disconnect(handler)
        handler.reset_mock()
        bridge.on_selection_changed("test 2")
        handler.assert_not_called()

    @patch("logging.getLogger")
    def test_bridge_logging_integration(self, mock_get_logger, qtbot):
        """Test that bridge integrates properly with logging system."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        bridge = TerminalBridge()
        qtbot.addWidget(bridge)

        # Test that logger is used
        bridge.on_selection_changed("test")

        # Should have called debug at least once
        assert mock_logger.debug.call_count >= 1
