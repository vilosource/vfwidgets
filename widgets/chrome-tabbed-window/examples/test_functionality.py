#!/usr/bin/env python3
"""
Test script for verifying new tab and close button functionality.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QLabel

from chrome_tabbed_window import ChromeTabbedWindow


def test_buttons():
    """Test new tab and close buttons programmatically."""
    app = QApplication.instance() or QApplication(sys.argv)

    # Create window
    window = ChromeTabbedWindow()
    window.setTabsClosable(True)
    window.resize(800, 600)

    # Add initial tabs
    for i in range(3):
        label = QLabel(f"Tab {i+1}")
        window.addTab(label, f"Tab {i+1}")

    # Get tab bar
    tab_bar = window._tab_bar

    # Show window briefly to trigger painting (initializes rects)
    window.show()
    tab_bar.update()  # Force update
    QTest.qWait(50)  # Wait for paint event
    app.processEvents()  # Process any pending events

    print(f"Initial tab count: {window.count()}")

    # Test 1: New tab button via signal
    print("\nTest 1: Testing new tab button via signal...")
    initial_count = window.count()
    tab_bar.newTabRequested.emit()
    assert window.count() == initial_count + 1, "New tab not added"
    print(f"✓ New tab added via signal (count: {window.count()})")

    # Test 2: Close button via signal
    print("\nTest 2: Testing close button via signal...")
    close_called = False
    def on_close(index):
        nonlocal close_called
        close_called = True
        print(f"  Close requested for tab {index}")

    window.tabCloseRequested.connect(on_close)
    tab_bar.tabCloseClicked.emit(0)
    assert close_called, "Close signal not emitted"
    print("✓ Close signal works")

    # Test 3: Check close button rect calculation
    print("\nTest 3: Checking close button rect...")
    if tab_bar.count() > 0:
        tab_rect = tab_bar.tabRect(0)
        close_rect = tab_bar._close_button_rect(tab_rect)
        print(f"  Tab rect: {tab_rect}")
        print(f"  Close button rect: {close_rect}")
        # Verify close button is within tab bounds
        assert close_rect.right() <= tab_rect.right(), "Close button outside tab"
        assert close_rect.left() >= tab_rect.left(), "Close button outside tab"
        print("✓ Close button positioned correctly")

    # Test 4: Check new tab button rect
    print("\nTest 4: Checking new tab button rect...")
    new_tab_rect = tab_bar.new_tab_button_rect
    print(f"  New tab button rect: {new_tab_rect}")
    assert new_tab_rect.width() > 0 and new_tab_rect.height() > 0, "Invalid new tab rect"
    print("✓ New tab button rect valid")

    print("\n" + "="*50)
    print("ALL TESTS PASSED!")
    print("="*50)

    return True


if __name__ == "__main__":
    success = test_buttons()
    sys.exit(0 if success else 1)
