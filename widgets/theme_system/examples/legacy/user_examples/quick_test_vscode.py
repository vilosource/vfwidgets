#!/usr/bin/env python3
"""Quick test to verify vscode theme loads correctly."""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from vfwidgets_theme import ThemedApplication


def test_vscode_theme():
    """Test that vscode theme can be loaded."""
    app = ThemedApplication(sys.argv)

    print(f"Available themes: {app.available_themes}")
    print(f"Current theme: {app.current_theme_name}")

    # Try to set vscode theme
    try:
        app.set_theme("vscode")
        print("✓ Successfully set vscode theme")
        print(f"Current theme after setting: {app.current_theme_name}")
        return True
    except Exception as e:
        print(f"✗ Error setting vscode theme: {e}")
        return False


if __name__ == "__main__":
    success = test_vscode_theme()
    sys.exit(0 if success else 1)
