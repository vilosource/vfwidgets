"""Simple test for search/filter - Task 3.3."""

import sys

from PySide6.QtCore import QModelIndex
from PySide6.QtWidgets import QApplication

from src.theme_studio.models import ThemeDocument
from src.theme_studio.panels import TokenBrowserPanel
from src.theme_studio.widgets import TokenTreeModel


def test_search():
    """Test search/filter functionality."""

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    print("=" * 60)
    print("Testing Token Search/Filter (Task 3.3)")
    print("=" * 60)

    # Create document and model
    document = ThemeDocument()
    model = TokenTreeModel(document)

    # Create token browser
    print("\n1. Creating token browser with search...")
    browser = TokenBrowserPanel()
    browser.set_model(model)

    assert browser.search_input is not None
    print("   ✓ Search input created")

    assert browser._proxy_model is not None
    print("   ✓ Proxy model created for filtering")

    # Test initial state - all categories visible
    print("\n2. Testing initial state (no filter)...")
    root = QModelIndex()
    initial_count = browser._proxy_model.rowCount(root)
    print(f"   Visible categories: {initial_count}")
    assert initial_count == 15
    print("   ✓ All 15 categories visible")

    # Test filter
    print("\n3. Testing filter: 'button'...")
    browser.search_input.setText("button")
    app.processEvents()

    visible_count = browser._proxy_model.rowCount(root)
    print(f"   Visible categories after filter: {visible_count}")
    assert visible_count > 0
    print("   ✓ Filter applied successfully")

    # Check that button category is visible
    found_button = False
    for row in range(visible_count):
        index = browser._proxy_model.index(row, 0, root)
        name = browser._proxy_model.data(index)
        if "Button" in name:
            found_button = True
            print(f"   Found: {name}")

    assert found_button
    print("   ✓ Button category visible in filtered results")

    # Clear filter
    print("\n4. Testing clear filter...")
    browser.search_input.clear()
    app.processEvents()

    final_count = browser._proxy_model.rowCount(root)
    print(f"   Visible categories after clear: {final_count}")
    assert final_count == 15
    print("   ✓ All categories visible after clearing")

    print("\n" + "=" * 60)
    print("Search/Filter Test: PASSED ✓")
    print("=" * 60)

if __name__ == "__main__":
    test_search()
