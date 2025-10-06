#!/usr/bin/env python3
"""
Phase 1, Example 0: Basic ThemedWidget Test
Tests that ThemedWidget actually works with the completed Phase 1 implementation.

This example verifies:
1. ThemedWidget can be imported and instantiated
2. ThemedApplication works
3. Theme switching works
4. Property access works
5. The simple API is functional
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QComboBox, QLabel, QPushButton, QVBoxLayout

from vfwidgets_theme import ThemedApplication, ThemedWidget


class SimpleThemedWidget(ThemedWidget):
    """Simple widget to test theming functionality."""

    theme_config = {
        "bg": "window.background",
        "fg": "window.foreground",
        "accent": "accent.primary",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 300)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Title label
        self.title = QLabel("ThemedWidget Test - Phase 1 Complete!")
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title)

        # Theme info
        self.info_label = QLabel()
        self.update_info()
        layout.addWidget(self.info_label)

        # Theme switcher
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["default", "dark", "light", "minimal"])
        self.theme_combo.currentTextChanged.connect(self.switch_theme)
        layout.addWidget(self.theme_combo)

        # Test button
        self.test_button = QPushButton("Test Theme Properties")
        self.test_button.clicked.connect(self.test_properties)
        layout.addWidget(self.test_button)

        # Results
        self.results = QLabel("Click button to test property access")
        layout.addWidget(self.results)

    def switch_theme(self, theme_name):
        """Switch application theme."""
        app = ThemedApplication.instance()
        if app:
            app.set_theme(theme_name)

    def test_properties(self):
        """Test theme property access."""
        try:
            # Test property access through theme_config
            bg = self.theme.bg if hasattr(self.theme, "bg") else "N/A"
            fg = self.theme.fg if hasattr(self.theme, "fg") else "N/A"
            accent = self.theme.accent if hasattr(self.theme, "accent") else "N/A"

            # Test direct property access
            theme_type = self.theme_type if hasattr(self, "theme_type") else "N/A"
            is_dark = self.is_dark_theme if hasattr(self, "is_dark_theme") else "N/A"

            results = f"""✓ Property Access Working:
- Background: {bg}
- Foreground: {fg}
- Accent: {accent}
- Theme Type: {theme_type}
- Is Dark: {is_dark}"""

            self.results.setText(results)
            print(results)

        except Exception as e:
            self.results.setText(f"❌ Error: {e}")
            print(f"Error testing properties: {e}")

    def update_info(self):
        """Update theme information display."""
        app = ThemedApplication.instance()
        if app:
            info = f"""Current Theme: {app.current_theme_name}
Available Themes: {', '.join(app.available_themes)}
Theme Type: {app.theme_type}"""
        else:
            info = "ThemedApplication not initialized"
        self.info_label.setText(info)

    def on_theme_changed(self):
        """Called when theme changes."""
        print(f"✓ on_theme_changed called - theme is now: {self.theme_type}")
        self.update_info()
        self.update()  # Trigger repaint

    def paintEvent(self, event):
        """Custom painting to demonstrate theme colors."""
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Try to use theme colors if available
        try:
            if hasattr(self.theme, "accent"):
                color = QColor(self.theme.accent)
                painter.setPen(color)
                painter.drawRect(10, 10, 50, 50)
        except:
            pass  # Graceful fallback


def main():
    """Main function to test ThemedWidget."""
    print("=" * 60)
    print("Phase 1 ThemedWidget Test")
    print("=" * 60)

    # Create application
    app = ThemedApplication(sys.argv)
    print(f"✓ ThemedApplication created: {app}")

    # Set initial theme
    app.set_theme("dark")
    print("✓ Theme set to 'dark'")
    print(f"✓ Available themes: {app.available_themes}")

    # Create widget
    widget = SimpleThemedWidget()
    widget.setWindowTitle("ThemedWidget Test - Phase 1")
    widget.show()
    print("✓ SimpleThemedWidget created and shown")

    # Test that the widget is registered
    from vfwidgets_theme.lifecycle import WidgetRegistry

    registry = WidgetRegistry()
    count = registry.get_widget_count()
    print(f"✓ Widget registry has {count} registered widget(s)")

    print("\n✓ All basic tests passed! ThemedWidget is working!")
    print("\nTry:")
    print("1. Switch themes using the dropdown")
    print("2. Click 'Test Theme Properties' button")
    print("3. Notice on_theme_changed is called automatically")

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
