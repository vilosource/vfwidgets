#!/usr/bin/env python3
"""Example 06: Production App - Complete Application Pattern
=============================================================

A production-quality code editor application demonstrating best practices
for building real applications with the VFWidgets theme system.

What you'll learn:
- Complete application structure (menus, toolbars, status bar)
- Complex layouts with splitters
- File operations (New, Open, Save, Close)
- Settings/preferences dialog
- Best practices for production apps

Features:
- Sidebar with file explorer
- Tabbed editor area with monospace font
- Menu bar with shortcuts (Ctrl+N, Ctrl+O, Ctrl+S)
- Settings dialog for theme selection
- Status bar showing file info and current theme
- Zero inline styles - everything from theme system!

This is a complete, working text editor you could actually use!

Run:
    python examples/06_production_app.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
)

from vfwidgets_theme import (
    ThemedApplication,
    ThemedDialog,
    ThemedMainWindow,
    ThemedQWidget,
    ThemedWidget,
    WidgetRole,
    set_widget_role,
)


class SettingsDialog(ThemedDialog):
    """Application settings dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumSize(450, 250)
        self.setup_ui()

    def setup_ui(self):
        """Setup UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Theme selection
        layout.addWidget(QLabel("Application Theme:"))

        self.theme_combo = QComboBox()
        self.theme_combo.setMinimumHeight(36)

        app = ThemedApplication.instance()
        if app:
            self.theme_combo.addItems(app.available_themes)
            current = str(app.current_theme_name)
            index = self.theme_combo.findText(current)
            if index >= 0:
                self.theme_combo.setCurrentIndex(index)

        layout.addWidget(self.theme_combo)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        apply_btn = QPushButton("Apply")
        apply_btn.setMinimumSize(80, 32)
        apply_btn.clicked.connect(self.apply_theme)
        button_layout.addWidget(apply_btn)

        ok_btn = QPushButton("OK")
        ok_btn.setMinimumSize(80, 32)
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumSize(80, 32)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def apply_theme(self):
        """Apply selected theme."""
        theme = self.theme_combo.currentText()
        app = ThemedApplication.instance()
        if app and theme:
            app.set_theme(theme)


class CodeEditor(ThemedWidget, QTextEdit):
    """Text editor with syntax highlighting role."""

    def __init__(self, parent=None):
        super().__init__(parent)
        set_widget_role(self, WidgetRole.EDITOR)
        self.file_path = None
        self.is_modified = False
        self.textChanged.connect(lambda: setattr(self, "is_modified", True))


class EditorTabs(ThemedWidget, QTabWidget):
    """Tabbed editor interface."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.tabCloseRequested.connect(self.close_tab)
        self.untitled_count = 0

    def new_file(self) -> CodeEditor:
        """Create new file."""
        self.untitled_count += 1
        editor = CodeEditor()
        index = self.addTab(editor, f"Untitled-{self.untitled_count}")
        self.setCurrentIndex(index)
        return editor

    def open_file(self, path: str) -> CodeEditor:
        """Open file from path."""
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()

            editor = CodeEditor()
            editor.setPlainText(content)
            editor.file_path = path
            editor.is_modified = False

            filename = Path(path).name
            index = self.addTab(editor, filename)
            self.setCurrentIndex(index)
            return editor
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to open file:\n{e}")
            return None

    def save_current(self) -> bool:
        """Save current file."""
        editor = self.currentWidget()
        if not isinstance(editor, CodeEditor):
            return False

        if editor.file_path:
            try:
                with open(editor.file_path, "w", encoding="utf-8") as f:
                    f.write(editor.toPlainText())
                editor.is_modified = False
                return True
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save:\n{e}")
                return False
        else:
            return self.save_as_current()

    def save_as_current(self) -> bool:
        """Save current file as..."""
        editor = self.currentWidget()
        if not isinstance(editor, CodeEditor):
            return False

        path, _ = QFileDialog.getSaveFileName(self, "Save File As")
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(editor.toPlainText())
                editor.file_path = path
                editor.is_modified = False
                self.setTabText(self.currentIndex(), Path(path).name)
                return True
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save:\n{e}")
                return False
        return False

    def close_tab(self, index: int):
        """Close tab at index."""
        self.removeTab(index)


class ProductionApp(ThemedMainWindow):
    """Production-quality text editor application."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("VFWidgets Editor - Production Example")
        self.setMinimumSize(1000, 700)
        self.setup_ui()
        self.create_menus()
        self.update_status()

    def setup_ui(self):
        """Setup user interface."""
        central = ThemedQWidget()
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Splitter for sidebar and editor
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Sidebar
        sidebar = ThemedQWidget()
        sidebar.setMinimumWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)

        sidebar_layout.addWidget(QLabel("EXPLORER"))

        self.file_list = QListWidget()
        self.file_list.addItems(["📄 README.md", "📄 main.py", "📁 src/", "📄 .gitignore"])
        sidebar_layout.addWidget(self.file_list)

        splitter.addWidget(sidebar)

        # Editor tabs
        self.editor_tabs = EditorTabs()
        splitter.addWidget(self.editor_tabs)

        splitter.setSizes([200, 800])
        layout.addWidget(splitter)

        # Status bar
        self.status_bar = self.statusBar()
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)

        self.theme_label = QLabel()
        self.status_bar.addPermanentWidget(self.theme_label)
        self.update_theme_label()

        # Create initial file
        self.editor_tabs.new_file()

    def create_menus(self):
        """Create menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        new_action = QAction("&New", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("&Open...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self.save_as_file)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Settings menu
        settings_menu = menubar.addMenu("&Settings")

        prefs_action = QAction("&Preferences...", self)
        prefs_action.triggered.connect(self.show_settings)
        settings_menu.addAction(prefs_action)

    def new_file(self):
        """Create new file."""
        self.editor_tabs.new_file()
        self.update_status()

    def open_file(self):
        """Open file dialog."""
        path, _ = QFileDialog.getOpenFileName(self, "Open File")
        if path:
            self.editor_tabs.open_file(path)
            self.update_status()

    def save_file(self):
        """Save current file."""
        if self.editor_tabs.save_current():
            self.update_status()

    def save_as_file(self):
        """Save current file as..."""
        if self.editor_tabs.save_as_current():
            self.update_status()

    def show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self)
        if dialog.exec():
            self.update_theme_label()

    def update_status(self):
        """Update status bar."""
        count = self.editor_tabs.count()
        self.status_label.setText(f"{count} file(s) open")

    def update_theme_label(self):
        """Update theme label."""
        app = ThemedApplication.instance()
        if app:
            self.theme_label.setText(f"Theme: {app.current_theme_name}")


def main():
    """Main entry point."""
    app = ThemedApplication(sys.argv)
    app.set_theme("dark")

    window = ProductionApp()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
