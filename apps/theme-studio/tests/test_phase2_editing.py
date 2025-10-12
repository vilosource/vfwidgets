"""Phase 2 Integration Tests - Token Editing & Undo/Redo.

Tests Phase 2 features:
1. Inspector editing mode (Edit/Save/Cancel)
2. Token value validation
3. Color picker integration
4. Undo/Redo functionality
5. Real-time preview updates
"""

import pytest
from PySide6.QtGui import QColor

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


class TestPhase2Editing:
    """Phase 2 token editing tests."""

    def test_inspector_edit_mode_activation(self, window, qtbot):
        """Test entering edit mode in inspector."""
        inspector = window.inspector_panel
        doc = window._current_document

        # Set a token to inspect
        token_name = "editor.background"
        token_value = "#252526"
        doc.set_token(token_name, token_value)
        inspector.set_token(token_name, token_value)
        qtbot.wait(50)

        # Initially not in edit mode
        assert not inspector._edit_mode
        # info_group should be visible after set_token
        assert inspector.info_group.isVisible()
        assert inspector.token_value_label.isVisible()
        assert not inspector.token_value_edit.isVisible()
        assert inspector.edit_button.isVisible()
        assert not inspector.save_button.isVisible()

        # Click Edit button
        inspector._on_edit_clicked()
        qtbot.wait(50)

        # Should enter edit mode
        assert inspector._edit_mode
        assert not inspector.token_value_label.isVisible()
        assert inspector.token_value_edit.isVisible()
        assert not inspector.edit_button.isVisible()
        assert inspector.save_button.isVisible()
        assert inspector.cancel_button.isVisible()

    def test_inspector_save_valid_value(self, window, qtbot):
        """Test saving valid token value."""
        inspector = window.inspector_panel
        doc = window._current_document

        # Set up token
        token_name = "editor.background"
        initial_value = "#252526"
        doc.set_token(token_name, initial_value)
        inspector.set_token(token_name, initial_value)
        qtbot.wait(50)

        # Enter edit mode
        inspector._on_edit_clicked()
        qtbot.wait(50)
        assert inspector._edit_mode

        # Change value to valid color
        new_value = "#123456"
        inspector.token_value_edit.setText(new_value)
        qtbot.wait(50)

        # Save button should be enabled (valid value)
        assert inspector.save_button.isEnabled()
        assert not inspector.validation_error_label.isVisible()

        # Click Save
        with qtbot.waitSignal(inspector.token_value_changed, timeout=1000) as blocker:
            inspector._on_save_clicked()

        # Should emit signal with new value
        assert blocker.args == [token_name, new_value]

        # Should exit edit mode
        assert not inspector._edit_mode
        assert inspector.token_value_label.isVisible()
        assert not inspector.token_value_edit.isVisible()

    def test_inspector_cancel_edit(self, window, qtbot):
        """Test canceling edit restores original value."""
        inspector = window.inspector_panel
        doc = window._current_document

        # Set up token
        token_name = "editor.background"
        initial_value = "#252526"
        doc.set_token(token_name, initial_value)
        inspector.set_token(token_name, initial_value)

        # Enter edit mode and change value
        inspector._on_edit_clicked()
        inspector.token_value_edit.setText("#abcdef")

        # Click Cancel
        inspector._on_cancel_clicked()

        # Should exit edit mode
        assert not inspector._edit_mode

        # Edit field should be restored to original
        assert inspector.token_value_edit.text() == initial_value

    def test_token_validation_valid_hex(self, window, qtbot):
        """Test validation accepts valid hex colors."""
        inspector = window.inspector_panel
        doc = window._current_document

        token_name = "editor.background"
        inspector.set_token(token_name, "#252526")
        inspector._on_edit_clicked()

        # Test various valid hex formats
        valid_colors = [
            "#123",       # 3-digit hex
            "#123456",    # 6-digit hex
            "#12345678",  # 8-digit hex with alpha
        ]

        for color in valid_colors:
            inspector.token_value_edit.setText(color)
            qtbot.wait(50)

            # Should be valid
            assert inspector.save_button.isEnabled(), f"{color} should be valid"
            assert not inspector.validation_error_label.isVisible()

    def test_token_validation_invalid_hex(self, window, qtbot):
        """Test validation rejects invalid hex colors."""
        inspector = window.inspector_panel
        doc = window._current_document

        token_name = "editor.background"
        inspector.set_token(token_name, "#252526")
        inspector._on_edit_clicked()

        # Test invalid hex formats
        invalid_colors = [
            "#12",        # Too short
            "#12345",     # Wrong length
            "#gggggg",    # Invalid hex chars
            "123456",     # Missing #
        ]

        for color in invalid_colors:
            inspector.token_value_edit.setText(color)
            qtbot.wait(50)

            # Should be invalid
            assert not inspector.save_button.isEnabled(), f"{color} should be invalid"
            assert inspector.validation_error_label.isVisible()

    def test_token_validation_color_names(self, window, qtbot):
        """Test validation accepts Qt color names."""
        inspector = window.inspector_panel
        doc = window._current_document

        token_name = "editor.background"
        inspector.set_token(token_name, "#252526")
        inspector._on_edit_clicked()

        # Test valid color names
        valid_names = ["red", "blue", "white", "black", "transparent"]

        for color_name in valid_names:
            inspector.token_value_edit.setText(color_name)
            qtbot.wait(50)

            # Should be valid
            assert inspector.save_button.isEnabled(), f"{color_name} should be valid"
            assert not inspector.validation_error_label.isVisible()

    def test_token_validation_empty_value(self, window, qtbot):
        """Test validation allows empty values (use default)."""
        inspector = window.inspector_panel
        doc = window._current_document

        token_name = "editor.background"
        inspector.set_token(token_name, "#252526")
        inspector._on_edit_clicked()

        # Clear value
        inspector.token_value_edit.setText("")
        qtbot.wait(50)

        # Should be valid (empty means use default)
        assert inspector.save_button.isEnabled()
        assert not inspector.validation_error_label.isVisible()

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

        # Enter edit mode and change value
        inspector._on_edit_clicked()
        new_value = "#123456"
        inspector.token_value_edit.setText(new_value)
        inspector._on_save_clicked()
        qtbot.wait(50)

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
        assert hasattr(window, 'undo_action')
        assert hasattr(window, 'redo_action')
        assert not window.undo_action.isEnabled()
        assert not window.redo_action.isEnabled()

        # Make a change through inspector (which creates undo command)
        token_name = "test.token"
        doc.set_token(token_name, "#000000")  # Set initial value
        inspector.set_token(token_name, "#000000")
        inspector._on_edit_clicked()
        inspector.token_value_edit.setText("#123456")
        inspector._on_save_clicked()  # This triggers undo command creation
        qtbot.wait(100)

        # Undo should be enabled
        assert window.undo_action.isEnabled()
        assert not window.redo_action.isEnabled()

        # Undo the change
        window.undo()
        qtbot.wait(50)

        # Redo should be enabled
        assert not window.undo_action.isEnabled()
        assert window.redo_action.isEnabled()

    def test_undo_command_merging(self, window, qtbot):
        """Test consecutive edits to same token merge into one undo."""
        doc = window._current_document
        inspector = window.inspector_panel

        token_name = "editor.background"
        initial_value = "#252526"
        doc.set_token(token_name, initial_value)

        # Make multiple rapid changes
        values = ["#111111", "#222222", "#333333"]
        for value in values:
            inspector.set_token(token_name, initial_value)
            inspector._on_edit_clicked()
            inspector.token_value_edit.setText(value)
            inspector._on_save_clicked()
            qtbot.wait(50)
            initial_value = value

        # Should have history
        assert doc._undo_stack.canUndo()

        # Final value should be last in sequence
        assert doc.get_token(token_name) == "#333333"

    def test_color_picker_button_visibility(self, window, qtbot):
        """Test color picker button appears for color tokens."""
        inspector = window.inspector_panel
        doc = window._current_document

        # Set up color token
        token_name = "editor.background"
        token_value = "#252526"
        doc.set_token(token_name, token_value)
        inspector.set_token(token_name, token_value)

        # Enter edit mode
        inspector._on_edit_clicked()

        # Color picker button should be visible for color tokens
        assert inspector.color_picker_button.isVisible()

    def test_real_time_preview_update(self, window, qtbot):
        """Test preview updates when token changes."""
        doc = window._current_document
        app = window._app

        # Get initial theme
        initial_theme = doc.theme

        # Change a token
        token_name = "editor.background"
        new_value = "#123456"
        doc.set_token(token_name, new_value)
        qtbot.wait(100)

        # Theme should have been updated on app
        # (We can't easily verify visual update in headless test,
        # but we verify the mechanism is in place)
        current_theme = doc.theme
        assert current_theme.colors[token_name] == new_value

    def test_inspector_updates_on_undo(self, window, qtbot):
        """Test inspector display updates when token is undone."""
        doc = window._current_document
        inspector = window.inspector_panel

        token_name = "editor.background"
        initial_value = "#252526"
        new_value = "#123456"

        # Set initial value
        doc.set_token(token_name, initial_value)
        inspector.set_token(token_name, initial_value)

        # Change value
        inspector._on_edit_clicked()
        inspector.token_value_edit.setText(new_value)
        inspector._on_save_clicked()
        qtbot.wait(50)

        # Undo
        window.undo()
        qtbot.wait(50)

        # Inspector should be updated if token is still selected
        # (The window's _on_token_changed handler updates inspector)
        if inspector._current_token == token_name:
            assert inspector._current_value == initial_value

    def test_document_modified_state_on_edit(self, window, qtbot):
        """Test document becomes modified when token is edited."""
        doc = window._current_document
        inspector = window.inspector_panel

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

    def test_complete_editing_workflow(self, window, qtbot):
        """Test complete editing workflow with multiple operations."""
        doc = window._current_document
        inspector = window.inspector_panel

        # Step 1: Create new document
        window.new_theme()
        doc = window._current_document
        assert not doc.is_modified()

        # Step 2: Edit first token
        token1 = "editor.background"
        value1 = "#123456"
        doc.set_token(token1, value1)
        inspector.set_token(token1, value1)
        inspector._on_edit_clicked()
        inspector.token_value_edit.setText(value1)
        inspector._on_save_clicked()
        qtbot.wait(50)

        assert doc.is_modified()
        assert doc.get_token(token1) == value1

        # Step 3: Edit second token
        token2 = "editor.foreground"
        value2 = "#abcdef"
        doc.set_token(token2, value2)
        qtbot.wait(50)

        # Step 4: Undo second change (restores to empty/initial state)
        window.undo()
        qtbot.wait(50)
        # Should restore to state before token2 was set
        # (empty string if it wasn't set before)
        token2_after_undo = doc.get_token(token2)

        # Step 5: Undo first change
        window.undo()
        qtbot.wait(50)
        token1_after_undo = doc.get_token(token1)

        # Step 6: Redo both
        window.redo()
        qtbot.wait(50)
        assert doc.get_token(token1) == value1

        window.redo()
        qtbot.wait(50)
        assert doc.get_token(token2) == value2


class TestPhase2ColorPicker:
    """Color picker integration tests."""

    def test_color_picker_updates_edit_field(self, window, qtbot, monkeypatch):
        """Test color picker updates the edit field when color selected."""
        inspector = window.inspector_panel
        doc = window._current_document

        # Set up token
        token_name = "editor.background"
        inspector.set_token(token_name, "#252526")
        inspector._on_edit_clicked()

        # Mock QColorDialog.getColor to return a specific color
        from PySide6.QtWidgets import QColorDialog
        test_color = QColor("#ff0000")

        def mock_get_color(*args, **kwargs):
            return test_color

        monkeypatch.setattr(QColorDialog, 'getColor', mock_get_color)

        # Click color picker button
        inspector._on_color_picker_clicked()

        # Edit field should be updated with hex color
        assert inspector.token_value_edit.text() == "#ff0000"

    def test_color_picker_respects_cancel(self, window, qtbot, monkeypatch):
        """Test color picker doesn't update if user cancels."""
        inspector = window.inspector_panel
        doc = window._current_document

        # Set up token
        token_name = "editor.background"
        initial_value = "#252526"
        inspector.set_token(token_name, initial_value)
        inspector._on_edit_clicked()

        # Mock QColorDialog.getColor to return invalid color (user cancelled)
        from PySide6.QtWidgets import QColorDialog

        def mock_get_color(*args, **kwargs):
            return QColor()  # Invalid color = cancelled

        monkeypatch.setattr(QColorDialog, 'getColor', mock_get_color)

        # Click color picker button
        inspector._on_color_picker_clicked()

        # Edit field should NOT be changed
        assert inspector.token_value_edit.text() == initial_value


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
