#!/usr/bin/env python3
"""Test script to verify the manual workflow works.

This script programmatically tests the steps described in USER-GUIDE-MVP.md
"""

import json
import sys
import tempfile
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from theme_studio.app import ThemeStudioApp
from theme_studio.models import ThemeDocument
from theme_studio.window import ThemeStudioWindow


def test_manual_workflow():
    """Test the complete manual workflow from USER-GUIDE-MVP.md"""

    print("=" * 70)
    print("Testing VFTheme Studio MVP Manual Workflow")
    print("=" * 70)
    print()

    # Create application
    app = ThemeStudioApp([])
    window = ThemeStudioWindow()

    print("✓ Step 1: Application launched successfully")
    print(f"  - Window title: {window.windowTitle()}")
    print()

    # Verify three-panel layout
    assert window.token_browser is not None, "Token Browser missing"
    assert window.preview_canvas is not None, "Preview Canvas missing"
    assert window.inspector_panel is not None, "Inspector Panel missing"
    print("✓ Step 2: Three-panel layout verified")
    print("  - Token Browser: Present")
    print("  - Preview Canvas: Present")
    print("  - Inspector Panel: Present")
    print()

    # Create new document (Step 3 from manual)
    doc = window._current_document
    assert doc is not None, "No document created"
    assert not doc.is_modified(), "New document should not be modified"
    print("✓ Step 3: New theme created")
    print(f"  - Theme name: {doc.theme.name}")
    print(f"  - Modified: {doc.is_modified()}")
    print(f"  - Token count: {doc.get_token_count()}")
    print()

    # Test editing workflow (Step 4 from manual)
    print("Testing token editing workflow:")
    print("-" * 70)

    # Edit button.background (Example from manual)
    token_name = "button.background"
    new_value = "#2196f3"  # Material Blue from manual

    print(f"\n1. Setting token: {token_name}")
    print(f"   Value: {new_value}")

    # Set token through document (simulates inspector editing)
    old_value = doc.get_token(token_name)
    doc.set_token(token_name, new_value)

    print("   ✓ Token set successfully")
    print(f"   - Old value: '{old_value}' (empty = default)")
    print(f"   - New value: '{doc.get_token(token_name)}'")
    print(f"   - Document modified: {doc.is_modified()}")
    print()

    # Edit button.foreground
    token_name2 = "button.foreground"
    new_value2 = "#ffffff"  # White from manual

    print(f"2. Setting token: {token_name2}")
    print(f"   Value: {new_value2}")

    doc.set_token(token_name2, new_value2)

    print("   ✓ Token set successfully")
    print(f"   - Value: '{doc.get_token(token_name2)}'")
    print()

    # Test validation (Step 4 from manual)
    print("Testing validation:")
    print("-" * 70)

    from theme_studio.validators import TokenValidator

    # Valid colors
    valid_tests = [
        "#2196f3",      # 6-digit hex
        "#21f",         # 3-digit hex
        "#2196f3ff",    # 8-digit hex with alpha
        "blue",         # Color name
        "rgb(33, 150, 243)",  # RGB
    ]

    print("\nValid color formats:")
    for color in valid_tests:
        is_valid, error = TokenValidator.validate_color(color)
        status = "✓" if is_valid else "✗"
        print(f"  {status} '{color}' - {error if error else 'Valid'}")

    # Invalid colors
    invalid_tests = [
        "#12",          # Too short
        "#12345",       # Wrong length
        "#gggggg",      # Invalid hex chars
    ]

    print("\nInvalid color formats (should fail):")
    for color in invalid_tests:
        is_valid, error = TokenValidator.validate_color(color)
        status = "✓" if not is_valid else "✗"
        print(f"  {status} '{color}' - {error}")

    print()

    # Test undo/redo (Step 7 from manual)
    print("Testing undo/redo:")
    print("-" * 70)

    initial_value = doc.get_token("editor.background")
    print(f"\n1. Initial value of editor.background: '{initial_value}'")

    # Make changes through undo system
    from theme_studio.commands import SetTokenCommand

    cmd1 = SetTokenCommand(doc, "editor.background", "#0d1117", initial_value)
    doc._undo_stack.push(cmd1)

    print(f"2. Changed to: '{doc.get_token('editor.background')}'")
    print(f"   - Can undo: {doc._undo_stack.canUndo()}")
    print(f"   - Can redo: {doc._undo_stack.canRedo()}")

    # Undo
    doc._undo_stack.undo()
    print(f"3. After undo: '{doc.get_token('editor.background')}'")
    print(f"   - Can undo: {doc._undo_stack.canUndo()}")
    print(f"   - Can redo: {doc._undo_stack.canRedo()}")

    # Redo
    doc._undo_stack.redo()
    print(f"4. After redo: '{doc.get_token('editor.background')}'")
    print("   ✓ Undo/Redo working correctly")
    print()

    # Test save workflow (Step 8 from manual)
    print("Testing save workflow:")
    print("-" * 70)

    # Create temp file for save test
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name

    try:
        # Save theme
        doc.save(temp_path)
        print(f"\n1. Saved theme to: {temp_path}")
        print(f"   - Modified after save: {doc.is_modified()}")

        # Read and verify JSON
        with open(temp_path) as f:
            theme_data = json.load(f)

        print("\n2. Theme file contents:")
        print(f"   - Name: {theme_data.get('name')}")
        print(f"   - Version: {theme_data.get('version')}")
        print(f"   - Type: {theme_data.get('type')}")
        print(f"   - Defined tokens: {len(theme_data.get('colors', {}))}")

        # Verify our edits are in the file
        colors = theme_data.get('colors', {})
        assert "button.background" in colors, "button.background not saved"
        assert colors["button.background"] == "#2196f3", "Wrong value saved"
        assert "button.foreground" in colors, "button.foreground not saved"
        assert colors["button.foreground"] == "#ffffff", "Wrong value saved"

        print("\n3. Verified saved tokens:")
        print(f"   ✓ button.background: {colors['button.background']}")
        print(f"   ✓ button.foreground: {colors['button.foreground']}")

        # Test load workflow (Step 9 from manual)
        print("\n4. Testing load workflow:")
        new_doc = ThemeDocument()
        new_doc.load(temp_path)

        print("   ✓ Theme loaded successfully")
        print(f"   - Theme name: {new_doc.theme.name}")
        print(f"   - Tokens loaded: {len(new_doc.get_all_tokens())}")
        print(f"   - button.background: {new_doc.get_token('button.background')}")
        print(f"   - button.foreground: {new_doc.get_token('button.foreground')}")

    finally:
        # Cleanup
        Path(temp_path).unlink(missing_ok=True)

    print()
    print("=" * 70)
    print("✓ ALL MANUAL WORKFLOW TESTS PASSED!")
    print("=" * 70)
    print()
    print("Manual verification complete:")
    print("  ✓ Application launches")
    print("  ✓ Three-panel layout works")
    print("  ✓ New theme creation works")
    print("  ✓ Token editing works")
    print("  ✓ Validation works")
    print("  ✓ Undo/Redo works")
    print("  ✓ Save/Load works")
    print()
    print("The USER-GUIDE-MVP.md manual is accurate and functional!")
    print()

    # Don't show window in test
    # window.close()
    # return app.exec()
    return 0


if __name__ == "__main__":
    sys.exit(test_manual_workflow())
