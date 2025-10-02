"""Type-safe widget roles for semantic styling.

This module provides a type-safe enum for widget roles and helper functions
for setting/getting roles. Widget roles enable semantic styling without
custom CSS.

The role system is backward compatible with string-based roles. The enum
provides IDE autocomplete and type safety while the underlying implementation
uses Qt's property system.

Usage:
    from vfwidgets_theme import WidgetRole, set_widget_role

    # Type-safe enum usage (recommended)
    button = QPushButton("Delete")
    set_widget_role(button, WidgetRole.DANGER)

    # Old string-based usage still works
    button.setProperty("role", "danger")

Available Roles:
    - DANGER: Red styling for destructive actions
    - SUCCESS: Green styling for positive actions
    - WARNING: Yellow/orange styling for warnings
    - SECONDARY: Muted styling for secondary actions
    - EDITOR: Monospace font, editor-specific colors
    - PRIMARY: Primary action styling (default button style)
    - INFO: Informational styling

Example:
    from vfwidgets_theme import WidgetRole, set_widget_role, get_widget_role

    # Set role with type safety
    delete_btn = QPushButton("Delete")
    set_widget_role(delete_btn, WidgetRole.DANGER)

    # Get role back
    role = get_widget_role(delete_btn)
    assert role == WidgetRole.DANGER

    # Role is applied in stylesheet via [role="danger"] selector

"""

from enum import Enum
from typing import Optional

from PySide6.QtWidgets import QWidget


class WidgetRole(Enum):
    """Semantic widget roles for styling.

    Each role maps to a semantic styling intent that is applied via
    Qt stylesheets using property selectors like QPushButton[role="danger"].

    The enum values are lowercase strings that match the existing stylesheet
    selectors, ensuring backward compatibility.
    """

    DANGER = "danger"
    """Red styling for destructive actions (delete, remove, etc.)."""

    SUCCESS = "success"
    """Green styling for positive actions (save, confirm, etc.)."""

    WARNING = "warning"
    """Yellow/orange styling for warnings and caution."""

    SECONDARY = "secondary"
    """Muted styling for secondary actions (cancel, etc.)."""

    EDITOR = "editor"
    """Monospace font and editor-specific colors for code/text editing."""

    PRIMARY = "primary"
    """Primary action styling (emphasized button, default action)."""

    INFO = "info"
    """Informational styling for info messages and help."""


def set_widget_role(widget: QWidget, role: WidgetRole) -> None:
    """Set widget role with automatic style refresh.

    This is the type-safe way to set widget roles. It sets the "role" property
    on the widget and triggers a style refresh so the new role is immediately
    applied.

    Args:
        widget: The widget to set the role on
        role: The WidgetRole enum value to apply

    Example:
        button = QPushButton("Delete")
        set_widget_role(button, WidgetRole.DANGER)
        # Button now has red danger styling

    Note:
        This function triggers style refresh (unpolish/polish/update) to ensure
        the role styling is immediately visible.

    """
    # Set the property (using enum's string value)
    widget.setProperty("role", role.value)

    # Trigger style refresh so the role is immediately applied
    # unpolish() removes old styling, polish() applies new styling
    style = widget.style()
    if style:
        style.unpolish(widget)
        style.polish(widget)

    # Update the widget to repaint with new style
    widget.update()


def get_widget_role(widget: QWidget) -> Optional[WidgetRole]:
    """Get widget role if set.

    Retrieves the role property from the widget and converts it back to
    a WidgetRole enum value. Returns None if no role is set or if the
    role string doesn't match any known WidgetRole.

    Args:
        widget: The widget to get the role from

    Returns:
        WidgetRole enum value if role is set and valid, None otherwise

    Example:
        button = QPushButton("Delete")
        set_widget_role(button, WidgetRole.DANGER)

        role = get_widget_role(button)
        assert role == WidgetRole.DANGER

    Note:
        This function is backward compatible with string-based roles.
        If a widget has role="danger" set via setProperty(), this will
        return WidgetRole.DANGER.

    """
    # Get the role property value (will be a string or None)
    role_value = widget.property("role")

    # If no role set, return None
    if not role_value:
        return None

    # Convert string value to enum
    # Try to find matching enum by value
    try:
        for role in WidgetRole:
            if role.value == role_value:
                return role
    except (ValueError, AttributeError):
        pass

    # No matching role found (invalid role string)
    return None
