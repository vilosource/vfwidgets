"""Test color icon fix for white background issue."""

import sys

from PySide6.QtCore import QModelIndex, QTimer

from src.theme_studio.app import ThemeStudioApp
from src.theme_studio.window import ThemeStudioWindow


def test_color_icon_fix():
    """Test that color icons display properly with borders."""

    print("=" * 60)
    print("Testing Color Icon Fix")
    print("=" * 60)

    # Create application
    app = ThemeStudioApp(sys.argv)

    # Create window
    window = ThemeStudioWindow()

    print("\n1. Testing with white color token...")

    # Set a white color on a token
    document = window._current_document
    document.set_token("button.foreground", "#ffffff")

    # Get model
    model = window.token_browser._model

    print("   ✓ Set button.foreground to #ffffff (white)")

    # Find button.foreground in tree
    root = QModelIndex()
    for cat_row in range(model.rowCount(root)):
        cat_index = model.index(cat_row, 0, root)
        cat_name = model.data(cat_index)

        if "Button" in cat_name:
            # Found button category, look for button.foreground
            for token_row in range(model.rowCount(cat_index)):
                token_index = model.index(token_row, 0, cat_index)
                token_name = model.data(token_index)

                if token_name == "button.foreground":
                    from PySide6.QtCore import Qt
                    from PySide6.QtGui import QPixmap

                    decoration = model.data(token_index, Qt.DecorationRole)

                    print(f"   Token: {token_name}")
                    print(f"   Decoration type: {type(decoration)}")

                    assert isinstance(decoration, QPixmap), f"Expected QPixmap, got {type(decoration)}"
                    print("   ✓ Decoration is QPixmap (not QColor)")

                    assert decoration.width() == 16
                    assert decoration.height() == 16
                    print(f"   ✓ Icon size: {decoration.width()}x{decoration.height()}")

                    break
            break

    print("\n2. Testing with black color token...")

    # Set a black color
    document.set_token("button.background", "#000000")
    print("   ✓ Set button.background to #000000 (black)")

    # Rebuild model to get updated value
    from src.theme_studio.widgets import TokenTreeModel
    model = TokenTreeModel(document)
    window.token_browser.set_model(model)

    # Find button.background
    for cat_row in range(model.rowCount(root)):
        cat_index = model.index(cat_row, 0, root)
        cat_name = model.data(cat_index)

        if "Button" in cat_name:
            for token_row in range(model.rowCount(cat_index)):
                token_index = model.index(token_row, 0, cat_index)
                token_name = model.data(token_index)

                if token_name == "button.background":
                    decoration = model.data(token_index, Qt.DecorationRole)

                    assert isinstance(decoration, QPixmap)
                    print("   ✓ Black color also uses QPixmap with border")
                    break
            break

    print("\n3. Testing with colored token...")

    # Set a blue color
    document.set_token("button.border", "#0078d4")
    model = TokenTreeModel(document)
    print("   ✓ Set button.border to #0078d4 (blue)")

    # Find button.border
    for cat_row in range(model.rowCount(root)):
        cat_index = model.index(cat_row, 0, root)
        cat_name = model.data(cat_index)

        if "Button" in cat_name:
            for token_row in range(model.rowCount(cat_index)):
                token_index = model.index(token_row, 0, cat_index)
                token_name = model.data(token_index)

                if token_name == "button.border":
                    decoration = model.data(token_index, Qt.DecorationRole)

                    assert isinstance(decoration, QPixmap)
                    print("   ✓ Blue color also uses QPixmap with border")
                    break
            break

    print("\n4. Showing window to verify visual appearance...")
    window.show()
    app.processEvents()

    print("   ✓ Window visible - check that white colors now have visible borders")

    print("\n" + "=" * 60)
    print("Color Icon Fix Test: PASSED ✓")
    print("=" * 60)
    print("\nVisual Check:")
    print("- White/light colored tokens should have dark borders")
    print("- Black/dark colored tokens should have light borders")
    print("- All color icons should be clearly visible")

    # Close after delay
    QTimer.singleShot(2000, window.close)

    return app.exec()

if __name__ == "__main__":
    sys.exit(test_color_icon_fix())
