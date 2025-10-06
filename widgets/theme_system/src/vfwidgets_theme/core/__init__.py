"""Core theme system components.

This module contains the core business logic and data models for the theme system:
- Theme data model (immutable, validated)
- ThemeManager (simplified with Single Responsibility Principle)
- ThemeProvider implementation
- Widget registry with WeakRefs for automatic memory management

The core module represents the heart of the theme system with all business logic
separated from presentation (widgets) and infrastructure (engine).
"""

# Core components (placeholders for Tasks 7-8)
from .manager import (
    ThemeManager,
    create_theme_manager,
)
from .provider import (
    CachedThemeProvider,
    CompositeThemeProvider,
    DefaultThemeProvider,
    create_cached_provider,
    create_composite_provider,
    create_default_provider,
)
from .registry import (
    DefaultRegistryEventHandler,
    RegistryEntry,
    RegistryEventHandler,
    RegistryEventType,
    ThemeWidgetRegistry,
    create_widget_registry,
)
from .theme import (
    PropertyResolver,
    Theme,
    ThemeBuilder,
    ThemeCollection,
    ThemeComposer,
    ThemeValidator,
    create_theme_from_dict,
    load_theme_from_file,
    save_theme_to_file,
    validate_theme_data,
)

__all__ = [
    # Core data models
    "Theme",
    "ThemeCollection",
    "validate_theme_data",
    "create_theme_from_dict",
    # Core management
    "ThemeManager",
    "ThemeLoader",
    "FileThemeLoader",
    "create_theme_manager",
    # Theme providers
    "DefaultThemeProvider",
    "CachedThemeProvider",
    "CompositeThemeProvider",
    "create_default_provider",
    "create_cached_provider",
    "create_composite_provider",
    # Registry system
    "ThemeWidgetRegistry",
    "RegistryEntry",
    "RegistryEventHandler",
    "RegistryEventType",
    "DefaultRegistryEventHandler",
    "create_widget_registry",
]
