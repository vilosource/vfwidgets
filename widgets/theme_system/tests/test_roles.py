"""Tests for WidgetRole enum and helper functions.

This module tests:
1. WidgetRole enum values match expected role strings
2. set_widget_role() sets property and refreshes style
3. get_widget_role() retrieves role correctly
4. Type safety and enum validation
5. Backward compatibility with string-based roles
"""

import pytest
from PySide6.QtWidgets import QApplication, QPushButton, QWidget

# These imports WILL FAIL initially (TDD)
from vfwidgets_theme.widgets.roles import WidgetRole, get_widget_role, set_widget_role


@pytest.fixture
def qapp():
    """Create QApplication instance for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def widget(qapp):
    """Create a test widget."""
    return QWidget()


@pytest.fixture
def button(qapp):
    """Create a test button."""
    return QPushButton("Test")


class TestWidgetRoleEnum:
    """Test WidgetRole enum definition."""

    def test_enum_has_all_roles(self):
        """Test that WidgetRole has all 7 expected roles."""
        expected_roles = {'DANGER', 'SUCCESS', 'WARNING', 'SECONDARY', 'EDITOR', 'PRIMARY', 'INFO'}
        actual_roles = {role.name for role in WidgetRole}
        assert actual_roles == expected_roles, f"Expected {expected_roles}, got {actual_roles}"

    def test_danger_role_value(self):
        """Test DANGER role has correct string value."""
        assert WidgetRole.DANGER.value == "danger"

    def test_success_role_value(self):
        """Test SUCCESS role has correct string value."""
        assert WidgetRole.SUCCESS.value == "success"

    def test_warning_role_value(self):
        """Test WARNING role has correct string value."""
        assert WidgetRole.WARNING.value == "warning"

    def test_secondary_role_value(self):
        """Test SECONDARY role has correct string value."""
        assert WidgetRole.SECONDARY.value == "secondary"

    def test_editor_role_value(self):
        """Test EDITOR role has correct string value."""
        assert WidgetRole.EDITOR.value == "editor"

    def test_primary_role_value(self):
        """Test PRIMARY role has correct string value."""
        assert WidgetRole.PRIMARY.value == "primary"

    def test_info_role_value(self):
        """Test INFO role has correct string value."""
        assert WidgetRole.INFO.value == "info"

    def test_enum_is_immutable(self):
        """Test that enum values cannot be changed."""
        with pytest.raises(AttributeError):
            WidgetRole.DANGER = "modified"

    def test_enum_string_representation(self):
        """Test enum string representation."""
        assert str(WidgetRole.DANGER) in ["WidgetRole.DANGER", "DANGER"]


class TestSetWidgetRole:
    """Test set_widget_role() helper function."""

    def test_set_role_sets_property(self, widget):
        """Test that set_widget_role sets the 'role' property."""
        set_widget_role(widget, WidgetRole.DANGER)
        assert widget.property("role") == "danger"

    def test_set_role_with_different_roles(self, button):
        """Test setting different roles on same widget."""
        set_widget_role(button, WidgetRole.SUCCESS)
        assert button.property("role") == "success"

        set_widget_role(button, WidgetRole.WARNING)
        assert button.property("role") == "warning"

    def test_set_role_triggers_style_update(self, widget):
        """Test that set_widget_role triggers style refresh."""
        # Set initial role
        set_widget_role(widget, WidgetRole.PRIMARY)

        # Widget should have the role property set
        assert widget.property("role") == "primary"

        # Note: We can't easily test style().unpolish/polish calls without mocking,
        # but we verify the property is set correctly

    def test_set_role_with_all_roles(self, widget):
        """Test setting each role type."""
        for role in WidgetRole:
            set_widget_role(widget, role)
            assert widget.property("role") == role.value

    def test_set_role_type_safety(self, widget):
        """Test that only WidgetRole enum is accepted (type safety)."""
        # This should work
        set_widget_role(widget, WidgetRole.DANGER)

        # Note: Python doesn't enforce type hints at runtime,
        # but IDE should catch this during development
        # We can add runtime validation if needed


class TestGetWidgetRole:
    """Test get_widget_role() helper function."""

    def test_get_role_returns_none_when_not_set(self, widget):
        """Test that get_widget_role returns None when role not set."""
        role = get_widget_role(widget)
        assert role is None

    def test_get_role_after_set(self, widget):
        """Test getting role after setting it."""
        set_widget_role(widget, WidgetRole.DANGER)
        role = get_widget_role(widget)
        assert role == WidgetRole.DANGER

    def test_get_role_with_all_roles(self, widget):
        """Test getting each role type."""
        for expected_role in WidgetRole:
            set_widget_role(widget, expected_role)
            actual_role = get_widget_role(widget)
            assert actual_role == expected_role

    def test_get_role_after_changing_role(self, widget):
        """Test getting role after changing it."""
        set_widget_role(widget, WidgetRole.PRIMARY)
        assert get_widget_role(widget) == WidgetRole.PRIMARY

        set_widget_role(widget, WidgetRole.SECONDARY)
        assert get_widget_role(widget) == WidgetRole.SECONDARY


class TestBackwardCompatibility:
    """Test backward compatibility with string-based roles."""

    def test_string_role_still_works(self, widget):
        """Test that old string-based setProperty still works."""
        # Old way (should still work)
        widget.setProperty("role", "danger")
        assert widget.property("role") == "danger"

    def test_get_role_from_string_property(self, widget):
        """Test that get_widget_role works with string-set properties."""
        # Set role the old way
        widget.setProperty("role", "success")

        # Get role the new way
        role = get_widget_role(widget)
        assert role == WidgetRole.SUCCESS

    def test_mixed_string_and_enum_usage(self, widget):
        """Test mixing string and enum usage."""
        # Set with string
        widget.setProperty("role", "warning")
        assert get_widget_role(widget) == WidgetRole.WARNING

        # Set with enum
        set_widget_role(widget, WidgetRole.INFO)
        assert widget.property("role") == "info"
        assert get_widget_role(widget) == WidgetRole.INFO

    def test_invalid_string_role_returns_none(self, widget):
        """Test that invalid string roles return None from get_widget_role."""
        widget.setProperty("role", "invalid_role_name")
        role = get_widget_role(widget)
        assert role is None

    def test_empty_string_role_returns_none(self, widget):
        """Test that empty string role returns None."""
        widget.setProperty("role", "")
        role = get_widget_role(widget)
        assert role is None


class TestRoleIntegration:
    """Integration tests for role system."""

    def test_multiple_widgets_different_roles(self, qapp):
        """Test setting different roles on multiple widgets."""
        widgets = [QWidget() for _ in range(7)]
        roles = list(WidgetRole)

        for widget, role in zip(widgets, roles):
            set_widget_role(widget, role)

        for widget, expected_role in zip(widgets, roles):
            assert get_widget_role(widget) == expected_role

    def test_role_survives_widget_operations(self, widget):
        """Test that role property persists through widget operations."""
        set_widget_role(widget, WidgetRole.DANGER)

        # Do some widget operations
        widget.setEnabled(False)
        widget.setEnabled(True)
        widget.hide()
        widget.show()

        # Role should still be set
        assert get_widget_role(widget) == WidgetRole.DANGER

    def test_button_with_role(self, button):
        """Test setting role on QPushButton specifically."""
        set_widget_role(button, WidgetRole.DANGER)
        assert get_widget_role(button) == WidgetRole.DANGER
        assert button.property("role") == "danger"


class TestRoleEnumValidation:
    """Test enum validation and error cases."""

    def test_all_role_values_are_lowercase(self):
        """Test that all enum values are lowercase strings."""
        for role in WidgetRole:
            assert role.value.islower(), f"{role.name} value should be lowercase"
            assert isinstance(role.value, str), f"{role.name} value should be string"

    def test_all_role_values_are_unique(self):
        """Test that all enum values are unique."""
        values = [role.value for role in WidgetRole]
        assert len(values) == len(set(values)), "Role values must be unique"

    def test_enum_iteration(self):
        """Test iterating over WidgetRole enum."""
        roles = list(WidgetRole)
        assert len(roles) == 7, "Should have exactly 7 roles"

    def test_enum_membership(self):
        """Test checking if value is in enum."""
        assert WidgetRole.DANGER in WidgetRole
        assert WidgetRole.SUCCESS in WidgetRole


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
