"""Unit tests for the modern event system (ProcessEvent, KeyEvent, ContextMenuEvent)."""

from datetime import datetime
from unittest.mock import Mock

import pytest
from PySide6.QtCore import QPoint
from vfwidgets_terminal import (
    ContextMenuEvent,
    EventCategory,
    EventConfig,
    KeyEvent,
    ProcessEvent,
    TerminalWidget,
)


class TestProcessEvent:
    """Test ProcessEvent data class."""

    def test_process_event_creation(self):
        """Test ProcessEvent initialization."""
        event = ProcessEvent(command="bash", pid=1234, working_directory="/tmp")

        assert event.command == "bash"
        assert event.pid == 1234
        assert event.working_directory == "/tmp"
        assert isinstance(event.timestamp, datetime)

    def test_process_event_with_defaults(self):
        """Test ProcessEvent with default values."""
        event = ProcessEvent(command="test")

        assert event.command == "test"
        assert event.pid is None
        assert event.working_directory is None
        assert isinstance(event.timestamp, datetime)

    def test_process_event_auto_timestamp(self):
        """Test ProcessEvent automatically sets timestamp."""
        event1 = ProcessEvent(command="test1")
        event2 = ProcessEvent(command="test2")

        # Timestamps should be different (even if very close)
        assert (
            event1.timestamp != event2.timestamp or event1.timestamp == event2.timestamp
        )
        assert isinstance(event1.timestamp, datetime)
        assert isinstance(event2.timestamp, datetime)

    def test_process_event_custom_timestamp(self):
        """Test ProcessEvent with custom timestamp."""
        custom_time = datetime(2023, 1, 1, 12, 0, 0)
        event = ProcessEvent(command="test", timestamp=custom_time)

        assert event.timestamp == custom_time

    def test_process_event_repr(self):
        """Test ProcessEvent string representation."""
        event = ProcessEvent(command="test", pid=1234)
        repr_str = repr(event)

        assert "ProcessEvent" in repr_str
        assert "test" in repr_str
        assert "1234" in repr_str


class TestKeyEvent:
    """Test KeyEvent data class."""

    def test_key_event_creation(self):
        """Test KeyEvent initialization."""
        event = KeyEvent(key="Enter", code="Enter", ctrl=True, alt=False, shift=True)

        assert event.key == "Enter"
        assert event.code == "Enter"
        assert event.ctrl is True
        assert event.alt is False
        assert event.shift is True
        assert isinstance(event.timestamp, datetime)

    def test_key_event_special_keys(self):
        """Test KeyEvent with special keys."""
        # Test arrow key
        arrow_event = KeyEvent(
            key="ArrowUp", code="ArrowUp", ctrl=False, alt=False, shift=False
        )
        assert arrow_event.key == "ArrowUp"

        # Test function key
        f_key_event = KeyEvent(key="F1", code="F1", ctrl=False, alt=False, shift=False)
        assert f_key_event.key == "F1"

        # Test modifier combinations
        combo_event = KeyEvent(key="c", code="KeyC", ctrl=True, alt=True, shift=False)
        assert combo_event.ctrl and combo_event.alt
        assert not combo_event.shift

    def test_key_event_auto_timestamp(self):
        """Test KeyEvent automatically sets timestamp."""
        event = KeyEvent(key="a", code="KeyA", ctrl=False, alt=False, shift=False)
        assert isinstance(event.timestamp, datetime)

    def test_key_event_modifier_combinations(self):
        """Test various modifier key combinations."""
        test_cases = [
            (True, True, True),  # Ctrl+Alt+Shift
            (True, False, False),  # Ctrl only
            (False, True, False),  # Alt only
            (False, False, True),  # Shift only
            (False, False, False),  # No modifiers
        ]

        for ctrl, alt, shift in test_cases:
            event = KeyEvent(key="test", code="test", ctrl=ctrl, alt=alt, shift=shift)
            assert event.ctrl == ctrl
            assert event.alt == alt
            assert event.shift == shift


class TestContextMenuEvent:
    """Test ContextMenuEvent data class."""

    def test_context_menu_event_creation(self):
        """Test ContextMenuEvent initialization."""
        position = QPoint(100, 200)
        global_position = QPoint(500, 600)

        event = ContextMenuEvent(
            position=position,
            global_position=global_position,
            selected_text="test selection",
            cursor_position=(10, 5),
        )

        assert event.position == position
        assert event.global_position == global_position
        assert event.selected_text == "test selection"
        assert event.cursor_position == (10, 5)
        assert isinstance(event.timestamp, datetime)

    def test_context_menu_event_with_defaults(self):
        """Test ContextMenuEvent with default values."""
        position = QPoint(50, 75)
        event = ContextMenuEvent(position=position)

        assert event.position == position
        assert event.global_position is None
        assert event.selected_text == ""
        assert event.cursor_position is None
        assert isinstance(event.timestamp, datetime)

    def test_context_menu_event_empty_selection(self):
        """Test ContextMenuEvent with no text selected."""
        event = ContextMenuEvent(position=QPoint(0, 0), selected_text="")

        assert event.selected_text == ""

    def test_context_menu_event_long_selection(self):
        """Test ContextMenuEvent with long selected text."""
        long_text = "This is a very long selection " * 10
        event = ContextMenuEvent(position=QPoint(0, 0), selected_text=long_text)

        assert event.selected_text == long_text


class TestEventCategory:
    """Test EventCategory enum."""

    def test_event_category_values(self):
        """Test EventCategory enum values."""
        assert EventCategory.LIFECYCLE.value == "lifecycle"
        assert EventCategory.PROCESS.value == "process"
        assert EventCategory.CONTENT.value == "content"
        assert EventCategory.INTERACTION.value == "interaction"
        assert EventCategory.FOCUS.value == "focus"
        assert EventCategory.APPEARANCE.value == "appearance"

    def test_event_category_completeness(self):
        """Test that all expected categories are present."""
        expected_categories = {
            "lifecycle",
            "process",
            "content",
            "interaction",
            "focus",
            "appearance",
        }

        actual_categories = {category.value for category in EventCategory}
        assert actual_categories == expected_categories

    def test_event_category_in_set(self):
        """Test EventCategory can be used in sets."""
        category_set = {
            EventCategory.LIFECYCLE,
            EventCategory.PROCESS,
            EventCategory.INTERACTION,
        }

        assert EventCategory.LIFECYCLE in category_set
        assert EventCategory.CONTENT not in category_set
        assert len(category_set) == 3


class TestEventConfig:
    """Test EventConfig data class."""

    def test_event_config_default(self):
        """Test EventConfig with default values."""
        config = EventConfig()

        # All categories should be enabled by default
        assert config.enabled_categories == set(EventCategory)
        assert config.throttle_high_frequency is True
        assert config.debug_logging is False
        assert config.enable_deprecation_warnings is True

    def test_event_config_custom(self):
        """Test EventConfig with custom values."""
        custom_categories = {EventCategory.LIFECYCLE, EventCategory.PROCESS}

        config = EventConfig(
            enabled_categories=custom_categories,
            throttle_high_frequency=False,
            debug_logging=True,
            enable_deprecation_warnings=False,
        )

        assert config.enabled_categories == custom_categories
        assert config.throttle_high_frequency is False
        assert config.debug_logging is True
        assert config.enable_deprecation_warnings is False

    def test_event_config_empty_categories(self):
        """Test EventConfig with no categories enabled."""
        config = EventConfig(enabled_categories=set())

        assert config.enabled_categories == set()
        # Other defaults should remain
        assert config.throttle_high_frequency is True

    def test_event_config_all_categories(self):
        """Test EventConfig with all categories explicitly set."""
        all_categories = set(EventCategory)
        config = EventConfig(enabled_categories=all_categories)

        assert config.enabled_categories == all_categories

    def test_event_config_post_init(self):
        """Test EventConfig post_init behavior."""
        # Test None gets converted to all categories
        config = EventConfig(enabled_categories=None)
        assert config.enabled_categories == set(EventCategory)


class TestTerminalWidgetEventSystem:
    """Test TerminalWidget integration with the modern event system."""

    def test_terminal_widget_event_config_default(self, basic_terminal_widget):
        """Test TerminalWidget has default event configuration."""
        widget = basic_terminal_widget

        assert isinstance(widget.event_config, EventConfig)
        assert widget.event_config.enabled_categories == set(EventCategory)

    def test_terminal_widget_event_config_custom(self, qtbot, mock_embedded_server):
        """Test TerminalWidget with custom event configuration."""
        custom_config = EventConfig(
            enabled_categories={EventCategory.LIFECYCLE, EventCategory.PROCESS},
            debug_logging=True,
        )

        widget = TerminalWidget(event_config=custom_config)
        qtbot.addWidget(widget)

        assert widget.event_config == custom_config
        assert widget.event_config.debug_logging is True

    def test_configure_events_method(self, basic_terminal_widget):
        """Test TerminalWidget.configure_events() method."""
        widget = basic_terminal_widget

        new_config = EventConfig(
            enabled_categories={EventCategory.INTERACTION},
            throttle_high_frequency=False,
        )

        widget.configure_events(new_config)

        assert widget.event_config == new_config
        assert widget.event_config.enabled_categories == {EventCategory.INTERACTION}

    def test_enable_event_category_method(self, basic_terminal_widget):
        """Test TerminalWidget.enable_event_category() method."""
        widget = basic_terminal_widget

        # Start with no categories
        widget.event_config.enabled_categories = set()

        widget.enable_event_category(EventCategory.LIFECYCLE)
        assert EventCategory.LIFECYCLE in widget.event_config.enabled_categories

        widget.enable_event_category(EventCategory.PROCESS)
        assert EventCategory.PROCESS in widget.event_config.enabled_categories
        assert len(widget.event_config.enabled_categories) == 2

    def test_disable_event_category_method(self, basic_terminal_widget):
        """Test TerminalWidget.disable_event_category() method."""
        widget = basic_terminal_widget

        # Start with all categories
        widget.event_config.enabled_categories = set(EventCategory)

        widget.disable_event_category(EventCategory.FOCUS)
        assert EventCategory.FOCUS not in widget.event_config.enabled_categories
        assert len(widget.event_config.enabled_categories) == len(EventCategory) - 1

    @pytest.mark.gui
    def test_qt_compliant_signals_exist(self, basic_terminal_widget):
        """Test that all Qt-compliant signals exist on TerminalWidget."""
        widget = basic_terminal_widget

        # Lifecycle signals
        assert hasattr(widget, "terminalReady")
        assert hasattr(widget, "terminalClosed")
        assert hasattr(widget, "serverStarted")

        # Process signals
        assert hasattr(widget, "processStarted")
        assert hasattr(widget, "processFinished")

        # Content signals
        assert hasattr(widget, "outputReceived")
        assert hasattr(widget, "inputSent")

        # Interaction signals
        assert hasattr(widget, "keyPressed")
        assert hasattr(widget, "selectionChanged")
        assert hasattr(widget, "contextMenuRequested")

        # Focus signals
        assert hasattr(widget, "focusReceived")
        assert hasattr(widget, "focusLost")

        # Appearance signals
        assert hasattr(widget, "sizeChanged")
        assert hasattr(widget, "titleChanged")
        assert hasattr(widget, "bellActivated")

    @pytest.mark.gui
    def test_deprecated_signals_exist(self, basic_terminal_widget):
        """Test that deprecated signals still exist for backwards compatibility."""
        widget = basic_terminal_widget

        # Test a few key deprecated signals
        assert hasattr(widget, "terminal_ready")
        assert hasattr(widget, "command_started")
        assert hasattr(widget, "output_received")
        assert hasattr(widget, "key_pressed")
        assert hasattr(widget, "context_menu_requested")

    @pytest.mark.gui
    def test_signal_forwarding_setup(self, basic_terminal_widget):
        """Test that signal forwarding is set up between new and old signals."""
        widget = basic_terminal_widget

        # Connect to both old and new signals
        new_signal_called = Mock()
        old_signal_called = Mock()

        widget.terminalReady.connect(new_signal_called)
        widget.terminal_ready.connect(old_signal_called)

        # Emit the new signal
        widget.terminalReady.emit()

        # Both should be called due to forwarding
        new_signal_called.assert_called_once()
        old_signal_called.assert_called_once()


class TestEventSystemHelperMethods:
    """Test helper methods in the event system."""

    def test_monitor_command_execution_helper(self, basic_terminal_widget):
        """Test monitor_command_execution helper method."""
        widget = basic_terminal_widget

        callback = Mock()
        widget.monitor_command_execution(callback)

        # Create a sample ProcessEvent
        process_event = ProcessEvent(command="test", pid=1234)

        # Emit the signal
        widget.processStarted.emit(process_event)

        # Callback should have been called with the event
        callback.assert_called_once_with(process_event)

    def test_set_selection_handler_helper(self, basic_terminal_widget):
        """Test set_selection_handler helper method."""
        widget = basic_terminal_widget

        handler = Mock()
        widget.set_selection_handler(handler)

        # Emit selection changed signal
        test_text = "test selection"
        widget.selectionChanged.emit(test_text)

        # Handler should have been called
        handler.assert_called_once_with(test_text)

    def test_enable_session_recording_helper(self, basic_terminal_widget):
        """Test enable_session_recording helper method."""
        widget = basic_terminal_widget

        callback = Mock()
        widget.enable_session_recording(callback)

        # Emit output received signal
        test_output = "test output"
        widget.outputReceived.emit(test_output)

        # Callback should have been called
        callback.assert_called_once_with(test_output)

    def test_add_context_menu_handler_helper(self, basic_terminal_widget):
        """Test add_context_menu_handler helper method."""
        widget = basic_terminal_widget

        handler = Mock()
        widget.add_context_menu_handler(handler)

        # The handler should be stored
        assert widget.custom_context_menu_handler == handler


@pytest.mark.gui
class TestEventCategoryFiltering:
    """Test that event category filtering works correctly."""

    def test_lifecycle_events_filtered(self, qtbot, mock_embedded_server):
        """Test lifecycle events are filtered based on configuration."""
        # Create widget with only PROCESS events enabled
        config = EventConfig(enabled_categories={EventCategory.PROCESS})
        widget = TerminalWidget(event_config=config)
        qtbot.addWidget(widget)

        # Mock the signal emission
        lifecycle_signal = Mock()
        widget.terminalReady.connect(lifecycle_signal)

        # Simulate terminal ready - should not emit because LIFECYCLE is disabled
        widget._on_load_finished(True)

        # Signal should not have been called
        lifecycle_signal.assert_not_called()

    def test_process_events_allowed(self, qtbot, mock_embedded_server):
        """Test process events are emitted when enabled."""
        # Create widget with PROCESS events enabled
        config = EventConfig(enabled_categories={EventCategory.PROCESS})
        widget = TerminalWidget(event_config=config)
        qtbot.addWidget(widget)

        # Mock the signal emission
        process_signal = Mock()
        widget.processStarted.connect(process_signal)

        # Simulate command started - should emit because PROCESS is enabled
        widget._on_command_started()

        # Signal should have been called
        process_signal.assert_called_once()

    def test_content_events_filtered(self, qtbot, mock_embedded_server):
        """Test content events are filtered correctly."""
        # Create widget with no CONTENT events
        config = EventConfig(enabled_categories={EventCategory.LIFECYCLE})
        widget = TerminalWidget(event_config=config)
        qtbot.addWidget(widget)

        # Mock the signal emission
        output_signal = Mock()
        widget.outputReceived.connect(output_signal)

        # Simulate output - should not emit because CONTENT is disabled
        widget._handle_output("test output")

        # Signal should not have been called
        output_signal.assert_not_called()

    def test_event_category_dynamic_changes(self, basic_terminal_widget):
        """Test dynamically changing event categories."""
        widget = basic_terminal_widget

        # Start with all categories disabled
        widget.event_config.enabled_categories = set()

        # Test enabling a category
        widget.enable_event_category(EventCategory.INTERACTION)
        assert EventCategory.INTERACTION in widget.event_config.enabled_categories

        # Test disabling a category
        widget.disable_event_category(EventCategory.INTERACTION)
        assert EventCategory.INTERACTION not in widget.event_config.enabled_categories
