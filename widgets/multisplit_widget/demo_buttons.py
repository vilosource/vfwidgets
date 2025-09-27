#!/usr/bin/env python3
"""Simple demo with buttons to test focus functionality."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

# Setup logging
import argparse

from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QStatusBar,
    QToolBar,
    QVBoxLayout,
    QWidget,
)
from vfwidgets_multisplit import MultisplitWidget
from vfwidgets_multisplit.core.logger import logger, setup_logging
from vfwidgets_multisplit.core.types import WherePosition
from vfwidgets_multisplit.view.container import WidgetProvider

parser = argparse.ArgumentParser()
parser.add_argument("--debug", action="store_true", help="Enable debug logging")
args = parser.parse_args()

if args.debug:
    setup_logging(level="DEBUG", detailed=True)
else:
    setup_logging(level="INFO", detailed=False)


class ButtonProvider(WidgetProvider):
    """Provides simple button widgets for testing."""

    def __init__(self):
        self.counter = 0

    def provide_widget(self, widget_id, pane_id):
        """Create a button widget."""
        self.counter += 1

        # Create a container with button
        container = QWidget()
        layout = QVBoxLayout(container)

        # Info label
        info_label = QLabel(f"Pane: {str(pane_id)[:8]}...")
        info_label.setStyleSheet("font-size: 10px; color: #666;")

        # Main button
        button = QPushButton(str(widget_id))
        button.setStyleSheet("""
            QPushButton {
                background-color: #4a4a4a;
                color: white;
                border: 2px solid #666;
                padding: 20px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
                border-color: #888;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
            }
            QPushButton:focus {
                border-color: #4CAF50;
                border-width: 3px;
            }
        """)

        # Click handler
        button.clicked.connect(lambda: print(f"Button clicked: {widget_id} in pane {pane_id}"))

        layout.addWidget(info_label)
        layout.addWidget(button, 1)

        logger.info(f"Created button widget: {widget_id} for pane {pane_id}")
        return container


class ButtonDemoWindow(QMainWindow):
    """Demo window with button widgets."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("MultiSplit Button Demo - Focus Test")
        self.setGeometry(100, 100, 1200, 800)

        # Dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QToolBar {
                background-color: #3c3f41;
                border-bottom: 1px solid #555;
                padding: 5px;
            }
            QToolBar QToolButton {
                background-color: #3c3f41;
                color: #a9b7c6;
                border: 1px solid #555;
                padding: 5px 10px;
                margin: 2px;
            }
            QToolBar QToolButton:hover {
                background-color: #4a4a4a;
                border-color: #6a6a6a;
            }
            QStatusBar {
                background-color: #3c3f41;
                color: #a9b7c6;
            }
        """)

        # Create provider
        self.provider = ButtonProvider()

        # Create MultiSplit widget
        self.multisplit = MultisplitWidget(provider=self.provider)
        self.setCentralWidget(self.multisplit)

        # Setup UI
        self.setup_toolbar()
        self.setup_statusbar()

        # Initialize with simple layout
        self.setup_initial_layout()

        # Connect focus signal
        self.multisplit.pane_focused.connect(self.on_pane_focused)

    def setup_initial_layout(self):
        """Create initial button layout."""
        # Start with main button
        self.multisplit.initialize_empty("Button-Main")

        panes = self.multisplit.get_pane_ids()
        if panes:
            main_pane = panes[0]

            # Add left button
            self.multisplit.split_pane(main_pane, "Button-Left", WherePosition.LEFT, 0.25)

            # Add bottom button
            self.multisplit.split_pane(main_pane, "Button-Bottom", WherePosition.BOTTOM, 0.7)

            # Add right button to bottom
            panes = self.multisplit.get_pane_ids()
            if len(panes) > 2:
                bottom_pane = panes[-1]
                self.multisplit.split_pane(bottom_pane, "Button-Right", WherePosition.RIGHT, 0.5)

        logger.info(f"Initial layout created with {len(self.multisplit.get_pane_ids())} panes")

    def setup_toolbar(self):
        """Setup toolbar with split actions."""
        toolbar = QToolBar("Main")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Split actions
        split_h = QAction("⬌ Split H", self)
        split_h.setToolTip("Split focused pane horizontally")
        split_h.triggered.connect(lambda: self.split_focused(WherePosition.RIGHT))
        toolbar.addAction(split_h)

        split_v = QAction("⬍ Split V", self)
        split_v.setToolTip("Split focused pane vertically")
        split_v.triggered.connect(lambda: self.split_focused(WherePosition.BOTTOM))
        toolbar.addAction(split_v)

        toolbar.addSeparator()

        # Remove action
        remove = QAction("✕ Remove", self)
        remove.setToolTip("Remove focused pane")
        remove.triggered.connect(self.remove_focused)
        toolbar.addAction(remove)

        toolbar.addSeparator()

        # Test focus
        test = QAction("? Test Focus", self)
        test.setToolTip("Show which pane is focused")
        test.triggered.connect(self.test_focus)
        toolbar.addAction(test)

    def setup_statusbar(self):
        """Setup status bar."""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Click on different panes to change focus")

    def split_focused(self, position):
        """Split the focused pane."""
        focused = self.multisplit.get_focused_pane()

        if not focused:
            # Try to get first pane
            panes = self.multisplit.get_pane_ids()
            if panes:
                focused = panes[0]
                self.statusbar.showMessage("No focus - using first pane", 2000)

        if focused:
            widget_id = f"Button-{self.provider.counter + 1}"
            success = self.multisplit.split_pane(focused, widget_id, position, 0.5)

            if success:
                logger.info(f"Split {focused} with {widget_id}")
                self.statusbar.showMessage(f"Split {focused[:8]}... → {widget_id}", 3000)
            else:
                self.statusbar.showMessage("Split failed", 2000)
        else:
            self.statusbar.showMessage("No pane to split", 2000)

    def remove_focused(self):
        """Remove focused pane."""
        focused = self.multisplit.get_focused_pane()

        if focused:
            success = self.multisplit.remove_pane(focused)
            if success:
                self.statusbar.showMessage(f"Removed {focused[:8]}...", 3000)
            else:
                self.statusbar.showMessage("Cannot remove - last pane?", 2000)
        else:
            self.statusbar.showMessage("No pane focused", 2000)

    def test_focus(self):
        """Test which pane is focused."""
        focused = self.multisplit.get_focused_pane()

        if focused:
            self.statusbar.showMessage(f"Focused: {focused}", 5000)
            logger.info(f"Currently focused: {focused}")
        else:
            self.statusbar.showMessage("No pane is focused", 3000)
            logger.warning("No pane is focused")

    def on_pane_focused(self, pane_id):
        """Handle focus change."""
        logger.info(f"FOCUS CHANGED TO: {pane_id}")
        self.statusbar.showMessage(f"Focus → {pane_id[:16]}...", 2000)


def main():
    app = QApplication(sys.argv)

    print("\n" + "=" * 60)
    print("MULTISPLIT BUTTON DEMO")
    print("=" * 60)
    print("\nThis demo uses simple buttons instead of complex widgets.")
    print("Click on different panes - you should see focus messages.")
    print("\nExpected behavior:")
    print("1. Click on a button/pane")
    print("2. Status bar shows 'Focus → pane_xxx...'")
    print("3. Split H/V should split the FOCUSED pane")
    print("4. Not always the same pane!")
    print("=" * 60 + "\n")

    window = ButtonDemoWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
