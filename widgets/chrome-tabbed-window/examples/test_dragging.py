#!/usr/bin/env python3
"""
Test window dragging functionality.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel

from chrome_tabbed_window import ChromeTabbedWindow


class TestWindow(ChromeTabbedWindow):
    """Test window with debug output."""

    def mousePressEvent(self, event):
        print(f"mousePressEvent at {event.pos()}, button: {event.button()}")
        print(f"  Window mode: {self._window_mode}")

        if self._window_mode == 1:  # Frameless
            # Check if we're in tab bar area
            tab_bar_rect = self._tab_bar.rect()
            tab_bar_pos = self._tab_bar.mapTo(self, tab_bar_rect.topLeft())
            tab_bar_global_rect = QRect(tab_bar_pos, tab_bar_rect.size())

            print(f"  Tab bar rect: {tab_bar_global_rect}")
            print(f"  Contains click: {tab_bar_global_rect.contains(event.pos())}")

            if tab_bar_global_rect.contains(event.pos()):
                local_pos = self._tab_bar.mapFrom(self, event.pos())
                tab_index = self._tab_bar.tabAt(local_pos)
                print(f"  Tab at position: {tab_index}")

                if tab_index == -1:
                    print("  Setting drag position!")
                    self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
                    event.accept()
                    return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if hasattr(self, '_drag_pos'):
            print(f"mouseMoveEvent - dragging! Moving to {event.globalPos() - self._drag_pos}")
        super().mouseMoveEvent(event)


def main():
    app = QApplication(sys.argv)

    # Create test window
    window = TestWindow()
    window.setWindowTitle("Drag Test - Try dragging the tab bar")
    window.resize(800, 600)

    # Add a few tabs
    for i in range(3):
        label = QLabel(f"<h2>Tab {i+1}</h2><p>Try dragging the empty tab bar area</p>")
        label.setAlignment(Qt.AlignCenter)
        window.addTab(label, f"Tab {i+1}")

    print("=" * 60)
    print("WINDOW DRAGGING TEST")
    print("=" * 60)
    print("\nInstructions:")
    print("1. Click and drag on the EMPTY tab bar area (not on tabs)")
    print("2. Watch console for debug output")
    print("3. The window should move when dragging")
    print("\nWindow info:")
    print(f"- Window mode: {window._window_mode}")
    print(f"- Tab count: {window.count()}")
    print("=" * 60)

    window.show()
    return app.exec()


if __name__ == "__main__":
    # Import QRect after Qt app is created
    from PySide6.QtCore import QRect
    sys.exit(main())
