"""Sidebar Demo - Demonstrates sidebar with multiple panels.

Shows how to add panels to the sidebar and switch between them.
Includes a real file explorer using QTreeWidget.
"""

import sys
from pathlib import Path

from PySide6.QtGui import QIcon
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
    """Create an icon from text/unicode symbol."""
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QColor, QFont, QPainter, QPixmap

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


def main() -> None:
    """Run the sidebar demo."""
    app = QApplication(sys.argv)

    # Create window
    window = ViloCodeWindow()
    window.setWindowTitle("Sidebar Demo - Multiple Panels")
    window.resize(1000, 700)

    # Add main content
    editor = QTextEdit()
    editor.setPlainText(
        """# Sidebar Demo

The sidebar on the left shows multiple stackable panels.

Features demonstrated:
- add_activity_item() - Add activity bar icons
- add_sidebar_panel() - Add panels to sidebar
- activity_item_clicked signal - Switch panels on click
- Resizable sidebar - Drag the right edge of sidebar
- Panel switching - Click activity bar items to switch panels
- Real file tree - QTreeWidget showing current directory structure

Try:
1. Click different activity bar items to switch sidebar panels
2. Browse the file tree in the Explorer panel
3. Expand/collapse folders by clicking them
4. Drag the right edge of the sidebar to resize it
5. Press Ctrl+B to toggle sidebar visibility
"""
    )
    window.set_main_content(editor)

    # Create sidebar panels
    # Explorer panel - Real file tree
    explorer = QTreeWidget()
    explorer.setHeaderLabel("FILES")
    explorer.setStyleSheet(
        """
        QTreeWidget {
            background-color: #252526;
            color: #cccccc;
            border: none;
            outline: none;
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
        QTreeWidget::branch:has-children:!has-siblings:closed,
        QTreeWidget::branch:closed:has-children:has-siblings {
            image: none;
        }
        QTreeWidget::branch:open:has-children:!has-siblings,
        QTreeWidget::branch:open:has-children:has-siblings {
            image: none;
        }
    """
    )

    def populate_tree(tree: QTreeWidget, root_path: Path) -> None:
        """Populate tree widget with files and directories.

        Args:
            tree: QTreeWidget to populate
            root_path: Root directory path
        """
        tree.clear()

        # Add root folder
        root_item = QTreeWidgetItem(tree)
        root_item.setText(0, f"📁 {root_path.name}")
        root_item.setExpanded(True)

        def add_directory(parent_item: QTreeWidgetItem, dir_path: Path) -> None:
            """Recursively add directory contents.

            Args:
                parent_item: Parent tree item
                dir_path: Directory path to add
            """
            try:
                # Get all entries and sort them (directories first, then files)
                entries = sorted(dir_path.iterdir(), key=lambda p: (not p.is_dir(), p.name))

                for entry in entries:
                    # Skip hidden files and __pycache__
                    if entry.name.startswith(".") or entry.name == "__pycache__":
                        continue

                    item = QTreeWidgetItem(parent_item)

                    if entry.is_dir():
                        item.setText(0, f"📁 {entry.name}")
                        # Add subdirectories (limit depth to avoid performance issues)
                        if len(entry.parts) - len(root_path.parts) < 3:
                            add_directory(item, entry)
                    else:
                        # Choose icon based on file extension
                        icon = "📄"
                        suffix = entry.suffix.lower()
                        if suffix in [".py"]:
                            icon = "🐍"
                        elif suffix in [".md", ".txt"]:
                            icon = "📝"
                        elif suffix in [".json", ".yaml", ".yml", ".toml"]:
                            icon = "⚙️"
                        elif suffix in [".png", ".jpg", ".jpeg", ".gif", ".svg"]:
                            icon = "🖼️"
                        elif suffix in [".html", ".css", ".js", ".ts"]:
                            icon = "🌐"

                        item.setText(0, f"{icon} {entry.name}")

            except PermissionError:
                # Skip directories we can't read
                pass

        # Populate from current directory
        current_dir = Path.cwd()
        add_directory(root_item, current_dir)

    # Populate the explorer tree
    populate_tree(explorer, Path.cwd())

    # Handle file/folder clicks
    def on_tree_item_clicked(item: QTreeWidgetItem, column: int) -> None:
        """Handle tree item click.

        Args:
            item: Clicked tree item
            column: Column index
        """
        file_name = item.text(0)
        # Remove emoji prefix
        clean_name = file_name.split(" ", 1)[-1] if " " in file_name else file_name
        window.set_status_message(f"📂 Selected: {clean_name}")

    explorer.itemClicked.connect(on_tree_item_clicked)

    # Search panel
    search_widget = QWidget()
    search_layout = QVBoxLayout(search_widget)
    search_layout.setContentsMargins(10, 10, 10, 10)
    search_title = QLabel("🔍 Search")
    search_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #cccccc;")
    search_content = QTextEdit()
    search_content.setPlainText("Search functionality would go here...")
    search_layout.addWidget(search_title)
    search_layout.addWidget(search_content)

    # Source Control panel
    source_control = QTextEdit()
    source_control.setPlainText(
        """SOURCE CONTROL

Git integration panel.

Would show:
- Changed files
- Staged changes
- Commit history
- Branch info
"""
    )

    # Add panels to sidebar
    window.add_sidebar_panel("explorer", explorer, "EXPLORER")
    window.add_sidebar_panel("search", search_widget, "SEARCH")
    window.add_sidebar_panel("source_control", source_control, "SOURCE CONTROL")

    # Add activity bar items
    explorer_icon = create_icon_from_text("📁")
    search_icon = create_icon_from_text("🔍")
    source_control_icon = create_icon_from_text("⎇")

    window.add_activity_item("explorer", explorer_icon, "Explorer (Ctrl+Shift+E)")
    window.add_activity_item("search", search_icon, "Search (Ctrl+Shift+F)")
    window.add_activity_item("source_control", source_control_icon, "Source Control (Ctrl+Shift+G)")

    # Set first item as active
    window.set_active_activity_item("explorer")

    # Connect activity bar to sidebar - switch panels on click
    def on_activity_clicked(item_id: str) -> None:
        window.show_sidebar_panel(item_id)
        window.set_status_message(f"📂 Showing panel: {item_id}")

    window.activity_item_clicked.connect(on_activity_clicked)

    # Show panel change notifications
    def on_panel_changed(panel_id: str) -> None:
        # Update active activity item when panel changes
        window.set_active_activity_item(panel_id)
        print(f"Panel changed to: {panel_id}")

    window.sidebar_panel_changed.connect(on_panel_changed)

    # Show visibility change notifications
    def on_visibility_changed(is_visible: bool) -> None:
        status = "visible" if is_visible else "hidden"
        window.set_status_message(f"👁 Sidebar is now {status} (press Ctrl+B to toggle)")
        print(f"Sidebar visibility: {is_visible}")

    window.sidebar_visibility_changed.connect(on_visibility_changed)

    # Set initial status
    window.set_status_message(
        "Click activity bar items to switch panels | "
        "Drag sidebar edge to resize | "
        "Press Ctrl+B to toggle visibility"
    )

    # Show window
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
