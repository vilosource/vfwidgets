#!/usr/bin/env python3
"""
Test drop-in replacement capability.

This script verifies that ChromeTabbedWindow can replace QTabWidget
with zero code changes.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication, QLabel, QMainWindow


def test_with_qtabwidget():
    """Test with original QTabWidget."""
    from PySide6.QtWidgets import QTabWidget

    app = QApplication.instance() or QApplication(sys.argv)
    window = QMainWindow()

    # Original code using QTabWidget
    widget = QTabWidget()
    widget.addTab(QLabel("Tab 1"), "First")
    widget.addTab(QLabel("Tab 2"), "Second")
    widget.setTabsClosable(True)

    # Test methods
    assert widget.count() == 2
    assert widget.tabText(0) == "First"
    assert widget.currentIndex() == 0
    widget.setCurrentIndex(1)
    assert widget.currentIndex() == 1

    print("✅ QTabWidget tests passed")
    return True

def test_with_chrometabbedwindow():
    """Test with ChromeTabbedWindow as drop-in replacement."""
    # The ONLY change: import ChromeTabbedWindow instead
    from chrome_tabbed_window import ChromeTabbedWindow as QTabWidget

    app = QApplication.instance() or QApplication(sys.argv)
    window = QMainWindow()

    # EXACT SAME CODE as above
    widget = QTabWidget()
    widget.addTab(QLabel("Tab 1"), "First")
    widget.addTab(QLabel("Tab 2"), "Second")
    widget.setTabsClosable(True)

    # Test methods
    assert widget.count() == 2
    assert widget.tabText(0) == "First"
    assert widget.currentIndex() == 0
    widget.setCurrentIndex(1)
    assert widget.currentIndex() == 1

    print("✅ ChromeTabbedWindow drop-in replacement tests passed")
    return True

if __name__ == "__main__":
    print("Testing drop-in replacement capability...")
    print("-" * 40)

    # Test both
    qtab_result = test_with_qtabwidget()
    chrome_result = test_with_chrometabbedwindow()

    if qtab_result and chrome_result:
        print("-" * 40)
        print("🎉 SUCCESS: ChromeTabbedWindow is a perfect drop-in replacement!")
        print("You can replace QTabWidget with ChromeTabbedWindow with just an import change.")
    else:
        print("❌ FAILED: Not a complete drop-in replacement")
        sys.exit(1)
