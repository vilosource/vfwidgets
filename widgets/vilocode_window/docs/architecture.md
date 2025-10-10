# ViloCodeWindow Architecture

Internal architecture documentation for developers working on ViloCodeWindow.

---

## Table of Contents

- [Overview](#overview)
- [Design Philosophy](#design-philosophy)
- [Component Structure](#component-structure)
- [Core Subsystems](#core-subsystems)
- [Event Flow](#event-flow)
- [Platform Adaptation](#platform-adaptation)
- [Testing Strategy](#testing-strategy)
- [Extension Points](#extension-points)

---

## Overview

ViloCodeWindow is a VS Code-style application window widget built with PySide6. It provides a complete VS Code-like layout with activity bar, collapsible sidebar, main content area, auxiliary bar, and status bar.

**Key Design Goals**:
- **Dual-mode operation**: Works as frameless window or embedded widget
- **Clean API**: Simple, intuitive public interface
- **Component-based**: Modular, reusable components
- **Theme integration**: Optional vfwidgets-theme support
- **Platform agnostic**: Windows, macOS, Linux (X11/Wayland), WSL

---

## Design Philosophy

### 1. Adaptive Mode Pattern

The widget **automatically** detects its usage context and adapts behavior:

```python
def _detect_window_mode(self) -> WindowMode:
    """Detect if widget is top-level (frameless) or embedded."""
    if self.parent() is None:
        return WindowMode.Frameless
    else:
        return WindowMode.Embedded
```

**Frameless Mode** (no parent):
- Custom title bar with window controls
- Native window move/resize via Qt APIs
- Window decorations disabled
- Qt WindowFlags: `FramelessWindowHint`

**Embedded Mode** (has parent):
- Regular widget behavior
- No custom title bar
- No window controls
- Uses parent's window management

**Why**: Allows single class to work in both top-level and embedded contexts without API changes.

---

### 2. Component-Based Architecture

Each UI region is a separate component with clear responsibility:

```
ViloCodeWindow
├── components/
│   ├── activity_bar.py     - Vertical icon strip (left edge)
│   ├── sidebar.py          - Collapsible left panel (stackable)
│   ├── main_pane.py        - Central content container
│   ├── auxiliary_bar.py    - Collapsible right panel
│   ├── title_bar.py        - Custom title bar (frameless only)
│   └── window_controls.py  - Min/max/close buttons (frameless only)
└── core/
    ├── shortcut_manager.py - Keyboard shortcut system
    └── shortcuts.py        - Default shortcut definitions
```

**Component Responsibilities**:
- **ActivityBar**: Manages vertical icon buttons, handles click events, maintains active state
- **SideBar**: Manages stackable panels, handles visibility/width, smooth animations
- **MainPane**: Simple container for primary content widget
- **AuxiliaryBar**: Right-side panel with visibility/width management, smooth animations
- **TitleBar**: Window title, menu bar integration, drag-to-move handling
- **WindowControls**: Minimize, maximize/restore, close buttons

---

### 3. Optional Theme Integration

Uses **dynamic base class composition** to support optional theme system:

```python
try:
    from vfwidgets_theme import ThemedWidget
    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False
    ThemedWidget = object

# Dynamic base class
if THEME_AVAILABLE:
    _BaseClass = type("_BaseClass", (ThemedWidget, QWidget), {})
else:
    _BaseClass = QWidget

class ViloCodeWindow(_BaseClass):
    """Works with or without theme system."""
    theme_config = {
        "background": "editor.background",
        "titlebar_bg": "titleBar.activeBackground",
        # ... VS Code color tokens
    }
```

**Benefits**:
- Zero dependencies on theme system
- Automatic theming when available
- Fallback colors for standalone use
- No conditional imports in business logic

---

## Component Structure

### Visual Layout

```
┌────────────────────────────────────────────────────────────┐
│ TitleBar (frameless mode only)                    [─][□][×]│
│   ├── Title label                                           │
│   ├── Menu bar (optional)                                   │
│   └── Window controls                                       │
├─┬──────────┬──────────────────────────┬────────────────────┤
│A│          │                          │                    │
│c│  SideBar │      Main Pane           │   Auxiliary Bar    │
│t│  (250px) │   (flexible width)       │      (300px)       │
│i│          │                          │   [hidden by       │
│v│ Stacked  │  Developer content       │    default]        │
│i│ Panels   │  (QTextEdit, tabs,       │                    │
│t│          │   splits, etc.)          │                    │
│y│          │                          │                    │
│ │          │                          │                    │
│B│          │                          │                    │
│a│          │                          │                    │
│r│          │                          │                    │
│ │          │                          │                    │
│(│          │                          │                    │
│4│          │                          │                    │
│8│          │                          │                    │
│p│          │                          │                    │
│x│          │                          │                    │
│)│          │                          │                    │
├─┴──────────┴──────────────────────────┴────────────────────┤
│ Status Bar (QStatusBar, 22px height)                       │
└────────────────────────────────────────────────────────────┘
```

### Component Hierarchy

```python
ViloCodeWindow (QWidget or ThemedWidget + QWidget)
  └── QVBoxLayout (main vertical layout)
      ├── TitleBar (only in frameless mode)
      │   └── QHBoxLayout
      │       ├── QLabel (window title)
      │       ├── QMenuBar (optional, developer-provided)
      │       └── WindowControls
      │           ├── QPushButton (minimize)
      │           ├── QPushButton (maximize/restore)
      │           └── QPushButton (close)
      ├── QHBoxLayout (content layout)
      │   ├── ActivityBar (48px fixed width)
      │   ├── SideBar (150-500px resizable, collapsible)
      │   ├── MainPane (flexible width, stretch=1)
      │   └── AuxiliaryBar (150-500px resizable, hidden default)
      └── QStatusBar (22px fixed height)
```

---

## Core Subsystems

### 1. Window Management (Frameless Mode)

**Setup**:
```python
def _setup_frameless_window(self):
    """Configure frameless window with custom decorations."""
    # Remove native decorations
    self.setWindowFlags(
        Qt.WindowType.FramelessWindowHint |
        Qt.WindowType.WindowSystemMenuHint |
        Qt.WindowType.WindowMinMaxButtonsHint |
        Qt.WindowType.WindowCloseButtonHint
    )

    # Enable translucent background for rounded corners
    self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    # Enable mouse tracking for resize edges
    self.setMouseTracking(True)

    # Minimum size
    self.setMinimumSize(600, 400)
```

**Window Move** (drag title bar):
```python
def mousePressEvent(self, event):
    if event.button() == Qt.MouseButton.LeftButton:
        if self._is_in_title_bar(event.pos()):
            # Use native system move (Qt 6.5+)
            self.windowHandle().startSystemMove()
```

**Window Resize** (drag edges):
```python
def mousePressEvent(self, event):
    edge = self._get_resize_edge(event.pos())
    if edge != Qt.Edge.NoEdge:
        # Use native system resize (Qt 6.5+)
        self.windowHandle().startSystemResize(edge)
```

**Resize Edge Detection**:
- 5px margin around window edges
- Updates cursor shape based on edge (SizeHorCursor, SizeVerCursor, SizeFDiagCursor, etc.)
- Works with native resize on supported platforms

---

### 2. Sidebar & Auxiliary Bar Animations

**Smooth Collapse/Expand** (200ms OutCubic easing):

```python
def set_visible(self, visible: bool, animated: bool = True):
    """Show/hide sidebar with optional smooth animation."""
    if not animated:
        super().setVisible(visible)
        self.visibility_changed.emit(visible)
        return

    # Create animation if needed
    if self._animation is None:
        self._animation = QPropertyAnimation(self, b"maximumWidth", self)
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.finished.connect(self._on_animation_finished)

    # Store target visibility (no lambda to avoid segfaults)
    self._animating_to_visible = visible

    if visible:
        # Expand: 0 → last_width
        super().setVisible(True)
        self._animation.setStartValue(0)
        self._animation.setEndValue(self._last_width)
    else:
        # Collapse: last_width → 0
        self._last_width = self.width()
        self._animation.setStartValue(self._last_width)
        self._animation.setEndValue(0)

    self._animation.start()

def _on_animation_finished(self):
    """Handle animation completion."""
    if not self._animating_to_visible:
        super().setVisible(False)
        self.setMaximumWidth(self._last_width)
    else:
        self.setMaximumWidth(self._max_width)
    self.visibility_changed.emit(self._animating_to_visible)
```

**Key Implementation Details**:
- Uses instance variable `_animating_to_visible` instead of lambda closure (prevents segfaults)
- Animates `maximumWidth` property (not `width` directly)
- Remembers last width when collapsing
- Single `finished` slot connected once (not per animation)
- Emits `visibility_changed` signal after animation completes

---

### 3. Keyboard Shortcut System

**Architecture**:
```
ShortcutManager (core/shortcut_manager.py)
  ├── _shortcuts: Dict[str, QShortcut]  # Action name → shortcut
  ├── _callbacks: Dict[str, Callable]   # Action name → callback
  └── _descriptions: Dict[str, str]     # Action name → description

Default Shortcuts (core/shortcuts.py)
  └── DEFAULT_SHORTCUTS: Dict[str, str]  # Action name → key sequence
```

**Registration Flow**:
```python
# 1. ViloCodeWindow creates ShortcutManager
self._shortcut_manager = ShortcutManager(self)

# 2. Load default shortcuts (if enabled)
if enable_default_shortcuts:
    self._load_default_shortcuts()

# 3. Register callbacks for each action
def _load_default_shortcuts(self):
    for action, key_seq in DEFAULT_SHORTCUTS.items():
        self._shortcut_manager.register(key_seq, action)

    # Connect callbacks
    self._shortcut_manager.register_callback("TOGGLE_SIDEBAR", self.toggle_sidebar)
    self._shortcut_manager.register_callback("TOGGLE_AUXILIARY_BAR", self.toggle_auxiliary_bar)
    self._shortcut_manager.register_callback("FOCUS_SIDEBAR", self._focus_sidebar)
    # ... more callbacks
```

**Custom Shortcuts**:
```python
# Developer can register custom shortcuts
def register_shortcut(self, key_seq, callback, desc=""):
    shortcut = QShortcut(QKeySequence(key_seq), self)
    shortcut.activated.connect(callback)
    return shortcut
```

---

### 4. Activity Bar ↔ Sidebar Integration

**Signal-Based Communication**:

```python
# ActivityBar item clicked
self._activity_bar.item_clicked.connect(self._on_activity_item_clicked)

def _on_activity_item_clicked(self, item_id: str):
    """Forward activity item click as window signal."""
    self.activity_item_clicked.emit(item_id)

# Developer connects to window signal
window.activity_item_clicked.connect(
    lambda item_id: window.show_sidebar_panel(item_id)
)

# Sidebar panel changed
self._sidebar.panel_changed.connect(self._on_sidebar_panel_changed)

def _on_sidebar_panel_changed(self, panel_id: str):
    """Update activity bar when sidebar panel changes."""
    self.set_active_activity_item(panel_id)
    self.sidebar_panel_changed.emit(panel_id)
```

**Auto-Connect** (via `configure()`):
```python
if config.get("auto_connect", False):
    # Automatically connect activity items to panels with matching IDs
    for item in activity_items:
        item_id = item["id"]
        action = self.get_activity_action(item_id)
        action.triggered.connect(
            lambda checked, pid=item_id: self.show_sidebar_panel(pid)
        )
```

---

## Event Flow

### Initialization Sequence

```
1. __init__(parent, enable_default_shortcuts)
   ↓
2. _detect_window_mode()
   - Checks if parent is None
   - Sets self._window_mode
   ↓
3. _setup_frameless_window() [if frameless]
   - Sets window flags
   - Enables translucent background
   - Minimum size, mouse tracking
   ↓
4. _setup_ui()
   - Creates main layout (QVBoxLayout)
   - Adds title bar (frameless only)
   - Creates content layout (QHBoxLayout)
   - Adds ActivityBar, SideBar, MainPane, AuxiliaryBar
   - Adds status bar
   - Sets object names for accessibility
   ↓
5. _apply_theme_colors() [if theme available]
   - Applies theme colors to components
   ↓
6. _setup_default_shortcuts() [if enabled]
   - Creates ShortcutManager
   - Registers default shortcuts
   - Connects callbacks
```

---

### Theme Change Event Flow

```
ThemeManager.theme_changed signal
  ↓
ThemedWidget.on_theme_changed(theme_name)
  ↓
ViloCodeWindow.on_theme_changed(theme_name)
  ↓
self._apply_theme_colors()
  ↓
Components update colors
  ↓
self.update() [repaint in frameless mode]
```

---

### Sidebar Toggle Event Flow

```
User presses Ctrl+B
  ↓
QShortcut.activated signal
  ↓
ShortcutManager callback lookup
  ↓
ViloCodeWindow.toggle_sidebar()
  ↓
SideBar.set_visible(not is_visible, animated=True)
  ↓
QPropertyAnimation starts (200ms)
  ↓
Animation updates maximumWidth property
  ↓
Animation.finished signal
  ↓
SideBar._on_animation_finished()
  ↓
SideBar.visibility_changed signal
  ↓
ViloCodeWindow.sidebar_visibility_changed signal
```

---

## Platform Adaptation

### Platform Detection

Uses `platform_support/` module for platform-specific behavior:

```python
from vfwidgets_vilocode_window.platform_support import (
    get_platform_capabilities,
    PlatformCapabilities
)

caps = get_platform_capabilities()
# PlatformCapabilities(
#     supports_frameless=True,
#     supports_system_move=True,
#     supports_system_resize=True,
#     ...
# )
```

### Platform-Specific Behaviors

**Windows**:
- Full frameless support
- Native Aero snap works with `startSystemResize()`
- Custom window controls required

**macOS**:
- Full frameless support
- Native fullscreen transitions
- Custom window controls required
- Unified title bar/toolbar area

**Linux X11**:
- Full frameless support
- Window manager integration varies
- Custom window controls required

**Linux Wayland**:
- Compositor-dependent support
- Requires Qt 6.5+ for proper support
- Some window managers may not support frameless

**WSL/WSLg**:
- Prefers native decorations (fallback mode)
- Frameless may be unreliable depending on X server

### Fallback Strategy

```python
if not caps.supports_frameless:
    # Use native decorations
    # Place menu bar below native title bar
```

---

## Testing Strategy

### Test Categories

1. **Unit Tests** (`tests/test_*.py`):
   - Component creation
   - API method behavior
   - Signal emission
   - Widget ownership/lifecycle

2. **Integration Tests** (`tests/test_component_integration.py`):
   - Activity bar ↔ sidebar interaction
   - Signal flow between components
   - Theme system integration
   - Multiple components working together

3. **Example Tests** (`examples/*.py`):
   - Each example must run successfully
   - Examples serve as integration tests
   - Validates real-world usage patterns

### Test Infrastructure

```python
# pytest with pytest-qt plugin
import pytest
from pytestqt.qt_compat import qt_api

@pytest.fixture
def window(qtbot):
    """Create ViloCodeWindow for testing."""
    w = ViloCodeWindow()
    qtbot.addWidget(w)
    return w

def test_toggle_sidebar(window, qtbot):
    """Test sidebar toggle with signal."""
    with qtbot.waitSignal(window.sidebar_visibility_changed, timeout=1000):
        window.set_sidebar_visible(False, animated=False)

    assert not window.is_sidebar_visible()
```

**Key Testing Patterns**:
- Use `animated=False` in tests to avoid timing issues
- Use `qtbot.waitSignal()` for signal testing
- Use `qtbot.addWidget()` for proper cleanup
- Test with and without theme system available

---

## Extension Points

### 1. Custom Components

Replace placeholder components with custom implementations:

```python
# Create custom sidebar with additional features
class MySidebar(SideBar):
    def __init__(self):
        super().__init__()
        # Add custom behavior

# Replace in ViloCodeWindow (requires modifying source)
self._sidebar = MySidebar()
```

### 2. Theme Customization

Define custom theme mappings:

```python
class MyViloCodeWindow(ViloCodeWindow):
    theme_config = {
        **ViloCodeWindow.theme_config,  # Inherit defaults
        "custom_color": "my.custom.token",  # Add custom
    }
```

### 3. Keyboard Shortcuts

Override default shortcuts or add custom ones:

```python
# Disable defaults, add custom
window = ViloCodeWindow(enable_default_shortcuts=False)
window.register_shortcut("Ctrl+H", show_help, "Show help")
window.register_shortcut("Ctrl+P", show_palette, "Command palette")

# Or override specific defaults
window = ViloCodeWindow()
window.set_shortcut("TOGGLE_SIDEBAR", "Ctrl+Shift+B")
```

### 4. Signal Connections

Connect to window signals for custom behavior:

```python
def on_activity_clicked(item_id: str):
    print(f"Activity: {item_id}")
    # Custom logic here

window.activity_item_clicked.connect(on_activity_clicked)
window.sidebar_panel_changed.connect(on_panel_changed)
window.sidebar_visibility_changed.connect(on_sidebar_toggled)
```

---

## Performance Considerations

### Layout Updates

- Use `batch_updates()` context manager when adding many items
- Defers layout recalculation until context exits
- Can improve performance 10-20x for bulk additions

### Animation Performance

- 200ms animations use OutCubic easing (smooth, natural)
- Animates `maximumWidth` (cheap) not `width` (expensive)
- No layout recalculation during animation
- Single animation instance reused (no allocation per toggle)

### Memory Management

- Qt parent-child ownership used throughout
- Widgets reparented when added to panels
- Removed widgets have parent cleared but not deleted
- No circular references between components

---

## Future Enhancements (v2.0+)

Planned features for future versions:

1. **Persistence**:
   - Save/restore layout state
   - Remember sidebar width, panel selection
   - JSON-based configuration

2. **Dockable Panels**:
   - Drag panels to different areas
   - Floating panels (separate windows)
   - Split sidebar (multiple panels visible)

3. **Tab Groups**:
   - Horizontal tabs in sidebar
   - Multiple tab groups (like VS Code outline + timeline)

4. **Plugin System**:
   - Extension points for third-party panels
   - Plugin lifecycle management

---

## See Also

- [api.md](api.md) - Complete API reference
- [theme.md](theme.md) - Theme integration guide
- [vilocode-window-SPECIFICATION.md](vilocode-window-SPECIFICATION.md) - Full specification
- [../../theme_system/README.md](../../theme_system/README.md) - Theme system documentation
