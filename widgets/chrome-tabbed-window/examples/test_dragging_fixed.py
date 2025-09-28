#!/usr/bin/env python3
"""
Test window dragging functionality after fix.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel

from chrome_tabbed_window import ChromeTabbedWindow


def main():
    app = QApplication(sys.argv)

    # Create frameless window
    window = ChromeTabbedWindow()  # No parent = frameless mode
    window.setWindowTitle("Drag Test - FIXED")
    window.resize(800, 600)

    # Add a few tabs
    for i in range(3):
        label = QLabel(f"""
            <h2>Tab {i+1}</h2>
            <p><b>Window Dragging Test - After Fix</b></p>
            <ul>
                <li>Click and drag on EMPTY tab bar area to move window</li>
                <li>Hover near edges to see resize cursor</li>
                <li>Drag edges to resize window</li>
            </ul>
        """)
        label.setAlignment(Qt.AlignCenter)
        window.addTab(label, f"Tab {i+1}")

    print("=" * 60)
    print("WINDOW DRAGGING TEST - FIXED VERSION")
    print("=" * 60)
    print("\nThe fix includes:")
    print("✓ Tab bar ignores mouse events on empty space")
    print("✓ Events propagate to parent window for dragging")
    print("\nInstructions:")
    print("1. Click and drag on EMPTY tab bar area → Window should move")
    print("2. Hover near window edges → Resize cursor should appear")
    print("3. Drag window edges → Window should resize")
    print("\nWindow info:")
    print(f"- Window mode: {window._window_mode} (1 = Frameless)")
    print(f"- Tab count: {window.count()}")
    print("=" * 60)

    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
