#!/usr/bin/env python3
"""
Tutorial 01: Hello Theme
========================

This tutorial shows how to create your first themed application.

What you'll learn:
- Creating a ThemedApplication
- Making a ThemedWidget
- Switching themes
- Responding to theme changes

Let's start with the simplest possible themed app...
"""

import os
import sys

# Add the parent directory to sys.path so we can import vfwidgets_theme
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QLabel, QPushButton, QVBoxLayout

# Import the VFWidgets theme system
from vfwidgets_theme import ThemedApplication, ThemedWidget


class HelloThemeWidget(ThemedWidget):
    """
    Our first themed widget!

    This widget demonstrates the basics of using ThemedWidget.
    Simply inherit from ThemedWidget and you automatically get:
    - Theme change notifications
    - Access to theme properties
    - Automatic styling updates
    """

    # Define what theme properties this widget uses
    # This maps semantic names to theme property paths
    theme_config = {
        "bg_color": "colors.background",  # Background color from colors
        "text_color": "colors.foreground",  # Text color from colors
        "accent_color": "colors.accent",  # Accent color from colors
    }

    def __init__(self, parent=None):
        # Always call parent __init__ first
        super().__init__(parent)

        # Set up the UI
        self.setup_ui()

        # Apply initial theme
        self.update_theme_styling()

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Welcome title
        self.title_label = QLabel("Hello, Themed World!")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        # Description
        self.desc_label = QLabel(
            "This is your first themed widget.\n" "Watch how it changes when you switch themes!"
        )
        self.desc_label.setAlignment(Qt.AlignCenter)
        self.desc_label.setWordWrap(True)
        layout.addWidget(self.desc_label)

        # Theme selector
        self.theme_selector = QComboBox()
        layout.addWidget(self.theme_selector)

        # Theme switch button
        self.theme_button = QPushButton("Apply Selected Theme")
        self.theme_button.clicked.connect(self.apply_selected_theme)
        layout.addWidget(self.theme_button)

        # Current theme display
        self.theme_display = QLabel("")
        self.theme_display.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.theme_display)

    def on_theme_changed(self):
        """
        This method is called automatically when the theme changes.

        Override this method to respond to theme changes.
        The theme system will call this whenever:
        - The global theme is switched
        - Theme properties are updated
        - The widget is first created
        """
        print("Theme changed! Updating widget appearance...")
        self.update_theme_styling()

    def update_theme_styling(self):
        """
        Update the widget's appearance based on current theme.

        This demonstrates how to:
        1. Get theme colors using self.theme property access
        2. Apply colors to widgets
        3. Update display based on current theme
        """

        # Access theme properties through the theme config mapping
        # The theme system automatically resolves these to actual values
        bg_color = getattr(self.theme, "bg_color", "#ffffff")
        text_color = getattr(self.theme, "text_color", "#000000")
        accent_color = getattr(self.theme, "accent_color", "#0066cc")

        print(f"Applying theme colors: bg={bg_color}, text={text_color}, accent={accent_color}")

        # Apply colors using Qt stylesheets
        self.setStyleSheet(
            f"""
        HelloThemeWidget {{
            background-color: {bg_color};
            color: {text_color};
            padding: 20px;
            border-radius: 8px;
        }}
        """
        )

        # Style individual widgets
        self.title_label.setStyleSheet(
            f"""
        QLabel {{
            color: {accent_color};
            font-size: 24px;
            font-weight: bold;
            margin: 10px;
        }}
        """
        )

        self.desc_label.setStyleSheet(
            f"""
        QLabel {{
            color: {text_color};
            font-size: 14px;
            margin: 10px;
        }}
        """
        )

        # Update theme display
        app = ThemedApplication.instance()
        if app:
            current_theme = app.current_theme_name
            self.theme_display.setText(f"Current Theme: {current_theme}")

            # Update theme selector if needed
            if self.theme_selector.count() == 0:
                themes = app.available_themes
                self.theme_selector.addItems(themes)
                if current_theme in themes:
                    self.theme_selector.setCurrentText(current_theme)

    def apply_selected_theme(self):
        """Apply the currently selected theme."""
        app = ThemedApplication.instance()
        selected_theme = self.theme_selector.currentText()

        if app and selected_theme:
            print(f"Switching to {selected_theme} theme")
            app.set_theme(selected_theme)


def main():
    """
    Main function to run the tutorial.

    This demonstrates:
    1. Creating a ThemedApplication
    2. Using built-in themes
    3. Setting the initial theme
    4. Creating and showing a themed widget
    """

    print("Tutorial 01: Hello Theme")
    print("=" * 30)
    print("Creating themed application...")

    # Step 1: Create a ThemedApplication
    # This replaces QApplication and adds theme management
    app = ThemedApplication(sys.argv)

    # Step 2: The application comes with built-in themes!
    # No need to register them - they're already available
    print(f"Available themes: {app.available_themes}")
    # Built-in themes are: default, dark, light, minimal

    # Step 3: Set the initial theme
    # You can use any of the built-in themes
    app.set_theme("light")
    print("Set initial theme to 'light'")

    # Step 4: Create and show the themed widget
    widget = HelloThemeWidget()

    # Set window properties
    widget.setWindowTitle("Tutorial 01: Hello Theme")
    widget.setMinimumSize(400, 350)

    # Show the widget
    widget.show()

    print("Widget created and shown!")
    print("\nSelect a theme from the dropdown and click 'Apply Selected Theme'!")
    print("Notice how the colors change automatically.")

    # Run the application
    return app.exec()


if __name__ == "__main__":
    """
    This is where the magic happens!

    When you run this file, it will:
    1. Create a themed application with built-in themes
    2. Show a simple widget that responds to theme changes
    3. Allow you to switch between all available themes

    Key takeaways:
    - ThemedApplication comes with built-in themes (no registration needed!)
    - ThemedWidget automatically handles theme changes
    - Use theme_config to map properties
    - Override on_theme_changed() to respond to theme changes
    - ThemedApplication manages all the theme switching logic
    """
    print(__doc__)
    sys.exit(main())
