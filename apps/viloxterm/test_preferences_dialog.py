#!/usr/bin/env python3
"""Test script for preferences dialog.

Run this to test the preferences dialog UI without running the full app.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication
from vfwidgets_theme import ThemedApplication
from viloxterm.components.preferences_dialog import PreferencesDialog


def main():
    """Test the preferences dialog."""
    app = ThemedApplication(sys.argv)
    app.set_theme("dark")

    # Create and show dialog
    dialog = PreferencesDialog()

    # Connect signals for testing
    dialog.preferences_applied.connect(
        lambda prefs: print(f"✅ Preferences applied: {prefs.to_dict()}")
    )
    dialog.terminal_preferences_applied.connect(
        lambda term_prefs: print(f"✅ Terminal preferences applied: {term_prefs}")
    )

    result = dialog.exec()

    if result:
        print("Dialog accepted (OK clicked)")
        print(f"General prefs: {dialog.get_app_preferences().general.to_dict()}")
        print(f"Appearance prefs: {dialog.get_app_preferences().appearance.to_dict()}")
    else:
        print("Dialog rejected (Cancel clicked)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
