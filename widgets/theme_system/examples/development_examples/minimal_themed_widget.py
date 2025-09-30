#!/usr/bin/env python3
"""
Minimal ThemedWidget Example - The Simplest Way to Theme Your Widget

This example shows the absolute minimum code needed to create a themed widget.
Just inherit from ThemedWidget and you get automatic theming!

NOTE: This example requires a Qt environment (GUI display) to run since
ThemedWidget inherits from QWidget. For headless/console demos, see
minimal_api_usage.py instead.

For real Qt applications with display:
1. ThemedApplication replaces QApplication
2. ThemedWidget is mixed with your Qt widget class
3. Theme changes automatically update all widgets
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from vfwidgets_theme import ThemedWidget, ThemedApplication


class MyWidget(ThemedWidget):
    """Your widget - just inherit from ThemedWidget!"""

    # Optional: Map theme properties to your widget
    theme_config = {
        'bg': 'window.background',
        'fg': 'window.foreground'
    }

    def on_theme_changed(self):
        """Optional: Called when theme changes."""
        print(f"Theme changed! Now using: {self.theme_type} theme")
        print(f"  Background: {self.theme.bg}")
        print(f"  Foreground: {self.theme.fg}")


def main():
    """Simple demo of ThemedWidget."""
    print("\n=== Minimal ThemedWidget Example ===\n")
    print("NOTE: This example requires a GUI environment (X11/Wayland display)")
    print("For headless demos, see minimal_api_usage.py\n")

    # Create app first with sys.argv - ThemedApplication IS QApplication
    app = ThemedApplication(sys.argv)
    print(f"Available themes: {app.available_themes}")

    # Now create your widget - it inherits from QWidget through ThemedWidget
    widget = MyWidget()
    print("Widget created with automatic theming!")

    # Switch themes - widget updates automatically!
    print("\nSwitching themes...")
    for theme in ['dark', 'light']:
        app.set_theme(theme)
        print(f"  Set theme to '{theme}'")

    print("\nThat's it! Your widget is fully themed with just inheritance!")
    print("No complex setup, no configuration files - it just works.")

    print("\nIn a real Qt app, you would now:")
    print("  widget.show()  # Show the widget")
    print("  return app.exec()  # Run the event loop")

    # For this demo, we just return since we need a display for the event loop
    return 0


if __name__ == '__main__':
    sys.exit(main())