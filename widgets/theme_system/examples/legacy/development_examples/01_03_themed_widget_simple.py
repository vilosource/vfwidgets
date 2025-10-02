#!/usr/bin/env python3
"""
Simple ThemedWidget Example

This example demonstrates the basic usage of ThemedWidget - the primary API
for creating themed widgets. This showcases the core philosophy:

"ThemedWidget provides clean architecture as THE way. Simple API,
correct implementation, no compromises."

Features demonstrated:
- Simple inheritance from ThemedWidget
- Automatic theme registration and cleanup
- Basic property access with fallbacks
- Theme change notifications
- Error recovery

Run this example:
    python themed_widget_simple.py
"""

import sys
import time
from pathlib import Path

# Add the source directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    import os

    from PySide6.QtCore import QTimer
    from PySide6.QtGui import QColor, QPainter
    from PySide6.QtWidgets import QHBoxLayout, QLabel, QMainWindow, QPushButton, QVBoxLayout

    # Force headless mode if no display available
    if not os.environ.get('DISPLAY') and not os.environ.get('WAYLAND_DISPLAY'):
        print("No display available - running in demonstration mode without Qt GUI")
        QT_AVAILABLE = False
    else:
        QT_AVAILABLE = True
except ImportError:
    print("PySide6 not available. This example requires PySide6 for full functionality.")
    print("Install with: pip install PySide6")
    QT_AVAILABLE = False

    # Fallback implementations
    class QVBoxLayout:
        def addWidget(self, widget): pass
    class QHBoxLayout:
        def addWidget(self, widget): pass
    class QPushButton:
        def __init__(self, text): self.text = text
        def clicked(self): pass
    class QLabel:
        def __init__(self, text): self.text = text
        def setText(self, text): self.text = text
    class QMainWindow:
        def __init__(self): pass
        def setCentralWidget(self, widget): pass
        def show(self): pass
    class QTimer:
        def __init__(self): pass
        def start(self, ms): pass
        def timeout(self): pass
    class QPainter:
        def __init__(self, widget): pass
        def fillRect(self, rect, color): pass
    class QColor:
        def __init__(self, color): pass

from vfwidgets_theme.widgets.application import ThemedApplication
from vfwidgets_theme.widgets.base import ThemedWidget


class SimpleThemedButton(ThemedWidget):
    """
    Simple themed button demonstrating basic ThemedWidget usage.

    This is THE way to create themed widgets - just inherit from ThemedWidget
    and optionally define theme_config. All architectural complexity is hidden.
    """

    # Define theme properties - this is optional but provides better control
    theme_config = {
        'bg': 'window.background',
        'fg': 'window.foreground',
        'accent': 'accent.primary',
        'border': 'control.border'
    }

    def __init__(self, text="Themed Button", parent=None):
        """Initialize simple themed button."""
        # Simple inheritance - ThemedWidget handles all complexity
        super().__init__(parent)

        self._text = text
        self._is_hovered = False

        # ThemedWidget automatically:
        # - Registers with theme system
        # - Sets up property access
        # - Handles memory management
        # - Provides error recovery
        # - Enables thread safety

        print(f"✅ Created SimpleThemedButton: {self._text}")
        print(f"   - Widget ID: {self._widget_id}")
        print(f"   - Theme ready: {self.is_theme_ready}")
        print(f"   - Theme config: {self._theme_config}")

    def on_theme_changed(self):
        """
        Override this method to handle theme changes.

        This method is called automatically when the theme changes.
        ThemedWidget handles all the complexity of registration and notifications.
        """
        print(f"🎨 Theme changed for button '{self._text}'")
        print(f"   - Background: {self.theme.get('bg', 'default')}")
        print(f"   - Foreground: {self.theme.get('fg', 'default')}")
        print(f"   - Accent: {self.theme.get('accent', 'default')}")

        # Update button appearance
        self.update()

    def paintEvent(self, event):
        """Paint the themed button."""
        if not QT_AVAILABLE:
            return

        painter = QPainter(self)

        # Use theme properties with automatic fallbacks
        bg_color = self.theme.get('bg', '#ffffff')
        fg_color = self.theme.get('fg', '#000000')
        accent_color = self.theme.get('accent', '#007acc')

        # Simple themed rendering
        if self._is_hovered:
            painter.fillRect(self.rect(), QColor(accent_color))
        else:
            painter.fillRect(self.rect(), QColor(bg_color))

        # Text would be rendered here in a real implementation
        print(f"🎨 Painting button with bg={bg_color}, fg={fg_color}, accent={accent_color}")


class SimpleThemedLabel(ThemedWidget):
    """Simple themed label with minimal theme configuration."""

    # Minimal theme config - uses ThemedWidget defaults for missing properties
    theme_config = {
        'text_color': 'window.foreground',
        'bg_color': 'window.background'
    }

    def __init__(self, text="Themed Label", parent=None):
        super().__init__(parent)
        self._text = text
        print(f"✅ Created SimpleThemedLabel: {self._text}")

    def on_theme_changed(self):
        """Handle theme changes for the label."""
        print(f"📝 Label '{self._text}' theme changed")
        print(f"   - Text color: {self.theme.get('text_color', 'default')}")
        print(f"   - Background: {self.theme.get('bg_color', 'default')}")


class SimpleThemedPanel(ThemedWidget):
    """Simple themed panel that can contain other widgets."""

    # No custom theme_config - uses ThemedWidget defaults

    def __init__(self, parent=None):
        super().__init__(parent)

        # Create child widgets - they automatically inherit theming
        self.button1 = SimpleThemedButton("Button 1", self)
        self.button2 = SimpleThemedButton("Button 2", self)
        self.label = SimpleThemedLabel("Panel Label", self)

        print("✅ Created SimpleThemedPanel with child widgets")
        print("   - Child widgets automatically themed")

    def on_theme_changed(self):
        """Handle theme changes for the panel."""
        print("📋 Panel theme changed")
        # Child widgets are automatically updated by ThemedWidget


class SimpleExample:
    """Demonstration of simple ThemedWidget usage."""

    def __init__(self):
        """Initialize the simple example."""
        print("🚀 Starting Simple ThemedWidget Example")
        print("="*60)

        # Create themed application - this sets up the entire theme system
        if QT_AVAILABLE:
            self.app = ThemedApplication([])
        else:
            # Fallback for testing without Qt
            self.app = ThemedApplication()

        print("✅ ThemedApplication created")
        print(f"   - Available themes: {[t.name if hasattr(t, 'name') else str(t) for t in self.app.get_available_themes()]}")
        print(f"   - Current theme: {self.app.get_current_theme().name if self.app.get_current_theme() else 'None'}")

        # Create themed widgets - demonstrates the simple API
        self.create_widgets()

        # Demonstrate theme switching
        self.demonstrate_theme_switching()

        # Demonstrate error recovery
        self.demonstrate_error_recovery()

        # Show performance statistics
        self.show_performance_stats()

    def create_widgets(self):
        """Create themed widgets demonstrating simple usage."""
        print("\n🏗️ Creating Themed Widgets")
        print("-" * 30)

        # Ensure application is ready before creating Qt widgets
        if QT_AVAILABLE:
            # Process any pending Qt events to ensure app is ready
            if hasattr(self.app, 'processEvents'):
                self.app.processEvents()

        try:
            # Simple widget creation - just inherit from ThemedWidget
            self.widgets = [
                SimpleThemedButton("Primary Button"),
                SimpleThemedButton("Secondary Button"),
                SimpleThemedLabel("Header Label"),
                SimpleThemedLabel("Status Label"),
                SimpleThemedPanel()
            ]
        except Exception as e:
            print(f"   - Error creating Qt widgets (using fallback mode): {e}")
            # Create widgets anyway for demonstration - they'll use fallback implementations
            self.widgets = [
                SimpleThemedButton("Primary Button"),
                SimpleThemedButton("Secondary Button"),
                SimpleThemedLabel("Header Label"),
                SimpleThemedLabel("Status Label"),
                SimpleThemedPanel()
            ]

        print(f"✅ Created {len(self.widgets)} themed widgets")

        # All widgets are automatically:
        # - Registered with the theme system
        # - Connected to theme change notifications
        # - Set up with memory management
        # - Protected by error recovery

    def demonstrate_theme_switching(self):
        """Demonstrate automatic theme switching."""
        print("\n🎨 Demonstrating Theme Switching")
        print("-" * 35)

        # Get available themes
        available_themes = self.app.get_available_themes()
        theme_names = [theme.name if hasattr(theme, 'name') else str(theme) for theme in available_themes]

        # Switch between themes - all widgets update automatically
        for theme_name in theme_names[:3]:  # Test first 3 themes
            print(f"\n🔄 Switching to theme: {theme_name}")
            success = self.app.set_theme(theme_name)
            print(f"   - Switch successful: {success}")

            # All ThemedWidgets automatically receive the theme change
            # No manual updates needed - this is the power of ThemedWidget

            # Small delay to show the switching
            if QT_AVAILABLE:
                self.app.processEvents()
            time.sleep(0.1)

    def demonstrate_error_recovery(self):
        """Demonstrate error recovery capabilities."""
        print("\n🛡️ Demonstrating Error Recovery")
        print("-" * 35)

        # Try to set a non-existent theme - should fallback gracefully
        print("🔄 Attempting to set non-existent theme...")
        success = self.app.set_theme("nonexistent_theme")
        print(f"   - Handled gracefully: {not success}")

        current_theme = self.app.get_current_theme()
        if current_theme:
            print(f"   - Fell back to: {current_theme.name}")

        # Create widget with invalid theme config - should still work
        print("🔄 Creating widget with problematic config...")
        try:
            class ProblematicWidget(ThemedWidget):
                theme_config = {
                    'invalid_property': 'nonexistent.path.to.nowhere'
                }

                def __init__(self):
                    super().__init__()
                    # Try to access invalid property - should get fallback
                    value = self.theme.get('invalid_property', 'fallback_value')
                    print(f"   - Got fallback value: {value}")

            widget = ProblematicWidget()
            print("   ✅ Widget created successfully despite invalid config")

            # Cleanup
            widget._cleanup_theme()

        except Exception as e:
            print(f"   - Error (unexpected): {e}")

    def show_performance_stats(self):
        """Show performance statistics."""
        print("\n📊 Performance Statistics")
        print("-" * 25)

        # Get application-level stats
        try:
            stats = self.app.get_performance_statistics()
            print("✅ Application Statistics:")
            print(f"   - Total themes: {stats.get('total_themes', 'N/A')}")
            print(f"   - Total widgets: {stats.get('total_widgets', 'N/A')}")
            print(f"   - Theme switches: {stats.get('theme_switches', 'N/A')}")
            print(f"   - Average switch time: {stats.get('average_switch_time', 0):.3f}s")
            print(f"   - Widgets updated: {stats.get('widgets_updated', 'N/A')}")

        except Exception as e:
            print(f"   - Could not get stats: {e}")

        # Get widget-level stats
        print("✅ Widget Statistics:")
        for i, widget in enumerate(self.widgets):
            try:
                if hasattr(widget, 'theme_statistics'):
                    stats = widget.theme_statistics
                    print(f"   - Widget {i+1}: {stats.get('update_count', 0)} updates, "
                          f"cache hit rate: {stats.get('hit_rate', 0):.1%}")
            except Exception as e:
                print(f"   - Widget {i+1}: stats unavailable ({e})")

    def cleanup(self):
        """Clean up the example."""
        print("\n🧹 Cleaning Up")
        print("-" * 15)

        # Clean up widgets - ThemedWidget handles this automatically
        for widget in self.widgets:
            widget._cleanup_theme()

        # Clean up application
        self.app.cleanup()

        print("✅ Cleanup completed")

    def run(self):
        """Run the example."""
        try:
            # Example has been demonstrated during initialization
            print("\n🎉 Simple ThemedWidget Example Completed Successfully!")
            print("="*60)
            print("\nKey Takeaways:")
            print("1. ThemedWidget provides THE simple way to create themed widgets")
            print("2. Just inherit and optionally define theme_config")
            print("3. All complexity is hidden - automatic registration, cleanup, error recovery")
            print("4. Performance is optimized with sub-microsecond property access")
            print("5. Thread-safe operations work transparently")
            print("6. Memory management is handled automatically")

            if not QT_AVAILABLE:
                print("\n💡 For full Qt functionality, install PySide6:")
                print("   pip install PySide6")

        finally:
            self.cleanup()


def main():
    """Main entry point."""
    try:
        example = SimpleExample()
        example.run()
        return 0

    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
        return 1

    except Exception as e:
        print(f"\n❌ Error running example: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
