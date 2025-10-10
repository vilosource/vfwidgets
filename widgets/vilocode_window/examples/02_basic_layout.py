#!/usr/bin/env python3
"""Basic Layout Example - Activity Bar + Sidebar + Main Content

This example demonstrates the 3-column VS Code-style layout:
[Activity Bar] [Sidebar] [Main Content]

What you'll learn:
- Adding activity bar items with add_activity_item()
- Creating sidebar panels with add_sidebar_panel()
- Connecting activity bar clicks to sidebar panels
- Building a simple file explorer
- Using signals for component interaction

Run this example:
    python examples/02_basic_layout.py
"""

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from vfwidgets_vilocode_window import ViloCodeWindow


def create_icon_from_text(text: str, size: int = 24) -> QIcon:
    """Create an icon from Unicode text/emoji.

    Args:
        text: Unicode character or emoji
        size: Icon size in pixels

    Returns:
        QIcon with the text rendered
    """
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    font = QFont("Segoe UI Symbol", int(size * 0.6))
    painter.setFont(font)
    painter.setPen(QColor("#cccccc"))

    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, text)
    painter.end()

    return QIcon(pixmap)


def create_file_tree(root_path: Path) -> QTreeWidget:
    """Create a file explorer tree widget.

    Args:
        root_path: Root directory to display

    Returns:
        QTreeWidget with file tree
    """
    tree = QTreeWidget()
    tree.setHeaderLabel("FILES")
    tree.setStyleSheet(
        """
        QTreeWidget {
            background-color: #252526;
            color: #cccccc;
            border: none;
        }
        QTreeWidget::item {
            padding: 3px;
        }
        QTreeWidget::item:selected {
            background-color: #094771;
        }
        QTreeWidget::item:hover {
            background-color: #2a2d2e;
        }
    """
    )

    # Add root folder
    root_item = QTreeWidgetItem(tree)
    root_item.setText(0, f"📁 {root_path.name}")
    root_item.setExpanded(True)

    # Add immediate children only (not recursive for simplicity)
    try:
        entries = sorted(root_path.iterdir(), key=lambda p: (not p.is_dir(), p.name))
        for entry in entries:
            if entry.name.startswith("."):
                continue

            item = QTreeWidgetItem(root_item)
            if entry.is_dir():
                item.setText(0, f"📁 {entry.name}")
            else:
                icon = "🐍" if entry.suffix == ".py" else "📄"
                item.setText(0, f"{icon} {entry.name}")
    except PermissionError:
        pass

    return tree


def main() -> None:
    """Create a window with basic VS Code layout."""
    app = QApplication(sys.argv)

    window = ViloCodeWindow()
    window.setWindowTitle("ViloCodeWindow - Basic Layout")
    window.resize(1200, 700)

    # ==================== Main Content ====================
    editor = QTextEdit()
    editor.setPlainText(
        """# Basic Layout Demo

This example shows the VS Code 3-column layout:
[Activity Bar] [Sidebar] [Main Content]

Features demonstrated:
✓ Activity bar with icons on the left
✓ Sidebar with multiple panels
✓ File explorer in the sidebar
✓ Search panel (placeholder)
✓ Signal-based communication between components

Try:
1. Click activity bar items to switch sidebar panels
2. Resize the sidebar by dragging its right edge
3. Browse the file tree in the Explorer panel
4. Press Ctrl+B to toggle sidebar visibility

Public API used:
- add_activity_item(id, icon, tooltip)
- add_sidebar_panel(id, widget, title)
- show_sidebar_panel(id)
- set_active_activity_item(id)
- Signals: activity_item_clicked, sidebar_panel_changed
"""
    )
    window.set_main_content(editor)

    # ==================== Sidebar Panels ====================
    # Explorer panel with file tree
    explorer = create_file_tree(Path.cwd())

    # Search panel (placeholder)
    search_widget = QWidget()
    search_layout = QVBoxLayout(search_widget)
    search_layout.setContentsMargins(10, 10, 10, 10)
    search_title = QLabel("🔍 Search")
    search_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #cccccc;")
    search_content = QTextEdit()
    search_content.setPlainText("Search functionality would go here...")
    search_layout.addWidget(search_title)
    search_layout.addWidget(search_content)

    # Add panels to sidebar
    window.add_sidebar_panel("explorer", explorer, "EXPLORER")
    window.add_sidebar_panel("search", search_widget, "SEARCH")

    # ==================== Activity Bar ====================
    explorer_icon = create_icon_from_text("📁")
    search_icon = create_icon_from_text("🔍")

    window.add_activity_item("explorer", explorer_icon, "Explorer (Ctrl+Shift+E)")
    window.add_activity_item("search", search_icon, "Search (Ctrl+Shift+F)")

    # Set first item as active
    window.set_active_activity_item("explorer")

    # ==================== Connect Components ====================
    # When activity item clicked, show corresponding sidebar panel
    def on_activity_clicked(item_id: str) -> None:
        window.show_sidebar_panel(item_id)
        window.set_status_message(f"📂 Showing {item_id} panel")

    window.activity_item_clicked.connect(on_activity_clicked)

    # When sidebar panel changes, update active activity item
    def on_panel_changed(panel_id: str) -> None:
        window.set_active_activity_item(panel_id)

    window.sidebar_panel_changed.connect(on_panel_changed)

    # File tree click handler
    def on_file_clicked(item: QTreeWidgetItem, column: int) -> None:
        file_name = item.text(0).split(" ", 1)[-1]
        window.set_status_message(f"📄 Selected: {file_name}")

    explorer.itemClicked.connect(on_file_clicked)

    # ==================== Status ====================
    window.set_status_message(
        "Click activity bar items to switch panels | Drag sidebar edge to resize | Press Ctrl+B to toggle"
    )

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
