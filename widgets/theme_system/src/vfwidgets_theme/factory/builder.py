#!/usr/bin/env python3
"""Theme Factory and Builder System - Task 19.

This module provides a comprehensive theme construction system with:
- ThemeFactory: Main factory for creating themed components
- ThemeBuilder: Fluent API for building themes step by step
- ThemeComposer: Compose multiple themes together
- ThemeVariantGenerator: Create light/dark variants from base themes

Features:
- Fluent builder API for intuitive theme construction
- Theme composition with priority-based merging
- Automatic light/dark variant generation
- Validation during construction
- Template themes for common patterns
- Performance optimization for theme creation
"""

import copy
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Union

# Import core theme system
from ..core.theme import Theme
from ..core.theme import ThemeBuilder as CoreThemeBuilder
from ..errors import ThemeError, ThemeValidationError
from ..protocols import ColorValue

logger = logging.getLogger(__name__)


@dataclass
class ThemeTemplate:
    """Template definition for creating themes."""

    name: str
    description: str
    base_colors: dict[str, ColorValue]
    base_styles: dict[str, dict[str, Any]]
    metadata: dict[str, Any] = field(default_factory=dict)
    variants: list[str] = field(default_factory=list)  # e.g., ['light', 'dark']

    def apply_to_builder(self, builder: "ThemeBuilder") -> "ThemeBuilder":
        """Apply this template to a theme builder."""
        # Add base colors
        for color_key, color_value in self.base_colors.items():
            builder.add_color(color_key, color_value)

        # Add base styles
        for style_key, style_value in self.base_styles.items():
            builder.add_style(style_key, style_value)

        # Add metadata
        for meta_key, meta_value in self.metadata.items():
            builder.add_metadata(meta_key, meta_value)

        return builder


class ThemeBuilder:
    """Fluent API for building themes step by step.

    This provides a clean, chainable interface for constructing themes
    with validation and intelligent defaults.

    Example:
        theme = (ThemeBuilder("my-theme")
            .add_color("primary", "#007acc")
            .add_color("background", "#1e1e1e")
            .add_style("window", {"background-color": "@colors.background"})
            .set_type("dark")
            .build())

    """

    def __init__(self, name: str):
        """Initialize theme builder.

        Args:
            name: Name of the theme being built

        """
        self._name = name
        self._colors: dict[str, ColorValue] = {}
        self._styles: dict[str, dict[str, Any]] = {}
        self._metadata: dict[str, Any] = {}
        self._type: str = "light"  # Default theme type
        self._description: str = ""
        self._parent_theme: Optional[Theme] = None
        self._validation_enabled = True
        self._created_at = time.time()

        logger.debug(f"Created ThemeBuilder for: {name}")

    def add_color(self, key: str, value: ColorValue) -> "ThemeBuilder":
        """Add a color to the theme.

        Args:
            key: Color key (e.g., "primary", "background")
            value: Color value (hex, rgb, rgba, or named color)

        Returns:
            Self for chaining

        """
        if self._validation_enabled:
            self._validate_color(key, value)

        self._colors[key] = value
        logger.debug(f"Added color {key}: {value}")
        return self

    def add_colors(self, colors: dict[str, ColorValue]) -> "ThemeBuilder":
        """Add multiple colors at once.

        Args:
            colors: Dictionary of color key-value pairs

        Returns:
            Self for chaining

        """
        for key, value in colors.items():
            self.add_color(key, value)
        return self

    def add_style(self, selector: str, properties: dict[str, Any]) -> "ThemeBuilder":
        """Add a style rule to the theme.

        Args:
            selector: CSS-like selector for the style
            properties: Dictionary of style properties

        Returns:
            Self for chaining

        """
        if self._validation_enabled:
            self._validate_style(selector, properties)

        self._styles[selector] = properties
        logger.debug(f"Added style {selector}: {properties}")
        return self

    def add_styles(self, styles: dict[str, dict[str, Any]]) -> "ThemeBuilder":
        """Add multiple style rules at once.

        Args:
            styles: Dictionary of selector -> properties mappings

        Returns:
            Self for chaining

        """
        for selector, properties in styles.items():
            self.add_style(selector, properties)
        return self

    def add_metadata(self, key: str, value: Any) -> "ThemeBuilder":
        """Add metadata to the theme.

        Args:
            key: Metadata key
            value: Metadata value

        Returns:
            Self for chaining

        """
        self._metadata[key] = value
        logger.debug(f"Added metadata {key}: {value}")
        return self

    def set_description(self, description: str) -> "ThemeBuilder":
        """Set theme description.

        Args:
            description: Theme description

        Returns:
            Self for chaining

        """
        self._description = description
        return self

    def set_type(self, theme_type: str) -> "ThemeBuilder":
        """Set theme type (light, dark, etc.).

        Args:
            theme_type: Theme type

        Returns:
            Self for chaining

        """
        if theme_type not in ["light", "dark", "high-contrast", "auto"]:
            logger.warning(f"Non-standard theme type: {theme_type}")

        self._type = theme_type
        return self

    def inherit_from(self, parent_theme: Theme) -> "ThemeBuilder":
        """Inherit properties from a parent theme.

        Args:
            parent_theme: Theme to inherit from

        Returns:
            Self for chaining

        """
        self._parent_theme = parent_theme

        # Copy parent colors and styles as base
        if hasattr(parent_theme, "colors"):
            self._colors.update(parent_theme.colors)

        if hasattr(parent_theme, "styles"):
            for selector, properties in parent_theme.styles.items():
                # Deep copy to avoid reference issues
                self._styles[selector] = copy.deepcopy(properties)

        # Copy metadata (but allow overriding)
        if hasattr(parent_theme, "metadata"):
            for key, value in parent_theme.metadata.items():
                if key not in self._metadata:
                    self._metadata[key] = value

        logger.debug(f"Inheriting from theme: {parent_theme.name}")
        return self

    def apply_template(self, template: ThemeTemplate) -> "ThemeBuilder":
        """Apply a theme template.

        Args:
            template: Theme template to apply

        Returns:
            Self for chaining

        """
        return template.apply_to_builder(self)

    def enable_validation(self, enabled: bool = True) -> "ThemeBuilder":
        """Enable or disable validation during building.

        Args:
            enabled: Whether to enable validation

        Returns:
            Self for chaining

        """
        self._validation_enabled = enabled
        return self

    def clone(self) -> "ThemeBuilder":
        """Create a copy of this builder.

        Returns:
            New ThemeBuilder with the same configuration

        """
        new_builder = ThemeBuilder(f"{self._name}_copy")
        new_builder._colors = copy.deepcopy(self._colors)
        new_builder._styles = copy.deepcopy(self._styles)
        new_builder._metadata = copy.deepcopy(self._metadata)
        new_builder._type = self._type
        new_builder._description = self._description
        new_builder._parent_theme = self._parent_theme
        new_builder._validation_enabled = self._validation_enabled

        return new_builder

    def build(self) -> Theme:
        """Build the final theme.

        Returns:
            Constructed Theme object

        Raises:
            ThemeValidationError: If theme validation fails

        """
        start_time = time.perf_counter()

        try:
            # Final validation
            if self._validation_enabled:
                self._validate_complete_theme()

            # Add construction metadata
            build_metadata = {
                **self._metadata,
                "builder_created_at": self._created_at,
                "builder_built_at": time.time(),
                "builder_type": "ThemeBuilder",
                "parent_theme": self._parent_theme.name if self._parent_theme else None,
            }

            # Create theme using core theme builder
            core_builder = CoreThemeBuilder(self._name)

            # Set type before building
            core_builder.type = self._type

            # Add colors
            for key, value in self._colors.items():
                core_builder.add_color(key, value)

            # Add styles
            for selector, properties in self._styles.items():
                core_builder.add_style(selector, properties)

            # Set metadata
            for key, value in build_metadata.items():
                core_builder.add_metadata(key, value)

            # Set description in metadata
            if self._description:
                core_builder.add_metadata("description", self._description)

            # Build final theme
            theme = core_builder.build()

            build_time = (time.perf_counter() - start_time) * 1000
            logger.debug(f"Built theme '{self._name}' in {build_time:.2f}ms")

            # Performance requirement check
            if build_time > 10:  # Task requirement: <10ms per theme
                logger.warning(f"Slow theme build: {build_time:.2f}ms for {self._name}")

            return theme

        except Exception as e:
            logger.error(f"Failed to build theme '{self._name}': {e}")
            raise ThemeValidationError(self._name, [str(e)], f"Theme build failed: {e}") from e

    def _validate_color(self, key: str, value: ColorValue):
        """Validate a color value."""
        if not key:
            raise ThemeValidationError(
                "validation", ["Color key cannot be empty"], "Color key cannot be empty"
            )

        if not value:
            raise ThemeValidationError(
                "validation",
                [f"Color value for '{key}' cannot be empty"],
                f"Color value for '{key}' cannot be empty",
            )

        # Basic color format validation
        color_str = str(value)
        if color_str.startswith("#"):
            if len(color_str) not in [4, 7]:  # #rgb or #rrggbb
                raise ThemeValidationError(
                    "validation",
                    [f"Invalid hex color format: {color_str}"],
                    f"Invalid hex color format: {color_str}",
                )

    def _validate_style(self, selector: str, properties: dict[str, Any]):
        """Validate a style rule."""
        if not selector:
            raise ThemeValidationError(
                "validation", ["Style selector cannot be empty"], "Style selector cannot be empty"
            )

        if not properties:
            raise ThemeValidationError(
                "validation",
                [f"Style properties for '{selector}' cannot be empty"],
                f"Style properties for '{selector}' cannot be empty",
            )

        # Validate property keys
        for prop_key in properties.keys():
            if not isinstance(prop_key, str) or not prop_key:
                raise ThemeValidationError(
                    "validation",
                    [f"Invalid property key: {prop_key}"],
                    f"Invalid property key: {prop_key}",
                )

    def _validate_complete_theme(self):
        """Validate the complete theme before building."""
        if not self._name:
            raise ThemeValidationError(
                "validation", ["Theme name cannot be empty"], "Theme name cannot be empty"
            )

        if not self._colors and not self._styles:
            raise ThemeValidationError(
                "validation",
                ["Theme must have at least colors or styles"],
                "Theme must have at least colors or styles",
            )


class ThemeComposer:
    """Compose multiple themes together with priority-based merging.

    This allows combining themes where properties from higher-priority
    themes override those from lower-priority ones.

    Example:
        composed = (ThemeComposer()
            .add_theme(base_theme, priority=100)
            .add_theme(accent_theme, priority=200)
            .add_theme(override_theme, priority=300)
            .compose("composed-theme"))

    """

    def __init__(self):
        """Initialize theme composer."""
        self._themes: list[tuple[Theme, int]] = []  # (theme, priority)
        self._merge_strategy = "override"  # or "blend"
        logger.debug("Created ThemeComposer")

    def add_theme(self, theme: Theme, priority: int = 100) -> "ThemeComposer":
        """Add a theme to the composition.

        Args:
            theme: Theme to add
            priority: Priority level (higher = more important)

        Returns:
            Self for chaining

        """
        self._themes.append((theme, priority))
        # Sort by priority (highest first)
        self._themes.sort(key=lambda x: x[1], reverse=True)

        logger.debug(f"Added theme {theme.name} with priority {priority}")
        return self

    def set_merge_strategy(self, strategy: str) -> "ThemeComposer":
        """Set merge strategy for conflicting properties.

        Args:
            strategy: "override" (default) or "blend"

        Returns:
            Self for chaining

        """
        if strategy not in ["override", "blend"]:
            raise ValueError(f"Invalid merge strategy: {strategy}")

        self._merge_strategy = strategy
        return self

    def compose(self, name: str, description: str = "") -> Theme:
        """Compose all added themes into a new theme.

        Args:
            name: Name for the composed theme
            description: Description for the composed theme

        Returns:
            New composed theme

        """
        if not self._themes:
            raise ThemeError("No themes added to composer")

        start_time = time.perf_counter()

        # Start with empty builder
        builder = ThemeBuilder(name)
        if description:
            builder.set_description(description)

        # Merge themes in reverse priority order (lowest first, highest last)
        for theme, priority in reversed(self._themes):
            logger.debug(f"Merging theme {theme.name} (priority {priority})")

            # Merge colors
            if hasattr(theme, "colors"):
                for key, value in theme.colors.items():
                    if self._merge_strategy == "override" or key not in builder._colors:
                        builder.add_color(key, value)
                    # For "blend" strategy, could implement color blending here

            # Merge styles
            if hasattr(theme, "styles"):
                for selector, properties in theme.styles.items():
                    if self._merge_strategy == "override" or selector not in builder._styles:
                        builder.add_style(selector, properties)
                    else:
                        # Merge properties within the style
                        merged_properties = {**builder._styles[selector]}
                        merged_properties.update(properties)
                        builder.add_style(selector, merged_properties)

            # Merge metadata (always additive)
            if hasattr(theme, "metadata"):
                for key, value in theme.metadata.items():
                    # Avoid overriding important metadata
                    if key not in ["name", "version", "created_at"]:
                        builder.add_metadata(f"source_{theme.name}_{key}", value)

        # Add composition metadata
        builder.add_metadata("composition_strategy", self._merge_strategy)
        builder.add_metadata("composed_from", [theme.name for theme, _ in self._themes])
        builder.add_metadata("composition_time", time.time())

        composed_theme = builder.build()

        compose_time = (time.perf_counter() - start_time) * 1000
        logger.debug(
            f"Composed theme '{name}' from {len(self._themes)} themes in {compose_time:.2f}ms"
        )

        return composed_theme


class ThemeVariantGenerator:
    """Generate theme variants (light/dark) from base themes.

    This automatically creates light and dark variants by intelligently
    adjusting colors while maintaining the theme's character.

    Example:
        generator = ThemeVariantGenerator()
        dark_variant = generator.create_dark_variant(light_theme)
        light_variant = generator.create_light_variant(dark_theme)

    """

    def __init__(self):
        """Initialize variant generator."""
        self._color_transformers: dict[str, Callable[[str], str]] = {}
        self._setup_default_transformers()
        logger.debug("Created ThemeVariantGenerator")

    def create_dark_variant(self, base_theme: Theme, name_suffix: str = "_dark") -> Theme:
        """Create a dark variant from a light theme.

        Args:
            base_theme: Base theme to create variant from
            name_suffix: Suffix to add to theme name

        Returns:
            New dark variant theme

        """
        return self._create_variant(base_theme, "dark", name_suffix)

    def create_light_variant(self, base_theme: Theme, name_suffix: str = "_light") -> Theme:
        """Create a light variant from a dark theme.

        Args:
            base_theme: Base theme to create variant from
            name_suffix: Suffix to add to theme name

        Returns:
            New light variant theme

        """
        return self._create_variant(base_theme, "light", name_suffix)

    def register_color_transformer(self, color_key: str, transformer: Callable[[str], str]):
        """Register a custom color transformer for specific color keys.

        Args:
            color_key: Color key to transform (e.g., "primary", "background")
            transformer: Function that transforms color values

        """
        self._color_transformers[color_key] = transformer
        logger.debug(f"Registered color transformer for: {color_key}")

    def _create_variant(self, base_theme: Theme, variant_type: str, name_suffix: str) -> Theme:
        """Create a theme variant."""
        start_time = time.perf_counter()

        new_name = f"{base_theme.name}{name_suffix}"
        builder = ThemeBuilder(new_name)

        # Set variant type
        builder.set_type(variant_type)
        builder.set_description(f"{variant_type.title()} variant of {base_theme.name}")

        # Transform colors
        if hasattr(base_theme, "colors"):
            for key, value in base_theme.colors.items():
                transformed_color = self._transform_color(key, value, variant_type)
                builder.add_color(key, transformed_color)

        # Copy styles (they usually don't need transformation)
        if hasattr(base_theme, "styles"):
            for selector, properties in base_theme.styles.items():
                builder.add_style(selector, properties)

        # Copy metadata with variant info
        if hasattr(base_theme, "metadata"):
            for key, value in base_theme.metadata.items():
                if key not in ["name", "version", "created_at", "variant_of"]:
                    builder.add_metadata(key, value)

        builder.add_metadata("variant_of", base_theme.name)
        builder.add_metadata("variant_type", variant_type)
        builder.add_metadata("variant_created_at", time.time())

        variant_theme = builder.build()

        variant_time = (time.perf_counter() - start_time) * 1000
        logger.debug(f"Created {variant_type} variant '{new_name}' in {variant_time:.2f}ms")

        return variant_theme

    def _transform_color(
        self, color_key: str, color_value: ColorValue, variant_type: str
    ) -> ColorValue:
        """Transform a color for the variant."""
        # Use custom transformer if available
        if color_key in self._color_transformers:
            return self._color_transformers[color_key](str(color_value))

        # Default color transformations
        color_str = str(color_value)

        # Simple transformation logic - in practice, this would be more sophisticated
        if variant_type == "dark":
            return (
                self._lighten_color(color_str)
                if self._is_light_color(color_str)
                else self._darken_color(color_str)
            )
        else:  # light variant
            return (
                self._darken_color(color_str)
                if self._is_light_color(color_str)
                else self._lighten_color(color_str)
            )

    def _setup_default_transformers(self):
        """Setup default color transformers."""

        # Example transformers for common color keys
        def background_transformer(color: str) -> str:
            # Backgrounds need significant contrast changes
            if self._is_light_color(color):
                return "#2d2d2d"  # Dark background
            else:
                return "#f8f8f8"  # Light background

        def text_transformer(color: str) -> str:
            # Text colors need high contrast
            if self._is_light_color(color):
                return "#1a1a1a"  # Dark text
            else:
                return "#e8e8e8"  # Light text

        self._color_transformers["background"] = background_transformer
        self._color_transformers["window.background"] = background_transformer
        self._color_transformers["foreground"] = text_transformer
        self._color_transformers["window.foreground"] = text_transformer
        self._color_transformers["text.foreground"] = text_transformer

    def _is_light_color(self, color: str) -> bool:
        """Simple check if color is light (would need proper color space conversion)."""
        if color.startswith("#"):
            if len(color) == 7:  # #rrggbb
                r = int(color[1:3], 16)
                g = int(color[3:5], 16)
                b = int(color[5:7], 16)
                # Simple luminance calculation
                luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
                return luminance > 0.5

        # Default for non-hex colors
        return True

    def _lighten_color(self, color: str) -> str:
        """Lighten a color (simplified implementation)."""
        if color.startswith("#") and len(color) == 7:
            r = min(255, int(color[1:3], 16) + 40)
            g = min(255, int(color[3:5], 16) + 40)
            b = min(255, int(color[5:7], 16) + 40)
            return f"#{r:02x}{g:02x}{b:02x}"
        return color

    def _darken_color(self, color: str) -> str:
        """Darken a color (simplified implementation)."""
        if color.startswith("#") and len(color) == 7:
            r = max(0, int(color[1:3], 16) - 40)
            g = max(0, int(color[3:5], 16) - 40)
            b = max(0, int(color[5:7], 16) - 40)
            return f"#{r:02x}{g:02x}{b:02x}"
        return color


class ThemeFactory:
    """Main factory for creating themes with various construction methods.

    This is the primary entry point for theme creation, providing:
    - Builder creation with templates
    - Theme composition utilities
    - Variant generation
    - Common theme patterns

    Example:
        factory = ThemeFactory()

        # Create with builder
        theme = (factory.create_builder("modern")
            .add_color("primary", "#007acc")
            .apply_template(factory.get_template("web_app"))
            .build())

        # Create variant
        dark_theme = factory.create_variant(theme, "dark")

        # Compose themes
        composed = factory.compose_themes(base_theme, accent_theme, name="composed")

    """

    def __init__(self):
        """Initialize theme factory."""
        self._templates: dict[str, ThemeTemplate] = {}
        self._composer = ThemeComposer()
        self._variant_generator = ThemeVariantGenerator()

        # Initialize with default templates
        self._setup_default_templates()

        logger.debug("Created ThemeFactory")

    def create_builder(self, name: str) -> ThemeBuilder:
        """Create a new theme builder.

        Args:
            name: Name for the theme

        Returns:
            New ThemeBuilder instance

        """
        return ThemeBuilder(name)

    def get_template(self, template_name: str) -> Optional[ThemeTemplate]:
        """Get a theme template by name.

        Args:
            template_name: Name of the template

        Returns:
            ThemeTemplate if found, None otherwise

        """
        return self._templates.get(template_name)

    def register_template(self, template: ThemeTemplate):
        """Register a new theme template.

        Args:
            template: Template to register

        """
        self._templates[template.name] = template
        logger.debug(f"Registered template: {template.name}")

    def list_templates(self) -> list[str]:
        """List available template names.

        Returns:
            List of template names

        """
        return list(self._templates.keys())

    def create_from_template(self, template_name: str, theme_name: str) -> ThemeBuilder:
        """Create a theme builder from a template.

        Args:
            template_name: Name of the template to use
            theme_name: Name for the new theme

        Returns:
            ThemeBuilder with template applied

        Raises:
            ThemeError: If template not found

        """
        template = self.get_template(template_name)
        if not template:
            raise ThemeError(f"Template not found: {template_name}")

        builder = self.create_builder(theme_name)
        builder.apply_template(template)

        return builder

    def create_variant(
        self, base_theme: Theme, variant_type: str, name_suffix: str = None
    ) -> Theme:
        """Create a variant of an existing theme.

        Args:
            base_theme: Base theme to create variant from
            variant_type: Type of variant ("light" or "dark")
            name_suffix: Optional suffix for the variant name

        Returns:
            New variant theme

        """
        if name_suffix is None:
            name_suffix = f"_{variant_type}"

        if variant_type == "dark":
            return self._variant_generator.create_dark_variant(base_theme, name_suffix)
        elif variant_type == "light":
            return self._variant_generator.create_light_variant(base_theme, name_suffix)
        else:
            raise ThemeError(f"Unknown variant type: {variant_type}")

    def compose_themes(
        self, *themes: Union[Theme, tuple[Theme, int]], name: str, description: str = ""
    ) -> Theme:
        """Compose multiple themes together.

        Args:
            *themes: Themes to compose. Can be Theme objects or (Theme, priority) tuples
            name: Name for composed theme
            description: Description for composed theme

        Returns:
            Composed theme

        """
        composer = ThemeComposer()

        for theme_or_tuple in themes:
            if isinstance(theme_or_tuple, tuple):
                theme, priority = theme_or_tuple
                composer.add_theme(theme, priority)
            else:
                composer.add_theme(theme_or_tuple)

        return composer.compose(name, description)

    def create_minimal_theme(self, name: str, primary_color: str, background_color: str) -> Theme:
        """Create a minimal theme with just basic colors.

        Args:
            name: Theme name
            primary_color: Primary color
            background_color: Background color

        Returns:
            Minimal theme

        """
        return (
            self.create_builder(name)
            .add_color("primary", primary_color)
            .add_color("background", background_color)
            .add_color(
                "foreground",
                (
                    "#ffffff"
                    if self._variant_generator._is_light_color(background_color)
                    else "#000000"
                ),
            )
            .add_style(
                "window", {"background-color": "@colors.background", "color": "@colors.foreground"}
            )
            .set_description(
                f"Minimal theme with {primary_color} primary and {background_color} background"
            )
            .build()
        )

    def get_statistics(self) -> dict[str, Any]:
        """Get factory usage statistics.

        Returns:
            Statistics dictionary

        """
        return {
            "templates_registered": len(self._templates),
            "available_templates": list(self._templates.keys()),
            "factory_initialized": True,
        }

    def _setup_default_templates(self):
        """Setup default theme templates."""
        # Web application template
        web_app_template = ThemeTemplate(
            name="web_app",
            description="Standard web application theme template",
            base_colors={
                "primary": "#007acc",
                "secondary": "#6c757d",
                "success": "#28a745",
                "warning": "#ffc107",
                "danger": "#dc3545",
                "info": "#17a2b8",
                "light": "#f8f9fa",
                "dark": "#343a40",
                "background": "#ffffff",
                "foreground": "#212529",
            },
            base_styles={
                "window": {
                    "background-color": "@colors.background",
                    "color": "@colors.foreground",
                    "font-family": "Arial, sans-serif",
                    "font-size": "14px",
                },
                "button": {
                    "background-color": "@colors.primary",
                    "color": "@colors.light",
                    "border": "1px solid @colors.primary",
                    "padding": "8px 16px",
                    "border-radius": "4px",
                },
            },
            metadata={
                "category": "application",
                "usage": "web applications",
                "author": "VFWidgets",
            },
            variants=["light", "dark"],
        )

        # Material design template
        material_template = ThemeTemplate(
            name="material",
            description="Material Design inspired theme template",
            base_colors={
                "primary": "#2196F3",
                "primary_dark": "#1976D2",
                "primary_light": "#BBDEFB",
                "accent": "#FF5722",
                "background": "#FAFAFA",
                "surface": "#FFFFFF",
                "error": "#F44336",
                "on_primary": "#FFFFFF",
                "on_secondary": "#000000",
                "on_background": "#000000",
                "on_surface": "#000000",
                "on_error": "#FFFFFF",
            },
            base_styles={
                "window": {
                    "background-color": "@colors.background",
                    "color": "@colors.on_background",
                    "font-family": "Roboto, sans-serif",
                },
                "card": {
                    "background-color": "@colors.surface",
                    "color": "@colors.on_surface",
                    "border-radius": "8px",
                    "box-shadow": "0 2px 4px rgba(0,0,0,0.1)",
                },
                "button.primary": {
                    "background-color": "@colors.primary",
                    "color": "@colors.on_primary",
                    "border-radius": "4px",
                    "text-transform": "uppercase",
                },
            },
            metadata={
                "category": "design_system",
                "usage": "material design applications",
                "author": "VFWidgets",
                "reference": "Material Design 3",
            },
            variants=["light", "dark"],
        )

        # Dark theme template
        dark_template = ThemeTemplate(
            name="dark",
            description="Dark theme template",
            base_colors={
                "background": "#1e1e1e",
                "foreground": "#ffffff",
                "primary": "#0e639c",
                "secondary": "#404040",
                "accent": "#007acc",
                "border": "#404040",
                "hover": "#2d2d2d",
            },
            base_styles={
                "window": {"background-color": "@colors.background", "color": "@colors.foreground"},
                "button": {
                    "background-color": "@colors.primary",
                    "color": "@colors.foreground",
                    "border": "1px solid @colors.border",
                },
                "input": {
                    "background-color": "@colors.secondary",
                    "color": "@colors.foreground",
                    "border": "1px solid @colors.border",
                },
            },
            metadata={
                "category": "theme_type",
                "usage": "dark mode applications",
                "author": "VFWidgets",
            },
        )

        # Register all default templates
        for template in [web_app_template, material_template, dark_template]:
            self.register_template(template)

        logger.debug(f"Registered {len(self._templates)} default templates")
