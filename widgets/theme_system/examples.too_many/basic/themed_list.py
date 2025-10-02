#!/usr/bin/env python3
"""themed_list.py - Themed list widget with alternating rows.

Shows how to create list widgets that respond to theme changes with
alternating row colors, selection styling, and hover effects.

Key Concepts:
- List widget theming
- Alternating row colors
- Selection and hover states
- Item styling
- Search and filtering

Example usage:
    python themed_list.py
"""

import sys

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
)

from vfwidgets_theme import ThemedApplication, ThemedWidget


class ThemedListWidget(ThemedWidget, QListWidget):
    """A themed list widget with alternating rows and selection styling."""

    theme_config = {
        'bg': 'list.background',
        'fg': 'list.foreground',
        'border': 'list.border',
        'alternate_bg': 'list.alternate.background',
        'selection_bg': 'list.selection.background',
        'selection_fg': 'list.selection.foreground',
        'hover_bg': 'list.hover.background',
        'hover_fg': 'list.hover.foreground',
        'font': 'list.font'
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlternatingRowColors(True)

        # Apply initial styling
        self.update_styling()

    def on_theme_changed(self):
        """Called automatically when theme changes."""
        self.update_styling()

    def update_styling(self):
        """Update list styling based on current theme."""
        # Get theme colors
        bg_color = self.theme.get('bg', '#ffffff')
        fg_color = self.theme.get('fg', '#000000')
        border_color = self.theme.get('border', '#cccccc')
        alternate_bg = self.theme.get('alternate_bg', '#f8f8f8')
        selection_bg = self.theme.get('selection_bg', '#0066cc')
        selection_fg = self.theme.get('selection_fg', '#ffffff')
        hover_bg = self.theme.get('hover_bg', '#e6f2ff')
        hover_fg = self.theme.get('hover_fg', '#000000')
        font = self.theme.get('font', 'Arial, sans-serif')

        # Generate stylesheet
        stylesheet = f"""
        QListWidget {{
            background-color: {bg_color};
            color: {fg_color};
            border: 1px solid {border_color};
            border-radius: 4px;
            font-family: {font};
            font-size: 13px;
            padding: 4px;
            outline: none;
        }}

        QListWidget::item {{
            padding: 8px;
            border-bottom: 1px solid {border_color};
        }}

        QListWidget::item:alternate {{
            background-color: {alternate_bg};
        }}

        QListWidget::item:selected {{
            background-color: {selection_bg};
            color: {selection_fg};
        }}

        QListWidget::item:hover {{
            background-color: {hover_bg};
            color: {hover_fg};
        }}

        QListWidget::item:selected:hover {{
            background-color: {selection_bg};
            color: {selection_fg};
        }}
        """

        self.setStyleSheet(stylesheet)

    def add_themed_item(self, text, item_type='normal'):
        """Add an item with specific styling based on type."""
        item = QListWidgetItem(text)

        # Set item data for type-specific styling
        item.setData(Qt.UserRole, item_type)

        # Add custom styling based on type
        if item_type == 'header':
            font = item.font()
            font.setBold(True)
            item.setFont(font)
        elif item_type == 'disabled':
            item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
        elif item_type == 'important':
            font = item.font()
            font.setItalic(True)
            item.setFont(font)

        self.addItem(item)
        return item


class FilterableList(ThemedWidget):
    """A list widget with filtering capabilities."""

    def __init__(self, items=None, parent=None):
        super().__init__(parent)
        self._all_items = items or []
        self.setup_ui()
        self.populate_list()

    def setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)

        # Filter input
        filter_layout = QHBoxLayout()

        filter_label = QLabel("Filter:")
        filter_layout.addWidget(filter_label)

        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Type to filter items...")
        self.filter_input.textChanged.connect(self.filter_items)
        filter_layout.addWidget(self.filter_input)

        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_filter)
        filter_layout.addWidget(clear_btn)

        layout.addLayout(filter_layout)

        # List widget
        self.list_widget = ThemedListWidget()
        layout.addWidget(self.list_widget)

        # Stats label
        self.stats_label = QLabel()
        layout.addWidget(self.stats_label)

    def populate_list(self):
        """Populate the list with items."""
        self.list_widget.clear()

        displayed_items = self.get_filtered_items()
        for item_data in displayed_items:
            if isinstance(item_data, dict):
                text = item_data.get('text', '')
                item_type = item_data.get('type', 'normal')
                self.list_widget.add_themed_item(text, item_type)
            else:
                self.list_widget.add_themed_item(str(item_data))

        self.update_stats()

    def get_filtered_items(self):
        """Get items that match the current filter."""
        filter_text = self.filter_input.text().lower()

        if not filter_text:
            return self._all_items

        filtered = []
        for item in self._all_items:
            if isinstance(item, dict):
                text = item.get('text', '').lower()
            else:
                text = str(item).lower()

            if filter_text in text:
                filtered.append(item)

        return filtered

    def filter_items(self):
        """Filter items based on input text."""
        # Use a timer to avoid filtering on every keystroke
        if hasattr(self, '_filter_timer'):
            self._filter_timer.stop()

        self._filter_timer = QTimer()
        self._filter_timer.timeout.connect(self.populate_list)
        self._filter_timer.setSingleShot(True)
        self._filter_timer.start(300)  # 300ms delay

    def clear_filter(self):
        """Clear the filter input."""
        self.filter_input.clear()

    def update_stats(self):
        """Update the statistics label."""
        total = len(self._all_items)
        displayed = self.list_widget.count()

        if total == displayed:
            self.stats_label.setText(f"Showing all {total} items")
        else:
            self.stats_label.setText(f"Showing {displayed} of {total} items")

    def add_items(self, items):
        """Add items to the list."""
        self._all_items.extend(items)
        self.populate_list()

    def set_items(self, items):
        """Set the list items."""
        self._all_items = items
        self.populate_list()


class ListDemo(ThemedWidget):
    """Demo window showing themed list widgets."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Themed List Widget Demo")
        self.setMinimumSize(800, 600)

        # Create main layout
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Themed List Widget Examples")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Create horizontal layout for lists
        lists_layout = QHBoxLayout()

        # Simple list
        self.create_simple_list(lists_layout)

        # Filterable list
        self.create_filterable_list(lists_layout)

        layout.addLayout(lists_layout)

        # Theme controls
        layout.addStretch()
        self.create_theme_controls(layout)

    def create_simple_list(self, layout):
        """Create a simple themed list example."""
        list_layout = QVBoxLayout()

        # Title
        title = QLabel("Simple Themed List")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-weight: bold; margin: 5px;")
        list_layout.addWidget(title)

        # Create list
        simple_list = ThemedListWidget()

        # Add various item types
        simple_list.add_themed_item("Header Item", "header")
        simple_list.add_themed_item("Normal Item 1", "normal")
        simple_list.add_themed_item("Normal Item 2", "normal")
        simple_list.add_themed_item("Important Item", "important")
        simple_list.add_themed_item("Normal Item 3", "normal")
        simple_list.add_themed_item("Disabled Item", "disabled")
        simple_list.add_themed_item("Normal Item 4", "normal")
        simple_list.add_themed_item("Another Header", "header")
        simple_list.add_themed_item("Normal Item 5", "normal")
        simple_list.add_themed_item("Normal Item 6", "normal")

        list_layout.addWidget(simple_list)

        # Add controls
        controls_layout = QHBoxLayout()

        add_btn = QPushButton("Add Item")
        add_btn.clicked.connect(lambda: self.add_simple_item(simple_list))
        controls_layout.addWidget(add_btn)

        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(lambda: self.remove_selected_item(simple_list))
        controls_layout.addWidget(remove_btn)

        list_layout.addLayout(controls_layout)
        layout.addLayout(list_layout)

    def create_filterable_list(self, layout):
        """Create a filterable list example."""
        list_layout = QVBoxLayout()

        # Title
        title = QLabel("Filterable List")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-weight: bold; margin: 5px;")
        list_layout.addWidget(title)

        # Create sample data
        sample_items = [
            {"text": "Programming Languages", "type": "header"},
            {"text": "Python - Easy to learn", "type": "normal"},
            {"text": "JavaScript - Web development", "type": "normal"},
            {"text": "C++ - System programming", "type": "normal"},
            {"text": "Java - Enterprise applications", "type": "normal"},
            {"text": "Rust - Memory safety", "type": "important"},
            {"text": "Go - Concurrent programming", "type": "normal"},
            {"text": "Frameworks", "type": "header"},
            {"text": "React - Frontend library", "type": "normal"},
            {"text": "Django - Python web framework", "type": "normal"},
            {"text": "Angular - Full-featured framework", "type": "normal"},
            {"text": "Vue.js - Progressive framework", "type": "normal"},
            {"text": "Flask - Micro web framework", "type": "normal"},
            {"text": "Databases", "type": "header"},
            {"text": "PostgreSQL - Relational database", "type": "normal"},
            {"text": "MongoDB - Document database", "type": "normal"},
            {"text": "Redis - In-memory store", "type": "important"},
            {"text": "SQLite - Embedded database", "type": "normal"},
        ]

        # Create filterable list
        self.filterable_list = FilterableList(sample_items)
        list_layout.addWidget(self.filterable_list)

        layout.addLayout(list_layout)

    def add_simple_item(self, list_widget):
        """Add a new item to simple list."""
        import random
        item_types = ['normal', 'important']
        item_type = random.choice(item_types)
        item_text = f"New Item {list_widget.count() + 1}"

        list_widget.add_themed_item(item_text, item_type)

    def remove_selected_item(self, list_widget):
        """Remove selected item from list."""
        current_row = list_widget.currentRow()
        if current_row >= 0:
            list_widget.takeItem(current_row)

    def create_theme_controls(self, layout):
        """Create theme switching controls."""
        from .themed_button import ThemedButton

        controls_layout = QHBoxLayout()

        # Theme buttons
        light_btn = ThemedButton("Light Theme")
        light_btn.clicked.connect(lambda: self.switch_theme('light'))
        controls_layout.addWidget(light_btn)

        dark_btn = ThemedButton("Dark Theme")
        dark_btn.clicked.connect(lambda: self.switch_theme('dark'))
        controls_layout.addWidget(dark_btn)

        colorful_btn = ThemedButton("Colorful Theme")
        colorful_btn.clicked.connect(lambda: self.switch_theme('colorful'))
        controls_layout.addWidget(colorful_btn)

        layout.addLayout(controls_layout)

    def switch_theme(self, theme_name):
        """Switch to a different theme."""
        app = ThemedApplication.instance()
        if app:
            try:
                app.set_theme(theme_name)
                print(f"Switched to {theme_name} theme")
            except Exception as e:
                print(f"Could not switch to {theme_name} theme: {e}")


def main():
    """Run the themed list demo."""
    # Create themed application
    app = ThemedApplication(sys.argv)

    # Define themes with list styling
    light_theme = {
        'name': 'light',
        'list': {
            'background': '#ffffff',
            'foreground': '#333333',
            'border': '#cccccc',
            'alternate': {'background': '#f8f8f8'},
            'selection': {'background': '#0066cc', 'foreground': '#ffffff'},
            'hover': {'background': '#e6f2ff', 'foreground': '#000000'},
            'font': 'Arial, sans-serif'
        },
        'button': {
            'background': '#f0f0f0',
            'foreground': '#333333',
            'border': '#cccccc',
            'hover': {'background': '#e0e0e0'},
            'pressed': {'background': '#d0d0d0'},
            'font': 'Arial, sans-serif'
        }
    }

    dark_theme = {
        'name': 'dark',
        'list': {
            'background': '#2d2d2d',
            'foreground': '#ffffff',
            'border': '#555555',
            'alternate': {'background': '#3a3a3a'},
            'selection': {'background': '#66aaff', 'foreground': '#000000'},
            'hover': {'background': '#404040', 'foreground': '#ffffff'},
            'font': 'Arial, sans-serif'
        },
        'button': {
            'background': '#555555',
            'foreground': '#ffffff',
            'border': '#777777',
            'hover': {'background': '#666666'},
            'pressed': {'background': '#444444'},
            'font': 'Arial, sans-serif'
        }
    }

    colorful_theme = {
        'name': 'colorful',
        'list': {
            'background': '#fff5f5',
            'foreground': '#2d1b30',
            'border': '#d68e8e',
            'alternate': {'background': '#ffe6e6'},
            'selection': {'background': '#ff6b9d', 'foreground': '#ffffff'},
            'hover': {'background': '#ffcccb', 'foreground': '#2d1b30'},
            'font': 'Arial, sans-serif'
        },
        'button': {
            'background': '#ffb3ba',
            'foreground': '#2d1b30',
            'border': '#ff8a95',
            'hover': {'background': '#ff9aa3'},
            'pressed': {'background': '#ff7a85'},
            'font': 'Arial, sans-serif'
        }
    }

    # Register themes
    app.register_theme('light', light_theme)
    app.register_theme('dark', dark_theme)
    app.register_theme('colorful', colorful_theme)

    # Set initial theme
    app.set_theme('light')

    # Create and show demo
    demo = ListDemo()
    demo.show()

    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
