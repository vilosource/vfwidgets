# ViloCodeWindow API Reference

Complete API documentation for ViloCodeWindow v1.0 - the VS Code-style application window widget.

---

## Table of Contents

- [Class Overview](#class-overview)
- [Constructor](#constructor)
- [Signals](#signals)
- [Activity Bar API](#activity-bar-api)
- [Sidebar API](#sidebar-api)
- [Main Pane API](#main-pane-api)
- [Auxiliary Bar API](#auxiliary-bar-api)
- [Menu Bar API](#menu-bar-api)
- [Status Bar API](#status-bar-api)
- [Keyboard Shortcuts API](#keyboard-shortcuts-api)
- [Batch Operations API](#batch-operations-api)
- [Declarative Configuration API](#declarative-configuration-api)

---

## Class Overview

```python
from vfwidgets_vilocode_window import ViloCodeWindow

class ViloCodeWindow(QWidget):
    """VS Code-style application window with adaptive behavior.

    Automatically operates in one of two modes:
    - Frameless Mode: Top-level window with custom title bar (no parent)
    - Embedded Mode: Regular widget without window decorations (has parent)

    Optionally integrates with vfwidgets-theme for automatic theming.
    """
```

---

## Constructor

### `ViloCodeWindow(parent=None, enable_default_shortcuts=True)`

Creates a new ViloCodeWindow instance.

**Parameters**:
- `parent` (`Optional[QWidget]`): Parent widget. If `None`, creates a frameless top-level window. If provided, creates an embedded widget.
- `enable_default_shortcuts` (`bool`): Whether to register VS Code-compatible keyboard shortcuts. Default: `True`

**Returns**: `ViloCodeWindow` instance

**Mode Detection**:
- `parent=None` → **Frameless mode** (top-level window with custom title bar)
- `parent=widget` → **Embedded mode** (regular widget, no window decorations)

**Examples**:

```python
# Frameless mode - standalone application window
app = QApplication([])
window = ViloCodeWindow()
window.setWindowTitle("My IDE")
window.show()

# Embedded mode - widget inside another window
main_window = QMainWindow()
vilocode_widget = ViloCodeWindow(parent=main_window)
main_window.setCentralWidget(vilocode_widget)

# Disable default shortcuts (register custom ones later)
window = ViloCodeWindow(enable_default_shortcuts=False)
```

---

## Signals

### `activity_item_clicked = Signal(str)`

Emitted when an activity bar item is clicked.

**Parameters**:
- `item_id` (`str`): Unique identifier of the clicked activity item

**Example**:
```python
def on_activity_clicked(item_id: str):
    print(f"Activity item clicked: {item_id}")
    window.show_sidebar_panel(item_id)

window.activity_item_clicked.connect(on_activity_clicked)
```

---

### `sidebar_panel_changed = Signal(str)`

Emitted when the sidebar switches to a different panel.

**Parameters**:
- `panel_id` (`str`): Identifier of the newly active panel

**Example**:
```python
def on_panel_changed(panel_id: str):
    print(f"Now showing panel: {panel_id}")
    window.set_active_activity_item(panel_id)

window.sidebar_panel_changed.connect(on_panel_changed)
```

---

### `sidebar_visibility_changed = Signal(bool)`

Emitted when sidebar visibility changes (shown or hidden).

**Parameters**:
- `is_visible` (`bool`): `True` if sidebar is now visible, `False` if hidden

**Example**:
```python
def on_sidebar_toggled(visible: bool):
    print(f"Sidebar is now {'visible' if visible else 'hidden'}")

window.sidebar_visibility_changed.connect(on_sidebar_toggled)
```

---

### `auxiliary_bar_visibility_changed = Signal(bool)`

Emitted when auxiliary bar visibility changes (shown or hidden).

**Parameters**:
- `is_visible` (`bool`): `True` if auxiliary bar is now visible, `False` if hidden

**Example**:
```python
def on_aux_bar_toggled(visible: bool):
    print(f"Auxiliary bar is now {'visible' if visible else 'hidden'}")

window.auxiliary_bar_visibility_changed.connect(on_aux_bar_toggled)
```

---

## Activity Bar API

The activity bar is the vertical icon strip on the left edge of the window (like VS Code's activity bar).

### `add_activity_item(item_id, icon, tooltip="") -> QAction`

Add an icon button to the activity bar.

**Parameters**:
- `item_id` (`str`): Unique identifier for this item
- `icon` (`QIcon`): Icon to display
- `tooltip` (`str`): Tooltip text shown on hover. Default: `""`

**Returns**: `QAction` - The action object (connect to `.triggered` signal for click handling)

**Example**:
```python
from PySide6.QtGui import QIcon

# Add "Files" activity item
files_icon = QIcon("icons/files.svg")
files_action = window.add_activity_item("files", files_icon, "Explorer")

# Connect to show corresponding sidebar panel
files_action.triggered.connect(lambda: window.show_sidebar_panel("explorer"))
```

---

### `remove_activity_item(item_id)`

Remove an activity bar item.

**Parameters**:
- `item_id` (`str`): Identifier of the item to remove

**Example**:
```python
window.remove_activity_item("files")
```

---

### `set_active_activity_item(item_id)`

Set which activity item is highlighted as active.

**Parameters**:
- `item_id` (`str`): Identifier of the item to activate

**Note**: Only one activity item can be active at a time.

**Example**:
```python
window.set_active_activity_item("search")
```

---

### `get_active_activity_item() -> Optional[str]`

Get the currently active activity item.

**Returns**: `str` - Active item ID, or `None` if no item is active

**Example**:
```python
active = window.get_active_activity_item()
print(f"Active: {active}")  # "search"
```

---

### `set_activity_item_icon(item_id, icon)`

Update the icon for an activity item.

**Parameters**:
- `item_id` (`str`): Activity item identifier
- `icon` (`QIcon`): New icon to display

**Use Case**: Show different icons based on state (e.g., git modified icon)

**Example**:
```python
# Show "git modified" icon when changes detected
modified_icon = QIcon("icons/git-modified.svg")
window.set_activity_item_icon("git", modified_icon)
```

---

### `set_activity_item_enabled(item_id, enabled)`

Enable or disable an activity item.

**Parameters**:
- `item_id` (`str`): Activity item identifier
- `enabled` (`bool`): `True` to enable, `False` to disable (grayed out)

**Example**:
```python
# Disable git item when no repository
window.set_activity_item_enabled("git", False)
```

---

### `is_activity_item_enabled(item_id) -> bool`

Check if an activity item is enabled.

**Parameters**:
- `item_id` (`str`): Activity item identifier

**Returns**: `bool` - `True` if enabled, `False` if disabled or doesn't exist

**Example**:
```python
if window.is_activity_item_enabled("git"):
    print("Git is available")
```

---

### `get_activity_items() -> List[str]`

Get all activity item IDs in display order.

**Returns**: `List[str]` - List of activity item IDs

**Example**:
```python
items = window.get_activity_items()
print(items)  # ["files", "search", "git", "debug"]
```

---

## Sidebar API

The sidebar is the collapsible left panel containing stackable panels (only one visible at a time).

### `add_sidebar_panel(panel_id, widget, title="")`

Add a panel to the sidebar.

**Parameters**:
- `panel_id` (`str`): Unique identifier for this panel
- `widget` (`QWidget`): Widget to display in the panel
- `title` (`str`): Panel title shown in header (e.g., "EXPLORER"). Default: `""`

**Note**: Widget is reparented to the sidebar.

**Example**:
```python
from PySide6.QtWidgets import QTreeView

file_tree = QTreeView()
window.add_sidebar_panel("explorer", file_tree, "EXPLORER")
```

---

### `remove_sidebar_panel(panel_id)`

Remove a panel from the sidebar.

**Parameters**:
- `panel_id` (`str`): Identifier of the panel to remove

**Behavior**:
- If removing the currently active panel: Shows first remaining panel
- If no panels remain: Hides the sidebar
- Emits `sidebar_panel_changed` signal with new panel ID (or empty if hidden)

**Example**:
```python
window.remove_sidebar_panel("explorer")
```

---

### `show_sidebar_panel(panel_id)`

Switch to a specific panel and show the sidebar.

**Parameters**:
- `panel_id` (`str`): Identifier of the panel to show

**Behavior**:
- Makes sidebar visible if hidden
- Switches to the specified panel
- Emits `sidebar_panel_changed` signal

**Example**:
```python
window.show_sidebar_panel("search")
```

---

### `get_sidebar_panel(panel_id) -> Optional[QWidget]`

Get the widget for a specific panel.

**Parameters**:
- `panel_id` (`str`): Panel identifier

**Returns**: `QWidget` - The widget passed to `add_sidebar_panel()`, or `None` if not found

**Example**:
```python
tree = window.get_sidebar_panel("explorer")
if tree:
    tree.expandAll()
```

---

### `get_current_sidebar_panel() -> Optional[str]`

Get the currently visible panel ID.

**Returns**: `str` - Active panel ID, or `None` if sidebar is hidden or no panels

**Example**:
```python
current = window.get_current_sidebar_panel()
print(f"Current panel: {current}")  # "explorer"
```

---

### `toggle_sidebar()`

Toggle sidebar visibility (show if hidden, hide if shown).

**Animation**: Uses smooth 200ms collapse/expand animation by default.

**Example**:
```python
window.toggle_sidebar()
```

---

### `set_sidebar_visible(visible, animated=True)`

Show or hide the sidebar.

**Parameters**:
- `visible` (`bool`): `True` to show, `False` to hide
- `animated` (`bool`): Whether to use smooth animation. Default: `True`

**Animation**: 200ms collapse/expand with OutCubic easing when `animated=True`.

**Example**:
```python
# Show with animation
window.set_sidebar_visible(True)

# Hide without animation (instant)
window.set_sidebar_visible(False, animated=False)
```

---

### `is_sidebar_visible() -> bool`

Check if sidebar is visible.

**Returns**: `bool` - `True` if visible, `False` if hidden

**Example**:
```python
if not window.is_sidebar_visible():
    window.show_sidebar_panel("explorer")
```

---

### `set_sidebar_width(width)`

Set sidebar width in pixels.

**Parameters**:
- `width` (`int`): Width in pixels (subject to min/max constraints)

**Example**:
```python
window.set_sidebar_width(350)
```

---

### `get_sidebar_width() -> int`

Get current sidebar width in pixels.

**Returns**: `int` - Current width

**Example**:
```python
width = window.get_sidebar_width()
print(f"Sidebar width: {width}px")
```

---

### `set_sidebar_panel_widget(panel_id, widget)`

Replace the content widget of an existing panel.

**Parameters**:
- `panel_id` (`str`): Panel identifier
- `widget` (`QWidget`): New widget to display

**Use Case**: Replace placeholder with real widget after initialization.

**Example**:
```python
# Replace placeholder with loaded file tree
real_tree = load_file_tree()
window.set_sidebar_panel_widget("explorer", real_tree)
```

---

### `set_sidebar_panel_title(panel_id, title)`

Update a panel's title.

**Parameters**:
- `panel_id` (`str`): Panel identifier
- `title` (`str`): New title text

**Use Case**: Show dynamic information in title (e.g., file count).

**Example**:
```python
file_count = get_file_count()
window.set_sidebar_panel_title("explorer", f"EXPLORER ({file_count} files)")
```

---

### `get_sidebar_panels() -> List[str]`

Get all sidebar panel IDs.

**Returns**: `List[str]` - List of panel IDs in display order

**Example**:
```python
panels = window.get_sidebar_panels()
print(panels)  # ["explorer", "search", "git"]
```

---

### `set_sidebar_width_constraints(min_width, max_width)`

Set minimum and maximum width constraints for the sidebar.

**Parameters**:
- `min_width` (`int`): Minimum width in pixels. Default: 150
- `max_width` (`int`): Maximum width in pixels. Default: 500

**Example**:
```python
window.set_sidebar_width_constraints(200, 600)
```

---

## Main Pane API

The main pane is the central content area where you place your primary widget (editor, tabs, etc.).

### `set_main_content(widget)`

Set the widget to display in the main pane.

**Parameters**:
- `widget` (`QWidget`): Widget to display (any Qt widget)

**Common Use Cases**:
- `QTextEdit` - Simple text editor
- `ChromeTabbedWindow` - Tabbed document interface
- `MultisplitWidget` - Split pane layout
- Custom widget - Your application UI

**Example**:
```python
from PySide6.QtWidgets import QTextEdit

# Simple text editor
editor = QTextEdit()
window.set_main_content(editor)

# Or tabbed interface (if ChromeTabbedWindow available)
from chrome_tabbed_window import ChromeTabbedWindow
tabs = ChromeTabbedWindow(parent=window)
tabs.addTab(QTextEdit(), "Untitled-1")
window.set_main_content(tabs)
```

---

### `get_main_content() -> Optional[QWidget]`

Get the current main pane widget.

**Returns**: `QWidget` - The widget set via `set_main_content()`, or `None` if not set

**Example**:
```python
editor = window.get_main_content()
if editor:
    editor.setPlainText("Hello World")
```

---

## Auxiliary Bar API

The auxiliary bar is an optional right-side panel (like VS Code's outline panel).

### `set_auxiliary_content(widget)`

Set the widget to display in the auxiliary bar.

**Parameters**:
- `widget` (`QWidget`): Widget to display

**Common Use Cases**:
- Outline view
- Timeline
- Minimap
- Preview panel

**Example**:
```python
from PySide6.QtWidgets import QTreeWidget

outline = QTreeWidget()
outline.setHeaderLabel("OUTLINE")
window.set_auxiliary_content(outline)
```

---

### `get_auxiliary_content() -> Optional[QWidget]`

Get the current auxiliary bar widget.

**Returns**: `QWidget` - The widget set via `set_auxiliary_content()`, or `None` if not set

**Example**:
```python
outline = window.get_auxiliary_content()
if outline:
    outline.clear()
```

---

### `toggle_auxiliary_bar()`

Toggle auxiliary bar visibility (show if hidden, hide if shown).

**Animation**: Uses smooth 200ms collapse/expand animation by default.

**Example**:
```python
window.toggle_auxiliary_bar()
```

---

### `set_auxiliary_bar_visible(visible, animated=True)`

Show or hide the auxiliary bar.

**Parameters**:
- `visible` (`bool`): `True` to show, `False` to hide
- `animated` (`bool`): Whether to use smooth animation. Default: `True`

**Animation**: 200ms collapse/expand with OutCubic easing when `animated=True`.

**Example**:
```python
# Show with animation
window.set_auxiliary_bar_visible(True)

# Hide without animation (instant)
window.set_auxiliary_bar_visible(False, animated=False)
```

---

### `is_auxiliary_bar_visible() -> bool`

Check if auxiliary bar is visible.

**Returns**: `bool` - `True` if visible, `False` if hidden

**Example**:
```python
if not window.is_auxiliary_bar_visible():
    window.set_auxiliary_bar_visible(True)
```

---

### `set_auxiliary_bar_width(width)`

Set auxiliary bar width in pixels.

**Parameters**:
- `width` (`int`): Width in pixels (subject to min/max constraints)

**Example**:
```python
window.set_auxiliary_bar_width(350)
```

---

### `get_auxiliary_bar_width() -> int`

Get current auxiliary bar width in pixels.

**Returns**: `int` - Current width

**Example**:
```python
width = window.get_auxiliary_bar_width()
print(f"Auxiliary bar width: {width}px")
```

---

### `set_auxiliary_bar_width_constraints(min_width, max_width)`

Set minimum and maximum width constraints for the auxiliary bar.

**Parameters**:
- `min_width` (`int`): Minimum width in pixels. Default: 150
- `max_width` (`int`): Maximum width in pixels. Default: 500

**Example**:
```python
window.set_auxiliary_bar_width_constraints(200, 400)
```

---

## Menu Bar API

The menu bar displays in the title bar (frameless mode) or at the top (embedded mode).

### `set_menu_bar(menubar)`

Set or replace the menu bar.

**Parameters**:
- `menubar` (`QMenuBar`): Menu bar widget to use

**Behavior**:
- **Frameless mode**: Menu bar appears in custom title bar
- **Embedded mode**: Menu bar appears at top of widget

**Example**:
```python
from PySide6.QtWidgets import QMenuBar

menubar = QMenuBar()

# Add File menu
file_menu = menubar.addMenu("File")
file_menu.addAction("New")
file_menu.addAction("Open")
file_menu.addAction("Save")

# Add Edit menu
edit_menu = menubar.addMenu("Edit")
edit_menu.addAction("Undo")
edit_menu.addAction("Redo")

window.set_menu_bar(menubar)
```

---

### `get_menu_bar() -> Optional[QMenuBar]`

Get the current menu bar widget.

**Returns**: `QMenuBar` - The menu bar set via `set_menu_bar()`, or `None` if not set

**Example**:
```python
menubar = window.get_menu_bar()
if menubar:
    view_menu = menubar.addMenu("View")
    view_menu.addAction("Toggle Sidebar")
```

---

## Status Bar API

The status bar is at the bottom of the window (like VS Code's status bar).

### `get_status_bar() -> QStatusBar`

Get the status bar widget for customization.

**Returns**: `QStatusBar` - Standard Qt status bar

**Example**:
```python
from PySide6.QtWidgets import QLabel

status_bar = window.get_status_bar()

# Add left-aligned widgets
status_bar.addWidget(QLabel("Ready"))

# Add right-aligned widgets
status_bar.addPermanentWidget(QLabel("UTF-8"))
status_bar.addPermanentWidget(QLabel("Python 3.12"))
```

---

### `set_status_bar_visible(visible)`

Show or hide the status bar.

**Parameters**:
- `visible` (`bool`): `True` to show, `False` to hide

**Example**:
```python
window.set_status_bar_visible(False)  # Hide status bar
```

---

### `is_status_bar_visible() -> bool`

Check if status bar is visible.

**Returns**: `bool` - `True` if visible, `False` if hidden

**Example**:
```python
if window.is_status_bar_visible():
    print("Status bar is shown")
```

---

### `set_status_message(message, timeout=0)`

Convenience method to show a temporary status message.

**Parameters**:
- `message` (`str`): Message text to display
- `timeout` (`int`): Timeout in milliseconds. `0` = permanent. Default: `0`

**Example**:
```python
# Permanent message
window.set_status_message("Ready")

# Temporary message (3 seconds)
window.set_status_message("File saved successfully", timeout=3000)
```

---

## Keyboard Shortcuts API

Register and manage keyboard shortcuts (VS Code-compatible by default).

### Default Shortcuts

When `enable_default_shortcuts=True` (default), these shortcuts are registered:

| Shortcut | Action |
|----------|--------|
| `Ctrl+B` | Toggle sidebar |
| `Ctrl+Alt+B` | Toggle auxiliary bar |
| `Ctrl+0` | Focus sidebar |
| `Ctrl+1` | Focus main pane |
| `Ctrl+Shift+E` | Show activity item 1 |
| `Ctrl+Shift+F` | Show activity item 2 |
| `Ctrl+Shift+G` | Show activity item 3 |
| `Ctrl+Shift+D` | Show activity item 4 |
| `Ctrl+Shift+X` | Show activity item 5 |
| `F11` | Toggle fullscreen |

### `register_shortcut(key_sequence, callback, description="") -> QShortcut`

Register a custom keyboard shortcut.

**Parameters**:
- `key_sequence` (`str`): Qt key sequence (e.g., `"Ctrl+H"`, `"Ctrl+Shift+P"`)
- `callback` (`Callable`): Function to call when shortcut activated
- `description` (`str`): Human-readable description. Default: `""`

**Returns**: `QShortcut` - The shortcut object

**Example**:
```python
def show_help():
    print("Help dialog")

window.register_shortcut("F1", show_help, "Show help")
window.register_shortcut("Ctrl+P", lambda: print("Command palette"))
```

---

### `unregister_shortcut(key_sequence)`

Remove a keyboard shortcut.

**Parameters**:
- `key_sequence` (`str`): Key sequence to remove

**Example**:
```python
window.unregister_shortcut("F1")
```

---

### `get_shortcuts() -> Dict[str, QShortcut]`

Get all registered shortcuts.

**Returns**: `Dict[str, QShortcut]` - Dictionary mapping key sequences to `QShortcut` objects

**Example**:
```python
shortcuts = window.get_shortcuts()
for key, shortcut in shortcuts.items():
    print(f"{key}: {shortcut.isEnabled()}")
```

---

### `get_default_shortcuts() -> Dict[str, str]`

Get the default shortcut mappings.

**Returns**: `Dict[str, str]` - Dictionary mapping action names to key sequences

**Example**:
```python
defaults = window.get_default_shortcuts()
print(defaults)
# {
#     "TOGGLE_SIDEBAR": "Ctrl+B",
#     "TOGGLE_AUXILIARY_BAR": "Ctrl+Alt+B",
#     "FOCUS_SIDEBAR": "Ctrl+0",
#     ...
# }
```

---

### `set_shortcut(action, key_sequence)`

Override a default shortcut with a new key binding.

**Parameters**:
- `action` (`str`): Action name (e.g., `"TOGGLE_SIDEBAR"`)
- `key_sequence` (`str`): New key sequence (e.g., `"Ctrl+Shift+B"`)

**Example**:
```python
# Change sidebar toggle from Ctrl+B to Ctrl+Shift+B
window.set_shortcut("TOGGLE_SIDEBAR", "Ctrl+Shift+B")
```

---

## Batch Operations API

Batch operations allow you to defer layout updates when adding many items at once.

### `batch_updates()`

Context manager to defer layout updates until completion.

**Use Case**: Improves performance when adding many activity items and panels.

**Example**:
```python
with window.batch_updates():
    # Add 10 activity items and panels
    for i in range(10):
        icon = create_icon(i)
        widget = create_widget(i)

        window.add_activity_item(f"item{i}", icon, f"Item {i}")
        window.add_sidebar_panel(f"panel{i}", widget, f"PANEL {i}")

# Layout updates once here, not 20 times
```

---

## Declarative Configuration API

Configure the entire window from a dictionary (alternative to imperative API).

### `configure(config)`

Configure window from a dictionary.

**Parameters**:
- `config` (`dict`): Configuration dictionary

**Config Format**:
```python
{
    "activity_items": [
        {"id": "files", "icon": QIcon(...), "tooltip": "Explorer"},
        {"id": "search", "icon": QIcon(...), "tooltip": "Search"},
    ],
    "sidebar_panels": [
        {"id": "explorer", "widget": QWidget(), "title": "EXPLORER"},
        {"id": "search", "widget": QWidget(), "title": "SEARCH"},
    ],
    "main_content": QTextEdit(),
    "auxiliary_content": QWidget(),
    "auto_connect": True,  # Auto-connect activity items to panels with matching IDs
    "sidebar_width": 300,
    "sidebar_visible": True,
    "auxiliary_bar_visible": False,
}
```

**Example**:
```python
window.configure({
    "activity_items": [
        {"id": "files", "icon": files_icon, "tooltip": "Files"},
        {"id": "search", "icon": search_icon, "tooltip": "Search"},
    ],
    "sidebar_panels": [
        {"id": "files", "widget": file_tree, "title": "FILES"},
        {"id": "search", "widget": search_widget, "title": "SEARCH"},
    ],
    "main_content": ChromeTabbedWindow(),
    "auto_connect": True,  # Automatically connects activity items to panels
})
```

**auto_connect Behavior**:
- When `"auto_connect": True`, activity items are automatically connected to sidebar panels with matching IDs
- Clicking activity item `"files"` will call `show_sidebar_panel("files")`
- Saves you from manually connecting signals

---

## See Also

- [README.md](../README.md) - Quick start and feature overview
- [architecture.md](architecture.md) - Internal architecture for developers
- [theme.md](theme.md) - Theme integration guide
- [vilocode-window-SPECIFICATION.md](vilocode-window-SPECIFICATION.md) - Complete specification
