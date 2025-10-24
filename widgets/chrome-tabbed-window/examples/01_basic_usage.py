#!/usr/bin/env python3
"""
Basic ChromeTabbedWindow usage example.

Demonstrates that ChromeTabbedWindow is a drop-in replacement for QTabWidget
with enhanced features like tab editing.

Features demonstrated:
- Adding/removing tabs
- Close buttons
- Tab reordering (drag & drop)
- Tab renaming (double-click)
- Signal connections
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
        title = QLabel(f"<h2>{name}</h2>")
        layout.addWidget(title)

        layout.addWidget(QLabel(f"Content for tab: {name}"))
        layout.addWidget(QLabel(""))

        # Add tip about tab editing
        tip = QLabel(
            "<b>💡 Tip:</b> Double-click the tab title above to rename it!<br>"
            "<small>Press Enter to save, ESC to cancel</small>"
        )
        tip.setWordWrap(True)
        tip.setStyleSheet("color: #0078d4; padding: 10px; background: #f0f0f0; border-radius: 4px;")
        layout.addWidget(tip)

        # Add a button
        button = QPushButton(f"Button in {name}")
        button.clicked.connect(lambda: print(f"Button clicked in {name}"))
        layout.addWidget(button)

        layout.addStretch()


class MainWindow(QMainWindow):
    """Main window demonstrating ChromeTabbedWindow usage."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChromeTabbedWindow Basic Example - Try double-clicking a tab!")
        self.setGeometry(100, 100, 900, 600)

        # Create the ChromeTabbedWindow
        self.tabs = ChromeTabbedWindow(self)

        # Enable features
        self.tabs.setTabsClosable(True)  # Show close buttons
        self.tabs.setMovable(True)  # Allow drag & drop reordering
        self.tabs.setTabsEditable(True)  # Enable tab renaming (NEW!)

        # Set optional validator for tab names
        self.tabs.setTabRenameValidator(self.validate_tab_name)

        # Connect signals to see them working
        self.tabs.currentChanged.connect(self.on_current_changed)
        self.tabs.tabCloseRequested.connect(self.on_tab_close_requested)

        # Connect tab renaming signals (NEW!)
        self.tabs.tabRenameStarted.connect(self.on_tab_rename_started)
        self.tabs.tabRenameFinished.connect(self.on_tab_rename_finished)
        self.tabs.tabRenameCancelled.connect(self.on_tab_rename_cancelled)

        # Add some tabs
        for i in range(4):
            widget = ExampleWidget(f"Tab {i + 1}")
            index = self.tabs.addTab(widget, f"Tab {i + 1}")
            print(f"Added tab at index: {index}")

        # Set as central widget
        self.setCentralWidget(self.tabs)

        # Print initial state
        print(f"Initial tab count: {self.tabs.count()}")
        print(f"Initial current index: {self.tabs.currentIndex()}")
        print(f"Tabs editable: {self.tabs.tabsEditable()}")
        print("\n💡 Double-click any tab title to rename it!\n")

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

    def on_tab_rename_started(self, index: int):
        """Handle tab rename started."""
        old_name = self.tabs.tabText(index)
        print(f"📝 User started editing tab {index}: '{old_name}'")

    def on_tab_rename_finished(self, index: int, new_text: str):
        """Handle tab rename finished."""
        print(f"✅ Tab {index} renamed to: '{new_text}'")

    def on_tab_rename_cancelled(self, index: int):
        """Handle tab rename cancelled."""
        tab_name = self.tabs.tabText(index)
        print(f"🚫 User cancelled editing tab {index}: '{tab_name}'")

    def validate_tab_name(self, index: int, proposed_text: str) -> tuple[bool, str]:
        """
        Validate proposed tab name.

        Args:
            index: Index of tab being renamed
            proposed_text: Proposed new name

        Returns:
            (is_valid, sanitized_text) tuple
        """
        # Trim whitespace
        sanitized = proposed_text.strip()

        # Reject empty names
        if not sanitized:
            print("❌ Validation failed: Empty name rejected")
            return (False, "")

        # Check for duplicates (excluding the tab being renamed)
        for i in range(self.tabs.count()):
            if i != index and self.tabs.tabText(i) == sanitized:
                print(f"❌ Validation failed: Duplicate name '{sanitized}' rejected")
                return (False, "")

        # Valid!
        print(f"✓ Validation passed: '{sanitized}'")
        return (True, sanitized)


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
    print(f"Tabs editable: {window.tabs.tabsEditable()}")  # NEW!
    print(f"Document mode: {window.tabs.documentMode()}")

    # Test tab properties
    if window.tabs.count() > 0:
        print(f"First tab text: {window.tabs.tabText(0)}")
        print(f"First tab enabled: {window.tabs.isTabEnabled(0)}")
        print(f"First tab visible: {window.tabs.isTabVisible(0)}")

    print("\n=== Quick Start Guide ===")
    print("1. Click a tab to switch to it")
    print("2. Drag a tab to reorder it")
    print("3. Double-click a tab title to rename it")
    print("4. Click the X button to close a tab")
    print("5. Try giving two tabs the same name (validation will reject it!)")
    print("\nHave fun exploring ChromeTabbedWindow! 🎉\n")

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
