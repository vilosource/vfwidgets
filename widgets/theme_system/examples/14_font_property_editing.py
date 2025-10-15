#!/usr/bin/env python3
"""Example 14: Font Property Editing (Phase 4).

This example demonstrates Phase 4 of the font support implementation:
editing individual font properties (size, weight, line height, letter spacing).

Features demonstrated:
1. FontPropertyEditorWidget for token-based property editing
2. Property-specific controls (spinbox, combo, double spinbox)
3. Validation feedback with error messages
4. Real-time signal emission on property changes
5. Integration with theme system

Based on: widgets/theme_system/docs/fonts-theme-studio-integration-PLAN.md
Phase 4 - Basic Font Property Editing
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Add src to path for development
src_path = Path(__file__).parent.parent / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))

from vfwidgets_theme import ThemedWidget
from vfwidgets_theme.core.theme import Theme
from vfwidgets_theme.widgets.font_property_editor import FontPropertyEditorWidget


class FontPropertyEditingDemo(ThemedWidget, QMainWindow):
    """Demo window showing font property editing."""

    def __init__(self):
        """Initialize demo window."""
        super().__init__()

        self.setWindowTitle("Font Property Editing Demo - Phase 4")
        self.resize(1000, 600)

        # Create test theme with various font properties
        self._test_theme = Theme(
            name="Property Test Theme",
            fonts={
                # Terminal fonts
                "terminal.fontSize": 14,
                "terminal.fontWeight": 400,
                "terminal.lineHeight": 1.4,
                "terminal.letterSpacing": 0.0,
                # Editor fonts
                "editor.fontSize": 13,
                "editor.fontWeight": 400,
                "editor.lineHeight": 1.5,
                # Base properties
                "fonts.size": 12,
                "fonts.weight": 400,
            },
        )

        # Setup UI
        self._setup_ui()

        # Start with terminal.fontSize
        self._select_token("terminal.fontSize")

    def _setup_ui(self) -> None:
        """Set up user interface."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        # Left: Token selector
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        left_layout.addWidget(QLabel("<b>Select Token to Edit:</b>"))

        # Token buttons
        self._token_buttons = {}
        token_list = [
            ("terminal.fontSize", "Terminal Font Size (14pt)"),
            ("terminal.fontWeight", "Terminal Font Weight (400)"),
            ("terminal.lineHeight", "Terminal Line Height (1.4×)"),
            ("terminal.letterSpacing", "Terminal Letter Spacing (0.0px)"),
            ("editor.fontSize", "Editor Font Size (13pt)"),
            ("editor.fontWeight", "Editor Font Weight (400)"),
            ("editor.lineHeight", "Editor Line Height (1.5×)"),
            ("fonts.size", "Default Font Size (12pt)"),
            ("fonts.weight", "Default Font Weight (400)"),
        ]

        for token_path, label_text in token_list:
            btn = QPushButton(label_text)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, t=token_path: self._select_token(t))
            self._token_buttons[token_path] = btn
            left_layout.addWidget(btn)

        left_layout.addStretch()
        layout.addWidget(left_panel)

        # Middle: Property editor
        middle_panel = QWidget()
        middle_layout = QVBoxLayout(middle_panel)

        middle_layout.addWidget(QLabel("<b>Font Property Editor:</b>"))

        self._property_editor = FontPropertyEditorWidget()
        self._property_editor.property_changed.connect(self._on_property_changed)
        middle_layout.addWidget(self._property_editor)

        middle_layout.addStretch()
        layout.addWidget(middle_panel)

        # Right: Event log
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        right_layout.addWidget(QLabel("<b>Change Log:</b>"))

        self._log = QTextEdit()
        self._log.setReadOnly(True)
        right_layout.addWidget(self._log)

        # Clear button
        clear_btn = QPushButton("Clear Log")
        clear_btn.clicked.connect(self._log.clear)
        right_layout.addWidget(clear_btn)

        layout.addWidget(right_panel)

        # Set proportions
        layout.setStretch(0, 2)  # Left: 2
        layout.setStretch(1, 3)  # Middle: 3
        layout.setStretch(2, 3)  # Right: 3

    def _select_token(self, token_path: str) -> None:
        """Select and edit a token.

        Args:
            token_path: Token path to edit

        """
        # Update button states
        for path, btn in self._token_buttons.items():
            btn.setChecked(path == token_path)

        # Get current value
        current_value = self._test_theme.fonts.get(token_path, None)

        # Set token in editor
        self._property_editor.set_token(token_path, current_value, self._test_theme)

        # Log selection
        self._log_event(f"<b>Selected token:</b> {token_path} = {current_value}")

    def _on_property_changed(self, token_path: str, new_value) -> None:
        """Handle property changes.

        Args:
            token_path: Token path that changed
            new_value: New property value

        """
        # Get old value
        old_value = self._test_theme.fonts.get(token_path, None)

        # Update theme
        self._test_theme.fonts[token_path] = new_value

        # Log change
        self._log_event(
            f"<span style='color: #4CAF50;'><b>Property changed:</b></span><br/>"
            f"  Token: {token_path}<br/>"
            f"  Old: {old_value}<br/>"
            f"  New: {new_value}<br/>"
            f"  Type: {type(new_value).__name__}"
        )

        # Update button label to show new value
        if token_path in self._token_buttons:
            btn = self._token_buttons[token_path]
            label_prefix = btn.text().split("(")[0].strip()

            # Format value based on token type
            if "Size" in token_path or token_path == "fonts.size":
                value_str = f"{new_value}pt"
            elif "Weight" in token_path or token_path == "fonts.weight":
                value_str = str(new_value)
            elif "lineHeight" in token_path:
                value_str = f"{new_value}×"
            elif "letterSpacing" in token_path:
                value_str = f"{new_value}px"
            else:
                value_str = str(new_value)

            btn.setText(f"{label_prefix} ({value_str})")

    def _log_event(self, message: str) -> None:
        """Add event to log.

        Args:
            message: Event message (HTML supported)

        """
        self._log.append(message)
        # Scroll to bottom
        self._log.verticalScrollBar().setValue(self._log.verticalScrollBar().maximum())


def main() -> int:
    """Run the demo application.

    Returns:
        Exit code

    """
    app = QApplication(sys.argv)

    window = FontPropertyEditingDemo()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
