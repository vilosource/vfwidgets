#!/usr/bin/env python3
"""
Tutorial 02: Custom Theme
=========================

This tutorial shows how to create your own custom theme.

What you'll learn:
- Creating custom theme definitions
- Using more theme properties
- Organizing theme data
- Best practices for theme structure

Building on Tutorial 01, let's create a custom theme...
"""

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from vfwidgets_theme import ThemedApplication, ThemedWidget


class CustomThemedWidget(ThemedWidget):
    """
    A widget that demonstrates using multiple theme properties.

    This extends our previous example by using more theme properties
    and showing how to organize styling for different widget types.
    """

    # Expanded theme configuration
    # Notice we're using more specific property paths
    theme_config = {
        # Window/background properties
        'window_bg': 'window.background',
        'window_fg': 'window.foreground',

        # Button properties
        'button_bg': 'button.background',
        'button_fg': 'button.foreground',
        'button_hover': 'button.hover.background',
        'button_border': 'button.border',

        # Card/panel properties
        'card_bg': 'card.background',
        'card_fg': 'card.foreground',
        'card_border': 'card.border',

        # Text properties
        'title_color': 'text.title.color',
        'body_color': 'text.body.color',
        'caption_color': 'text.caption.color',

        # Status colors
        'success_color': 'status.success',
        'warning_color': 'status.warning',
        'error_color': 'status.error',

        # Accent colors
        'primary_accent': 'accent.primary',
        'secondary_accent': 'accent.secondary'
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_theme = 'ocean'  # Start with our custom theme
        self.setup_ui()

    def setup_ui(self):
        """Set up a more complex UI to demonstrate theme properties."""
        layout = QVBoxLayout(self)

        # Title section
        self.title_label = QLabel("Custom Theme Demo")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        # Info card
        self.info_card = QFrame()
        self.info_card.setFrameStyle(QFrame.Box)
        card_layout = QVBoxLayout(self.info_card)

        self.card_title = QLabel("Theme Information")
        card_layout.addWidget(self.card_title)

        self.card_body = QLabel("This card demonstrates themed panels with borders.")
        self.card_body.setWordWrap(True)
        card_layout.addWidget(self.card_body)

        self.card_caption = QLabel("Caption text in muted color")
        card_layout.addWidget(self.card_caption)

        layout.addWidget(self.info_card)

        # Status indicators
        status_layout = QHBoxLayout()

        self.success_label = QLabel("✓ Success")
        self.success_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.success_label)

        self.warning_label = QLabel("⚠ Warning")
        self.warning_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.warning_label)

        self.error_label = QLabel("✗ Error")
        self.error_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.error_label)

        layout.addLayout(status_layout)

        # Theme selection buttons
        button_layout = QHBoxLayout()

        self.ocean_btn = QPushButton("Ocean Theme")
        self.ocean_btn.clicked.connect(lambda: self.switch_theme('ocean'))
        button_layout.addWidget(self.ocean_btn)

        self.sunset_btn = QPushButton("Sunset Theme")
        self.sunset_btn.clicked.connect(lambda: self.switch_theme('sunset'))
        button_layout.addWidget(self.sunset_btn)

        self.forest_btn = QPushButton("Forest Theme")
        self.forest_btn.clicked.connect(lambda: self.switch_theme('forest'))
        button_layout.addWidget(self.forest_btn)

        self.mono_btn = QPushButton("Monochrome")
        self.mono_btn.clicked.connect(lambda: self.switch_theme('monochrome'))
        button_layout.addWidget(self.mono_btn)

        layout.addLayout(button_layout)

        # Current theme display
        self.theme_display = QLabel()
        self.theme_display.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.theme_display)

    def on_theme_changed(self):
        """Update styling when theme changes."""
        self.update_styling()

    def update_styling(self):
        """Apply theme properties to all widgets."""
        # Get all theme properties
        window_bg = self.theme.get('window_bg', '#ffffff')
        window_fg = self.theme.get('window_fg', '#000000')

        button_bg = self.theme.get('button_bg', '#e0e0e0')
        button_fg = self.theme.get('button_fg', '#000000')
        button_hover = self.theme.get('button_hover', '#d0d0d0')
        button_border = self.theme.get('button_border', '#cccccc')

        card_bg = self.theme.get('card_bg', '#f8f8f8')
        card_fg = self.theme.get('card_fg', '#000000')
        card_border = self.theme.get('card_border', '#dddddd')

        title_color = self.theme.get('title_color', '#000000')
        body_color = self.theme.get('body_color', '#333333')
        caption_color = self.theme.get('caption_color', '#666666')

        success_color = self.theme.get('success_color', '#28a745')
        warning_color = self.theme.get('warning_color', '#ffc107')
        error_color = self.theme.get('error_color', '#dc3545')

        primary_accent = self.theme.get('primary_accent', '#007bff')

        # Apply window styling
        self.setStyleSheet(f"""
        CustomThemedWidget {{
            background-color: {window_bg};
            color: {window_fg};
            padding: 20px;
        }}
        """)

        # Apply title styling
        self.title_label.setStyleSheet(f"""
        QLabel {{
            color: {title_color};
            font-size: 24px;
            font-weight: bold;
            margin: 10px;
        }}
        """)

        # Apply card styling
        self.info_card.setStyleSheet(f"""
        QFrame {{
            background-color: {card_bg};
            color: {card_fg};
            border: 2px solid {card_border};
            border-radius: 8px;
            padding: 10px;
            margin: 10px;
        }}
        """)

        self.card_title.setStyleSheet(f"""
        QLabel {{
            color: {primary_accent};
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        """)

        self.card_body.setStyleSheet(f"""
        QLabel {{
            color: {body_color};
            font-size: 14px;
            margin-bottom: 5px;
        }}
        """)

        self.card_caption.setStyleSheet(f"""
        QLabel {{
            color: {caption_color};
            font-size: 12px;
            font-style: italic;
        }}
        """)

        # Apply status colors
        self.success_label.setStyleSheet(f"""
        QLabel {{
            color: {success_color};
            font-weight: bold;
            padding: 5px;
        }}
        """)

        self.warning_label.setStyleSheet(f"""
        QLabel {{
            color: {warning_color};
            font-weight: bold;
            padding: 5px;
        }}
        """)

        self.error_label.setStyleSheet(f"""
        QLabel {{
            color: {error_color};
            font-weight: bold;
            padding: 5px;
        }}
        """)

        # Apply button styling
        button_style = f"""
        QPushButton {{
            background-color: {button_bg};
            color: {button_fg};
            border: 2px solid {button_border};
            border-radius: 4px;
            padding: 8px 16px;
            font-size: 12px;
            min-width: 80px;
        }}

        QPushButton:hover {{
            background-color: {button_hover};
        }}

        QPushButton:pressed {{
            background-color: {button_border};
        }}
        """

        for btn in [self.ocean_btn, self.sunset_btn, self.forest_btn, self.mono_btn]:
            btn.setStyleSheet(button_style)

        # Update theme display
        self.theme_display.setText(f"Current Theme: {self.current_theme.title()}")
        self.theme_display.setStyleSheet(f"""
        QLabel {{
            color: {primary_accent};
            font-size: 14px;
            font-weight: bold;
            margin: 10px;
        }}
        """)

    def switch_theme(self, theme_name):
        """Switch to the specified theme."""
        app = ThemedApplication.instance()
        self.current_theme = theme_name
        app.set_theme(theme_name)
        print(f"Switched to {theme_name} theme")


def create_custom_themes():
    """
    Create our custom themes.

    This function demonstrates how to structure theme data
    with comprehensive property definitions.
    """

    # Ocean Theme - Cool blues and teals
    ocean_theme = {
        'name': 'ocean',
        'window': {
            'background': '#f0f8ff',    # Alice blue
            'foreground': '#2c3e50'     # Dark blue-gray
        },
        'button': {
            'background': '#3498db',    # Blue
            'foreground': '#ffffff',    # White
            'hover': {'background': '#2980b9'},  # Darker blue
            'border': '#2980b9'
        },
        'card': {
            'background': '#ffffff',    # White
            'foreground': '#2c3e50',    # Dark blue-gray
            'border': '#bdc3c7'         # Light gray
        },
        'text': {
            'title': {'color': '#2980b9'},     # Blue
            'body': {'color': '#34495e'},      # Dark gray
            'caption': {'color': '#7f8c8d'}    # Gray
        },
        'status': {
            'success': '#27ae60',       # Green
            'warning': '#f39c12',       # Orange
            'error': '#e74c3c'          # Red
        },
        'accent': {
            'primary': '#3498db',       # Blue
            'secondary': '#1abc9c'      # Teal
        }
    }

    # Sunset Theme - Warm oranges and reds
    sunset_theme = {
        'name': 'sunset',
        'window': {
            'background': '#fff5f0',    # Very light orange
            'foreground': '#5d4037'     # Brown
        },
        'button': {
            'background': '#ff6b35',    # Orange-red
            'foreground': '#ffffff',    # White
            'hover': {'background': '#e55a2e'},
            'border': '#e55a2e'
        },
        'card': {
            'background': '#ffffff',    # White
            'foreground': '#5d4037',    # Brown
            'border': '#ffab91'         # Light orange
        },
        'text': {
            'title': {'color': '#d84315'},     # Dark orange
            'body': {'color': '#6d4c41'},      # Brown
            'caption': {'color': '#8d6e63'}    # Light brown
        },
        'status': {
            'success': '#4caf50',       # Green
            'warning': '#ff9800',       # Orange
            'error': '#f44336'          # Red
        },
        'accent': {
            'primary': '#ff6b35',       # Orange-red
            'secondary': '#ffab40'      # Light orange
        }
    }

    # Forest Theme - Natural greens
    forest_theme = {
        'name': 'forest',
        'window': {
            'background': '#f1f8e9',    # Very light green
            'foreground': '#1b5e20'     # Dark green
        },
        'button': {
            'background': '#4caf50',    # Green
            'foreground': '#ffffff',    # White
            'hover': {'background': '#43a047'},
            'border': '#43a047'
        },
        'card': {
            'background': '#ffffff',    # White
            'foreground': '#1b5e20',    # Dark green
            'border': '#a5d6a7'         # Light green
        },
        'text': {
            'title': {'color': '#2e7d32'},     # Green
            'body': {'color': '#388e3c'},      # Green
            'caption': {'color': '#66bb6a'}    # Light green
        },
        'status': {
            'success': '#4caf50',       # Green
            'warning': '#ff9800',       # Orange
            'error': '#f44336'          # Red
        },
        'accent': {
            'primary': '#4caf50',       # Green
            'secondary': '#8bc34a'      # Light green
        }
    }

    # Monochrome Theme - Black, white, and grays
    monochrome_theme = {
        'name': 'monochrome',
        'window': {
            'background': '#fafafa',    # Very light gray
            'foreground': '#212121'     # Very dark gray
        },
        'button': {
            'background': '#616161',    # Gray
            'foreground': '#ffffff',    # White
            'hover': {'background': '#424242'},
            'border': '#424242'
        },
        'card': {
            'background': '#ffffff',    # White
            'foreground': '#212121',    # Very dark gray
            'border': '#e0e0e0'         # Light gray
        },
        'text': {
            'title': {'color': '#000000'},     # Black
            'body': {'color': '#424242'},      # Dark gray
            'caption': {'color': '#757575'}    # Gray
        },
        'status': {
            'success': '#424242',       # Dark gray
            'warning': '#616161',       # Gray
            'error': '#212121'          # Very dark gray
        },
        'accent': {
            'primary': '#212121',       # Very dark gray
            'secondary': '#616161'      # Gray
        }
    }

    return [ocean_theme, sunset_theme, forest_theme, monochrome_theme]


def main():
    """Main function demonstrating custom themes."""
    print("Tutorial 02: Custom Theme")
    print("=" * 30)

    # Create the application
    app = ThemedApplication(sys.argv)

    # Create and register our custom themes
    print("Creating custom themes...")
    themes = create_custom_themes()

    for theme in themes:
        app.register_theme(theme['name'], theme)
        print(f"Registered theme: {theme['name']}")

    # Set initial theme
    app.set_theme('ocean')
    print("Set initial theme to 'ocean'")

    # Create and show the widget
    widget = CustomThemedWidget()
    widget.setWindowTitle("Tutorial 02: Custom Theme")
    widget.setMinimumSize(600, 500)
    widget.show()

    print("\nCustom themes created!")
    print("Try switching between Ocean, Sunset, Forest, and Monochrome themes.")
    print("Notice how each theme provides a completely different look and feel.")

    return app.exec()


if __name__ == '__main__':
    """
    Tutorial 02 demonstrates:

    1. Creating comprehensive theme definitions
    2. Using multiple theme properties in one widget
    3. Organizing theme data logically
    4. Creating themed UI components (cards, buttons, status indicators)
    5. Best practices for theme property naming

    Key learnings:
    - Theme properties can be nested (e.g., 'button.hover.background')
    - Use semantic naming for theme properties
    - Group related properties together
    - Provide fallback values for all theme.get() calls
    - Consider creating theme families (light/dark variants)
    """
    sys.exit(main())
