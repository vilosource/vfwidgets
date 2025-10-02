#!/usr/bin/env python3
"""
tab_widget.py - Themed tab widget with styled tabs

Shows how to create tab widgets that respond to theme changes with
consistent tab styling, content areas, and dynamic tab management.

Key Concepts:
- Tab widget theming
- Tab bar styling
- Content area theming
- Dynamic tab management
- Closable tabs

Example usage:
    python tab_widget.py
"""

import random
import sys

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
)

from vfwidgets_theme import ThemedApplication, ThemedWidget


class ThemedTabWidget(ThemedWidget, QTabWidget):
    """A themed tab widget with styled tabs and content areas."""

    theme_config = {
        'bg': 'tabs.background',
        'fg': 'tabs.foreground',
        'tab_bg': 'tabs.tab.background',
        'tab_fg': 'tabs.tab.foreground',
        'tab_border': 'tabs.tab.border',
        'active_tab_bg': 'tabs.active.background',
        'active_tab_fg': 'tabs.active.foreground',
        'hover_tab_bg': 'tabs.hover.background',
        'content_bg': 'tabs.content.background',
        'content_fg': 'tabs.content.foreground',
        'font': 'tabs.font'
    }

    # Custom signals
    tab_context_menu = Signal(int)  # Tab index for context menu

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)

        # Connect signals
        self.tabCloseRequested.connect(self.close_tab)

        # Apply initial styling
        self.update_styling()

    def on_theme_changed(self):
        """Called automatically when theme changes."""
        self.update_styling()

    def update_styling(self):
        """Update tab widget styling based on current theme."""
        # Get theme colors
        bg_color = self.theme.get('bg', '#f0f0f0')
        fg_color = self.theme.get('fg', '#000000')
        tab_bg = self.theme.get('tab_bg', '#e0e0e0')
        tab_fg = self.theme.get('tab_fg', '#333333')
        tab_border = self.theme.get('tab_border', '#cccccc')
        active_tab_bg = self.theme.get('active_tab_bg', '#ffffff')
        active_tab_fg = self.theme.get('active_tab_fg', '#000000')
        hover_tab_bg = self.theme.get('hover_tab_bg', '#f5f5f5')
        content_bg = self.theme.get('content_bg', '#ffffff')
        content_fg = self.theme.get('content_fg', '#000000')
        font = self.theme.get('font', 'Arial, sans-serif')

        # Generate comprehensive stylesheet
        stylesheet = f"""
        QTabWidget {{
            background-color: {bg_color};
            color: {fg_color};
            font-family: {font};
        }}

        QTabWidget::pane {{
            background-color: {content_bg};
            color: {content_fg};
            border: 2px solid {tab_border};
            border-radius: 4px;
            top: -2px;
        }}

        QTabWidget::tab-bar {{
            alignment: left;
        }}

        QTabBar::tab {{
            background-color: {tab_bg};
            color: {tab_fg};
            border: 2px solid {tab_border};
            border-bottom: none;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            min-width: 100px;
            padding: 8px 12px;
            margin: 0px 2px;
            font-family: {font};
            font-size: 12px;
        }}

        QTabBar::tab:selected {{
            background-color: {active_tab_bg};
            color: {active_tab_fg};
            border-bottom: 2px solid {active_tab_bg};
        }}

        QTabBar::tab:hover:!selected {{
            background-color: {hover_tab_bg};
        }}

        QTabBar::tab:disabled {{
            color: #999999;
            background-color: #f0f0f0;
        }}

        QTabBar::close-button {{
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiI+CiAgPGxpbmUgeDE9IjQiIHkxPSI0IiB4Mj0iMTIiIHkyPSIxMiIgc3Ryb2tlPSIjNjY2IiBzdHJva2Utd2lkdGg9IjIiLz4KICA8bGluZSB4MT0iMTIiIHkxPSI0IiB4Mj0iNCIgeTI9IjEyIiBzdHJva2U9IiM2NjYiIHN0cm9rZS13aWR0aD0iMiIvPgo8L3N2Zz4=);
            subcontrol-position: right;
        }}

        QTabBar::close-button:hover {{
            background-color: #ff6666;
            border-radius: 2px;
        }}
        """

        self.setStyleSheet(stylesheet)

        # Update all tab content widgets
        for i in range(self.count()):
            widget = self.widget(i)
            if hasattr(widget, 'update_styling'):
                widget.update_styling()

    def add_themed_tab(self, widget, title, closable=True):
        """Add a tab with themed styling."""
        index = self.addTab(widget, title)
        if not closable:
            # Remove close button for non-closable tabs
            self.tabBar().setTabButton(index, self.tabBar().RightSide, None)
        return index

    def close_tab(self, index):
        """Close a tab with confirmation if needed."""
        if self.count() <= 1:
            return  # Don't close the last tab

        # Check if tab has unsaved changes (if applicable)
        widget = self.widget(index)
        if hasattr(widget, 'has_unsaved_changes') and widget.has_unsaved_changes():
            # In a real application, you might show a confirmation dialog
            print(f"Tab '{self.tabText(index)}' has unsaved changes")

        self.removeTab(index)

    def contextMenuEvent(self, event):
        """Handle context menu on tabs."""
        # Find which tab was right-clicked
        pos = event.pos()
        for i in range(self.count()):
            tab_rect = self.tabBar().tabRect(i)
            if tab_rect.contains(pos):
                self.tab_context_menu.emit(i)
                break


class TabContent(ThemedWidget):
    """Base class for tab content with theming."""

    theme_config = {
        'bg': 'tabs.content.background',
        'fg': 'tabs.content.foreground',
        'font': 'tabs.content.font'
    }

    def __init__(self, content_type="basic", parent=None):
        super().__init__(parent)
        self._content_type = content_type
        self._has_unsaved_changes = False

    def on_theme_changed(self):
        """Called automatically when theme changes."""
        self.update_styling()

    def update_styling(self):
        """Update content styling."""
        bg_color = self.theme.get('bg', '#ffffff')
        fg_color = self.theme.get('fg', '#000000')
        font = self.theme.get('font', 'Arial, sans-serif')

        self.setStyleSheet(f"""
        QWidget {{
            background-color: {bg_color};
            color: {fg_color};
            font-family: {font};
        }}
        """)

    def has_unsaved_changes(self):
        """Check if tab has unsaved changes."""
        return self._has_unsaved_changes

    def set_unsaved_changes(self, has_changes):
        """Set unsaved changes state."""
        self._has_unsaved_changes = has_changes


class TextEditorTab(TabContent):
    """A text editor tab content."""

    def __init__(self, parent=None):
        super().__init__("editor", parent)
        self.setup_ui()

    def setup_ui(self):
        """Set up the text editor UI."""
        layout = QVBoxLayout(self)

        # Toolbar
        toolbar = QHBoxLayout()

        self.filename_edit = QLineEdit("untitled.txt")
        toolbar.addWidget(QLabel("File:"))
        toolbar.addWidget(self.filename_edit)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_content)
        toolbar.addWidget(save_btn)

        toolbar.addStretch()

        layout.addLayout(toolbar)

        # Text editor
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Start typing your text here...")
        self.text_edit.textChanged.connect(self.on_text_changed)
        layout.addWidget(self.text_edit)

        # Status
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

    def on_text_changed(self):
        """Handle text changes."""
        self.set_unsaved_changes(True)
        self.status_label.setText("Modified")

    def save_content(self):
        """Save the content."""
        # In a real application, this would save to file
        self.set_unsaved_changes(False)
        self.status_label.setText("Saved")
        print(f"Saved content to {self.filename_edit.text()}")


class ListViewerTab(TabContent):
    """A list viewer tab content."""

    def __init__(self, parent=None):
        super().__init__("list", parent)
        self.setup_ui()
        self.populate_list()

    def setup_ui(self):
        """Set up the list viewer UI."""
        layout = QVBoxLayout(self)

        # Controls
        controls = QHBoxLayout()

        add_btn = QPushButton("Add Item")
        add_btn.clicked.connect(self.add_item)
        controls.addWidget(add_btn)

        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_selected)
        controls.addWidget(remove_btn)

        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self.clear_list)
        controls.addWidget(clear_btn)

        controls.addStretch()

        layout.addLayout(controls)

        # List widget
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        # Status
        self.status_label = QLabel()
        layout.addWidget(self.status_label)

    def populate_list(self):
        """Populate with sample items."""
        sample_items = [
            "Document 1.pdf", "Image_001.jpg", "Spreadsheet.xlsx",
            "Presentation.pptx", "Archive.zip", "Music.mp3",
            "Video.mp4", "Text_file.txt", "Database.db"
        ]

        for item in sample_items:
            self.list_widget.addItem(item)

        self.update_status()

    def add_item(self):
        """Add a new item."""
        item_names = ["New File", "Document", "Image", "Audio", "Video"]
        extensions = [".txt", ".pdf", ".jpg", ".mp3", ".mp4"]

        name = random.choice(item_names)
        ext = random.choice(extensions)
        item_text = f"{name}_{random.randint(1, 999)}{ext}"

        self.list_widget.addItem(item_text)
        self.update_status()

    def remove_selected(self):
        """Remove selected items."""
        for item in self.list_widget.selectedItems():
            self.list_widget.takeItem(self.list_widget.row(item))
        self.update_status()

    def clear_list(self):
        """Clear all items."""
        self.list_widget.clear()
        self.update_status()

    def update_status(self):
        """Update status label."""
        count = self.list_widget.count()
        selected = len(self.list_widget.selectedItems())
        self.status_label.setText(f"Items: {count}, Selected: {selected}")


class SettingsTab(TabContent):
    """A settings tab content."""

    def __init__(self, parent=None):
        super().__init__("settings", parent)
        self.setup_ui()

    def setup_ui(self):
        """Set up the settings UI."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Application Settings")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Settings form
        from PySide6.QtWidgets import QCheckBox, QComboBox, QFormLayout, QSpinBox

        form = QFormLayout()

        # Theme setting
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "Colorful", "Auto"])
        form.addRow("Theme:", self.theme_combo)

        # Font size
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(12)
        form.addRow("Font Size:", self.font_size_spin)

        # Auto-save
        self.auto_save_check = QCheckBox("Enable auto-save")
        self.auto_save_check.setChecked(True)
        form.addRow("", self.auto_save_check)

        # Max tabs
        self.max_tabs_spin = QSpinBox()
        self.max_tabs_spin.setRange(1, 20)
        self.max_tabs_spin.setValue(10)
        form.addRow("Max Tabs:", self.max_tabs_spin)

        layout.addLayout(form)

        # Apply button
        apply_btn = QPushButton("Apply Settings")
        apply_btn.clicked.connect(self.apply_settings)
        layout.addWidget(apply_btn)

        layout.addStretch()

    def apply_settings(self):
        """Apply the settings."""
        theme = self.theme_combo.currentText().lower()
        font_size = self.font_size_spin.value()
        auto_save = self.auto_save_check.isChecked()
        max_tabs = self.max_tabs_spin.value()

        print(f"Applied settings: Theme={theme}, Font={font_size}, "
              f"AutoSave={auto_save}, MaxTabs={max_tabs}")

        # Apply theme if changed
        if theme in ['light', 'dark', 'colorful']:
            app = ThemedApplication.instance()
            if app:
                app.set_theme(theme)


class TabWidgetDemo(ThemedWidget):
    """Demo window showing themed tab widgets."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Themed Tab Widget Demo")
        self.setMinimumSize(900, 600)

        self.setup_ui()

    def setup_ui(self):
        """Set up the demo UI."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Themed Tab Widget Examples")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Tab management controls
        self.create_tab_controls(layout)

        # Main tab widget
        self.tab_widget = ThemedTabWidget()
        self.tab_widget.tab_context_menu.connect(self.show_tab_context_menu)
        layout.addWidget(self.tab_widget)

        # Create initial tabs
        self.create_initial_tabs()

        # Theme controls
        self.create_theme_controls(layout)

    def create_tab_controls(self, layout):
        """Create tab management controls."""
        controls = QHBoxLayout()

        new_editor_btn = QPushButton("New Editor Tab")
        new_editor_btn.clicked.connect(self.add_editor_tab)
        controls.addWidget(new_editor_btn)

        new_list_btn = QPushButton("New List Tab")
        new_list_btn.clicked.connect(self.add_list_tab)
        controls.addWidget(new_list_btn)

        close_current_btn = QPushButton("Close Current")
        close_current_btn.clicked.connect(self.close_current_tab)
        controls.addWidget(close_current_btn)

        controls.addStretch()

        layout.addLayout(controls)

    def create_initial_tabs(self):
        """Create initial tabs."""
        # Text editor tab
        editor_tab = TextEditorTab()
        self.tab_widget.add_themed_tab(editor_tab, "Editor", True)

        # List viewer tab
        list_tab = ListViewerTab()
        self.tab_widget.add_themed_tab(list_tab, "Files", True)

        # Settings tab (not closable)
        settings_tab = SettingsTab()
        self.tab_widget.add_themed_tab(settings_tab, "Settings", False)

    def add_editor_tab(self):
        """Add a new editor tab."""
        editor_tab = TextEditorTab()
        tab_count = sum(1 for i in range(self.tab_widget.count())
                       if isinstance(self.tab_widget.widget(i), TextEditorTab))
        title = f"Editor {tab_count + 1}"
        index = self.tab_widget.add_themed_tab(editor_tab, title, True)
        self.tab_widget.setCurrentIndex(index)

    def add_list_tab(self):
        """Add a new list tab."""
        list_tab = ListViewerTab()
        tab_count = sum(1 for i in range(self.tab_widget.count())
                       if isinstance(self.tab_widget.widget(i), ListViewerTab))
        title = f"List {tab_count + 1}"
        index = self.tab_widget.add_themed_tab(list_tab, title, True)
        self.tab_widget.setCurrentIndex(index)

    def close_current_tab(self):
        """Close the current tab."""
        current_index = self.tab_widget.currentIndex()
        if current_index >= 0:
            self.tab_widget.close_tab(current_index)

    def show_tab_context_menu(self, tab_index):
        """Show context menu for tab."""
        print(f"Context menu for tab {tab_index}: {self.tab_widget.tabText(tab_index)}")

    def create_theme_controls(self, layout):
        """Create theme switching controls."""
        controls_layout = QHBoxLayout()

        # Theme buttons
        light_btn = QPushButton("Light Theme")
        light_btn.clicked.connect(lambda: self.switch_theme('light'))
        controls_layout.addWidget(light_btn)

        dark_btn = QPushButton("Dark Theme")
        dark_btn.clicked.connect(lambda: self.switch_theme('dark'))
        controls_layout.addWidget(dark_btn)

        colorful_btn = QPushButton("Colorful Theme")
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
    """Run the themed tab widget demo."""
    # Create themed application
    app = ThemedApplication(sys.argv)

    # Define themes with tab styling
    light_theme = {
        'name': 'light',
        'tabs': {
            'background': '#f5f5f5',
            'foreground': '#333333',
            'tab': {
                'background': '#e0e0e0',
                'foreground': '#333333',
                'border': '#cccccc'
            },
            'active': {
                'background': '#ffffff',
                'foreground': '#000000'
            },
            'hover': {
                'background': '#f0f0f0'
            },
            'content': {
                'background': '#ffffff',
                'foreground': '#000000',
                'font': 'Arial, sans-serif'
            },
            'font': 'Arial, sans-serif'
        }
    }

    dark_theme = {
        'name': 'dark',
        'tabs': {
            'background': '#2d2d2d',
            'foreground': '#ffffff',
            'tab': {
                'background': '#3a3a3a',
                'foreground': '#ffffff',
                'border': '#555555'
            },
            'active': {
                'background': '#4a4a4a',
                'foreground': '#ffffff'
            },
            'hover': {
                'background': '#404040'
            },
            'content': {
                'background': '#3a3a3a',
                'foreground': '#ffffff',
                'font': 'Arial, sans-serif'
            },
            'font': 'Arial, sans-serif'
        }
    }

    colorful_theme = {
        'name': 'colorful',
        'tabs': {
            'background': '#fff5f0',
            'foreground': '#2d1810',
            'tab': {
                'background': '#ffcc99',
                'foreground': '#2d1810',
                'border': '#ff9966'
            },
            'active': {
                'background': '#ffffff',
                'foreground': '#2d1810'
            },
            'hover': {
                'background': '#ffe6d9'
            },
            'content': {
                'background': '#ffffff',
                'foreground': '#2d1810',
                'font': 'Arial, sans-serif'
            },
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
    demo = TabWidgetDemo()
    demo.show()

    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
