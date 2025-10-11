#!/usr/bin/env python3
"""Test case for text editors and complex input widgets focus functionality."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPlainTextEdit,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from vfwidgets_multisplit import MultisplitWidget
from vfwidgets_multisplit.core.logger import setup_logging
from vfwidgets_multisplit.core.types import WherePosition
from vfwidgets_multisplit.view.container import WidgetProvider

# Setup logging
setup_logging(level="INFO", detailed=True)


class EditorWidgetProvider(WidgetProvider):
    """Provider for text editor widgets."""

    def __init__(self):
        self.counter = 0

    def provide_widget(self, widget_id, pane_id):
        """Create text editor widgets for testing."""
        self.counter += 1
        widget_type = str(widget_id).split("-")[0]

        if widget_type == "textedit":
            # Rich text editor
            editor = QTextEdit()
            editor.setPlainText(
                f"Rich Text Editor {self.counter}\n\nClick here and type to test focus tracking.\nThis editor supports:\n- Rich text formatting\n- Multiple lines\n- Copy/paste\n- etc."
            )
            editor.setStyleSheet("""
                QTextEdit {
                    background-color: #2d3748;
                    color: #e2e8f0;
                    border: 2px solid #4a5568;
                    font-family: 'Courier New', monospace;
                    font-size: 12px;
                }
                QTextEdit:focus {
                    border-color: #63b3ed;
                    border-width: 3px;
                }
            """)
            return editor

        elif widget_type == "plaintextedit":
            # Plain text editor
            editor = QPlainTextEdit()
            editor.setPlainText(
                f"Plain Text Editor {self.counter}\n\nThis is a plain text editor.\nType here to test focus events.\n\nFeatures:\n- Plain text only\n- Line numbers possible\n- Fast rendering"
            )
            editor.setStyleSheet("""
                QPlainTextEdit {
                    background-color: #1a202c;
                    color: #f7fafc;
                    border: 2px solid #2d3748;
                    font-family: 'Courier New', monospace;
                    font-size: 12px;
                }
                QPlainTextEdit:focus {
                    border-color: #68d391;
                    border-width: 3px;
                }
            """)
            return editor

        elif widget_type == "lineedit":
            # Single line editor
            editor = QLineEdit()
            editor.setText(f"Single Line Editor {self.counter}")
            editor.setPlaceholder("Type here...")
            editor.setStyleSheet("""
                QLineEdit {
                    background-color: #4a5568;
                    color: #e2e8f0;
                    border: 2px solid #718096;
                    padding: 8px;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border-color: #f6ad55;
                    border-width: 3px;
                }
            """)
            return editor

        elif widget_type == "composite":
            # Composite widget with multiple editors
            container = QWidget()
            layout = QVBoxLayout(container)

            title = QLabel(f"Composite Editor {self.counter}")
            title.setStyleSheet("font-weight: bold; color: #ed8936; margin: 5px;")

            # Add multiple input types
            line_edit = QLineEdit("Single line input")
            line_edit.setPlaceholder("Enter text here...")

            text_edit = QTextEdit()
            text_edit.setPlainText("Multi-line text area\nClick and type here")
            text_edit.setMaximumHeight(100)

            # Style the composite
            container.setStyleSheet("""
                QWidget {
                    background-color: #553c9a;
                    border: 2px solid #7c3aed;
                    border-radius: 5px;
                    padding: 5px;
                }
                QLineEdit, QTextEdit {
                    background-color: #f7fafc;
                    color: #2d3748;
                    border: 1px solid #cbd5e0;
                    margin: 2px;
                }
            """)

            layout.addWidget(title)
            layout.addWidget(line_edit)
            layout.addWidget(text_edit)

            return container

        else:
            # Fallback: simple text edit
            return QTextEdit(f"Fallback Editor {self.counter}")


def test_editor_focus():
    """Test focus tracking with text editors."""
    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("Text Editor Focus Test")
    window.setGeometry(100, 100, 1000, 700)

    # Create provider and multisplit
    provider = EditorWidgetProvider()
    multisplit = MultisplitWidget(provider=provider)
    window.setCentralWidget(multisplit)

    # Track focus changes
    focus_log = []

    def on_focus_changed(pane_id):
        focus_log.append(pane_id)
        print(f"📝 TEXT EDITOR FOCUS: {pane_id}")

    multisplit.pane_focused.connect(on_focus_changed)

    # Setup test layout
    print("\n" + "=" * 60)
    print("TEXT EDITOR FOCUS TEST")
    print("=" * 60)

    # Initialize with rich text editor
    multisplit.initialize_empty("textedit-main")

    # Add more editor types
    panes = multisplit.get_pane_ids()
    if panes:
        main_pane = panes[0]

        # Split with plain text editor
        multisplit.split_pane(main_pane, "plaintextedit-code", WherePosition.RIGHT, 0.5)

        # Split with line editor
        multisplit.split_pane(main_pane, "lineedit-input", WherePosition.BOTTOM, 0.7)

        # Add composite widget
        panes = multisplit.get_pane_ids()
        if len(panes) > 2:
            multisplit.split_pane(panes[-1], "composite-multi", WherePosition.RIGHT, 0.6)

    print(f"\nCreated layout with {len(multisplit.get_pane_ids())} panes")
    print("Expected behavior:")
    print("1. Click inside any text editor")
    print("2. Should see '📝 TEXT EDITOR FOCUS: pane_xxx' messages")
    print("3. Type in editors - should update focus")
    print("4. Tab between fields should update focus")
    print("5. All editor types should work:")
    print("   - QTextEdit (rich text)")
    print("   - QPlainTextEdit (plain text)")
    print("   - QLineEdit (single line)")
    print("   - Composite (multiple inputs)")
    print("=" * 60 + "\n")

    window.show()

    # Auto-test after a delay
    from PySide6.QtCore import QTimer

    def test_status():
        print(f"\nFocus changes detected so far: {len(focus_log)}")
        if focus_log:
            print("✅ Text editor focus tracking is working!")
            for i, pane_id in enumerate(focus_log):
                print(f"  {i + 1}. {pane_id}")
        else:
            print("ℹ️ No focus changes yet - click in different editors to test")

        print("\nContinue typing and clicking in different editors...")

    QTimer.singleShot(3000, test_status)

    return app.exec()


if __name__ == "__main__":
    sys.exit(test_editor_focus())
