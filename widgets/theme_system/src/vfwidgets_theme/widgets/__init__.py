"""Widget layer components.

This module contains the user-facing widget classes and theming mixins:
- ThemedWidget: The primary API - simple inheritance provides complete theming
- ThemedQWidget, ThemedMainWindow, ThemedDialog: Convenience classes
- ThemedApplication: Application-level theme management
- Property descriptors: Type-safe theme properties
- Theming mixins: Composable theming behavior

This is THE layer that developers interact with. All complexity from core,
engine, and utils is hidden behind clean, simple APIs here.
"""

# Widget components (placeholders for Tasks 7-9)
from .application import (
    ApplicationConfig,
    ApplicationThemeManager,
    ThemedApplication,
    get_global_available_themes,
    get_global_theme,
    get_themed_application,
    set_global_theme,
)
from .base import (
    ThemedWidget,
    create_themed_widget,
)

# Convenience themed widgets
from .convenience import (
    ThemedDialog,
    ThemedMainWindow,
    ThemedQWidget,
)
from .dialogs import (
    ThemePickerDialog,
    ThemeSettingsWidget,
)
from .color_editor import (
    ColorEditorWidget,
)
from .font_editor import (
    FontEditorWidget,
)
from .preview_samples import (
    PreviewSampleGenerator,
    ThemePreviewWidget,
)
from .theme_editor import (
    ThemeEditorDialog,
    ThemeEditorWidget,
)
from .token_browser import (
    TokenBrowserWidget,
)
from .validation_panel import (
    ValidationPanel,
)
from .import_export import (
    ThemeExportDialog,
    ThemeImportDialog,
    ThemeMetadataEditor,
)
from .helpers import (
    ThemePreview,
    ThemeSettings,
    add_theme_menu,
    add_theme_toolbar,
)
from .metadata import (
    ThemeInfo,
    ThemeMetadataProvider,
)
from .mixins import (
    CacheMixin,
    CompositeMixin,
    LifecycleMixin,
    NotificationMixin,
    PropertyMixin,
    ThemeableMixin,
    add_theming_to_widget,
    remove_theming_from_widget,
    themeable,
)
from .primitives import (
    ThemeButtonGroup,
    ThemeComboBox,
    ThemeListWidget,
)
from .properties import (
    ColorProperty,
    FontProperty,
    ThemeProperty,
)
from .shortcuts import (
    ThemeShortcuts,
)

__all__ = [
    # Primary user-facing classes - THE API
    "ThemedWidget",      # THE way to create themed widgets (flexible, multiple inheritance)
    "ThemedQWidget",     # Convenience class for themed QWidget (single inheritance)
    "ThemedMainWindow",  # Convenience class for themed QMainWindow (single inheritance)
    "ThemedDialog",      # Convenience class for themed QDialog (single inheritance)
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

    # Metadata system
    "ThemeInfo",
    "ThemeMetadataProvider",

    # Theme switching primitives
    "ThemeComboBox",
    "ThemeListWidget",
    "ThemeButtonGroup",

    # Theme switching helpers
    "add_theme_menu",
    "add_theme_toolbar",
    "ThemePreview",
    "ThemeSettings",
    "ThemeShortcuts",

    # Theme switching dialogs
    "ThemePickerDialog",
    "ThemeSettingsWidget",

    # Theme editor (Phase 1-5)
    "ThemeEditorDialog",
    "ThemeEditorWidget",
    "TokenBrowserWidget",
    "ColorEditorWidget",
    "FontEditorWidget",
    "ThemePreviewWidget",
    "PreviewSampleGenerator",
    "ValidationPanel",
    "ThemeImportDialog",
    "ThemeExportDialog",
    "ThemeMetadataEditor",
]
