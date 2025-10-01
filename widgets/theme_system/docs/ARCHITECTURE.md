# VFWidgets Theme System - Architecture

This document describes the **actual implemented architecture** of the VFWidgets Theme System.

**Related Documents:**
- [ROADMAP.md](ROADMAP.md) - Design rationale and future enhancements
- [api-REFERENCE.md](api-REFERENCE.md) - User-facing API documentation
- [quick-start-GUIDE.md](quick-start-GUIDE.md) - Getting started guide

---

## Table of Contents

1. [Overview](#overview)
2. [Design Philosophy](#design-philosophy)
3. [System Layers](#system-layers)
4. [Core Components](#core-components)
5. [Data Flow](#data-flow)
6. [Architecture Patterns](#architecture-patterns)

---

## Overview

The VFWidgets Theme System provides comprehensive theming for PySide6/Qt applications through a clean, performance-first architecture.

**Key Statistics:**
- 69 Python files across 19 modules
- 197 theme tokens (192 colors + 5 fonts)
- < 100ms theme switching (100+ widgets)
- < 1KB memory overhead per widget
- Thread-safe by design

**Primary API:**
```python
from vfwidgets_theme import ThemedWidget, ThemedApplication

class MyWidget(ThemedWidget, QWidget):
    theme_config = {
        'bg': 'window.background',
        'fg': 'window.foreground'
    }

app = ThemedApplication(sys.argv)
app.set_theme("vscode")  # Instant theme switching
```

---

## Design Philosophy

### "ThemedWidget is THE Way"

**Simple API, Complex Internals**

Users inherit from `ThemedWidget` and get:
- ✅ Automatic theme registration
- ✅ Memory leak prevention (WeakRef tracking)
- ✅ Thread-safe updates (Qt signals)
- ✅ Property caching for performance
- ✅ Error recovery with fallbacks
- ✅ Zero configuration required

Behind this simple API:
- Dependency injection for testability
- Protocol-based clean architecture
- Immutable data structures for thread safety
- Multi-layered caching
- Comprehensive lifecycle management

> **Why this architecture?** See [ROADMAP.md > Design Rationale](ROADMAP.md#design-rationale)

### Progressive Enhancement

```
Level 1: class MyWidget(ThemedQWidget)
         → Automatic theming, zero config

Level 2: theme_config = {'bg': 'window.background'}
         → Custom property mapping

Level 3: def on_theme_changed(self): ...
         → React to theme changes

Level 4: Access internal components for advanced use
         → Full architectural control
```

---

## System Layers

The system is organized into clear architectural layers:

```
┌─────────────────────────────────────────────────┐
│ USER LAYER                                      │
│  ThemedWidget, ThemedApplication                │
│  (Simple API - "THE Way")                       │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│ WIDGET LAYER                                    │
│  base.py: ThemedWidget core implementation      │
│  convenience.py: ThemedQWidget, ThemedMainWindow │
│  application.py: ThemedApplication              │
│  stylesheet_generator.py: Qt CSS generation     │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│ CORE SYSTEM                                     │
│  manager.py: ThemeManager (Facade)              │
│  repository.py: Theme storage/retrieval         │
│  applicator.py: Theme application               │
│  provider.py: Cached theme data access          │
│  registry.py: Widget tracking (WeakRefs)        │
│  notifier.py: Change notifications              │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│ FOUNDATION                                      │
│  theme.py: Immutable Theme, ThemeBuilder        │
│  tokens.py: ColorTokenRegistry (197 tokens)     │
│  protocols.py: Type protocols for DI            │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│ SUPPORT SYSTEMS                                 │
│  lifecycle.py: Widget lifecycle management      │
│  threading.py: Thread-safe operations           │
│  errors.py: Exception hierarchy + recovery      │
│  fallbacks.py: Fallback colors + minimal theme  │
│  logging.py: Logging + performance tracking     │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│ EXTENSIONS                                      │
│  vscode/: VSCode theme import                   │
│  validation/: Theme validation                  │
│  testing/: Test infrastructure                  │
└─────────────────────────────────────────────────┘
```

> **Future enhancements:** See [ROADMAP.md > Future Enhancements](ROADMAP.md#future-enhancements)

---

## Core Components

### ThemedWidget

**Location:** `src/vfwidgets_theme/widgets/base.py:454`

**Purpose:** Primary user-facing API - the mixin class that makes widgets themeable.

**Key Features:**
- Metaclass-based for multiple inheritance support
- Automatic registration with ThemeWidgetRegistry
- Property caching via ThemePropertiesManager
- Theme access through proxy object
- Lifecycle integration with WeakRef cleanup

**Implementation:**
```python
class ThemedWidget(metaclass=ThemedWidgetMeta):
    """The primary API for creating themed widgets."""

    theme_config = {}  # User-defined property mapping

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

        # Unique ID for tracking
        self._widget_id = str(uuid.uuid4())

        # Dependency injection
        self._theme_manager = None  # Injected on first use
        self._lifecycle_manager = None
        self._thread_manager = None

        # Property access
        self._theme_properties = ThemePropertiesManager(self)
        self.theme = ThemeAccess(self)  # Proxy for theme.property access

        # Registration happens automatically
        self._setup_widget()

    def on_theme_changed(self):
        """Override to react to theme changes."""
        pass
```

> **Why a mixin?** See [ROADMAP.md > Why ThemedWidget is a Mixin](ROADMAP.md#why-themedwidget-is-a-mixin)

### ThemeManager

**Location:** `src/vfwidgets_theme/core/manager.py:76`

**Purpose:** Facade that coordinates all theme system components.

**Coordinated Components:**
- **ThemeRepository**: Theme storage and retrieval
- **ThemeApplicator**: Theme application to widgets/app
- **ThemeNotifier**: Change notifications to subscribers
- **DefaultThemeProvider**: Cached theme data access
- **ThemeWidgetRegistry**: Widget registration/tracking
- **LifecycleManager**: Widget lifecycle management (optional)
- **ThreadSafeThemeManager**: Thread-safe operations (optional)

**Singleton Pattern:**
```python
class ThemeManager:
    _instance = None
    _instance_lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> 'ThemeManager':
        """Thread-safe singleton access."""
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:  # Double-checked locking
                    cls._instance = create_theme_manager()
        return cls._instance
```

**Key Methods:**
```python
def set_theme(self, theme_name: str) -> bool:
    """Switch to theme by name."""
    theme = self._repository.get_theme(theme_name)
    self._current_theme = theme
    self._applicator.apply_to_all_widgets(theme)
    self._notifier.notify_theme_changed(theme)
    return True

def list_themes(self) -> List[str]:
    """Get available theme names."""
    return self._repository.list_themes()

def register_widget(self, widget: ThemedWidget) -> None:
    """Register widget for theme updates."""
    self._widget_registry.register(widget)
```

> **Why a facade?** See [ROADMAP.md > Why ThemeManager is a Facade](ROADMAP.md#why-thememanager-is-a-facade)

### Theme (Immutable Data Model)

**Location:** `src/vfwidgets_theme/core/theme.py:68`

**Purpose:** Immutable, validated theme data structure.

**Structure:**
```python
@dataclass(frozen=True)
class Theme:
    """Immutable theme data."""
    name: str
    version: str = "1.0.0"
    colors: Dict[str, str] = field(default_factory=dict)  # 197 tokens
    styles: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    token_colors: List[Dict[str, Any]] = field(default_factory=list)
    type: str = "light"  # "light", "dark", or "high-contrast"

    def get(self, key: str, default: Any = None) -> Any:
        """Get property with fallback chain."""
        # 1. Check colors
        if key in self.colors:
            return self.colors[key]
        # 2. Check styles
        if key in self.styles:
            return self.styles[key]
        # 3. Return default
        return default
```

**Creation via ThemeBuilder:**
```python
theme = (ThemeBuilder("my_theme")
    .set_type("dark")
    .add_color("colors.foreground", "#e0e0e0")
    .add_color("colors.background", "#1e1e1e")
    .add_metadata("description", "My custom theme")
    .build())  # Returns immutable Theme
```

> **Why immutable?** See [ROADMAP.md > Why Themes are Immutable](ROADMAP.md#why-themes-are-immutable)

### ThemeWidgetRegistry

**Location:** `src/vfwidgets_theme/core/registry.py:98`

**Purpose:** Track registered widgets using WeakRefs for automatic cleanup.

**Implementation:**
```python
class ThemeWidgetRegistry:
    """Tracks widgets with automatic cleanup."""

    def __init__(self):
        self._widgets: Dict[str, weakref.ref] = {}  # widget_id → WeakRef
        self._by_type: Dict[Type, Set[str]] = {}    # Type → widget_ids
        self._lock = threading.RLock()

    def register(self, widget: ThemedWidget) -> None:
        """Register widget with WeakRef tracking."""
        with self._lock:
            widget_id = widget._widget_id

            # Store WeakRef with cleanup callback
            def cleanup():
                self._unregister_id(widget_id)

            self._widgets[widget_id] = weakref.ref(widget, cleanup)

            # Index by type
            widget_type = type(widget)
            if widget_type not in self._by_type:
                self._by_type[widget_type] = set()
            self._by_type[widget_type].add(widget_id)

    def get_all_widgets(self) -> List[ThemedWidget]:
        """Get all live widgets."""
        with self._lock:
            live = []
            for widget_ref in self._widgets.values():
                widget = widget_ref()  # Dereference WeakRef
                if widget is not None:
                    live.append(widget)
            return live
```

> **Why WeakRefs?** See [ROADMAP.md > Why WeakRef Widget Registry](ROADMAP.md#why-weakref-widget-registry)

### ThemeApplicator

**Location:** `src/vfwidgets_theme/core/applicator.py:743`

**Purpose:** Apply themes to widgets and application.

**Sub-Components:**
- `WidgetThemeApplicator` (line 85): Apply to individual widgets
- `ApplicationThemeApplicator` (line 294): Apply to QApplication palette
- `AsyncThemeApplicator` (line 560): Async theme operations

**Implementation:**
```python
class ThemeApplicator:
    """Coordinates theme application."""

    def __init__(self, widget_registry: ThemeWidgetRegistry):
        self._widget_registry = widget_registry
        self._widget_applicator = WidgetThemeApplicator()
        self._app_applicator = ApplicationThemeApplicator()

    def apply_to_all_widgets(self, theme: Theme) -> None:
        """Apply theme to all registered widgets."""
        widgets = self._widget_registry.get_all_widgets()

        for widget in widgets:
            self._widget_applicator.apply_to_widget(widget, theme)

        # Also update application palette
        self._app_applicator.apply_to_application(theme)
```

> **Future optimization:** See [ROADMAP.md > Batch Theme Application](ROADMAP.md#11-batch-theme-application)

### StylesheetGenerator

**Location:** `src/vfwidgets_theme/widgets/stylesheet_generator.py:38`

**Purpose:** Generate comprehensive Qt stylesheets from themes.

**Coverage:**
- 11 widget categories (buttons, inputs, lists, tables, menus, etc.)
- All pseudo-states (`:hover`, `:pressed`, `:disabled`, `:focus`, `:checked`)
- Role markers (`[role="danger"]`, `[role="editor"]`)
- Descendant selectors for automatic child widget theming

**Implementation:**
```python
class StylesheetGenerator:
    """Generates comprehensive Qt stylesheets."""

    def __init__(self, theme: Theme, widget_class_name: str):
        self.theme = theme
        self.widget_class_name = widget_class_name  # Used for descendant selectors

    def generate_comprehensive_stylesheet(self) -> str:
        """Generate complete stylesheet for all child widgets."""
        sections = [
            self._generate_widget_styles(),      # Widget itself
            self._generate_button_styles(),      # QPushButton, QToolButton, etc
            self._generate_input_styles(),       # QLineEdit, QTextEdit, etc
            self._generate_list_styles(),        # QListWidget, QTreeWidget, etc
            self._generate_combo_styles(),       # QComboBox
            self._generate_tab_styles(),         # QTabWidget, QTabBar
            self._generate_menu_styles(),        # QMenuBar, QMenu
            self._generate_scrollbar_styles(),   # QScrollBar
            self._generate_container_styles(),   # QGroupBox, QFrame, etc
            self._generate_text_styles(),        # QLabel
            self._generate_misc_styles(),        # QProgressBar, QSlider
        ]

        return "\n\n".join(s for s in sections if s)

    def _generate_button_styles(self) -> str:
        """Generate button styles with all pseudo-states."""
        prefix = self.widget_class_name
        bg = self.theme.get('button.background', '#0e639c')
        fg = self.theme.get('button.foreground', '#ffffff')
        hover_bg = self.theme.get('button.hoverBackground', '#1177bb')
        pressed_bg = self.theme.get('button.pressedBackground', '#094771')

        return f"""
/* Buttons */
{prefix} QPushButton {{
    background-color: {bg};
    color: {fg};
    border: none;
    padding: 5px 15px;
}}
{prefix} QPushButton:hover {{
    background-color: {hover_bg};
}}
{prefix} QPushButton:pressed {{
    background-color: {pressed_bg};
}}
{prefix} QPushButton[role="danger"] {{
    background-color: {self.theme.get('button.danger.background', '#dc3545')};
}}
"""
```

> **Why stylesheets vs runtime?** See [ROADMAP.md > Why StylesheetGenerator](ROADMAP.md#why-stylesheetgenerator-vs-runtime-properties)

### ColorTokenRegistry

**Location:** `src/vfwidgets_theme/core/tokens.py`

**Purpose:** Central registry of all 197 theme tokens with smart defaults.

**Token Categories:**
- Base colors (11): `colors.*`
- Buttons (18): `button.*`
- Inputs (18): `input.*`
- Editor (35): `editor.*`
- Lists/Trees (22): `list.*`, `tree.*`
- Tables (10): `table.*`
- Tabs (17): `tab.*`
- Menus (11): `menu.*`
- Panels (8): `panel.*`
- Status bar (11): `statusBar.*`
- Fonts (14): `font.*`
- Others (22): `scrollbar.*`, `progressBar.*`, etc.

**Smart Defaults:**
```python
class ColorTokenRegistry:
    """Registry with intelligent fallbacks."""

    _DEFAULTS = {
        # Colors
        'colors.foreground': '#000000',
        'colors.background': '#ffffff',
        'colors.primary': '#007acc',

        # Fonts
        'font.default.family': 'Arial, sans-serif',
        'font.default.size': '9pt',
        'font.editor.family': 'Courier New, monospace',
        'font.editor.size': '11pt',

        # ... 197 total tokens
    }

    def get(self, key: str, theme: Theme) -> Any:
        """Get token with fallback chain."""
        # 1. Theme value
        value = theme.get(key)
        if value is not None:
            return value

        # 2. Registry default
        if key in self._DEFAULTS:
            return self._DEFAULTS[key]

        # 3. Smart default based on key name
        return self._get_smart_default(key)
```

---

## Data Flow

### Theme Loading Flow

```
1. User: app.load_theme_file("custom.json")
         ↓
2. File loading: Read JSON from disk
         ↓
3. Validation: Validate structure and colors
         ↓
4. Theme creation: Theme.from_dict(data)
         ↓
5. Storage: repository.add_theme(theme)
         ↓
6. Ready: Theme available via list_themes()
```

> **Future enhancement:** See [ROADMAP.md > Lazy Theme Loading](ROADMAP.md#12-lazy-theme-loading)

### Theme Switching Flow

```
1. User: app.set_theme("vscode")
         ↓
2. Manager: Retrieve theme from repository
         ↓
3. Manager: Set as current theme
         ↓
4. Applicator: For each registered widget:
    ├─ Generate stylesheet (StylesheetGenerator)
    ├─ Apply stylesheet (widget.setStyleSheet())
    └─ Call widget.on_theme_changed()
         ↓
5. Applicator: Update application palette
         ↓
6. Notifier: Emit theme_changed signal
         ↓
7. Complete: All widgets now using new theme
```

**Performance:** ~100ms for 100 widgets

> **Future optimization:** See [ROADMAP.md > Batch Application](ROADMAP.md#11-batch-theme-application)

### Widget Registration Flow

```
1. Widget creation: MyWidget(ThemedWidget, QWidget)
         ↓
2. ThemedWidget.__init__: Initialize theme system
         ↓
3. Registration: manager.register_widget(self)
         ↓
4. Registry: Store WeakRef with cleanup callback
         ↓
5. Ready: Widget receives theme updates
         ↓
...
         ↓
Widget destroyed: WeakRef callback automatically unregisters
```

> **Why WeakRefs?** See [ROADMAP.md > WeakRef Registry](ROADMAP.md#why-weakref-widget-registry)

### Property Access Flow

```
1. User code: color = self.theme.background
         ↓
2. ThemeAccess proxy: __getattr__("background")
         ↓
3. ThemePropertiesManager: Resolve property
         ↓
4. Cache check: Is "background" cached?
    ├─ Yes: Return cached value (sub-microsecond)
    └─ No: Continue to resolution
         ↓
5. Property resolution:
    ├─ Check theme_config mapping
    ├─ Resolve to token (e.g., "window.background")
    ├─ Get from theme.colors
    └─ Fall back to ColorTokenRegistry default
         ↓
6. Cache result
         ↓
7. Return value
```

**Performance:** Cached access < 1 microsecond

---

## Architecture Patterns

### Dependency Injection

**All components are injectable for testing:**

```python
# Production
manager = ThemeManager(
    repository=ThemeRepository(),
    applicator=ThemeApplicator(registry),
    notifier=ThemeNotifier(),
    provider=DefaultThemeProvider(),
    widget_registry=ThemeWidgetRegistry()
)

# Testing
manager = ThemeManager(
    repository=MockRepository(),
    applicator=MockApplicator(),
    notifier=MockNotifier(),
    provider=MockProvider(),
    widget_registry=MockRegistry()
)
```

**Protocols define interfaces:**

```python
class ThemeProvider(Protocol):
    """Interface for theme data access."""
    def get_current_theme(self) -> Theme: ...
    def get_property(self, key: str) -> Any: ...

# Multiple implementations
class DefaultThemeProvider: ...     # Production
class CachedThemeProvider: ...      # With caching
class MockThemeProvider: ...        # For testing
```

### Facade Pattern

**ThemeManager hides internal complexity:**

```python
# User sees:
manager = ThemeManager.get_instance()
manager.set_theme("vscode")

# Behind the facade:
theme = self._repository.get_theme("vscode")
self._current_theme = theme
self._applicator.apply_to_all_widgets(theme)
self._applicator.apply_to_application(theme)
self._notifier.notify_theme_changed(theme)
```

> **Why?** See [ROADMAP.md > Why Facade](ROADMAP.md#why-thememanager-is-a-facade)

### Immutable Data

**Themes are frozen dataclasses:**

```python
@dataclass(frozen=True)
class Theme:
    name: str
    colors: Dict[str, str]
    # ... other fields

# Cannot modify
theme.colors["button.background"] = "#red"  # ❌ AttributeError

# Create new via builder
new_theme = ThemeBuilder.from_theme(theme)
    .add_color("button.background", "#red")
    .build()  # New immutable instance
```

**Benefits:**
- Thread-safe without locks
- Safe to cache
- Predictable behavior

> **Why?** See [ROADMAP.md > Why Immutable](ROADMAP.md#why-themes-are-immutable)

### WeakRef Memory Management

**Registry uses weak references:**

```python
class ThemeWidgetRegistry:
    def __init__(self):
        self._widgets: Dict[str, weakref.ref] = {}

    def register(self, widget: ThemedWidget):
        def cleanup():
            del self._widgets[widget._widget_id]

        self._widgets[widget._widget_id] = weakref.ref(widget, cleanup)
```

**Benefits:**
- Automatic cleanup
- No memory leaks
- No manual unregistration needed

> **Why?** See [ROADMAP.md > Why WeakRefs](ROADMAP.md#why-weakref-widget-registry)

### Signal/Slot Thread Safety

**Qt signals for cross-thread communication:**

```python
class ThemedWidget(QObject):
    theme_changed = Signal(str)  # Theme name

    def _on_theme_changed_internal(self, theme: Theme):
        # This can be called from any thread
        # Qt marshals to widget's thread automatically
        self.theme_changed.emit(theme.name)
```

**Benefits:**
- Thread-safe by design
- No manual thread marshaling
- Leverages Qt's event loop

---

## Module Organization

**Complete module listing:**

```
vfwidgets_theme/
├── __init__.py               # Public API exports
├── protocols.py              # Type protocols for DI
├── errors.py                 # Exception hierarchy + ErrorRecoveryManager
├── fallbacks.py              # FallbackColorSystem, MINIMAL_THEME
├── logging.py                # ThemeLogger, PerformanceTracker
├── lifecycle.py              # LifecycleManager (widget lifecycle)
├── threading.py              # ThreadSafeThemeManager
│
├── core/                     # Core system (9 files)
│   ├── manager.py            # ThemeManager (facade)
│   ├── repository.py         # ThemeRepository (storage)
│   ├── applicator.py         # ThemeApplicator (application)
│   ├── provider.py           # DefaultThemeProvider (cached access)
│   ├── registry.py           # ThemeWidgetRegistry (WeakRefs)
│   ├── notifier.py           # ThemeNotifier (change notifications)
│   ├── theme.py              # Theme, ThemeBuilder
│   ├── tokens.py             # ColorTokenRegistry
│   └── __init__.py
│
├── widgets/                  # Widget layer (7 files)
│   ├── base.py               # ThemedWidget (main mixin)
│   ├── convenience.py        # ThemedQWidget, ThemedMainWindow, etc
│   ├── application.py        # ThemedApplication
│   ├── stylesheet_generator.py  # StylesheetGenerator
│   ├── properties.py         # Property utilities
│   ├── mixins.py             # Additional capabilities
│   └── __init__.py
│
├── vscode/                   # VSCode theme import (3 files)
│   ├── importer.py           # VSCode JSON → Theme
│   ├── marketplace.py        # VSCode marketplace integration
│   └── __init__.py
│
├── validation/               # Theme validation (6 files)
│   └── ...
│
├── testing/                  # Test infrastructure (5 files)
│   ├── mocks.py              # Mock implementations
│   ├── utils.py              # ThemedTestCase
│   ├── benchmarks.py         # Performance testing
│   └── ...
│
└── [other modules]           # Extensions, utilities, etc
    ├── development/          # Hot reload, dev tools
    ├── extensions/           # Extension API
    ├── factory/              # Factory functions
    ├── importers/            # Other importers
    ├── mapping/              # Property mapping
    ├── packages/             # Theme packages
    ├── patterns/             # Design patterns
    ├── persistence/          # Storage
    ├── properties/           # Property system
    ├── syntax/               # Syntax highlighting
    └── utils/                # Utilities
```

---

## Performance Characteristics

**Measured performance (100 widgets):**
- Theme switch: ~100ms
- Property access (cached): < 1μs
- Widget registration: ~10μs
- Memory overhead: < 1KB per widget

**Caching Strategy:**
- L1: Property value cache (per widget)
- Future: L2/L3 caches ([ROADMAP.md](ROADMAP.md#13-stylesheet-caching))

---

## Testing Architecture

**Test infrastructure in `testing/`:**

```python
from vfwidgets_theme.testing import ThemedTestCase, MockThemeProvider

class TestMyWidget(ThemedTestCase):
    def test_theme_property(self):
        widget = MyWidget()
        self.assert_theme_property(widget, 'background', '#1e1e1e')

    def test_with_mock(self):
        mock = MockThemeProvider({'button.background': '#ff0000'})
        widget = MyWidget()
        widget._theme_provider = mock  # Inject mock
        assert widget.theme.background == '#ff0000'
```

---

## Summary

The VFWidgets Theme System architecture prioritizes:
1. **Simple API** - ThemedWidget is THE way
2. **Clean Architecture** - Dependency injection, protocols, separation of concerns
3. **Performance** - Caching, efficient stylesheets, minimal overhead
4. **Safety** - Immutable data, WeakRefs, thread-safe by design
5. **Extensibility** - Protocol-based, testable, injectable

**Future enhancements:** See [ROADMAP.md](ROADMAP.md) for planned improvements and design rationale.

---

*This architecture document describes the system as implemented. For future plans, see [ROADMAP.md](ROADMAP.md).*
