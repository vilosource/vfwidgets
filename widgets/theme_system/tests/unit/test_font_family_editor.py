"""Unit tests for FontFamilyListEditor.

This module tests Phase 5 of the font support implementation:
- Font family list editing with drag-drop
- Add/remove fonts via system font picker
- Font availability indicators
- Validation feedback in UI
- Signal emission on family list changes
- Integration with theme editor

Based on: widgets/theme_system/docs/fonts-theme-studio-integration-PLAN.md
Phase 5 - Font Family List Editing
"""


from vfwidgets_theme.core.theme import Theme
from vfwidgets_theme.widgets.font_family_editor import FontFamilyListEditor


class TestFontFamilyListEditor:
    """Test suite for FontFamilyListEditor."""

    def test_widget_initialization(self, qtbot):
        """Widget should initialize without errors."""
        editor = FontFamilyListEditor()
        qtbot.addWidget(editor)

        assert editor._current_token is None
        assert editor._current_theme is None
        assert not editor._updating

    def test_set_token_displays_families(self, qtbot):
        """Setting token should display font families in list."""
        theme = Theme(
            name="test",
            fonts={"terminal.fontFamily": ["JetBrains Mono", "Consolas", "monospace"]},
        )
        editor = FontFamilyListEditor()
        qtbot.addWidget(editor)

        families = ["JetBrains Mono", "Consolas", "monospace"]
        editor.set_token("terminal.fontFamily", families, theme)

        # Verify list has 3 items
        assert editor._family_list.count() == 3

        # Verify families are displayed (items contain indicator + family name)
        assert "JetBrains Mono" in editor._family_list.item(0).text()
        assert "Consolas" in editor._family_list.item(1).text()
        assert "monospace" in editor._family_list.item(2).text()

        assert editor.get_current_token() == "terminal.fontFamily"

    def test_get_current_families(self, qtbot):
        """get_current_families should return current family list."""
        theme = Theme(
            name="test",
            fonts={"fonts.mono": ["Fira Code", "monospace"]},
        )
        editor = FontFamilyListEditor()
        qtbot.addWidget(editor)

        families = ["Fira Code", "monospace"]
        editor.set_token("fonts.mono", families, theme)

        current = editor.get_current_families()
        assert current == families

    def test_font_availability_indicators(self, qtbot):
        """Font availability should be indicated with checkmarks/X."""
        theme = Theme(
            name="test",
            fonts={"fonts.mono": ["NonExistentFont123", "monospace"]},
        )
        editor = FontFamilyListEditor()
        qtbot.addWidget(editor)

        families = ["NonExistentFont123", "monospace"]
        editor.set_token("fonts.mono", families, theme)

        # Check that items have indicators (✓ or ✗)
        item0_text = editor._family_list.item(0).text()
        item1_text = editor._family_list.item(1).text()

        # Items should contain either ✓ or ✗
        assert "✓" in item0_text or "✗" in item0_text
        assert "✓" in item1_text or "✗" in item1_text

    def test_remove_button_disabled_without_selection(self, qtbot):
        """Remove button should be disabled without selection."""
        theme = Theme(name="test", fonts={"fonts.mono": ["monospace"]})
        editor = FontFamilyListEditor()
        qtbot.addWidget(editor)

        editor.set_token("fonts.mono", ["monospace"], theme)

        # No selection - remove button should be disabled
        assert not editor._remove_button.isEnabled()

    def test_remove_button_enabled_with_selection(self, qtbot):
        """Remove button should be enabled when item is selected."""
        theme = Theme(
            name="test",
            fonts={"fonts.mono": ["Consolas", "monospace"]},
        )
        editor = FontFamilyListEditor()
        qtbot.addWidget(editor)

        editor.set_token("fonts.mono", ["Consolas", "monospace"], theme)

        # Select first item
        editor._family_list.setCurrentRow(0)

        # Remove button should be enabled
        assert editor._remove_button.isEnabled()

    def test_cannot_remove_last_generic_family(self, qtbot):
        """Should not allow removing the last generic family."""
        theme = Theme(name="test", fonts={"fonts.mono": ["monospace"]})
        editor = FontFamilyListEditor()
        qtbot.addWidget(editor)

        editor.set_token("fonts.mono", ["monospace"], theme)

        # Select the only generic family
        editor._family_list.setCurrentRow(0)

        # Try to remove it
        initial_count = editor._family_list.count()
        editor._on_remove_font()

        # Should still have the same count (removal blocked)
        assert editor._family_list.count() == initial_count

    def test_can_remove_non_last_font(self, qtbot):
        """Should allow removing a non-generic font."""
        theme = Theme(
            name="test",
            fonts={"terminal.fontFamily": ["Consolas", "Courier New", "monospace"]},
        )
        editor = FontFamilyListEditor()
        qtbot.addWidget(editor)

        families = ["Consolas", "Courier New", "monospace"]
        editor.set_token("terminal.fontFamily", families, theme)

        # Select "Consolas" (index 0)
        editor._family_list.setCurrentRow(0)

        # Count before
        initial_count = editor._family_list.count()

        # Should emit families_changed signal
        with qtbot.waitSignal(editor.families_changed, timeout=1000) as blocker:
            editor._on_remove_font()

        # Should have one less item
        assert editor._family_list.count() == initial_count - 1

        # Signal should be emitted with new list
        assert blocker.args[0] == "terminal.fontFamily"
        assert "Consolas" not in blocker.args[1]
        assert "Courier New" in blocker.args[1]
        assert "monospace" in blocker.args[1]

    def test_remove_specific_font(self, qtbot):
        """Removing a specific font should work."""
        theme = Theme(
            name="test",
            fonts={"terminal.fontFamily": ["Arial", "Helvetica", "sans-serif"]},
        )
        editor = FontFamilyListEditor()
        qtbot.addWidget(editor)

        families = ["Arial", "Helvetica", "sans-serif"]
        editor.set_token("terminal.fontFamily", families, theme)

        # Select "Helvetica" (index 1)
        editor._family_list.setCurrentRow(1)

        with qtbot.waitSignal(editor.families_changed, timeout=1000) as blocker:
            editor._on_remove_font()

        # Verify "Helvetica" was removed
        new_families = blocker.args[1]
        assert "Helvetica" not in new_families
        assert "Arial" in new_families
        assert "sans-serif" in new_families

    def test_updating_flag_prevents_signal_loop(self, qtbot):
        """_updating flag should prevent signal emission during setup."""
        theme = Theme(name="test", fonts={"fonts.mono": ["Consolas", "monospace"]})
        editor = FontFamilyListEditor()
        qtbot.addWidget(editor)

        # No signal should be emitted during set_token
        with qtbot.assertNotEmitted(editor.families_changed):
            editor.set_token("fonts.mono", ["Consolas", "monospace"], theme)

    def test_token_label_updates(self, qtbot):
        """Token label should show current token path."""
        theme = Theme(name="test", fonts={"terminal.fontFamily": ["monospace"]})
        editor = FontFamilyListEditor()
        qtbot.addWidget(editor)

        editor.set_token("terminal.fontFamily", ["monospace"], theme)

        assert "terminal.fontFamily" in editor._token_label.text()

    def test_is_last_generic_family_detection(self, qtbot):
        """_is_last_generic_family should correctly detect last generic."""
        editor = FontFamilyListEditor()
        qtbot.addWidget(editor)

        # Case 1: Last generic family
        families1 = ["Consolas", "monospace"]
        assert editor._is_last_generic_family("monospace", families1)

        # Case 2: Not last (multiple generics)
        families2 = ["monospace", "sans-serif"]
        assert not editor._is_last_generic_family("monospace", families2)

        # Case 3: Not generic at all
        families3 = ["Consolas", "monospace"]
        assert not editor._is_last_generic_family("Consolas", families3)

    def test_is_family_in_list(self, qtbot):
        """_is_family_in_list should detect duplicates."""
        theme = Theme(name="test", fonts={"fonts.mono": ["Consolas", "monospace"]})
        editor = FontFamilyListEditor()
        qtbot.addWidget(editor)

        editor.set_token("fonts.mono", ["Consolas", "monospace"], theme)

        assert editor._is_family_in_list("Consolas")
        assert editor._is_family_in_list("monospace")
        assert not editor._is_family_in_list("Arial")

    def test_clear_error(self, qtbot):
        """_clear_error should hide error label."""
        editor = FontFamilyListEditor()
        qtbot.addWidget(editor)

        # Show error first
        editor._show_error("Test error")
        assert len(editor._error_label.text()) > 0

        # Clear error
        editor._clear_error()
        assert len(editor._error_label.text()) == 0

    def test_get_current_token(self, qtbot):
        """get_current_token should return current token path."""
        theme = Theme(name="test", fonts={"fonts.mono": ["monospace"]})
        editor = FontFamilyListEditor()
        qtbot.addWidget(editor)

        editor.set_token("fonts.mono", ["monospace"], theme)

        assert editor.get_current_token() == "fonts.mono"

    def test_multiple_token_switches(self, qtbot):
        """Should handle switching between different font family tokens."""
        theme = Theme(
            name="test",
            fonts={
                "terminal.fontFamily": ["Consolas", "monospace"],
                "fonts.mono": ["Fira Code", "monospace"],
                "fonts.ui": ["Segoe UI", "sans-serif"],
            },
        )
        editor = FontFamilyListEditor()
        qtbot.addWidget(editor)

        # Switch to terminal.fontFamily
        editor.set_token(
            "terminal.fontFamily",
            ["Consolas", "monospace"],
            theme,
        )
        assert editor.get_current_token() == "terminal.fontFamily"
        assert editor._family_list.count() == 2

        # Switch to fonts.mono
        editor.set_token("fonts.mono", ["Fira Code", "monospace"], theme)
        assert editor.get_current_token() == "fonts.mono"
        assert editor._family_list.count() == 2

        # Switch to fonts.ui
        editor.set_token("fonts.ui", ["Segoe UI", "sans-serif"], theme)
        assert editor.get_current_token() == "fonts.ui"
        assert editor._family_list.count() == 2

    def test_validation_error_handling(self, qtbot):
        """Invalid font family lists should show error."""
        theme = Theme(name="test", fonts={"fonts.mono": ["monospace"]})
        editor = FontFamilyListEditor()
        qtbot.addWidget(editor)

        editor.set_token("fonts.mono", ["monospace"], theme)

        # Try to validate empty list (should fail)
        editor._validate_and_emit([])

        # Wait for validation
        qtbot.wait(100)

        # Verify error message shown (empty list should fail validation)
        assert len(editor._error_label.text()) > 0

    def test_generic_families_constant(self, qtbot):
        """GENERIC_FAMILIES should contain all CSS generic families."""
        expected_generics = {"monospace", "sans-serif", "serif", "cursive", "fantasy"}

        assert FontFamilyListEditor.GENERIC_FAMILIES == expected_generics

    def test_drag_drop_enabled(self, qtbot):
        """List widget should have drag-drop enabled."""
        editor = FontFamilyListEditor()
        qtbot.addWidget(editor)

        from PySide6.QtWidgets import QListWidget

        assert (
            editor._family_list.dragDropMode()
            == QListWidget.DragDropMode.InternalMove
        )
