#!/usr/bin/env python3
"""
stacked_widget.py - Themed stacked widget with transitions

Shows how to create stacked widgets that respond to theme changes.

Key Concepts:
- Stacked widget theming
- Page transitions
- Navigation controls
- Dynamic page management

Example usage:
    python stacked_widget.py
"""

import sys
from PySide6.QtWidgets import (QStackedWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QWidget, QListWidget,
                               QTextEdit, QFormLayout, QLineEdit)
from PySide6.QtCore import Qt

from vfwidgets_theme import ThemedWidget, ThemedApplication


class ThemedStackedWidget(ThemedWidget, QStackedWidget):
    """A themed stacked widget."""

    theme_config = {
        'bg': 'stack.background',
        'fg': 'stack.foreground',
        'border': 'stack.border'
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.update_styling()

    def on_theme_changed(self):
        """Called automatically when theme changes."""
        self.update_styling()

    def update_styling(self):
        """Update stack styling."""
        bg_color = self.theme.get('bg', '#ffffff')
        fg_color = self.theme.get('fg', '#000000')
        border_color = self.theme.get('border', '#cccccc')

        self.setStyleSheet(f"""
        QStackedWidget {{
            background-color: {bg_color};
            color: {fg_color};
            border: 1px solid {border_color};
            border-radius: 4px;
        }}
        """)


class StackPage(ThemedWidget):
    """Base class for stack pages."""

    theme_config = {
        'bg': 'page.background',
        'fg': 'page.foreground'
    }

    def __init__(self, title="Page", parent=None):
        super().__init__(parent)
        self._title = title

    def on_theme_changed(self):
        """Called automatically when theme changes."""
        self.update_styling()

    def update_styling(self):
        """Update page styling."""
        bg_color = self.theme.get('bg', '#ffffff')
        fg_color = self.theme.get('fg', '#000000')

        self.setStyleSheet(f"""
        QWidget {{
            background-color: {bg_color};
            color: {fg_color};
        }}
        """)

    def get_title(self):
        """Get page title."""
        return self._title


class WelcomePage(StackPage):
    """Welcome page."""

    def __init__(self, parent=None):
        super().__init__("Welcome", parent)
        self.setup_ui()

    def setup_ui(self):
        """Set up the welcome page."""
        layout = QVBoxLayout(self)

        title = QLabel("Welcome to the Demo")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)

        description = QLabel(
            "This demonstrates a themed stacked widget.\n\n"
            "Use the navigation buttons to switch between pages.\n"
            "Each page maintains consistent theming."
        )
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)
        layout.addWidget(description)

        layout.addStretch()


class SettingsPage(StackPage):
    """Settings page."""

    def __init__(self, parent=None):
        super().__init__("Settings", parent)
        self.setup_ui()

    def setup_ui(self):
        """Set up the settings page."""
        layout = QVBoxLayout(self)

        title = QLabel("Application Settings")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        form = QFormLayout()

        self.name_edit = QLineEdit("User Name")
        form.addRow("Name:", self.name_edit)

        self.email_edit = QLineEdit("user@example.com")
        form.addRow("Email:", self.email_edit)

        layout.addLayout(form)

        save_btn = QPushButton("Save Settings")
        layout.addWidget(save_btn)

        layout.addStretch()


class DataPage(StackPage):
    """Data page with list."""

    def __init__(self, parent=None):
        super().__init__("Data", parent)
        self.setup_ui()

    def setup_ui(self):
        """Set up the data page."""
        layout = QVBoxLayout(self)

        title = QLabel("Data Management")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Data list
        self.data_list = QListWidget()
        for i in range(15):
            self.data_list.addItem(f"Data Item {i+1}")
        layout.addWidget(self.data_list)

        # Controls
        controls = QHBoxLayout()

        add_btn = QPushButton("Add Item")
        add_btn.clicked.connect(self.add_item)
        controls.addWidget(add_btn)

        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_selected)
        controls.addWidget(remove_btn)

        layout.addLayout(controls)

    def add_item(self):
        """Add new item."""
        count = self.data_list.count()
        self.data_list.addItem(f"New Item {count + 1}")

    def remove_selected(self):
        """Remove selected item."""
        current_row = self.data_list.currentRow()
        if current_row >= 0:
            self.data_list.takeItem(current_row)


class AboutPage(StackPage):
    """About page."""

    def __init__(self, parent=None):
        super().__init__("About", parent)
        self.setup_ui()

    def setup_ui(self):
        """Set up the about page."""
        layout = QVBoxLayout(self)

        title = QLabel("About This Demo")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        content = QTextEdit()
        content.setHtml("""
        <h3>Themed Stacked Widget Demo</h3>
        <p>This demonstration shows how to create a stacked widget that
        responds to theme changes.</p>

        <h4>Features:</h4>
        <ul>
        <li>Multiple pages with navigation</li>
        <li>Consistent theming across all pages</li>
        <li>Automatic theme updates</li>
        <li>Custom page content</li>
        </ul>

        <p>Each page is a separate widget that can contain any content
        while maintaining theme consistency.</p>
        """)
        content.setReadOnly(True)
        layout.addWidget(content)


class StackedDemo(ThemedWidget):
    """Demo showing themed stacked widgets."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Themed Stacked Widget Demo")
        self.setMinimumSize(700, 500)
        self.setup_ui()

    def setup_ui(self):
        """Set up the demo UI."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Themed Stacked Widget Example")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Navigation
        nav_layout = QHBoxLayout()

        self.nav_buttons = []
        self.pages = []

        # Create pages
        pages_data = [
            ("Welcome", WelcomePage()),
            ("Settings", SettingsPage()),
            ("Data", DataPage()),
            ("About", AboutPage())
        ]

        # Stacked widget
        self.stacked_widget = ThemedStackedWidget()

        for title, page in pages_data:
            # Add page to stack
            self.stacked_widget.addWidget(page)
            self.pages.append(page)

            # Create navigation button
            btn = QPushButton(title)
            btn.clicked.connect(lambda checked, idx=len(self.nav_buttons): self.show_page(idx))
            self.nav_buttons.append(btn)
            nav_layout.addWidget(btn)

        layout.addLayout(nav_layout)

        # Current page indicator
        self.page_label = QLabel()
        self.page_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.page_label)

        # Add stacked widget
        layout.addWidget(self.stacked_widget)

        # Theme controls
        self.create_theme_controls(layout)

        # Show first page
        self.show_page(0)

    def show_page(self, index):
        """Show page at index."""
        if 0 <= index < len(self.pages):
            self.stacked_widget.setCurrentIndex(index)

            # Update navigation buttons
            for i, btn in enumerate(self.nav_buttons):
                btn.setEnabled(i != index)

            # Update page label
            page = self.pages[index]
            self.page_label.setText(f"Current: {page.get_title()}")

    def create_theme_controls(self, layout):
        """Create theme controls."""
        controls_layout = QHBoxLayout()

        # Navigation controls
        prev_btn = QPushButton("Previous")
        prev_btn.clicked.connect(self.previous_page)
        controls_layout.addWidget(prev_btn)

        next_btn = QPushButton("Next")
        next_btn.clicked.connect(self.next_page)
        controls_layout.addWidget(next_btn)

        controls_layout.addStretch()

        # Theme buttons
        light_btn = QPushButton("Light Theme")
        light_btn.clicked.connect(lambda: self.switch_theme('light'))
        controls_layout.addWidget(light_btn)

        dark_btn = QPushButton("Dark Theme")
        dark_btn.clicked.connect(lambda: self.switch_theme('dark'))
        controls_layout.addWidget(dark_btn)

        layout.addLayout(controls_layout)

    def previous_page(self):
        """Show previous page."""
        current = self.stacked_widget.currentIndex()
        if current > 0:
            self.show_page(current - 1)

    def next_page(self):
        """Show next page."""
        current = self.stacked_widget.currentIndex()
        if current < len(self.pages) - 1:
            self.show_page(current + 1)

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
        'stack': {
            'background': '#ffffff',
            'foreground': '#000000',
            'border': '#cccccc'
        },
        'page': {
            'background': '#ffffff',
            'foreground': '#000000'
        }
    }

    dark_theme = {
        'name': 'dark',
        'stack': {
            'background': '#3a3a3a',
            'foreground': '#ffffff',
            'border': '#555555'
        },
        'page': {
            'background': '#3a3a3a',
            'foreground': '#ffffff'
        }
    }

    app.register_theme('light', light_theme)
    app.register_theme('dark', dark_theme)
    app.set_theme('light')

    demo = StackedDemo()
    demo.show()

    return app.exec()


if __name__ == '__main__':
    sys.exit(main())