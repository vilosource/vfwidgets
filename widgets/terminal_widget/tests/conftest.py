"""Pytest configuration and shared fixtures for VFWidgets Terminal Widget tests."""

import logging
import os
import sys
from collections.abc import Generator
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from PySide6.QtCore import QTimer  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

# Import our components
from vfwidgets_terminal import (  # noqa: E402
    ContextMenuEvent,
    EmbeddedTerminalServer,
    EventCategory,
    EventConfig,
    KeyEvent,
    ProcessEvent,
    TerminalWidget,
)

# =============================================================================
# Qt Application Setup
# =============================================================================


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for the entire test session."""
    # Check if QApplication already exists
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
        app.setApplicationName("VFWidgets Terminal Tests")

        # Set up for headless testing
        if os.environ.get("CI") or os.environ.get("HEADLESS"):
            app.setQuitOnLastWindowClosed(False)

    yield app

    # Cleanup
    if app is not None:
        app.quit()


@pytest.fixture
def qtbot(qapp, qtbot):
    """Enhanced qtbot with terminal-specific configuration."""
    # Increase timeout for terminal operations
    qtbot.wait_timeout = 15000  # 15 seconds for terminal startup
    return qtbot


# =============================================================================
# Mock Fixtures
# =============================================================================


@pytest.fixture
def mock_embedded_server():
    """Create a mock EmbeddedTerminalServer for unit testing."""
    with patch("vfwidgets_terminal.terminal.EmbeddedTerminalServer") as mock_server_class:
        mock_server = Mock(spec=EmbeddedTerminalServer)
        mock_server.start.return_value = 12345  # Mock port
        mock_server.stop.return_value = 0  # Mock exit code
        mock_server.send_input.return_value = None
        mock_server.get_process_info.return_value = {
            "pid": 1234,
            "command": "bash",
            "running": True,
        }
        mock_server.child_pid = 1234
        mock_server_class.return_value = mock_server
        yield mock_server


@pytest.fixture
def mock_qwebengineview():
    """Mock QWebEngineView to avoid browser engine in tests."""
    with patch("vfwidgets_terminal.terminal.DebugWebEngineView") as mock_view_class:
        mock_view = Mock()
        mock_view.load.return_value = None
        mock_view.loadFinished.connect.return_value = None
        mock_view.page.return_value = Mock()
        mock_view.focusProxy.return_value = Mock()
        mock_view_class.return_value = mock_view
        yield mock_view


@pytest.fixture
def mock_qwebchannel():
    """Mock QWebChannel for JavaScript bridge testing."""
    with patch("vfwidgets_terminal.terminal.QWebChannel") as mock_channel_class:
        mock_channel = Mock()
        mock_channel.registerObject.return_value = None
        mock_channel_class.return_value = mock_channel
        yield mock_channel


# =============================================================================
# Terminal Widget Fixtures
# =============================================================================


@pytest.fixture
def basic_terminal_widget(qtbot, mock_embedded_server) -> TerminalWidget:
    """Create a basic TerminalWidget with mocked server for unit testing."""
    widget = TerminalWidget(debug=True)
    qtbot.addWidget(widget)
    return widget


@pytest.fixture
def terminal_widget_with_config(qtbot, mock_embedded_server) -> TerminalWidget:
    """Create TerminalWidget with custom event configuration."""
    config = EventConfig(
        enabled_categories={
            EventCategory.LIFECYCLE,
            EventCategory.PROCESS,
            EventCategory.INTERACTION,
        },
        debug_logging=True,
        throttle_high_frequency=False,  # For testing
    )

    widget = TerminalWidget(debug=True, event_config=config, capture_output=True)
    qtbot.addWidget(widget)
    return widget


@pytest.fixture
def python_terminal_widget(qtbot, mock_embedded_server) -> TerminalWidget:
    """Create TerminalWidget configured for Python REPL."""
    widget = TerminalWidget(command="python", args=["-i"], debug=True)
    qtbot.addWidget(widget)
    return widget


@pytest.fixture
def real_terminal_widget(qtbot) -> Generator[TerminalWidget, None, None]:
    """Create TerminalWidget with real server for integration testing.

    WARNING: This creates actual processes and network connections.
    Use sparingly and only for integration tests.
    """
    # Don't override QT_QPA_PLATFORM here - let the test runner handle it
    # The test runner will use either Xvfb (preferred) or offscreen platform

    widget = TerminalWidget(
        port=0,  # Random port
        debug=False,  # Disable debug to reduce output
        capture_output=True,
    )
    qtbot.addWidget(widget)

    # Don't show the widget unless explicitly needed
    # widget.show() - commented out to prevent window popup

    yield widget

    # Cleanup
    try:
        widget.close_terminal()
        widget.close()
        widget.deleteLater()
    except Exception:
        pass  # Widget already closed or invalid


# =============================================================================
# Server Fixtures
# =============================================================================


@pytest.fixture
def embedded_server() -> Generator[EmbeddedTerminalServer, None, None]:
    """Create real EmbeddedTerminalServer for integration testing."""
    server = EmbeddedTerminalServer(
        command="bash",
        port=0,  # Random port
        capture_output=True,
    )

    yield server

    # Cleanup
    try:
        server.stop()
    except Exception:
        pass  # Widget already closed or invalid


@pytest.fixture
def python_server() -> Generator[EmbeddedTerminalServer, None, None]:
    """Create EmbeddedTerminalServer with Python command."""
    server = EmbeddedTerminalServer(command="python", args=["-i"], port=0, capture_output=True)

    yield server

    # Cleanup
    try:
        server.stop()
    except Exception:
        pass  # Widget already closed or invalid


# =============================================================================
# Event System Fixtures
# =============================================================================


@pytest.fixture
def sample_process_event() -> ProcessEvent:
    """Create sample ProcessEvent for testing."""
    return ProcessEvent(command="test command", pid=1234, working_directory="/tmp")


@pytest.fixture
def sample_key_event() -> KeyEvent:
    """Create sample KeyEvent for testing."""
    return KeyEvent(key="Enter", code="Enter", ctrl=False, alt=False, shift=False)


@pytest.fixture
def sample_context_menu_event() -> ContextMenuEvent:
    """Create sample ContextMenuEvent for testing."""
    from PySide6.QtCore import QPoint

    return ContextMenuEvent(
        position=QPoint(100, 100),
        global_position=QPoint(500, 300),
        selected_text="sample text",
        cursor_position=(10, 20),
    )


@pytest.fixture
def event_config_all_enabled() -> EventConfig:
    """EventConfig with all categories enabled."""
    return EventConfig(
        enabled_categories=set(EventCategory), debug_logging=True, throttle_high_frequency=False
    )


@pytest.fixture
def event_config_minimal() -> EventConfig:
    """EventConfig with minimal categories enabled."""
    return EventConfig(
        enabled_categories={EventCategory.LIFECYCLE},
        debug_logging=False,
        throttle_high_frequency=True,
    )


# =============================================================================
# Network & Process Fixtures
# =============================================================================


@pytest.fixture
def free_port() -> int:
    """Get a free port for testing."""
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


@pytest.fixture
def temp_working_directory(tmp_path) -> Path:
    """Create temporary directory for process testing."""
    work_dir = tmp_path / "terminal_test"
    work_dir.mkdir()

    # Create some test files
    (work_dir / "test.txt").write_text("test file content")
    (work_dir / "script.sh").write_text("#!/bin/bash\necho 'test script'\n")
    (work_dir / "script.sh").chmod(0o755)

    return work_dir


# =============================================================================
# Performance & Reliability Fixtures
# =============================================================================


@pytest.fixture
def performance_timer():
    """Timer for performance testing."""
    import time

    class PerformanceTimer:
        def __init__(self):
            self.start_time = None
            self.end_time = None

        def start(self):
            self.start_time = time.perf_counter()

        def stop(self):
            self.end_time = time.perf_counter()

        @property
        def elapsed(self) -> float:
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return 0.0

    return PerformanceTimer()


@pytest.fixture
def event_collector():
    """Collect events for testing event flows."""

    class EventCollector:
        def __init__(self):
            self.events = []
            self.event_count = {}

        def collect_event(self, event_type: str, data=None):
            """Collect an event."""
            self.events.append(
                {
                    "type": event_type,
                    "data": data,
                    "timestamp": pytest.approx(0, abs=1e9),  # Current time
                }
            )
            self.event_count[event_type] = self.event_count.get(event_type, 0) + 1

        def get_events_of_type(self, event_type: str) -> list:
            """Get all events of specific type."""
            return [e for e in self.events if e["type"] == event_type]

        def clear(self):
            """Clear collected events."""
            self.events.clear()
            self.event_count.clear()

    return EventCollector()


# =============================================================================
# Test Configuration
# =============================================================================


def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Disable Qt warnings for cleaner test output
    os.environ["QT_LOGGING_RULES"] = "*.debug=false"

    # Set up test-specific environment
    os.environ["VFWIDGETS_NO_AUTO_SETUP"] = "1"  # Disable auto-setup
    os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"  # For testing

    # Configure for headless testing if requested
    if config.getoption("--headless", default=False) or os.environ.get("CI"):
        # If DISPLAY is set (e.g., by Xvfb), use it
        # Otherwise fall back to offscreen platform
        if not os.environ.get("DISPLAY"):
            os.environ["QT_QPA_PLATFORM"] = "offscreen"
            print("Warning: Using offscreen platform. Some tests may fail.")
            print("         Install Xvfb for better test compatibility.")

    # Use virtual display for GUI tests on Linux without display
    if sys.platform.startswith("linux") and not os.environ.get("DISPLAY"):
        # Only set offscreen if not already in headless mode
        if not config.getoption("--headless", default=False):
            os.environ["QT_QPA_PLATFORM"] = "offscreen"

    # Configure logging for tests
    logging.basicConfig(
        level=logging.WARNING,  # Reduce noise in tests
        format="%(name)s - %(levelname)s - %(message)s",
    )


def pytest_runtest_setup(item):
    """Setup for each test."""
    # Mark slow tests
    if "slow" in item.keywords and not item.config.getoption("--slow"):
        pytest.skip("need --slow option to run")


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption("--slow", action="store_true", default=False, help="run slow tests")
    parser.addoption(
        "--integration", action="store_true", default=False, help="run integration tests"
    )
    parser.addoption("--gui", action="store_true", default=False, help="run GUI tests")
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="run tests in headless mode (no GUI windows)",
    )


# =============================================================================
# Utility Functions
# =============================================================================


def wait_for_signal(qtbot, signal, timeout=5000):
    """Utility to wait for Qt signal with better error handling."""
    try:
        with qtbot.waitSignal(signal, timeout=timeout) as blocker:
            pass
        return blocker.args
    except Exception as e:
        pytest.fail(f"Signal {signal} not emitted within {timeout}ms: {e}")


def simulate_terminal_ready(widget, qtbot):
    """Simulate terminal ready state for testing."""
    # Mock the ready signal emission
    QTimer.singleShot(100, lambda: widget.terminalReady.emit())

    # Wait for the signal
    with qtbot.waitSignal(widget.terminalReady, timeout=1000):
        pass
