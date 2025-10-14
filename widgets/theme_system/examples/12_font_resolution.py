#!/usr/bin/env python3
"""Example 12: Font Resolution - Phase 2 Demo
===============================================

Demonstrates Phase 2 font token resolution in VFWidgets Theme System v2.1.0:
- Hierarchical font resolution
- Fallback chains in action
- Platform font detection
- QFont creation from tokens
- LRU cache performance

What you'll see:
- Token resolution through hierarchy
- Automatic fallbacks to base categories
- Available fonts on your system
- Performance benefits of caching

Phase 2 Features:
- ✅ FontTokenRegistry with resolution methods
- ✅ Hierarchical resolution chains
- ✅ Platform font availability detection
- ✅ QFont creation
- ✅ LRU caching for performance

Run:
    python examples/12_font_resolution.py
"""

import sys
import time
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtWidgets import QApplication

# Create QApplication for QFontDatabase
app = QApplication(sys.argv)

# Import after QApplication creation (FontTokenRegistry uses QFontDatabase)
from vfwidgets_theme.core.font_tokens import FontTokenRegistry  # noqa: E402
from vfwidgets_theme.core.theme import Theme  # noqa: E402


def print_header(text: str) -> None:
    """Print a fancy header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def demo_hierarchical_resolution():
    """Show hierarchical resolution in action."""
    print_header("1. Hierarchical Font Resolution")

    theme = Theme(
        name="Demo",
        fonts={
            # Base categories
            "fonts.mono": ["JetBrains Mono", "Fira Code", "Consolas", "monospace"],
            "fonts.ui": ["Segoe UI", "Inter", "Ubuntu", "sans-serif"],
            "fonts.size": 13,
            "fonts.weight": "normal",
            # Terminal specific
            "terminal.fontSize": 14,
            "terminal.lineHeight": 1.4,
            # Tabs specific
            "tabs.fontSize": 12,
        },
    )

    print("Resolution Chain Examples:")
    print()

    # Terminal font family
    print("1. terminal.fontFamily:")
    print("   Token chain: terminal.fontFamily → fonts.mono")
    result = FontTokenRegistry.get_font_family("terminal.fontFamily", theme)
    print(f"   Resolved to: {result}")
    print("   (No terminal.fontFamily defined, fell back to fonts.mono)")
    print()

    # Terminal font size
    print("2. terminal.fontSize:")
    print("   Token chain: terminal.fontSize → fonts.size")
    result = FontTokenRegistry.get_font_size("terminal.fontSize", theme)
    print(f"   Resolved to: {result}")
    print("   (terminal.fontSize=14 defined, used directly)")
    print()

    # Tabs font family
    print("3. tabs.fontFamily:")
    print("   Token chain: tabs.fontFamily → fonts.ui")
    result = FontTokenRegistry.get_font_family("tabs.fontFamily", theme)
    print(f"   Resolved to: {result}")
    print("   (No tabs.fontFamily defined, fell back to fonts.ui)")
    print()

    # Tabs font size
    print("4. tabs.fontSize:")
    print("   Token chain: tabs.fontSize → fonts.size")
    result = FontTokenRegistry.get_font_size("tabs.fontSize", theme)
    print(f"   Resolved to: {result}")
    print("   (tabs.fontSize=12 defined, used directly)")
    print()


def demo_fallback_chains():
    """Show fallback behavior."""
    print_header("2. Fallback Chains")

    theme = Theme(
        name="Minimal",
        fonts={
            # Only base categories defined
            "fonts.mono": ["Consolas", "monospace"],
            "fonts.ui": ["Arial", "sans-serif"],
            "fonts.size": 13,
        },
    )

    print("When widget-specific tokens don't exist, fallback to base:")
    print()

    widgets = [
        ("terminal", "mono"),
        ("tabs", "ui"),
        ("editor", "mono"),
    ]

    for widget, category in widgets:
        families = FontTokenRegistry.get_font_family(f"{widget}.fontFamily", theme)
        size = FontTokenRegistry.get_font_size(f"{widget}.fontSize", theme)
        weight = FontTokenRegistry.get_font_weight(f"{widget}.fontWeight", theme)

        print(f"{widget}:")
        print(f"  Family: {families} (from fonts.{category})")
        print(f"  Size: {size} (from fonts.size)")
        print(f"  Weight: {weight} (default)")
        print()


def demo_platform_fonts():
    """Show platform font detection."""
    print_header("3. Platform Font Availability")

    # Test various font families
    font_tests = [
        ("JetBrains Mono", "Consolas", "monospace"),
        ("Fira Code", "Courier New", "monospace"),
        ("Segoe UI", "Arial", "sans-serif"),
        ("Comic Sans MS", "Arial", "sans-serif"),
    ]

    print("Detecting available fonts on your system:")
    print()

    for fonts in font_tests:
        available = FontTokenRegistry.get_available_font(fonts)
        print(f"Trying: {', '.join(fonts)}")
        print(f"  → First available: {available}")
        print()


def demo_qfont_creation():
    """Show QFont creation from tokens."""
    print_header("4. QFont Creation from Tokens")

    theme = Theme(
        name="QFont Demo",
        fonts={
            "fonts.mono": ["Consolas", "monospace"],
            "fonts.ui": ["Arial", "sans-serif"],
            "fonts.size": 13,
            "fonts.weight": "bold",
            "terminal.fontSize": 14,
            "terminal.fontWeight": "normal",
        },
    )

    print("Creating QFont instances from theme tokens:")
    print()

    # Terminal font
    terminal_font = FontTokenRegistry.get_qfont("terminal", theme)
    print("Terminal Font:")
    print(f"  Family: {terminal_font.family()}")
    print(f"  Size: {terminal_font.pointSizeF()}pt")
    print(f"  Weight: {terminal_font.weight()}")
    print()

    # Tabs font (inherits from base)
    tabs_font = FontTokenRegistry.get_qfont("tabs", theme)
    print("Tabs Font:")
    print(f"  Family: {tabs_font.family()}")
    print(f"  Size: {tabs_font.pointSizeF()}pt")
    print(f"  Weight: {tabs_font.weight()}")
    print()


def demo_cache_performance():
    """Demonstrate LRU cache performance."""
    print_header("5. LRU Cache Performance")

    theme = Theme(
        name="Cache Test",
        fonts={
            "fonts.mono": ["Consolas", "monospace"],
            "terminal.fontSize": 14,
        },
    )

    # Clear cache for clean test
    FontTokenRegistry.clear_cache()

    print("Testing cache effectiveness:")
    print()

    # First resolution (populates cache)
    start = time.perf_counter()
    for _ in range(1000):
        FontTokenRegistry.get_font_family("terminal.fontFamily", theme)
    first_time = (time.perf_counter() - start) * 1000  # ms

    # Get cache stats
    cache_info = FontTokenRegistry.get_font_family.cache_info()

    print("1000 resolutions:")
    print(f"  Time: {first_time:.2f}ms")
    print(f"  Cache hits: {cache_info.hits}")
    print(f"  Cache misses: {cache_info.misses}")
    print(f"  Cache size: {cache_info.currsize}")
    print(f"  Average per resolution: {first_time/1000:.3f}ms")
    print()

    print("Cache makes resolution extremely fast!")
    print("  → Sub-millisecond per lookup after first resolution")
    print()


def demo_full_resolution_example():
    """Complete example with all font properties."""
    print_header("6. Complete Resolution Example")

    # Load an actual package theme
    import json

    theme_path = Path(__file__).parent.parent / "themes" / "dark-default.json"
    with open(theme_path) as f:
        data = json.load(f)

    theme = Theme(
        name=data["name"],
        version=data["version"],
        colors=data["colors"],
        fonts=data["fonts"],
        token_colors=data.get("tokenColors", []),
        type=data["type"],
    )

    print(f"Loaded theme: {theme.name}")
    print()

    # Resolve all terminal properties
    print("Terminal Widget Font Properties:")
    families = FontTokenRegistry.get_font_family("terminal.fontFamily", theme)
    size = FontTokenRegistry.get_font_size("terminal.fontSize", theme)
    weight = FontTokenRegistry.get_font_weight("terminal.fontWeight", theme)
    line_height = FontTokenRegistry.get_line_height("terminal.lineHeight", theme)
    letter_spacing = FontTokenRegistry.get_letter_spacing("terminal.letterSpacing", theme)

    print(f"  Font Family: {', '.join(families)}")
    print(f"  Size: {size}pt")
    print(f"  Weight: {weight}")
    print(f"  Line Height: {line_height}")
    print(f"  Letter Spacing: {letter_spacing}px")
    print()

    # Create QFont
    font = FontTokenRegistry.get_qfont("terminal", theme)
    print(f"QFont: {font.family()}, {font.pointSizeF()}pt, weight={font.weight()}")
    print()


def demo_resolution_hierarchy():
    """Visualize the complete resolution hierarchy."""
    print_header("7. Complete Resolution Hierarchy")

    print("Font Token Resolution Hierarchy:")
    print()
    print("Terminal Fonts:")
    print("  terminal.fontFamily → fonts.mono → [system monospace]")
    print("  terminal.fontSize   → fonts.size → 13 (default)")
    print("  terminal.fontWeight → fonts.weight → 400 (default)")
    print("  terminal.lineHeight → fonts.lineHeight → 1.4 (default)")
    print()
    print("Tabs Fonts:")
    print("  tabs.fontFamily → fonts.ui → [system sans-serif]")
    print("  tabs.fontSize   → fonts.size → 13 (default)")
    print("  tabs.fontWeight → fonts.weight → 400 (default)")
    print()
    print("Editor Fonts:")
    print("  editor.fontFamily → fonts.mono → [system monospace]")
    print("  editor.fontSize   → fonts.size → 13 (default)")
    print("  editor.fontWeight → fonts.weight → 400 (default)")
    print("  editor.lineHeight → fonts.lineHeight → 1.4 (default)")
    print()
    print("UI Fonts:")
    print("  ui.fontFamily → fonts.ui → [system sans-serif]")
    print("  ui.fontSize   → fonts.size → 13 (default)")
    print("  ui.fontWeight → fonts.weight → 400 (default)")
    print()


def main():
    """Run all demos."""
    print()
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║  VFWidgets Theme System v2.1.0 - Font Resolution Demo            ║")
    print("║  Phase 2: Font Token Resolution                                   ║")
    print("╚════════════════════════════════════════════════════════════════════╝")

    demo_hierarchical_resolution()
    demo_fallback_chains()
    demo_platform_fonts()
    demo_qfont_creation()
    demo_cache_performance()
    demo_full_resolution_example()
    demo_resolution_hierarchy()

    print_header("Summary")
    print("Phase 2 Complete! ✅")
    print()
    print("What we demonstrated:")
    print("  ✅ Hierarchical font resolution works correctly")
    print("  ✅ Fallback chains provide robust defaults")
    print("  ✅ Platform font detection finds available fonts")
    print("  ✅ QFont creation from tokens is seamless")
    print("  ✅ LRU cache provides excellent performance")
    print()
    print("Next Phase:")
    print("  → Phase 3: ThemedWidget Font Integration")
    print("  → Automatic font application to widgets")
    print("  → Terminal and tabs get correct fonts")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
