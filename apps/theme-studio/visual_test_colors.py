"""Visual test to verify color icons with borders."""

import sys

from PySide6.QtCore import QTimer

from src.theme_studio.app import ThemeStudioApp
from src.theme_studio.window import ThemeStudioWindow


def setup_test_colors():
    """Set up test colors to verify the fix."""

    app = ThemeStudioApp(sys.argv)
    window = ThemeStudioWindow()

    # Get document
    doc = window._current_document

    # Set various colors to test
    test_colors = {
        'button.foreground': '#ffffff',      # White
        'button.background': '#000000',      # Black
        'button.border': '#ff0000',          # Red
        'input.background': '#f0f0f0',       # Very light gray
        'input.foreground': '#101010',       # Very dark gray
        'list.activeSelectionBackground': '#0078d4',  # Blue
    }

    print("Setting test colors:")
    for token, color in test_colors.items():
        doc.set_token(token, color)
        print(f"  {token}: {color}")

    print("\n✓ All test colors set")
    print("\nVisual verification:")
    print("  - Check token browser (left panel)")
    print("  - Look for colored squares next to token names")
    print("  - White/light colors should have DARK borders")
    print("  - Black/dark colors should have LIGHT borders")
    print("  - All colors should be clearly visible")

    window.show()

    # Keep window open for 10 seconds
    QTimer.singleShot(10000, app.quit)

    return app.exec()

if __name__ == "__main__":
    sys.exit(setup_test_colors())
