#!/usr/bin/env python3
"""Advanced IDE Example - Production-Ready Patterns

This example demonstrates a more realistic IDE implementation with:
- Tab widget for multiple open files
- Working file operations
- Search with results
- Theme-based styling for main pane widgets
- Best practices for real-world usage

What you'll learn:
- Integrating ChromeTabbedWindow (if available) or QTabWidget
- Managing multiple document tabs
- Real file I/O operations
- Search functionality with results display
- Styling main pane widgets using theme system colors
- Getting theme colors with get_theme_manager() and theme.get_color()
- Extensible architecture for production use

Run this example:
    python examples/05_advanced_ide.py
"""

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QColor, QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenuBar,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from vfwidgets_vilocode_window import ViloCodeWindow

# Check for optional widgets
try:
    from chrome_tabbed_window import ChromeTabbedWindow

    CHROME_TABS_AVAILABLE = True
except ImportError:
    CHROME_TABS_AVAILABLE = False


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


class FileExplorerPanel(QWidget):
    """File explorer panel with working file operations."""

    def __init__(self, root_path: Path, on_file_open) -> None:
        """Initialize file explorer.

        Args:
            root_path: Root directory to explore
            on_file_open: Callback when file is double-clicked
        """
        super().__init__()
        self.root_path = root_path
        self.on_file_open = on_file_open

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("FILES")
        self.tree.setStyleSheet(
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
        layout.addWidget(self.tree)

        self._populate_tree()
        self.tree.itemDoubleClicked.connect(self._on_item_double_clicked)

    def _populate_tree(self) -> None:
        """Populate tree with files."""
        root_item = QTreeWidgetItem(self.tree)
        root_item.setText(0, f"📁 {self.root_path.name}")
        root_item.setExpanded(True)
        root_item.setData(0, Qt.ItemDataRole.UserRole, self.root_path)

        self._add_directory(root_item, self.root_path)

    def _add_directory(self, parent_item: QTreeWidgetItem, dir_path: Path) -> None:
        """Add directory contents recursively."""
        try:
            entries = sorted(dir_path.iterdir(), key=lambda p: (not p.is_dir(), p.name))
            for entry in entries:
                if entry.name.startswith("."):
                    continue

                item = QTreeWidgetItem(parent_item)
                if entry.is_dir():
                    item.setText(0, f"📁 {entry.name}")
                    item.setData(0, Qt.ItemDataRole.UserRole, entry)
                    # Add first level only
                    if len(entry.parts) - len(self.root_path.parts) < 2:
                        self._add_directory(item, entry)
                else:
                    icon = "🐍" if entry.suffix == ".py" else "📄"
                    item.setText(0, f"{icon} {entry.name}")
                    item.setData(0, Qt.ItemDataRole.UserRole, entry)
        except PermissionError:
            pass

    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """Handle double-click on item."""
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if path and path.is_file():
            self.on_file_open(path)


class SearchPanel(QWidget):
    """Search panel with working search functionality."""

    def __init__(self, root_path: Path, on_result_click) -> None:
        """Initialize search panel.

        Args:
            root_path: Root directory to search in
            on_result_click: Callback when result is clicked
        """
        super().__init__()
        self.root_path = root_path
        self.on_result_click = on_result_click

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Search input
        input_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search in files...")
        self.search_button = QPushButton("🔍 Search")
        input_layout.addWidget(self.search_input)
        input_layout.addWidget(self.search_button)
        layout.addLayout(input_layout)

        # Results list
        self.results_list = QListWidget()
        self.results_list.setStyleSheet(
            """
            QListWidget {
                background-color: #1e1e1e;
                color: #cccccc;
                border: none;
            }
            QListWidget::item:selected {
                background-color: #094771;
            }
        """
        )
        layout.addWidget(self.results_list)

        # Connect signals
        self.search_button.clicked.connect(self._perform_search)
        self.search_input.returnPressed.connect(self._perform_search)
        self.results_list.itemDoubleClicked.connect(self._on_result_double_clicked)

    def _perform_search(self) -> None:
        """Perform search in files."""
        search_text = self.search_input.text().strip()
        if not search_text:
            return

        self.results_list.clear()
        self.results_list.addItem(f"Searching for '{search_text}'...")

        # Search in Python files only (for demo)
        results = []
        for py_file in self.root_path.rglob("*.py"):
            if any(part.startswith(".") for part in py_file.parts):
                continue
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()
                    if search_text.lower() in content.lower():
                        # Count occurrences
                        count = content.lower().count(search_text.lower())
                        results.append((py_file, count))
            except Exception:
                pass

        self.results_list.clear()
        if results:
            for path, count in sorted(results, key=lambda x: x[1], reverse=True):
                rel_path = path.relative_to(self.root_path)
                item = QListWidgetItem(f"📄 {rel_path} ({count} matches)")
                item.setData(Qt.ItemDataRole.UserRole, path)
                self.results_list.addItem(item)
        else:
            self.results_list.addItem("No results found")

    def _on_result_double_clicked(self, item: QListWidgetItem) -> None:
        """Handle double-click on result."""
        path = item.data(Qt.ItemDataRole.UserRole)
        if path:
            self.on_result_click(path)


def get_editor_stylesheet() -> str:
    """Get editor stylesheet using theme colors if available.

    Returns:
        CSS stylesheet string for QTextEdit
    """
    try:
        from vfwidgets_theme import get_theme_manager

        theme_manager = get_theme_manager()
        theme = theme_manager.get_current_theme()

        # Get editor colors from theme
        bg = theme.get_color("editor.background") or "#1e1e1e"
        fg = theme.get_color("editor.foreground") or "#d4d4d4"

        return f"""
            QTextEdit {{
                background-color: {bg};
                color: {fg};
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 14px;
                border: none;
            }}
        """
    except ImportError:
        # Fallback if theme system not available
        return """
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 14px;
                border: none;
            }
        """


def main() -> None:
    """Create an advanced IDE window."""
    app = QApplication(sys.argv)

    # IMPORTANT: Set a theme with proper VS Code tab tokens for ChromeTabbedWindow
    #
    # ChromeTabbedWindow looks best with themes that include VS Code tab.* tokens:
    # - "Dark Default" / "Light Default" → Full Chrome-style tab appearance
    # - "default" / "dark" → Generic fallback colors (less refined)
    #
    # Without proper tokens, tabs will use generic colors.primary/colors.hover fallbacks
    try:
        from vfwidgets_theme.core.manager import ThemeManager

        theme_manager = ThemeManager.get_instance()
        try:
            # Use "Dark Default" which has all VS Code tab tokens:
            # tab.activeBackground, tab.inactiveBackground, tab.activeForeground, etc.
            theme_manager.set_theme("Dark Default")
            print("✓ Using 'Dark Default' theme with full VS Code tab styling")
        except Exception:
            print("ℹ Using default theme (tabs will use generic fallback colors)")
    except ImportError:
        pass  # Theme system not available, widgets will use hardcoded fallback colors

    window = ViloCodeWindow()
    window.setWindowTitle("ViloCodeWindow - Advanced IDE")
    window.resize(1400, 900)

    # ==================== Tab Widget for Multiple Files ====================
    # Use ChromeTabbedWindow if available, fallback to QTabWidget
    if CHROME_TABS_AVAILABLE:
        # Pass window as parent to use embedded mode (no window controls)
        tab_widget = ChromeTabbedWindow(parent=window)
        # ChromeTabbedWindow has built-in theme integration, no manual styling needed
        print("✓ Using ChromeTabbedWindow for tabs (embedded mode)")
    else:
        tab_widget = QTabWidget()
        tab_widget.setTabsClosable(True)
        print("✗ ChromeTabbedWindow not available, using QTabWidget")

        # Demonstrate how to style main pane widgets using theme system
        # Get theme colors from the theme manager if available
        try:
            from vfwidgets_theme import get_theme_manager

            theme_manager = get_theme_manager()
            theme = theme_manager.get_current_theme()

            # Get VS Code tab colors from theme
            tab_bg = theme.get_color("tab.inactiveBackground") or "#2d2d2d"
            tab_fg = theme.get_color("tab.inactiveForeground") or "#969696"
            tab_active_bg = theme.get_color("tab.activeBackground") or "#1e1e1e"
            tab_active_fg = theme.get_color("tab.activeForeground") or "#ffffff"
            tab_hover_bg = theme.get_color("tab.hoverBackground") or "#323232"
            editor_bg = theme.get_color("editor.background") or "#1e1e1e"
            border = theme.get_color("tab.border") or "#1e1e1e"

            # Apply theme-based stylesheet
            tab_widget.setStyleSheet(
                f"""
                QTabWidget::pane {{
                    background-color: {editor_bg};
                    border: none;
                }}
                QTabBar::tab {{
                    background-color: {tab_bg};
                    color: {tab_fg};
                    padding: 8px 12px;
                    border: none;
                    border-right: 1px solid {border};
                }}
                QTabBar::tab:selected {{
                    background-color: {tab_active_bg};
                    color: {tab_active_fg};
                }}
                QTabBar::tab:hover {{
                    background-color: {tab_hover_bg};
                    color: {tab_active_fg};
                }}
            """
            )
        except ImportError:
            # Fallback to hardcoded VS Code Dark+ colors if theme system not available
            tab_widget.setStyleSheet(
                """
                QTabWidget::pane {
                    background-color: #1e1e1e;
                    border: none;
                }
                QTabBar::tab {
                    background-color: #2d2d2d;
                    color: #969696;
                    padding: 8px 12px;
                    border: none;
                    border-right: 1px solid #1e1e1e;
                }
                QTabBar::tab:selected {
                    background-color: #1e1e1e;
                    color: #ffffff;
                }
                QTabBar::tab:hover {
                    background-color: #323232;
                    color: #ffffff;
                }
            """
            )

    # Store open files
    open_files = {}  # path -> (tab_index, editor)

    def open_file(path: Path) -> None:
        """Open a file in a new tab or switch to existing tab."""
        if path in open_files:
            # File already open, switch to it
            tab_index, _ = open_files[path]
            tab_widget.setCurrentIndex(tab_index)
            window.set_status_message(f"📄 {path.name} (already open)")
            return

        # Read file content
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()

            editor = QTextEdit()
            editor.setPlainText(content)
            # Apply theme-based styling
            editor.setStyleSheet(get_editor_stylesheet())

            tab_index = tab_widget.addTab(editor, path.name)
            tab_widget.setCurrentIndex(tab_index)
            open_files[path] = (tab_index, editor)

            window.set_status_message(f"✓ Opened {path.name}")
        except Exception as e:
            window.set_status_message(f"✗ Error opening {path.name}: {e}")

    window.set_main_content(tab_widget)

    # Open a welcome tab
    welcome_editor = QTextEdit()
    welcome_editor.setPlainText(
        """# Welcome to Advanced IDE Example!

This example demonstrates production-ready patterns:

## Features
✓ Tab widget for multiple open files
✓ Working file explorer (double-click to open)
✓ Search functionality (search in *.py files)
✓ Real file I/O operations
✓ Theme-based styling for main pane widgets
✓ Clean architecture with reusable components

## Try It
1. Double-click files in the Explorer to open them
2. Use Search to find text in Python files
3. Multiple tabs are supported (close with X button)
4. All features use public API only

## Architecture
This example shows how to build a real IDE:
- FileExplorerPanel: Reusable file browser
- SearchPanel: Working search functionality
- Tab management: Multiple documents
- Event handling: Proper signal/slot patterns
- Theme integration: get_editor_stylesheet() helper

## Styling Main Pane Widgets
This example demonstrates how to style widgets in the main pane:
✓ Get theme colors from get_theme_manager()
✓ Use theme.get_color() for VS Code tokens
✓ Apply via setStyleSheet() with theme colors
✓ Graceful fallback when theme system unavailable

See get_editor_stylesheet() and tab widget styling code.

## Public API Used
✓ set_main_content(tab_widget)
✓ add_activity_item() / add_sidebar_panel()
✓ set_auxiliary_content()
✓ Signal connections for interactivity
✓ All component APIs

Start by double-clicking a .py file in the Explorer!
"""
    )
    # Apply theme-based styling to welcome editor
    welcome_editor.setStyleSheet(get_editor_stylesheet())
    tab_widget.addTab(welcome_editor, "Welcome")

    # ==================== Sidebar Panels ====================
    root_path = Path.cwd()

    explorer = FileExplorerPanel(root_path, open_file)
    search = SearchPanel(root_path, open_file)

    window.add_sidebar_panel("explorer", explorer, "EXPLORER")
    window.add_sidebar_panel("search", search, "SEARCH")

    # ==================== Activity Bar ====================
    window.add_activity_item("explorer", create_icon_from_text("📁"), "Explorer")
    window.add_activity_item("search", create_icon_from_text("🔍"), "Search")

    window.set_active_activity_item("explorer")

    # Connect activity bar to sidebar
    def on_activity_clicked(item_id: str) -> None:
        window.show_sidebar_panel(item_id)

    window.activity_item_clicked.connect(on_activity_clicked)

    def on_panel_changed(panel_id: str) -> None:
        window.set_active_activity_item(panel_id)

    window.sidebar_panel_changed.connect(on_panel_changed)

    # ==================== Menu Bar ====================
    menubar = QMenuBar()
    file_menu = menubar.addMenu("File")

    new_action = QAction("New File", window)
    new_action.setShortcut("Ctrl+N")
    file_menu.addAction(new_action)

    close_tab_action = QAction("Close Tab", window)
    close_tab_action.setShortcut("Ctrl+W")
    close_tab_action.triggered.connect(lambda: tab_widget.removeTab(tab_widget.currentIndex()))
    file_menu.addAction(close_tab_action)

    window.set_menu_bar(menubar)

    # ==================== Initial Status ====================
    window.set_status_message(
        "Advanced IDE ready | Double-click files to open | Search in *.py files | "
        "Multiple tabs supported"
    )

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
