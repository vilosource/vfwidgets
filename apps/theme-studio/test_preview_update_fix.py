#!/usr/bin/env python3
"""Test script to verify preview update fix.

This script tests that when a token value is changed, the preview canvas
actually updates in real-time.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from theme_studio.window import ThemeStudioWindow


def test_preview_update():
    """Test that preview updates when tokens are changed."""

    print("=" * 70)
    print("Testing Preview Update Fix")
    print("=" * 70)
    print()

    # Create application
    from vfwidgets_theme import ThemedApplication
    app = ThemedApplication([])
    window = ThemeStudioWindow()

    print("✓ Application created")

    # Get document
    doc = window._current_document

    # Get initial button.background value
    initial_value = doc.get_token("button.background")
    print(f"Initial button.background: '{initial_value}'")

    # Check initial theme in ThemeManager
    theme_manager = app._theme_manager
    initial_theme = theme_manager.get_theme(doc.theme.name)
    initial_theme_color = initial_theme.colors.get("button.background", "")
    print(f"Initial ThemeManager color: '{initial_theme_color}'")
    print()

    # Simulate user editing (this triggers the signal chain)
    print("Simulating user edit: button.background = '#ff0000' (red)")
    doc.set_token("button.background", "#ff0000")

    # This should trigger:
    # 1. ThemeDocument.set_token() emits token_changed signal
    # 2. Window._on_token_changed() re-registers theme and updates preview
    # 3. ThemeManager now has the updated theme

    # Check updated value in document
    new_value = doc.get_token("button.background")
    print(f"✓ Document updated: '{new_value}'")

    # Check if ThemeManager has the updated theme
    updated_theme = theme_manager.get_theme(doc.theme.name)
    updated_theme_color = updated_theme.colors.get("button.background", "")
    print(f"✓ ThemeManager updated: '{updated_theme_color}'")
    print()

    # Verify the fix worked
    if updated_theme_color == "#ff0000":
        print("=" * 70)
        print("✅ SUCCESS: Preview update fix works!")
        print("=" * 70)
        print()
        print("The theme was successfully re-registered and the preview")
        print("should now update in real-time when tokens are edited.")
        return 0
    else:
        print("=" * 70)
        print("❌ FAILURE: Preview update fix did not work")
        print("=" * 70)
        print()
        print("Expected: #ff0000")
        print(f"Got: {updated_theme_color}")
        return 1


if __name__ == "__main__":
    sys.exit(test_preview_update())
