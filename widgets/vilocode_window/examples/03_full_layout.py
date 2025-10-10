#!/usr/bin/env python3
"""Full Layout Example - All Components Together

This example demonstrates the complete VS Code-style IDE layout:
[Activity Bar] [Sidebar] [Main Content] [Auxiliary Bar]

What you'll learn:
- Using all four main components together
- Creating multiple sidebar panels (files, search, git)
- Adding an auxiliary bar for secondary content (outline)
- Building a cohesive IDE experience
- Managing visibility of all components

Run this example:
    python examples/03_full_layout.py
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
    """Create an icon from Unicode text/emoji."""
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


def create_outline_tree() -> QTreeWidget:
    """Create document outline tree widget."""
    tree = QTreeWidget()
    tree.setHeaderLabel("OUTLINE")
    tree.setStyleSheet(
        """
        QTreeWidget {
            background-color: #252526;
            color: #cccccc;
            border: none;
        }
        QTreeWidget::item {
            padding: 4px;
        }
        QTreeWidget::item:selected {
            background-color: #094771;
        }
        QTreeWidget::item:hover {
            background-color: #2a2d2e;
        }
    """
    )

    # Add sample outline structure
    root = QTreeWidgetItem(tree)
    root.setText(0, "📄 Document")
    root.setExpanded(True)

    h1 = QTreeWidgetItem(root)
    h1.setText(0, "# Full Layout Demo")
    h1.setExpanded(True)

    section1 = QTreeWidgetItem(h1)
    section1.setText(0, "## Components")
    item1 = QTreeWidgetItem(section1)
    item1.setText(0, "  • Activity Bar")
    item2 = QTreeWidgetItem(section1)
    item2.setText(0, "  • Sidebar")
    item3 = QTreeWidgetItem(section1)
    item3.setText(0, "  • Main Content")
    item4 = QTreeWidgetItem(section1)
    item4.setText(0, "  • Auxiliary Bar")

    section2 = QTreeWidgetItem(h1)
    section2.setText(0, "## Features")

    return tree


def create_file_tree(root_path: Path) -> QTreeWidget:
    """Create file explorer tree widget."""
    tree = QTreeWidget()
    tree.setHeaderLabel("FILES")
    tree.setStyleSheet(
        """
        QTreeWidget {
            background-color: #252526;
            color: #cccccc;
            border: none;
        }
        QTreeWidget::item:selected {
            background-color: #094771;
        }
    """
    )

    root_item = QTreeWidgetItem(tree)
    root_item.setText(0, f"📁 {root_path.name}")
    root_item.setExpanded(True)

    try:
        for entry in sorted(root_path.iterdir(), key=lambda p: (not p.is_dir(), p.name)):
            if entry.name.startswith("."):
                continue
            item = QTreeWidgetItem(root_item)
            icon = "📁" if entry.is_dir() else ("🐍" if entry.suffix == ".py" else "📄")
            item.setText(0, f"{icon} {entry.name}")
    except PermissionError:
        pass

    return tree


def main() -> None:
    """Create a window with complete IDE layout."""
    app = QApplication(sys.argv)

    window = ViloCodeWindow()
    window.setWindowTitle("ViloCodeWindow - Full Layout")
    window.resize(1400, 800)

    # ==================== Main Content ====================
    editor = QTextEdit()
    editor.setPlainText(
        """# Full Layout Demo

This example shows the complete VS Code IDE layout with all four components:

┌──────────────────────────────────────────────────────────────┐
│ [Activity Bar] [Sidebar] [Main Content] [Auxiliary Bar]      │
└──────────────────────────────────────────────────────────────┘

Components:
✓ Activity Bar - Left icon bar (48px wide)
✓ Sidebar - Left panel with multiple views (Explorer, Search, Git)
✓ Main Content - Center area (this editor)
✓ Auxiliary Bar - Right panel for secondary content (Outline)

Features demonstrated:
✓ Multiple sidebar panels switching
✓ Activity bar → Sidebar integration
✓ Auxiliary bar with outline view
✓ Resize handles on sidebars
✓ Independent visibility control for each component

Try:
1. Click activity bar icons to switch sidebar panels
2. Drag sidebar edges to resize
3. Press Ctrl+B to toggle sidebar
4. Press Alt+O to toggle auxiliary bar (custom shortcut)
5. Browse the file tree and outline

Public API used:
- add_activity_item(id, icon, tooltip)
- add_sidebar_panel(id, widget, title)
- set_auxiliary_content(widget)
- register_custom_shortcut(name, key, callback, description)
- All visibility and state management methods
"""
    )
    window.set_main_content(editor)

    # ==================== Sidebar Panels ====================
    # Explorer panel
    explorer = create_file_tree(Path.cwd())

    # Search panel
    search_widget = QWidget()
    search_layout = QVBoxLayout(search_widget)
    search_layout.setContentsMargins(10, 10, 10, 10)
    search_label = QLabel("🔍 Search in Files")
    search_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #cccccc;")
    search_text = QTextEdit()
    search_text.setPlainText(
        "Enter search term to find in workspace...\n\n"
        "This would integrate with a real search backend."
    )
    search_layout.addWidget(search_label)
    search_layout.addWidget(search_text)

    # Source Control panel
    git_widget = QWidget()
    git_layout = QVBoxLayout(git_widget)
    git_layout.setContentsMargins(10, 10, 10, 10)
    git_label = QLabel("⎇ Source Control")
    git_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #cccccc;")
    git_text = QTextEdit()
    git_text.setPlainText(
        "SOURCE CONTROL\n\n"
        "Would show:\n"
        "• Changed files\n"
        "• Staged changes\n"
        "• Commit history\n"
        "• Branch information\n"
        "• Push/pull status"
    )
    git_layout.addWidget(git_label)
    git_layout.addWidget(git_text)

    # Add all sidebar panels
    window.add_sidebar_panel("explorer", explorer, "EXPLORER")
    window.add_sidebar_panel("search", search_widget, "SEARCH")
    window.add_sidebar_panel("git", git_widget, "SOURCE CONTROL")

    # ==================== Activity Bar ====================
    explorer_icon = create_icon_from_text("📁")
    search_icon = create_icon_from_text("🔍")
    git_icon = create_icon_from_text("⎇")

    window.add_activity_item("explorer", explorer_icon, "Explorer (Ctrl+Shift+E)")
    window.add_activity_item("search", search_icon, "Search (Ctrl+Shift+F)")
    window.add_activity_item("git", git_icon, "Source Control (Ctrl+Shift+G)")

    window.set_active_activity_item("explorer")

    # ==================== Auxiliary Bar ====================
    outline = create_outline_tree()
    window.set_auxiliary_content(outline)
    window.set_auxiliary_bar_visible(True)

    # ==================== Connect Components ====================
    def on_activity_clicked(item_id: str) -> None:
        window.show_sidebar_panel(item_id)
        panel_names = {"explorer": "Explorer", "search": "Search", "git": "Source Control"}
        window.set_status_message(f"📂 {panel_names.get(item_id, item_id)} panel active")

    window.activity_item_clicked.connect(on_activity_clicked)

    def on_panel_changed(panel_id: str) -> None:
        window.set_active_activity_item(panel_id)

    window.sidebar_panel_changed.connect(on_panel_changed)

    def on_file_clicked(item: QTreeWidgetItem, column: int) -> None:
        file_name = item.text(0).split(" ", 1)[-1]
        window.set_status_message(f"📄 {file_name}")

    explorer.itemClicked.connect(on_file_clicked)

    def on_outline_clicked(item: QTreeWidgetItem, column: int) -> None:
        section = item.text(0).strip()
        window.set_status_message(f"📝 {section}")

    outline.itemClicked.connect(on_outline_clicked)

    # ==================== Custom Shortcuts ====================
    # Add custom shortcut for auxiliary bar toggle
    window.register_custom_shortcut(
        "toggle_auxiliary_bar",
        "Alt+O",
        window.toggle_auxiliary_bar,
        "Toggle Auxiliary Bar",
    )

    # ==================== Status ====================
    window.set_status_message(
        "Full IDE layout active | Ctrl+B: toggle sidebar | Alt+O: toggle auxiliary bar | "
        "Drag edges to resize"
    )

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
