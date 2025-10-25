#!/usr/bin/env python3
"""Example 03: File Filtering

Demonstrates:
- Filtering files by extension
- Custom filter callbacks
- Excluded folders
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QComboBox, QLabel, QMainWindow, QVBoxLayout, QWidget
from vfwidgets_workspace import FileInfo, WorkspaceFolder, WorkspaceWidget


class FilterExample(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Filtering Example")
        self.resize(800, 600)

        # Layout
        central = QWidget()
        layout = QVBoxLayout(central)

        # Filter selector
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(
            [
                "All Files",
                "Python Files (.py)",
                "Markdown Files (.md)",
                "Config Files (.json, .toml)",
                "Custom: Only README files",
            ]
        )
        self.filter_combo.currentTextChanged.connect(self.change_filter)
        layout.addWidget(QLabel("Filter:"))
        layout.addWidget(self.filter_combo)

        # Workspace
        self.workspace = WorkspaceWidget(
            excluded_folders=["__pycache__", ".git", "node_modules", ".venv"]
        )
        layout.addWidget(self.workspace)

        self.setCentralWidget(central)

        # Open workspace
        self.workspace.open_workspace(Path.cwd())

    def change_filter(self, filter_name: str):
        """Change active filter."""
        self.workspace.close_workspace()

        if filter_name == "Python Files (.py)":
            workspace = WorkspaceWidget(
                file_extensions=[".py"], excluded_folders=["__pycache__", ".git"]
            )
        elif filter_name == "Markdown Files (.md)":
            workspace = WorkspaceWidget(file_extensions=[".md"], excluded_folders=[".git"])
        elif filter_name == "Config Files (.json, .toml)":
            workspace = WorkspaceWidget(
                file_extensions=[".json", ".toml", ".yaml", ".yml"], excluded_folders=[".git"]
            )
        elif filter_name == "Custom: Only README files":
            # Custom callback filter
            def readme_filter(file_info: FileInfo, workspace_folder: WorkspaceFolder) -> bool:
                # Show all directories
                if file_info.is_dir:
                    return True
                # Only show README files
                name = Path(file_info.path).name.lower()
                return name.startswith("readme")

            workspace = WorkspaceWidget(filter_callback=readme_filter, excluded_folders=[".git"])
        else:  # All Files
            workspace = WorkspaceWidget(excluded_folders=["__pycache__", ".git", "node_modules"])

        # Replace widget
        old_workspace = self.workspace
        layout = self.centralWidget().layout()
        layout.replaceWidget(old_workspace, workspace)
        old_workspace.deleteLater()
        self.workspace = workspace

        # Open workspace
        self.workspace.open_workspace(Path.cwd())


def main():
    app = QApplication(sys.argv)
    window = FilterExample()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
