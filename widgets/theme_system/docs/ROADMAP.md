# VFWidgets Theme System - Roadmap

This document explains the design rationale behind the current architecture and outlines planned enhancements.

**Related Documents:**
- [ARCHITECTURE.md](ARCHITECTURE.md) - Current system implementation
- [api-REFERENCE.md](api-REFERENCE.md) - User-facing API documentation

---

## Table of Contents

1. [Design Rationale](#design-rationale)
2. [Known Limitations](#known-limitations)
3. [Future Enhancements](#future-enhancements)

---

## Design Rationale

### Why ThemedWidget is a Mixin

**Current Implementation:** [ARCHITECTURE.md > ThemedWidget](ARCHITECTURE.md#themedwidget)

**Decision:** ThemedWidget uses metaclass-based multiple inheritance rather than direct QWidget inheritance.

**Rationale:**
- **Flexibility**: Users can theme any Qt widget (QWidget, QMainWindow, QDialog, custom widgets)
- **No Inheritance Conflicts**: Avoids diamond inheritance problems with complex Qt hierarchies
- **Composition Over Restriction**: Doesn't force a specific base class

**Trade-off Accepted:**
- Inheritance order matters (ThemedWidget must come first)
- Slightly more complex for beginners vs single inheritance

**Future:**
- Continue providing convenience classes (ThemedQWidget, ThemedMainWindow) for common cases
- Investigate if metaclass complexity can be reduced in Python 3.12+

### Why ThemeManager is a Facade

**Current Implementation:** [ARCHITECTURE.md > ThemeManager](ARCHITECTURE.md#thememanager)

**Decision:** Single ThemeManager coordinates all components rather than exposing them individually.

**Rationale:**
- **Simplicity**: Users interact with one object, not six (repository, applicator, notifier, provider, registry, lifecycle)
- **Encapsulation**: Internal component architecture can evolve without breaking API
- **Testability**: Easy to mock entire theme system for widget tests

**Trade-off Accepted:**
- Granular control requires accessing private `_repository`, `_applicator` etc
- Some flexibility sacrificed for simplicity

**Future:**
- Consider exposing specific components (like repository) for advanced use cases
- Add configuration hooks without exposing internal structure

### Why Themes are Immutable

**Current Implementation:** [ARCHITECTURE.md > Theme Data Model](ARCHITECTURE.md#theme-data-model)

**Decision:** Theme instances are frozen dataclasses that cannot be modified after creation.

**Rationale:**
- **Thread Safety**: Can be safely shared across threads without locks
- **Predictability**: Theme never changes under your feet
- **Caching**: Safe to cache derived values since theme won't mutate
- **Copy-on-Write**: ThemeBuilder enables modifications without mutating original

**Trade-off Accepted:**
- Must create new Theme for any modification
- Slightly more memory for transient theme variants

**Future:**
- Explore structural sharing for memory efficiency with many theme variants
- Consider persistent data structures for efficient theme composition

### Why WeakRef Widget Registry

**Current Implementation:** [ARCHITECTURE.md > ThemeWidgetRegistry](ARCHITECTURE.md#themewidgetregistry)

**Decision:** Registry stores weak references to widgets, not strong references.

**Rationale:**
- **Memory Safety**: Widgets automatically unregister when destroyed
- **No Manual Cleanup**: Developers don't need to call `unregister()`
- **Leak Prevention**: Registry can't prevent widget garbage collection

**Trade-off Accepted:**
- WeakRefs have small overhead vs regular references
- Cannot iterate registry while deleting widgets (Python WeakSet limitation)

**Future:**
- Monitor for WeakRef performance issues in large applications
- Consider ref-counted hybrid approach if needed

### Why StylesheetGenerator vs Runtime Properties

**Current Implementation:** [ARCHITECTURE.md > StylesheetGenerator](ARCHITECTURE.md#stylesheetgenerator)

**Decision:** Generate complete Qt stylesheets upfront rather than resolving properties at runtime.

**Rationale:**
- **Performance**: Qt's CSS engine is highly optimized; runtime property lookup is not
- **Qt Native**: Leverages Qt's pseudo-state handling (:hover, :pressed, etc)
- **Compatibility**: Works with standard Qt widgets without modification
- **Cascade**: Descendant selectors automatically theme child widgets

**Trade-off Accepted:**
- Large stylesheets (several KB per themed widget)
- Cannot animate individual property changes
- Stylesheet regeneration on theme switch (not incremental)

**Future:**
- Investigate hybrid approach for animated theme transitions
- Consider stylesheet caching/reuse for common widget types

### Why No ThemeEngine Abstraction

**Current Implementation:** [ARCHITECTURE.md > Data Flow](ARCHITECTURE.md#data-flow)

**Decision:** No separate ThemeEngine layer - StylesheetGenerator directly creates Qt CSS.

**Rationale:**
- **YAGNI**: Don't need abstraction over Qt's stylesheet system (only target platform)
- **Simplicity**: Fewer layers means easier to understand and debug
- **Performance**: Direct generation avoids intermediate representation

**Trade-off Accepted:**
- Tightly coupled to Qt stylesheet format
- Porting to other GUI frameworks would require significant refactoring

**Future:**
- If we support additional platforms (GTK, web), introduce abstraction then
- Current focus: Make Qt theming exceptional, not generic

---

## Known Limitations

This section documents current limitations and their workarounds. Each will be addressed in future releases.

### 1. No Batch Theme Application

**Current Behavior:** [ARCHITECTURE.md > ThemeApplicator](ARCHITECTURE.md#themeapplicator)

When switching themes, the applicator processes widgets one at a time:
```python
for widget in registry.get_all_widgets():
    applicator.apply_to_widget(widget, theme)  # Individual updates
```

**Impact:**
- Theme switching with 100+ widgets takes ~50-100ms
- Noticeable lag in large applications
- Multiple repaints during theme switch

**Workaround:**
- Minimize widget count by reusing widgets
- Use `QApplication.setOverrideCursor(Qt.WaitCursor)` during switch

**Planned Fix:** [Phase 1: Batch Application](#phase-1-performance-optimization)

### 2. No Lazy Theme Loading

**Current Behavior:** [ARCHITECTURE.md > ThemeRepository](ARCHITECTURE.md#themerepository)

All built-in themes load at application startup:
```python
def _initialize_builtin_themes(self):
    for theme_name in ["vscode", "default", "minimal"]:
        theme = load_builtin_theme(theme_name)  # All loaded upfront
        self._repository.add_theme(theme)
```

**Impact:**
- ~200-300ms additional startup time
- ~500KB memory for themes not currently used

**Workaround:**
- Pre-build theme JSON files to reduce parsing time
- Use smaller built-in theme set

**Planned Fix:** [Phase 1: Lazy Loading](#phase-1-performance-optimization)

### 3. No Theme Inheritance/Composition

**Current Behavior:** [ARCHITECTURE.md > Theme](ARCHITECTURE.md#theme-data-model)

Themes cannot extend or compose other themes (except through VSCode import):
```python
# NOT SUPPORTED:
custom_theme = ThemeBuilder("custom")
    .extend("vscode")        # ❌ No extend()
    .override("button.*")    # ❌ No selective override
    .compose(partial_theme)  # ❌ No composition
    .build()
```

**Impact:**
- Must duplicate all properties when customizing a theme
- Cannot create theme variants efficiently
- No partial themes for component libraries

**Workaround:**
```python
# Current approach: Manual copying
base = app.get_current_theme()
custom = ThemeBuilder("custom")
    .add_colors(base.colors)  # Copy all
    .add_color("button.background", "#custom")  # Override one
    .build()
```

**Planned Fix:** [Phase 2: Theme Inheritance](#phase-2-developer-experience)

### 4. No Platform Theme Sync

**Current Behavior:** No system dark/light mode detection.

**Impact:**
- Users must manually switch themes to match system
- Application doesn't respect OS theme preferences

**Workaround:**
```python
# Manual detection (Linux/macOS)
import subprocess
result = subprocess.run(["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
                       capture_output=True)
if "dark" in result.stdout.decode().lower():
    app.set_theme("vscode")
else:
    app.set_theme("default")
```

**Planned Fix:** [Phase 3: Platform Integration](#phase-3-platform-integration)

### 5. Limited Theme Validation

**Current Behavior:** [ARCHITECTURE.md > Validation](ARCHITECTURE.md#validation)

Theme validation is basic:
- Checks JSON structure
- Validates color formats
- No semantic validation (e.g., "is contrast sufficient?")
- No computed property safety (no sandboxing)

**Impact:**
- Malformed themes can cause visual issues
- No warnings for accessibility problems
- Unsafe computed properties could execute arbitrary code

**Workaround:**
- Manually test themes thoroughly
- Use built-in themes as templates
- Avoid computed properties

**Planned Fix:** [Phase 2: Validation Improvements](#phase-2-developer-experience)

### 6. No Stylesheet Caching

**Current Behavior:** Stylesheets regenerate on every theme switch.

**Impact:**
- Repeated theme switching is slower than necessary
- Same stylesheet generated multiple times for identical widget types

**Workaround:**
- Avoid rapid theme switching
- Profile application if theme switch performance is critical

**Planned Fix:** [Phase 1: L2/L3 Cache](#phase-1-performance-optimization)

---

## Future Enhancements

Enhancements are organized by development phase. Each phase builds on previous ones.

### Phase 1: Performance Optimization (v1.1)

**Goal:** Reduce theme switching time from ~100ms to <50ms for 100+ widgets.

**Target Release:** Q2 2025

#### 1.1 Batch Theme Application

**Current:** [Limitation #1](#1-no-batch-theme-application)

**Implementation:**
```python
class BatchThemeApplicator:
    def apply_batch(self, theme: Theme, widgets: List[ThemedWidget]):
        # Group by widget type
        by_type = self._group_by_type(widgets)

        # Generate stylesheet once per type
        stylesheets = {}
        for widget_type, widget_list in by_type.items():
            stylesheets[widget_type] = self._generate_stylesheet(theme, widget_type)

        # Apply in single pass with batched repaints
        with QPainter.batched_updates():
            for widget in widgets:
                widget.setStyleSheet(stylesheets[type(widget)])
```

**Benefits:**
- 50% reduction in theme switch time (100ms → 50ms)
- Single repaint instead of per-widget repaints

#### 1.2 Lazy Theme Loading

**Current:** [Limitation #2](#2-no-lazy-theme-loading)

**Implementation:**
```python
class LazyThemeRepository:
    def __init__(self):
        self._manifest = self._load_manifest()  # Lightweight metadata only
        self._loaded = {}

    def get_theme(self, name: str) -> Theme:
        if name not in self._loaded:
            self._loaded[name] = self._load_theme(name)  # Load on demand
        return self._loaded[name]
```

**Benefits:**
- 200ms faster startup
- 500KB memory savings
- Only pay for themes actually used

#### 1.3 Stylesheet Caching

**Current:** [Limitation #6](#6-no-stylesheet-caching)

**Implementation:**
```python
class StylesheetCache:
    # L2: Per widget type
    _type_cache: Dict[Tuple[str, Type], str] = {}

    # L3: Pre-compiled common widgets
    _precompiled: Dict[str, Dict[Type, str]] = {}

    def get_or_generate(self, theme: Theme, widget_type: Type) -> str:
        key = (theme.name, widget_type)
        if key not in self._type_cache:
            self._type_cache[key] = self._generate(theme, widget_type)
        return self._type_cache[key]
```

**Benefits:**
- Instant theme re-application (switching back to previous theme)
- Reduced CPU usage for theme operations

#### 1.4 Async Theme Loading

**Implementation:**
```python
class AsyncThemeLoader:
    async def load_theme_file(self, path: Path) -> Theme:
        # Load file in background thread
        theme_data = await asyncio.to_thread(self._load_json, path)

        # Parse and validate
        theme = Theme.from_dict(theme_data)

        return theme

# Usage:
theme = await app.load_theme_file_async("custom.json")
app.set_theme(theme.name)
```

**Benefits:**
- Non-blocking theme loading
- Better UX for large theme files

### Phase 2: Developer Experience (v1.2)

**Goal:** Make theme customization 10x easier.

**Target Release:** Q3 2025

#### 2.1 Theme Inheritance

**Current:** [Limitation #3](#3-no-theme-inheritancecomposition)

**Implementation:**
```python
class ThemeBuilder:
    def extend(self, parent_theme: Union[str, Theme]) -> 'ThemeBuilder':
        """Inherit from parent theme."""
        if isinstance(parent_theme, str):
            parent = get_theme(parent_theme)
        else:
            parent = parent_theme

        # Copy parent colors/properties
        self.add_colors(parent.colors)
        self.add_styles(parent.styles)

        # Track parent for property resolution
        self._parent = parent
        return self

# Usage:
custom = (ThemeBuilder("my-vscode-variant")
    .extend("vscode")                      # Inherit everything
    .add_color("button.background", "#f00") # Override one property
    .build())
```

**Benefits:**
- DRY principle - no property duplication
- Easy theme variants
- Clear inheritance chain

#### 2.2 Theme Composition

**Implementation:**
```python
class ThemeComposer:
    def compose(self, *themes: Theme) -> Theme:
        """Merge multiple themes with priority."""
        result = ThemeBuilder(themes[0].name)

        for theme in themes:
            result.add_colors(theme.colors)  # Later themes override
            result.add_styles(theme.styles)

        return result.build()

# Usage:
base = get_theme("vscode")
buttons = get_theme("custom-buttons")
inputs = get_theme("custom-inputs")

app_theme = compose(base, buttons, inputs)  # Layer themes
```

**Benefits:**
- Component library theme packages
- Mix-and-match theme features
- Cleaner theme organization

#### 2.3 Better Validation

**Implementation:**
```python
class ThemeValidator:
    def validate_accessibility(self, theme: Theme) -> ValidationReport:
        issues = []

        # Check contrast ratios
        bg = theme.get('colors.background')
        fg = theme.get('colors.foreground')
        ratio = calculate_contrast(bg, fg)
        if ratio < 4.5:
            issues.append(ValidationIssue(
                severity="warning",
                message=f"Low contrast: {ratio:.2f} (minimum 4.5)",
                suggestion="Increase foreground brightness"
            ))

        return ValidationReport(issues)
```

**Benefits:**
- Catch accessibility issues during development
- Helpful error messages with suggestions
- Theme quality guidelines

#### 2.4 Enhanced Error Messages

**Implementation:**
```python
# Current:
PropertyNotFoundError: Property 'button.backgroud' not found

# Enhanced:
PropertyNotFoundError: Property 'button.backgroud' not found
  Did you mean: 'button.background'?
  Available button properties:
    - button.background
    - button.foreground
    - button.hoverBackground
  See: https://docs.vfwidgets.com/themes/properties#button
```

**Benefits:**
- Faster debugging
- Self-documenting API
- Lower learning curve

### Phase 3: Platform Integration (v1.3)

**Goal:** Respect system preferences and platform conventions.

**Target Release:** Q4 2025

#### 3.1 System Theme Detection

**Current:** [Limitation #4](#4-no-platform-theme-sync)

**Implementation:**
```python
class PlatformThemeAdapter:
    def detect_system_theme(self) -> str:
        """Detect OS dark/light preference."""
        if sys.platform == "win32":
            return self._detect_windows()
        elif sys.platform == "darwin":
            return self._detect_macos()
        else:
            return self._detect_linux()

    def watch_system_theme_changes(self, callback: Callable):
        """Monitor OS theme changes."""
        # Platform-specific monitoring
        self._watcher = PlatformThemeWatcher()
        self._watcher.changed.connect(callback)

# Usage:
adapter = PlatformThemeAdapter()
if adapter.detect_system_theme() == "dark":
    app.set_theme("vscode")

adapter.watch_system_theme_changes(lambda: app.sync_with_system())
```

**Benefits:**
- Automatic dark/light mode sync
- Native OS integration
- Better user experience

#### 3.2 High Contrast Support

**Implementation:**
```python
# High contrast theme variant
high_contrast_theme = (ThemeBuilder("high-contrast")
    .set_type("high-contrast")
    .add_color("colors.foreground", "#ffffff")
    .add_color("colors.background", "#000000")
    .add_color("button.border", "#ffffff")
    .add_metadata("contrast_ratio", 21.0)  # Maximum contrast
    .build())

# Auto-enable based on OS settings
if adapter.is_high_contrast_enabled():
    app.set_theme("high-contrast")
```

**Benefits:**
- Accessibility compliance
- OS high contrast mode support
- WCAG AAA compliance

### Phase 4: Advanced Features (v2.0)

**Goal:** Enable advanced theming scenarios.

**Target Release:** Q2 2026

#### 4.1 Animated Theme Transitions

**Implementation:**
```python
class AnimatedThemeTransition:
    def transition(self, old_theme: Theme, new_theme: Theme, duration_ms: int):
        """Smoothly animate between themes."""
        # Interpolate colors
        steps = duration_ms // 16  # 60 FPS

        for i in range(steps):
            t = i / steps
            interpolated = self._interpolate_themes(old_theme, new_theme, t)
            self._apply_theme(interpolated)
            await asyncio.sleep(0.016)

# Usage:
await app.transition_theme("vscode", duration_ms=300)
```

**Benefits:**
- Smooth visual transitions
- Less jarring theme switches
- Modern UX

#### 4.2 Conditional Themes

**Implementation:**
```python
class ConditionalThemeManager:
    def add_condition(self, name: str, condition: Callable[[], bool], theme: str):
        """Apply theme based on condition."""
        self._conditions[name] = (condition, theme)

    def update_conditional_themes(self):
        """Check all conditions and apply appropriate theme."""
        for name, (condition, theme) in self._conditions.items():
            if condition():
                self.set_theme(theme)
                break

# Usage:
conditional = ConditionalThemeManager()
conditional.add_condition("night", lambda: datetime.now().hour >= 20, "dark")
conditional.add_condition("day", lambda: datetime.now().hour < 20, "light")
conditional.update_conditional_themes()  # Auto-switch based on time
```

**Benefits:**
- Time-based themes (day/night)
- Context-based themes (debugging, presenting)
- Location-based themes

#### 4.3 Theme Marketplace

**Implementation:**
```python
class ThemeMarketplace:
    def search_themes(self, query: str) -> List[ThemePackage]:
        """Search community themes."""
        return self._api.search(query)

    def install_theme(self, package: ThemePackage):
        """Install theme from marketplace."""
        theme_data = self._api.download(package.id)
        theme = Theme.from_dict(theme_data)
        self._repository.add_theme(theme)

# Usage:
marketplace = ThemeMarketplace()
results = marketplace.search_themes("dracula")
marketplace.install_theme(results[0])
app.set_theme("dracula")
```

**Benefits:**
- Community theme sharing
- Discover new themes
- Easy theme distribution

#### 4.4 Plugin Architecture

**Implementation:**
```python
class ThemePlugin(ABC):
    @abstractmethod
    def on_theme_loaded(self, theme: Theme):
        """Hook called when theme loads."""
        pass

    @abstractmethod
    def on_theme_applied(self, widget: ThemedWidget, theme: Theme):
        """Hook called when theme applies to widget."""
        pass

# Example: Syntax highlighting plugin
class SyntaxHighlightPlugin(ThemePlugin):
    def on_theme_loaded(self, theme: Theme):
        # Extract token colors
        self._token_colors = theme.token_colors

    def on_theme_applied(self, widget: ThemedWidget, theme: Theme):
        if isinstance(widget, QTextEdit):
            # Apply syntax highlighting
            highlighter = SyntaxHighlighter(widget.document())
            highlighter.set_colors(self._token_colors)
```

**Benefits:**
- Extensibility without modifying core
- Community plugins
- Domain-specific theming (code editors, design tools)

---

## Contributing

Want to help implement these features? See [CONTRIBUTING.md](../CONTRIBUTING.md) for development guidelines.

**Priority Areas:**
1. Performance optimization (Phase 1)
2. Better error messages (Phase 2)
3. Platform integration (Phase 3)

**Contact:** Open an issue or pull request on GitHub.

---

*This roadmap is a living document and will be updated as the system evolves.*
