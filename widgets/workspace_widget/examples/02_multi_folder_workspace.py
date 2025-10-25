#!/usr/bin/env python3
"""Example 02: Multi-Folder Workspace

Demonstrates:
- Loading workspace configuration from .workspace.json
- Multiple workspace folders in one workspace
- Folder hierarchy display
"""

import json
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget
from vfwidgets_workspace import WorkspaceWidget


class MultiFolderWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-Folder Workspace Example")
        self.resize(800, 600)

        # Create layout
        central = QWidget()
        layout = QVBoxLayout(central)

        # Status label
        self.status = QLabel("No workspace open")
        layout.addWidget(self.status)

        # Workspace widget
        self.workspace = WorkspaceWidget()
        layout.addWidget(self.workspace)

        self.setCentralWidget(central)

        # Connect signals
        self.workspace.workspace_opened.connect(self.on_workspace_opened)
        self.workspace.file_selected.connect(self.on_file_selected)

        # Create example config
        self.create_example_config()

        # Open workspace
        self.workspace.open_workspace(Path.cwd())

    def create_example_config(self):
        """Create example .workspace.json config."""
        config = {
            "version": 1,
            "name": "Example Multi-Folder Project",
            "folders": [
                {"path": str(Path.cwd() / "src"), "name": "Source Code"},
                {"path": str(Path.cwd() / "tests"), "name": "Tests"},
                {"path": str(Path.cwd() / "examples"), "name": "Examples"},
            ],
            "excluded_folders": ["node_modules", "__pycache__", ".git"],
        }

        config_path = Path.cwd() / ".workspace.json"

        # Only create if doesn't exist
        if not config_path.exists():
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)
            print(f"Created example config: {config_path}")

    def on_workspace_opened(self, folders):
        """Handle workspace opened."""
        folder_count = len(folders)
        folder_names = [f.name for f in folders]

        self.status.setText(f"Workspace opened: {folder_count} folders - {', '.join(folder_names)}")

    def on_file_selected(self, file_path: str):
        """Handle file selection."""
        self.status.setText(f"Selected: {Path(file_path).name}")


def main():
    app = QApplication(sys.argv)
    window = MultiFolderWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
