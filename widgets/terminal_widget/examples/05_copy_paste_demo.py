#!/usr/bin/env python3
"""Copy-Paste Demo - Demonstrates clipboard integration features.

This example shows:
1. Auto-copy on selection (X11-style PRIMARY selection)
2. Middle-click paste
3. Right-click context menu (Copy/Paste)
4. Keyboard shortcuts (Ctrl+Shift+C/V handled by Qt)

Features demonstrated:
- set_auto_copy_on_selection() - Enable/disable auto-copy
- set_middle_click_paste() - Enable/disable middle-click paste
- Right-click context menu with Copy/Paste actions
"""

import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QHBoxLayout,
    QLabel,
)

from vfwidgets_terminal import TerminalWidget


class CopyPasteDemo(QMainWindow):
    """Demo window showing copy-paste features."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Terminal Copy-Paste Demo")
        self.resize(900, 600)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Info label
        info = QLabel(
            "<b>Copy-Paste Features Demo</b><br>"
            "• Select text → Auto-copy to clipboard (if enabled)<br>"
            "• Middle-click → Paste from clipboard<br>"
            "• Right-click → Context menu (Copy/Paste)<br>"
            "• Ctrl+Shift+C → Copy selection<br>"
            "• Ctrl+Shift+V → Paste from clipboard"
        )
        info.setStyleSheet(
            "padding: 10px; background: #2d2d2d; color: #d4d4d4; border-radius: 5px;"
        )
        layout.addWidget(info)

        # Control buttons
        controls = QHBoxLayout()
        layout.addLayout(controls)

        # Auto-copy toggle
        self.auto_copy_btn = QPushButton("Enable Auto-Copy")
        self.auto_copy_btn.setCheckable(True)
        self.auto_copy_btn.setChecked(False)
        self.auto_copy_btn.clicked.connect(self._toggle_auto_copy)
        controls.addWidget(self.auto_copy_btn)

        # Middle-click paste toggle
        self.middle_click_btn = QPushButton("Disable Middle-Click Paste")
        self.middle_click_btn.setCheckable(True)
        self.middle_click_btn.setChecked(True)
        self.middle_click_btn.clicked.connect(self._toggle_middle_click)
        controls.addWidget(self.middle_click_btn)

        controls.addStretch()

        # Terminal widget with copy-paste features
        self.terminal = TerminalWidget(
            command="bash",
            debug=True,  # Enable debug logging to see copy-paste events
        )

        # Configure copy-paste features
        self.terminal.set_auto_copy_on_selection(
            False
        )  # Off by default, user can enable
        self.terminal.set_middle_click_paste(True)  # On by default

        layout.addWidget(self.terminal)

        # Connect to selection changed signal to show feedback
        self.terminal.selectionChanged.connect(self._on_selection_changed)

    def _toggle_auto_copy(self, checked: bool):
        """Toggle auto-copy on selection."""
        self.terminal.set_auto_copy_on_selection(checked)
        self.auto_copy_btn.setText(
            "Disable Auto-Copy" if checked else "Enable Auto-Copy"
        )
        print(f"Auto-copy on selection: {'enabled' if checked else 'disabled'}")

    def _toggle_middle_click(self, checked: bool):
        """Toggle middle-click paste."""
        self.terminal.set_middle_click_paste(checked)
        self.middle_click_btn.setText(
            "Disable Middle-Click Paste" if checked else "Enable Middle-Click Paste"
        )
        print(f"Middle-click paste: {'enabled' if checked else 'disabled'}")

    def _on_selection_changed(self, text: str):
        """Show feedback when text is selected."""
        if text:
            print(
                f"Selected {len(text)} characters: '{text[:50]}{'...' if len(text) > 50 else ''}'"
            )

    def closeEvent(self, event):
        """Clean up on close."""
        self.terminal.close_terminal()
        super().closeEvent(event)


def main():
    """Run the demo."""
    app = QApplication(sys.argv)

    # Create demo window
    demo = CopyPasteDemo()
    demo.show()

    print("\n" + "=" * 70)
    print("COPY-PASTE DEMO")
    print("=" * 70)
    print("Try these actions in the terminal:")
    print("1. Select some text (observe auto-copy when enabled)")
    print("2. Middle-click to paste")
    print("3. Right-click to open context menu")
    print("4. Use Ctrl+Shift+C to copy, Ctrl+Shift+V to paste")
    print("=" * 70 + "\n")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
