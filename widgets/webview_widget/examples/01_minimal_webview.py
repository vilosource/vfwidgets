"""01_minimal_webview.py

The absolute minimum code to create a working web view.

This example shows:
- How to create a WebView
- How to load a URL
- How to display it in a window

Note: This is NOT yet the full browser - that comes later!
This just demonstrates the WebView component we built.
"""

import sys

from PySide6.QtWidgets import QApplication, QMainWindow

# Import our WebView
from vfwidgets_webview import WebView


def main():
    """Create and show a minimal web view."""
    # Create Qt application
    app = QApplication(sys.argv)

    # Create main window
    window = QMainWindow()
    window.setWindowTitle("Minimal WebView Example")

    # Create web view
    webview = WebView()

    # Load a page
    webview.load("https://example.com")

    # Optional: Connect to signals to see what's happening
    webview.load_started.connect(lambda: print("Loading started..."))
    webview.load_progress.connect(lambda p: print(f"Loading: {p}%"))
    webview.load_finished.connect(lambda s: print(f"Loading finished: {s}"))
    webview.title_changed.connect(lambda t: window.setWindowTitle(f"{t} - WebView"))

    # Set as central widget
    window.setCentralWidget(webview)

    # Show window
    window.resize(1024, 768)
    window.show()

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
