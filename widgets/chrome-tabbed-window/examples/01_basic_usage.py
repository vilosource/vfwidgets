#!/usr/bin/env python3
"""
Basic ChromeTabbedWindow usage example.

Demonstrates that ChromeTabbedWindow is a drop-in replacement for QTabWidget.
"""

import sys
from pathlib import Path

# Add src to path so we can import ChromeTabbedWindow
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget

from chrome_tabbed_window import ChromeTabbedWindow


class ExampleWidget(QWidget):
    """Example widget to put in tabs."""

    def __init__(self, name: str, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # Add some content
        layout.addWidget(QLabel(f"This is {name}"))
        layout.addWidget(QLabel(f"Content for tab: {name}"))

        # Add a button
        button = QPushButton(f"Button in {name}")
        button.clicked.connect(lambda: print(f"Button clicked in {name}"))
        layout.addWidget(button)

        layout.addStretch()


class MainWindow(QMainWindow):
    """Main window demonstrating ChromeTabbedWindow usage."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChromeTabbedWindow Basic Example")
        self.setGeometry(100, 100, 800, 600)

        # Create the ChromeTabbedWindow
        self.tabs = ChromeTabbedWindow(self)

        # Connect signals to see them working
        self.tabs.currentChanged.connect(self.on_current_changed)
        self.tabs.tabCloseRequested.connect(self.on_tab_close_requested)

        # Add some tabs
        for i in range(4):
            widget = ExampleWidget(f"Tab {i + 1}")
            index = self.tabs.addTab(widget, f"Tab {i + 1}")
            print(f"Added tab at index: {index}")

        # Enable close buttons
        self.tabs.setTabsClosable(True)

        # Set as central widget
        self.setCentralWidget(self.tabs)

        # Print initial state
        print(f"Initial tab count: {self.tabs.count()}")
        print(f"Initial current index: {self.tabs.currentIndex()}")

    def on_current_changed(self, index: int):
        """Handle current tab change."""
        print(f"Current tab changed to: {index}")
        if index >= 0:
            widget = self.tabs.currentWidget()
            print(f"Current widget: {widget}")
            print(f"Current tab text: {self.tabs.tabText(index)}")

    def on_tab_close_requested(self, index: int):
        """Handle tab close request."""
        print(f"Close requested for tab: {index}")
        tab_text = self.tabs.tabText(index)
        print(f"Removing tab: {tab_text}")
        self.tabs.removeTab(index)
        print(f"Tab count after removal: {self.tabs.count()}")


def main():
    """Run the example."""
    app = QApplication(sys.argv)

    # Test basic functionality first
    print("=== Testing Basic API ===")
    tabs = ChromeTabbedWindow()

    # Test empty state
    print(f"Empty tab count: {tabs.count()}")
    print(f"Empty current index: {tabs.currentIndex()}")

    # Test adding tabs
    widget1 = QLabel("Widget 1")
    widget2 = QLabel("Widget 2")

    idx1 = tabs.addTab(widget1, "First Tab")
    print(f"Added first tab at index: {idx1}")
    print(f"Count after first: {tabs.count()}")
    print(f"Current after first: {tabs.currentIndex()}")

    idx2 = tabs.addTab(widget2, "Second Tab")
    print(f"Added second tab at index: {idx2}")
    print(f"Count after second: {tabs.count()}")
    print(f"Current after second: {tabs.currentIndex()}")

    # Test changing current
    tabs.setCurrentIndex(1)
    print(f"Set current to 1, actual current: {tabs.currentIndex()}")

    print("=== Basic API Test Complete ===\n")

    # Show the main window
    window = MainWindow()
    window.show()

    # Test some API methods while running
    print("\n=== Testing Additional API ===")
    print(f"Tabs closable: {window.tabs.tabsClosable()}")
    print(f"Movable: {window.tabs.isMovable()}")
    print(f"Document mode: {window.tabs.documentMode()}")

    # Test tab properties
    if window.tabs.count() > 0:
        print(f"First tab text: {window.tabs.tabText(0)}")
        print(f"First tab enabled: {window.tabs.isTabEnabled(0)}")
        print(f"First tab visible: {window.tabs.isTabVisible(0)}")

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
