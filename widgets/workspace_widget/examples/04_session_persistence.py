#!/usr/bin/env python3
"""Example 04: Session Persistence

Demonstrates:
- Automatic session save/restore
- Expanded folders persistence
- Scroll position preservation
- Active file restoration
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from vfwidgets_workspace import WorkspaceWidget


class SessionExample(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Session Persistence Example")
        self.resize(800, 600)

        # Layout
        central = QWidget()
        layout = QVBoxLayout(central)

        # Instructions
        info = QLabel(
            "1. Expand some folders in the tree\n"
            "2. Select a file\n"
            "3. Close workspace\n"
            "4. Re-open workspace\n"
            "→ Expanded folders and active file are restored!"
        )
        layout.addWidget(info)

        # Buttons
        btn_layout = QHBoxLayout()
        self.open_btn = QPushButton("Open Workspace")
        self.close_btn = QPushButton("Close Workspace")
        self.open_btn.clicked.connect(self.open_workspace)
        self.close_btn.clicked.connect(self.close_workspace)
        btn_layout.addWidget(self.open_btn)
        btn_layout.addWidget(self.close_btn)
        layout.addLayout(btn_layout)

        # Status
        self.status = QLabel("No workspace open")
        layout.addWidget(self.status)

        # Workspace (session persistence enabled by default)
        self.workspace = WorkspaceWidget()
        self.workspace.workspace_opened.connect(self.on_opened)
        self.workspace.workspace_closed.connect(self.on_closed)
        self.workspace.active_file_changed.connect(self.on_file_changed)
        layout.addWidget(self.workspace)

        self.setCentralWidget(central)

        self.workspace_path = Path.cwd()

        # Auto-open
        self.open_workspace()

    def open_workspace(self):
        """Open workspace (session auto-restored)."""
        success = self.workspace.open_workspace(self.workspace_path)
        if success:
            self.status.setText(f"Workspace opened: {self.workspace_path}")
            self.open_btn.setEnabled(False)
            self.close_btn.setEnabled(True)

    def close_workspace(self):
        """Close workspace (session auto-saved)."""
        self.workspace.close_workspace()

    def on_opened(self, folders):
        self.status.setText(f"✅ Workspace opened ({len(folders)} folders) - Session restored")

    def on_closed(self):
        self.status.setText("Workspace closed - Session saved")
        self.open_btn.setEnabled(True)
        self.close_btn.setEnabled(False)

    def on_file_changed(self, file_path: str):
        self.status.setText(f"Active file: {Path(file_path).name}")


def main():
    app = QApplication(sys.argv)
    window = SessionExample()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
