#!/usr/bin/env python3
"""Example 05: File Navigation

Demonstrates:
- reveal_file() - Expand parents and scroll to file
- highlight_file() - Select file without expanding
- find_file() - Search with fuzzy matching
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from vfwidgets_workspace import WorkspaceWidget


class NavigationExample(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Navigation Example")
        self.resize(1200, 700)

        # Layout
        central = QWidget()
        layout = QVBoxLayout(central)

        # Search section
        layout.addWidget(QLabel("Search Files (fuzzy matching):"))
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to search (e.g., 'readme' or 'init')")
        self.search_input.textChanged.connect(self.search_files)
        self.search_btn = QPushButton("Find Exact")
        self.search_btn.clicked.connect(lambda: self.search_files(fuzzy=False))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)
        layout.addLayout(search_layout)

        # Results list
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.reveal_selected_result)
        layout.addWidget(QLabel("Results (double-click to reveal):"))
        layout.addWidget(self.results_list)

        # Workspace
        self.workspace = WorkspaceWidget()
        layout.addWidget(self.workspace)

        self.setCentralWidget(central)

        # Open workspace
        self.workspace.open_workspace(Path.cwd())

    def search_files(self, fuzzy: bool = True):
        """Search for files."""
        query = self.search_input.text()

        if not query:
            self.results_list.clear()
            return

        # Find files
        results = self.workspace.find_file(query, fuzzy=fuzzy)

        # Display results
        self.results_list.clear()
        for file_path in results[:50]:  # Limit to 50 results
            # Show relative path for readability
            try:
                rel_path = Path(file_path).relative_to(Path.cwd())
            except ValueError:
                rel_path = Path(file_path)

            self.results_list.addItem(str(rel_path))
            self.results_list.item(self.results_list.count() - 1).setData(
                0x0100,
                file_path,  # UserRole
            )

        if not results:
            self.results_list.addItem("No matches found")
        elif len(results) > 50:
            self.results_list.addItem(f"... and {len(results) - 50} more")

    def reveal_selected_result(self, item):
        """Reveal selected file in workspace."""
        file_path = item.data(0x0100)  # UserRole
        if file_path:
            # Reveal file (expands parents, scrolls to view)
            success = self.workspace.reveal_file(file_path)
            if success:
                print(f"Revealed: {file_path}")


def main():
    app = QApplication(sys.argv)
    window = NavigationExample()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
