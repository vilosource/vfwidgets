#!/usr/bin/env python3
"""
Example 05: VS Code-Inspired Editor (BRIDGE TO ADVANCED API)
=============================================================

⭐ THIS EXAMPLE INTRODUCES ThemedWidget FOR THE FIRST TIME ⭐

You've successfully used ThemedMainWindow, ThemedDialog, and ThemedQWidget
in examples 01-04. Now you need to build widgets that inherit from classes
OTHER than QWidget (like QTextEdit and QTabWidget).

THE PROBLEM:
- We need a QTextEdit subclass for the code editor
- We need a QTabWidget subclass for the tabbed interface
- ThemedQWidget only works with QWidget base class!

THE SOLUTION: ThemedWidget mixin
- ThemedWidget can combine with ANY Qt base class
- Pattern: class MyWidget(ThemedWidget, QtBaseClass)
- IMPORTANT: ThemedWidget must come FIRST

THE "AHA!" MOMENT:
ThemedQWidget was actually this all along:
    class ThemedQWidget(ThemedWidget, QWidget):
        pass

Now you understand the full pattern! When you need non-QWidget bases,
just use ThemedWidget directly.

---

This example showcases a production-quality application
inspired by Visual Studio Code.

Features:
- Dark theme by default (VS Code-inspired styling)
- Action bar (vertical icon sidebar)
- Collapsible sidebar
- Tabbed editor area with role="editor" for monospace font
- Settings dialog for theme selection
- Full file operations (New, Open, Save, Close)
- Menu bar with shortcuts
- Status bar
- **Zero inline styles** - all styling from theme system!

Theme System Features Used:
- ⭐ ThemedWidget mixin with QTextEdit and QTabWidget (NEW!)
- Role markers (role="editor" for text editors)
- Automatic widget styling (all buttons, inputs, lists themed)
- Dynamic theme switching
- Complete font hierarchy (editor vs UI fonts)

WHAT TO LEARN:
1. When to use ThemedWidget (this example: QTextEdit, QTabWidget)
2. How to use ThemedWidget (see TextEditor and EditorTabs classes below)
3. Why ThemedWidget must come first in inheritance
4. The relationship between ThemedQWidget and ThemedWidget
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
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
)


class SettingsDialog(ThemedDialog):
    """Settings dialog for theme selection."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumSize(450, 300)
        self.selected_theme = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(25, 25, 25, 25)

        # Title
        title = QLabel("Application Settings")
        # Note: Title gets proper styling from theme system automatically
        layout.addWidget(title)

        # Theme selection
        theme_label = QLabel("Theme:")
        layout.addWidget(theme_label)

        self.theme_combo = QComboBox()
        self.theme_combo.setMinimumHeight(34)

        # Get available themes
        app = ThemedApplication.instance()
        if app:
            themes = app.available_themes
            self.theme_combo.addItems(themes)

            # Set current theme
            current = app.current_theme_name
            if hasattr(current, 'name'):
                current = current.name
            elif not isinstance(current, str):
                current = str(current)

            index = self.theme_combo.findText(current)
            if index >= 0:
                self.theme_combo.setCurrentIndex(index)

        layout.addWidget(self.theme_combo)

        # Theme descriptions
        desc = QLabel(
            "Available themes:\n"
            "• default - Standard light theme\n"
            "• dark - Dark theme (recommended)\n"
            "• light - High contrast light theme\n"
            "• minimal - Fallback theme"
        )
        # Description text styled by theme automatically
        layout.addWidget(desc)

        # Spacer
        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        btn_apply = QPushButton("Apply")
        btn_apply.setMinimumSize(90, 32)
        btn_apply.clicked.connect(self.apply_theme)
        button_layout.addWidget(btn_apply)

        btn_ok = QPushButton("OK")
        btn_ok.setMinimumSize(90, 32)
        btn_ok.clicked.connect(self.accept)
        button_layout.addWidget(btn_ok)

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setMinimumSize(90, 32)
        btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(btn_cancel)

        layout.addLayout(button_layout)

    def apply_theme(self):
        """Apply the selected theme without closing dialog."""
        theme_name = self.theme_combo.currentText()
        app = ThemedApplication.instance()
        if app and theme_name:
            app.set_theme(theme_name)
            self.selected_theme = theme_name


class ActionBar(ThemedQWidget):
    """Vertical action bar with icon buttons (left sidebar)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(50)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignTop)

        # Action buttons (styled by theme automatically)
        btn_explorer = QPushButton("📁")
        btn_explorer.setFixedSize(48, 48)
        btn_explorer.setToolTip("Explorer")
        layout.addWidget(btn_explorer)

        btn_search = QPushButton("🔍")
        btn_search.setFixedSize(48, 48)
        btn_search.setToolTip("Search")
        layout.addWidget(btn_search)

        btn_settings = QPushButton("⚙️")
        btn_settings.setFixedSize(48, 48)
        btn_settings.setToolTip("Settings")
        layout.addWidget(btn_settings)

        # Connect settings button to parent's show_settings
        btn_settings.clicked.connect(self.on_settings_clicked)

        layout.addStretch()

    def on_settings_clicked(self):
        """Handle settings button click."""
        # Find parent window and call show_settings
        parent = self.parent()
        while parent and not isinstance(parent, VSCodeMainWindow):
            parent = parent.parent()
        if parent:
            parent.show_settings()


class SideBar(ThemedQWidget):
    """Collapsible sidebar for file explorer."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(200)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)

        # Title (styled by theme automatically)
        title = QLabel("EXPLORER")
        layout.addWidget(title)

        # File list (simulated)
        self.file_list = QListWidget()
        self.file_list.addItems([
            "📄 README.md",
            "📄 main.py",
            "📁 src/",
            "📄 requirements.txt",
            "📁 docs/",
            "📄 .gitignore"
        ])
        layout.addWidget(self.file_list)


class TextEditor(ThemedWidget, QTextEdit):
    """Themed text editor widget with role marker.

    ⭐ FIRST USAGE OF ThemedWidget MIXIN! ⭐

    WHY: We need a QTextEdit subclass for code editing functionality.
         ThemedQWidget won't work because it inherits from QWidget, not QTextEdit.

    PATTERN: class TextEditor(ThemedWidget, QTextEdit)
             ^^^^^^^^^^^^^^^^^^ ThemedWidget MUST come first!

    WRONG:   class TextEditor(QTextEdit, ThemedWidget)  # ❌ Won't work!
    RIGHT:   class TextEditor(ThemedWidget, QTextEdit)  # ✅ Correct!

    This gives us:
    - Full QTextEdit functionality (text editing, selection, etc.)
    - Automatic theme integration (colors, fonts, etc.)
    - Role marker support (see setup_ui for role="editor")
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_path = None
        self.is_modified = False
        self.setup_ui()
        self.textChanged.connect(self.on_text_changed)

    def setup_ui(self):
        # Use role marker to get editor styling automatically
        # This gives us:
        # - Monospace font (11pt Courier New)
        # - Editor-specific colors
        # - Proper selection colors
        self.setProperty("role", "editor")

    def on_text_changed(self):
        """Mark document as modified."""
        if not self.is_modified:
            self.is_modified = True


class EditorTabs(ThemedWidget, QTabWidget):
    """Themed tab widget for multiple editors.

    ⭐ SECOND USAGE OF ThemedWidget MIXIN! ⭐

    WHY: We need a QTabWidget subclass for tabbed interface functionality.
         Again, ThemedQWidget won't work - we need QTabWidget features.

    PATTERN: class EditorTabs(ThemedWidget, QTabWidget)
             Same pattern - ThemedWidget first, then Qt base class.

    Once you understand this pattern, you can create themed versions of:
    - QFrame, QPushButton, QLineEdit, QComboBox, etc.
    - ANY Qt widget class!

    That's the power of the mixin approach.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.tabCloseRequested.connect(self.close_tab)
        self.untitled_count = 0

    def new_file(self):
        """Create a new untitled file."""
        self.untitled_count += 1
        editor = TextEditor()
        editor.setPlaceholderText("Start typing...")
        tab_title = f"Untitled-{self.untitled_count}"
        index = self.addTab(editor, tab_title)
        self.setCurrentIndex(index)
        return editor

    def open_file(self, file_path):
        """Open a file in a new tab."""
        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()

            editor = TextEditor()
            editor.setPlainText(content)
            editor.file_path = file_path
            editor.is_modified = False

            file_name = os.path.basename(file_path)
            index = self.addTab(editor, file_name)
            self.setCurrentIndex(index)
            return editor
        except Exception as e:
            print(f"Error opening file: {e}")
            return None

    def save_current_file(self):
        """Save the current file."""
        editor = self.currentWidget()
        if not isinstance(editor, TextEditor):
            return False

        if editor.file_path:
            # File has a path, save it
            try:
                with open(editor.file_path, 'w', encoding='utf-8') as f:
                    f.write(editor.toPlainText())
                editor.is_modified = False
                return True
            except Exception as e:
                print(f"Error saving file: {e}")
                return False
        else:
            # No path, use Save As
            return self.save_as_current_file()

    def save_as_current_file(self):
        """Save the current file with a new name."""
        editor = self.currentWidget()
        if not isinstance(editor, TextEditor):
            return False

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File As",
            "",
            "All Files (*.*)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(editor.toPlainText())

                editor.file_path = file_path
                editor.is_modified = False

                # Update tab title
                file_name = os.path.basename(file_path)
                self.setTabText(self.currentIndex(), file_name)
                return True
            except Exception as e:
                print(f"Error saving file: {e}")
                return False

        return False

    def close_tab(self, index):
        """Close a tab."""
        editor = self.widget(index)
        if isinstance(editor, TextEditor) and editor.is_modified:
            # TODO: Add confirmation dialog
            pass

        self.removeTab(index)

    def get_current_file_info(self):
        """Get info about the current file."""
        editor = self.currentWidget()
        if isinstance(editor, TextEditor):
            if editor.file_path:
                return os.path.basename(editor.file_path)
            else:
                return self.tabText(self.currentIndex())
        return "No file open"


class VSCodeMainWindow(ThemedMainWindow):
    """Main window resembling VS Code."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("VFWidgets Editor - VS Code-Inspired")
        self.setMinimumSize(900, 600)
        self.setup_ui()
        self.create_menus()
        self.update_status_bar()

    def setup_ui(self):
        # Create central widget with horizontal splitter
        central = ThemedQWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Action bar (vertical left)
        self.action_bar = ActionBar()
        main_layout.addWidget(self.action_bar)

        # Splitter for sidebar and editor
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(1)

        # Sidebar
        self.sidebar = SideBar()
        splitter.addWidget(self.sidebar)

        # Editor tabs
        self.editor_tabs = EditorTabs()
        splitter.addWidget(self.editor_tabs)

        # Set splitter sizes (sidebar 20%, editor 80%)
        splitter.setSizes([200, 700])

        main_layout.addWidget(splitter)

        # Status bar
        self.status_bar = self.statusBar()
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)

        self.theme_label = QLabel()
        self.status_bar.addPermanentWidget(self.theme_label)
        self.update_theme_label()

        # Create initial empty file
        self.editor_tabs.new_file()

    def create_menus(self):
        """Create menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        new_action = QAction("&New", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("&Open...", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.triggered.connect(self.save_as_file)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        close_action = QAction("&Close Tab", self)
        close_action.setShortcut(QKeySequence("Ctrl+W"))
        close_action.triggered.connect(self.close_current_tab)
        file_menu.addAction(close_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        menubar.addMenu("&Edit")

        # View menu
        menubar.addMenu("&View")

        # Settings menu
        settings_menu = menubar.addMenu("&Settings")

        settings_action = QAction("&Preferences...", self)
        settings_action.triggered.connect(self.show_settings)
        settings_menu.addAction(settings_action)

    def new_file(self):
        """Create a new file."""
        self.editor_tabs.new_file()
        self.update_status_bar()

    def open_file(self):
        """Open a file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "All Files (*.*)"
        )

        if file_path:
            self.editor_tabs.open_file(file_path)
            self.update_status_bar()

    def save_file(self):
        """Save the current file."""
        if self.editor_tabs.save_current_file():
            self.update_status_bar()

    def save_as_file(self):
        """Save the current file with a new name."""
        if self.editor_tabs.save_as_current_file():
            self.update_status_bar()

    def close_current_tab(self):
        """Close the current tab."""
        current_index = self.editor_tabs.currentIndex()
        if current_index >= 0:
            self.editor_tabs.close_tab(current_index)
        self.update_status_bar()

    def show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self)
        if dialog.exec():
            # Settings accepted
            self.update_theme_label()

    def update_status_bar(self):
        """Update status bar information."""
        file_info = self.editor_tabs.get_current_file_info()
        tab_count = self.editor_tabs.count()
        self.status_label.setText(f"{file_info} | {tab_count} file(s) open")

    def update_theme_label(self):
        """Update theme label in status bar."""
        app = ThemedApplication.instance()
        if app:
            current = app.current_theme_name
            if hasattr(current, 'name'):
                current = current.name
            elif not isinstance(current, str):
                current = str(current)

            self.theme_label.setText(f"Theme: {current}")


def main():
    app = ThemedApplication(sys.argv)

    # Set dark theme (VS Code-inspired UI)
    app.set_theme("dark")

    window = VSCodeMainWindow()
    window.show()

    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
