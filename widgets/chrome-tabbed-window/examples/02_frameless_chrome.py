#!/usr/bin/env python3
"""
Frameless Chrome window example.

Demonstrates ChromeTabbedWindow as a frameless window that looks like Chrome browser.
"""

import sys
from pathlib import Path

# Add src to path so we can import ChromeTabbedWindow
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QTextEdit, QVBoxLayout, QWidget

from chrome_tabbed_window import ChromeTabbedWindow


class WebPageWidget(QWidget):
    """Simulated web page widget for tabs."""

    def __init__(self, title: str, url: str, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # URL bar simulation
        url_label = QLabel(f"🔒 {url}")
        url_label.setStyleSheet("""
            QLabel {
                background: #f1f3f4;
                padding: 8px;
                border-radius: 4px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        layout.addWidget(url_label)

        # Page content
        content = QTextEdit()
        content.setHtml(f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h1>{title}</h1>
                <p>This is a simulated web page in a Chrome-style tab.</p>
                <p>The window has no native title bar - it's using our custom Chrome implementation!</p>
                <ul>
                    <li>Frameless window mode active</li>
                    <li>Custom window controls (minimize, maximize, close)</li>
                    <li>Chrome-style tab rendering</li>
                    <li>Drag the tab bar area to move the window</li>
                </ul>
            </body>
            </html>
        """)
        content.setReadOnly(True)
        layout.addWidget(content)


def create_chrome_window():
    """Create a frameless Chrome-style window."""
    # Create ChromeTabbedWindow as top-level (no parent)
    # This triggers frameless mode automatically
    chrome_window = ChromeTabbedWindow()

    # Set window title (shown in taskbar)
    chrome_window.setWindowTitle("Chrome Browser Clone")

    # Set initial size
    chrome_window.resize(1200, 800)

    # Enable tab close buttons
    chrome_window.setTabsClosable(True)

    # Add some tabs with web page simulation
    tabs = [
        ("Google", "google.com"),
        ("GitHub", "github.com"),
        ("Stack Overflow", "stackoverflow.com"),
        ("YouTube", "youtube.com"),
        ("Reddit", "reddit.com"),
    ]

    for title, url in tabs:
        page = WebPageWidget(title, f"https://{url}")
        chrome_window.addTab(page, title)

    # Connect signals
    chrome_window.tabCloseRequested.connect(lambda index: handle_tab_close(chrome_window, index))

    # Add a new tab button (using corner widget)
    new_tab_button = QPushButton("+")
    new_tab_button.setFixedSize(28, 28)
    new_tab_button.setStyleSheet("""
        QPushButton {
            background: transparent;
            border: none;
            font-size: 20px;
            color: #5f6368;
        }
        QPushButton:hover {
            background: rgba(0, 0, 0, 0.06);
            border-radius: 14px;
        }
    """)
    new_tab_button.clicked.connect(lambda: add_new_tab(chrome_window))
    chrome_window.setCornerWidget(new_tab_button, Qt.Corner.TopRightCorner)

    return chrome_window


def handle_tab_close(window: ChromeTabbedWindow, index: int):
    """Handle tab close with minimum tab requirement."""
    if window.count() > 1:
        window.removeTab(index)
    else:
        # Last tab - close the window
        window.close()


def add_new_tab(window: ChromeTabbedWindow):
    """Add a new tab to the window."""
    tab_count = window.count()
    page = WebPageWidget("New Tab", "newtab")
    index = window.addTab(page, "New Tab")
    window.setCurrentIndex(index)

    # Print compression info
    if hasattr(window, "_tab_bar"):
        tab_bar = window._tab_bar
        if tab_bar.count() > 0:
            size_hint = tab_bar.tabSizeHint(0)
            print(f"Added tab {tab_count + 1}: Tab width is now {size_hint.width()}px")


def main():
    """Run the frameless Chrome example."""
    app = QApplication(sys.argv)

    # Set application name for better integration
    app.setApplicationName("Chrome Clone")

    print("=== Frameless Chrome Window Example ===")
    print("Creating a Chrome browser clone with:")
    print("- Frameless window (no OS title bar)")
    print("- Custom window controls")
    print("- Chrome-style tabs")
    print("- Drag to move window")
    print("")

    # Create and show the Chrome window
    chrome = create_chrome_window()
    chrome.show()

    print(f"Window mode: {chrome._window_mode}")
    print(f"Tab count: {chrome.count()}")
    print("Window is now running in frameless mode!")
    print("")
    print("Try:")
    print("- Clicking the window control buttons")
    print("- Dragging the tab bar to move the window")
    print("- Adding/closing tabs to see compression")
    print("- Hovering over tabs")
    print("")
    print("Tab compression behavior:")
    print("- Tabs compress as more are added (min 52px, max 240px)")
    print("- All tabs always visible (no scroll)")
    print("- Just like Chrome browser!")

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
