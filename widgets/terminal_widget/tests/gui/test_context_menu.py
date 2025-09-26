"""GUI tests for context menu system and right-click interactions."""

from unittest.mock import Mock, patch

import pytest
from PySide6.QtCore import QPoint
from PySide6.QtGui import QAction, QContextMenuEvent
from PySide6.QtWidgets import QApplication
from vfwidgets_terminal import ContextMenuEvent, EventCategory, TerminalWidget


@pytest.mark.gui
class TestContextMenuEventCreation:
    """Test context menu event creation and handling."""

    def test_context_menu_event_creation_basic(self, qtbot, mock_embedded_server):
        """Test basic context menu event creation."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        # Create context menu event
        pos = QPoint(100, 200)
        event = QContextMenuEvent(QContextMenuEvent.Mouse, pos)

        # Connect signal to capture emitted event
        context_events = []
        widget.contextMenuRequested.connect(lambda e: context_events.append(e))

        # Trigger context menu
        widget.contextMenuEvent(event)

        # Verify event was created and emitted
        assert len(context_events) == 1
        context_event = context_events[0]
        assert isinstance(context_event, ContextMenuEvent)
        assert context_event.position == pos
        assert context_event.global_position == event.globalPos()

    def test_context_menu_event_with_selection(self, qtbot, mock_embedded_server):
        """Test context menu event with text selection."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        # Mock bridge with selection
        widget.bridge = Mock()
        widget.bridge._last_selection = "selected text"

        pos = QPoint(150, 250)
        event = QContextMenuEvent(QContextMenuEvent.Mouse, pos)

        context_events = []
        widget.contextMenuRequested.connect(lambda e: context_events.append(e))

        widget.contextMenuEvent(event)

        context_event = context_events[0]
        assert context_event.selected_text == "selected text"

    def test_context_menu_event_no_bridge(self, qtbot, mock_embedded_server):
        """Test context menu event when bridge is not available."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        # Ensure no bridge
        widget.bridge = None

        pos = QPoint(50, 75)
        event = QContextMenuEvent(QContextMenuEvent.Mouse, pos)

        context_events = []
        widget.contextMenuRequested.connect(lambda e: context_events.append(e))

        widget.contextMenuEvent(event)

        context_event = context_events[0]
        assert context_event.selected_text == ""  # Should default to empty

    def test_context_menu_event_category_filtering(self, qtbot, mock_embedded_server):
        """Test context menu events respect category filtering."""
        from vfwidgets_terminal import EventConfig

        # Create widget with INTERACTION category disabled
        config = EventConfig(
            enabled_categories={EventCategory.LIFECYCLE}  # No INTERACTION
        )
        widget = TerminalWidget(event_config=config)
        qtbot.addWidget(widget)

        pos = QPoint(100, 100)
        event = QContextMenuEvent(QContextMenuEvent.Mouse, pos)

        context_events = []
        widget.contextMenuRequested.connect(lambda e: context_events.append(e))

        widget.contextMenuEvent(event)

        # Should not emit event because INTERACTION category is disabled
        assert len(context_events) == 0


@pytest.mark.gui
class TestDefaultContextMenu:
    """Test default context menu creation and behavior."""

    @patch("vfwidgets_terminal.terminal.QMenu")
    def test_default_context_menu_no_selection(self, mock_qmenu_class, qtbot, mock_embedded_server):
        """Test default context menu with no text selected."""
        mock_menu = Mock()
        mock_qmenu_class.return_value = mock_menu

        widget = TerminalWidget()
        qtbot.addWidget(widget)

        QPoint(100, 100)
        global_pos = QPoint(500, 400)

        # Call the default context menu method directly
        widget._show_default_context_menu(global_pos, "")

        # Verify menu was created and configured
        mock_qmenu_class.assert_called_once_with(widget)

        # Should have paste action but no copy action (no selection)
        assert mock_menu.addAction.call_count >= 1  # At least paste action

        # Menu should be shown
        mock_menu.exec_.assert_called_once_with(global_pos)

    @patch("vfwidgets_terminal.terminal.QMenu")
    def test_default_context_menu_with_selection(
        self, mock_qmenu_class, qtbot, mock_embedded_server
    ):
        """Test default context menu with text selected."""
        mock_menu = Mock()
        mock_qmenu_class.return_value = mock_menu

        widget = TerminalWidget()
        qtbot.addWidget(widget)

        QPoint(100, 100)
        global_pos = QPoint(500, 400)
        selected_text = "selected terminal text"

        widget._show_default_context_menu(global_pos, selected_text)

        # Should have both copy and paste actions
        assert mock_menu.addAction.call_count >= 2  # Copy, paste, and possibly more

        # Should add separator and clear action
        assert mock_menu.addSeparator.call_count >= 1

    def test_default_context_menu_copy_action(self, qtbot, mock_embedded_server):
        """Test copy action in default context menu."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        selected_text = "text to copy"

        with patch.object(QApplication, "clipboard") as mock_clipboard_func:
            mock_clipboard = Mock()
            mock_clipboard_func.return_value = mock_clipboard

            widget._copy_to_clipboard(selected_text)

            mock_clipboard.setText.assert_called_once_with(selected_text)

    def test_default_context_menu_paste_action(
        self, qtbot, mock_embedded_server, mock_qwebengineview
    ):
        """Test paste action in default context menu."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        # Mock server
        mock_server = Mock()
        widget.server = mock_server

        clipboard_text = "text to paste"

        with patch.object(QApplication, "clipboard") as mock_clipboard_func:
            mock_clipboard = Mock()
            mock_clipboard.text.return_value = clipboard_text
            mock_clipboard_func.return_value = mock_clipboard

            widget._paste_from_clipboard()

            mock_server.send_input.assert_called_once_with(clipboard_text)

    def test_default_context_menu_paste_empty_clipboard(self, qtbot, mock_embedded_server):
        """Test paste action with empty clipboard."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        mock_server = Mock()
        widget.server = mock_server

        with patch.object(QApplication, "clipboard") as mock_clipboard_func:
            mock_clipboard = Mock()
            mock_clipboard.text.return_value = ""  # Empty clipboard
            mock_clipboard_func.return_value = mock_clipboard

            widget._paste_from_clipboard()

            # Should not call send_input with empty text
            mock_server.send_input.assert_not_called()

    def test_default_context_menu_paste_no_server(self, qtbot, mock_embedded_server):
        """Test paste action when server is not available."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        widget.server = None  # No server

        with patch.object(QApplication, "clipboard") as mock_clipboard_func:
            mock_clipboard = Mock()
            mock_clipboard.text.return_value = "some text"
            mock_clipboard_func.return_value = mock_clipboard

            # Should not raise exception
            widget._paste_from_clipboard()

    def test_clear_terminal_action(self, qtbot, mock_embedded_server):
        """Test clear terminal context menu action."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        with patch.object(widget, "clear") as mock_clear:
            widget.clear_terminal()
            mock_clear.assert_called_once()


@pytest.mark.gui
class TestCustomContextMenuHandlers:
    """Test custom context menu handlers and actions."""

    def test_set_custom_context_menu_handler(self, qtbot, mock_embedded_server):
        """Test setting a custom context menu handler."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        custom_handler = Mock()
        custom_handler.return_value = None  # Return None to use default

        widget.set_context_menu_handler(custom_handler)

        assert widget.custom_context_menu_handler == custom_handler

    def test_custom_context_menu_handler_called(self, qtbot, mock_embedded_server):
        """Test custom context menu handler is called."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        custom_handler = Mock()
        custom_menu = Mock()
        custom_handler.return_value = custom_menu

        widget.set_context_menu_handler(custom_handler)

        pos = QPoint(100, 100)
        event = QContextMenuEvent(QContextMenuEvent.Mouse, pos)

        widget.contextMenuEvent(event)

        # Custom handler should be called
        custom_handler.assert_called_once()
        # Custom menu should be shown
        custom_menu.exec_.assert_called_once()

    def test_custom_context_menu_handler_returns_none(self, qtbot, mock_embedded_server):
        """Test custom context menu handler that returns None."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        custom_handler = Mock()
        custom_handler.return_value = None  # Return None for default behavior

        widget.set_context_menu_handler(custom_handler)

        pos = QPoint(100, 100)
        event = QContextMenuEvent(QContextMenuEvent.Mouse, pos)

        with patch.object(widget, "_show_default_context_menu") as mock_default:
            widget.contextMenuEvent(event)

            # Should fall back to default menu
            mock_default.assert_called_once()

    def test_custom_context_menu_handler_exception(self, qtbot, mock_embedded_server):
        """Test custom context menu handler that raises exception."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        custom_handler = Mock()
        custom_handler.side_effect = Exception("Handler error")

        widget.set_context_menu_handler(custom_handler)

        pos = QPoint(100, 100)
        event = QContextMenuEvent(QContextMenuEvent.Mouse, pos)

        with patch.object(widget, "_show_default_context_menu") as mock_default:
            widget.contextMenuEvent(event)

            # Should fall back to default menu after exception
            mock_default.assert_called_once()

    def test_add_custom_context_menu_action(self, qtbot, mock_embedded_server):
        """Test adding custom actions to context menu."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        custom_action = QAction("Custom Action", widget)
        widget.add_context_menu_action(custom_action)

        assert custom_action in widget.custom_context_actions

    def test_remove_custom_context_menu_action(self, qtbot, mock_embedded_server):
        """Test removing custom actions from context menu."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        custom_action = QAction("Custom Action", widget)
        widget.add_context_menu_action(custom_action)
        widget.remove_context_menu_action(custom_action)

        assert custom_action not in widget.custom_context_actions

    def test_clear_custom_context_menu_actions(self, qtbot, mock_embedded_server):
        """Test clearing all custom context menu actions."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        action1 = QAction("Action 1", widget)
        action2 = QAction("Action 2", widget)

        widget.add_context_menu_action(action1)
        widget.add_context_menu_action(action2)

        assert len(widget.custom_context_actions) == 2

        widget.clear_context_menu_actions()

        assert len(widget.custom_context_actions) == 0

    @patch("vfwidgets_terminal.terminal.QMenu")
    def test_custom_actions_in_default_menu(self, mock_qmenu_class, qtbot, mock_embedded_server):
        """Test custom actions are added to default menu."""
        mock_menu = Mock()
        mock_qmenu_class.return_value = mock_menu

        widget = TerminalWidget()
        qtbot.addWidget(widget)

        custom_action = QAction("Custom Action", widget)
        widget.add_context_menu_action(custom_action)

        widget._show_default_context_menu(QPoint(100, 100), "")

        # Should add the custom action to menu
        mock_menu.addAction.assert_any_call(custom_action)


@pytest.mark.gui
class TestDebugWebEngineViewContextMenu:
    """Test DebugWebEngineView context menu interception."""

    def test_debug_web_engine_view_context_menu_interception(self, qtbot):
        """Test DebugWebEngineView intercepts context menu events."""
        from vfwidgets_terminal.terminal import DebugWebEngineView

        view = DebugWebEngineView()
        qtbot.addWidget(view)

        # Connect to right_clicked signal
        right_click_events = []
        view.right_clicked.connect(lambda pos: right_click_events.append(pos))

        pos = QPoint(150, 200)
        event = QContextMenuEvent(QContextMenuEvent.Mouse, pos)

        # Mock parent widget
        mock_parent = Mock()
        mock_parent.contextMenuEvent = Mock()
        with patch.object(view, "parent", return_value=mock_parent):
            view.contextMenuEvent(event)

        # Should emit right_clicked signal
        assert len(right_click_events) == 1
        assert right_click_events[0] == pos

        # Should forward to parent
        mock_parent.contextMenuEvent.assert_called_once_with(event)

    def test_debug_web_engine_view_context_menu_no_parent(self, qtbot):
        """Test DebugWebEngineView context menu when no parent available."""
        from vfwidgets_terminal.terminal import DebugWebEngineView

        view = DebugWebEngineView()
        qtbot.addWidget(view)

        pos = QPoint(100, 100)
        event = QContextMenuEvent(QContextMenuEvent.Mouse, pos)

        # Mock parent to return None
        with patch.object(view, "parent", return_value=None):
            with patch("super") as mock_super:
                view.contextMenuEvent(event)

                # Should call parent class contextMenuEvent
                mock_super.assert_called()

    def test_debug_web_engine_view_context_menu_debug_logging(self, qtbot):
        """Test DebugWebEngineView context menu debug logging."""
        from vfwidgets_terminal.terminal import DebugWebEngineView

        view = DebugWebEngineView()
        qtbot.addWidget(view)

        view.set_debug(True)

        pos = QPoint(75, 125)
        event = QContextMenuEvent(QContextMenuEvent.Mouse, pos)

        mock_parent = Mock()
        mock_parent.contextMenuEvent = Mock()

        with patch.object(view, "parent", return_value=mock_parent):
            with patch("logging.Logger.info") as mock_log:
                view.contextMenuEvent(event)

                # Should log the right-click when debug is enabled
                mock_log.assert_called()


@pytest.mark.gui
class TestContextMenuSignalForwarding:
    """Test context menu signal forwarding to deprecated signals."""

    def test_context_menu_signal_forwarding(self, qtbot, mock_embedded_server):
        """Test contextMenuRequested forwards to deprecated context_menu_requested."""
        widget = TerminalWidget()
        qtbot.addWidget(widget)

        # Connect to both new and old signals
        new_signal_events = []
        old_signal_events = []

        widget.contextMenuRequested.connect(lambda e: new_signal_events.append(e))
        widget.context_menu_requested.connect(
            lambda pos, text: old_signal_events.append((pos, text))
        )

        pos = QPoint(100, 100)
        event = QContextMenuEvent(QContextMenuEvent.Mouse, pos)

        # Mock bridge with selection
        widget.bridge = Mock()
        widget.bridge._last_selection = "test selection"

        widget.contextMenuEvent(event)

        # Both signals should be called
        assert len(new_signal_events) == 1
        assert len(old_signal_events) == 1

        # Check new signal event data
        context_event = new_signal_events[0]
        assert isinstance(context_event, ContextMenuEvent)

        # Check old signal data
        old_pos, old_text = old_signal_events[0]
        assert old_pos == pos
        assert old_text == "test selection"


@pytest.mark.integration
class TestContextMenuIntegration:
    """Integration tests for context menu system."""

    def test_full_context_menu_flow(self, real_terminal_widget, qtbot):
        """Test complete context menu flow with real widget."""
        widget = real_terminal_widget

        # Wait for terminal to be ready
        with qtbot.waitSignal(widget.terminalReady, timeout=10000):
            pass

        # Track context menu events
        context_events = []
        widget.contextMenuRequested.connect(lambda e: context_events.append(e))

        # Simulate right-click
        pos = QPoint(200, 150)
        event = QContextMenuEvent(QContextMenuEvent.Mouse, pos)

        widget.contextMenuEvent(event)

        # Should have captured the event
        assert len(context_events) == 1
        context_event = context_events[0]
        assert context_event.position == pos

    def test_context_menu_with_custom_handler_integration(self, real_terminal_widget, qtbot):
        """Test context menu with custom handler integration."""
        widget = real_terminal_widget

        # Wait for terminal to be ready
        with qtbot.waitSignal(widget.terminalReady, timeout=10000):
            pass

        # Set up custom handler
        custom_menu_calls = []

        def custom_handler(event):
            custom_menu_calls.append(event)
            # Return None to use default menu
            return None

        widget.add_context_menu_handler(custom_handler)

        # Trigger context menu
        pos = QPoint(100, 100)
        event = QContextMenuEvent(QContextMenuEvent.Mouse, pos)

        widget.contextMenuEvent(event)

        # Custom handler should have been called
        assert len(custom_menu_calls) == 1

    @pytest.mark.slow
    def test_context_menu_performance(self, real_terminal_widget, qtbot, performance_timer):
        """Test context menu performance."""
        widget = real_terminal_widget

        # Wait for terminal to be ready
        with qtbot.waitSignal(widget.terminalReady, timeout=10000):
            pass

        performance_timer.start()

        # Trigger multiple context menu events
        for i in range(100):
            pos = QPoint(100 + i, 100 + i)
            event = QContextMenuEvent(QContextMenuEvent.Mouse, pos)
            widget.contextMenuEvent(event)

        performance_timer.stop()

        # Should complete quickly (less than 1 second for 100 events)
        assert performance_timer.elapsed < 1.0

    def test_context_menu_memory_usage(self, real_terminal_widget, qtbot):
        """Test context menu doesn't leak memory."""
        widget = real_terminal_widget

        # Wait for terminal to be ready
        with qtbot.waitSignal(widget.terminalReady, timeout=10000):
            pass

        import gc

        initial_objects = len(gc.get_objects())

        # Create many context menu events
        for i in range(1000):
            pos = QPoint(i % 500, i % 300)
            event = QContextMenuEvent(QContextMenuEvent.Mouse, pos)
            widget.contextMenuEvent(event)

            if i % 100 == 0:
                gc.collect()

        gc.collect()
        final_objects = len(gc.get_objects())

        # Should not have significant memory growth
        # Allow some growth but not proportional to number of events
        assert final_objects - initial_objects < 100
