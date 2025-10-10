#!/usr/bin/env python3
"""
Debug window dragging with comprehensive logging.

This example demonstrates how ChromeTabbedWindow delegates window dragging
and resizing to FramelessWindowBehavior. All drag/resize logic is now handled
by the shared behavior class from vfwidgets-common.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication, QLabel

from chrome_tabbed_window import ChromeTabbedWindow
from chrome_tabbed_window.view.chrome_tab_bar import ChromeTabBar


class DebugTabBar(ChromeTabBar):
    """Tab bar with debug logging."""

    def mousePressEvent(self, event: QMouseEvent) -> None:
        print("\n[TAB_BAR] mousePressEvent:")
        print(f"  Position: {event.pos()}")
        print(f"  Button: {event.button()}")

        if event.button() == Qt.MouseButton.LeftButton:
            # Check what's at this position
            index = self.tabAt(event.pos())
            print(f"  Tab at position: {index}")

            if self.new_tab_button_rect.contains(event.pos()):
                print("  -> New tab button clicked!")
                self.newTabRequested.emit()
                return

            if index >= 0:
                print(f"  -> Click on tab {index}")
                tab_rect = self.tabRect(index)
                close_rect = self._close_button_rect(tab_rect)
                if close_rect.contains(event.pos()):
                    print("  -> Close button clicked!")
                    self.tabCloseClicked.emit(index)
                    return
                # Start tab drag
                self._drag_start_position = event.pos()
                self._dragged_tab_index = index
                print("  -> Starting tab drag")
            else:
                print("  -> Empty space clicked - IGNORING event for window drag")
                event.ignore()
                return

        print("  -> Calling super().mousePressEvent()")
        super(ChromeTabBar, self).mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        index = self.tabAt(event.pos())
        if index == -1 and event.buttons() == Qt.MouseButton.LeftButton:
            print("[TAB_BAR] mouseMoveEvent: Empty space drag - IGNORING")
            event.ignore()
            return
        super().mouseMoveEvent(event)


class DebugWindow(ChromeTabbedWindow):
    """Window with debug logging.

    Note: This is a simplified debug window that just adds logging to mouse events.
    It doesn't replace the tab bar, which would require deep internal changes.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event) -> None:
        print("\n[WINDOW] mousePressEvent:")
        print(f"  Position: {event.pos()}")
        print(f"  Global position: {event.globalPos()}")
        print(f"  Button: {event.button()}")
        print(f"  Window mode: {self._window_mode}")

        if self._window_mode == 1:  # Frameless
            if event.button() == Qt.MouseButton.LeftButton:
                # Check if in tab bar area
                tab_bar_rect = self._tab_bar.rect()
                tab_bar_pos = self._tab_bar.mapTo(self, tab_bar_rect.topLeft())
                tab_bar_global_rect = QRect(tab_bar_pos, tab_bar_rect.size())

                print(f"  Tab bar rect in window: {tab_bar_global_rect}")
                print(f"  Click in tab bar? {tab_bar_global_rect.contains(event.pos())}")

                if tab_bar_global_rect.contains(event.pos()):
                    # Map to tab bar coordinates
                    local_pos = self._tab_bar.mapFrom(self, event.pos())
                    tab_index = self._tab_bar.tabAt(local_pos)
                    print(f"  Tab at local pos {local_pos}: {tab_index}")

                    if tab_index == -1:
                        print("  -> EMPTY TAB BAR - Will be handled by FramelessWindowBehavior")
                    else:
                        print(f"  -> Click on tab {tab_index} - not dragging window")

        # Delegate to FramelessWindowBehavior (via parent implementation)
        print("  -> Calling super().mousePressEvent() (delegates to FramelessWindowBehavior)")
        super().mousePressEvent(event)
        print("  -> Returned from super().mousePressEvent()")

    def mouseMoveEvent(self, event) -> None:
        # Don't log every move event - too noisy, just delegate
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        print("[WINDOW] mouseReleaseEvent: Delegating to FramelessWindowBehavior")
        super().mouseReleaseEvent(event)


def main():
    app = QApplication(sys.argv)

    # Create debug window
    window = DebugWindow()  # No parent = frameless
    window.setWindowTitle("Debug Dragging")
    window.resize(800, 600)

    # Add tabs
    for i in range(3):
        label = QLabel(f"<h2>Tab {i+1}</h2><p>Watch console for debug output</p>")
        label.setAlignment(Qt.AlignCenter)
        window.addTab(label, f"Tab {i+1}")

    print("=" * 80)
    print("DEBUG WINDOW DRAGGING")
    print("=" * 80)
    print("\nThis will log EVERY event in the chain:")
    print("1. Tab bar receives mouse press")
    print("2. Tab bar decides to handle or ignore")
    print("3. Window receives event (if propagated)")
    print("4. Window sets drag position")
    print("5. Mouse move events trigger window movement")
    print("\nTry clicking on:")
    print("- A tab (should not drag)")
    print("- Empty tab bar space (SHOULD drag)")
    print("- Window edges (should resize)")
    print("=" * 80)

    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
