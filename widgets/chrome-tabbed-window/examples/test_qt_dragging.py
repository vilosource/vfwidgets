#!/usr/bin/env python3
"""
Test Qt's native window dragging capabilities.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6 import __version__ as pyside_version
from PySide6.QtCore import __version__ as qt_version
from PySide6.QtWidgets import QApplication, QLabel

from chrome_tabbed_window import ChromeTabbedWindow


def main():
    app = QApplication(sys.argv)

    print("=" * 60)
    print("QT DRAGGING CAPABILITY TEST")
    print("=" * 60)
    print(f"PySide6 version: {pyside_version}")
    print(f"Qt version: {qt_version}")

    # Create frameless window
    window = ChromeTabbedWindow()
    window.setWindowTitle("Qt Dragging Test")
    window.resize(800, 600)

    # Add tabs
    for i in range(3):
        label = QLabel(f"Tab {i+1}")
        window.addTab(label, f"Tab {i+1}")

    window.show()
    app.processEvents()

    # Check window handle
    print(f"\nWindow handle: {window.windowHandle()}")

    # Check for startSystemMove
    if hasattr(window.windowHandle(), 'startSystemMove'):
        print("✓ startSystemMove() is available")
    else:
        print("✗ startSystemMove() is NOT available")

    # Check for startSystemResize
    if hasattr(window.windowHandle(), 'startSystemResize'):
        print("✓ startSystemResize() is available")
    else:
        print("✗ startSystemResize() is NOT available")

    print("\nTesting manual window movement...")
    initial_pos = window.pos()
    print(f"Initial position: {initial_pos}")

    # Try to move window manually
    from PySide6.QtCore import QPoint
    new_pos = QPoint(initial_pos.x() + 100, initial_pos.y() + 100)
    window.move(new_pos)
    app.processEvents()

    actual_pos = window.pos()
    print(f"After move() to {new_pos}: actual position is {actual_pos}")

    if actual_pos == new_pos:
        print("✓ Manual window.move() works!")
    else:
        print("✗ Manual window.move() FAILED")
        print(f"  Expected: {new_pos}")
        print(f"  Got: {actual_pos}")

    # Move back
    window.move(initial_pos)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    if hasattr(window.windowHandle(), 'startSystemMove'):
        print("This system supports native window dragging (Qt 5.15+)")
        print("Using startSystemMove() should work for dragging.")
    else:
        print("This system does NOT support native window dragging.")
        print("Need to use manual dragging with window.move()")

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
