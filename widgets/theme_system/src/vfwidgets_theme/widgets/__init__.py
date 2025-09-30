"""
Widget layer components.

This module contains the user-facing widget classes and theming mixins:
- ThemedWidget: The primary API - simple inheritance provides complete theming
- ThemedApplication: Application-level theme management
- Property descriptors: Type-safe theme properties
- Theming mixins: Composable theming behavior

This is THE layer that developers interact with. All complexity from core,
engine, and utils is hidden behind clean, simple APIs here.
"""

# Widget components (placeholders for Tasks 7-9)
from .base import (
    ThemedWidget,
    create_themed_widget,
)

from .application import (
    ThemedApplication,
    ApplicationThemeManager,
    ApplicationConfig,
    get_themed_application,
    set_global_theme,
    get_global_theme,
    get_global_available_themes,
)

from .properties import (
    ThemeProperty,
    ColorProperty,
    FontProperty,
)

from .mixins import (
    ThemeableMixin,
    PropertyMixin,
    NotificationMixin,
    CacheMixin,
    LifecycleMixin,
    CompositeMixin,
    add_theming_to_widget,
    remove_theming_from_widget,
    themeable,
)

__all__ = [
    # Primary user-facing classes - THE API
    "ThemedWidget",      # THE way to create themed widgets
    "ThemedApplication", # THE way to manage themes
    "create_themed_widget",
    "get_themed_application",
    "set_global_theme",
    "get_global_theme",
    "get_global_available_themes",

    # Property system
    "ThemeProperty",
    "ColorProperty",
    "FontProperty",

    # Composable behavior
    "ThemeMixin",
    "ColorMixin",
]