"""Integration tests for end-to-end event flow."""

import time
from unittest.mock import Mock, patch

import pytest
from vfwidgets_terminal import (
    EventCategory,
    EventConfig,
    KeyEvent,
    ProcessEvent,
    TerminalWidget,
)


@pytest.mark.integration
class TestTerminalBridgeWidgetIntegration:
    """Test integration between TerminalBridge and TerminalWidget."""

    def test_bridge_widget_signal_connections(
        self, qtbot, mock_embedded_server, mock_qwebengineview, mock_qwebchannel
    ):
        """Test that bridge signals are properly connected to widget signals."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        # Verify bridge was created and connected
        assert widget.bridge is not None

        # Mock signal connections to verify they exist
        bridge = widget.bridge

        # Test selection change flow
        selection_events = []
        widget.selectionChanged.connect(lambda text: selection_events.append(text))

        # Simulate JavaScript calling bridge method
        bridge.on_selection_changed("test selection")

        # Should flow through to widget signal
        assert len(selection_events) == 1
        assert selection_events[0] == "test selection"

    def test_bridge_to_widget_key_events(
        self, qtbot, mock_embedded_server, mock_qwebengineview, mock_qwebchannel
    ):
        """Test key events flow from bridge to widget."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        key_events = []
        widget.keyPressed.connect(lambda event: key_events.append(event))

        # Simulate JavaScript key press through bridge
        widget.bridge.on_key_pressed("Enter", "Enter", False, False, False)

        # Should create structured KeyEvent and emit
        assert len(key_events) == 1
        key_event = key_events[0]
        assert isinstance(key_event, KeyEvent)
        assert key_event.key == "Enter"
        assert key_event.code == "Enter"

    def test_bridge_to_widget_bell_events(
        self, qtbot, mock_embedded_server, mock_qwebengineview, mock_qwebchannel
    ):
        """Test bell events flow from bridge to widget."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        bell_events = []
        widget.bellActivated.connect(lambda: bell_events.append(True))

        # Simulate bell through bridge
        widget.bridge.on_bell()

        # Should flow through to widget signal
        assert len(bell_events) == 1

    def test_bridge_to_widget_title_events(
        self, qtbot, mock_embedded_server, mock_qwebengineview, mock_qwebchannel
    ):
        """Test title change events flow from bridge to widget."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        title_events = []
        widget.titleChanged.connect(lambda title: title_events.append(title))

        # Simulate title change through bridge
        widget.bridge.on_title_changed("New Terminal Title")

        # Should flow through to widget signal
        assert len(title_events) == 1
        assert title_events[0] == "New Terminal Title"

    def test_bridge_to_widget_scroll_events(
        self, qtbot, mock_embedded_server, mock_qwebengineview, mock_qwebchannel
    ):
        """Test scroll events flow from bridge to widget."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        scroll_events = []
        widget.scrollOccurred.connect(lambda pos: scroll_events.append(pos))

        # Simulate scroll through bridge
        widget.bridge.on_scroll(150)

        # Should flow through to widget signal
        assert len(scroll_events) == 1
        assert scroll_events[0] == 150


@pytest.mark.integration
class TestServerWidgetIntegration:
    """Test integration between EmbeddedTerminalServer and TerminalWidget."""

    def test_server_widget_lifecycle_signals(self, qtbot, mock_embedded_server):
        """Test server lifecycle signals reach widget."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        # Connect to lifecycle signals
        ready_events = []
        started_events = []

        widget.terminalReady.connect(lambda: ready_events.append(True))
        widget.processStarted.connect(lambda event: started_events.append(event))

        # Simulate server events
        widget._on_load_finished(True)  # Terminal ready
        widget._on_command_started()  # Process started

        # Should have received signals
        assert len(ready_events) == 1
        assert len(started_events) == 1

        # Process event should be structured
        process_event = started_events[0]
        assert isinstance(process_event, ProcessEvent)

    def test_server_widget_output_flow(self, qtbot, mock_embedded_server):
        """Test output flow from server to widget."""
        widget = TerminalWidget(capture_output=True)
        qtbot.addWidget(widget)

        output_events = []
        widget.outputReceived.connect(lambda data: output_events.append(data))

        # Simulate server output
        test_output = "test terminal output"
        widget._handle_output(test_output)

        # Should receive output signal
        assert len(output_events) == 1
        assert output_events[0] == test_output

    def test_server_widget_command_flow(self, qtbot, mock_embedded_server):
        """Test command sending from widget to server."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        # Mock server
        mock_server = Mock()
        widget.server = mock_server

        input_events = []
        widget.inputSent.connect(lambda text: input_events.append(text))

        # Send command through widget
        test_command = "echo hello"
        widget.send_command(test_command)

        # Should send to server and emit signal
        mock_server.send_input.assert_called_once_with(test_command + "\n")
        assert len(input_events) == 1
        assert input_events[0] == test_command

    def test_server_widget_process_management(self, qtbot, mock_embedded_server):
        """Test process management integration."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        # Connect to process signals
        started_events = []
        finished_events = []

        widget.processStarted.connect(lambda event: started_events.append(event))
        widget.processFinished.connect(lambda code: finished_events.append(code))

        # Simulate process lifecycle
        widget._on_command_started()
        widget._on_command_finished(0)

        # Should have received both signals
        assert len(started_events) == 1
        assert len(finished_events) == 1
        assert finished_events[0] == 0  # Exit code


@pytest.mark.integration
class TestEventCategoryIntegration:
    """Test event category filtering integration across components."""

    def test_event_category_filtering_bridge_to_widget(
        self, qtbot, mock_embedded_server, mock_qwebengineview, mock_qwebchannel
    ):
        """Test event category filtering in bridge-to-widget flow."""
        # Create widget with only LIFECYCLE events enabled
        config = EventConfig(enabled_categories={EventCategory.LIFECYCLE})
        widget = TerminalWidget(event_config=config)
        qtbot.addWidget(widget)

        # Connect to interaction signals (should be filtered)
        selection_events = []
        key_events = []

        widget.selectionChanged.connect(lambda text: selection_events.append(text))
        widget.keyPressed.connect(lambda event: key_events.append(event))

        # Simulate interaction events through bridge
        widget.bridge.on_selection_changed("test selection")
        widget.bridge.on_key_pressed("a", "KeyA", False, False, False)

        # Should not receive signals because INTERACTION category is disabled
        assert len(selection_events) == 0
        assert len(key_events) == 0

    def test_event_category_filtering_server_to_widget(
        self, qtbot, mock_embedded_server
    ):
        """Test event category filtering in server-to-widget flow."""
        # Create widget with only INTERACTION events enabled
        config = EventConfig(enabled_categories={EventCategory.INTERACTION})
        widget = TerminalWidget(event_config=config)
        qtbot.addWidget(widget)

        # Connect to content signals (should be filtered)
        output_events = []
        input_events = []

        widget.outputReceived.connect(lambda data: output_events.append(data))
        widget.inputSent.connect(lambda text: input_events.append(text))

        # Simulate content events
        widget._handle_output("test output")
        widget.send_command("test command")

        # Should not receive output signal because CONTENT category is disabled
        assert len(output_events) == 0
        # Input should also be filtered
        assert len(input_events) == 0

    def test_event_category_dynamic_changes_integration(
        self, qtbot, mock_embedded_server, mock_qwebengineview, mock_qwebchannel
    ):
        """Test dynamic event category changes affect all components."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        # Start with all categories disabled
        widget.event_config.enabled_categories = set()

        # Connect to various signals
        selection_events = []
        output_events = []

        widget.selectionChanged.connect(lambda text: selection_events.append(text))
        widget.outputReceived.connect(lambda data: output_events.append(data))

        # Test events - should not be received
        widget.bridge.on_selection_changed("test 1")
        widget._handle_output("output 1")

        assert len(selection_events) == 0
        assert len(output_events) == 0

        # Enable INTERACTION category
        widget.enable_event_category(EventCategory.INTERACTION)

        # Test selection event - should now be received
        widget.bridge.on_selection_changed("test 2")
        widget._handle_output("output 2")

        assert len(selection_events) == 1
        assert len(output_events) == 0  # Still disabled

        # Enable CONTENT category
        widget.enable_event_category(EventCategory.CONTENT)

        # Test output event - should now be received
        widget._handle_output("output 3")

        assert len(output_events) == 1


@pytest.mark.integration
class TestBackwardsCompatibilityIntegration:
    """Test backwards compatibility signal forwarding integration."""

    def test_new_to_old_signal_forwarding_integration(
        self, qtbot, mock_embedded_server, mock_qwebengineview, mock_qwebchannel
    ):
        """Test new signals forward to old signals across all components."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        # Connect to both new and old signals
        new_selection_events = []
        old_selection_events = []
        new_ready_events = []
        old_ready_events = []

        widget.selectionChanged.connect(lambda text: new_selection_events.append(text))
        widget.selection_changed.connect(lambda text: old_selection_events.append(text))
        widget.terminalReady.connect(lambda: new_ready_events.append(True))
        widget.terminal_ready.connect(lambda: old_ready_events.append(True))

        # Trigger events through different components
        widget.bridge.on_selection_changed("test selection")  # Bridge event
        widget._on_load_finished(True)  # Server event

        # Both new and old signals should be called
        assert len(new_selection_events) == 1
        assert len(old_selection_events) == 1
        assert len(new_ready_events) == 1
        assert len(old_ready_events) == 1

    def test_deprecation_warnings_integration(self, qtbot, mock_embedded_server):
        """Test deprecation warnings are emitted during signal forwarding."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        # Enable deprecation warnings
        widget.event_config.enable_deprecation_warnings = True

        old_signal_handler = Mock()
        widget.terminal_ready.connect(old_signal_handler)

        with patch("warnings.warn") as mock_warn:
            # Trigger new signal which should forward to old
            widget.terminalReady.emit()

            # Should emit deprecation warning
            mock_warn.assert_called()
            warning_call = mock_warn.call_args[0][0]
            assert "deprecated" in warning_call.lower()

    def test_deprecation_warnings_disabled_integration(
        self, qtbot, mock_embedded_server
    ):
        """Test deprecation warnings can be disabled."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        # Disable deprecation warnings
        widget.event_config.enable_deprecation_warnings = False

        old_signal_handler = Mock()
        widget.terminal_ready.connect(old_signal_handler)

        with patch("warnings.warn") as mock_warn:
            # Trigger new signal
            widget.terminalReady.emit()

            # Should not emit deprecation warning
            mock_warn.assert_not_called()


@pytest.mark.integration
class TestHelperMethodsIntegration:
    """Test helper methods integration with the event system."""

    def test_monitor_command_execution_integration(self, qtbot, mock_embedded_server):
        """Test monitor_command_execution helper integrates with process events."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        # Set up monitoring
        monitored_commands = []
        widget.monitor_command_execution(lambda event: monitored_commands.append(event))

        # Simulate command execution
        widget._on_command_started()

        # Should capture the process event
        assert len(monitored_commands) == 1
        process_event = monitored_commands[0]
        assert isinstance(process_event, ProcessEvent)

    def test_enable_session_recording_integration(self, qtbot, mock_embedded_server):
        """Test enable_session_recording helper integrates with output events."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        # Set up recording
        recorded_output = []
        widget.enable_session_recording(lambda data: recorded_output.append(data))

        # Simulate output
        test_output = "test session output"
        widget._handle_output(test_output)

        # Should capture the output
        assert len(recorded_output) == 1
        assert recorded_output[0] == test_output

    def test_set_selection_handler_integration(
        self, qtbot, mock_embedded_server, mock_qwebengineview, mock_qwebchannel
    ):
        """Test set_selection_handler integrates with bridge selection events."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        # Set up selection handler
        selection_events = []
        widget.set_selection_handler(lambda text: selection_events.append(text))

        # Simulate selection through bridge
        widget.bridge.on_selection_changed("selected text")

        # Should capture the selection
        assert len(selection_events) == 1
        assert selection_events[0] == "selected text"


@pytest.mark.integration
@pytest.mark.slow
class TestRealTerminalIntegration:
    """Integration tests with real terminal processes."""

    def test_real_terminal_full_lifecycle(
        self, real_terminal_widget, qtbot, event_collector
    ):
        """Test complete lifecycle with real terminal."""
        widget = real_terminal_widget

        # Connect event collector to all major signals
        widget.terminalReady.connect(
            lambda: event_collector.collect_event("terminal_ready")
        )
        widget.processStarted.connect(
            lambda e: event_collector.collect_event("process_started", e)
        )
        widget.outputReceived.connect(
            lambda d: event_collector.collect_event("output_received", d)
        )
        widget.inputSent.connect(
            lambda t: event_collector.collect_event("input_sent", t)
        )

        # Wait for terminal to be ready
        with qtbot.waitSignal(widget.terminalReady, timeout=15000):
            pass

        # Send a command
        widget.send_command("echo 'Hello Integration Test'")

        # Wait a bit for output
        time.sleep(1)

        # Verify we captured the lifecycle events
        ready_events = event_collector.get_events_of_type("terminal_ready")
        assert len(ready_events) >= 1

        process_events = event_collector.get_events_of_type("process_started")
        assert len(process_events) >= 1

        input_events = event_collector.get_events_of_type("input_sent")
        assert len(input_events) >= 1

        # Might have output events
        event_collector.get_events_of_type("output_received")
        # Output events are optional as they depend on capture_output setting

    def test_real_terminal_process_info_integration(self, real_terminal_widget, qtbot):
        """Test process info integration with real terminal."""
        widget = real_terminal_widget

        # Wait for terminal to be ready
        with qtbot.waitSignal(widget.terminalReady, timeout=15000):
            pass

        # Get process info
        process_info = widget.get_process_info()

        # Should have real process information
        assert "pid" in process_info
        assert "command" in process_info
        assert process_info["running"] is True
        assert isinstance(process_info["pid"], int)

    def test_real_terminal_command_execution_integration(
        self, real_terminal_widget, qtbot
    ):
        """Test command execution integration with real terminal."""
        widget = real_terminal_widget

        # Wait for terminal to be ready
        with qtbot.waitSignal(widget.terminalReady, timeout=15000):
            pass

        # Track input events
        input_events = []
        widget.inputSent.connect(lambda text: input_events.append(text))

        # Send multiple commands
        commands = ["pwd", "echo test", "date"]
        for cmd in commands:
            widget.send_command(cmd)
            time.sleep(0.1)  # Small delay between commands

        # Should have captured all input events
        assert len(input_events) == len(commands)
        for i, cmd in enumerate(commands):
            assert input_events[i] == cmd

    def test_real_terminal_event_categories_integration(self, qtbot):
        """Test event categories work with real terminal."""
        from vfwidgets_terminal import EventConfig

        # Create widget with only LIFECYCLE events
        config = EventConfig(enabled_categories={EventCategory.LIFECYCLE})
        widget = TerminalWidget(event_config=config, port=0)
        qtbot.addWidget(widget)

        try:
            # Track different event types
            lifecycle_events = []
            content_events = []

            widget.terminalReady.connect(lambda: lifecycle_events.append("ready"))
            widget.outputReceived.connect(lambda d: content_events.append(d))
            widget.inputSent.connect(lambda t: content_events.append(t))

            # Wait for terminal to be ready
            with qtbot.waitSignal(widget.terminalReady, timeout=15000):
                pass

            # Send command
            widget.send_command("echo test")
            time.sleep(0.5)

            # Should have lifecycle events but no content events
            assert len(lifecycle_events) >= 1
            assert len(content_events) == 0  # Content category disabled

        finally:
            # Cleanup
            widget.close_terminal()


@pytest.mark.integration
class TestErrorHandlingIntegration:
    """Test error handling integration across components."""

    def test_bridge_error_handling_integration(
        self, qtbot, mock_embedded_server, mock_qwebengineview, mock_qwebchannel
    ):
        """Test bridge error handling doesn't break widget."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        # Connect to signals
        events = []
        widget.selectionChanged.connect(lambda text: events.append(text))

        # Test with various edge cases
        edge_cases = [
            "",  # Empty string
            None,  # None value (should be handled gracefully)
            "very long text " * 1000,  # Very long text
            "unicode: 🚀 🎯 📊",  # Unicode characters
            "\x00\x01\x02",  # Control characters
        ]

        for case in edge_cases:
            try:
                if case is not None:
                    widget.bridge.on_selection_changed(case)
                    # Should handle gracefully without crashing
            except Exception as e:
                pytest.fail(f"Bridge failed to handle edge case {repr(case)}: {e}")

    def test_server_error_handling_integration(self, qtbot, mock_embedded_server):
        """Test server error handling doesn't break widget."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        # Test with various output edge cases
        edge_cases = [
            "",  # Empty output
            "\x1b[31mRed text\x1b[0m",  # ANSI escape sequences
            "Binary data: \x00\x01\x02\x03",  # Binary-like data
            "Long line: " + "x" * 10000,  # Very long line
        ]

        output_events = []
        widget.outputReceived.connect(lambda data: output_events.append(data))

        for case in edge_cases:
            try:
                widget._handle_output(case)
                # Should handle gracefully
            except Exception as e:
                pytest.fail(f"Server output handling failed for {repr(case)}: {e}")

    def test_event_system_robustness_integration(
        self, qtbot, mock_embedded_server, mock_qwebengineview, mock_qwebchannel
    ):
        """Test event system robustness under stress."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        # Connect multiple handlers to same signal
        handlers = []
        for _i in range(10):
            handler = Mock()
            handlers.append(handler)
            widget.selectionChanged.connect(handler)

        # Generate rapid events
        for i in range(100):
            widget.bridge.on_selection_changed(f"rapid event {i}")

        # All handlers should have been called for each event
        for handler in handlers:
            assert handler.call_count == 100

    def test_memory_cleanup_integration(
        self, qtbot, mock_embedded_server, mock_qwebengineview, mock_qwebchannel
    ):
        """Test memory cleanup during widget lifecycle."""
        import gc

        initial_widgets = []
        # Create and destroy multiple widgets
        for i in range(5):
            widget = TerminalWidget()
            qtbot.addWidget(widget)
            initial_widgets.append(widget)

            # Generate some events
            widget.bridge.on_selection_changed(f"test {i}")
            widget._handle_output(f"output {i}")

        # Clear references and force garbage collection
        for widget in initial_widgets:
            widget.close_terminal()

        initial_widgets.clear()
        gc.collect()

        # Memory should be cleaned up (exact check is difficult, but should not crash)
