#!/usr/bin/env python3
"""Example 15: Font Family List Editing (Phase 5).

This example demonstrates Phase 5 of the font support implementation:
editing font family lists with drag-drop reordering and system font availability.

Features demonstrated:
1. FontFamilyListEditor for editing font family fallback chains
2. Drag-drop reordering of font families
3. Add fonts via system font picker dialog
4. Remove fonts with validation (can't remove last generic family)
5. Font availability indicators (checkmarks/X icons)
6. Real-time signal emission on family list changes
7. Integration with theme system

Based on: widgets/theme_system/docs/fonts-theme-studio-integration-PLAN.md
Phase 5 - Font Family List Editing
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
from vfwidgets_theme.widgets.font_family_editor import FontFamilyListEditor


class FontFamilyEditingDemo(ThemedWidget, QMainWindow):
    """Demo window showing font family list editing."""

    def __init__(self):
        """Initialize demo window."""
        super().__init__()

        self.setWindowTitle("Font Family List Editing Demo - Phase 5")
        self.resize(1200, 700)

        # Create test theme with various font families
        self._test_theme = Theme(
            name="Family Test Theme",
            fonts={
                # Terminal fonts
                "terminal.fontFamily": [
                    "JetBrains Mono",
                    "Fira Code",
                    "Consolas",
                    "monospace",
                ],
                # Editor fonts
                "editor.fontFamily": [
                    "Source Code Pro",
                    "Monaco",
                    "Courier New",
                    "monospace",
                ],
                # UI fonts
                "ui.fontFamily": [
                    "Segoe UI",
                    "Roboto",
                    "Helvetica",
                    "sans-serif",
                ],
                # Base mono fonts
                "fonts.mono": ["Consolas", "Courier New", "monospace"],
                # Base UI fonts
                "fonts.ui": ["Arial", "Helvetica", "sans-serif"],
                # Base serif fonts
                "fonts.serif": ["Georgia", "Times New Roman", "serif"],
            },
        )

        # Setup UI
        self._setup_ui()

        # Start with terminal.fontFamily
        self._select_token("terminal.fontFamily")

    def _setup_ui(self) -> None:
        """Set up user interface."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        # Left: Token selector
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        left_layout.addWidget(QLabel("<b>Select Font Family Token:</b>"))

        # Token buttons
        self._token_buttons = {}
        token_list = [
            ("terminal.fontFamily", "Terminal Font Family"),
            ("editor.fontFamily", "Editor Font Family"),
            ("ui.fontFamily", "UI Font Family"),
            ("fonts.mono", "Base Monospace Fonts"),
            ("fonts.ui", "Base UI Fonts"),
            ("fonts.serif", "Base Serif Fonts"),
        ]

        for token_path, label_text in token_list:
            btn = QPushButton(label_text)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, t=token_path: self._select_token(t))
            self._token_buttons[token_path] = btn
            left_layout.addWidget(btn)

        left_layout.addWidget(QLabel("\n<b>Instructions:</b>\n" "• Drag fonts to reorder\n" "• Click \"Add Font...\" to add new fonts\n" "• Select and remove fonts\n" "• ✓ = Font available on system\n" "• ✗ = Font not installed\n"))

        left_layout.addStretch()
        layout.addWidget(left_panel)

        # Middle: Font family list editor
        middle_panel = QWidget()
        middle_layout = QVBoxLayout(middle_panel)

        middle_layout.addWidget(QLabel("<b>Font Family List Editor:</b>"))

        self._family_editor = FontFamilyListEditor()
        self._family_editor.families_changed.connect(self._on_families_changed)
        middle_layout.addWidget(self._family_editor)

        layout.addWidget(middle_panel)

        # Right: Change log
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

        # Current family list display
        right_layout.addWidget(QLabel("<b>Current Family List:</b>"))
        self._current_list_label = QLabel("(select a token)")
        self._current_list_label.setWordWrap(True)
        self._current_list_label.setStyleSheet("padding: 10px; background: #f0f0f0;")
        right_layout.addWidget(self._current_list_label)

        layout.addWidget(right_panel)

        # Set proportions
        layout.setStretch(0, 2)  # Left: 2
        layout.setStretch(1, 4)  # Middle: 4
        layout.setStretch(2, 3)  # Right: 3

    def _select_token(self, token_path: str) -> None:
        """Select and edit a token.

        Args:
            token_path: Token path to edit

        """
        # Update button states
        for path, btn in self._token_buttons.items():
            btn.setChecked(path == token_path)

        # Get current family list
        current_families = self._test_theme.fonts.get(token_path, [])

        # Set token in editor
        self._family_editor.set_token(token_path, current_families, self._test_theme)

        # Update current list display
        self._update_current_list_display(token_path, current_families)

        # Log selection
        self._log_event(f"<b>Selected token:</b> {token_path}<br/>" f"Families: {', '.join(current_families)}")

    def _on_families_changed(self, token_path: str, new_families: list[str]) -> None:
        """Handle family list changes.

        Args:
            token_path: Token path that changed
            new_families: New font family list

        """
        # Get old families
        old_families = self._test_theme.fonts.get(token_path, [])

        # Update theme
        self._test_theme.fonts[token_path] = new_families

        # Update current list display
        self._update_current_list_display(token_path, new_families)

        # Log change
        self._log_event(
            f"<span style='color: #4CAF50;'><b>Families changed:</b></span><br/>"
            f"  Token: {token_path}<br/>"
            f"  Old: {', '.join(old_families)}<br/>"
            f"  New: {', '.join(new_families)}<br/>"
            f"  Count: {len(new_families)} families"
        )

    def _update_current_list_display(self, token_path: str, families: list[str]) -> None:
        """Update the current family list display.

        Args:
            token_path: Token path
            families: Font family list

        """
        # Format families list
        families_html = []
        for i, family in enumerate(families, 1):
            families_html.append(f"{i}. {family}")

        display_text = (
            f"<b>{token_path}</b><br/><br/>" f"{'<br/>'.join(families_html)}<br/><br/>" f"<i>Total: {len(families)} families</i>"
        )

        self._current_list_label.setText(display_text)

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

    window = FontFamilyEditingDemo()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
