#!/usr/bin/env python3
"""Example 01: Basic Single Folder Workspace

Demonstrates:
- Opening a single folder workspace
- Handling file selection signal
- Minimal working example
"""

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QSplitter, QTextEdit
from vfwidgets_workspace import WorkspaceWidget


class BasicWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Basic Workspace Example")
        self.resize(1000, 700)

        # Create workspace widget
        self.workspace = WorkspaceWidget()

        # Create text display
        self.text_display = QTextEdit()
        self.text_display.setPlaceholderText("Select a file from the workspace...")

        # Layout with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.workspace)
        splitter.addWidget(self.text_display)
        splitter.setSizes([250, 750])

        self.setCentralWidget(splitter)

        # Connect signals
        self.workspace.file_selected.connect(self.on_file_selected)

        # Open workspace (current directory for demo)
        workspace_path = Path.cwd()
        self.workspace.open_workspace(workspace_path)

    def on_file_selected(self, file_path: str):
        """Handle file selection."""
        print(f"Selected: {file_path}")

        # Load and display file content (text files only)
        path = Path(file_path)

        if path.suffix in [".txt", ".md", ".py", ".json", ".toml"]:
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
                self.text_display.setPlainText(content)
            except Exception as e:
                self.text_display.setPlainText(f"Error reading file: {e}")
        else:
            self.text_display.setPlainText(f"File: {file_path}\n\nBinary or unsupported file type")


def main():
    app = QApplication(sys.argv)
    window = BasicWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
