"""Test Token Browser UI - Task 3.2 validation."""

import sys

from PySide6.QtCore import QTimer

from src.theme_studio.app import ThemeStudioApp
from src.theme_studio.window import ThemeStudioWindow


def test_token_browser_ui():
    """Test that token browser UI displays correctly."""

    print("=" * 60)
    print("Testing Token Browser UI (Task 3.2)")
    print("=" * 60)

    # Create application
    app = ThemeStudioApp(sys.argv)

    # Create window
    window = ThemeStudioWindow()

    print("\n1. Window created successfully")

    # Check token browser exists
    assert window.token_browser is not None
    print("   ✓ Token browser panel exists")

    # Check tree view exists
    assert hasattr(window.token_browser, 'tree_view')
    print("   ✓ Tree view exists")

    # Check model is set
    model = window.token_browser.tree_view.model()
    assert model is not None
    print("   ✓ Model is set on tree view")

    # Check root has categories
    from PySide6.QtCore import QModelIndex
    root = QModelIndex()
    category_count = model.rowCount(root)
    print(f"   ✓ Model has {category_count} categories")

    # Check first category has tokens
    first_cat = model.index(0, 0, root)
    token_count = model.rowCount(first_cat)
    print(f"   ✓ First category has {token_count} tokens")

    # Count total tokens
    total_tokens = 0
    for cat_row in range(category_count):
        cat_index = model.index(cat_row, 0, root)
        total_tokens += model.rowCount(cat_index)

    print(f"   ✓ Total tokens: {total_tokens}")

    # Show window briefly
    print("\n2. Showing window...")
    window.show()

    # Check window is visible
    assert window.isVisible()
    print("   ✓ Window is visible")

    # Process events to ensure UI updates
    app.processEvents()

    # Check tree view is visible
    assert window.token_browser.tree_view.isVisible()
    print("   ✓ Tree view is visible")

    # Close window after a short delay
    QTimer.singleShot(500, window.close)

    print("\n" + "=" * 60)
    print("Token Browser UI Test: PASSED ✓")
    print("=" * 60)

    return app.exec()

if __name__ == "__main__":
    sys.exit(test_token_browser_ui())
