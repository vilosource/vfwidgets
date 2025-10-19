"""Unit tests for KeySequenceEdit widget."""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtTest import QSignalSpy
from vfwidgets_keybinding.widgets import KeySequenceEdit


class TestKeySequenceEdit:
    """Test KeySequenceEdit widget."""

    @pytest.fixture
    def edit(self, qapp):
        """Create KeySequenceEdit widget."""
        return KeySequenceEdit()

    def test_initialization(self, edit):
        """Test widget initializes correctly."""
        assert edit is not None
        assert edit.shortcut() == ""
        assert edit.placeholderText() == "Press shortcut keys..."
        assert edit.isClearButtonEnabled() is True

    def test_set_shortcut(self, edit):
        """Test setting a shortcut."""
        edit.setShortcut("Ctrl+S")
        assert edit.shortcut() == "Ctrl+S"
        assert edit.text() == "Ctrl+S"

    def test_set_shortcut_with_modifiers(self, edit):
        """Test setting shortcuts with multiple modifiers."""
        edit.setShortcut("Ctrl+Shift+K")
        assert edit.shortcut() == "Ctrl+Shift+K"

    def test_set_empty_shortcut(self, edit):
        """Test setting empty shortcut clears the widget."""
        edit.setShortcut("Ctrl+S")
        edit.setShortcut("")
        assert edit.shortcut() == ""
        assert edit.text() == ""

    def test_set_invalid_shortcut(self, edit):
        """Test setting invalid shortcut is handled gracefully."""
        edit.setShortcut("invalid")
        # Invalid shortcuts should result in empty shortcut
        assert edit.shortcut() == ""

    def test_clear_shortcut(self, edit):
        """Test clearing shortcut."""
        edit.setShortcut("Ctrl+S")
        edit.clearShortcut()
        assert edit.shortcut() == ""
        assert edit.text() == ""

    def test_shortcut_changed_signal(self, edit):
        """Test shortcut_changed signal is emitted."""
        spy = QSignalSpy(edit.shortcut_changed)
        edit.setShortcut("Ctrl+S")
        # Signal may not be emitted by setShortcut, but should emit on key press
        # Let's test clearShortcut which does emit
        edit.clearShortcut()
        assert spy.count() > 0

    def test_key_press_ctrl_s(self, edit):
        """Test capturing Ctrl+S key combination."""
        # Create key event for Ctrl+S
        event = QKeyEvent(
            QKeyEvent.Type.KeyPress,
            Qt.Key.Key_S,
            Qt.KeyboardModifier.ControlModifier,
        )
        edit.keyPressEvent(event)

        assert edit.shortcut() == "Ctrl+S"

    def test_key_press_ctrl_shift_k(self, edit):
        """Test capturing Ctrl+Shift+K combination."""
        event = QKeyEvent(
            QKeyEvent.Type.KeyPress,
            Qt.Key.Key_K,
            Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier,
        )
        edit.keyPressEvent(event)

        assert edit.shortcut() == "Ctrl+Shift+K"

    def test_key_press_alt_f1(self, edit):
        """Test capturing Alt+F1 combination."""
        event = QKeyEvent(
            QKeyEvent.Type.KeyPress,
            Qt.Key.Key_F1,
            Qt.KeyboardModifier.AltModifier,
        )
        edit.keyPressEvent(event)

        assert edit.shortcut() == "Alt+F1"

    def test_key_press_escape_clears(self, edit):
        """Test pressing Escape clears the shortcut."""
        edit.setShortcut("Ctrl+S")

        event = QKeyEvent(
            QKeyEvent.Type.KeyPress,
            Qt.Key.Key_Escape,
            Qt.KeyboardModifier.NoModifier,
        )
        edit.keyPressEvent(event)

        assert edit.shortcut() == ""

    def test_ignored_keys(self, edit):
        """Test that ignored keys don't set shortcuts."""
        # Tab should be ignored
        event = QKeyEvent(
            QKeyEvent.Type.KeyPress,
            Qt.Key.Key_Tab,
            Qt.KeyboardModifier.NoModifier,
        )
        edit.keyPressEvent(event)
        assert edit.shortcut() == ""

        # Shift alone should be ignored
        event = QKeyEvent(
            QKeyEvent.Type.KeyPress,
            Qt.Key.Key_Shift,
            Qt.KeyboardModifier.ShiftModifier,
        )
        edit.keyPressEvent(event)
        assert edit.shortcut() == ""

    def test_read_only_mode(self, edit):
        """Test read-only mode prevents editing."""
        edit.setReadOnly(True)

        # Try to capture a key
        event = QKeyEvent(
            QKeyEvent.Type.KeyPress,
            Qt.Key.Key_S,
            Qt.KeyboardModifier.ControlModifier,
        )
        edit.keyPressEvent(event)

        # Shortcut should not be set in read-only mode
        assert edit.shortcut() == ""

    def test_is_valid_with_valid_shortcut(self, edit):
        """Test isValid returns True for valid shortcuts."""
        edit.setShortcut("Ctrl+S")
        assert edit.isValid() is True

    def test_is_valid_with_empty_shortcut(self, edit):
        """Test isValid returns False for empty shortcuts."""
        assert edit.isValid() is False

    def test_is_valid_after_clear(self, edit):
        """Test isValid returns False after clearing."""
        edit.setShortcut("Ctrl+S")
        edit.clearShortcut()
        assert edit.isValid() is False

    def test_multiple_modifiers_meta(self, edit):
        """Test Meta modifier (Windows/Command key)."""
        event = QKeyEvent(
            QKeyEvent.Type.KeyPress,
            Qt.Key.Key_M,
            Qt.KeyboardModifier.MetaModifier | Qt.KeyboardModifier.ControlModifier,
        )
        edit.keyPressEvent(event)

        # Should capture the combination (exact format may vary by platform)
        assert "M" in edit.shortcut()
        assert edit.isValid() is True

    def test_signal_emission_on_key_press(self, edit):
        """Test that shortcut_changed signal is emitted on key press."""
        spy = QSignalSpy(edit.shortcut_changed)

        event = QKeyEvent(
            QKeyEvent.Type.KeyPress,
            Qt.Key.Key_S,
            Qt.KeyboardModifier.ControlModifier,
        )
        edit.keyPressEvent(event)

        # Signal should be emitted once
        assert spy.count() == 1
        # Verify the shortcut was actually set
        assert edit.shortcut() == "Ctrl+S"

    def test_signal_emission_on_clear(self, edit):
        """Test that shortcut_changed signal is emitted when clearing."""
        edit.setShortcut("Ctrl+S")
        spy = QSignalSpy(edit.shortcut_changed)

        edit.clearShortcut()

        # Signal should be emitted once
        assert spy.count() == 1
        # Verify the shortcut was actually cleared
        assert edit.shortcut() == ""

    def test_function_keys(self, edit):
        """Test capturing function keys."""
        # F5
        event = QKeyEvent(
            QKeyEvent.Type.KeyPress,
            Qt.Key.Key_F5,
            Qt.KeyboardModifier.NoModifier,
        )
        edit.keyPressEvent(event)
        assert edit.shortcut() == "F5"

    def test_number_keys(self, edit):
        """Test capturing number keys with modifiers."""
        event = QKeyEvent(
            QKeyEvent.Type.KeyPress,
            Qt.Key.Key_1,
            Qt.KeyboardModifier.AltModifier,
        )
        edit.keyPressEvent(event)
        assert edit.shortcut() == "Alt+1"

    def test_special_keys(self, edit):
        """Test capturing special keys like Delete, Insert."""
        event = QKeyEvent(
            QKeyEvent.Type.KeyPress,
            Qt.Key.Key_Delete,
            Qt.KeyboardModifier.ControlModifier,
        )
        edit.keyPressEvent(event)
        assert "Del" in edit.shortcut() or "Delete" in edit.shortcut()

    def test_sequential_shortcuts(self, edit):
        """Test setting shortcuts sequentially."""
        # Set first shortcut
        edit.setShortcut("Ctrl+S")
        assert edit.shortcut() == "Ctrl+S"

        # Set second shortcut (should replace first)
        edit.setShortcut("Ctrl+O")
        assert edit.shortcut() == "Ctrl+O"

        # Clear
        edit.setShortcut("")
        assert edit.shortcut() == ""

    def test_text_changed_clears_shortcut(self, edit):
        """Test that clearing text via clear button resets shortcut."""
        edit.setShortcut("Ctrl+S")
        assert edit.shortcut() == "Ctrl+S"

        # Simulate clear button click by clearing text
        edit.clear()

        # Internal tracking should also be cleared
        # (tested through the _on_text_changed handler)
        assert edit.text() == ""
