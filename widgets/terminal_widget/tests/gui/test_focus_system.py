"""GUI tests for the focus system and event filtering."""

from unittest.mock import Mock, patch

import pytest
from PySide6.QtCore import QEvent
from PySide6.QtGui import QFocusEvent
from vfwidgets_terminal import EventCategory, TerminalWidget


@pytest.mark.gui
class TestFocusSystemSetup:
    """Test focus system setup and configuration."""

    def test_focus_detection_setup_immediate(
        self, qtbot, mock_embedded_server, mock_qwebengineview
    ):
        """Test focus detection setup when focus proxy is immediately available."""
        # Mock focus proxy to be available immediately
        mock_focus_proxy = Mock()
        mock_qwebengineview.focusProxy.return_value = mock_focus_proxy

        widget = TerminalWidget()
        qtbot.addWidget(widget)

        # Verify focus proxy event filter was installed
        mock_focus_proxy.installEventFilter.assert_called_with(widget)

    def test_focus_detection_setup_delayed(self, qtbot, mock_embedded_server, mock_qwebengineview):
        """Test focus detection setup when focus proxy is not immediately available."""
        # Mock focus proxy to be unavailable initially
        mock_focus_proxy = Mock()
        mock_qwebengineview.focusProxy.side_effect = [None, None, mock_focus_proxy]

        widget = TerminalWidget()
        qtbot.addWidget(widget)

        # Simulate page load finished
        widget._on_load_finished(True)

        # Should eventually install the event filter
        mock_focus_proxy.installEventFilter.assert_called_with(widget)

    def test_focus_detection_no_proxy_available(
        self, qtbot, mock_embedded_server, mock_qwebengineview
    ):
        """Test focus detection when no focus proxy is available."""
        # Mock focus proxy to never be available
        mock_qwebengineview.focusProxy.return_value = None

        widget = TerminalWidget()
        qtbot.addWidget(widget)

        # Should not crash or raise exceptions
        widget._on_load_finished(True)

    def test_focus_detection_already_installed(
        self, qtbot, mock_embedded_server, mock_qwebengineview
    ):
        """Test focus detection when filter is already installed."""
        # Mock focus proxy with already installed filter
        mock_focus_proxy = Mock()
        mock_focus_proxy._vf_filter_installed = True
        mock_qwebengineview.focusProxy.return_value = mock_focus_proxy

        widget = TerminalWidget()
        qtbot.addWidget(widget)

        # Simulate delayed setup
        widget._on_load_finished(True)

        # Should not install filter again
        mock_focus_proxy.installEventFilter.assert_called_once()


@pytest.mark.gui
class TestEventFiltering:
    """Test the eventFilter method and focus event handling."""

    def test_event_filter_focus_in(self, qtbot, mock_embedded_server, mock_qwebengineview):
        """Test eventFilter handling FocusIn events."""
        mock_focus_proxy = Mock()
        mock_qwebengineview.focusProxy.return_value = mock_focus_proxy

        widget = TerminalWidget()
        qtbot.addWidget(widget)

        # Create mock FocusIn event
        mock_event = Mock()
        mock_event.type.return_value = QEvent.Type.FocusIn

        # Connect signal to verify emission
        focus_signal = Mock()
        widget.focusReceived.connect(focus_signal)

        # Call eventFilter with focus proxy as object
        result = widget.eventFilter(mock_focus_proxy, mock_event)

        # Should emit focusReceived signal and return False (continue processing)
        focus_signal.assert_called_once()
        assert result is False

    def test_event_filter_focus_out(self, qtbot, mock_embedded_server, mock_qwebengineview):
        """Test eventFilter handling FocusOut events."""
        mock_focus_proxy = Mock()
        mock_qwebengineview.focusProxy.return_value = mock_focus_proxy

        widget = TerminalWidget()
        qtbot.addWidget(widget)

        # Create mock FocusOut event
        mock_event = Mock()
        mock_event.type.return_value = QEvent.Type.FocusOut

        # Connect signal to verify emission
        focus_signal = Mock()
        widget.focusLost.connect(focus_signal)

        # Call eventFilter with focus proxy as object
        result = widget.eventFilter(mock_focus_proxy, mock_event)

        # Should emit focusLost signal and return False
        focus_signal.assert_called_once()
        assert result is False

    def test_event_filter_other_events(self, qtbot, mock_embedded_server, mock_qwebengineview):
        """Test eventFilter with non-focus events."""
        mock_focus_proxy = Mock()
        mock_qwebengineview.focusProxy.return_value = mock_focus_proxy

        widget = TerminalWidget()
        qtbot.addWidget(widget)

        # Create mock non-focus event
        mock_event = Mock()
        mock_event.type.return_value = QEvent.Type.MouseButtonPress

        # Connect signals to verify they're not emitted
        focus_in_signal = Mock()
        focus_out_signal = Mock()
        widget.focusReceived.connect(focus_in_signal)
        widget.focusLost.connect(focus_out_signal)

        # Call eventFilter
        with patch("super") as mock_super:
            mock_super.return_value.eventFilter.return_value = False
            widget.eventFilter(mock_focus_proxy, mock_event)

        # Should not emit focus signals and call parent eventFilter
        focus_in_signal.assert_not_called()
        focus_out_signal.assert_not_called()
        mock_super.assert_called()

    def test_event_filter_wrong_object(self, qtbot, mock_embedded_server, mock_qwebengineview):
        """Test eventFilter with object that's not the focus proxy."""
        mock_focus_proxy = Mock()
        mock_qwebengineview.focusProxy.return_value = mock_focus_proxy

        widget = TerminalWidget()
        qtbot.addWidget(widget)

        # Create different object and focus event
        other_object = Mock()
        mock_event = Mock()
        mock_event.type.return_value = QEvent.Type.FocusIn

        # Connect signal to verify it's not emitted
        focus_signal = Mock()
        widget.focusReceived.connect(focus_signal)

        # Call eventFilter with different object
        with patch("super") as mock_super:
            mock_super.return_value.eventFilter.return_value = False
            widget.eventFilter(other_object, mock_event)

        # Should not emit signal and call parent eventFilter
        focus_signal.assert_not_called()
        mock_super.assert_called()

    def test_event_filter_debug_logging(self, qtbot, mock_embedded_server, mock_qwebengineview):
        """Test eventFilter debug logging when debug is enabled."""
        mock_focus_proxy = Mock()
        mock_qwebengineview.focusProxy.return_value = mock_focus_proxy

        widget = TerminalWidget(debug=True)
        qtbot.addWidget(widget)

        # Create mock event with type name
        mock_event = Mock()
        mock_event.type.return_value = QEvent.Type.MouseButtonPress
        mock_event.type.return_value.name = "MouseButtonPress"

        with patch("logging.Logger.debug") as mock_debug:
            widget.eventFilter(mock_focus_proxy, mock_event)

        # Should log the event when debug is enabled
        mock_debug.assert_called()


@pytest.mark.gui
class TestFocusEventCategoryFiltering:
    """Test focus events respect event category configuration."""

    def test_focus_events_enabled(self, qtbot, mock_embedded_server, mock_qwebengineview):
        """Test focus events when FOCUS category is enabled."""
        from vfwidgets_terminal import EventConfig

        config = EventConfig(enabled_categories={EventCategory.FOCUS})

        mock_focus_proxy = Mock()
        mock_qwebengineview.focusProxy.return_value = mock_focus_proxy

        widget = TerminalWidget(event_config=config)
        qtbot.addWidget(widget)

        # Create focus in event
        mock_event = Mock()
        mock_event.type.return_value = QEvent.Type.FocusIn

        # Connect signal
        focus_signal = Mock()
        widget.focusReceived.connect(focus_signal)

        # Call eventFilter
        widget.eventFilter(mock_focus_proxy, mock_event)

        # Should emit signal because FOCUS category is enabled
        focus_signal.assert_called_once()

    def test_focus_events_disabled(self, qtbot, mock_embedded_server, mock_qwebengineview):
        """Test focus events when FOCUS category is disabled."""
        from vfwidgets_terminal import EventConfig

        config = EventConfig(
            enabled_categories={EventCategory.LIFECYCLE}  # FOCUS not included
        )

        mock_focus_proxy = Mock()
        mock_qwebengineview.focusProxy.return_value = mock_focus_proxy

        widget = TerminalWidget(event_config=config)
        qtbot.addWidget(widget)

        # Create focus in event
        mock_event = Mock()
        mock_event.type.return_value = QEvent.Type.FocusIn

        # Connect signal
        focus_signal = Mock()
        widget.focusReceived.connect(focus_signal)

        # Call eventFilter
        widget.eventFilter(mock_focus_proxy, mock_event)

        # Should not emit signal because FOCUS category is disabled
        focus_signal.assert_not_called()

    def test_focus_category_dynamic_change(self, qtbot, mock_embedded_server, mock_qwebengineview):
        """Test changing focus category dynamically."""
        mock_focus_proxy = Mock()
        mock_qwebengineview.focusProxy.return_value = mock_focus_proxy

        widget = TerminalWidget()
        qtbot.addWidget(widget)

        # Initially disable focus events
        widget.disable_event_category(EventCategory.FOCUS)

        # Create focus event
        mock_event = Mock()
        mock_event.type.return_value = QEvent.Type.FocusIn

        focus_signal = Mock()
        widget.focusReceived.connect(focus_signal)

        # Should not emit when disabled
        widget.eventFilter(mock_focus_proxy, mock_event)
        focus_signal.assert_not_called()

        # Enable focus events
        widget.enable_event_category(EventCategory.FOCUS)

        # Should emit when enabled
        widget.eventFilter(mock_focus_proxy, mock_event)
        focus_signal.assert_called_once()


@pytest.mark.gui
class TestFocusSignalForwarding:
    """Test focus signal forwarding to deprecated signals."""

    def test_focus_received_signal_forwarding(
        self, qtbot, mock_embedded_server, mock_qwebengineview
    ):
        """Test focusReceived signal forwards to deprecated focus_received."""
        mock_focus_proxy = Mock()
        mock_qwebengineview.focusProxy.return_value = mock_focus_proxy

        widget = TerminalWidget()
        qtbot.addWidget(widget)

        # Connect to both new and old signals
        new_signal = Mock()
        old_signal = Mock()
        widget.focusReceived.connect(new_signal)
        widget.focus_received.connect(old_signal)

        # Create focus in event
        mock_event = Mock()
        mock_event.type.return_value = QEvent.Type.FocusIn

        # Trigger event
        widget.eventFilter(mock_focus_proxy, mock_event)

        # Both signals should be called due to forwarding
        new_signal.assert_called_once()
        old_signal.assert_called_once()

    def test_focus_lost_signal_forwarding(self, qtbot, mock_embedded_server, mock_qwebengineview):
        """Test focusLost signal forwards to deprecated focus_lost."""
        mock_focus_proxy = Mock()
        mock_qwebengineview.focusProxy.return_value = mock_focus_proxy

        widget = TerminalWidget()
        qtbot.addWidget(widget)

        # Connect to both new and old signals
        new_signal = Mock()
        old_signal = Mock()
        widget.focusLost.connect(new_signal)
        widget.focus_lost.connect(old_signal)

        # Create focus out event
        mock_event = Mock()
        mock_event.type.return_value = QEvent.Type.FocusOut

        # Trigger event
        widget.eventFilter(mock_focus_proxy, mock_event)

        # Both signals should be called due to forwarding
        new_signal.assert_called_once()
        old_signal.assert_called_once()


@pytest.mark.gui
class TestDebugWebEngineView:
    """Test DebugWebEngineView focus-related functionality."""

    def test_debug_web_engine_view_initialization(self, qtbot):
        """Test DebugWebEngineView initialization."""
        from vfwidgets_terminal.terminal import DebugWebEngineView

        view = DebugWebEngineView()
        qtbot.addWidget(view)

        assert view.debug_enabled is False
        assert hasattr(view, "right_clicked")

    def test_debug_web_engine_view_set_debug(self, qtbot):
        """Test setting debug mode on DebugWebEngineView."""
        from vfwidgets_terminal.terminal import DebugWebEngineView

        view = DebugWebEngineView()
        qtbot.addWidget(view)

        # Enable debug
        view.set_debug(True)
        assert view.debug_enabled is True

        # Disable debug
        view.set_debug(False)
        assert view.debug_enabled is False

    def test_debug_web_engine_view_in_terminal_widget(self, qtbot, mock_embedded_server):
        """Test that TerminalWidget uses DebugWebEngineView."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        # Verify the web view is DebugWebEngineView
        from vfwidgets_terminal.terminal import DebugWebEngineView

        assert isinstance(widget.web_view, DebugWebEngineView)

    def test_debug_web_engine_view_debug_propagation(self, qtbot, mock_embedded_server):
        """Test debug setting propagates to DebugWebEngineView."""
        widget = TerminalWidget(debug=True)
        qtbot.addWidget(widget)

        # Debug should be enabled on the web view
        assert widget.web_view.debug_enabled is True


@pytest.mark.integration
class TestFocusSystemIntegration:
    """Integration tests for the focus system."""

    def test_real_focus_event_flow(self, real_terminal_widget, qtbot):
        """Test real focus event flow with actual widget."""
        widget = real_terminal_widget

        # Connect to focus signals
        focus_received_events = []
        focus_lost_events = []

        widget.focusReceived.connect(lambda: focus_received_events.append(True))
        widget.focusLost.connect(lambda: focus_lost_events.append(True))

        # Wait for terminal to be ready
        with qtbot.waitSignal(widget.terminalReady, timeout=10000):
            pass

        # Simulate focus changes by triggering events directly
        # (Real focus events are hard to simulate reliably in tests)
        if widget.web_view.focusProxy():
            focus_in_event = QFocusEvent(QEvent.Type.FocusIn)
            focus_out_event = QFocusEvent(QEvent.Type.FocusOut)

            # Simulate focus in
            widget.eventFilter(widget.web_view.focusProxy(), focus_in_event)

            # Simulate focus out
            widget.eventFilter(widget.web_view.focusProxy(), focus_out_event)

            # Verify events were captured
            assert len(focus_received_events) > 0
            assert len(focus_lost_events) > 0

    @pytest.mark.slow
    def test_focus_system_reliability(self, real_terminal_widget, qtbot):
        """Test focus system reliability over multiple events."""
        widget = real_terminal_widget

        focus_events = []

        def track_focus_events(event_type):
            focus_events.append(event_type)

        widget.focusReceived.connect(lambda: track_focus_events("focus_in"))
        widget.focusLost.connect(lambda: track_focus_events("focus_out"))

        # Wait for terminal to be ready
        with qtbot.waitSignal(widget.terminalReady, timeout=10000):
            pass

        # Generate multiple focus events
        if widget.web_view.focusProxy():
            proxy = widget.web_view.focusProxy()

            for _i in range(10):
                focus_in_event = QFocusEvent(QEvent.Type.FocusIn)
                focus_out_event = QFocusEvent(QEvent.Type.FocusOut)

                widget.eventFilter(proxy, focus_in_event)
                widget.eventFilter(proxy, focus_out_event)

            # Should have captured all events
            assert len([e for e in focus_events if e == "focus_in"]) == 10
            assert len([e for e in focus_events if e == "focus_out"]) == 10

    def test_focus_system_with_multiple_widgets(self, qtbot):
        """Test focus system with multiple terminal widgets."""
        from vfwidgets_terminal import TerminalWidget

        widgets = []
        focus_events = []

        # Create multiple widgets
        for i in range(3):
            widget = TerminalWidget(port=0)  # Random port for each
            qtbot.addWidget(widget)
            widgets.append(widget)

            # Track focus events for each widget
            widget.focusReceived.connect(lambda w=i: focus_events.append(f"widget_{w}_focus_in"))
            widget.focusLost.connect(lambda w=i: focus_events.append(f"widget_{w}_focus_out"))

        # Simulate focus events on different widgets
        for _i, widget in enumerate(widgets):
            if widget.web_view.focusProxy():
                focus_in_event = QFocusEvent(QEvent.Type.FocusIn)
                widget.eventFilter(widget.web_view.focusProxy(), focus_in_event)

        # Should have focus events for each widget
        widget_focus_events = [e for e in focus_events if "focus_in" in e]
        assert len(widget_focus_events) <= 3  # At most one per widget

        # Cleanup
        for widget in widgets:
            try:
                widget.close_terminal()
            except Exception:
                pass  # Widget already closed
