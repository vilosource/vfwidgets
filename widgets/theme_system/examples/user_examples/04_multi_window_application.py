#!/usr/bin/env python3
"""
Example 04: Multi-Window Application
=====================================

Demonstrates a real application with multiple windows, all synchronized
to the same theme. Shows how theme changes propagate across the entire
application instantly.

What this demonstrates:
- Multiple windows sharing the same theme
- Theme persistence across application restarts
- Dialog theming
- Menu bar theming
- Status bar with theme info
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QMenuBar, QMenu, QStatusBar, QDialog, QLabel, QPushButton,
    QListWidget, QSplitter, QTreeWidget, QTreeWidgetItem,
    QDialogButtonBox, QComboBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction
from vfwidgets_theme import ThemedWidget, ThemedApplication


class ThemedDialog(ThemedWidget, QDialog):
    """A themed dialog window."""

    theme_config = {
        'dialog_bg': 'colors.background',
        'dialog_fg': 'colors.foreground',
        'dialog_accent': 'colors.accent'
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Theme Settings")
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Choose Application Theme")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Theme selector
        self.theme_combo = QComboBox()
        app = ThemedApplication.instance()
        if app:
            self.theme_combo.addItems(app.available_themes)
            current = app.current_theme_name
            if current:
                self.theme_combo.setCurrentText(current)
        layout.addWidget(self.theme_combo)

        # Preview area
        preview_label = QLabel("Preview:")
        layout.addWidget(preview_label)

        self.preview = QTextEdit()
        self.preview.setPlainText(
            "This is a preview of the selected theme.\n"
            "The theme affects all windows and dialogs.\n"
            "Changes are applied instantly."
        )
        self.preview.setMaximumHeight(100)
        layout.addWidget(self.preview)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setMinimumWidth(400)

    def on_theme_changed(self):
        """Update dialog styling."""
        bg = getattr(self.theme, 'dialog_bg', '#ffffff')
        fg = getattr(self.theme, 'dialog_fg', '#000000')
        accent = getattr(self.theme, 'dialog_accent', '#0066cc')

        self.setStyleSheet(f"""
            ThemedDialog {{
                background-color: {bg};
                color: {fg};
            }}
            QLabel {{
                color: {fg};
            }}
            QComboBox {{
                padding: 5px;
                background-color: {bg};
                color: {fg};
                border: 1px solid {accent};
            }}
            QTextEdit {{
                background-color: {bg};
                color: {fg};
                border: 1px solid {accent};
            }}
        """)

    def get_selected_theme(self):
        return self.theme_combo.currentText()


class SidePanel(ThemedWidget, QWidget):
    """A side panel with file tree."""

    theme_config = {
        'panel_bg': 'colors.background',
        'panel_fg': 'colors.foreground',
        'panel_border': 'colors.border'
    }

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # File tree
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Project")

        # Add sample items
        root = QTreeWidgetItem(self.tree, ["My Project"])
        src = QTreeWidgetItem(root, ["src"])
        QTreeWidgetItem(src, ["main.py"])
        QTreeWidgetItem(src, ["widgets.py"])
        QTreeWidgetItem(src, ["themes.py"])

        docs = QTreeWidgetItem(root, ["docs"])
        QTreeWidgetItem(docs, ["README.md"])
        QTreeWidgetItem(docs, ["tutorial.md"])

        self.tree.expandAll()
        layout.addWidget(self.tree)

    def on_theme_changed(self):
        """Update panel styling."""
        bg = getattr(self.theme, 'panel_bg', '#ffffff')
        fg = getattr(self.theme, 'panel_fg', '#000000')
        border = getattr(self.theme, 'panel_border', '#cccccc')

        self.tree.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {bg};
                color: {fg};
                border: 1px solid {border};
            }}
            QTreeWidget::item:selected {{
                background-color: {border};
            }}
        """)


class EditorWindow(ThemedWidget, QMainWindow):
    """A themed editor window."""

    theme_config = {
        'window_bg': 'colors.background',
        'window_fg': 'colors.foreground',
        'editor_bg': 'colors.background',
        'editor_fg': 'colors.foreground'
    }

    def __init__(self, window_number=1):
        super().__init__()
        self.window_number = window_number
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle(f"Editor Window {self.window_number}")
        self.setGeometry(100 + self.window_number * 50, 100 + self.window_number * 50, 800, 600)

        # Central widget with splitter
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # Side panel
        self.side_panel = SidePanel()
        splitter.addWidget(self.side_panel)

        # Editor
        self.editor = QTextEdit()
        self.editor.setPlainText(
            f"# Editor Window {self.window_number}\n\n"
            "This is a themed editor window.\n"
            "All windows share the same theme.\n"
            "Try switching themes from the menu!"
        )
        splitter.addWidget(self.editor)

        splitter.setSizes([200, 600])

        # Menu bar
        self.create_menu_bar()

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status()

        # Update status periodically
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)

    def create_menu_bar(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        new_window = QAction("New Window", self)
        new_window.triggered.connect(self.new_window)
        file_menu.addAction(new_window)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Theme menu
        theme_menu = menubar.addMenu("Theme")

        settings_action = QAction("Theme Settings...", self)
        settings_action.triggered.connect(self.show_theme_settings)
        theme_menu.addAction(settings_action)

        theme_menu.addSeparator()

        # Quick theme switches
        app = ThemedApplication.instance()
        if app:
            for theme_name in app.available_themes:
                action = QAction(theme_name.title(), self)
                action.triggered.connect(lambda checked, name=theme_name: app.set_theme(name))
                theme_menu.addAction(action)

    def new_window(self):
        """Create a new editor window."""
        window = EditorWindow(self.window_number + 1)
        window.show()

    def show_theme_settings(self):
        """Show theme settings dialog."""
        dialog = ThemedDialog(self)
        if dialog.exec() == QDialog.Accepted:
            theme = dialog.get_selected_theme()
            app = ThemedApplication.instance()
            if app:
                app.set_theme(theme)

    def update_status(self):
        """Update status bar with current theme."""
        app = ThemedApplication.instance()
        if app:
            theme = app.current_theme_name
            theme_type = app.theme_type
            self.status_bar.showMessage(f"Theme: {theme} ({theme_type})")

    def on_theme_changed(self):
        """Update window styling."""
        bg = getattr(self.theme, 'window_bg', '#ffffff')
        fg = getattr(self.theme, 'window_fg', '#000000')
        editor_bg = getattr(self.theme, 'editor_bg', '#ffffff')
        editor_fg = getattr(self.theme, 'editor_fg', '#000000')

        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {bg};
            }}
            QMenuBar {{
                background-color: {bg};
                color: {fg};
            }}
            QMenuBar::item:selected {{
                background-color: {fg};
                color: {bg};
            }}
            QMenu {{
                background-color: {bg};
                color: {fg};
            }}
            QMenu::item:selected {{
                background-color: {fg};
                color: {bg};
            }}
            QStatusBar {{
                background-color: {bg};
                color: {fg};
            }}
        """)

        self.editor.setStyleSheet(f"""
            QTextEdit {{
                background-color: {editor_bg};
                color: {editor_fg};
                border: none;
                font-family: 'Courier New', monospace;
                font-size: 14px;
            }}
        """)


def main():
    app = ThemedApplication(sys.argv)

    # Create multiple windows
    window1 = EditorWindow(1)
    window1.show()

    window2 = EditorWindow(2)
    window2.show()

    return app.exec()


if __name__ == '__main__':
    sys.exit(main())