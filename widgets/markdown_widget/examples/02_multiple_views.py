"""Demo: Multiple Views with Dual Pattern Approach

This demo showcases the dual pattern approach:
- Python Observer Pattern: Model → Views (model changes update all views)
- Qt Signals/Slots: View ↔ View (UI coordination between views)

The demo shows:
1. One MarkdownDocument (pure Python model)
2. Two MarkdownTextEditors + One MarkdownTocView
3. Python Observer: Edit in either editor → all views update via model
4. Qt Signals: TOC heading click → editor scrolls (view-to-view coordination)
"""

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QSplitter, QVBoxLayout, QWidget

from vfwidgets_markdown.models import MarkdownDocument
from vfwidgets_markdown.widgets import MarkdownTextEditor, MarkdownTocView


def print_architecture():
    """Print the architecture diagram."""
    print("\n" + "=" * 70)
    print("DUAL PATTERN ARCHITECTURE")
    print("=" * 70)
    print(
        """
    ┌─────────────────────────────────────────────────────────────┐
    │                    MarkdownDocument                         │
    │                  (Pure Python Model)                        │
    │                                                             │
    │  - get_text(), set_text(), append_text()                   │
    │  - get_toc()                                                │
    │  - add_observer(), remove_observer()                        │
    │  - _notify_observers()  ← Python Observer Pattern          │
    └─────────────────────────────────────────────────────────────┘
                              ↓ ↓ ↓
            ┌─────────────────┴─┴─┴─────────────────┐
            ↓                   ↓                    ↓
    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
    │   Editor 1   │    │   Editor 2   │    │   TOC View   │
    │              │    │              │    │              │
    │ Observer:    │    │ Observer:    │    │ Observer:    │
    │ - on_document│    │ - on_document│    │ - on_document│
    │   _changed() │    │   _changed() │    │   _changed() │
    │              │    │              │    │              │
    │ Qt Signals:  │    │ Qt Signals:  │    │ Qt Signals:  │
    │ - content_   │    │ - content_   │    │ - heading_   │
    │   modified   │    │   modified   │    │   clicked    │
    │ - cursor_    │    │ - cursor_    │    │ - heading_   │
    │   moved      │    │   moved      │    │   hovered    │
    │              │    │              │    │              │
    │ Qt Slots:    │    │ Qt Slots:    │    │              │
    │ - scroll_to_ │←───┼──────────────┼────│ (clicking    │
    │   heading()  │    │              │    │  emits       │
    └──────────────┘    └──────────────┘    │  signal)     │
                                             └──────────────┘

    Pattern 1: Python Observer (Model → Views)
    ─────────────────────────────────────────
    User types in Editor 1
    → Editor 1 calls document.set_text()
    → Model calls _notify_observers()
    → All observers get on_document_changed() callback
    → Editor 1, Editor 2, and TOC View all update

    Pattern 2: Qt Signals/Slots (View ↔ View)
    ──────────────────────────────────────────
    User clicks heading in TOC
    → TOC emits heading_clicked(heading_id) signal
    → Connected to Editor 1's scroll_to_heading() slot
    → Editor 1 scrolls to that heading
    """
    )
    print("=" * 70 + "\n")


class DemoWindow(QWidget):
    """Demo window showing multiple views observing one model."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Markdown Widget - Dual Pattern Demo")
        self.resize(1200, 800)

        # Create the model (pure Python, no Qt)
        initial_content = """# Dual Pattern Architecture Demo

This demo showcases two patterns working together:

## Python Observer Pattern

Edit this text in either editor, and watch how:
- Both editors stay synchronized
- The Table of Contents updates automatically
- All updates happen via the model's observer pattern

## Qt Signals and Slots

Try clicking headings in the TOC:
- The TOC emits a Qt signal: `heading_clicked`
- The editors receive it via Qt slot: `scroll_to_heading()`
- This is pure Qt view-to-view coordination

## Why Both Patterns?

### Python Observer (Model → Views)
- Model stays pure Python (testable without Qt)
- Views react to model changes
- Automatic synchronization across all views

### Qt Signals/Slots (View ↔ View)
- Native Qt mechanism for UI coordination
- Type-safe, automatic cleanup
- Perfect for view-to-view communication

## Try It Yourself

1. **Type in either editor** - see Python observer pattern in action
2. **Click a heading in TOC** - see Qt signals/slots in action
3. **Watch the console** - see which pattern is being used
"""
        print("[MODEL] Creating MarkdownDocument with initial content")
        self.document = MarkdownDocument(initial_content)

        # Create the UI
        self._setup_ui()

        # Connect the signals (Qt signals/slots pattern)
        self._connect_signals()

        print("[SETUP] All views are now observing the model")
        print("[SETUP] Qt signals connected for view-to-view coordination")
        print("\n[INFO] Try editing text or clicking TOC headings!\n")

    def _setup_ui(self):
        """Create the UI layout with multiple views."""
        layout = QHBoxLayout(self)

        # Left side: TOC
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        toc_label = QLabel("Table of Contents")
        toc_label.setStyleSheet("font-weight: bold; padding: 5px;")
        left_layout.addWidget(toc_label)

        print("[VIEW] Creating MarkdownTocView (adds itself as observer)")
        self.toc_view = MarkdownTocView(self.document)
        left_layout.addWidget(self.toc_view)

        # Right side: Two editors in vertical split
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Vertical)

        # Editor 1
        editor1_container = QWidget()
        editor1_layout = QVBoxLayout(editor1_container)
        editor1_layout.setContentsMargins(0, 0, 0, 0)

        editor1_label = QLabel("Editor 1")
        editor1_label.setStyleSheet("font-weight: bold; padding: 5px;")
        editor1_layout.addWidget(editor1_label)

        print("[VIEW] Creating MarkdownTextEditor #1 (adds itself as observer)")
        self.editor1 = MarkdownTextEditor(self.document)
        editor1_layout.addWidget(self.editor1)
        splitter.addWidget(editor1_container)

        # Editor 2
        editor2_container = QWidget()
        editor2_layout = QVBoxLayout(editor2_container)
        editor2_layout.setContentsMargins(0, 0, 0, 0)

        editor2_label = QLabel("Editor 2")
        editor2_label.setStyleSheet("font-weight: bold; padding: 5px;")
        editor2_layout.addWidget(editor2_label)

        print("[VIEW] Creating MarkdownTextEditor #2 (adds itself as observer)")
        self.editor2 = MarkdownTextEditor(self.document)
        editor2_layout.addWidget(self.editor2)
        splitter.addWidget(editor2_container)

        right_layout.addWidget(splitter)

        # Add panels to main layout
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setStretchFactor(0, 1)  # TOC
        main_splitter.setStretchFactor(1, 3)  # Editors

        layout.addWidget(main_splitter)

    def _connect_signals(self):
        """Connect Qt signals between views (View ↔ View coordination)."""
        print("[SIGNALS] Connecting Qt signals for view-to-view coordination...")

        # Pattern 2: Qt Signals/Slots (View → View)
        # When TOC heading is clicked, scroll both editors
        self.toc_view.heading_clicked.connect(self.editor1.scroll_to_heading)
        self.toc_view.heading_clicked.connect(self.editor2.scroll_to_heading)
        print("[SIGNALS] - TOC heading_clicked → Editor 1 scroll_to_heading()")
        print("[SIGNALS] - TOC heading_clicked → Editor 2 scroll_to_heading()")

        # Monitor content changes to show pattern usage
        self.editor1.content_modified.connect(
            lambda: print("[QT SIGNAL] Editor 1 content_modified signal emitted")
        )
        self.editor2.content_modified.connect(
            lambda: print("[QT SIGNAL] Editor 2 content_modified signal emitted")
        )
        print("[SIGNALS] - Editor 1 content_modified → console logger")
        print("[SIGNALS] - Editor 2 content_modified → console logger")

        # Monitor cursor movements (optional - demonstrates signal with parameters)
        self.editor1.cursor_moved.connect(
            lambda line, col: print(f"[QT SIGNAL] Editor 1 cursor at line {line}, column {col}")
        )
        print("[SIGNALS] - Editor 1 cursor_moved(line, col) → console logger")

        # Monitor TOC clicks
        self.toc_view.heading_clicked.connect(
            lambda heading_id: print(
                f"[QT SIGNAL] TOC heading_clicked: '{heading_id}' (triggering editor scrolls)"
            )
        )
        print("[SIGNALS] - TOC heading_clicked → console logger")


def main():
    """Run the demo."""
    print_architecture()

    app = QApplication(sys.argv)
    window = DemoWindow()
    window.show()

    print("\n" + "=" * 70)
    print("DEMO RUNNING")
    print("=" * 70)
    print("Actions you can try:")
    print("1. Edit text in Editor 1 → Watch Editor 2 and TOC update (Observer Pattern)")
    print("2. Edit text in Editor 2 → Watch Editor 1 and TOC update (Observer Pattern)")
    print("3. Click a heading in TOC → Watch editors scroll (Qt Signals)")
    print("4. Watch console to see which pattern is being used")
    print("=" * 70 + "\n")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
