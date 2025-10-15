#!/usr/bin/env python3
"""Verify FONT TOKENS category exists in Token Browser."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication

from vfwidgets_theme.core.theme import Theme
from vfwidgets_theme.widgets.token_browser import TokenBrowserWidget


def verify_font_tokens():
    """Verify font tokens are in the token browser."""
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
    print("VERIFICATION: Font Tokens in Token Browser")
    print("=" * 70)
    print()

    # Check categories
    print(f"Total categories: {len(browser._categories)}")
    print(f"Total tokens: {len(browser._all_tokens)}")
    print()

    # Check if FONT TOKENS category exists
    if "FONT TOKENS" in browser._categories:
        font_tokens = browser._categories["FONT TOKENS"]
        print("✓ FONT TOKENS category EXISTS")
        print(f"  Token count: {len(font_tokens)}")
        print()
        print("  First 10 font tokens:")
        for i, (name, path) in enumerate(font_tokens[:10], 1):
            # Get display value
            value = ""
            if path in theme.fonts:
                val = theme.fonts[path]
                if isinstance(val, list):
                    value = f"{', '.join(val[:2])}..."
                else:
                    value = str(val)

            print(f"    {i:2d}. {name:25s} → {path:30s} = {value}")

        if len(font_tokens) > 10:
            print(f"    ... and {len(font_tokens) - 10} more tokens")
    else:
        print("✗ FONT TOKENS category NOT FOUND")
        print(f"  Available categories: {list(browser._categories.keys())}")

    print()
    print("=" * 70)
    print("Verification complete!")
    print("=" * 70)

    return 0

if __name__ == "__main__":
    sys.exit(verify_font_tokens())
