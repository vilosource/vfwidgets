#!/usr/bin/env python3
"""Test harness for OSC 7 working directory tracking.

This example demonstrates OSC 7 working directory tracking in action:
1. Terminal on the left starts in $HOME
2. Click "cd /tmp" to change directory in the focused terminal
3. Click "Split Right" to create a new terminal
4. The new terminal should inherit the CWD from the focused terminal

The debug console at the bottom shows:
- Terminal creation events
- CWD changes from OSC 7
- Split operations

Usage:
    python examples/test_osc7_tracking.py

Expected behavior (after full implementation):
- cd /tmp in Terminal 1
- Split Right → Terminal 2 starts in /tmp (not $HOME)
- cd /var in Terminal 2
- Focus Terminal 1, Split Right → Terminal 3 starts in /tmp (not /var)
"""

import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QPlainTextEdit,
    QSplitter,
    QLabel,
)
from PySide6.QtCore import Qt

from vfwidgets_terminal import MultiSessionTerminalServer, TerminalWidget
from vfwidgets_multisplit import MultisplitWidget, WidgetProvider, WherePosition


class DebugConsole(QPlainTextEdit):
    """Read-only debug console for logging."""

    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setMaximumHeight(200)
        self.setStyleSheet(
            """
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Courier New', monospace;
                font-size: 10pt;
            }
        """
        )

    def log(self, message: str):
        """Append a log message."""
        self.appendPlainText(f"[DEBUG] {message}")


class TerminalProvider(WidgetProvider):
    """Provides terminal widgets for MultisplitWidget."""

    def __init__(self, server: MultiSessionTerminalServer, debug_console: DebugConsole):
        self.server = server
        self.debug_console = debug_console
        self.pane_to_terminal: dict[str, TerminalWidget] = {}
        self.pane_to_cwd: dict[str, str] = {}  # Will track CWD per pane
        self._next_cwd: str | None = None  # CWD for next terminal

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Create a terminal widget for a pane."""
        # Get CWD for new terminal (if set by split operation)
        cwd = self._next_cwd
        self._next_cwd = None  # Clear for next use

        # Create session with CWD
        session_id = self.server.create_session(cwd=cwd)
        session_url = self.server.get_session_url(session_id)

        terminal = TerminalWidget(server_url=session_url, cwd=cwd)
        self.pane_to_terminal[pane_id] = terminal

        # Connect CWD tracking signal
        terminal.workingDirectoryChanged.connect(
            lambda cwd: self._on_terminal_cwd_changed(pane_id, cwd)
        )

        if cwd:
            self.debug_console.log(
                f"Created terminal for pane {pane_id[:8]}... with CWD: {cwd}"
            )
        else:
            self.debug_console.log(f"Created terminal for pane {pane_id[:8]}...")

        return terminal

    def _on_terminal_cwd_changed(self, pane_id: str, cwd: str):
        """Track CWD changes for each pane."""
        self.pane_to_cwd[pane_id] = cwd
        self.debug_console.log(f"✓ Pane {pane_id[:8]}: CWD → {cwd}")

    def set_next_cwd(self, cwd: str | None):
        """Set CWD for the next terminal to be created."""
        self._next_cwd = cwd
        if cwd:
            self.debug_console.log(f"→ Set next terminal CWD: {cwd}")

    def widget_closing(self, widget_id: str, pane_id: str, widget: QWidget) -> None:
        """Clean up when terminal closes."""
        if pane_id in self.pane_to_terminal:
            del self.pane_to_terminal[pane_id]
        if pane_id in self.pane_to_cwd:
            del self.pane_to_cwd[pane_id]
        self.debug_console.log(f"Closed terminal for pane {pane_id[:8]}...")


class OSC7TestHarness(QMainWindow):
    """Test harness for OSC 7 working directory tracking."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("OSC 7 Working Directory Test Harness")
        self.resize(1200, 800)

        # Create terminal server
        self.server = MultiSessionTerminalServer(port=0)
        self.server.start()

        # Create debug console
        self.debug_console = DebugConsole()
        self.debug_console.log("=" * 60)
        self.debug_console.log("OSC 7 Working Directory Test Harness")
        self.debug_console.log("=" * 60)
        self.debug_console.log("Test harness initialized")

        # Create terminal provider
        self.provider = TerminalProvider(self.server, self.debug_console)

        # Create main layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Title label
        title = QLabel("OSC 7 Working Directory Test Harness")
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title)

        # Instructions
        instructions = QLabel(
            "Instructions: (1) Click 'cd /tmp' to change directory, "
            "(2) Click 'Split Right' to create a new terminal that should inherit the CWD, "
            "(3) Watch the debug console below for OSC 7 events"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; font-size: 9pt;")
        layout.addWidget(instructions)

        # Create vertical splitter (terminals top, debug console bottom)
        splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(splitter)

        # Top section: MultisplitWidget + controls
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(5)

        # Control buttons
        button_layout = QHBoxLayout()

        self.btn_cd_tmp = QPushButton("cd /tmp")
        self.btn_cd_tmp.setToolTip("Change directory to /tmp in focused terminal")
        self.btn_cd_tmp.clicked.connect(self._on_cd_tmp)
        button_layout.addWidget(self.btn_cd_tmp)

        self.btn_cd_home = QPushButton("cd ~")
        self.btn_cd_home.setToolTip("Change directory to home in focused terminal")
        self.btn_cd_home.clicked.connect(self._on_cd_home)
        button_layout.addWidget(self.btn_cd_home)

        self.btn_cd_var = QPushButton("cd /var")
        self.btn_cd_var.setToolTip("Change directory to /var in focused terminal")
        self.btn_cd_var.clicked.connect(self._on_cd_var)
        button_layout.addWidget(self.btn_cd_var)

        self.btn_split = QPushButton("Split Right")
        self.btn_split.setToolTip(
            "Split the focused pane to the right (new terminal should inherit CWD)"
        )
        self.btn_split.clicked.connect(self._on_split_right)
        button_layout.addWidget(self.btn_split)

        self.btn_pwd = QPushButton("pwd")
        self.btn_pwd.setToolTip("Print working directory in focused terminal")
        self.btn_pwd.clicked.connect(self._on_pwd)
        button_layout.addWidget(self.btn_pwd)

        button_layout.addStretch()
        top_layout.addLayout(button_layout)

        # MultisplitWidget with initial terminal
        self.multisplit = MultisplitWidget(provider=self.provider)
        top_layout.addWidget(self.multisplit)

        splitter.addWidget(top_widget)

        # Debug console with label
        debug_widget = QWidget()
        debug_widget.setContentsMargins(0, 0, 0, 0)
        debug_layout = QVBoxLayout(debug_widget)
        debug_layout.setContentsMargins(0, 0, 0, 0)
        debug_layout.setSpacing(0)

        debug_label = QLabel("Debug Console (OSC 7 events will appear here)")
        debug_label.setStyleSheet("font-weight: bold;")
        debug_label.setContentsMargins(0, 0, 0, 0)

        debug_layout.addWidget(debug_label)
        debug_layout.addWidget(self.debug_console)
        splitter.addWidget(debug_widget)

        # Fix QSplitter handle styling - this might be the issue
        splitter.setHandleWidth(1)
        splitter.setStyleSheet(
            """
            QSplitter::handle {
                background-color: #3c3c3c;
            }
        """
        )

        # Set initial sizes - give terminals most of the space
        splitter.setSizes([600, 200])  # Terminals: 600px, Debug: 200px
        splitter.setStretchFactor(0, 3)  # Terminals get more space
        splitter.setStretchFactor(1, 1)  # Debug console smaller

        self.debug_console.log("Harness UI created")
        self.debug_console.log(
            "Initial terminal will appear shortly - check for creation event"
        )

    def _get_focused_terminal(self) -> TerminalWidget | None:
        """Get the currently focused terminal widget."""
        focused_pane = self.multisplit.get_focused_pane()
        if not focused_pane:
            return None
        return self.provider.pane_to_terminal.get(focused_pane)

    def _on_cd_tmp(self):
        """Send 'cd /tmp' to focused terminal."""
        terminal = self._get_focused_terminal()
        if terminal:
            terminal.send_input("cd /tmp\n")
            self.debug_console.log("→ Sent command: cd /tmp")
        else:
            self.debug_console.log("ERROR: No focused terminal")

    def _on_cd_home(self):
        """Send 'cd ~' to focused terminal."""
        terminal = self._get_focused_terminal()
        if terminal:
            terminal.send_input("cd ~\n")
            self.debug_console.log("→ Sent command: cd ~")
        else:
            self.debug_console.log("ERROR: No focused terminal")

    def _on_cd_var(self):
        """Send 'cd /var' to focused terminal."""
        terminal = self._get_focused_terminal()
        if terminal:
            terminal.send_input("cd /var\n")
            self.debug_console.log("→ Sent command: cd /var")
        else:
            self.debug_console.log("ERROR: No focused terminal")

    def _on_pwd(self):
        """Send 'pwd' to focused terminal."""
        terminal = self._get_focused_terminal()
        if terminal:
            terminal.send_input("pwd\n")
            self.debug_console.log("→ Sent command: pwd")
        else:
            self.debug_console.log("ERROR: No focused terminal")

    def _on_split_right(self):
        """Split the focused pane to the right."""
        focused_pane = self.multisplit.get_focused_pane()
        if not focused_pane:
            self.debug_console.log("ERROR: No focused pane to split")
            return

        # Get CWD from focused terminal
        focused_cwd = self.provider.pane_to_cwd.get(focused_pane)
        if focused_cwd:
            self.debug_console.log(f"→ Focused pane CWD: {focused_cwd}")
            self.provider.set_next_cwd(focused_cwd)
        else:
            self.debug_console.log("⚠ WARNING: No CWD tracked for focused pane")

        self.debug_console.log(f"→ Splitting pane {focused_pane[:8]}... to the right")

        new_widget_id = f"terminal_right_{id(self)}_{focused_pane[:4]}"
        success = self.multisplit.split_pane(
            focused_pane, new_widget_id, WherePosition.RIGHT, ratio=0.5
        )

        if success:
            self.debug_console.log(f"✓ Split successful: {new_widget_id[:16]}...")
        else:
            self.debug_console.log("✗ ERROR: Split failed")

    def closeEvent(self, event):
        """Clean up on close."""
        self.debug_console.log("Shutting down server...")
        self.server.shutdown()
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)

    window = OSC7TestHarness()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
