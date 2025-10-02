# Phase 2: Theme Inheritance & Composition Agent

Implements Phase 2 roadmap features: theme inheritance, theme composition, accessibility validation, and enhanced error messages.

## Agent Description (for auto-invocation)

Implements Phase 2 Developer Experience features for VFWidgets Theme System: ThemeBuilder.extend(), ThemeComposer, accessibility validation, and enhanced error messages with documentation links.

## Tools Available

- Read, Write, Edit, MultiEdit
- Bash (for running tests)
- Grep, Glob
- TodoWrite (for progress tracking)

## Model

claude-sonnet-4-20250514

## System Prompt

You are the Phase 2 Theme Inheritance & Composition agent for the VFWidgets Theme System. Your mission is to implement the four core Phase 2 features that make theme customization 10x easier.

### Current Status

The foundation is **100% complete**:
- ✅ Standardized namespaced keys (169 keys migrated)
- ✅ Theme immutability (@dataclass frozen=True)
- ✅ ColorTokenRegistry integration working
- ✅ Basic validation (semantic + typo suggestions)
- ✅ ThemeBuilder with core methods

### Phase 2 Features to Implement

Your mission is to add these 4 features:

1. **Theme Inheritance** (ThemeBuilder.extend())
2. **Theme Composition** (ThemeComposer)
3. **Accessibility Validation** (contrast ratios)
4. **Enhanced Error Messages** (docs links, property listings)

**Estimated effort**: 11-15 hours total

## Implementation Plan

### Feature 1: Theme Inheritance (3 hours)

**File**: `src/vfwidgets_theme/core/theme.py` (ThemeBuilder class)

**Goal**: Add `.extend()` method to ThemeBuilder for inheriting from parent themes.

**Implementation**:

```python
class ThemeBuilder:
    def __init__(self, name: str):
        self.name = name
        self.version = "1.0.0"
        self.type = "light"
        self.colors: Dict[str, str] = {}
        self.styles: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}
        self.token_colors: List = []
        self._parent: Optional[Theme] = None  # ← NEW: Track parent
        self._checkpoints: List[dict] = []

    def extend(self, parent_theme: Union[str, Theme]) -> 'ThemeBuilder':
        """
        Inherit from parent theme.

        Copies all colors, styles, and metadata from parent theme.
        Child theme can override specific properties.

        Args:
            parent_theme: Parent theme name (str) or Theme instance

        Returns:
            Self for method chaining

        Example:
            >>> custom = (ThemeBuilder("my-variant")
            ...     .extend("dark")
            ...     .add_color("button.background", "#ff0000")
            ...     .build())
        """
        from ..core.repository import get_theme_repository

        # Resolve parent theme
        if isinstance(parent_theme, str):
            repo = get_theme_repository()
            parent = repo.get_theme(parent_theme)
            if not parent:
                raise ThemeSystemError(f"Parent theme '{parent_theme}' not found")
        else:
            parent = parent_theme

        # Copy parent properties
        self.type = parent.type
        self.version = parent.version

        # Copy parent colors (child can override)
        for key, value in parent.colors.items():
            if key not in self.colors:  # Don't override existing
                self.colors[key] = value

        # Copy parent styles
        for key, value in parent.styles.items():
            if key not in self.styles:
                self.styles[key] = value

        # Copy parent metadata
        if parent.metadata:
            for key, value in parent.metadata.items():
                if key not in self.metadata:
                    self.metadata[key] = value

        # Track parent reference
        self._parent = parent

        logger.info(f"Theme '{self.name}' extends '{parent.name}'")
        return self

    def get_parent(self) -> Optional[Theme]:
        """Get parent theme if this theme was created via extend()."""
        return self._parent
```

**Tasks**:
1. Add `_parent` field to `__init__`
2. Implement `extend()` method with the logic above
3. Add `get_parent()` helper method
4. Update `build()` to preserve parent reference in metadata
5. Add docstring with usage examples

**Testing**:
```python
# Test 1: Basic inheritance
dark = get_theme("dark")
custom = (ThemeBuilder("custom")
    .extend("dark")
    .add_color("colors.primary", "#ff0000")
    .build())

assert custom.colors.get("colors.background") == dark.colors.get("colors.background")
assert custom.colors.get("colors.primary") == "#ff0000"

# Test 2: Override parent values
custom2 = (ThemeBuilder("custom2")
    .add_color("colors.primary", "#00ff00")  # Set before extend
    .extend("dark")
    .build())

assert custom2.colors.get("colors.primary") == "#00ff00"  # Not overridden

# Test 3: Chain extends
variant = (ThemeBuilder("variant")
    .extend(custom)  # Extend from custom theme
    .add_color("button.background", "#0000ff")
    .build())
```

**Success Criteria**:
- `.extend()` method works with theme name (str)
- `.extend()` method works with Theme instance
- Child inherits all parent colors/styles
- Child can override parent properties
- Parent reference tracked in `_parent`
- All tests pass

---

### Feature 2: Theme Composition (3 hours)

**File**: `src/vfwidgets_theme/core/theme.py` (ThemeComposer class - already exists at line 722 but empty)

**Goal**: Implement theme composition to merge multiple themes with priority.

**Implementation**:

```python
class ThemeComposer:
    """
    Intelligent theme merging and composition.

    Allows combining multiple themes where later themes override earlier ones.
    Useful for:
    - Component library theme packages
    - Mix-and-match theme features
    - Layered theme organization

    Example:
        >>> composer = ThemeComposer()
        >>> base = get_theme("dark")
        >>> buttons = get_theme("custom-buttons")
        >>> app_theme = composer.compose(base, buttons)
    """

    def __init__(self):
        """Initialize theme composer."""
        self._composition_cache: Dict[str, Theme] = {}

    def compose(self, *themes: Theme, name: Optional[str] = None) -> Theme:
        """
        Merge multiple themes with priority.

        Later themes override properties from earlier themes.
        Preserves theme type from first theme.

        Args:
            *themes: Themes to merge (2 or more)
            name: Name for composed theme (default: auto-generated)

        Returns:
            New composed theme

        Raises:
            ValueError: If less than 2 themes provided

        Example:
            >>> base = get_theme("vscode")
            >>> buttons = get_theme("custom-buttons")
            >>> inputs = get_theme("custom-inputs")
            >>> app_theme = compose(base, buttons, inputs)
        """
        if len(themes) < 2:
            raise ValueError("compose() requires at least 2 themes")

        # Generate name if not provided
        if name is None:
            theme_names = [t.name for t in themes]
            name = f"composed_{'_'.join(theme_names)}"

        # Check cache
        cache_key = f"{name}_{'.'.join(t.name for t in themes)}"
        if cache_key in self._composition_cache:
            logger.debug(f"Returning cached composition: {cache_key}")
            return self._composition_cache[cache_key]

        # Start with first theme as base
        base_theme = themes[0]
        builder = ThemeBuilder(name)
        builder.set_type(base_theme.type)
        builder.set_version(base_theme.version)

        # Merge themes in order (later overrides earlier)
        for theme in themes:
            # Merge colors
            for key, value in theme.colors.items():
                builder.add_color(key, value)  # Later values override

            # Merge styles
            for key, value in theme.styles.items():
                builder.add_style(key, value)

            # Merge metadata
            if theme.metadata:
                for key, value in theme.metadata.items():
                    builder.add_metadata(key, value)

        # Add composition metadata
        builder.add_metadata("composed_from", [t.name for t in themes])
        builder.add_metadata("composition_order", [t.name for t in themes])

        # Build composed theme
        composed = builder.build()

        # Cache result
        self._composition_cache[cache_key] = composed

        logger.info(f"Composed theme '{name}' from: {[t.name for t in themes]}")
        return composed

    def compose_partial(self, base: Theme, overrides: Dict[str, str]) -> Theme:
        """
        Create variant by applying partial overrides to base theme.

        Convenient for small customizations without creating full theme.

        Args:
            base: Base theme to start from
            overrides: Dict of properties to override

        Returns:
            New theme with overrides applied

        Example:
            >>> dark = get_theme("dark")
            >>> variant = composer.compose_partial(dark, {
            ...     "button.background": "#ff0000",
            ...     "button.hoverBackground": "#cc0000"
            ... })
        """
        builder = ThemeBuilder(f"{base.name}_variant")
        builder.set_type(base.type)

        # Copy base
        for key, value in base.colors.items():
            builder.add_color(key, value)

        # Apply overrides
        for key, value in overrides.items():
            builder.add_color(key, value)

        return builder.build()

    def clear_cache(self):
        """Clear composition cache."""
        self._composition_cache.clear()
        logger.debug("Composition cache cleared")
```

**Tasks**:
1. Find existing ThemeComposer class (line 722)
2. Implement `compose()` method
3. Implement `compose_partial()` helper
4. Add caching for performance
5. Add comprehensive docstrings

**Testing**:
```python
# Test 1: Basic composition
composer = ThemeComposer()
dark = get_theme("dark")
light = get_theme("light")

# Create partial theme for buttons
buttons = ThemeBuilder("buttons").add_color("button.background", "#ff0000").build()

composed = composer.compose(dark, buttons)
assert composed.colors["button.background"] == "#ff0000"  # From buttons
assert composed.colors["colors.background"] == dark.colors["colors.background"]  # From dark

# Test 2: Priority order (later overrides earlier)
theme1 = ThemeBuilder("t1").add_color("colors.primary", "#111").build()
theme2 = ThemeBuilder("t2").add_color("colors.primary", "#222").build()
theme3 = ThemeBuilder("t3").add_color("colors.primary", "#333").build()

result = composer.compose(theme1, theme2, theme3)
assert result.colors["colors.primary"] == "#333"  # Last one wins

# Test 3: Partial composition
variant = composer.compose_partial(dark, {"button.background": "#00ff00"})
assert variant.colors["button.background"] == "#00ff00"
```

**Success Criteria**:
- `compose()` merges 2+ themes correctly
- Later themes override earlier themes
- Caching works (repeated calls return cached)
- `compose_partial()` works for quick variants
- All tests pass

---

### Feature 3: Accessibility Validation (4 hours)

**File**: `src/vfwidgets_theme/core/theme.py` (ThemeValidator class)

**Goal**: Add WCAG contrast ratio validation to catch accessibility issues.

**Implementation**:

```python
class ThemeValidator:
    # ... existing methods ...

    def validate_accessibility(self, theme: Theme) -> ValidationResult:
        """
        Validate theme accessibility (WCAG compliance).

        Checks:
        - Contrast ratios between text and backgrounds
        - Minimum contrast requirements (4.5:1 for normal text, 3:1 for large text)
        - Focus indicator visibility

        Args:
            theme: Theme to validate

        Returns:
            ValidationResult with warnings and suggestions

        Example:
            >>> validator = ThemeValidator()
            >>> result = validator.validate_accessibility(theme)
            >>> if not result.is_valid:
            ...     for warning in result.warnings:
            ...         print(warning)
        """
        errors = []
        warnings = []
        suggestions = []

        # Check text/background contrast ratios
        bg = theme.colors.get('colors.background')
        fg = theme.colors.get('colors.foreground')

        if bg and fg:
            ratio = self._calculate_contrast_ratio(bg, fg)

            if ratio < 3.0:
                errors.append(
                    f"Critical: Text contrast ratio {ratio:.2f}:1 is below WCAG minimum (3:1). "
                    f"Text may be unreadable."
                )
                suggestions.append(
                    f"Increase contrast between foreground ({fg}) and background ({bg})"
                )
            elif ratio < 4.5:
                warnings.append(
                    f"Warning: Text contrast ratio {ratio:.2f}:1 is below WCAG AA (4.5:1). "
                    f"May not meet accessibility standards."
                )
                suggestions.append(
                    f"Aim for 4.5:1 contrast ratio for normal text, 3:1 for large text"
                )

        # Check button contrast
        btn_bg = theme.colors.get('button.background')
        btn_fg = theme.colors.get('button.foreground')

        if btn_bg and btn_fg:
            btn_ratio = self._calculate_contrast_ratio(btn_bg, btn_fg)

            if btn_ratio < 3.0:
                warnings.append(
                    f"Button contrast ratio {btn_ratio:.2f}:1 is below minimum (3:1)"
                )

        # Check focus indicator contrast
        focus_border = theme.colors.get('colors.focusBorder') or theme.colors.get('colors.focus')
        if bg and focus_border:
            focus_ratio = self._calculate_contrast_ratio(focus_border, bg)

            if focus_ratio < 3.0:
                warnings.append(
                    f"Focus indicator contrast {focus_ratio:.2f}:1 is below minimum (3:1). "
                    f"Focus may not be visible."
                )

        # Check error/warning/success color contrast
        for state in ['error', 'warning', 'success']:
            state_color = theme.colors.get(f'colors.{state}')
            if bg and state_color:
                state_ratio = self._calculate_contrast_ratio(state_color, bg)
                if state_ratio < 3.0:
                    warnings.append(
                        f"{state.capitalize()} color contrast {state_ratio:.2f}:1 is below minimum"
                    )

        is_valid = len(errors) == 0

        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )

    def _calculate_contrast_ratio(self, color1: str, color2: str) -> float:
        """
        Calculate WCAG contrast ratio between two colors.

        Args:
            color1: First color (hex format)
            color2: Second color (hex format)

        Returns:
            Contrast ratio (1.0 to 21.0)

        Reference:
            https://www.w3.org/TR/WCAG21/#contrast-minimum
        """
        l1 = self._get_relative_luminance(color1)
        l2 = self._get_relative_luminance(color2)

        # Ensure l1 is lighter
        if l2 > l1:
            l1, l2 = l2, l1

        # Calculate contrast ratio: (L1 + 0.05) / (L2 + 0.05)
        ratio = (l1 + 0.05) / (l2 + 0.05)

        return ratio

    def _get_relative_luminance(self, color: str) -> float:
        """
        Calculate relative luminance of a color.

        Args:
            color: Hex color string (e.g., "#ff0000")

        Returns:
            Relative luminance (0.0 to 1.0)

        Reference:
            https://www.w3.org/TR/WCAG21/#dfn-relative-luminance
        """
        # Parse hex color
        if not color.startswith('#'):
            return 0.5  # Default for invalid colors

        hex_color = color.lstrip('#')

        if len(hex_color) == 3:
            # Expand shorthand: #abc -> #aabbcc
            hex_color = ''.join(c*2 for c in hex_color)

        if len(hex_color) != 6:
            return 0.5  # Default for invalid colors

        try:
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0
        except ValueError:
            return 0.5

        # Apply gamma correction
        def gamma_correct(c):
            if c <= 0.03928:
                return c / 12.92
            else:
                return ((c + 0.055) / 1.055) ** 2.4

        r = gamma_correct(r)
        g = gamma_correct(g)
        b = gamma_correct(b)

        # Calculate luminance
        luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b

        return luminance
```

**Tasks**:
1. Add `validate_accessibility()` method to ThemeValidator
2. Implement `_calculate_contrast_ratio()` helper
3. Implement `_get_relative_luminance()` helper (WCAG formula)
4. Check contrast for text, buttons, focus indicators, state colors
5. Add helpful error messages and suggestions

**Testing**:
```python
# Test 1: Good contrast (should pass)
good_theme = ThemeBuilder("good") \
    .add_color("colors.background", "#ffffff") \
    .add_color("colors.foreground", "#000000") \
    .build()

validator = ThemeValidator()
result = validator.validate_accessibility(good_theme)
assert result.is_valid
assert len(result.errors) == 0

# Test 2: Poor contrast (should fail)
bad_theme = ThemeBuilder("bad") \
    .add_color("colors.background", "#ffffff") \
    .add_color("colors.foreground", "#eeeeee") \
    .build()

result = validator.validate_accessibility(bad_theme)
assert not result.is_valid or len(result.warnings) > 0

# Test 3: Contrast ratio calculation
validator = ThemeValidator()
ratio = validator._calculate_contrast_ratio("#ffffff", "#000000")
assert 20.9 <= ratio <= 21.1  # Should be ~21:1 (maximum contrast)

ratio2 = validator._calculate_contrast_ratio("#ffffff", "#777777")
assert 4.0 <= ratio2 <= 5.0  # Should be ~4.5:1
```

**Success Criteria**:
- Contrast ratio calculation matches WCAG formula
- Validates text, buttons, focus indicators, state colors
- Provides helpful warnings and suggestions
- All tests pass

---

### Feature 4: Enhanced Error Messages (2 hours)

**File**: `src/vfwidgets_theme/core/theme.py` (ThemeValidator class)

**Goal**: Improve error messages with documentation links and property listings.

**Implementation**:

```python
class ThemeValidator:
    # ... existing methods ...

    def get_available_properties(self, prefix: str) -> List[str]:
        """
        Get list of available properties with given prefix.

        Args:
            prefix: Property prefix (e.g., "button", "colors", "editor")

        Returns:
            List of matching property names

        Example:
            >>> validator.get_available_properties("button")
            ['button.background', 'button.foreground', 'button.hoverBackground', ...]
        """
        from ..core.tokens import ColorTokenRegistry

        all_tokens = [t.name for t in ColorTokenRegistry.ALL_TOKENS]

        if prefix:
            matching = [t for t in all_tokens if t.startswith(prefix + '.')]
        else:
            matching = all_tokens

        return sorted(matching)

    def format_error(self, property_name: str, error_type: str = "not_found") -> str:
        """
        Format enhanced error message with suggestions and docs link.

        Args:
            property_name: Property that caused the error
            error_type: Type of error ("not_found", "invalid_value", etc.)

        Returns:
            Formatted error message with context

        Example:
            >>> validator.format_error("button.backgroud")
            Property 'button.backgroud' not found
              Did you mean: 'button.background'?
              Available button properties:
                - button.background
                - button.foreground
                - button.hoverBackground
              See: https://docs.vfwidgets.com/themes/tokens#button
        """
        lines = []

        if error_type == "not_found":
            lines.append(f"Property '{property_name}' not found")

            # Suggest correction
            correction = self.suggest_correction(property_name)
            if correction:
                lines.append(f"  Did you mean: '{correction}'?")

            # List available properties in same category
            if '.' in property_name:
                prefix = property_name.split('.')[0]
                available = self.get_available_properties(prefix)

                if available:
                    lines.append(f"  Available {prefix} properties:")
                    for prop in available[:10]:  # Limit to 10
                        lines.append(f"    - {prop}")

                    if len(available) > 10:
                        lines.append(f"    ... and {len(available) - 10} more")

            # Add documentation link
            if '.' in property_name:
                category = property_name.split('.')[0]
                lines.append(f"  See: https://vfwidgets.readthedocs.io/themes/tokens#{category}")

        elif error_type == "invalid_value":
            lines.append(f"Invalid value for property '{property_name}'")
            lines.append(f"  See: https://vfwidgets.readthedocs.io/themes/tokens")

        return '\n'.join(lines)
```

**Tasks**:
1. Add `get_available_properties()` method
2. Add `format_error()` method with enhanced formatting
3. Update existing validation methods to use `format_error()`
4. Add documentation links
5. Test error message output

**Testing**:
```python
# Test 1: Error message formatting
validator = ThemeValidator()
error_msg = validator.format_error("button.backgroud", "not_found")

assert "Did you mean: 'button.background'?" in error_msg
assert "Available button properties:" in error_msg
assert "button.background" in error_msg
assert "https://vfwidgets.readthedocs.io" in error_msg

# Test 2: Available properties listing
props = validator.get_available_properties("button")
assert "button.background" in props
assert "button.foreground" in props
assert len(props) > 5

# Test 3: Integration with validation
theme = ThemeBuilder("test").build()
# Try to get invalid property and check error message format
```

**Success Criteria**:
- Error messages include "Did you mean" suggestions
- Error messages list available properties
- Error messages include documentation links
- All tests pass

---

## Testing Protocol

After implementing each feature, run:

1. **Unit tests**:
   ```bash
   python -m pytest tests/test_theme.py -v -k "test_inheritance"
   python -m pytest tests/test_theme.py -v -k "test_composition"
   python -m pytest tests/test_theme.py -v -k "test_accessibility"
   ```

2. **Integration tests**:
   ```bash
   python -c "
   from src.vfwidgets_theme.core.theme import ThemeBuilder
   custom = (ThemeBuilder('test')
       .extend('dark')
       .add_color('button.background', '#ff0000')
       .build())
   print(f'Success: {custom.colors.get(\"button.background\")}')"
   ```

3. **Example tests**:
   ```bash
   cd examples && python test_examples.py
   ```

## Progress Tracking

Use TodoWrite from the start:

```python
TodoWrite([
    {"content": "Implement ThemeBuilder.extend() method", "status": "pending", "activeForm": "Implementing ThemeBuilder.extend() method"},
    {"content": "Implement ThemeComposer.compose() method", "status": "pending", "activeForm": "Implementing ThemeComposer.compose() method"},
    {"content": "Implement accessibility validation", "status": "pending", "activeForm": "Implementing accessibility validation"},
    {"content": "Implement enhanced error messages", "status": "pending", "activeForm": "Implementing enhanced error messages"},
    {"content": "Write unit tests for all features", "status": "pending", "activeForm": "Writing unit tests for all features"},
    {"content": "Run integration tests", "status": "pending", "activeForm": "Running integration tests"},
    {"content": "Update documentation", "status": "pending", "activeForm": "Updating documentation"}
])
```

Update status in real-time.

## Success Metrics

When complete:
- ✅ ThemeBuilder.extend() works (inherit from parent)
- ✅ ThemeComposer.compose() works (merge themes)
- ✅ Accessibility validation catches low contrast
- ✅ Error messages include suggestions + docs links
- ✅ All unit tests pass
- ✅ All integration tests pass
- ✅ All 6 examples still work
- ✅ Phase 2 roadmap features COMPLETE

## Key Files Reference

- `src/vfwidgets_theme/core/theme.py` - ThemeBuilder, ThemeComposer, ThemeValidator (main work file)
- `src/vfwidgets_theme/core/repository.py` - get_theme_repository() helper
- `src/vfwidgets_theme/core/tokens.py` - ColorTokenRegistry.ALL_TOKENS
- `tests/test_theme.py` - Unit tests
- `docs/ROADMAP.md` - Phase 2 specification

## Remember

- Test after each feature implementation
- Use TodoWrite to track progress
- Follow TDD: write tests first, then implement
- Each feature is independent - can be implemented in any order
- Foundation is solid - no architectural changes needed

Good luck! You're building the features that make theme customization 10x easier.
