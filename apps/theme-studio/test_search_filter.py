"""Test Token Search/Filter - Task 3.3 validation."""

import sys

from PySide6.QtCore import QModelIndex, QTimer

from src.theme_studio.app import ThemeStudioApp
from src.theme_studio.window import ThemeStudioWindow


def test_search_filter():
    """Test that search/filter functionality works."""

    print("=" * 60)
    print("Testing Token Search/Filter (Task 3.3)")
    print("=" * 60)

    # Create application
    app = ThemeStudioApp(sys.argv)

    # Create window
    window = ThemeStudioWindow()

    print("\n1. Window and token browser created")

    # Get references
    token_browser = window.token_browser
    proxy_model = token_browser._proxy_model

    assert proxy_model is not None
    print("   ✓ Proxy model created")

    # Test 1: No filter - should show all tokens
    print("\n2. Testing with no filter...")
    root = QModelIndex()
    initial_count = proxy_model.rowCount(root)
    print(f"   Categories visible: {initial_count}")
    assert initial_count == 15, f"Expected 15 categories, got {initial_count}"
    print("   ✓ All 15 categories visible")

    # Test 2: Filter by "button"
    print("\n3. Testing filter: 'button'...")
    token_browser.search_input.setText("button")
    app.processEvents()

    # Count visible categories/tokens
    visible_categories = proxy_model.rowCount(root)
    print(f"   Visible categories: {visible_categories}")

    # Check that button category is visible
    found_button = False
    for row in range(visible_categories):
        cat_index = proxy_model.index(row, 0, root)
        cat_name = proxy_model.data(cat_index)
        if "Button" in cat_name:
            found_button = True
            token_count = proxy_model.rowCount(cat_index)
            print(f"   Found: {cat_name} with {token_count} tokens")

    assert found_button, "Button category should be visible"
    print("   ✓ Filter shows button-related tokens")

    # Test 3: Filter by specific token
    print("\n4. Testing filter: 'background'...")
    token_browser.search_input.setText("background")
    app.processEvents()

    visible_after_filter = proxy_model.rowCount(root)
    print(f"   Visible categories: {visible_after_filter}")
    assert visible_after_filter > 0, "Should have visible categories with 'background' tokens"
    print("   ✓ Filter shows background tokens")

    # Test 4: Clear filter
    print("\n5. Testing clear filter...")
    token_browser.search_input.clear()
    app.processEvents()

    final_count = proxy_model.rowCount(root)
    print(f"   Categories visible after clear: {final_count}")
    assert final_count == 15, f"Expected 15 categories after clear, got {final_count}"
    print("   ✓ All categories visible after clearing filter")

    # Test 5: Case insensitive search
    print("\n6. Testing case-insensitive search: 'BUTTON'...")
    token_browser.search_input.setText("BUTTON")
    app.processEvents()

    found_button_upper = False
    for row in range(proxy_model.rowCount(root)):
        cat_index = proxy_model.index(row, 0, root)
        cat_name = proxy_model.data(cat_index)
        if "Button" in cat_name:
            found_button_upper = True
            break

    assert found_button_upper, "Case-insensitive search should work"
    print("   ✓ Case-insensitive search works")

    print("\n" + "=" * 60)
    print("Token Search/Filter Test: PASSED ✓")
    print("=" * 60)

    # Close window
    QTimer.singleShot(500, window.close)

    return app.exec()

if __name__ == "__main__":
    sys.exit(test_search_filter())
