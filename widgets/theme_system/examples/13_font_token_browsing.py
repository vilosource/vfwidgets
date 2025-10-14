#!/usr/bin/env python3
"""Example 13: Font Token Browsing - Phase 3 Demo
===================================================

Demonstrates Phase 3 font token browsing in Theme Studio:
- Font tokens visible in token browser
- Font token selection works
- Font token values display correctly
- Tooltips show hierarchical resolution chains

What you'll see:
- "FONT TOKENS" category in token browser
- Font family, size, weight tokens organized by widget
- Value column showing current font settings
- Tooltips with resolution chains (hover over tokens)

Phase 3 Features:
- ✅ Font tokens in TokenBrowserWidget
- ✅ Font token value display
- ✅ Hierarchical resolution tooltips
- ✅ Theme updates reflected in browser

Run:
    python examples/13_font_token_browsing.py
"""

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget

from vfwidgets_theme.core.theme import Theme
from vfwidgets_theme.widgets.theme_editor import ThemeEditorWidget


def create_test_theme() -> Theme:
    """Create a test theme with font tokens."""
    return Theme(
        name="Font Browsing Demo",
        version="1.0.0",
        type="dark",
        colors={
            # Minimal colors for theme editor
            "colors.foreground": "#E0E0E0",
            "colors.background": "#1E1E1E",
        },
        fonts={
            # Base Categories
            "fonts.mono": ["JetBrains Mono", "Fira Code", "Consolas", "monospace"],
            "fonts.ui": ["Segoe UI", "Inter", "Ubuntu", "sans-serif"],
            "fonts.serif": ["Georgia", "Times New Roman", "serif"],
            # Base Properties
            "fonts.size": 13,
            "fonts.weight": "normal",
            "fonts.lineHeight": 1.4,
            "fonts.letterSpacing": 0.0,
            # Terminal Fonts
            "terminal.fontFamily": ["Cascadia Code", "Consolas", "monospace"],
            "terminal.fontSize": 14,
            "terminal.fontWeight": 400,
            "terminal.lineHeight": 1.4,
            "terminal.letterSpacing": 0.0,
            # Tabs Fonts
            "tabs.fontFamily": ["Segoe UI Semibold", "Inter", "sans-serif"],
            "tabs.fontSize": 12,
            "tabs.fontWeight": 600,
            # Editor Fonts
            "editor.fontFamily": ["Fira Code", "JetBrains Mono", "monospace"],
            "editor.fontSize": 14,
            "editor.fontWeight": "normal",
            "editor.lineHeight": 1.5,
        },
    )


class FontBrowsingDemo(QMainWindow):
    """Demo window showing font token browsing."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phase 3: Font Token Browsing Demo")
        self.resize(1200, 800)

        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Add instructions
        instructions = QLabel(
            "<h2>Phase 3: Font Token Browsing Demo</h2>"
            "<p><b>What to try:</b></p>"
            "<ul>"
            "<li><b>Navigate:</b> Expand 'FONT TOKENS' category in left panel</li>"
            "<li><b>View Values:</b> See 'Value' column showing current font settings</li>"
            "<li><b>Tooltips:</b> Hover over tokens like 'terminal.fontFamily' to see "
            "resolution chains</li>"
            "<li><b>Selection:</b> Click any font token to select it</li>"
            "<li><b>Search:</b> Type 'terminal' in search box to filter tokens</li>"
            "</ul>"
            "<p><b>Font Token Categories:</b></p>"
            "<ul>"
            "<li><b>Base Categories:</b> fonts.mono, fonts.ui, fonts.serif</li>"
            "<li><b>Base Properties:</b> fonts.size, fonts.weight, fonts.lineHeight</li>"
            "<li><b>Widget Specific:</b> terminal.*, tabs.*, editor.*, ui.*</li>"
            "</ul>"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet(
            "background: #2D2D30; color: #CCCCCC; padding: 15px; "
            "border-radius: 5px; margin: 10px;"
        )
        layout.addWidget(instructions)

        # Create theme editor with test theme
        theme = create_test_theme()
        self.editor = ThemeEditorWidget(
            base_theme=theme,
            show_preview=False,  # Disable preview for Phase 3
            show_validation=False,  # Disable validation for Phase 3
        )
        layout.addWidget(self.editor)


def main():
    """Run the demo."""
    print()
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║  Phase 3: Font Token Browsing Demo                               ║")
    print("║  VFWidgets Theme System v2.1.0                                    ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print()
    print("Demo Steps:")
    print("  1. Expand 'FONT TOKENS' category in token browser")
    print("  2. Observe subcategories (Base Categories, Base Properties, etc.)")
    print("  3. Look at 'Value' column showing current font settings")
    print("  4. Hover over 'terminal.fontFamily' to see resolution chain tooltip")
    print("  5. Click 'terminal.fontSize' to select it")
    print("  6. Try searching for 'terminal' in search box")
    print()
    print("Expected Results:")
    print("  ✓ FONT TOKENS category visible")
    print("  ✓ ~22 font tokens organized by widget")
    print("  ✓ Values displayed: '14pt', 'JetBrains Mono, Fira Code...'")
    print("  ✓ Tooltips show resolution chains")
    print("  ✓ Selection signal emitted on click")
    print()

    app = QApplication(sys.argv)

    # Create and show demo window
    demo = FontBrowsingDemo()
    demo.show()

    print("Demo running! Close window to exit.")
    print()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
