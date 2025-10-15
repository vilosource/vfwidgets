#!/usr/bin/env python3
"""Test markdown_widget theme integration.

This script verifies that:
1. MarkdownViewer inherits from ThemedWidget when theme system is available
2. Theme configuration is properly defined
3. Theme colors are applied to the viewer
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from PySide6.QtWidgets import QApplication

# Import markdown viewer
from vfwidgets_markdown.widgets.markdown_viewer import THEME_AVAILABLE, MarkdownViewer

# Import theme system
try:
    from vfwidgets_theme import ThemedWidget
    from vfwidgets_theme.core.theme import Theme

    THEME_SYSTEM_AVAILABLE = True
except ImportError:
    THEME_SYSTEM_AVAILABLE = False


def test_theme_integration():
    """Test that MarkdownViewer properly integrates with theme system."""

    print("Testing MarkdownViewer Theme Integration")
    print("=" * 60)

    # Check if theme system is available
    print(f"\n1. Theme system available: {THEME_AVAILABLE}")
    print(f"   vfwidgets-theme installed: {THEME_SYSTEM_AVAILABLE}")

    if not THEME_AVAILABLE:
        print("   ⚠️  Theme system not available - widget will use default styling")
        return

    # Check if MarkdownViewer inherits from ThemedWidget
    print(f"\n2. MarkdownViewer inherits from ThemedWidget: {issubclass(MarkdownViewer, ThemedWidget)}")

    # Check theme_config
    print(f"\n3. theme_config defined: {hasattr(MarkdownViewer, 'theme_config')}")
    if hasattr(MarkdownViewer, 'theme_config'):
        print(f"   Number of theme tokens: {len(MarkdownViewer.theme_config)}")
        print("   Tokens:")
        for key, value in MarkdownViewer.theme_config.items():
            print(f"      {key:30} → {value}")

    # Create viewer and check theme attributes
    print("\n4. Creating MarkdownViewer instance...")
    app = QApplication.instance() or QApplication(sys.argv)

    viewer = MarkdownViewer(initial_content="# Theme Test\n\nTesting markdown viewer with themes.")

    # Check if theme attribute exists after initialization
    has_theme = hasattr(viewer, 'theme')
    print(f"   Has 'theme' attribute: {has_theme}")

    if has_theme:
        print("   Theme tokens available:")
        for key in MarkdownViewer.theme_config.keys():
            if hasattr(viewer.theme, key):
                value = getattr(viewer.theme, key)
                print(f"      {key:30} = {value}")

    # Check page background color
    bg_color = viewer.page().backgroundColor()
    print(f"\n5. Page background color set: {bg_color.isValid()}")
    if bg_color.isValid():
        print(f"   Color: {bg_color.name()}")

    # Show viewer
    print("\n6. Showing viewer...")
    viewer.show()
    viewer.resize(800, 600)

    print("\n✓ All checks complete!")
    print("\nViewer window opened. Press Ctrl+C to exit.")

    # Run event loop
    return app.exec()


if __name__ == "__main__":
    sys.exit(test_theme_integration())
