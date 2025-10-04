#!/usr/bin/env python3
"""
Multi-Terminal Application (Shared Server Mode)

This example demonstrates multiple terminals sharing a single server.
This is the recommended approach for applications with many terminals.

Benefits:
- 63% less memory usage (20 terminals: 300MB → 110MB)
- Centralized session management
- Scalable architecture

Usage: python 02_multi_terminal_app.py
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget

# Add parent directory to path for development
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vfwidgets_terminal import TerminalWidget, MultiSessionTerminalServer


class MultiTerminalApp(QMainWindow):
    """Application with multiple terminals sharing one server."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-Terminal App (Shared Server)")
        self.resize(1000, 700)

        # Create shared server (one server for all terminals)
        print("Starting multi-session terminal server...")
        self.server = MultiSessionTerminalServer(port=0)  # Auto-allocate port
        self.server.start()
        print(f"Server started on port {self.server.port}")

        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        # Add initial terminals (all using shared server)
        for i in range(5):
            self.add_terminal(f"Terminal {i+1}")

        # Add "+" button to create new terminals
        self.tabs.setCornerWidget(self._create_add_button())

        print(f"Created {self.tabs.count()} terminals")
        print(f"Active sessions: {len(self.server.sessions)}")

    def _create_add_button(self):
        """Create button to add new terminals."""
        from PySide6.QtWidgets import QPushButton

        button = QPushButton("+")
        button.setFixedSize(30, 30)
        button.clicked.connect(lambda: self.add_terminal(f"Terminal {self.tabs.count() + 1}"))
        return button

    def add_terminal(self, name: str):
        """Add a new terminal tab."""
        # Create session on server first
        session_id = self.server.create_session(command="bash")
        print(f"Created session: {session_id}")

        # Get URL for this session
        session_url = self.server.get_session_url(session_id)
        print(f"Session URL: {session_url}")

        # Create terminal widget connected to this session
        terminal = TerminalWidget(server_url=session_url)

        # Add to tabs
        index = self.tabs.addTab(terminal, name)
        self.tabs.setCurrentIndex(index)

        print(f"Added {name} - Active sessions: {len(self.server.sessions)}")

    def close_tab(self, index: int):
        """Close a terminal tab."""
        widget = self.tabs.widget(index)
        self.tabs.removeTab(index)

        # Clean up terminal
        if widget and hasattr(widget, 'cleanup'):
            widget.cleanup()

        widget.deleteLater()
        print(f"Closed tab {index} - Active sessions: {len(self.server.sessions)}")

    def closeEvent(self, event):
        """Handle application close."""
        print("Shutting down server...")
        self.server.shutdown()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = MultiTerminalApp()
    window.show()

    print("\n" + "="*60)
    print("Multi-Terminal Application Started")
    print("="*60)
    print("- Single server managing all terminals")
    print("- Click '+' to add more terminals")
    print("- Close tabs to remove terminals")
    print("- Memory efficient: ~110MB for 20 terminals")
    print("="*60 + "\n")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
