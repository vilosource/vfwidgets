#!/usr/bin/env python3
"""
Interactive test for new tab and close buttons.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

from chrome_tabbed_window import ChromeTabbedWindow


def main():
    app = QApplication(sys.argv)

    # Create frameless Chrome window
    chrome = ChromeTabbedWindow()
    chrome.setWindowTitle("Button Test - Click + to add, X to close tabs")
    chrome.resize(800, 600)
    chrome.setTabsClosable(True)

    # Add initial tabs
    for i in range(3):
        content = QWidget()
        layout = QVBoxLayout(content)
        label = QLabel(f"<h2>Tab {i + 1}</h2>")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        instruction = QLabel("Click the + button to add a new tab\nClick the X on a tab to close it")
        instruction.setAlignment(Qt.AlignCenter)
        layout.addWidget(instruction)
        chrome.addTab(content, f"Tab {i + 1}")

    # Connect close signal
    def handle_close(index):
        print(f"Closing tab at index {index}")
        if chrome.count() > 1:
            chrome.removeTab(index)
        else:
            print("Cannot close last tab")

    chrome.tabCloseRequested.connect(handle_close)

    # Show status
    print("=" * 60)
    print("INTERACTIVE BUTTON TEST")
    print("=" * 60)
    print("\nInstructions:")
    print("1. Click the + button in the tab bar to add a new tab")
    print("2. Click the X button on any tab to close it")
    print("3. Watch the console for feedback")
    print("\nCurrent state:")
    print(f"- Tab count: {chrome.count()}")
    print(f"- Tabs closable: {chrome.tabsClosable()}")
    print("=" * 60)

    chrome.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
