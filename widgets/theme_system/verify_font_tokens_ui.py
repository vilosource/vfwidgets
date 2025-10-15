#!/usr/bin/env python3
"""Verify FONT TOKENS category is visible in the Token Browser UI."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication

from vfwidgets_theme.core.theme import Theme
from vfwidgets_theme.widgets.token_browser import TokenBrowserWidget


def verify_ui_tree():
    """Verify font tokens appear in the UI tree."""
    QApplication(sys.argv)

    # Create theme with font properties
    theme = Theme(
        name="Test Theme",
        fonts={
            "fonts.mono": ["Consolas", "monospace"],
            "fonts.size": 14,
            "terminal.fontFamily": ["JetBrains Mono", "monospace"],
        }
    )

    # Create token browser
    browser = TokenBrowserWidget(theme=theme)

    print("=" * 70)
    print("VERIFICATION: Font Tokens in UI Tree")
    print("=" * 70)
    print()

    # Get tree widget
    tree = browser._tree

    print(f"Total top-level items in tree: {tree.topLevelItemCount()}")
    print()

    # Find FONT TOKENS category in tree
    font_tokens_item = None
    for i in range(tree.topLevelItemCount()):
        item = tree.topLevelItem(i)
        category_name = item.text(0)

        if "FONT TOKENS" in category_name:
            font_tokens_item = item
            print(f"✓ Found: '{category_name}'")
            print(f"  Child count: {item.childCount()}")
            print()

            # Show first 5 children
            print("  First 5 tokens in tree:")
            for j in range(min(5, item.childCount())):
                child = item.child(j)
                token_name = child.text(0)  # Column 0: Token name
                token_path = child.text(1)  # Column 1: Token path
                token_value = child.text(2)  # Column 2: Current value
                print(f"    {j+1}. {token_name:25s} | {token_path:30s} | {token_value}")

            if item.childCount() > 5:
                print(f"    ... and {item.childCount() - 5} more")
            break

    if not font_tokens_item:
        print("✗ FONT TOKENS category NOT FOUND in UI tree")
        print("\nAvailable categories in tree:")
        for i in range(tree.topLevelItemCount()):
            item = tree.topLevelItem(i)
            print(f"  {i+1}. {item.text(0)}")

    print()
    print("=" * 70)
    print("Verification complete!")
    print("=" * 70)

    return 0

if __name__ == "__main__":
    sys.exit(verify_ui_tree())
