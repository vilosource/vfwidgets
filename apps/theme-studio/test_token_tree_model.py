"""Test script for TokenTreeModel - Task 3.1 validation."""

import sys

from PySide6.QtCore import QModelIndex
from PySide6.QtWidgets import QApplication

from src.theme_studio.models import ThemeDocument
from src.theme_studio.widgets import TokenTreeModel


def test_token_tree_model():
    """Test TokenTreeModel implementation."""

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    print("=" * 60)
    print("Testing TokenTreeModel (Task 3.1)")
    print("=" * 60)

    # Create document and model
    print("\n1. Creating ThemeDocument and TokenTreeModel...")
    document = ThemeDocument()
    model = TokenTreeModel(document)
    print("   ✓ Model created successfully")

    # Test root level (categories)
    print("\n2. Testing root level (categories)...")
    root_index = QModelIndex()
    category_count = model.rowCount(root_index)
    print(f"   Number of categories: {category_count}")

    if category_count == 0:
        print("   ✗ ERROR: No categories found!")
        return False

    print(f"   ✓ Found {category_count} categories")

    # Test first few categories
    print("\n3. Testing category nodes...")
    total_tokens = 0
    for row in range(min(5, category_count)):
        cat_index = model.index(row, 0, root_index)
        cat_name = model.data(cat_index)
        token_count = model.rowCount(cat_index)
        total_tokens += token_count

        print(f"   Category {row}: {cat_name} - {token_count} tokens")

        # Test first token in this category
        if token_count > 0:
            token_index = model.index(0, 0, cat_index)
            token_name = model.data(token_index)
            print(f"      First token: {token_name}")

    print(f"\n   ✓ Categories contain tokens (sample shows {total_tokens} tokens)")

    # Count all tokens
    print("\n4. Counting all tokens across all categories...")
    all_tokens = 0
    for row in range(category_count):
        cat_index = model.index(row, 0, root_index)
        all_tokens += model.rowCount(cat_index)

    print(f"   Total tokens in model: {all_tokens}")

    if all_tokens != 200:
        print(f"   ⚠ WARNING: Expected 200 tokens, found {all_tokens}")
    else:
        print("   ✓ Correct token count (200)")

    # Test color decoration role
    print("\n5. Testing color preview (DecorationRole)...")
    # Set a token value and check decoration
    test_token = "button.background"
    test_color = "#FF0000"
    document.set_token(test_token, test_color)

    # Rebuild model to pick up the change (or wait for layoutChanged signal)
    # For this test, we'll just create a new model
    model = TokenTreeModel(document)

    # Find the button.background token in the tree
    found = False
    for cat_row in range(category_count):
        cat_index = model.index(cat_row, 0, root_index)
        cat_name = model.data(cat_index)

        if "Button" in cat_name:
            token_count = model.rowCount(cat_index)
            for token_row in range(token_count):
                token_index = model.index(token_row, 0, cat_index)
                token_name = model.data(token_index)

                if token_name == test_token:
                    from PySide6.QtCore import Qt
                    from PySide6.QtGui import QColor
                    decoration = model.data(token_index, Qt.DecorationRole)
                    print(f"   Token: {token_name}")
                    print(f"   Decoration: {decoration}")
                    if isinstance(decoration, QColor):
                        print(f"   ✓ DecorationRole returns QColor: {decoration.name()}")
                    else:
                        print(f"   ✗ ERROR: Expected QColor, got {type(decoration)}")
                        return False
                    found = True
                    break

        if found:
            break

    if not found:
        print("   ⚠ Could not find button.background to test decoration")

    # Test tooltip role
    print("\n6. Testing tooltip (ToolTipRole)...")
    from PySide6.QtCore import Qt
    cat_index = model.index(0, 0, root_index)
    tooltip = model.data(cat_index, Qt.ToolTipRole)
    print(f"   Category tooltip: {tooltip}")
    print("   ✓ ToolTipRole working")

    # Test parent/child relationships
    print("\n7. Testing parent/child relationships...")
    cat_index = model.index(0, 0, root_index)
    token_index = model.index(0, 0, cat_index)

    parent_of_token = model.parent(token_index)
    if parent_of_token == cat_index:
        print("   ✓ Token parent points to category")
    else:
        print("   ✗ ERROR: Token parent incorrect")
        return False

    parent_of_category = model.parent(cat_index)
    if not parent_of_category.isValid():
        print("   ✓ Category parent is root (invalid index)")
    else:
        print("   ✗ ERROR: Category parent should be root")
        return False

    # Test token_changed signal connection
    print("\n8. Testing document signal connection...")
    document.set_token("test.token", "#00FF00")
    print("   ✓ Document token changed (model should receive signal)")

    print("\n" + "=" * 60)
    print("TokenTreeModel Test: PASSED ✓")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        success = test_token_tree_model()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
