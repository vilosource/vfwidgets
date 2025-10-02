#!/usr/bin/env python3
"""Phase 5 Living Example - Comprehensive Example Showcase.
=======================================================

This is the main showcase for Phase 5 examples, demonstrating all
the capabilities of the VFWidgets theme system through a comprehensive
gallery of examples.

Features demonstrated:
- Basic themed widgets (buttons, labels, inputs, lists, dialogs)
- Layout examples (grids, tabs, splitters, dock widgets, stacked widgets)
- Tutorial series progression
- Complete application architecture
- Theme switching and management
- Best practices for themed applications

This serves as both a demo and a reference implementation.
"""

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from vfwidgets_theme import ThemedApplication, ThemedWidget

# Import examples from different categories
try:
    from basic.themed_button import ThemedButton
    from basic.themed_dialog import ThemedDialog
    from basic.themed_input import ThemedInput, ValidationLabel
    from basic.themed_label import ThemedLabel
    from basic.themed_list import ThemedListWidget
except ImportError:
    print("Warning: Could not import basic examples")

try:
    from layouts.dock_widget import ThemedDockWidget
    from layouts.grid_layout import ThemedGridCell
    from layouts.splitter import SplitterPane, ThemedSplitter
    from layouts.stacked_widget import ThemedStackedWidget
    from layouts.tab_widget import ThemedTabWidget
except ImportError:
    print("Warning: Could not import layout examples")


class ExampleShowcase(ThemedWidget):
    """Main showcase widget demonstrating all Phase 5 examples."""

    theme_config = {
        'bg': 'window.background',
        'fg': 'window.foreground',
        'accent': 'accent.primary',
        'card_bg': 'card.background',
        'card_border': 'card.border'
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_theme = 'light'
        self.setup_ui()

    def setup_ui(self):
        """Set up the showcase UI."""
        layout = QVBoxLayout(self)

        # Header
        self.create_header(layout)

        # Main content
        self.create_main_content(layout)

        # Footer with controls
        self.create_footer(layout)

    def create_header(self, layout):
        """Create the header section."""
        header_layout = QVBoxLayout()

        # Title
        title = QLabel("VFWidgets Theme System - Phase 5 Examples")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
        QLabel {
            font-size: 24px;
            font-weight: bold;
            margin: 20px;
            padding: 10px;
        }
        """)
        header_layout.addWidget(title)

        # Description
        description = QLabel(
            "This showcase demonstrates all the themed widgets and examples "
            "created in Phase 5 of the VFWidgets theme system. "
            "Use the tabs below to explore different categories of examples."
        )
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)
        description.setStyleSheet("font-size: 14px; margin: 10px; color: #666;")
        header_layout.addWidget(description)

        layout.addLayout(header_layout)

    def create_main_content(self, layout):
        """Create the main content area with tabs."""
        self.tab_widget = QTabWidget()

        # Basic widgets tab
        self.create_basic_widgets_tab()

        # Layout examples tab
        self.create_layout_examples_tab()

        # Interactive demo tab
        self.create_interactive_demo_tab()

        # Theme gallery tab
        self.create_theme_gallery_tab()

        # Tutorial showcase tab
        self.create_tutorial_showcase_tab()

        layout.addWidget(self.tab_widget)

    def create_basic_widgets_tab(self):
        """Create tab showcasing basic themed widgets."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Section title
        section_title = QLabel("Basic Themed Widgets")
        section_title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(section_title)

        # Buttons section
        buttons_group = QGroupBox("Themed Buttons")
        buttons_layout = QHBoxLayout(buttons_group)

        button1 = QPushButton("Primary Button")
        button2 = QPushButton("Secondary Button")
        button3 = QPushButton("Action Button")

        for btn in [button1, button2, button3]:
            buttons_layout.addWidget(btn)

        layout.addWidget(buttons_group)

        # Labels section
        labels_group = QGroupBox("Themed Labels")
        labels_layout = QVBoxLayout(labels_group)

        title_label = QLabel("This is a title label")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")

        body_label = QLabel("This is body text that adapts to the current theme.")

        caption_label = QLabel("This is caption text in a muted color.")
        caption_label.setStyleSheet("font-size: 12px; color: #888;")

        for label in [title_label, body_label, caption_label]:
            labels_layout.addWidget(label)

        layout.addWidget(labels_group)

        # Inputs section
        inputs_group = QGroupBox("Themed Input Fields")
        inputs_layout = QFormLayout(inputs_group)

        name_input = QLineEdit()
        name_input.setPlaceholderText("Enter your name...")

        email_input = QLineEdit()
        email_input.setPlaceholderText("Enter email address...")

        inputs_layout.addRow("Name:", name_input)
        inputs_layout.addRow("Email:", email_input)

        layout.addWidget(inputs_group)

        # List section
        list_group = QGroupBox("Themed List")
        list_layout = QVBoxLayout(list_group)

        sample_list = QListWidget()
        sample_items = ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"]
        for item in sample_items:
            sample_list.addItem(item)

        list_layout.addWidget(sample_list)
        layout.addWidget(list_group)

        layout.addStretch()
        self.tab_widget.addTab(widget, "Basic Widgets")

    def create_layout_examples_tab(self):
        """Create tab showcasing layout examples."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Section title
        section_title = QLabel("Layout Examples")
        section_title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(section_title)

        # Grid layout example
        grid_group = QGroupBox("Grid Layout")
        grid_layout = QGridLayout(grid_group)

        for row in range(3):
            for col in range(4):
                cell = QPushButton(f"Cell {row},{col}")
                cell.setMinimumSize(80, 40)
                grid_layout.addWidget(cell, row, col)

        layout.addWidget(grid_group)

        # Splitter example
        splitter_group = QGroupBox("Splitter Layout")
        splitter_layout = QVBoxLayout(splitter_group)

        splitter = QSplitter(Qt.Horizontal)

        left_panel = QTextEdit()
        left_panel.setPlaceholderText("Left panel content...")

        right_panel = QTextEdit()
        right_panel.setPlaceholderText("Right panel content...")

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 300])

        splitter_layout.addWidget(splitter)
        layout.addWidget(splitter_group)

        layout.addStretch()
        self.tab_widget.addTab(widget, "Layouts")

    def create_interactive_demo_tab(self):
        """Create interactive demo tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Section title
        section_title = QLabel("Interactive Demo")
        section_title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(section_title)

        # Demo controls
        controls_group = QGroupBox("Demo Controls")
        controls_layout = QFormLayout(controls_group)

        # Theme selector
        self.demo_theme_combo = QComboBox()
        self.demo_theme_combo.addItems(['light', 'dark', 'blue', 'green', 'purple'])
        self.demo_theme_combo.currentTextChanged.connect(self.switch_theme)
        controls_layout.addRow("Theme:", self.demo_theme_combo)

        # Feature toggles
        self.animations_check = QCheckBox("Enable Animations")
        self.animations_check.setChecked(True)
        controls_layout.addRow("", self.animations_check)

        self.tooltips_check = QCheckBox("Show Tooltips")
        self.tooltips_check.setChecked(True)
        controls_layout.addRow("", self.tooltips_check)

        layout.addWidget(controls_group)

        # Interactive elements
        interactive_group = QGroupBox("Interactive Elements")
        interactive_layout = QVBoxLayout(interactive_group)

        # Action buttons
        action_layout = QHBoxLayout()

        demo_dialog_btn = QPushButton("Show Demo Dialog")
        demo_dialog_btn.clicked.connect(self.show_demo_dialog)
        action_layout.addWidget(demo_dialog_btn)

        demo_notification_btn = QPushButton("Show Notification")
        demo_notification_btn.clicked.connect(self.show_notification)
        action_layout.addWidget(demo_notification_btn)

        refresh_demo_btn = QPushButton("Refresh Demo")
        refresh_demo_btn.clicked.connect(self.refresh_demo)
        action_layout.addWidget(refresh_demo_btn)

        interactive_layout.addLayout(action_layout)

        # Demo output area
        self.demo_output = QTextEdit()
        self.demo_output.setMaximumHeight(150)
        self.demo_output.setPlaceholderText("Demo output will appear here...")
        interactive_layout.addWidget(self.demo_output)

        layout.addWidget(interactive_group)

        layout.addStretch()
        self.tab_widget.addTab(widget, "Interactive")

    def create_theme_gallery_tab(self):
        """Create theme gallery tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Section title
        section_title = QLabel("Theme Gallery")
        section_title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(section_title)

        # Theme preview grid
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QGridLayout(scroll_widget)

        themes = [
            ('Light', 'light', '#ffffff', '#000000'),
            ('Dark', 'dark', '#2d2d2d', '#ffffff'),
            ('Blue', 'blue', '#e3f2fd', '#0d47a1'),
            ('Green', 'green', '#e8f5e8', '#1b5e20'),
            ('Purple', 'purple', '#f3e5f5', '#4a148c'),
        ]

        for i, (name, theme_id, bg, fg) in enumerate(themes):
            row = i // 3
            col = i % 3

            # Theme preview card
            theme_card = QWidget()
            theme_card.setFixedSize(200, 150)
            theme_card.setStyleSheet(f"""
            QWidget {{
                background-color: {bg};
                color: {fg};
                border: 2px solid #ccc;
                border-radius: 8px;
            }}
            """)

            card_layout = QVBoxLayout(theme_card)

            # Theme name
            theme_name = QLabel(name)
            theme_name.setAlignment(Qt.AlignCenter)
            theme_name.setStyleSheet("font-weight: bold; font-size: 14px; margin: 5px;")
            card_layout.addWidget(theme_name)

            # Sample elements
            sample_btn = QPushButton("Sample Button")
            sample_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {fg};
                color: {bg};
                border: none;
                border-radius: 4px;
                padding: 5px;
                margin: 2px;
            }}
            """)
            card_layout.addWidget(sample_btn)

            sample_text = QLabel("Sample text content")
            sample_text.setAlignment(Qt.AlignCenter)
            sample_text.setStyleSheet("margin: 5px;")
            card_layout.addWidget(sample_text)

            # Apply button
            apply_btn = QPushButton("Apply Theme")
            apply_btn.clicked.connect(lambda checked, t=theme_id: self.switch_theme(t))
            apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px;
                margin: 2px;
            }
            """)
            card_layout.addWidget(apply_btn)

            scroll_layout.addWidget(theme_card, row, col)

        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

        self.tab_widget.addTab(widget, "Theme Gallery")

    def create_tutorial_showcase_tab(self):
        """Create tutorial showcase tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Section title
        section_title = QLabel("Tutorial Showcase")
        section_title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(section_title)

        # Tutorial list
        tutorials_group = QGroupBox("Available Tutorials")
        tutorials_layout = QVBoxLayout(tutorials_group)

        tutorial_info = [
            ("01_hello_theme.py", "Introduction to themed widgets and applications"),
            ("02_custom_theme.py", "Creating and using custom themes"),
            ("03_theme_switching.py", "Advanced theme switching techniques"),
            ("04_vscode_import.py", "Importing and using VSCode themes"),
            ("05_custom_widget.py", "Building custom themed widgets from scratch"),
            ("06_complete_app.py", "Complete themed application example"),
        ]

        for filename, description in tutorial_info:
            tutorial_widget = QWidget()
            tutorial_layout = QHBoxLayout(tutorial_widget)

            # Tutorial info
            info_layout = QVBoxLayout()

            name_label = QLabel(filename)
            name_label.setStyleSheet("font-weight: bold;")
            info_layout.addWidget(name_label)

            desc_label = QLabel(description)
            desc_label.setStyleSheet("color: #666; font-size: 12px;")
            info_layout.addWidget(desc_label)

            tutorial_layout.addLayout(info_layout)

            # Run button
            run_btn = QPushButton("View Tutorial")
            run_btn.clicked.connect(lambda checked, f=filename: self.show_tutorial_info(f))
            tutorial_layout.addWidget(run_btn)

            tutorials_layout.addWidget(tutorial_widget)

        layout.addWidget(tutorials_group)

        # Tutorial output
        self.tutorial_output = QTextEdit()
        self.tutorial_output.setPlaceholderText("Select a tutorial to see details...")
        layout.addWidget(self.tutorial_output)

        self.tab_widget.addTab(widget, "Tutorials")

    def create_footer(self, layout):
        """Create footer with global controls."""
        footer_layout = QHBoxLayout()

        # Global theme selector
        footer_layout.addWidget(QLabel("Global Theme:"))

        self.global_theme_combo = QComboBox()
        self.global_theme_combo.addItems(['light', 'dark', 'blue', 'green', 'purple'])
        self.global_theme_combo.currentTextChanged.connect(self.switch_theme)
        footer_layout.addWidget(self.global_theme_combo)

        footer_layout.addStretch()

        # Info button
        info_btn = QPushButton("About Phase 5")
        info_btn.clicked.connect(self.show_about_dialog)
        footer_layout.addWidget(info_btn)

        # Reset button
        reset_btn = QPushButton("Reset Demo")
        reset_btn.clicked.connect(self.reset_demo)
        footer_layout.addWidget(reset_btn)

        layout.addLayout(footer_layout)

    def on_theme_changed(self):
        """Handle theme changes."""
        self.update_styling()

    def update_styling(self):
        """Update styling based on current theme."""
        bg = self.theme.get('bg', '#ffffff')
        fg = self.theme.get('fg', '#000000')
        accent = self.theme.get('accent', '#007bff')
        card_bg = self.theme.get('card_bg', '#f8f8f8')
        card_border = self.theme.get('card_border', '#dddddd')

        # Update main widget styling
        self.setStyleSheet(f"""
        ExampleShowcase {{
            background-color: {bg};
            color: {fg};
        }}

        QGroupBox {{
            font-weight: bold;
            border: 2px solid {card_border};
            border-radius: 8px;
            margin: 5px;
            padding-top: 15px;
            background-color: {card_bg};
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: {accent};
        }}

        QPushButton {{
            background-color: {accent};
            color: white;
            border: none;
            border-radius: 4px;
            padding: 6px 12px;
            font-size: 12px;
            min-width: 80px;
        }}

        QPushButton:hover {{
            background-color: {accent};
            opacity: 0.8;
        }}
        """)

    def switch_theme(self, theme_name):
        """Switch to specified theme."""
        app = ThemedApplication.instance()
        try:
            app.set_theme(theme_name)
            self.current_theme = theme_name

            # Update all combo boxes
            for combo in [self.global_theme_combo, self.demo_theme_combo]:
                if combo.currentText() != theme_name:
                    index = combo.findText(theme_name)
                    if index >= 0:
                        combo.setCurrentIndex(index)

            self.log_demo_output(f"Switched to {theme_name} theme")

        except Exception as e:
            self.log_demo_output(f"Error switching theme: {e}")

    def show_demo_dialog(self):
        """Show a demo dialog."""
        dialog = QWidget()
        dialog.setWindowTitle("Demo Dialog")
        dialog.setWindowFlags(Qt.Dialog)
        dialog.setFixedSize(300, 200)

        layout = QVBoxLayout(dialog)

        label = QLabel("This is a demo dialog that demonstrates theme consistency.")
        label.setWordWrap(True)
        layout.addWidget(label)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        dialog.show()
        self.log_demo_output("Demo dialog opened")

    def show_notification(self):
        """Show a notification."""
        self.log_demo_output("Notification: Demo feature activated!")

    def refresh_demo(self):
        """Refresh the demo."""
        self.demo_output.clear()
        self.log_demo_output("Demo refreshed")

    def show_tutorial_info(self, filename):
        """Show information about a tutorial."""
        tutorial_docs = {
            "01_hello_theme.py": """
Tutorial 01: Hello Theme
========================

This tutorial introduces the basics of the VFWidgets theme system:

Key Concepts:
• Creating a ThemedApplication
• Inheriting from ThemedWidget
• Defining theme_config mappings
• Responding to theme changes with on_theme_changed()
• Using self.theme.get() to access theme properties

Learning Outcomes:
After completing this tutorial, you'll understand how to create
your first themed widget and switch between light and dark themes.
            """,
            "02_custom_theme.py": """
Tutorial 02: Custom Theme
=========================

This tutorial shows how to create comprehensive custom themes:

Key Concepts:
• Structuring theme data with nested properties
• Creating multiple theme variants
• Using semantic property names
• Organizing colors by component type
• Building theme families

Learning Outcomes:
You'll learn to create professional-looking custom themes
with consistent color schemes and proper organization.
            """,
            # Add more tutorial documentation here...
        }

        info = tutorial_docs.get(filename, f"Documentation for {filename} not available.")
        self.tutorial_output.setPlainText(info)
        self.log_demo_output(f"Viewed tutorial: {filename}")

    def show_about_dialog(self):
        """Show about dialog."""
        about_text = """
VFWidgets Theme System - Phase 5 Examples
==========================================

This showcase demonstrates the comprehensive theming capabilities
built in Phase 5 of the VFWidgets theme system.

Features:
• Complete widget theming with automatic updates
• Custom theme creation and management
• VSCode theme import capabilities
• Layout-aware theming
• Performance-optimized theme switching
• Educational tutorial series

The VFWidgets theme system provides a clean, simple API for
creating beautiful, consistent, and accessible user interfaces.
        """

        dialog = QWidget()
        dialog.setWindowTitle("About Phase 5")
        dialog.setWindowFlags(Qt.Dialog)
        dialog.setFixedSize(500, 400)

        layout = QVBoxLayout(dialog)

        text_edit = QTextEdit()
        text_edit.setPlainText(about_text)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        dialog.show()

    def reset_demo(self):
        """Reset the demo to initial state."""
        self.switch_theme('light')
        self.demo_output.clear()
        self.tutorial_output.clear()
        self.log_demo_output("Demo reset to initial state")

    def log_demo_output(self, message):
        """Log message to demo output."""
        if hasattr(self, 'demo_output'):
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.demo_output.append(f"[{timestamp}] {message}")


def create_showcase_themes():
    """Create themes for the showcase application."""
    themes = {
        'light': {
            'name': 'light',
            'window': {'background': '#ffffff', 'foreground': '#333333'},
            'card': {'background': '#f8f8f8', 'border': '#dddddd'},
            'accent': {'primary': '#007bff'}
        },
        'dark': {
            'name': 'dark',
            'window': {'background': '#2d2d2d', 'foreground': '#ffffff'},
            'card': {'background': '#3a3a3a', 'border': '#555555'},
            'accent': {'primary': '#66aaff'}
        },
        'blue': {
            'name': 'blue',
            'window': {'background': '#e3f2fd', 'foreground': '#0d47a1'},
            'card': {'background': '#ffffff', 'border': '#90caf9'},
            'accent': {'primary': '#1976d2'}
        },
        'green': {
            'name': 'green',
            'window': {'background': '#e8f5e8', 'foreground': '#1b5e20'},
            'card': {'background': '#ffffff', 'border': '#a5d6a7'},
            'accent': {'primary': '#388e3c'}
        },
        'purple': {
            'name': 'purple',
            'window': {'background': '#f3e5f5', 'foreground': '#4a148c'},
            'card': {'background': '#ffffff', 'border': '#ce93d8'},
            'accent': {'primary': '#7b1fa2'}
        }
    }
    return themes


def main():
    """Main function for Phase 5 living example."""
    print("VFWidgets Theme System - Phase 5 Living Example")
    print("=" * 50)
    print("Starting comprehensive example showcase...")

    # Create themed application
    app = ThemedApplication(sys.argv)

    # Register showcase themes
    themes = create_showcase_themes()
    for name, theme in themes.items():
        app.register_theme(name, theme)
        print(f"Registered theme: {name}")

    # Set initial theme
    app.set_theme('light')
    print("Set initial theme to 'light'")

    # Create main showcase window
    showcase = ExampleShowcase()
    showcase.setWindowTitle("VFWidgets Theme System - Phase 5 Examples")
    showcase.setMinimumSize(900, 700)
    showcase.show()

    print("\nPhase 5 Examples Showcase is ready!")
    print("\nFeatures available:")
    print("• Basic Widgets: Buttons, labels, inputs, lists, dialogs")
    print("• Layout Examples: Grids, tabs, splitters, dock widgets, stacked widgets")
    print("• Interactive Demo: Live theme switching and feature testing")
    print("• Theme Gallery: Visual preview of all available themes")
    print("• Tutorial Showcase: Access to the complete tutorial series")
    print("\nUse the tabs to explore different categories of examples.")
    print("Try switching themes to see the system in action!")

    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
