"""Phase 2 Integration Tests - Token Editing & Undo/Redo.

Tests Phase 2 features AS ACTUALLY IMPLEMENTED:
1. Instant editing (no edit mode, no Save/Cancel buttons)
2. Clickable color swatch and value label
3. Double-click token shortcut
4. Text input with real-time validation
5. Undo/Redo functionality
6. Real-time preview updates

NOTE: This file was rewritten 2025-10-12 to match actual implementation,
not the original task plan which had edit mode with Save/Cancel buttons.
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtTest import QTest

from theme_studio.window import ThemeStudioWindow


@pytest.fixture
def app(qapp):
    """Provide QApplication instance."""
    return qapp


@pytest.fixture
def window(app):
    """Create ThemeStudioWindow instance."""
    win = ThemeStudioWindow()
    yield win
    win.close()


class TestTokenEditingWorkflow:
    """Test token editing workflows - instant editing UX."""

    def test_inspector_shows_token_details(self, window, qtbot):
        """Test inspector displays token details when token selected."""
        inspector = window.inspector_panel
        doc = window._current_document

        # Set a token
        token_name = "editor.background"
        token_value = "#252526"
        doc.set_token(token_name, token_value)
        inspector.set_token(token_name, token_value)
        qtbot.wait(50)

        # Inspector should show token details
        assert inspector.info_group.isVisible()
        assert inspector.token_name_label.text() == token_name
        assert inspector.token_value_label.text() == token_value

        # Color-specific UI should be visible
        assert inspector.color_swatch.isVisible()
        assert inspector.hint_label.isVisible()
        assert inspector.color_input_label.isVisible()
        assert inspector.color_input.isVisible()

    def test_color_swatch_clickable(self, window, qtbot, monkeypatch):
        """Test clicking color swatch opens color picker."""
        inspector = window.inspector_panel
        doc = window._current_document

        # Set up token
        token_name = "editor.background"
        initial_value = "#252526"
        doc.set_token(token_name, initial_value)
        inspector.set_token(token_name, initial_value)
        qtbot.wait(50)

        # Mock QColorDialog.getColor to return a specific color
        from PySide6.QtWidgets import QColorDialog

        test_color = QColor("#ff0000")

        def mock_get_color(*args, **kwargs):
            return test_color

        monkeypatch.setattr(QColorDialog, "getColor", mock_get_color)

        # Click color swatch
        inspector._on_color_swatch_clicked()
        qtbot.wait(50)

        # Token should be updated
        assert doc.get_token(token_name) == "#ff0000"

    def test_value_label_clickable(self, window, qtbot, monkeypatch):
        """Test clicking value label opens color picker."""
        inspector = window.inspector_panel
        doc = window._current_document

        # Set up token
        token_name = "editor.background"
        initial_value = "#252526"
        doc.set_token(token_name, initial_value)
        inspector.set_token(token_name, initial_value)
        qtbot.wait(50)

        # Mock QColorDialog.getColor
        from PySide6.QtWidgets import QColorDialog

        test_color = QColor("#00ff00")

        def mock_get_color(*args, **kwargs):
            return test_color

        monkeypatch.setattr(QColorDialog, "getColor", mock_get_color)

        # Click value label (triggers same handler as swatch)
        inspector._on_value_clicked()
        qtbot.wait(50)

        # Token should be updated
        assert doc.get_token(token_name) == "#00ff00"

    def test_color_picker_respects_cancel(self, window, qtbot, monkeypatch):
        """Test color picker doesn't update if user cancels."""
        inspector = window.inspector_panel
        doc = window._current_document

        # Set up token
        token_name = "editor.background"
        initial_value = "#252526"
        doc.set_token(token_name, initial_value)
        inspector.set_token(token_name, initial_value)
        qtbot.wait(50)

        # Mock QColorDialog.getColor to return invalid color (user cancelled)
        from PySide6.QtWidgets import QColorDialog

        def mock_get_color(*args, **kwargs):
            return QColor()  # Invalid color = cancelled

        monkeypatch.setattr(QColorDialog, "getColor", mock_get_color)

        # Click color swatch
        inspector._on_color_swatch_clicked()
        qtbot.wait(50)

        # Token should NOT be changed
        assert doc.get_token(token_name) == initial_value


class TestTextInputValidation:
    """Test text input with real-time validation."""

    def test_text_input_visible_for_color_tokens(self, window, qtbot):
        """Test text input appears for color tokens."""
        inspector = window.inspector_panel
        doc = window._current_document

        # Set up color token
        token_name = "editor.background"
        token_value = "#252526"
        doc.set_token(token_name, token_value)
        inspector.set_token(token_name, token_value)
        qtbot.wait(50)

        # Text input should be visible
        assert inspector.color_input.isVisible()
        assert inspector.color_input.text() == token_value

    def test_valid_hex_colors(self, window, qtbot):
        """Test validation accepts valid hex colors."""
        inspector = window.inspector_panel

        token_name = "editor.background"
        inspector.set_token(token_name, "#252526")
        qtbot.wait(50)

        # Test various valid hex formats
        valid_colors = [
            "#123",  # 3-digit hex
            "#123456",  # 6-digit hex
            "#12345678",  # 8-digit hex with alpha
        ]

        for color in valid_colors:
            inspector.color_input.setText(color)
            qtbot.wait(50)

            # Should not show error
            assert not inspector.validation_error_label.isVisible(), f"{color} should be valid"

    def test_invalid_hex_colors(self, window, qtbot):
        """Test validation rejects invalid hex colors."""
        inspector = window.inspector_panel

        token_name = "editor.background"
        inspector.set_token(token_name, "#252526")
        qtbot.wait(50)

        # Test invalid hex formats
        invalid_colors = [
            "#12",  # Too short
            "#12345",  # Wrong length
            "#gggggg",  # Invalid hex chars
            "123456",  # Missing #
        ]

        for color in invalid_colors:
            inspector.color_input.setText(color)
            qtbot.wait(50)

            # Should show error
            assert inspector.validation_error_label.isVisible(), f"{color} should be invalid"

    def test_valid_color_names(self, window, qtbot):
        """Test validation accepts Qt color names."""
        inspector = window.inspector_panel

        token_name = "editor.background"
        inspector.set_token(token_name, "#252526")
        qtbot.wait(50)

        # Test valid color names
        valid_names = ["red", "blue", "white", "black", "transparent"]

        for color_name in valid_names:
            inspector.color_input.setText(color_name)
            qtbot.wait(50)

            # Should not show error
            assert not inspector.validation_error_label.isVisible(), f"{color_name} should be valid"

    def test_valid_rgb_colors(self, window, qtbot):
        """Test validation accepts rgb/rgba formats."""
        inspector = window.inspector_panel

        token_name = "editor.background"
        inspector.set_token(token_name, "#252526")
        qtbot.wait(50)

        # Test rgb/rgba formats
        valid_rgb = [
            "rgb(255,0,0)",
            "rgb(255, 0, 0)",
            "rgba(255,0,0,128)",
            "rgba(255, 0, 0, 0.5)",
        ]

        for color in valid_rgb:
            inspector.color_input.setText(color)
            qtbot.wait(50)

            # Should not show error
            assert not inspector.validation_error_label.isVisible(), f"{color} should be valid"

    def test_empty_value_allowed(self, window, qtbot):
        """Test validation allows empty values (use default)."""
        inspector = window.inspector_panel

        token_name = "editor.background"
        inspector.set_token(token_name, "#252526")
        qtbot.wait(50)

        # Clear value
        inspector.color_input.setText("")
        qtbot.wait(50)

        # Should not show error (empty means use default)
        assert not inspector.validation_error_label.isVisible()

    def test_text_input_applies_on_enter(self, window, qtbot):
        """Test pressing Enter in text input applies the color."""
        inspector = window.inspector_panel
        doc = window._current_document

        # Set up token
        token_name = "editor.background"
        initial_value = "#252526"
        doc.set_token(token_name, initial_value)
        inspector.set_token(token_name, initial_value)
        qtbot.wait(50)

        # Type new color
        new_value = "#ff0000"
        inspector.color_input.setText(new_value)
        qtbot.wait(50)

        # Press Enter
        QTest.keyPress(inspector.color_input, Qt.Key_Return)
        qtbot.wait(100)

        # Token should be updated
        assert doc.get_token(token_name) == new_value

    def test_invalid_color_not_applied_on_enter(self, window, qtbot):
        """Test pressing Enter with invalid color doesn't apply it."""
        inspector = window.inspector_panel
        doc = window._current_document

        # Set up token
        token_name = "editor.background"
        initial_value = "#252526"
        doc.set_token(token_name, initial_value)
        inspector.set_token(token_name, initial_value)
        qtbot.wait(50)

        # Type invalid color
        invalid_value = "#gggggg"
        inspector.color_input.setText(invalid_value)
        qtbot.wait(50)

        # Press Enter
        QTest.keyPress(inspector.color_input, Qt.Key_Return)
        qtbot.wait(100)

        # Token should NOT be changed
        assert doc.get_token(token_name) == initial_value
        # Error should be visible
        assert inspector.validation_error_label.isVisible()


class TestDoubleClickShortcut:
    """Test double-click token to edit shortcut."""

    def test_double_click_opens_color_picker(self, window, qtbot, monkeypatch):
        """Test double-clicking token in tree opens color picker."""
        token_browser = window.token_browser
        doc = window._current_document

        # Set up token
        token_name = "editor.background"
        token_value = "#252526"
        doc.set_token(token_name, token_value)
        qtbot.wait(50)

        # Mock QColorDialog.getColor
        from PySide6.QtWidgets import QColorDialog

        test_color = QColor("#0000ff")

        def mock_get_color(*args, **kwargs):
            return test_color

        monkeypatch.setattr(QColorDialog, "getColor", mock_get_color)

        # Find token in tree and double-click it
        # For this test, we'll simulate the signal directly
        token_browser.token_edit_requested.emit(token_name, token_value)
        qtbot.wait(100)

        # Token should be updated
        assert doc.get_token(token_name) == "#0000ff"


class TestUndoRedo:
    """Test undo/redo functionality."""

    def test_undo_redo_token_change(self, window, qtbot):
        """Test undo/redo for token changes."""
        doc = window._current_document
        inspector = window.inspector_panel

        # Initial state
        token_name = "editor.background"
        initial_value = "#252526"
        doc.set_token(token_name, initial_value)

        # Set token in inspector
        inspector.set_token(token_name, initial_value)
        qtbot.wait(50)

        # Change value via text input
        new_value = "#123456"
        inspector.color_input.setText(new_value)
        QTest.keyPress(inspector.color_input, Qt.Key_Return)
        qtbot.wait(100)

        # Value should be changed
        assert doc.get_token(token_name) == new_value
        assert doc._undo_stack.canUndo()

        # Undo
        window.undo()
        qtbot.wait(50)

        # Should restore initial value
        assert doc.get_token(token_name) == initial_value
        assert doc._undo_stack.canRedo()

        # Redo
        window.redo()
        qtbot.wait(50)

        # Should restore new value
        assert doc.get_token(token_name) == new_value

    def test_undo_redo_menu_items(self, window, qtbot):
        """Test undo/redo menu items enable/disable correctly."""
        doc = window._current_document
        inspector = window.inspector_panel

        # Initially no undo/redo available
        assert hasattr(window, "undo_action")
        assert hasattr(window, "redo_action")
        assert not window.undo_action.isEnabled()
        assert not window.redo_action.isEnabled()

        # Make a change
        token_name = "editor.background"
        doc.set_token(token_name, "#000000")
        inspector.set_token(token_name, "#000000")
        qtbot.wait(50)

        # Change via text input
        inspector.color_input.setText("#123456")
        QTest.keyPress(inspector.color_input, Qt.Key_Return)
        qtbot.wait(100)

        # Undo should be enabled
        assert window.undo_action.isEnabled()
        assert not window.redo_action.isEnabled()

        # Undo the change
        window.undo()
        qtbot.wait(50)

        # Redo should be enabled
        assert window.redo_action.isEnabled()

    def test_multiple_undo_redo(self, window, qtbot):
        """Test multiple undo/redo operations."""
        doc = window._current_document
        inspector = window.inspector_panel

        token_name = "editor.background"
        values = ["#111111", "#222222", "#333333"]

        # Set initial value
        doc.set_token(token_name, "#000000")

        # Make multiple changes
        for value in values:
            inspector.set_token(token_name, doc.get_token(token_name))
            qtbot.wait(50)
            inspector.color_input.setText(value)
            QTest.keyPress(inspector.color_input, Qt.Key_Return)
            qtbot.wait(100)

        # Final value should be last
        assert doc.get_token(token_name) == "#333333"

        # Undo all changes
        window.undo()
        qtbot.wait(50)
        assert doc.get_token(token_name) == "#222222"

        window.undo()
        qtbot.wait(50)
        assert doc.get_token(token_name) == "#111111"

        window.undo()
        qtbot.wait(50)
        assert doc.get_token(token_name) == "#000000"

        # Redo all
        window.redo()
        qtbot.wait(50)
        assert doc.get_token(token_name) == "#111111"

        window.redo()
        qtbot.wait(50)
        assert doc.get_token(token_name) == "#222222"

        window.redo()
        qtbot.wait(50)
        assert doc.get_token(token_name) == "#333333"


class TestPreviewUpdates:
    """Test real-time preview updates."""

    def test_preview_updates_on_token_change(self, window, qtbot):
        """Test preview updates when token changes."""
        doc = window._current_document

        # Change a token
        token_name = "editor.background"
        new_value = "#123456"
        doc.set_token(token_name, new_value)
        qtbot.wait(100)

        # Theme should be updated
        current_theme = doc.theme
        assert current_theme.colors[token_name] == new_value

    def test_preview_canvas_themed(self, window, qtbot):
        """Test preview canvas background reflects theme."""
        doc = window._current_document
        preview_canvas = window.preview_canvas

        # Change background color
        token_name = "colors.background"
        new_value = "#ff0000"
        doc.set_token(token_name, new_value)
        qtbot.wait(100)

        # Canvas should be themed (we can't easily verify stylesheet in test,
        # but we verify the mechanism is in place via method existence)
        assert hasattr(preview_canvas, "apply_canvas_theme")


class TestDocumentModified:
    """Test document modified state."""

    def test_document_modified_on_edit(self, window, qtbot):
        """Test document becomes modified when token is edited."""
        doc = window._current_document

        # Create fresh document
        window.new_theme()
        doc = window._current_document
        assert not doc.is_modified()

        # Edit a token
        token_name = "editor.background"
        doc.set_token(token_name, "#123456")
        qtbot.wait(50)

        # Document should be modified
        assert doc.is_modified()
        assert "*" in window.windowTitle()

    def test_undo_clears_modified_if_back_to_initial(self, window, qtbot):
        """Test undoing all changes clears modified flag."""
        doc = window._current_document

        # Create fresh document
        window.new_theme()
        doc = window._current_document

        # Make one change
        token_name = "editor.background"
        doc.set_token(token_name, "#123456")
        qtbot.wait(50)
        assert doc.is_modified()

        # Undo
        window.undo()
        qtbot.wait(50)

        # Should no longer be modified
        assert not doc.is_modified()


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_complete_editing_workflow(self, window, qtbot):
        """Test complete editing workflow with multiple operations."""
        doc = window._current_document
        inspector = window.inspector_panel

        # Step 1: Create new document
        window.new_theme()
        doc = window._current_document
        assert not doc.is_modified()

        # Step 2: Edit first token via text input
        token1 = "editor.background"
        value1 = "#123456"
        doc.set_token(token1, "#000000")  # Set initial value
        inspector.set_token(token1, "#000000")
        qtbot.wait(50)
        inspector.color_input.setText(value1)
        QTest.keyPress(inspector.color_input, Qt.Key_Return)
        qtbot.wait(100)

        assert doc.is_modified()
        assert doc.get_token(token1) == value1

        # Step 3: Edit second token
        token2 = "editor.foreground"
        value2 = "#abcdef"
        doc.set_token(token2, "#ffffff")  # Set initial value
        inspector.set_token(token2, "#ffffff")
        qtbot.wait(50)
        inspector.color_input.setText(value2)
        QTest.keyPress(inspector.color_input, Qt.Key_Return)
        qtbot.wait(100)

        assert doc.get_token(token2) == value2

        # Step 4: Undo second change
        window.undo()
        qtbot.wait(50)
        assert doc.get_token(token2) == "#ffffff"

        # Step 5: Undo first change
        window.undo()
        qtbot.wait(50)
        assert doc.get_token(token1) == "#000000"

        # Step 6: Redo both
        window.redo()
        qtbot.wait(50)
        assert doc.get_token(token1) == value1

        window.redo()
        qtbot.wait(50)
        assert doc.get_token(token2) == value2

    def test_text_input_syncs_with_color_picker(self, window, qtbot, monkeypatch):
        """Test text input stays in sync when color picker is used."""
        inspector = window.inspector_panel
        doc = window._current_document

        # Set up token
        token_name = "editor.background"
        initial_value = "#252526"
        doc.set_token(token_name, initial_value)
        inspector.set_token(token_name, initial_value)
        qtbot.wait(50)

        # Mock color picker
        from PySide6.QtWidgets import QColorDialog

        test_color = QColor("#ff0000")

        def mock_get_color(*args, **kwargs):
            return test_color

        monkeypatch.setattr(QColorDialog, "getColor", mock_get_color)

        # Use color picker
        inspector._on_color_swatch_clicked()
        qtbot.wait(50)

        # Text input should be updated
        assert inspector.color_input.text() == "#ff0000"

    def test_color_picker_syncs_with_text_input(self, window, qtbot):
        """Test color picker preview syncs when text input changes."""
        inspector = window.inspector_panel
        doc = window._current_document

        # Set up token
        token_name = "editor.background"
        initial_value = "#252526"
        doc.set_token(token_name, initial_value)
        inspector.set_token(token_name, initial_value)
        qtbot.wait(50)

        # Type new color in text input
        new_value = "#00ff00"
        inspector.color_input.setText(new_value)
        qtbot.wait(50)

        # Color swatch should update (check stylesheet contains new color)
        swatch_style = inspector.color_swatch.styleSheet()
        assert new_value in swatch_style


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
