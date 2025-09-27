#!/usr/bin/env python3
"""Test case for simple widgets (buttons, labels) focus functionality."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget
from vfwidgets_multisplit import MultisplitWidget
from vfwidgets_multisplit.core.logger import setup_logging
from vfwidgets_multisplit.core.types import WherePosition
from vfwidgets_multisplit.view.container import WidgetProvider

# Setup logging
setup_logging(level="INFO", detailed=True)


class SimpleWidgetProvider(WidgetProvider):
    """Provider for simple widgets (buttons, labels)."""

    def __init__(self):
        self.counter = 0

    def provide_widget(self, widget_id, pane_id):
        """Create simple widgets for testing."""
        self.counter += 1
        widget_type = str(widget_id).split("-")[0]

        if widget_type == "button":
            # Simple button
            button = QPushButton(f"Button {self.counter}")
            button.setStyleSheet("""
                QPushButton {
                    background-color: #4a90e2;
                    color: white;
                    border: 2px solid #357abd;
                    padding: 10px;
                    font-size: 14px;
                }
                QPushButton:focus {
                    border-color: #ff6b6b;
                    border-width: 3px;
                }
            """)
            button.clicked.connect(lambda: print(f"Button clicked: {widget_id}"))
            return button

        elif widget_type == "label":
            # Simple label with click handling
            label = QLabel(f"Label {self.counter}")
            label.setStyleSheet("""
                QLabel {
                    background-color: #f39c12;
                    color: white;
                    border: 2px solid #e67e22;
                    padding: 10px;
                    font-size: 14px;
                }
                QLabel:hover {
                    background-color: #e67e22;
                }
            """)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            return label

        elif widget_type == "container":
            # Container with multiple widgets
            container = QWidget()
            layout = QVBoxLayout(container)

            label = QLabel(f"Container {self.counter}")
            label.setStyleSheet("font-weight: bold; margin: 5px;")

            button1 = QPushButton("Action 1")
            button2 = QPushButton("Action 2")

            button1.clicked.connect(lambda: print(f"Action 1 in {widget_id}"))
            button2.clicked.connect(lambda: print(f"Action 2 in {widget_id}"))

            layout.addWidget(label)
            layout.addWidget(button1)
            layout.addWidget(button2)

            container.setStyleSheet("""
                QWidget {
                    background-color: #9b59b6;
                    border: 2px solid #8e44ad;
                    border-radius: 5px;
                }
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: 1px solid #2980b9;
                    padding: 5px;
                    margin: 2px;
                }
            """)

            return container

        else:
            # Fallback: simple label
            return QLabel(f"Widget {self.counter}")


def test_focus_tracking():
    """Test focus tracking with simple widgets."""
    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("Simple Widget Focus Test")
    window.setGeometry(100, 100, 800, 600)

    # Create provider and multisplit
    provider = SimpleWidgetProvider()
    multisplit = MultisplitWidget(provider=provider)
    window.setCentralWidget(multisplit)

    # Track focus changes
    focus_log = []

    def on_focus_changed(pane_id):
        focus_log.append(pane_id)
        print(f"📍 FOCUS CHANGED TO: {pane_id}")

    multisplit.pane_focused.connect(on_focus_changed)

    # Setup test layout
    print("\n" + "=" * 60)
    print("SIMPLE WIDGET FOCUS TEST")
    print("=" * 60)

    # Initialize with button
    multisplit.initialize_empty("button-main")

    # Add more widgets
    panes = multisplit.get_pane_ids()
    if panes:
        main_pane = panes[0]

        # Split with label
        multisplit.split_pane(main_pane, "label-side", WherePosition.RIGHT, 0.5)

        # Split with container
        multisplit.split_pane(main_pane, "container-bottom", WherePosition.BOTTOM, 0.6)

    print(f"\nCreated layout with {len(multisplit.get_pane_ids())} panes")
    print("Expected behavior:")
    print("1. Click on any widget (button, label, container)")
    print("2. Should see '📍 FOCUS CHANGED TO: pane_xxx' messages")
    print("3. Focus should update for ALL widget types")
    print("=" * 60 + "\n")

    window.show()

    # Run for a short time to test
    from PySide6.QtCore import QTimer

    def test_complete():
        print(f"\nTest completed. Focus changes detected: {len(focus_log)}")
        if focus_log:
            print("✅ Focus tracking is working!")
            for i, pane_id in enumerate(focus_log):
                print(f"  {i+1}. {pane_id}")
        else:
            print("❌ No focus changes detected")

        # Don't exit automatically - let user interact
        print("\nContinue testing manually or close window to exit.")

    # Auto-test after a short delay
    QTimer.singleShot(2000, test_complete)

    return app.exec()


if __name__ == "__main__":
    sys.exit(test_focus_tracking())
