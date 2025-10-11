# Menu Bar Quick Start Guide

This guide shows you how to add menus to your ViloCodeWindow applications using the new fluent API.

## Why the Fluent API?

The fluent API makes menu creation:
- **75% less code** (17 lines vs 67 lines)
- **No initialization traps** (automatic menu bar creation)
- **Automatic theme integration** (no manual color management)
- **Clean and readable** (method chaining)

## Basic Usage

### 1. Simple Menu

```python
from vfwidgets_vilocode_window import ViloCodeWindow

class MyWindow(ViloCodeWindow):
    def __init__(self):
        super().__init__()

        # Add a File menu with actions
        self.add_menu("&File") \
            .add_action("&Open", self.on_open, "Ctrl+O") \
            .add_action("E&xit", self.close, "Ctrl+Q")

    def on_open(self):
        print("Open file")
```

That's it! No `QMenuBar()` creation, no `set_menu_bar()` call, no theme workarounds.

### 2. Menu with Separators and Tooltips

```python
self.add_menu("&File") \
    .add_action("&New", self.on_new, "Ctrl+N", tooltip="Create new file") \
    .add_action("&Open", self.on_open, "Ctrl+O", tooltip="Open file") \
    .add_separator() \
    .add_action("&Save", self.on_save, "Ctrl+S", tooltip="Save file") \
    .add_action("Save &As...", self.on_save_as, "Ctrl+Shift+S") \
    .add_separator() \
    .add_action("E&xit", self.close, "Ctrl+Q")
```

### 3. Checkable Items (Toggles)

```python
self.add_menu("&View") \
    .add_checkable("Show &Sidebar", self.on_sidebar_toggle, checked=True) \
    .add_checkable("Show &Minimap", self.on_minimap_toggle)

def on_sidebar_toggle(self, checked: bool):
    print(f"Sidebar visible: {checked}")
```

### 4. Submenus

```python
self.add_menu("&File") \
    .add_submenu("Recent Files") \
        .add_action("file1.txt", lambda: self.open_recent("file1.txt")) \
        .add_action("file2.txt", lambda: self.open_recent("file2.txt")) \
    .end_submenu() \
    .add_separator() \
    .add_action("E&xit", self.close)
```

**Important**: Always call `end_submenu()` after adding submenu items to return to the parent menu.

### 5. Action Groups (Radio Buttons)

```python
settings = self.add_menu("&Settings")

settings.add_action_group([
    ("Small Font", lambda: self.set_font("small")),
    ("Medium Font", lambda: self.set_font("medium")),
    ("Large Font", lambda: self.set_font("large")),
], default_index=1)  # Medium selected by default
```

### 6. Multiple Menus

```python
# File menu
self.add_menu("&File") \
    .add_action("&Open", self.on_open, "Ctrl+O") \
    .add_action("E&xit", self.close, "Ctrl+Q")

# Edit menu
self.add_menu("&Edit") \
    .add_action("&Undo", self.on_undo, "Ctrl+Z") \
    .add_action("&Redo", self.on_redo, "Ctrl+Y")

# View menu
self.add_menu("&View") \
    .add_checkable("Show &Sidebar", self.on_sidebar_toggle)
```

## Complete Example

Here's a complete application with File, Edit, and View menus:

```python
from vfwidgets_vilocode_window import ViloCodeWindow
from PySide6.QtWidgets import QApplication, QTextEdit
import sys

class MyIDE(ViloCodeWindow):
    def __init__(self):
        super().__init__(
            show_activity_bar=False,
            show_sidebar=False,
            show_auxiliary_bar=False,
        )

        self.setWindowTitle("My IDE")
        self.resize(800, 600)

        # Setup content
        editor = QTextEdit()
        self.set_main_content(editor)

        # Setup menus
        self._setup_menus()

    def _setup_menus(self):
        # File menu
        self.add_menu("&File") \
            .add_action("&New", self.on_new, "Ctrl+N", tooltip="New file") \
            .add_action("&Open", self.on_open, "Ctrl+O", tooltip="Open file") \
            .add_separator() \
            .add_action("E&xit", self.close, "Ctrl+Q")

        # Edit menu
        self.add_menu("&Edit") \
            .add_action("&Undo", self.on_undo, "Ctrl+Z") \
            .add_action("&Redo", self.on_redo, "Ctrl+Y") \
            .add_separator() \
            .add_action("Cu&t", self.on_cut, "Ctrl+X") \
            .add_action("&Copy", self.on_copy, "Ctrl+C") \
            .add_action("&Paste", self.on_paste, "Ctrl+V")

        # View menu
        self.add_menu("&View") \
            .add_checkable("Show &Sidebar", lambda c: print(f"Sidebar: {c}")) \
            .add_checkable("Show &Minimap", lambda c: print(f"Minimap: {c}"))

    def on_new(self): print("New")
    def on_open(self): print("Open")
    def on_undo(self): print("Undo")
    def on_redo(self): print("Redo")
    def on_cut(self): print("Cut")
    def on_copy(self): print("Copy")
    def on_paste(self): print("Paste")

def main():
    app = QApplication(sys.argv)

    # Enable theme if available
    try:
        from vfwidgets_theme import ThemedApplication
        app = ThemedApplication.create_or_get_application()
        app.set_theme("dark")
    except ImportError:
        pass

    window = MyIDE()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

## API Reference

### `add_menu(title: str) -> MenuBuilder`

Add a new menu to the menu bar.

**Parameters:**
- `title`: Menu title (use `&` for keyboard mnemonics, e.g., `"&File"`)

**Returns:** `MenuBuilder` for method chaining

### `MenuBuilder.add_action(...)`

Add an action to the menu.

**Parameters:**
- `text`: Action text (required)
- `callback`: Function to call when triggered (optional)
- `shortcut`: Keyboard shortcut, e.g., `"Ctrl+O"` (optional)
- `icon`: QIcon (optional)
- `tooltip`: Tooltip and status tip text (optional)
- `enabled`: Whether action is enabled (default: `True`)
- `checkable`: Whether action is checkable (default: `False`)
- `checked`: Initial checked state if checkable (default: `False`)

**Returns:** `self` for chaining

### `MenuBuilder.add_separator()`

Add a separator line.

**Returns:** `self` for chaining

### `MenuBuilder.add_submenu(title: str)`

Add a submenu and switch context to it.

**Parameters:**
- `title`: Submenu title

**Returns:** `self` for chaining

**Important:** Must call `end_submenu()` to return to parent menu.

### `MenuBuilder.end_submenu()`

Return to parent menu after adding submenu items.

**Returns:** `self` for chaining

### `MenuBuilder.add_checkable(...)`

Add a checkable (toggle) action.

**Parameters:**
- `text`: Action text (required)
- `callback`: Function called with bool parameter (checked state) (optional)
- `checked`: Initial checked state (default: `False`)
- `shortcut`: Keyboard shortcut (optional)
- `tooltip`: Tooltip text (optional)
- `enabled`: Whether enabled (default: `True`)

**Returns:** `self` for chaining

### `MenuBuilder.add_action_group(...)`

Add a group of mutually exclusive actions (radio buttons).

**Parameters:**
- `actions`: List of `(text, callback)` tuples (required)
- `exclusive`: Whether actions are mutually exclusive (default: `True`)
- `default_index`: Index of initially checked action (default: `0`)

**Returns:** `self` for chaining

## Migration from Old API

### Before (Old API - 67 lines)

```python
def _setup_file_menu(self):
    from PySide6.QtWidgets import QMenuBar

    menu_bar = self.get_menu_bar()
    if not menu_bar:
        menu_bar = QMenuBar()

    file_menu = menu_bar.addMenu("&File")

    open_action = file_menu.addAction("&Open...")
    open_action.setShortcut("Ctrl+O")
    open_action.setStatusTip("Open a file")
    open_action.triggered.connect(self._on_open)

    close_action = file_menu.addAction("&Close")
    close_action.setShortcut("Ctrl+W")
    close_action.setStatusTip("Close the current tab")
    close_action.triggered.connect(self._on_close)

    file_menu.addSeparator()

    exit_action = file_menu.addAction("E&xit")
    exit_action.setShortcut("Ctrl+Q")
    exit_action.setStatusTip("Exit")
    exit_action.triggered.connect(self.close)

    self.set_menu_bar(menu_bar)  # MUST BE LAST!

def showEvent(self, event):
    # 22 more lines of theme workaround code...
    super().showEvent(event)
    # Theme integration hacks...
```

### After (New API - 17 lines)

```python
def _setup_file_menu(self):
    self.add_menu("&File") \
        .add_action("&Open...", self._on_open, "Ctrl+O",
                    tooltip="Open a file") \
        .add_action("&Close", self._on_close, "Ctrl+W",
                    tooltip="Close the current tab") \
        .add_separator() \
        .add_action("E&xit", self.close, "Ctrl+Q",
                    tooltip="Exit")

# showEvent workaround removed - not needed!
```

**Result:** 75% less code, automatic theme integration, no initialization traps!

## Troubleshooting

### My menu doesn't appear

Make sure you're calling `add_menu()` in your `__init__()` or similar initialization method.  The menu bar is automatically integrated when the window is shown.

### Theme colors not applied

The fluent API automatically applies theme colors if `vfwidgets-theme` is installed. No manual intervention needed!

### Submenu items not showing

Make sure you call `end_submenu()` after adding submenu items:

```python
self.add_menu("File") \
    .add_submenu("Recent") \
        .add_action("file1.txt") \
        .add_action("file2.txt") \
    .end_submenu()  # Don't forget this!
```

### ValueError: end_submenu() called without matching add_submenu()

You called `end_submenu()` too many times. Each `add_submenu()` must have exactly one matching `end_submenu()`.

## See Also

- [Example 06: Menu Fluent API](../examples/06_menu_fluent_api.py) - Complete working example
- [Example 05: Advanced IDE](../examples/05_advanced_ide.py) - Real-world usage
- [MenuBuilder API](../src/vfwidgets_vilocode_window/menu_builder.py) - Source code with detailed docstrings
