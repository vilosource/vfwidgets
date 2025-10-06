#!/usr/bin/env python3
"""Example 07: Themed Tabbed Text Editor - Complete Application Showcase.
========================================================================

A professional tabbed text editor that demonstrates the VFWidgets theme system
with real-world application features.

Features Showcased:
- File operations (New, Open, Save, Close)
- Tabbed interface with multiple documents
- Theme switching via Properties dialog
- Toolbar with themed buttons, icons, and dropdowns
- Menu bar with actions
- Status bar with theme indicator
- All widgets automatically update on theme change

Themed Widgets Demonstrated:
- ThemedMainWindow (main application window)
- ThemedDialog (properties dialog)
- ThemedWidget + QTabWidget (tabbed interface)
- ThemedWidget + QTextEdit (text editors)
- QComboBox (themed dropdown)
- QPushButton (themed buttons)
- QMenuBar, QToolBar (themed bars)
- QStatusBar (themed status)

This showcases the new simplified API and smart property defaults.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
)

from vfwidgets_theme import ThemedApplication, ThemedDialog, ThemedMainWindow, ThemedWidget


class ThemedTextEdit(ThemedWidget, QTextEdit):
    """Text editor that automatically themes itself."""

    theme_config = {
        "editor_bg": "colors.background",
        "editor_fg": "colors.foreground",
        "selection_bg": "colors.primary",
        "border": "colors.border",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptRichText(False)  # Plain text only
        self.apply_theme_styling()

    def apply_theme_styling(self):
        """Apply theme colors to the text editor."""
        bg = self.theme.editor_bg
        fg = self.theme.editor_fg
        selection = self.theme.selection_bg
        border = self.theme.border

        self.setStyleSheet(
            f"""
            QTextEdit {{
                background-color: {bg};
                color: {fg};
                border: 1px solid {border};
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 12pt;
                padding: 8px;
            }}
            QTextEdit:focus {{
                border: 2px solid {selection};
            }}
        """
        )

    def on_theme_changed(self):
        """Called automatically when theme changes."""
        self.apply_theme_styling()


class ThemedTabWidget(ThemedWidget, QTabWidget):
    """Tab widget that themes itself and its tabs."""

    theme_config = {
        "tab_bg": "colors.background",
        "tab_fg": "colors.foreground",
        "tab_selected_bg": "colors.primary",
        "tab_selected_fg": "colors.background",
        "tab_hover": "colors.accent",
        "border": "colors.border",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.apply_theme_styling()

    def apply_theme_styling(self):
        """Apply theme colors to tabs."""
        bg = self.theme.tab_bg
        fg = self.theme.tab_fg
        selected_bg = self.theme.tab_selected_bg
        selected_fg = self.theme.tab_selected_fg
        hover = self.theme.tab_hover
        border = self.theme.border

        self.setStyleSheet(
            f"""
            QTabWidget::pane {{
                border: 1px solid {border};
                background: {bg};
                top: -1px;
            }}

            QTabBar::tab {{
                background: {bg};
                color: {fg};
                padding: 8px 16px;
                border: 1px solid {border};
                border-bottom: none;
                margin-right: 2px;
            }}

            QTabBar::tab:selected {{
                background: {selected_bg};
                color: {selected_fg};
                font-weight: bold;
            }}

            QTabBar::tab:hover:!selected {{
                background: {hover};
            }}

            QTabBar::close-button {{
                image: url(none);
                subcontrol-position: right;
            }}
        """
        )

    def on_theme_changed(self):
        """Called automatically when theme changes."""
        self.apply_theme_styling()


class ThemePropertiesDialog(ThemedDialog):
    """Dialog for selecting and previewing themes."""

    theme_config = {
        "dialog_bg": "colors.background",
        "dialog_fg": "colors.foreground",
        "preview_border": "colors.border",
        "button_bg": "colors.primary",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Theme Properties")
        self.setMinimumSize(450, 400)
        self.setup_ui()
        self.apply_theme_styling()

    def setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # Title
        title = QLabel("Theme Selection")
        title.setStyleSheet("font-size: 18pt; font-weight: bold;")
        layout.addWidget(title)

        # Theme selection
        theme_group = QGroupBox("Available Themes")
        theme_layout = QVBoxLayout(theme_group)

        select_label = QLabel("Choose a theme:")
        theme_layout.addWidget(select_label)

        self.theme_combo = QComboBox()
        app = ThemedApplication.instance()
        if app:
            # Get available themes
            themes = app.available_themes
            theme_names = []
            for t in themes:
                if isinstance(t, str):
                    theme_names.append(t)
                elif hasattr(t, "name"):
                    theme_names.append(t.name)

            self.theme_combo.addItems(theme_names)

            # Set current theme
            if app.current_theme_name:
                # Get theme name as string
                current_name = app.current_theme_name
                if hasattr(current_name, "name"):
                    current_name = current_name.name
                elif not isinstance(current_name, str):
                    current_name = str(current_name)

                index = self.theme_combo.findText(current_name)
                if index >= 0:
                    self.theme_combo.setCurrentIndex(index)

        self.theme_combo.currentTextChanged.connect(self.on_theme_selected)
        theme_layout.addWidget(self.theme_combo)

        layout.addWidget(theme_group)

        # Preview area
        preview_group = QGroupBox("Theme Preview")
        preview_layout = QVBoxLayout(preview_group)

        self.preview_label = QLabel("Select a theme to preview its colors")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(100)
        preview_layout.addWidget(self.preview_label)

        layout.addWidget(preview_group)

        # Current theme info
        self.info_label = QLabel()
        self.update_info_label()
        layout.addWidget(self.info_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_theme)
        button_layout.addWidget(self.apply_button)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept_and_apply)
        self.ok_button.setDefault(True)
        button_layout.addWidget(self.ok_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

    def apply_theme_styling(self):
        """Apply theme colors to dialog."""
        bg = self.theme.dialog_bg
        fg = self.theme.dialog_fg
        border = self.theme.preview_border
        button_bg = self.theme.button_bg

        # Update preview area styling
        if hasattr(self, "preview_label"):
            self.preview_label.setStyleSheet(
                f"""
                QLabel {{
                    background-color: {bg};
                    color: {fg};
                    border: 2px solid {border};
                    border-radius: 4px;
                    padding: 16px;
                }}
            """
            )

        # Style buttons
        for button in [self.apply_button, self.ok_button, self.cancel_button]:
            if button:
                button.setStyleSheet(
                    f"""
                    QPushButton {{
                        background-color: {button_bg};
                        color: {bg};
                        border: none;
                        border-radius: 4px;
                        padding: 8px 16px;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background-color: {fg};
                        color: {bg};
                    }}
                    QPushButton:pressed {{
                        background-color: {border};
                    }}
                """
                )

    def on_theme_changed(self):
        """Called automatically when theme changes."""
        self.apply_theme_styling()
        self.update_info_label()

    def on_theme_selected(self, theme_name):
        """Update preview when theme is selected."""
        self.preview_label.setText(f"Theme: {theme_name}\n\nClick 'Apply' to see the full effect")

    def apply_theme(self):
        """Apply the selected theme."""
        theme_name = self.theme_combo.currentText()
        app = ThemedApplication.instance()
        if app:
            app.set_theme(theme_name)
            self.update_info_label()

    def accept_and_apply(self):
        """Apply theme and close dialog."""
        self.apply_theme()
        self.accept()

    def update_info_label(self):
        """Update the current theme info label."""
        app = ThemedApplication.instance()
        if app and hasattr(self, "info_label"):
            theme_name = app.current_theme_name or "unknown"
            self.info_label.setText(f"Current active theme: {theme_name}")


class ThemedTextEditor(ThemedMainWindow):
    """Professional themed tabbed text editor."""

    theme_config = {
        "window_bg": "colors.background",
        "window_fg": "colors.foreground",
        "toolbar_bg": "colors.background",
        "statusbar_bg": "colors.background",
        "accent": "colors.primary",
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Themed Text Editor")
        self.setMinimumSize(900, 600)

        # Track open files: {editor_widget: file_path}
        self.open_files = {}

        self.setup_ui()
        self.apply_theme_styling()

        # Open with one empty tab
        self.new_file()

    def setup_ui(self):
        """Set up the main window UI."""
        # Create menu bar
        self.create_menus()

        # Create toolbar
        self.create_toolbar()

        # Create central widget with tabs
        self.tab_widget = ThemedTabWidget(self)
        self.tab_widget.tabCloseRequested.connect(self.close_tab_at_index)
        self.setCentralWidget(self.tab_widget)

        # Create status bar
        self.status_label = QLabel("Ready")
        self.theme_label = QLabel()
        self.update_theme_label()

        self.statusBar().addWidget(self.status_label, 1)
        self.statusBar().addPermanentWidget(self.theme_label)

    def create_menus(self):
        """Create menu bar with actions."""
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

        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        close_action = QAction("&Close Tab", self)
        close_action.setShortcut(QKeySequence.Close)
        close_action.triggered.connect(self.close_tab)
        file_menu.addAction(close_action)

        file_menu.addSeparator()

        properties_action = QAction("&Properties...", self)
        properties_action.triggered.connect(self.show_properties)
        file_menu.addAction(properties_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def create_toolbar(self):
        """Create toolbar with themed widgets."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # New button
        new_action = QAction("New", self)
        new_action.triggered.connect(self.new_file)
        toolbar.addAction(new_action)

        # Open button
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)

        # Save button
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)

        toolbar.addSeparator()

        # Font size dropdown
        font_label = QLabel(" Font Size: ")
        toolbar.addWidget(font_label)

        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems(["8", "10", "12", "14", "16", "18", "20", "24"])
        self.font_size_combo.setCurrentText("12")
        self.font_size_combo.currentTextChanged.connect(self.change_font_size)
        self.font_size_combo.setMinimumWidth(70)
        toolbar.addWidget(self.font_size_combo)

        toolbar.addSeparator()

        # Theme button
        self.theme_button = QPushButton("Theme Settings")
        self.theme_button.clicked.connect(self.show_properties)
        toolbar.addWidget(self.theme_button)

    def apply_theme_styling(self):
        """Apply theme colors to main window."""
        bg = self.theme.window_bg
        fg = self.theme.window_fg
        toolbar_bg = self.theme.toolbar_bg
        accent = self.theme.accent

        # Style the main window
        self.setStyleSheet(
            f"""
            QMainWindow {{
                background-color: {bg};
                color: {fg};
            }}

            QMenuBar {{
                background-color: {bg};
                color: {fg};
                border-bottom: 1px solid {accent};
            }}

            QMenuBar::item:selected {{
                background-color: {accent};
                color: {bg};
            }}

            QMenu {{
                background-color: {bg};
                color: {fg};
                border: 1px solid {accent};
            }}

            QMenu::item:selected {{
                background-color: {accent};
                color: {bg};
            }}

            QToolBar {{
                background-color: {toolbar_bg};
                border-bottom: 1px solid {accent};
                padding: 4px;
                spacing: 4px;
            }}

            QToolBar QLabel {{
                color: {fg};
            }}

            QComboBox {{
                background-color: {bg};
                color: {fg};
                border: 1px solid {accent};
                border-radius: 3px;
                padding: 4px 8px;
            }}

            QComboBox:hover {{
                border: 2px solid {accent};
            }}

            QComboBox::drop-down {{
                border: none;
            }}

            QPushButton {{
                background-color: {accent};
                color: {bg};
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }}

            QPushButton:hover {{
                background-color: {fg};
                color: {bg};
            }}

            QPushButton:pressed {{
                background-color: {bg};
                color: {fg};
                border: 1px solid {accent};
            }}

            QStatusBar {{
                background-color: {toolbar_bg};
                color: {fg};
                border-top: 1px solid {accent};
            }}
        """
        )

    def on_theme_changed(self):
        """Called automatically when theme changes."""
        self.apply_theme_styling()
        self.update_theme_label()

    def new_file(self):
        """Create a new empty file in a new tab."""
        editor = ThemedTextEdit()
        index = self.tab_widget.addTab(editor, "Untitled")
        self.tab_widget.setCurrentIndex(index)
        self.open_files[editor] = None
        self.update_status("New file created")

    def open_file(self):
        """Open a file dialog and load the selected file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "Text Files (*.txt);;Python Files (*.py);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                editor = ThemedTextEdit()
                editor.setPlainText(content)

                file_name = Path(file_path).name
                index = self.tab_widget.addTab(editor, file_name)
                self.tab_widget.setCurrentIndex(index)

                self.open_files[editor] = file_path
                self.update_status(f"Opened: {file_name}")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file:\n{str(e)}")

    def save_file(self):
        """Save the current file."""
        current_editor = self.tab_widget.currentWidget()
        if not current_editor:
            return

        file_path = self.open_files.get(current_editor)

        if not file_path:
            # No path yet, do Save As
            self.save_file_as()
        else:
            self._save_to_path(current_editor, file_path)

    def save_file_as(self):
        """Save the current file with a new name."""
        current_editor = self.tab_widget.currentWidget()
        if not current_editor:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save File As", "", "Text Files (*.txt);;Python Files (*.py);;All Files (*)"
        )

        if file_path:
            self._save_to_path(current_editor, file_path)

    def _save_to_path(self, editor, file_path):
        """Internal method to save editor content to a file path."""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(editor.toPlainText())

            self.open_files[editor] = file_path
            file_name = Path(file_path).name

            # Update tab title
            index = self.tab_widget.indexOf(editor)
            if index >= 0:
                self.tab_widget.setTabText(index, file_name)

            self.update_status(f"Saved: {file_name}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")

    def close_tab(self):
        """Close the current tab."""
        index = self.tab_widget.currentIndex()
        if index >= 0:
            self.close_tab_at_index(index)

    def close_tab_at_index(self, index):
        """Close tab at the specified index."""
        editor = self.tab_widget.widget(index)
        if not editor:
            return

        # TODO: Check for unsaved changes
        # For now, just close it

        self.tab_widget.removeTab(index)
        if editor in self.open_files:
            del self.open_files[editor]

        self.update_status("Tab closed")

    def show_properties(self):
        """Show the theme properties dialog."""
        dialog = ThemePropertiesDialog(self)
        dialog.exec()
        self.update_theme_label()

    def change_font_size(self, size_str):
        """Change font size of current editor."""
        current_editor = self.tab_widget.currentWidget()
        if current_editor and isinstance(current_editor, ThemedTextEdit):
            try:
                size = int(size_str)
                font = current_editor.font()
                font.setPointSize(size)
                current_editor.setFont(font)
                self.update_status(f"Font size changed to {size}pt")
            except ValueError:
                pass

    def update_status(self, message):
        """Update the status bar message."""
        self.status_label.setText(message)

    def update_theme_label(self):
        """Update the theme label in status bar."""
        app = ThemedApplication.instance()
        if app:
            theme_name = app.current_theme_name or "default"
            self.theme_label.setText(f"Theme: {theme_name}")


def main():
    """Main application entry point."""
    app = ThemedApplication(sys.argv)

    # Set initial theme
    app.set_theme("default")

    # Create and show the editor
    editor = ThemedTextEditor()
    editor.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
