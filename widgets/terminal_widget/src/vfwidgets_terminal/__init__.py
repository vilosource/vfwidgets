"""VFWidgets Terminal - A powerful PySide6 terminal emulator widget.

This module provides a fully-featured terminal emulator widget that can be
embedded in PySide6/Qt applications. It uses xterm.js for terminal emulation
and Flask/SocketIO for the backend server.

Basic Usage:
    from vfwidgets_terminal import TerminalWidget
    from PySide6.QtWidgets import QApplication, QMainWindow

    app = QApplication([])
    window = QMainWindow()
    terminal = TerminalWidget()
    window.setCentralWidget(terminal)
    window.show()
    app.exec()
"""

__version__ = "0.1.0"
__author__ = "Vilosource"
__email__ = "vilosource@viloforge.com"

# Import presets module (not individual constants to avoid clutter)
from . import presets
from .constants import DEFAULT_COLS, DEFAULT_ROWS, THEMES
from .multi_session_server import MultiSessionTerminalServer
from .session import TerminalSession
from .terminal import (
    ContextMenuEvent,
    DebugWebEngineView,
    EventCategory,
    EventConfig,
    KeyEvent,
    ProcessEvent,
    TerminalBridge,
    TerminalWidget,
)
from .utils import get_default_shell

# Platform-specific imports
import sys

# EmbeddedTerminalServer is Unix-only (uses fcntl, pty, termios)
if sys.platform != "win32":
    from .embedded_server import EmbeddedTerminalServer

__all__ = [
    # Main widget
    "TerminalWidget",
    # Multi-session server
    "MultiSessionTerminalServer",
    "TerminalSession",
    # Event system types (Phase 2 & 3)
    "ProcessEvent",
    "KeyEvent",
    "ContextMenuEvent",
    "EventCategory",
    "EventConfig",
    # Internal classes (for advanced usage)
    "TerminalBridge",
    "DebugWebEngineView",
    # Constants
    "THEMES",
    "DEFAULT_ROWS",
    "DEFAULT_COLS",
    # Configuration presets module
    "presets",
    # Utilities
    "get_default_shell",
]

# Add EmbeddedTerminalServer to exports only on Unix
if sys.platform != "win32":
    __all__.append("EmbeddedTerminalServer")

# Optional: Setup environment for better compatibility
import os


def setup_environment():
    """Setup environment variables for better compatibility in WSL/VM."""
    # Only set if not already configured
    if "QT_OPENGL" not in os.environ:
        os.environ["QT_OPENGL"] = "software"
    if "QTWEBENGINE_DISABLE_SANDBOX" not in os.environ:
        os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"


# Auto-setup can be disabled by setting VFWIDGETS_NO_AUTO_SETUP=1
if os.environ.get("VFWIDGETS_NO_AUTO_SETUP") != "1":
    setup_environment()
