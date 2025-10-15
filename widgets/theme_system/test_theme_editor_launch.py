#!/usr/bin/env python3
"""Test launching ThemeEditorDialog to verify TokenBrowser is present."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication

from vfwidgets_theme.widgets import ThemeEditorDialog


def main():
    """Launch theme editor dialog and verify components."""
    app = QApplication(sys.argv)

    print("=" * 80)
    print("Launching ThemeEditorDialog...")
    print("=" * 80)
    print()

    # Create dialog
    dialog = ThemeEditorDialog()

    # Check components
    editor = dialog._editor
    print(f"✓ ThemeEditorWidget created: {editor}")
    print(f"✓ TokenBrowserWidget present: {editor._token_browser}")
    print(f"✓ FontPropertyEditor present: {editor._font_property_editor}")
    print(f"✓ FontFamilyEditor present: {editor._font_family_editor}")
    print()

    # Check token browser has font tokens
    token_browser = editor._token_browser
    if "FONT TOKENS" in token_browser._categories:
        count = len(token_browser._categories["FONT TOKENS"])
        print(f"✓ FONT TOKENS category exists with {count} tokens")

        # Check if visible in tree
        tree = token_browser._tree
        for i in range(tree.topLevelItemCount()):
            item = tree.topLevelItem(i)
            if "FONT TOKENS" in item.text(0):
                print(f"✓ FONT TOKENS visible in tree: '{item.text(0)}'")
                print(f"  Children in tree: {item.childCount()}")
                break
    else:
        print("✗ FONT TOKENS category NOT found")

    print()
    print("=" * 80)
    print("Theme Editor is ready!")
    print("=" * 80)
    print()
    print("To set default font:")
    print("  1. Look at LEFT PANEL (Token Browser)")
    print("  2. Scroll to bottom and expand 'FONT TOKENS (22)'")
    print("  3. Click 'DEFAULT_SIZE' or 'MONO_FONTS'")
    print("  4. Middle panel will show appropriate editor")
    print()
    print("Close the dialog window to exit...")
    print("=" * 80)

    # Show dialog
    dialog.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
