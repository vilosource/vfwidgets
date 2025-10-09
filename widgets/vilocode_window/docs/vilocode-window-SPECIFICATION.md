# ViloCodeWindow — Full Requirements Specification (v1.0)

## Version Scope

**v1.0 Focus**: This specification defines ViloCodeWindow v1.0, which provides:
- VS Code-style window layout (activity bar, sidebar, main pane, auxiliary bar, status bar)
- Dual-mode operation (frameless top-level or embedded widget)
- Fully customizable by developers (no built-in content)
- Theme system integration
- Platform-aware window management (Windows, macOS, Linux, WSL)

Future versions (v2.0+) will add persistence, advanced layouts, and additional features while maintaining backward compatibility.

## 1) Purpose

* Provide a reusable, VS Code-style **application window** component that developers can customize for their IDE, terminal, or application needs.
* Offer a unified layout structure with activity bar, sidebar, main pane, and optional auxiliary bar.
* Support both frameless (top-level) and embedded modes automatically.

## 2) Scope

* Single class that operates in two modes:
  1. **Top-level mode:** Frameless window (when supported) with custom title bar (menu bar + window buttons), native move/resize.
  2. **Embedded mode:** Acts like a regular widget with the same layout, no window controls, no window move/resize.
* No business logic or content widgets included — developers provide all content.
* Focus on layout structure and developer experience.

## 3) Non-Goals

* No built-in file explorer, search, or editor components.
* No persistence in v1.0 (planned for v2.0).
* No plugin system in v1.0.
* No dockable/floating panels in v1.0 (sidebar is stackable only).

## 4) Platforms & Compatibility

* Qt/PySide6 on Windows, macOS, Linux (Wayland & X11), including WSL/WSLg.
* High-DPI/Per-monitor DPI supported.
* Keyboard/mouse/trackpad parity with native Qt widgets.
* Reuses ChromeTabbedWindow's platform detection and adaptation.

## 5) Dependencies & Runtime

* Qt/PySide6 **6.5+** (prefer 6.6+) for `startSystemMove`/`startSystemResize`.
* Optional: `vfwidgets-theme` for automatic theming.
* No other third-party libraries.

## 6) Layout Structure

```
┌──────────────────────────────────────────────────────────────┐
│ MenuBar (optional)              [Minimize] [Maximize] [Close] │ ← Same height
├─┬─────────┬─────────────────────────────────┬────────────────┤
│A│         │                                 │                │
│c│ Sidebar │         Main Pane               │  Auxiliary Bar │
│t│ (Left)  │    (Developer Content)          │     (Right)    │
│i│         │                                 │    [Hidden]    │
│v│ Stacked │                                 │                │
│i│ Panels  │                                 │                │
│t│         │                                 │                │
│y│         │                                 │                │
│ │         │                                 │                │
│B│         │                                 │                │
│a│         │                                 │                │
│r│         │                                 │                │
├─┴─────────┴─────────────────────────────────┴────────────────┤
│ Status Bar (QStatusBar, optional)                            │
└──────────────────────────────────────────────────────────────┘
```

### Component Descriptions

#### Activity Bar (Left Edge, Vertical)
- Vertical strip with icon buttons
- Developer adds items via `add_activity_item(id, icon, tooltip)`
- Returns `QAction` for developer to connect signals
- Only one item can be "active" (highlighted) at a time
- Fixed width (~48px like VS Code)

#### Sidebar (Left Panel, Collapsible)
- Contains stackable panels (one visible at a time)
- Developer adds panels via `add_sidebar_panel(id, widget, title)`
- Panel header shows title (e.g., "EXPLORER", "SEARCH")
- Can be toggled visible/hidden
- Resizable width (user can drag border)

#### Main Pane (Center)
- Single content area
- Developer sets content via `set_main_content(widget)`
- Can contain any Qt widget:
  - `ChromeTabbedWindow` (embedded) for tabs
  - `MultisplitWidget` for split panes
  - `QTextEdit` for simple editor
  - Custom widget for app-specific UI

#### Auxiliary Bar (Right Panel, Optional)
- Similar to sidebar but on right side
- Hidden by default
- Single content widget (not stackable)
- Developer sets content via `set_auxiliary_content(widget)`
- Can be toggled visible/hidden
- Resizable width

#### Menu Bar (Top Bar, Frameless Mode)
- Standard `QMenuBar` in custom title bar
- Developer provides via `set_menu_bar(menubar)`
- Same height as window controls
- In embedded mode, appears at top of widget

#### Status Bar (Bottom)
- Standard `QStatusBar`
- Developer accesses via `get_status_bar()`
- Uses standard Qt APIs to add widgets/messages
- Styled like VS Code (height, colors from theme)

## 7) Public API

### Core Widget

```python
class ViloCodeWindow(QWidget):
    """VS Code-style application window.

    Automatically detects mode:
    - No parent → frameless top-level window
    - Has parent → embedded widget
    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        enable_default_shortcuts: bool = True
    ):
        """Initialize window.

        Args:
            parent: Parent widget (None = frameless top-level)
            enable_default_shortcuts: If True, registers VS Code-compatible
                                     keyboard shortcuts (Ctrl+B, Ctrl+0, etc.)
        """
```

### Activity Bar API

```python
def add_activity_item(
    self,
    item_id: str,
    icon: QIcon,
    tooltip: str = ""
) -> QAction:
    """Add an activity bar item (vertical icon button).

    Args:
        item_id: Unique identifier for this item
        icon: Icon to display
        tooltip: Tooltip text

    Returns:
        QAction that developer can connect to triggered signal

    Example:
        action = window.add_activity_item(
            "explorer",
            QIcon("icons/files.svg"),
            "Explorer"
        )
        action.triggered.connect(lambda: window.show_sidebar_panel("explorer"))
    """

def remove_activity_item(self, item_id: str) -> None:
    """Remove an activity bar item."""

def set_active_activity_item(self, item_id: str) -> None:
    """Set the active (highlighted) activity item."""

def get_active_activity_item(self) -> Optional[str]:
    """Get the currently active activity item ID."""

def set_activity_item_icon(self, item_id: str, icon: QIcon) -> None:
    """Update activity item icon.

    Args:
        item_id: Activity item identifier
        icon: New icon to display

    Example:
        window.set_activity_item_icon("git", QIcon("icons/git-modified.svg"))
    """

def set_activity_item_enabled(self, item_id: str, enabled: bool) -> None:
    """Enable or disable an activity item.

    Args:
        item_id: Activity item identifier
        enabled: True to enable, False to disable (grayed out)
    """

def is_activity_item_enabled(self, item_id: str) -> bool:
    """Check if activity item is enabled.

    Returns:
        True if enabled, False if disabled or doesn't exist
    """

def get_activity_items(self) -> List[str]:
    """Get all activity item IDs.

    Returns:
        List of activity item IDs in display order

    Example:
        items = window.get_activity_items()  # ["files", "search", "git"]
    """
```

### Sidebar API (Stackable Panels)

```python
def add_sidebar_panel(
    self,
    panel_id: str,
    widget: QWidget,
    title: str = ""
) -> None:
    """Add a sidebar panel (stackable).

    Only one panel visible at a time, like VS Code.

    Args:
        panel_id: Unique identifier for this panel
        widget: Widget to display in panel
        title: Panel title (shown in header)

    Example:
        explorer_widget = QTreeView()
        window.add_sidebar_panel("explorer", explorer_widget, "EXPLORER")
    """

def remove_sidebar_panel(self, panel_id: str) -> None:
    """Remove a sidebar panel.

    If removing the currently active panel:
    - Shows first remaining panel
    - Hides sidebar if no panels remain
    """

def show_sidebar_panel(self, panel_id: str) -> None:
    """Switch to specified panel and show sidebar."""

def get_sidebar_panel(self, panel_id: str) -> Optional[QWidget]:
    """Get the widget for a specific panel.

    Returns:
        The widget passed to add_sidebar_panel(), not a container
    """

def get_current_sidebar_panel(self) -> Optional[str]:
    """Get the currently visible panel ID."""

def toggle_sidebar(self) -> None:
    """Toggle sidebar visibility."""

def set_sidebar_visible(self, visible: bool) -> None:
    """Show/hide sidebar."""

def is_sidebar_visible(self) -> bool:
    """Check if sidebar is visible."""

def set_sidebar_width(self, width: int) -> None:
    """Set sidebar width in pixels."""

def get_sidebar_width(self) -> int:
    """Get current sidebar width."""

def set_sidebar_panel_widget(self, panel_id: str, widget: QWidget) -> None:
    """Replace panel content widget.

    Args:
        panel_id: Panel identifier
        widget: New widget to display in panel

    Example:
        # Replace placeholder with real widget
        window.set_sidebar_panel_widget("explorer", real_explorer_widget)
    """

def set_sidebar_panel_title(self, panel_id: str, title: str) -> None:
    """Update panel title.

    Args:
        panel_id: Panel identifier
        title: New title text

    Example:
        window.set_sidebar_panel_title("explorer", "EXPLORER (3 files)")
    """

def get_sidebar_panels(self) -> List[str]:
    """Get all sidebar panel IDs.

    Returns:
        List of panel IDs in display order
    """

def set_sidebar_width_constraints(self, min_width: int, max_width: int) -> None:
    """Set min/max width constraints for sidebar.

    Args:
        min_width: Minimum width in pixels (default: 150)
        max_width: Maximum width in pixels (default: 500)

    Example:
        window.set_sidebar_width_constraints(200, 600)
    """
```

### Main Pane API

```python
def set_main_content(self, widget: QWidget) -> None:
    """Set the main pane content.

    Developer can use:
    - ChromeTabbedWindow (embedded mode) for tabs
    - MultisplitWidget for split panes
    - QTextEdit for simple editor
    - Custom widget for their app

    Args:
        widget: Widget to display in main pane

    Example 1 - Simple text editor:
        editor = QTextEdit()
        window.set_main_content(editor)

    Example 2 - Chrome tabs:
        tabs = ChromeTabbedWindow(parent=window)
        tabs.addTab(QTextEdit(), "File 1")
        window.set_main_content(tabs)

    Example 3 - Multisplit:
        splits = MultisplitWidget(provider=MyProvider())
        window.set_main_content(splits)
    """

def get_main_content(self) -> Optional[QWidget]:
    """Get the current main pane widget."""
```

### Auxiliary Bar API (Right Sidebar)

```python
def set_auxiliary_content(self, widget: QWidget) -> None:
    """Set the auxiliary bar content (right sidebar).

    Args:
        widget: Widget to display in auxiliary bar

    Example:
        outline_view = QTreeView()
        window.set_auxiliary_content(outline_view)
    """

def get_auxiliary_content(self) -> Optional[QWidget]:
    """Get the current auxiliary bar widget."""

def toggle_auxiliary_bar(self) -> None:
    """Toggle auxiliary bar visibility."""

def set_auxiliary_bar_visible(self, visible: bool) -> None:
    """Show/hide auxiliary bar."""

def is_auxiliary_bar_visible(self) -> bool:
    """Check if auxiliary bar is visible."""

def set_auxiliary_bar_width(self, width: int) -> None:
    """Set auxiliary bar width in pixels."""

def get_auxiliary_bar_width(self) -> int:
    """Get current auxiliary bar width."""

def set_auxiliary_bar_width_constraints(self, min_width: int, max_width: int) -> None:
    """Set min/max width constraints for auxiliary bar.

    Args:
        min_width: Minimum width in pixels (default: 150)
        max_width: Maximum width in pixels (default: 500)
    """
```

### Menu Bar API

```python
def set_menu_bar(self, menubar: QMenuBar) -> None:
    """Set the menu bar (appears in top bar).

    In frameless mode, menu bar appears in the custom title bar.
    In embedded mode, menu bar appears at top of widget.

    Args:
        menubar: QMenuBar instance

    Example:
        menubar = QMenuBar()
        file_menu = menubar.addMenu("File")
        file_menu.addAction("Open")
        window.set_menu_bar(menubar)
    """

def get_menu_bar(self) -> Optional[QMenuBar]:
    """Get the menu bar widget."""
```

### Status Bar API

```python
def get_status_bar(self) -> QStatusBar:
    """Get the status bar widget for customization.

    Returns standard QStatusBar that developer can customize.

    Returns:
        QStatusBar instance

    Example:
        status = window.get_status_bar()
        status.addWidget(QLabel("Ready"))
        status.addPermanentWidget(QLabel("UTF-8"))
    """

def set_status_bar_visible(self, visible: bool) -> None:
    """Show/hide status bar."""

def is_status_bar_visible(self) -> bool:
    """Check if status bar is visible."""

def set_status_message(self, message: str, timeout: int = 0) -> None:
    """Convenience method to show status message.

    Args:
        message: Message text to display
        timeout: Timeout in milliseconds (0 = permanent)

    Example:
        window.set_status_message("Ready")
        window.set_status_message("Saved file", timeout=3000)
    """
```

### Keyboard Shortcuts API

```python
def register_shortcut(
    self,
    key_sequence: str,
    callback: Callable,
    description: str = ""
) -> QShortcut:
    """Register a keyboard shortcut.

    Args:
        key_sequence: Qt key sequence (e.g., "Ctrl+B", "Ctrl+Shift+E")
        callback: Function to call when shortcut activated
        description: Human-readable description

    Returns:
        QShortcut object

    Example:
        window.register_shortcut("Ctrl+H", lambda: print("Hello"))
        window.register_shortcut("F5", self.refresh, "Refresh content")
    """

def unregister_shortcut(self, key_sequence: str) -> None:
    """Unregister a keyboard shortcut.

    Args:
        key_sequence: Qt key sequence to remove
    """

def get_shortcuts(self) -> Dict[str, QShortcut]:
    """Get all registered shortcuts.

    Returns:
        Dict mapping key sequences to QShortcut objects
    """

def get_default_shortcuts(self) -> Dict[str, str]:
    """Get default keyboard shortcuts.

    Returns:
        Dict mapping action names to key sequences

    Example:
        {
            "toggle_sidebar": "Ctrl+B",
            "toggle_auxiliary_bar": "Ctrl+Alt+B",
            "focus_main_pane": "Ctrl+1",
            "focus_sidebar": "Ctrl+0",
            "show_activity_1": "Ctrl+Shift+E",
            "show_activity_2": "Ctrl+Shift+F",
            ...
        }
    """

def set_shortcut(self, action: str, key_sequence: str) -> None:
    """Override a default shortcut.

    Args:
        action: Action name (e.g., "toggle_sidebar")
        key_sequence: New key sequence (e.g., "Ctrl+Shift+B")

    Example:
        window.set_shortcut("toggle_sidebar", "Ctrl+Shift+B")
    """
```

### Batch Operations API

```python
@contextmanager
def batch_updates(self):
    """Context manager to defer layout updates.

    Useful when adding many items at once to avoid
    multiple layout recalculations.

    Example:
        with window.batch_updates():
            for item in items:
                window.add_activity_item(item.id, item.icon)
                window.add_sidebar_panel(item.id, item.widget)
        # Layout updates once at end
    """
```

### Declarative Configuration API

```python
def configure(self, config: dict) -> None:
    """Configure window from dictionary (declarative setup).

    Config format:
    {
        "activity_items": [
            {
                "id": "files",
                "icon": QIcon(...),
                "tooltip": "Explorer",
            },
        ],
        "sidebar_panels": [
            {
                "id": "files",
                "widget": QWidget(),
                "title": "EXPLORER",
            },
        ],
        "auto_connect": True,  # Auto-connect matching IDs
        "sidebar_width": 300,
        "auxiliary_bar_visible": False,
    }

    Args:
        config: Configuration dictionary

    Example:
        window.configure({
            "activity_items": [
                {"id": "files", "icon": file_icon, "tooltip": "Files"},
                {"id": "search", "icon": search_icon, "tooltip": "Search"},
            ],
            "sidebar_panels": [
                {"id": "files", "widget": file_tree, "title": "EXPLORER"},
                {"id": "search", "widget": search_widget, "title": "SEARCH"},
            ],
            "auto_connect": True,  # Automatically connects activity→panels
        })
    """
```

### Signals

```python
# Activity Bar
activity_item_clicked = Signal(str)  # item_id

# Sidebar
sidebar_panel_changed = Signal(str)  # panel_id
sidebar_visibility_changed = Signal(bool)  # is_visible

# Auxiliary Bar
auxiliary_bar_visibility_changed = Signal(bool)  # is_visible
```

## 8) Default Keyboard Shortcuts

ViloCodeWindow provides VS Code-compatible keyboard shortcuts by default (can be disabled via `enable_default_shortcuts=False`).

### Default Shortcut Mapping

```python
DEFAULT_SHORTCUTS = {
    # Core Layout (VS Code compatible)
    "toggle_sidebar": "Ctrl+B",                    # Toggle left sidebar
    "toggle_auxiliary_bar": "Ctrl+Alt+B",          # Toggle right sidebar
    "focus_sidebar": "Ctrl+0",                     # Focus sidebar panel
    "focus_main_pane": "Ctrl+1",                   # Focus main content

    # Activity Items (VS Code compatible)
    # Dynamically bound to first 5 activity items added
    "show_activity_1": "Ctrl+Shift+E",             # Show 1st activity (usually Explorer)
    "show_activity_2": "Ctrl+Shift+F",             # Show 2nd activity (usually Search)
    "show_activity_3": "Ctrl+Shift+G",             # Show 3rd activity (usually Git)
    "show_activity_4": "Ctrl+Shift+D",             # Show 4th activity (usually Debug)
    "show_activity_5": "Ctrl+Shift+X",             # Show 5th activity (usually Extensions)

    # Window
    "toggle_fullscreen": "F11",                    # Toggle fullscreen
}
```

### Shortcut Behavior

**Activity Item Shortcuts (Ctrl+Shift+E/F/G/D/X)**:
- Automatically bound to first 5 activity items in order added
- Triggers `show_sidebar_panel()` for corresponding panel (if IDs match)
- Can be manually connected by developer if different behavior needed

**Focus Management**:
- `Ctrl+0`: Sets focus to current sidebar panel widget
- `Ctrl+1`: Sets focus to main pane content widget

**Customization**:
```python
# Disable defaults and use custom shortcuts
window = ViloCodeWindow(enable_default_shortcuts=False)
window.register_shortcut("F1", my_custom_action)

# Or override specific defaults
window = ViloCodeWindow()  # Defaults enabled
window.set_shortcut("toggle_sidebar", "Ctrl+Shift+B")
```

### Integration with KeybindingManager (Optional)

For advanced keyboard shortcut management with conflict detection and settings UI:

```python
from vfwidgets_keybinding import KeybindingManager

# Application-wide keyboard shortcut manager
manager = KeybindingManager()

# Integrate window shortcuts
window.integrate_keybinding_manager(manager, context="vilocode_window")

# Manager now knows about window shortcuts
# Can detect conflicts, show in settings UI, etc.
```

## 9) Theme Integration

ViloCodeWindow integrates with vfwidgets-theme system using VS Code color tokens:

```python
try:
    from vfwidgets_theme import ThemedWidget
    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False
    ThemedWidget = object

if THEME_AVAILABLE:
    _BaseClass = type("_BaseClass", (ThemedWidget, QWidget), {})
else:
    _BaseClass = QWidget

class ViloCodeWindow(_BaseClass):
    theme_config = {
        # Activity Bar
        "activity_bar_background": "activityBar.background",
        "activity_bar_foreground": "activityBar.foreground",
        "activity_bar_border": "activityBar.border",
        "activity_bar_active_border": "activityBar.activeBorder",
        "activity_bar_inactive_foreground": "activityBar.inactiveForeground",

        # Sidebar
        "sidebar_background": "sideBar.background",
        "sidebar_foreground": "sideBar.foreground",
        "sidebar_border": "sideBar.border",
        "sidebar_title_foreground": "sideBarTitle.foreground",

        # Editor/Main Pane
        "editor_background": "editor.background",
        "editor_foreground": "editor.foreground",

        # Status Bar
        "statusbar_background": "statusBar.background",
        "statusbar_foreground": "statusBar.foreground",
        "statusbar_border": "statusBar.border",

        # Menu
        "menu_background": "menu.background",
        "menu_foreground": "menu.foreground",

        # Title Bar (frameless mode)
        "titlebar_background": "titleBar.activeBackground",
        "titlebar_foreground": "titleBar.activeForeground",
        "titlebar_border": "titleBar.border",
    }
```

**Fallback Behavior:**
- When vfwidgets-theme not available, uses sensible dark theme defaults
- All colors configurable via Qt stylesheets

## 10) Behavioral Requirements

### Widget Ownership & Lifecycle
* Widgets added to panels/main pane are reparented to the window
* Removing panels clears parent but doesn't delete widget (developer's responsibility)
* Window destruction cleans up all child widgets automatically (Qt parent-child)

### Panel Removal Behavior
When removing a sidebar panel:
* **If removing active panel**: Shows first remaining panel
* **If no panels remain**: Hides sidebar
* **Signal emitted**: `sidebar_panel_changed` with new panel ID (or empty string if hidden)

### Activity Item to Panel Connection
* **Manual connection** (default): Developer connects QAction.triggered to show_sidebar_panel()
* **Auto-connect** (via configure()): When `auto_connect: True`, automatically connects activity items to panels with matching IDs
* **Dynamic binding**: Activity shortcuts (Ctrl+Shift+E/F/G/D/X) bound to first 5 activity items in order added

### Focus Management
* `focus_sidebar`: Sets focus to current sidebar panel widget (if visible)
* `focus_main_pane`: Sets focus to main pane content widget (if set)
* Keyboard navigation: Tab cycles through focusable widgets in normal Qt order

### Layout Behavior
* **Activity bar**: Fixed width (~48px), always visible
* **Sidebar**: Resizable width (150-500px default), collapsible, remembers last width
* **Main pane**: Takes all remaining horizontal space (stretch factor = 1)
* **Auxiliary bar**: Resizable width (150-500px default), hidden by default, remembers last width
* **Status bar**: Fixed height (~22px), optional

### Batch Updates
* Layout recalculation deferred when inside `batch_updates()` context
* All updates applied once at context exit
* Improves performance when adding many items

## 11) Developer Experience

### Tier 1: Zero Config (Just Works)
```python
# Absolute minimum
window = ViloCodeWindow()
window.set_main_content(QTextEdit())
window.show()
```

### Tier 2: Helper Functions (Common Patterns)
```python
from vfwidgets_vilocode_window.helpers import create_basic_ide_window

# Pre-configured IDE with placeholders
window = create_basic_ide_window()
window.set_sidebar_panel_widget("explorer", my_tree)
window.set_main_content(my_editor)
window.show()
```

### Tier 3: Template Subclasses (Override Methods)
```python
from vfwidgets_vilocode_window.templates import BasicIDEWindow

# Subclass template
class MyIDE(BasicIDEWindow):
    def create_main_widget(self):
        return ChromeTabbedWindow()

app = MyIDE()
app.show()
```

### Tier 4: Full Manual Control (Power Users)
```python
# Complete customization
window = ViloCodeWindow()

# Add activity items
files = window.add_activity_item("files", QIcon("icons/folder.svg"), "Explorer")
search = window.add_activity_item("search", QIcon("icons/search.svg"), "Search")

# Add sidebar panels
window.add_sidebar_panel("explorer", file_tree, "EXPLORER")
window.add_sidebar_panel("search", search_widget, "SEARCH")

# Connect signals
files.triggered.connect(lambda: window.show_sidebar_panel("explorer"))
search.triggered.connect(lambda: window.show_sidebar_panel("search"))

# Main content
window.set_main_content(editor)

# Status bar
status = window.get_status_bar()
status.showMessage("Ready")

window.show()
```

## 10) Behavioral Requirements

### Mode Detection
* Mode determined by parent widget at initialization
* No parent (`parent=None`) → Top-level frameless mode
* Has parent → Embedded mode
* Mode cannot be changed after initialization

### Window Management (Frameless Mode)
* Custom title bar with menu bar + window controls
* Native window move via Qt's `startSystemMove()` (Qt 6.5+)
* Native window resize via Qt's `startSystemResize()` (Qt 6.5+)
* Fallback to manual drag/resize on older Qt or unsupported platforms
* Double-click title bar to maximize/restore
* Right-click title bar for system menu (platform-dependent)

### Layout Behavior
* Activity bar: Fixed width (~48px), always visible
* Sidebar: Resizable width, collapsible, remembers last width
* Main pane: Takes all remaining space
* Auxiliary bar: Resizable width, hidden by default, remembers last width
* Status bar: Fixed height (~22px), optional

### Panel Switching
* Only one sidebar panel visible at a time
* Switching panels preserves sidebar visibility state
* If sidebar hidden, showing a panel makes sidebar visible
* Activity item highlights match active sidebar panel

### Widget Ownership
* Widgets added to panels/main pane are reparented to the window
* Removing panels clears parent but doesn't delete widget
* Window destruction cleans up all child widgets

## 11) Platform-Specific Behavior

### Detection & Adaptation
Reuses ChromeTabbedWindow's platform detection:
```python
@dataclass
class PlatformCapabilities:
    supports_frameless: bool = False
    supports_system_move: bool = False
    supports_system_resize: bool = False
    supports_client_side_decorations: bool = False
    has_native_shadows: bool = False
    requires_composition: bool = False
    xdg_portals_available: bool = False
    running_under_wsl: bool = False
```

### Fallback Policy
* If frameless unsupported → use native decorations, place menu bar below title bar
* If system move/resize unsupported → manual dragging (fallback implementation)
* If client-side decorations unsupported → keep native title bar
* Always degrade gracefully — widget must always display

### Platform Notes
* **Windows**: Full frameless support, Aero snap
* **macOS**: Full frameless support, native fullscreen
* **Linux X11**: Full frameless support
* **Linux Wayland**: Compositor-dependent, Qt 6.5+ required
* **WSL/WSLg**: Prefer native decorations if frameless unreliable

## 12) Configuration & Styling

### Default Dimensions
* Activity bar width: 48px
* Sidebar width: 250px (default), 150-500px (range)
* Auxiliary bar width: 300px (default), 150-500px (range)
* Status bar height: 22px
* Title bar height: 32px (frameless mode)

### Styling Approach
* No hardcoded colors — use theme system or Qt palette
* QSS object names for custom styling:
  - `activityBar`
  - `sideBar`
  - `mainPane`
  - `auxiliaryBar`
  - `statusBar`
  - `titleBar`

### Properties (Qt Properties)
```python
# Visibility
sidebar_visible: bool
auxiliary_bar_visible: bool
status_bar_visible: bool

# Dimensions
sidebar_width: int
auxiliary_bar_width: int

# State
active_activity_item: str
current_sidebar_panel: str
```

## 13) Future Enhancements (v2.0+)

**Not included in v1.0, documented for future reference:**

### Persistence
* Save/restore layout state (sidebar width, auxiliary bar visibility, active panel)
* Per-application settings storage
* JSON-based configuration

### Advanced Layouts
* Dockable panels (drag panels to different areas)
* Floating panels (detach panels to separate windows)
* Multiple sidebar panels visible simultaneously (split sidebar)

### Plugin System
* Extension points for third-party panels
* Plugin manager for activity items
* Lifecycle hooks for plugins

### Tab Groups in Sidebar
* Multiple tab groups in sidebar (like VS Code's outline + timeline)
* Horizontal tabs within sidebar panels

## 14) Testing Strategy

### Unit Tests
* Layout calculations
* Mode detection
* Panel management (add/remove/switch)
* Activity item management
* Signal emission

### Integration Tests
* Theme system integration
* Widget reparenting
* Platform detection
* Frameless window behavior

### Visual Tests
* Layout rendering across platforms
* Theme color application
* Resize behavior
* Panel transitions

## 15) Documentation Requirements

### User Documentation
* README.md - Quick start, features, installation
* docs/api.md - Complete API reference
* docs/usage.md - Usage patterns, best practices
* docs/examples.md - Example descriptions

### Developer Documentation
* docs/architecture.md - Internal architecture, MVC design
* docs/theming.md - Theme integration details
* docs/platform-notes.md - Platform-specific behavior
* CONTRIBUTING.md - Contribution guidelines

### Examples
* 01_minimal_window.py - Simplest possible usage
* 02_activity_sidebar.py - Activity bar + sidebar
* 03_full_layout.py - All components
* 04_terminal_ide.py - With MultisplitWidget
* 05_tabbed_editor.py - With ChromeTabbedWindow
* 06_themed_ide.py - Theme system integration
* run_examples.py - Interactive example launcher

## 16) Success Criteria

**v1.0 is complete when:**
1. ✅ Dual-mode operation (frameless/embedded) works on all platforms
2. ✅ All public APIs documented and tested
3. ✅ Theme system integration functional
4. ✅ 6+ working examples covering all use cases
5. ✅ README with quick start guide
6. ✅ Architecture documentation complete
7. ✅ Can be used to build a simple IDE in < 100 lines of code
8. ✅ Zero errors on basic usage (Tier 1 API)

## 17) Non-Functional Requirements

### Performance
* Layout updates < 16ms (60 FPS)
* Panel switching < 50ms
* Memory footprint < 5MB (empty window)
* No memory leaks on panel add/remove

### Accessibility
* Keyboard navigation for all components
* Screen reader support via Qt accessibility
* High contrast theme support
* Keyboard shortcuts for toggle sidebar/auxiliary bar

### Code Quality
* 100% type hints (mypy strict)
* Black formatting (100 char line length)
* Ruff linting with no errors
* Test coverage > 80%

## See Also

* [ChromeTabbedWindow Specification](../../chrome-tabbed-window/docs/chrome-tabbed-window-SPECIFICATION.md) - Similar widget for reference
* [VFWidgets Architecture Guide](../../../docs/CleanArchitectureAsTheWay.md) - Clean architecture principles
* [Theme System Documentation](../../theme_system/README.md) - Theme integration details
