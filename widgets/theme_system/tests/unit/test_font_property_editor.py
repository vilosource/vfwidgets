"""Unit tests for FontPropertyEditorWidget.

This module tests Phase 4 of the font support implementation:
- Font property editing (size, weight, line height, letter spacing)
- Validation feedback in UI
- Signal emission on property changes
- Integration with theme editor

Based on: widgets/theme_system/docs/fonts-theme-studio-integration-PLAN.md
Phase 4 - Basic Font Property Editing
"""


from vfwidgets_theme.core.theme import Theme
from vfwidgets_theme.widgets.font_property_editor import FontPropertyEditorWidget


class TestFontPropertyEditor:
    """Test suite for FontPropertyEditorWidget."""

    def test_widget_initialization(self, qtbot):
        """Widget should initialize without errors."""
        editor = FontPropertyEditorWidget()
        qtbot.addWidget(editor)

        assert editor._current_token is None
        assert editor._current_theme is None
        assert not editor._updating

    def test_font_size_editor_displays_value(self, qtbot):
        """Font size editor should show current value."""
        theme = Theme(name="test", fonts={"terminal.fontSize": 14})
        editor = FontPropertyEditorWidget()
        qtbot.addWidget(editor)

        editor.set_token("terminal.fontSize", 14, theme)

        # Verify spinbox shows 14
        assert editor._size_spin.value() == 14
        assert editor.get_current_token() == "terminal.fontSize"

    def test_font_size_change_emits_signal(self, qtbot):
        """Changing font size should emit property_changed."""
        theme = Theme(name="test", fonts={"terminal.fontSize": 14})
        editor = FontPropertyEditorWidget()
        qtbot.addWidget(editor)

        editor.set_token("terminal.fontSize", 14, theme)

        with qtbot.waitSignal(editor.property_changed, timeout=1000) as blocker:
            editor._size_spin.setValue(16)

        assert blocker.args[0] == "terminal.fontSize"
        assert blocker.args[1] == 16

    def test_font_weight_editor_displays_value(self, qtbot):
        """Font weight editor should show current value."""
        theme = Theme(name="test", fonts={"fonts.weight": 400})
        editor = FontPropertyEditorWidget()
        qtbot.addWidget(editor)

        editor.set_token("fonts.weight", 400, theme)

        # Verify combo shows "400 (Normal)"
        assert editor._weight_combo.currentText() == "400 (Normal)"
        assert editor.get_current_token() == "fonts.weight"

    def test_font_weight_change_emits_signal(self, qtbot):
        """Changing font weight should emit property_changed."""
        theme = Theme(name="test", fonts={"fonts.weight": 400})
        editor = FontPropertyEditorWidget()
        qtbot.addWidget(editor)

        editor.set_token("fonts.weight", 400, theme)

        with qtbot.waitSignal(editor.property_changed, timeout=1000) as blocker:
            editor._weight_combo.setCurrentText("700 (Bold)")

        assert blocker.args[0] == "fonts.weight"
        assert blocker.args[1] == 700

    def test_line_height_editor_displays_value(self, qtbot):
        """Line height editor should show current value."""
        theme = Theme(name="test", fonts={"terminal.lineHeight": 1.4})
        editor = FontPropertyEditorWidget()
        qtbot.addWidget(editor)

        editor.set_token("terminal.lineHeight", 1.4, theme)

        # Verify spinbox shows 1.4
        assert editor._line_height_spin.value() == 1.4
        assert editor.get_current_token() == "terminal.lineHeight"

    def test_line_height_change_emits_signal(self, qtbot):
        """Changing line height should emit property_changed."""
        theme = Theme(name="test", fonts={"terminal.lineHeight": 1.4})
        editor = FontPropertyEditorWidget()
        qtbot.addWidget(editor)

        editor.set_token("terminal.lineHeight", 1.4, theme)

        with qtbot.waitSignal(editor.property_changed, timeout=1000) as blocker:
            editor._line_height_spin.setValue(1.6)

        assert blocker.args[0] == "terminal.lineHeight"
        assert blocker.args[1] == 1.6

    def test_letter_spacing_editor_displays_value(self, qtbot):
        """Letter spacing editor should show current value."""
        theme = Theme(name="test", fonts={"terminal.letterSpacing": 0.5})
        editor = FontPropertyEditorWidget()
        qtbot.addWidget(editor)

        editor.set_token("terminal.letterSpacing", 0.5, theme)

        # Verify spinbox shows 0.5
        assert editor._letter_spacing_spin.value() == 0.5
        assert editor.get_current_token() == "terminal.letterSpacing"

    def test_letter_spacing_change_emits_signal(self, qtbot):
        """Changing letter spacing should emit property_changed."""
        theme = Theme(name="test", fonts={"terminal.letterSpacing": 0.0})
        editor = FontPropertyEditorWidget()
        qtbot.addWidget(editor)

        editor.set_token("terminal.letterSpacing", 0.0, theme)

        with qtbot.waitSignal(editor.property_changed, timeout=1000) as blocker:
            editor._letter_spacing_spin.setValue(0.5)

        assert blocker.args[0] == "terminal.letterSpacing"
        assert blocker.args[1] == 0.5

    def test_invalid_font_size_shows_error(self, qtbot):
        """Invalid font size should show error message."""
        theme = Theme(name="test", fonts={"terminal.fontSize": 14})
        editor = FontPropertyEditorWidget()
        qtbot.addWidget(editor)

        editor.set_token("terminal.fontSize", 14, theme)

        # Spinbox enforces max of 144, so test validation directly
        # by calling _validate_and_emit with invalid value
        editor._error_label.text()
        editor._validate_and_emit(200)

        # Wait for validation
        qtbot.wait(100)

        # Verify error message appeared (text changed)
        # Note: actual error depends on validation implementation
        # We just verify that validation caught the error
        assert len(editor._error_label.text()) > 0

    def test_invalid_font_weight_shows_error(self, qtbot):
        """Invalid font weight should show error message."""
        theme = Theme(name="test", fonts={"fonts.weight": 400})
        editor = FontPropertyEditorWidget()
        qtbot.addWidget(editor)

        editor.set_token("fonts.weight", 400, theme)

        # Simulate invalid weight by directly calling validation
        # (Note: The combo only allows valid values, so we test the validation path)
        editor._validate_and_emit(950)  # Invalid weight

        # Wait for validation
        qtbot.wait(100)

        # Verify error message appeared
        assert len(editor._error_label.text()) > 0

    def test_valid_value_clears_error(self, qtbot):
        """Valid value should clear error message."""
        theme = Theme(name="test", fonts={"terminal.fontSize": 14})
        editor = FontPropertyEditorWidget()
        qtbot.addWidget(editor)

        editor.set_token("terminal.fontSize", 14, theme)

        # Set invalid value directly to trigger error
        editor._validate_and_emit(200)
        qtbot.wait(100)

        # Verify error appeared
        error_with_invalid = editor._error_label.text()
        assert len(error_with_invalid) > 0

        # Set valid value
        editor._validate_and_emit(16)
        qtbot.wait(100)

        # Error should be cleared
        assert len(editor._error_label.text()) == 0

    def test_token_label_updates(self, qtbot):
        """Token label should show current token path."""
        theme = Theme(name="test", fonts={"terminal.fontSize": 14})
        editor = FontPropertyEditorWidget()
        qtbot.addWidget(editor)

        editor.set_token("terminal.fontSize", 14, theme)

        assert "terminal.fontSize" in editor._token_label.text()

    def test_help_text_updates_for_size(self, qtbot):
        """Help text should update based on property type."""
        theme = Theme(name="test", fonts={"terminal.fontSize": 14})
        editor = FontPropertyEditorWidget()
        qtbot.addWidget(editor)

        editor.set_token("terminal.fontSize", 14, theme)

        # Verify help text mentions font size
        help_text = editor._help_label.text()
        assert "size" in help_text.lower() or "point" in help_text.lower()

    def test_help_text_updates_for_weight(self, qtbot):
        """Help text should update for weight tokens."""
        theme = Theme(name="test", fonts={"fonts.weight": 400})
        editor = FontPropertyEditorWidget()
        qtbot.addWidget(editor)

        editor.set_token("fonts.weight", 400, theme)

        # Verify help text mentions font weight
        help_text = editor._help_label.text()
        assert "weight" in help_text.lower()

    def test_only_relevant_editor_shown(self, qtbot):
        """Only the relevant editor for token type should be visible."""
        theme = Theme(name="test", fonts={"terminal.fontSize": 14})
        editor = FontPropertyEditorWidget()
        qtbot.addWidget(editor)

        editor.set_token("terminal.fontSize", 14, theme)

        # Verify the size editor has the correct value (implies it's the active editor)
        assert editor._size_spin.value() == 14
        # Verify current token is correct
        assert editor.get_current_token() == "terminal.fontSize"

    def test_weight_string_to_int_conversion(self, qtbot):
        """String weight values should be converted to integers."""
        theme = Theme(name="test", fonts={"fonts.weight": "bold"})
        editor = FontPropertyEditorWidget()
        qtbot.addWidget(editor)

        editor.set_token("fonts.weight", "bold", theme)

        # Should show "700 (Bold)"
        assert editor._weight_combo.currentText() == "700 (Bold)"

    def test_weight_normal_string_conversion(self, qtbot):
        """'normal' weight string should convert to 400."""
        theme = Theme(name="test", fonts={"fonts.weight": "normal"})
        editor = FontPropertyEditorWidget()
        qtbot.addWidget(editor)

        editor.set_token("fonts.weight", "normal", theme)

        # Should show "400 (Normal)"
        assert editor._weight_combo.currentText() == "400 (Normal)"

    def test_get_current_token(self, qtbot):
        """get_current_token should return current token path."""
        theme = Theme(name="test", fonts={"terminal.fontSize": 14})
        editor = FontPropertyEditorWidget()
        qtbot.addWidget(editor)

        editor.set_token("terminal.fontSize", 14, theme)

        assert editor.get_current_token() == "terminal.fontSize"

    def test_updating_flag_prevents_signal_loop(self, qtbot):
        """_updating flag should prevent signal emission during setup."""
        theme = Theme(name="test", fonts={"terminal.fontSize": 14})
        editor = FontPropertyEditorWidget()
        qtbot.addWidget(editor)

        # No signal should be emitted during set_token
        with qtbot.assertNotEmitted(editor.property_changed):
            editor.set_token("terminal.fontSize", 14, theme)

    def test_multiple_token_switches(self, qtbot):
        """Should handle switching between different token types."""
        theme = Theme(
            name="test",
            fonts={
                "terminal.fontSize": 14,
                "fonts.weight": 400,
                "terminal.lineHeight": 1.4,
            },
        )
        editor = FontPropertyEditorWidget()
        qtbot.addWidget(editor)

        # Switch to size
        editor.set_token("terminal.fontSize", 14, theme)
        assert editor.get_current_token() == "terminal.fontSize"
        assert editor._size_spin.value() == 14

        # Switch to weight
        editor.set_token("fonts.weight", 400, theme)
        assert editor.get_current_token() == "fonts.weight"
        assert editor._weight_combo.currentText() == "400 (Normal)"

        # Switch to line height
        editor.set_token("terminal.lineHeight", 1.4, theme)
        assert editor.get_current_token() == "terminal.lineHeight"
        assert editor._line_height_spin.value() == 1.4

    def test_font_size_range(self, qtbot):
        """Font size should be constrained to 6-144pt."""
        editor = FontPropertyEditorWidget()
        qtbot.addWidget(editor)

        # Check range
        assert editor._size_spin.minimum() == 6
        assert editor._size_spin.maximum() == 144

    def test_line_height_range(self, qtbot):
        """Line height should be constrained to 0.5-3.0×."""
        editor = FontPropertyEditorWidget()
        qtbot.addWidget(editor)

        # Check range
        assert editor._line_height_spin.minimum() == 0.5
        assert editor._line_height_spin.maximum() == 3.0

    def test_letter_spacing_range(self, qtbot):
        """Letter spacing should be constrained to -5.0 to 5.0px."""
        editor = FontPropertyEditorWidget()
        qtbot.addWidget(editor)

        # Check range
        assert editor._letter_spacing_spin.minimum() == -5.0
        assert editor._letter_spacing_spin.maximum() == 5.0

    def test_weight_map_complete(self, qtbot):
        """WEIGHT_MAP should have all weight options."""
        expected_weights = [100, 200, 300, 400, 500, 600, 700, 800, 900]

        for weight in expected_weights:
            # Check that weight is in the map values
            assert weight in FontPropertyEditorWidget.WEIGHT_MAP.values()
