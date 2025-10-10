#!/usr/bin/env python3
"""Example demonstrating theme integration in ViloCodeWindow.

This example shows:
- Automatic theme detection and application
- Theme colors applied to all components
- Dynamic theme switching
- Fallback when theme system unavailable
"""

import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

try:
    from vfwidgets_theme import ThemedApplication

    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False

from vfwidgets_vilocode_window import ViloCodeWindow


def main():
    """Demonstrate theme integration."""
    if THEME_AVAILABLE:
        app = ThemedApplication(sys.argv)
        print("=" * 70)
        print("ViloCodeWindow - Theme Integration Demo")
        print("=" * 70)
        print()
        print("Theme system: Available ✓")
        print(f"Current theme: {app.current_theme_name()}")
        print()
    else:
        app = QApplication(sys.argv)
        print("=" * 70)
        print("ViloCodeWindow - Theme Integration Demo (Fallback Mode)")
        print("=" * 70)
        print()
        print("Theme system: Not available (using fallback colors)")
        print()

    # Create window
    window = ViloCodeWindow()
    window.setWindowTitle("ViloCodeWindow - Theme Integration")
    window.resize(1200, 800)

    if THEME_AVAILABLE:
        # Get available themes
        themes = app.available_themes()
        print(f"Available themes: {', '.join(themes)}")
        print()

        # Theme cycling
        theme_index = [0]
        theme_list = list(themes)

        def cycle_theme():
            """Cycle through available themes."""
            theme_index[0] = (theme_index[0] + 1) % len(theme_list)
            theme_name = theme_list[theme_index[0]]
            app.set_theme(theme_name)
            window.set_status_message(f"Theme changed to: {theme_name}", 3000)
            print(f"  [Event] Theme changed to: {theme_name}")

        # Auto-cycle themes every 5 seconds
        timer = QTimer()
        timer.timeout.connect(cycle_theme)
        timer.start(5000)

        window.set_status_message(
            f"Theme: {app.current_theme_name()} - Will auto-cycle every 5 seconds"
        )

        print("Features:")
        print("  • Themes will auto-cycle every 5 seconds")
        print("  • Watch title bar, status bar, and window background colors change")
        print("  • All components automatically update with theme colors")
        print()
        print("Theme Mappings:")
        print("  • Window background  → editor.background")
        print("  • Title bar colors   → titleBar.activeBackground/Foreground")
        print("  • Status bar colors  → statusBar.background/foreground")
        print("  • Border color       → panel.border")
    else:
        window.set_status_message("Using fallback colors (theme system not available)")

        print("Fallback Colors:")
        print("  • Window background:  #1e1e1e (dark gray)")
        print("  • Title bar:          #323233 (gray)")
        print("  • Status bar:         #007acc (blue)")
        print("  • Border:             #333333 (dark gray)")

    print()
    print("The window demonstrates theme integration:")
    print("  • ThemedWidget mixin for automatic theme support")
    print("  • theme_config mapping VS Code tokens")
    print("  • on_theme_changed() handler for dynamic updates")
    print("  • Graceful fallback when theme system unavailable")
    print("=" * 70)

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
