#!/usr/bin/env python3
"""Example 05: Portable Workspace Files

Demonstrates:
- Saving workspace to portable .workspace file
- Loading workspace from file
- Workspace files can be stored anywhere
- Switching between different workspace files
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from vfwidgets_workspace import WorkspaceWidget


class PortableWorkspaceExample(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Portable Workspace Files Example")
        self.resize(900, 600)

        # Layout
        central = QWidget()
        layout = QVBoxLayout(central)

        # Instructions
        info = QLabel(
            "<b>Portable Workspace Files:</b><br>"
            "1. Open a folder<br>"
            "2. Save workspace to .workspace file (can be saved anywhere)<br>"
            "3. Close workspace<br>"
            "4. Load workspace file → All folders and structure restored!<br>"
            "<br>"
            "<i>Workspace files are portable - share them, put them in git, etc.</i>"
        )
        layout.addWidget(info)

        # Buttons
        btn_layout = QHBoxLayout()

        self.open_folder_btn = QPushButton("Open Folder")
        self.save_workspace_btn = QPushButton("Save Workspace File...")
        self.load_workspace_btn = QPushButton("Load Workspace File...")
        self.close_btn = QPushButton("Close Workspace")

        self.open_folder_btn.clicked.connect(self.open_folder)
        self.save_workspace_btn.clicked.connect(self.save_workspace_file)
        self.load_workspace_btn.clicked.connect(self.load_workspace_file)
        self.close_btn.clicked.connect(self.close_workspace)

        btn_layout.addWidget(self.open_folder_btn)
        btn_layout.addWidget(self.save_workspace_btn)
        btn_layout.addWidget(self.load_workspace_btn)
        btn_layout.addWidget(self.close_btn)

        layout.addLayout(btn_layout)

        # Status
        self.status = QLabel("No workspace open")
        layout.addWidget(self.status)

        # Workspace
        self.workspace = WorkspaceWidget()
        self.workspace.workspace_opened.connect(self.on_opened)
        self.workspace.workspace_closed.connect(self.on_closed)
        layout.addWidget(self.workspace)

        self.setCentralWidget(central)

        self.update_buttons()

    def open_folder(self):
        """Open folder as workspace."""
        folder = QFileDialog.getExistingDirectory(self, "Open Workspace Folder", str(Path.cwd()))

        if folder:
            success = self.workspace.open_workspace(Path(folder))
            if success:
                self.status.setText(f"Opened folder: {folder}")

    def save_workspace_file(self):
        """Save workspace to portable file."""
        if not self.workspace._manager.get_folders():
            self.status.setText("⚠️ No workspace to save")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Workspace File",
            str(Path.home() / "my-workspace.workspace"),
            "Workspace Files (*.workspace)",
        )

        if file_path:
            success = self.workspace._manager.save_workspace_file(Path(file_path))
            if success:
                self.status.setText(f"✅ Saved workspace to: {file_path}")
            else:
                self.status.setText("❌ Failed to save workspace")

    def load_workspace_file(self):
        """Load workspace from portable file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Workspace File", str(Path.home()), "Workspace Files (*.workspace)"
        )

        if file_path:
            success = self.workspace._manager.load_workspace_file(Path(file_path))
            if success:
                folders = self.workspace._manager.get_folders()
                self.status.setText(
                    f"✅ Loaded workspace: {Path(file_path).name} ({len(folders)} folders)"
                )
            else:
                self.status.setText("❌ Failed to load workspace")

    def close_workspace(self):
        """Close workspace."""
        self.workspace.close_workspace()

    def on_opened(self, folders):
        self.status.setText(f"✅ Workspace opened ({len(folders)} folders)")
        self.update_buttons()

    def on_closed(self):
        self.status.setText("Workspace closed")
        self.update_buttons()

    def update_buttons(self):
        """Update button states based on workspace status."""
        has_workspace = bool(self.workspace._manager.get_folders())

        self.open_folder_btn.setEnabled(True)
        self.save_workspace_btn.setEnabled(has_workspace)
        self.load_workspace_btn.setEnabled(True)
        self.close_btn.setEnabled(has_workspace)


def main():
    app = QApplication(sys.argv)
    window = PortableWorkspaceExample()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
