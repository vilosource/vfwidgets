"""Test Generic Widgets Plugin - Task 4.2 validation."""

import sys

from PySide6.QtCore import QTimer

from src.theme_studio.app import ThemeStudioApp
from src.theme_studio.plugins import GenericWidgetsPlugin


def test_generic_plugin():
    """Test Generic Widgets Plugin."""

    print("=" * 60)
    print("Testing Generic Widgets Plugin (Task 4.2)")
    print("=" * 60)

    # Create application
    app = ThemeStudioApp(sys.argv)

    # Create plugin
    print("\n1. Creating plugin...")
    plugin = GenericWidgetsPlugin()

    assert plugin.get_name() == "Generic Widgets"
    print(f"   ✓ Plugin name: {plugin.get_name()}")

    desc = plugin.get_description()
    assert len(desc) > 0
    print(f"   ✓ Plugin description: {desc}")

    # Create preview widget
    print("\n2. Creating preview widget...")
    widget = plugin.create_preview_widget()

    assert widget is not None
    print("   ✓ Preview widget created")

    # Check widget has content
    assert widget.layout() is not None
    print("   ✓ Widget has layout")

    item_count = widget.layout().count()
    print(f"   ✓ Widget has {item_count} child items")
    assert item_count > 0

    # Show widget
    print("\n3. Showing widget...")
    widget.show()
    app.processEvents()

    assert widget.isVisible()
    print("   ✓ Widget is visible")

    # Check widget size
    print(f"   Size: {widget.width()}x{widget.height()}")

    print("\n" + "=" * 60)
    print("Generic Widgets Plugin Test: PASSED ✓")
    print("=" * 60)

    # Close after delay
    QTimer.singleShot(500, widget.close)

    return app.exec()

if __name__ == "__main__":
    sys.exit(test_generic_plugin())
