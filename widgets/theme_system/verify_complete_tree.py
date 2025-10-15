#!/usr/bin/env python3
"""Show complete token browser tree structure."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication

from vfwidgets_theme.core.theme import Theme
from vfwidgets_theme.widgets.token_browser import TokenBrowserWidget


def show_complete_tree():
    """Show the complete tree structure."""
    QApplication(sys.argv)

    theme = Theme(
        name="Test",
        fonts={
            "fonts.mono": ["Consolas", "monospace"],
            "fonts.size": 14,
            "fonts.weight": 400,
        }
    )

    browser = TokenBrowserWidget(theme=theme)
    tree = browser._tree

    print()
    print("=" * 80)
    print("TOKEN BROWSER TREE - Complete Structure")
    print("=" * 80)
    print()

    for i in range(tree.topLevelItemCount()):
        item = tree.topLevelItem(i)
        category = item.text(0)

        # Highlight FONT TOKENS
        if "FONT TOKENS" in category:
            print(f">>> {category} <<<  ** THIS IS WHERE FONT TOKENS ARE **")
        else:
            print(f"{category}")

    print()
    print("=" * 80)
    print()
    print("To set default font:")
    print("  1. Expand 'FONT TOKENS (22)' in the token browser")
    print("  2. Click on 'DEFAULT_SIZE (fonts.size)' to change default size")
    print("  3. Click on 'MONO_FONTS (fonts.mono)' to change default monospace font")
    print("=" * 80)

    return 0

if __name__ == "__main__":
    sys.exit(show_complete_tree())
