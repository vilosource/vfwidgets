#!/usr/bin/env python3
"""
Simple Themed Application Example

This example demonstrates how end users should use the VFWidgets Theme System.
It only uses the public API (ThemedApplication and ThemedWidget) and shows
the intended developer experience.

This is THE way to create themed applications with VFWidgets.

Usage:
    python simple_themed_app.py
"""

import sys
from pathlib import Path

# Add the source directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import the public API - this is all you need!
from vfwidgets_theme.widgets.application import ThemedApplication
from vfwidgets_theme.widgets.base import ThemedWidget


class MyButton(ThemedWidget):
    """
    Example themed button - THE simple way to create themed widgets.

    Just inherit from ThemedWidget and optionally define theme_config.
    All complexity is hidden - automatic registration, cleanup, thread safety, etc.
    """

    # Optional: Define which theme properties you want to use
    theme_config = {
        "button_bg": "background",
        "button_fg": "foreground",
        "button_accent": "primary",
    }

    def __init__(self, text="My Button"):
        # Simple inheritance - ThemedWidget handles everything
        super().__init__()
        self.text = text
        print(f"✨ Created themed button: {text}")

        # Theme properties are automatically available via self.theme
        bg = self.theme.get("button_bg", "#ffffff")
        fg = self.theme.get("button_fg", "#000000")
        print(f"   Button colors: bg={bg}, fg={fg}")

    def on_theme_changed(self):
        """
        Called automatically when theme changes.
        Override this to update your widget's appearance.
        """
        print(f"🎨 Theme changed for button '{self.text}'")
        bg = self.theme.get("button_bg", "#ffffff")
        fg = self.theme.get("button_fg", "#000000")
        accent = self.theme.get("button_accent", "#007acc")
        print(f"   New colors: bg={bg}, fg={fg}, accent={accent}")


class MyWindow(ThemedWidget):
    """Example themed window containing multiple widgets."""

    theme_config = {"window_bg": "background", "window_fg": "foreground"}

    def __init__(self):
        super().__init__()

        # Create child widgets - they automatically get themed too!
        self.button1 = MyButton("Primary Button")
        self.button2 = MyButton("Secondary Button")
        self.button3 = MyButton("Action Button")

        print("🏠 Created themed window with child widgets")

    def on_theme_changed(self):
        """Handle theme changes for the window."""
        print("🏠 Window theme changed")
        bg = self.theme.get("window_bg", "#ffffff")
        fg = self.theme.get("window_fg", "#000000")
        print(f"   Window colors: bg={bg}, fg={fg}")


def main():
    """Demonstrate the simple themed application experience."""
    print("=" * 60)
    print("SIMPLE THEMED APPLICATION EXAMPLE")
    print("=" * 60)
    print("This shows THE way to create themed apps with VFWidgets")
    print()

    # Step 1: Create themed application
    print("Step 1: Create ThemedApplication")
    app = ThemedApplication()
    print(f"✅ Application created with {len(app.get_available_themes())} themes")

    # Step 2: See what themes are available
    print("\nStep 2: Discover available themes")
    themes = app.get_available_themes()
    theme_names = [t.name if hasattr(t, "name") else str(t) for t in themes]
    print(f"📋 Available themes: {theme_names}")

    # Step 3: Create themed widgets
    print("\nStep 3: Create themed widgets")
    MyWindow()  # This creates multiple themed widgets
    print("✅ All widgets created and automatically themed")

    # Step 4: Switch themes and see automatic updates
    print("\nStep 4: Switch themes - watch automatic updates!")
    for theme_name in theme_names[:3]:  # Try first 3 themes
        print(f"\n🔄 Switching to: {theme_name}")
        success = app.set_theme(theme_name)
        if success:
            current = app.get_current_theme()
            if current:
                print(f"✅ Now using: {current.name}")
            # All widgets automatically updated - no manual work needed!
        else:
            print(f"❌ Failed to switch to: {theme_name}")

    # Step 5: Show performance statistics
    print("\nStep 5: Check performance")
    try:
        stats = app.get_performance_statistics()
        print("📊 Performance statistics:")
        if "total_themes" in stats:
            print(f"   - Total themes: {stats['total_themes']}")
        if "total_widgets" in stats:
            print(f"   - Total widgets: {stats['total_widgets']}")
        if "initialized" in stats:
            print(f"   - System initialized: {stats['initialized']}")
    except Exception as e:
        print(f"   - Stats not available: {e}")

    # Step 6: Clean up
    print("\nStep 6: Clean up")
    app.cleanup()
    print("✅ Application cleaned up automatically")

    print("\n" + "=" * 60)
    print("EXAMPLE COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\n🎉 Key Points Demonstrated:")
    print("1. ThemedApplication - Simple app-level theme management")
    print("2. ThemedWidget - Simple widget-level theming via inheritance")
    print("3. Automatic theme updates - No manual work needed")
    print("4. Built-in themes - Ready to use out of the box")
    print("5. Clean API - Only 2 classes needed for complete theming")
    print("6. Automatic cleanup - No memory leaks or manual management")

    print("\n💡 For real Qt applications:")
    print("- Add 'from PySide6.QtWidgets import *' imports")
    print("- Create actual Qt widgets in your themed widget classes")
    print("- Use app.exec() to start the Qt event loop")
    print("- Theme changes will automatically update all Qt widgets")

    return 0


if __name__ == "__main__":
    sys.exit(main())
