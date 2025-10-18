"""Core theme system components.

This module contains the core business logic and data models for the theme system:
- Theme data model (immutable, validated)
- ThemeManager (simplified with Single Responsibility Principle)
- ThemeProvider implementation
- Widget registry with WeakRefs for automatic memory management
- Widget introspection for plugin discovery

The core module represents the heart of the theme system with all business logic
separated from presentation (widgets) and infrastructure (engine).
"""

# Core components (placeholders for Tasks 7-8)
from .font_tokens import (
    FontTokenRegistry,
    create_qfont_from_token,
    resolve_font_family,
    resolve_font_size,
    resolve_font_weight,
)
from .introspection import (
    PluginAvailability,
    WidgetMetadata,
    extract_theme_tokens,
    validate_metadata,
)
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
from .token_types import (
    ColorTokenResolver,
    FontTokenResolver,
    GenericTokenResolver,
    SizeTokenResolver,
    TokenResolver,
    TokenType,
    TOKEN_RESOLVERS,
    get_resolver,
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
    # Introspection API
    "PluginAvailability",
    "WidgetMetadata",
    "extract_theme_tokens",
    "validate_metadata",
    # Font token resolution (Phase 2)
    "FontTokenRegistry",
    "create_qfont_from_token",
    "resolve_font_family",
    "resolve_font_size",
    "resolve_font_weight",
    # Token type system (v2.1.0)
    "TokenType",
    "TokenResolver",
    "ColorTokenResolver",
    "FontTokenResolver",
    "SizeTokenResolver",
    "GenericTokenResolver",
    "TOKEN_RESOLVERS",
    "get_resolver",
]
