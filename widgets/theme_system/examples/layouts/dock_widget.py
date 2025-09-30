#!/usr/bin/env python3
"""
dock_widget.py - Themed dock widgets with styled title bars

Shows how to create dock widgets that respond to theme changes.

Key Concepts:
- Dock widget theming
- Title bar styling
- Dockable areas
- Floating docks

Example usage:
    python dock_widget.py
"""

import sys
from PySide6.QtWidgets import (QMainWindow, QDockWidget, QVBoxLayout, QLabel,
                               QPushButton, QTextEdit, QListWidget, QWidget)
from PySide6.QtCore import Qt

from vfwidgets_theme import ThemedWidget, ThemedApplication


class ThemedDockWidget(ThemedWidget, QDockWidget):
    """A themed dock widget."""

    theme_config = {
        'bg': 'dock.background',
        'fg': 'dock.foreground',
        'title_bg': 'dock.title.background',
        'title_fg': 'dock.title.foreground',
        'border': 'dock.border'
    }

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.update_styling()

    def on_theme_changed(self):
        """Called automatically when theme changes."""
        self.update_styling()

    def update_styling(self):
        """Update dock styling."""
        bg_color = self.theme.get('bg', '#ffffff')
        fg_color = self.theme.get('fg', '#000000')
        title_bg = self.theme.get('title_bg', '#e0e0e0')
        title_fg = self.theme.get('title_fg', '#000000')
        border_color = self.theme.get('border', '#cccccc')

        self.setStyleSheet(f"""
        QDockWidget {{
            background-color: {bg_color};
            color: {fg_color};
            border: 1px solid {border_color};
        }}

        QDockWidget::title {{
            background-color: {title_bg};
            color: {title_fg};
            padding: 5px;
            border-bottom: 1px solid {border_color};
        }}
        """)


class DockDemo(ThemedWidget, QMainWindow):
    """Demo showing themed dock widgets."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Themed Dock Widget Demo")
        self.setMinimumSize(900, 600)
        self.setup_ui()

    def setup_ui(self):
        """Set up the demo UI."""
        # Central widget
        central = QWidget()
        layout = QVBoxLayout(central)

        title = QLabel("Main Content Area")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        content = QTextEdit()
        content.setPlaceholderText("Main editor area...")
        layout.addWidget(content)

        self.setCentralWidget(central)

        # Create dock widgets
        self.create_docks()

        # Menu bar for theme switching
        self.create_menu()

    def create_docks(self):
        """Create themed dock widgets."""
        # File explorer dock
        file_dock = ThemedDockWidget("File Explorer")
        file_list = QListWidget()
        for i in range(10):
            file_list.addItem(f"file_{i+1}.txt")
        file_dock.setWidget(file_list)
        self.addDockWidget(Qt.LeftDockWidgetArea, file_dock)

        # Properties dock
        props_dock = ThemedDockWidget("Properties")
        props_widget = QWidget()
        props_layout = QVBoxLayout(props_widget)
        props_layout.addWidget(QLabel("Property 1: Value"))
        props_layout.addWidget(QLabel("Property 2: Value"))
        props_layout.addStretch()
        props_dock.setWidget(props_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, props_dock)

        # Console dock
        console_dock = ThemedDockWidget("Console")
        console_text = QTextEdit()
        console_text.setPlaceholderText("Console output...")
        console_dock.setWidget(console_text)
        self.addDockWidget(Qt.BottomDockWidgetArea, console_dock)

    def create_menu(self):
        """Create menu bar."""
        menubar = self.menuBar()

        # Theme menu
        theme_menu = menubar.addMenu('Theme')

        light_action = theme_menu.addAction('Light')
        light_action.triggered.connect(lambda: self.switch_theme('light'))

        dark_action = theme_menu.addAction('Dark')
        dark_action.triggered.connect(lambda: self.switch_theme('dark'))

    def switch_theme(self, theme_name):
        """Switch theme."""
        app = ThemedApplication.instance()
        if app:
            app.set_theme(theme_name)


def main():
    """Run the demo."""
    app = ThemedApplication(sys.argv)

    light_theme = {
        'name': 'light',
        'dock': {
            'background': '#ffffff',
            'foreground': '#000000',
            'title': {'background': '#e0e0e0', 'foreground': '#000000'},
            'border': '#cccccc'
        }
    }

    dark_theme = {
        'name': 'dark',
        'dock': {
            'background': '#3a3a3a',
            'foreground': '#ffffff',
            'title': {'background': '#2a2a2a', 'foreground': '#ffffff'},
            'border': '#555555'
        }
    }

    app.register_theme('light', light_theme)
    app.register_theme('dark', dark_theme)
    app.set_theme('light')

    demo = DockDemo()
    demo.show()

    return app.exec()


if __name__ == '__main__':
    sys.exit(main())