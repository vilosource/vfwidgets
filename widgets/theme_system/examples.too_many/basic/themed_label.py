#!/usr/bin/env python3
"""themed_label.py - Themed label with dynamic colors.

Shows how to create labels that respond to theme changes with different
text colors, backgrounds, and font styling.

Key Concepts:
- Dynamic color changes
- Font theming
- Background styling
- Different label types (title, body, caption)

Example usage:
    python themed_label.py
"""

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout

from vfwidgets_theme import ThemedApplication, ThemedWidget


class ThemedLabel(ThemedWidget, QLabel):
    """A themed label that adapts to the current theme."""

    theme_config = {
        'color': 'text.primary',
        'background': 'surface.primary',
        'font': 'text.font',
        'font_size': 'text.size',
        'font_weight': 'text.weight'
    }

    def __init__(self, text="", label_type="body", parent=None):
        super().__init__(parent)
        self.setText(text)
        self._label_type = label_type

        # Set initial styling
        self.update_styling()

    def on_theme_changed(self):
        """Called automatically when theme changes."""
        self.update_styling()

    def update_styling(self):
        """Update label styling based on theme and type."""
        # Base theme properties
        base_color = self.theme.get('color', '#000000')
        bg_color = self.theme.get('background', 'transparent')
        font_family = self.theme.get('font', 'Arial, sans-serif')

        # Type-specific styling
        if self._label_type == 'title':
            color = self.theme.get('text.title.color', base_color)
            font_size = self.theme.get('text.title.size', '18px')
            font_weight = self.theme.get('text.title.weight', 'bold')
        elif self._label_type == 'subtitle':
            color = self.theme.get('text.subtitle.color', base_color)
            font_size = self.theme.get('text.subtitle.size', '14px')
            font_weight = self.theme.get('text.subtitle.weight', 'normal')
        elif self._label_type == 'caption':
            color = self.theme.get('text.caption.color', '#666666')
            font_size = self.theme.get('text.caption.size', '10px')
            font_weight = self.theme.get('text.caption.weight', 'normal')
        elif self._label_type == 'accent':
            color = self.theme.get('accent.primary', '#0066cc')
            font_size = self.theme.get('text.body.size', '12px')
            font_weight = self.theme.get('text.body.weight', 'normal')
        else:  # body
            color = base_color
            font_size = self.theme.get('text.body.size', '12px')
            font_weight = self.theme.get('text.body.weight', 'normal')

        # Generate stylesheet
        stylesheet = f"""
        QLabel {{
            color: {color};
            background-color: {bg_color};
            font-family: {font_family};
            font-size: {font_size};
            font-weight: {font_weight};
            padding: 4px;
        }}
        """

        self.setStyleSheet(stylesheet)

    def set_label_type(self, label_type):
        """Change the label type and update styling."""
        self._label_type = label_type
        self.update_styling()


class LabelDemo(ThemedWidget):
    """Demo window showing different themed label types."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Themed Label Demo")
        self.setMinimumSize(500, 400)

        # Create layout
        layout = QVBoxLayout(self)

        # Create different label types
        self.labels = []

        # Title label
        title = ThemedLabel("This is a Title Label", "title")
        title.setAlignment(Qt.AlignCenter)
        self.labels.append(title)
        layout.addWidget(title)

        # Subtitle label
        subtitle = ThemedLabel("This is a subtitle label", "subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        self.labels.append(subtitle)
        layout.addWidget(subtitle)

        # Body labels
        body1 = ThemedLabel("This is a normal body text label. It uses the default text styling.")
        self.labels.append(body1)
        layout.addWidget(body1)

        body2 = ThemedLabel("Here's another body text label to show consistency.")
        self.labels.append(body2)
        layout.addWidget(body2)

        # Accent label
        accent = ThemedLabel("This is an accent label for highlighting", "accent")
        accent.setAlignment(Qt.AlignCenter)
        self.labels.append(accent)
        layout.addWidget(accent)

        # Caption label
        caption = ThemedLabel("This is a caption with smaller, muted text", "caption")
        caption.setAlignment(Qt.AlignCenter)
        self.labels.append(caption)
        layout.addWidget(caption)

        # Add spacer
        layout.addStretch()

        # Theme switching controls
        self.create_theme_controls(layout)

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

        blue_btn = ThemedButton("Blue Theme")
        blue_btn.clicked.connect(lambda: self.switch_theme('blue'))
        controls_layout.addWidget(blue_btn)

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
    """Run the themed label demo."""
    # Create themed application
    app = ThemedApplication(sys.argv)

    # Register themes with different text styling
    light_theme = {
        'name': 'light',
        'text': {
            'primary': '#333333',
            'font': 'Arial, sans-serif',
            'title': {
                'color': '#000000',
                'size': '20px',
                'weight': 'bold'
            },
            'subtitle': {
                'color': '#444444',
                'size': '16px',
                'weight': '600'
            },
            'body': {
                'size': '13px',
                'weight': 'normal'
            },
            'caption': {
                'color': '#888888',
                'size': '11px',
                'weight': 'normal'
            }
        },
        'surface': {
            'primary': '#ffffff'
        },
        'accent': {
            'primary': '#0066cc'
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
        'text': {
            'primary': '#ffffff',
            'font': 'Arial, sans-serif',
            'title': {
                'color': '#ffffff',
                'size': '20px',
                'weight': 'bold'
            },
            'subtitle': {
                'color': '#cccccc',
                'size': '16px',
                'weight': '600'
            },
            'body': {
                'size': '13px',
                'weight': 'normal'
            },
            'caption': {
                'color': '#888888',
                'size': '11px',
                'weight': 'normal'
            }
        },
        'surface': {
            'primary': '#2d2d2d'
        },
        'accent': {
            'primary': '#66aaff'
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

    blue_theme = {
        'name': 'blue',
        'text': {
            'primary': '#1a1a1a',
            'font': 'Arial, sans-serif',
            'title': {
                'color': '#003366',
                'size': '20px',
                'weight': 'bold'
            },
            'subtitle': {
                'color': '#004488',
                'size': '16px',
                'weight': '600'
            },
            'body': {
                'size': '13px',
                'weight': 'normal'
            },
            'caption': {
                'color': '#666666',
                'size': '11px',
                'weight': 'normal'
            }
        },
        'surface': {
            'primary': '#f0f6ff'
        },
        'accent': {
            'primary': '#0088cc'
        },
        'button': {
            'background': '#e6f2ff',
            'foreground': '#003366',
            'border': '#b3d9ff',
            'hover': {'background': '#cce6ff'},
            'pressed': {'background': '#b3d9ff'},
            'font': 'Arial, sans-serif'
        }
    }

    # Register themes
    app.register_theme('light', light_theme)
    app.register_theme('dark', dark_theme)
    app.register_theme('blue', blue_theme)

    # Set initial theme
    app.set_theme('light')

    # Create and show demo
    demo = LabelDemo()
    demo.show()

    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
