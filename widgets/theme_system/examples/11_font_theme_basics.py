#!/usr/bin/env python3
"""Example 11: Font Theme Basics - Phase 1 Demo
================================================

Demonstrates Phase 1 font support in VFWidgets Theme System v2.1.0:
- Loading themes with font tokens
- Font validation in action
- Inspecting font configuration
- Understanding font token structure

What you'll see:
- Theme loads successfully with fonts
- Font tokens are validated on theme creation
- Pretty-printed font configuration
- Examples of invalid font configs (commented out)

Phase 1 Features:
- ✅ Theme.fonts field
- ✅ Font exception hierarchy
- ✅ Font validation logic
- ✅ Package themes with font tokens

Run:
    python examples/11_font_theme_basics.py
"""

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vfwidgets_theme.core.theme import Theme
from vfwidgets_theme.errors import FontPropertyError, FontValidationError


def print_header(text: str) -> None:
    """Print a fancy header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def demo_basic_font_loading():
    """Demonstrate loading a theme with fonts."""
    print_header("1. Loading Theme with Font Tokens")

    # Create a theme with basic font configuration
    theme = Theme(
        name="Demo Theme",
        version="1.0.0",
        fonts={
            "fonts.mono": ["JetBrains Mono", "Fira Code", "Consolas", "monospace"],
            "fonts.ui": ["Segoe UI", "Inter", "Ubuntu", "sans-serif"],
            "fonts.serif": ["Georgia", "Times New Roman", "serif"],
            "fonts.size": 13,
            "fonts.weight": "normal",
            "terminal.fontFamily": ["Cascadia Code", "Consolas", "monospace"],
            "terminal.fontSize": 14,
            "terminal.lineHeight": 1.4,
            "tabs.fontFamily": ["Segoe UI Semibold", "sans-serif"],
            "tabs.fontSize": 12,
        },
    )

    print(f"✅ Successfully loaded theme: {theme.name}")
    print(f"   Version: {theme.version}")
    print(f"   Font tokens: {len(theme.fonts)}")
    print()


def demo_font_token_structure():
    """Show the structure of font tokens."""
    print_header("2. Font Token Structure")

    theme = Theme(
        name="Structure Demo",
        fonts={
            "fonts.mono": ["JetBrains Mono", "monospace"],
            "fonts.ui": ["Segoe UI", "sans-serif"],
            "fonts.size": 13,
            "terminal.fontFamily": ["Consolas", "monospace"],
            "terminal.fontSize": 14,
        },
    )

    print("Font tokens in theme:")
    print()
    for key, value in theme.fonts.items():
        print(f"  {key:30} = {value}")
    print()


def demo_validation_success():
    """Show validation working correctly."""
    print_header("3. Font Validation - Success Cases")

    # Test different valid configurations
    test_cases = [
        {
            "name": "String font family",
            "fonts": {"terminal.fontFamily": "monospace"},
        },
        {
            "name": "List font family",
            "fonts": {"fonts.mono": ["JetBrains Mono", "Consolas", "monospace"]},
        },
        {
            "name": "Integer font size",
            "fonts": {"terminal.fontSize": 14},
        },
        {
            "name": "Float font size",
            "fonts": {"terminal.fontSize": 13.5},
        },
        {
            "name": "Integer font weight",
            "fonts": {"fonts.weight": 700},
        },
        {
            "name": "String font weight",
            "fonts": {"fonts.weight": "bold"},
        },
    ]

    for test in test_cases:
        _theme = Theme(name="test", fonts=test["fonts"])
        print(f"  ✅ {test['name']}: {test['fonts']}")

    print()


def demo_validation_failures():
    """Show validation catching errors."""
    print_header("4. Font Validation - Error Detection")

    # Test invalid configurations
    invalid_cases = [
        {
            "name": "Invalid font family type (number)",
            "fonts": {"fonts.mono": 123},
            "error": FontPropertyError,
        },
        {
            "name": "Negative font size",
            "fonts": {"terminal.fontSize": -5},
            "error": FontPropertyError,
        },
        {
            "name": "Font size too large (>144pt)",
            "fonts": {"terminal.fontSize": 200},
            "error": FontPropertyError,
        },
        {
            "name": "Invalid font weight",
            "fonts": {"fonts.weight": 950},
            "error": FontPropertyError,
        },
        {
            "name": "Missing monospace fallback",
            "fonts": {"fonts.mono": ["JetBrains Mono"]},
            "error": FontValidationError,
        },
        {
            "name": "Missing sans-serif fallback",
            "fonts": {"fonts.ui": ["Segoe UI"]},
            "error": FontValidationError,
        },
    ]

    for test in invalid_cases:
        try:
            Theme(name="test", fonts=test["fonts"])
            print(f"  ❌ {test['name']}: Should have raised {test['error'].__name__}")
        except test["error"] as e:
            print(f"  ✅ {test['name']}: Caught {type(e).__name__}")
            print(f"     Error: {str(e)[:60]}...")

    print()


def demo_package_themes():
    """Load and inspect package themes with fonts."""
    print_header("5. Package Themes with Fonts")

    import json

    themes_dir = Path(__file__).parent.parent / "themes"

    for theme_file in ["dark-default.json", "light-default.json", "high-contrast.json"]:
        with open(themes_dir / theme_file) as f:
            data = json.load(f)

        theme = Theme(
            name=data["name"],
            version=data["version"],
            colors=data["colors"],
            fonts=data["fonts"],
            token_colors=data.get("tokenColors", []),
            type=data["type"],
        )

        print(f"Theme: {theme.name}")
        print(f"  Font tokens: {len(theme.fonts)}")
        print("  Categories:")
        for key in ["fonts.mono", "fonts.ui", "fonts.serif"]:
            if key in theme.fonts:
                fonts = theme.fonts[key]
                if isinstance(fonts, list):
                    print(f"    {key:20} = {', '.join(fonts)}")
                else:
                    print(f"    {key:20} = {fonts}")
        print()


def demo_font_token_categories():
    """Explain the font token categories."""
    print_header("6. Understanding Font Token Categories")

    print("Font tokens are organized hierarchically:")
    print()
    print("Base Categories:")
    print("  fonts.mono       - Monospace fonts (programming, terminal)")
    print("  fonts.ui         - UI fonts (buttons, tabs, menus)")
    print("  fonts.serif      - Serif fonts (documentation, content)")
    print()
    print("Base Properties:")
    print("  fonts.size       - Default font size (pt)")
    print("  fonts.weight     - Default font weight (normal, bold, 100-900)")
    print()
    print("Widget-Specific Overrides:")
    print("  terminal.fontFamily    - Terminal font (inherits from fonts.mono)")
    print("  terminal.fontSize      - Terminal font size")
    print("  terminal.lineHeight    - Terminal line height")
    print("  tabs.fontFamily        - Tab bar font (inherits from fonts.ui)")
    print("  tabs.fontSize          - Tab bar font size")
    print()
    print("Resolution Hierarchy (Phase 2):")
    print("  terminal.fontSize → fonts.size → 13 (default)")
    print("  tabs.fontFamily → fonts.ui → ['sans-serif']")
    print()


def main():
    """Run all demos."""
    print()
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║  VFWidgets Theme System v2.1.0 - Font Theme Basics Demo          ║")
    print("║  Phase 1: Core Font Infrastructure                                ║")
    print("╚════════════════════════════════════════════════════════════════════╝")

    demo_basic_font_loading()
    demo_font_token_structure()
    demo_validation_success()
    demo_validation_failures()
    demo_package_themes()
    demo_font_token_categories()

    print_header("Summary")
    print("Phase 1 Complete! ✅")
    print()
    print("What we demonstrated:")
    print("  ✅ Theme loads with fonts field")
    print("  ✅ Font validation works correctly")
    print("  ✅ Invalid fonts raise clear errors")
    print("  ✅ Package themes have complete font definitions")
    print()
    print("Next Phase:")
    print("  → Phase 2: Font Token Resolution with FontTokenRegistry")
    print("  → Hierarchical resolution (terminal.fontSize → fonts.size)")
    print("  → Platform font detection and fallbacks")
    print()


if __name__ == "__main__":
    sys.exit(main())
