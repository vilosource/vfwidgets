"""Test Preview Canvas - Task 4.1 validation."""

import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QLabel

from src.theme_studio.app import ThemeStudioApp
from src.theme_studio.window import ThemeStudioWindow


def test_preview_canvas():
    """Test that preview canvas UI is set up correctly."""

    print("=" * 60)
    print("Testing Preview Canvas (Task 4.1)")
    print("=" * 60)

    # Create application
    app = ThemeStudioApp(sys.argv)

    # Create window
    window = ThemeStudioWindow()

    print("\n1. Checking preview canvas components...")

    # Get preview canvas
    canvas = window.preview_canvas
    assert canvas is not None
    print("   ✓ Preview canvas exists")

    # Check toolbar exists
    assert canvas.plugin_selector is not None
    print("   ✓ Plugin selector exists")

    # Check scroll area exists
    assert canvas.scroll_area is not None
    print("   ✓ Scroll area exists")

    # Check content widget exists
    assert canvas.content_widget is not None
    print("   ✓ Content widget exists")

    # Check placeholder is shown
    assert canvas.placeholder_label is not None
    print("   ✓ Placeholder label shown")

    print("\n2. Testing set_plugin_content method...")

    # Create a test widget
    test_widget = QLabel("Test Plugin Content")

    # Set content
    canvas.set_plugin_content(test_widget)
    app.processEvents()

    # Check placeholder is hidden
    assert canvas.placeholder_label is None
    print("   ✓ Placeholder hidden after setting content")

    # Check test widget is displayed
    assert canvas._current_plugin == test_widget
    print("   ✓ Plugin content set correctly")

    print("\n3. Testing clear_content method...")

    # Clear content
    canvas.clear_content()
    app.processEvents()

    # Check placeholder is shown again
    assert canvas.placeholder_label is not None
    print("   ✓ Placeholder shown after clearing")

    # Check plugin widget is removed
    assert canvas._current_plugin is None
    print("   ✓ Plugin content cleared")

    print("\n4. Showing window briefly...")
    window.show()
    app.processEvents()

    assert window.isVisible()
    print("   ✓ Window visible")

    assert canvas.isVisible()
    print("   ✓ Canvas visible")

    print("\n" + "=" * 60)
    print("Preview Canvas Test: PASSED ✓")
    print("=" * 60)

    # Close window
    QTimer.singleShot(500, window.close)

    return app.exec()

if __name__ == "__main__":
    sys.exit(test_preview_canvas())
