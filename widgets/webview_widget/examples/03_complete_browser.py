"""03_complete_browser.py

The complete browser widget - our MVP!

This example shows:
- How to use BrowserWidget (the complete solution)
- How navigation and webview work together automatically
- How to connect to browser events
- A fully functional single-page browser

Educational Focus:
    This is the TARGET for our MVP. A simple, single-page browser
    like the old school browsers (Mosaic, early Netscape).

    Compare the simplicity of this example to example 02:
    - We don't need to wire signals manually
    - Navigation and webview are already connected
    - We just use the high-level API: navigate(), back(), etc.

    This demonstrates the power of the COMPOSITE pattern!
"""

import sys

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QApplication, QMainWindow

# Import our complete BrowserWidget
from vfwidgets_webview import BrowserWidget


def main():
    """Create and show a complete browser."""
    # Create Qt application
    app = QApplication(sys.argv)

    # Create main window
    window = QMainWindow()
    window.setWindowTitle("VFWidgets Browser - MVP")

    # Create browser widget - THIS IS THE WHOLE BROWSER!
    browser = BrowserWidget(home_url="https://example.com")

    # Optional: Connect to signals to update window title
    @Slot(str)
    def on_title_changed(title: str):
        """Update window title when page title changes."""
        if title:
            window.setWindowTitle(f"{title} - VFWidgets Browser")
        else:
            window.setWindowTitle("VFWidgets Browser - MVP")

    @Slot(bool)
    def on_load_finished(success: bool):
        """Log when page finishes loading."""
        if success:
            print(f"✓ Loaded: {browser.get_url()}")
            print(f"  Title: {browser.get_title()}")
        else:
            print(f"✗ Failed to load: {browser.get_url()}")

    @Slot(int)
    def on_load_progress(progress: int):
        """Show loading progress."""
        if progress < 100:
            print(f"Loading... {progress}%", end="\r")
        else:
            print("")  # New line after completion

    # Connect signals
    browser.title_changed.connect(on_title_changed)
    browser.load_finished.connect(on_load_finished)
    browser.load_progress.connect(on_load_progress)

    # Set as central widget
    window.setCentralWidget(browser)

    # Show window
    window.resize(1200, 800)
    window.show()

    # Navigate to initial page
    print("=== VFWidgets Browser MVP ===")
    print("This is a fully functional single-page browser!")
    print("\nFeatures:")
    print("  • Back/Forward navigation")
    print("  • URL bar with Enter to navigate")
    print("  • Reload/Stop buttons")
    print("  • Home button")
    print("  • Loading progress indicator")
    print("\nKeyboard shortcuts:")
    print("  • Ctrl+L: Focus URL bar")
    print("  • Ctrl+R: Reload page")
    print("  • Alt+Left: Back")
    print("  • Alt+Right: Forward")
    print("\nNavigating to home page...")
    browser.navigate("https://example.com")

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
