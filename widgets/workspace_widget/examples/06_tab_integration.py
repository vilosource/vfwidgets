#!/usr/bin/env python3
"""Example 06: Tab Integration

Demonstrates:
- sync_with_tab_widget() - Auto-highlight file when tab changes
- Opening files in tabs
- Bidirectional workspace ↔ tabs synchronization
"""

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QSplitter, QTabWidget, QTextEdit
from vfwidgets_workspace import WorkspaceWidget


class EditorTab(QTextEdit):
    """Simple text editor tab with file_path attribute."""

    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self.file_path = file_path  # Required for sync

        # Load file
        try:
            with open(file_path, encoding="utf-8") as f:
                self.setPlainText(f.read())
        except Exception as e:
            self.setPlainText(f"Error loading file: {e}")


class TabIntegrationExample(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tab Integration Example")
        self.resize(1400, 800)

        # Main layout
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Workspace
        self.workspace = WorkspaceWidget()
        self.workspace.file_double_clicked.connect(self.open_file_in_tab)
        splitter.addWidget(self.workspace)

        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.tab_widget.removeTab)
        splitter.addWidget(self.tab_widget)

        splitter.setSizes([300, 1100])
        self.setCentralWidget(splitter)

        # Enable auto-sync: when tab changes, highlight file in workspace
        self.workspace.sync_with_tab_widget(
            self.tab_widget, file_path_attr="file_path", auto_sync=True
        )

        # Open workspace
        self.workspace.open_workspace(Path.cwd())

    def open_file_in_tab(self, file_path: str):
        """Open file in new tab."""
        file_name = Path(file_path).name

        # Check if already open
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            if hasattr(tab, "file_path") and tab.file_path == file_path:
                # Already open - switch to it
                self.tab_widget.setCurrentIndex(i)
                return

        # Only open text files
        path = Path(file_path)
        if path.suffix not in [".py", ".md", ".txt", ".json", ".toml", ".yaml", ".yml"]:
            print(f"Skipping non-text file: {file_path}")
            return

        # Open new tab
        editor = EditorTab(file_path)
        index = self.tab_widget.addTab(editor, file_name)
        self.tab_widget.setCurrentIndex(index)

        # Note: When tab switches, workspace automatically highlights the file
        # (due to sync_with_tab_widget)


def main():
    app = QApplication(sys.argv)
    window = TabIntegrationExample()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
