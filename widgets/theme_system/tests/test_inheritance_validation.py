"""Tests for inheritance order validation in ThemedWidget.

This module tests the Phase 5 feature: Runtime validation that ensures
ThemedWidget comes BEFORE Qt base classes in the inheritance order.

The validation prevents common mistakes like:
    class MyWidget(QWidget, ThemedWidget)  # Wrong!

Instead of the correct:
    class MyWidget(ThemedWidget, QWidget)  # Correct!
"""

import pytest
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QLabel,
    QListWidget,
    QMainWindow,
    QPushButton,
    QTableWidget,
    QTextEdit,
    QWidget,
)

from vfwidgets_theme.widgets.base import ThemedWidget


class TestInheritanceOrderValidation:
    """Test suite for inheritance order validation."""

    def test_correct_order_themed_widget_first(self, qtbot):
        """Test that correct inheritance order (ThemedWidget first) doesn't raise."""

        class CorrectWidget(ThemedWidget, QWidget):
            """Correctly ordered widget."""
            pass

        # Should not raise any exception
        widget = CorrectWidget()
        qtbot.addWidget(widget)  # Register with qtbot for cleanup
        assert widget is not None
        assert isinstance(widget, ThemedWidget)
        assert isinstance(widget, QWidget)

    def test_correct_order_with_qmainwindow(self, qtbot):
        """Test correct inheritance order with QMainWindow."""

        class CorrectMainWindow(ThemedWidget, QMainWindow):
            """Correctly ordered main window."""
            pass

        # Should not raise any exception
        widget = CorrectMainWindow()
        qtbot.addWidget(widget)
        assert widget is not None
        assert isinstance(widget, ThemedWidget)
        assert isinstance(widget, QMainWindow)

    def test_correct_order_with_qdialog(self, qtbot):
        """Test correct inheritance order with QDialog."""

        class CorrectDialog(ThemedWidget, QDialog):
            """Correctly ordered dialog."""
            pass

        # Should not raise any exception
        widget = CorrectDialog()
        qtbot.addWidget(widget)
        assert widget is not None
        assert isinstance(widget, ThemedWidget)
        assert isinstance(widget, QDialog)

    def test_correct_order_with_qframe(self, qtbot):
        """Test correct inheritance order with QFrame."""

        class CorrectFrame(ThemedWidget, QFrame):
            """Correctly ordered frame."""
            pass

        # Should not raise any exception
        widget = CorrectFrame()
        qtbot.addWidget(widget)
        assert widget is not None
        assert isinstance(widget, ThemedWidget)
        assert isinstance(widget, QFrame)

    def test_correct_order_with_qtextedit(self, qtbot):
        """Test correct inheritance order with QTextEdit."""

        class CorrectEditor(ThemedWidget, QTextEdit):
            """Correctly ordered text editor."""
            pass

        # Should not raise any exception
        widget = CorrectEditor()
        qtbot.addWidget(widget)
        assert widget is not None
        assert isinstance(widget, ThemedWidget)
        assert isinstance(widget, QTextEdit)

    def test_correct_order_with_qpushbutton(self, qtbot):
        """Test correct inheritance order with QPushButton."""

        class CorrectButton(ThemedWidget, QPushButton):
            """Correctly ordered push button."""
            pass

        # Should not raise any exception
        widget = CorrectButton()
        assert widget is not None
        assert isinstance(widget, ThemedWidget)
        assert isinstance(widget, QPushButton)

    def test_wrong_order_qwidget_first_raises_error(self, qtbot):
        """Test that wrong inheritance order (QWidget first) raises TypeError."""

        class WrongWidget(QWidget, ThemedWidget):
            """Incorrectly ordered widget - should fail at instantiation."""
            pass

        # Should raise TypeError with helpful message
        with pytest.raises(TypeError) as exc_info:
            WrongWidget()

        # Verify error message is helpful
        error_msg = str(exc_info.value)
        assert "ThemedWidget must come BEFORE" in error_msg
        assert "QWidget" in error_msg
        assert "WrongWidget" in error_msg
        # Check for wrong example
        assert "❌" in error_msg or "Wrong" in error_msg
        # Check for correct example
        assert "✅" in error_msg or "Correct" in error_msg

    def test_wrong_order_qmainwindow_first_raises_error(self, qtbot):
        """Test that wrong order with QMainWindow raises TypeError."""

        class WrongMainWindow(QMainWindow, ThemedWidget):
            """Incorrectly ordered main window."""
            pass

        with pytest.raises(TypeError) as exc_info:
            WrongMainWindow()

        error_msg = str(exc_info.value)
        assert "ThemedWidget must come BEFORE" in error_msg
        assert "QMainWindow" in error_msg
        assert "WrongMainWindow" in error_msg

    def test_wrong_order_qdialog_first_raises_error(self, qtbot):
        """Test that wrong order with QDialog raises TypeError."""

        class WrongDialog(QDialog, ThemedWidget):
            """Incorrectly ordered dialog."""
            pass

        with pytest.raises(TypeError) as exc_info:
            WrongDialog()

        error_msg = str(exc_info.value)
        assert "ThemedWidget must come BEFORE" in error_msg
        assert "QDialog" in error_msg

    def test_wrong_order_qframe_first_raises_error(self, qtbot):
        """Test that wrong order with QFrame raises TypeError."""

        class WrongFrame(QFrame, ThemedWidget):
            """Incorrectly ordered frame."""
            pass

        with pytest.raises(TypeError) as exc_info:
            WrongFrame()

        error_msg = str(exc_info.value)
        assert "ThemedWidget must come BEFORE" in error_msg
        assert "QFrame" in error_msg

    def test_wrong_order_qtextedit_first_raises_error(self, qtbot):
        """Test that wrong order with QTextEdit raises TypeError."""

        class WrongEditor(QTextEdit, ThemedWidget):
            """Incorrectly ordered text editor."""
            pass

        with pytest.raises(TypeError) as exc_info:
            WrongEditor()

        error_msg = str(exc_info.value)
        assert "ThemedWidget must come BEFORE" in error_msg
        assert "QTextEdit" in error_msg

    def test_wrong_order_qpushbutton_first_raises_error(self, qtbot):
        """Test that wrong order with QPushButton raises TypeError."""

        class WrongButton(QPushButton, ThemedWidget):
            """Incorrectly ordered push button."""
            pass

        with pytest.raises(TypeError) as exc_info:
            WrongButton()

        error_msg = str(exc_info.value)
        assert "ThemedWidget must come BEFORE" in error_msg
        assert "QPushButton" in error_msg

    def test_error_message_shows_wrong_example(self, qtbot):
        """Test that error message shows the WRONG inheritance pattern."""

        class BadWidget(QWidget, ThemedWidget):
            """Widget with wrong inheritance order."""
            pass

        with pytest.raises(TypeError) as exc_info:
            BadWidget()

        error_msg = str(exc_info.value)
        # Should show the wrong pattern: class BadWidget(QWidget, ThemedWidget)
        assert "class BadWidget(QWidget, ThemedWidget" in error_msg or \
               "BadWidget(QWidget, " in error_msg

    def test_error_message_shows_correct_example(self, qtbot):
        """Test that error message shows the CORRECT inheritance pattern."""

        class BadWidget(QWidget, ThemedWidget):
            """Widget with wrong inheritance order."""
            pass

        with pytest.raises(TypeError) as exc_info:
            BadWidget()

        error_msg = str(exc_info.value)
        # Should show the correct pattern: class BadWidget(ThemedWidget, QWidget)
        assert "class BadWidget(ThemedWidget, QWidget" in error_msg or \
               "BadWidget(ThemedWidget, " in error_msg

    def test_error_message_explains_why(self, qtbot):
        """Test that error message explains WHY the order matters."""

        class BadWidget(QWidget, ThemedWidget):
            """Widget with wrong inheritance order."""
            pass

        with pytest.raises(TypeError) as exc_info:
            BadWidget()

        error_msg = str(exc_info.value)
        # Should explain the reason (MRO or initialization)
        assert "MRO" in error_msg or "initialize" in error_msg or "Method Resolution" in error_msg

    def test_multiple_inheritance_with_correct_order(self, qtbot):
        """Test that multiple inheritance works when ThemedWidget is first."""

        class CustomMixin:
            """A custom mixin class."""
            custom_value = 42

        class CorrectMultiInherit(ThemedWidget, CustomMixin, QWidget):
            """Widget with multiple inheritance, correct order."""
            pass

        # Should not raise - ThemedWidget is first
        widget = CorrectMultiInherit()
        assert widget is not None
        assert hasattr(widget, 'custom_value')
        assert widget.custom_value == 42

    def test_themedwidget_requires_qt_base(self, qtbot):
        """Test that ThemedWidget requires a Qt base class.

        ThemedWidget is a mixin and requires a Qt widget base class to function.
        This test verifies that using ThemedWidget alone (without a Qt base) will fail,
        which is the expected behavior.
        """

        class OnlyThemed(ThemedWidget):
            """Widget inheriting only from ThemedWidget - should fail."""
            pass

        # This SHOULD raise because ThemedWidget needs a Qt base class
        # ThemedWidget.__init__ calls super().__init__(parent, **kwargs)
        # which expects a Qt widget in the MRO
        with pytest.raises(TypeError) as exc_info:
            OnlyThemed()

        # The error should be about object.__init__ not accepting arguments
        error_msg = str(exc_info.value)
        assert "object.__init__()" in error_msg or "__init__" in error_msg

    def test_deeply_nested_inheritance_correct_order(self, qtbot):
        """Test that deeply nested inheritance works with correct order."""

        class BaseWidget(ThemedWidget, QWidget):
            """Base widget with correct order."""
            pass

        class DerivedWidget(BaseWidget):
            """Derived widget - should inherit correct order."""
            pass

        # Should not raise - order is correct in base class
        widget = DerivedWidget()
        assert widget is not None
        assert isinstance(widget, ThemedWidget)
        assert isinstance(widget, QWidget)

    def test_validation_happens_at_init_not_class_creation(self, qtbot):
        """Test that validation happens at __init__, not class definition."""

        # Class definition should not raise
        class WrongWidget(QWidget, ThemedWidget):
            """This class definition should not raise."""
            pass

        # Error should only happen when we try to instantiate
        with pytest.raises(TypeError):
            WrongWidget()

    def test_validation_with_qlabel(self, qtbot):
        """Test validation with QLabel."""

        class CorrectLabel(ThemedWidget, QLabel):
            """Correct order with QLabel."""
            pass

        class WrongLabel(QLabel, ThemedWidget):
            """Wrong order with QLabel."""
            pass

        # Correct should work
        correct = CorrectLabel()
        assert correct is not None

        # Wrong should fail
        with pytest.raises(TypeError):
            WrongLabel()

    def test_validation_with_qlistwidget(self, qtbot):
        """Test validation with QListWidget."""

        class CorrectList(ThemedWidget, QListWidget):
            """Correct order with QListWidget."""
            pass

        class WrongList(QListWidget, ThemedWidget):
            """Wrong order with QListWidget."""
            pass

        # Correct should work
        correct = CorrectList()
        assert correct is not None

        # Wrong should fail
        with pytest.raises(TypeError):
            WrongList()

    def test_validation_with_qtablewidget(self, qtbot):
        """Test validation with QTableWidget."""

        class CorrectTable(ThemedWidget, QTableWidget):
            """Correct order with QTableWidget."""
            pass

        class WrongTable(QTableWidget, ThemedWidget):
            """Wrong order with QTableWidget."""
            pass

        # Correct should work
        correct = CorrectTable()
        assert correct is not None

        # Wrong should fail
        with pytest.raises(TypeError):
            WrongTable()


class TestInheritanceValidationEdgeCases:
    """Test edge cases for inheritance validation."""

    def test_no_validation_for_non_qt_inheritance(self, qtbot):
        """Test that non-Qt mixin works when combined with ThemedWidget + Qt widget."""

        class CustomMixin:
            """Non-Qt mixin class."""
            custom_method_called = False

            def custom_method(self):
                self.custom_method_called = True

        class MixedWidget(ThemedWidget, CustomMixin, QWidget):
            """Widget with ThemedWidget first, then mixin, then Qt base."""
            pass

        # Should work - ThemedWidget is first, CustomMixin is not a Qt class
        widget = MixedWidget()
        qtbot.addWidget(widget)
        assert widget is not None
        assert isinstance(widget, ThemedWidget)
        assert isinstance(widget, QWidget)
        assert hasattr(widget, 'custom_method')
        widget.custom_method()
        assert widget.custom_method_called is True

    def test_validation_error_is_typeerror(self, qtbot):
        """Test that validation raises TypeError specifically."""

        class WrongWidget(QWidget, ThemedWidget):
            """Wrong order."""
            pass

        # Must raise TypeError (not ValueError or other exception types)
        with pytest.raises(TypeError):
            WrongWidget()

    def test_validation_message_is_string(self, qtbot):
        """Test that error message is a proper string."""

        class WrongWidget(QWidget, ThemedWidget):
            """Wrong order."""
            pass

        try:
            WrongWidget()
            pytest.fail("Should have raised TypeError")
        except TypeError as e:
            error_msg = str(e)
            assert isinstance(error_msg, str)
            assert len(error_msg) > 0


class TestInheritanceValidationDocumentation:
    """Test that error messages serve as good documentation."""

    def test_error_message_mentions_fix(self, qtbot):
        """Test that error message tells user how to fix the issue."""

        class WrongWidget(QWidget, ThemedWidget):
            """Wrong order."""
            pass

        with pytest.raises(TypeError) as exc_info:
            WrongWidget()

        error_msg = str(exc_info.value)
        # Should mention "fix" or "correct" or show how to fix
        assert "fix" in error_msg.lower() or "correct" in error_msg.lower()

    def test_error_message_is_multiline(self, qtbot):
        """Test that error message uses multiple lines for clarity."""

        class WrongWidget(QWidget, ThemedWidget):
            """Wrong order."""
            pass

        with pytest.raises(TypeError) as exc_info:
            WrongWidget()

        error_msg = str(exc_info.value)
        # Should be multiline for readability
        lines = error_msg.split('\n')
        assert len(lines) > 3  # Should have multiple lines of explanation

    def test_error_message_class_specific(self, qtbot):
        """Test that error message is specific to the user's class name."""

        class MyCustomWidget(QWidget, ThemedWidget):
            """Custom widget with wrong order."""
            pass

        with pytest.raises(TypeError) as exc_info:
            MyCustomWidget()

        error_msg = str(exc_info.value)
        # Should mention the actual class name
        assert "MyCustomWidget" in error_msg
