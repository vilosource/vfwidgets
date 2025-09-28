#!/usr/bin/env python3
"""
Debug window dragging with comprehensive logging.
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
    """Window with debug logging."""

    def __init__(self, parent=None):
        super().__init__(parent)
        # Replace tab bar with debug version
        old_bar = self._tab_bar
        self._tab_bar = DebugTabBar(self)
        self._tab_bar.set_model(self._model)

        # Copy settings
        self._tab_bar.setTabsClosable(old_bar.tabsClosable())

        # Reconnect signals
        self._tab_bar.currentChanged.connect(self._on_current_changed)
        self._tab_bar.tabMoved.connect(self._on_tab_moved)
        self._tab_bar.tabBarClicked.connect(self._on_tab_bar_clicked)
        self._tab_bar.tabBarDoubleClicked.connect(self._on_tab_bar_double_clicked)
        self._tab_bar.tabCloseClicked.connect(self._on_tab_close_requested)
        self._tab_bar.newTabRequested.connect(self._on_new_tab_requested)

        # Replace in layout
        self._main_layout.replaceWidget(old_bar, self._tab_bar)
        old_bar.deleteLater()

    def mousePressEvent(self, event) -> None:
        print("\n[WINDOW] mousePressEvent:")
        print(f"  Position: {event.pos()}")
        print(f"  Global position: {event.globalPos()}")
        print(f"  Button: {event.button()}")
        print(f"  Window mode: {self._window_mode}")

        if self._window_mode == 1:  # Frameless
            if event.button() == Qt.MouseButton.LeftButton:
                # Check for edge resize
                edges = self._get_resize_edge(event.pos())
                print(f"  Edges detected: {edges}")

                if edges:
                    print("  -> Starting resize")
                    self._resize_edge = edges
                    self._start_system_resize(edges)
                    event.accept()
                    return

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
                        print("  -> EMPTY TAB BAR - Setting drag position!")
                        self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
                        print(f"  -> Drag position set to: {self._drag_pos}")
                        event.accept()
                        return
                    else:
                        print(f"  -> Click on tab {tab_index} - not dragging window")

        print("  -> Calling super().mousePressEvent()")
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if hasattr(self, '_drag_pos'):
            new_pos = event.globalPos() - self._drag_pos
            print(f"[WINDOW] mouseMoveEvent: DRAGGING to {new_pos}")
            self.move(new_pos)
            event.accept()
            return

        # Don't log every move event - too noisy
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if hasattr(self, '_drag_pos'):
            print("[WINDOW] mouseReleaseEvent: Stopping drag")
            del self._drag_pos
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
