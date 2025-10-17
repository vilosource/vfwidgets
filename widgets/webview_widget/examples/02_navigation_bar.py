"""02_navigation_bar.py

Demonstrate the NavigationBar component by itself.

This example shows:
- How to use NavigationBar standalone
- How to connect to its signals
- How to update its state programmatically
- How navigation controls work

Educational Focus:
    This shows that NavigationBar is a reusable component
    that can be used independently of the full BrowserWidget.
    You could use this in your own custom browser implementation.
"""

import sys

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget

# Import our NavigationBar
from vfwidgets_webview import NavigationBar


class NavigationDemo(QWidget):
    """Demo widget showing NavigationBar with a text display."""

    def __init__(self):
        super().__init__()

        # Create navigation bar
        self.navbar = NavigationBar()

        # Create text display to show events
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("Navigation events will appear here...")

        # Setup layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.navbar)
        layout.addWidget(self.log)

        # Connect signals to log events
        self.navbar.back_clicked.connect(self.on_back)
        self.navbar.forward_clicked.connect(self.on_forward)
        self.navbar.reload_clicked.connect(self.on_reload)
        self.navbar.stop_clicked.connect(self.on_stop)
        self.navbar.home_clicked.connect(self.on_home)
        self.navbar.url_submitted.connect(self.on_url_submitted)

        # Set initial state
        self.navbar.set_url("https://example.com")
        self.log_event("Navigation bar initialized")
        self.log_event("Try typing a URL and pressing Enter!")
        self.log_event("Click the buttons to see events logged here.")

        # Simulate having some history (enable buttons)
        self.navbar.set_back_enabled(True)
        self.navbar.set_forward_enabled(True)

    def log_event(self, message: str) -> None:
        """Add event to log."""
        self.log.append(f"• {message}")

    @Slot()
    def on_back(self):
        """Handle back button click."""
        self.log_event("🔙 Back button clicked")
        # In a real browser, we'd call webview.back()

    @Slot()
    def on_forward(self):
        """Handle forward button click."""
        self.log_event("▶️  Forward button clicked")
        # In a real browser, we'd call webview.forward()

    @Slot()
    def on_reload(self):
        """Handle reload button click."""
        self.log_event("🔄 Reload button clicked")
        # In a real browser, we'd call webview.reload()

        # Simulate loading
        self.simulate_loading()

    @Slot()
    def on_stop(self):
        """Handle stop button click."""
        self.log_event("⏹️  Stop button clicked")
        # Stop the simulated loading
        self.navbar.set_loading(False)

    @Slot()
    def on_home(self):
        """Handle home button click."""
        self.log_event("🏠 Home button clicked")
        self.navbar.set_url("https://example.com")

    @Slot(str)
    def on_url_submitted(self, url: str):
        """Handle URL submission."""
        self.log_event(f"📄 URL submitted: {url}")

        # Update URL bar (in real browser, webview would do this)
        self.navbar.set_url(url)

        # Simulate loading
        self.simulate_loading()

    def simulate_loading(self):
        """Simulate page loading with progress."""
        from PySide6.QtCore import QTimer

        self.log_event("Loading started...")
        self.navbar.set_loading(True)

        # Simulate progress updates
        progress = 0

        def update_progress():
            nonlocal progress
            progress += 10
            self.navbar.set_progress(progress)

            if progress >= 100:
                self.navbar.set_loading(False)
                self.log_event("Loading finished!")
            else:
                QTimer.singleShot(100, update_progress)

        QTimer.singleShot(100, update_progress)


def main():
    """Create and show the navigation bar demo."""
    # Create Qt application
    app = QApplication(sys.argv)

    # Create main window
    window = QMainWindow()
    window.setWindowTitle("NavigationBar Demo - vfwidgets-webview")

    # Create demo widget
    demo = NavigationDemo()

    # Set as central widget
    window.setCentralWidget(demo)

    # Show window
    window.resize(800, 600)
    window.show()

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
