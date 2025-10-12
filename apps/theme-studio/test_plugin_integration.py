"""Test Plugin Integration - Task 4.3 validation."""

import sys

from PySide6.QtCore import QTimer

from src.theme_studio.app import ThemeStudioApp
from src.theme_studio.window import ThemeStudioWindow


def test_plugin_integration():
    """Test that plugins integrate with canvas correctly."""

    print("=" * 60)
    print("Testing Plugin Integration (Task 4.3)")
    print("=" * 60)

    # Create application
    app = ThemeStudioApp(sys.argv)

    # Create window
    window = ThemeStudioWindow()

    print("\n1. Checking plugin registration...")

    # Check plugins are registered
    assert len(window._plugins) > 0
    print(f"   ✓ {len(window._plugins)} plugin(s) registered")

    # Check plugin selector has items
    selector = window.preview_canvas.plugin_selector
    item_count = selector.count()
    print(f"   ✓ Plugin selector has {item_count} items")

    # List plugins
    for i in range(selector.count()):
        print(f"      - {selector.itemText(i)}")

    print("\n2. Checking default plugin is loaded...")

    # Check current selection
    current_plugin = selector.currentText()
    print(f"   Current plugin: {current_plugin}")

    # Check plugin content is displayed
    assert window.preview_canvas._current_plugin is not None
    print("   ✓ Plugin content is displayed")

    print("\n3. Testing plugin switching...")

    # Switch to (None)
    selector.setCurrentText("(None)")
    app.processEvents()

    assert window.preview_canvas._current_plugin is None
    print("   ✓ Cleared content when selecting (None)")

    # Switch back to Generic Widgets
    selector.setCurrentText("Generic Widgets")
    app.processEvents()

    assert window.preview_canvas._current_plugin is not None
    print("   ✓ Plugin content loaded when selecting Generic Widgets")

    print("\n4. Showing window...")
    window.show()
    app.processEvents()

    assert window.isVisible()
    print("   ✓ Window visible")

    assert window.preview_canvas._current_plugin.isVisible()
    print("   ✓ Plugin content visible in canvas")

    print("\n" + "=" * 60)
    print("Plugin Integration Test: PASSED ✓")
    print("=" * 60)

    # Close window
    QTimer.singleShot(500, window.close)

    return app.exec()

if __name__ == "__main__":
    sys.exit(test_plugin_integration())
