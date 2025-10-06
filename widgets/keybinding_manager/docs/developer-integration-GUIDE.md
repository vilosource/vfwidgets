# KeybindingManager Developer Integration Guide

**Document Type**: GUIDE
**Audience**: Application Developers
**Purpose**: How to integrate KeybindingManager into your application

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Core Concepts](#core-concepts)
3. [Integration Patterns](#integration-patterns)
4. [Callback Patterns](#callback-patterns)
5. [Migration from Hardcoded Shortcuts](#migration-from-hardcoded-shortcuts)
6. [Advanced Usage](#advanced-usage)
7. [Testing](#testing)
8. [Best Practices](#best-practices)

---

## Quick Start

### 3-Step Integration

```python
from PySide6.QtWidgets import QMainWindow
from vfwidgets_keybinding import KeybindingManager, ActionDefinition

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Step 1: Create manager with storage path
        self.manager = KeybindingManager(
            storage_path="~/.config/myapp/keybindings.json",
            auto_save=True
        )

        # Step 2: Register actions with callbacks
        self.manager.register_action(ActionDefinition(
            id="file.save",
            description="Save File",
            default_shortcut="Ctrl+S",
            category="File",
            callback=self.save_file
        ))

        # Step 3: Apply shortcuts to window
        self.manager.apply_shortcuts(self)

    def save_file(self):
        print("Saving file...")
```

That's it! The shortcut is now active and persisted.

---

## Core Concepts

### ActionDefinition

Defines what an action is and what it does:

```python
ActionDefinition(
    id="edit.copy",              # Unique identifier (dot-separated)
    description="Copy",          # Human-readable name
    default_shortcut="Ctrl+C",   # Default keyboard shortcut
    category="Edit",             # Category for grouping (optional)
    callback=self.copy           # Function to call (optional)
)
```

**Action ID Naming Convention:**
```
<category>.<action>

Examples:
  file.save
  file.open
  edit.copy
  view.fullscreen
  help.about
```

### KeybindingManager

Central orchestrator that:
- Stores action definitions (ActionRegistry)
- Manages keybinding persistence (KeybindingStorage)
- Creates and applies QActions to widgets
- Handles user customizations

---

## Integration Patterns

### Pattern 1: Basic Integration

**Use When**: Simple application with a few shortcuts

```python
class SimpleApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create manager
        self.manager = KeybindingManager()

        # Register actions
        self.manager.register_actions([
            ActionDefinition(
                id="app.quit",
                description="Quit",
                default_shortcut="Ctrl+Q",
                callback=self.close
            )
        ])

        # Apply to window
        self.manager.apply_shortcuts(self)
```

### Pattern 2: Persistent Shortcuts

**Use When**: You want shortcuts to persist across sessions

```python
from pathlib import Path

class PersistentApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Define storage location
        config_dir = Path.home() / ".config" / "myapp"
        storage_path = config_dir / "keybindings.json"

        # Create manager with persistence
        self.manager = KeybindingManager(
            storage_path=str(storage_path),
            auto_save=True  # Automatically save changes
        )

        # Register actions
        self._register_actions()

        # Load saved keybindings (or use defaults)
        self.manager.load_bindings()

        # Apply shortcuts
        self.manager.apply_shortcuts(self)

    def _register_actions(self):
        """Centralize action registration."""
        self.manager.register_actions([
            ActionDefinition(
                id="file.save",
                description="Save",
                default_shortcut="Ctrl+S",
                category="File",
                callback=self.save
            ),
            # ... more actions
        ])
```

### Pattern 3: Menu Integration

**Use When**: You want shortcuts to appear in menus

```python
class MenuApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Setup manager
        self.manager = KeybindingManager()
        self._register_actions()

        # Apply shortcuts FIRST (creates QActions)
        self.actions = self.manager.apply_shortcuts(self)

        # Then use QActions in menus
        self._create_menus()

    def _create_menus(self):
        """Create menus using QActions from manager."""
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")
        file_menu.addAction(self.actions["file.save"])
        file_menu.addAction(self.actions["file.open"])
        file_menu.addAction(self.actions["file.quit"])

        # Edit menu
        edit_menu = menu_bar.addMenu("Edit")
        edit_menu.addAction(self.actions["edit.copy"])
        edit_menu.addAction(self.actions["edit.paste"])
```

### Pattern 4: Category-Based Menus

**Use When**: You want automatic menu generation

```python
class CategorizedApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.manager = KeybindingManager()
        self._register_actions()
        self.actions = self.manager.apply_shortcuts(self)
        self._create_menus()

    def _create_menus(self):
        """Automatically create menus from categories."""
        menu_bar = self.menuBar()

        # Iterate through categories
        for category in self.manager.get_categories():
            menu = menu_bar.addMenu(category)

            # Add all actions in this category
            for action_def in self.manager.get_actions_by_category(category):
                qaction = self.actions.get(action_def.id)
                if qaction:
                    menu.addAction(qaction)
```

---

## Callback Patterns

### Method Callbacks

```python
class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.manager = KeybindingManager()

        # Direct method reference
        self.manager.register_action(ActionDefinition(
            id="file.save",
            description="Save",
            default_shortcut="Ctrl+S",
            callback=self.save_file  # Method reference
        ))

        self.manager.apply_shortcuts(self)

    def save_file(self):
        """This gets called when Ctrl+S is pressed."""
        print("Saving...")
```

### Lambda Callbacks

```python
# Simple lambda
self.manager.register_action(ActionDefinition(
    id="debug.toggle",
    description="Toggle Debug",
    default_shortcut="F12",
    callback=lambda: self.set_debug(not self.debug_mode)
))

# Lambda with parameters
self.manager.register_action(ActionDefinition(
    id="zoom.in",
    description="Zoom In",
    default_shortcut="Ctrl++",
    callback=lambda: self.set_zoom(self.zoom_level + 0.1)
))
```

### Signal Connections

```python
from PySide6.QtCore import Signal

class MyApp(QMainWindow):
    file_saved = Signal()

    def __init__(self):
        super().__init__()
        self.manager = KeybindingManager()

        # Connect to signal
        self.manager.register_action(ActionDefinition(
            id="file.save",
            description="Save",
            default_shortcut="Ctrl+S",
            callback=lambda: self.file_saved.emit()
        ))

        # Connect signal to slot
        self.file_saved.connect(self.on_file_saved)

        self.manager.apply_shortcuts(self)

    def on_file_saved(self):
        print("File saved signal received")
```

### Manual QAction Connection

```python
class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.manager = KeybindingManager()

        # Register action without callback
        self.manager.register_action(ActionDefinition(
            id="file.save",
            description="Save",
            default_shortcut="Ctrl+S"
            # No callback specified
        ))

        # Apply shortcuts
        actions = self.manager.apply_shortcuts(self)

        # Manually connect the QAction
        save_action = actions["file.save"]
        save_action.triggered.connect(self.save_file)

    def save_file(self):
        print("Saving...")
```

---

## Migration from Hardcoded Shortcuts

### Before: Hardcoded QActions

```python
class OldApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Hardcoded shortcuts
        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.triggered.connect(self.save_file)
        self.addAction(save_action)

        open_action = QAction("Open", self)
        open_action.setShortcut(QKeySequence("Ctrl+O"))
        open_action.triggered.connect(self.open_file)
        self.addAction(open_action)
```

### After: KeybindingManager

```python
class NewApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Flexible, user-customizable shortcuts
        self.manager = KeybindingManager("~/.config/myapp/shortcuts.json")

        self.manager.register_actions([
            ActionDefinition(
                id="file.save",
                description="Save",
                default_shortcut="Ctrl+S",
                callback=self.save_file
            ),
            ActionDefinition(
                id="file.open",
                description="Open",
                default_shortcut="Ctrl+O",
                callback=self.open_file
            )
        ])

        self.manager.load_bindings()
        self.manager.apply_shortcuts(self)
```

### Migration Steps

1. **Identify all QActions** with shortcuts
2. **Convert to ActionDefinitions**:
   - `QAction text` → `description`
   - `setShortcut()` → `default_shortcut`
   - `triggered.connect()` → `callback`
3. **Choose action IDs** (use dot-separated naming)
4. **Add categories** for organization
5. **Test** that all shortcuts work
6. **Remove** old QAction code

---

## Advanced Usage

### Dynamic Action Registration

```python
class DynamicApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.manager = KeybindingManager()
        self.manager.apply_shortcuts(self)

    def add_plugin(self, plugin):
        """Dynamically register plugin actions."""
        for action in plugin.get_actions():
            self.manager.register_action(action)

        # Re-apply shortcuts to include new actions
        self.manager.apply_shortcuts(self)
```

### Conditional Actions

```python
class ConditionalApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.manager = KeybindingManager()

        # Register action with conditional callback
        self.manager.register_action(ActionDefinition(
            id="edit.paste",
            description="Paste",
            default_shortcut="Ctrl+V",
            callback=self.try_paste
        ))

        self.manager.apply_shortcuts(self)

    def try_paste(self):
        """Only paste if clipboard has content."""
        clipboard = QApplication.clipboard()
        if clipboard.text():
            self.editor.insertPlainText(clipboard.text())
        else:
            QMessageBox.information(self, "Paste", "Clipboard is empty")
```

### Context-Aware Actions

```python
class ContextApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.manager = KeybindingManager()

        # Same shortcut, different behavior based on context
        self.manager.register_action(ActionDefinition(
            id="context.delete",
            description="Delete",
            default_shortcut="Del",
            callback=self.context_delete
        ))

        self.manager.apply_shortcuts(self)

    def context_delete(self):
        """Delete behavior depends on what's focused."""
        focus_widget = QApplication.focusWidget()

        if isinstance(focus_widget, QTextEdit):
            focus_widget.textCursor().removeSelectedText()
        elif isinstance(focus_widget, QListWidget):
            focus_widget.takeItem(focus_widget.currentRow())
        else:
            print("Delete not applicable in this context")
```

### Programmatic Shortcut Changes

```python
class CustomizableApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.manager = KeybindingManager("~/.config/myapp/shortcuts.json")
        self._register_actions()
        self.manager.load_bindings()
        self.manager.apply_shortcuts(self)

    def change_shortcut(self, action_id: str, new_shortcut: str):
        """Allow programmatic shortcut changes."""
        if self.manager.set_binding(action_id, new_shortcut):
            QMessageBox.information(
                self,
                "Shortcut Changed",
                f"'{action_id}' is now bound to {new_shortcut}"
            )
        else:
            QMessageBox.warning(
                self,
                "Error",
                f"Action '{action_id}' not found"
            )

    def reset_all_shortcuts(self):
        """Reset to defaults."""
        reply = QMessageBox.question(
            self,
            "Reset Shortcuts",
            "Reset all keyboard shortcuts to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.manager.reset_to_defaults()
            QMessageBox.information(self, "Reset", "Shortcuts reset to defaults")
```

---

## Testing

### Unit Testing Actions

```python
import pytest
from PySide6.QtWidgets import QApplication
from vfwidgets_keybinding import KeybindingManager, ActionDefinition

@pytest.fixture
def qapp():
    """Qt application fixture."""
    return QApplication.instance() or QApplication([])

@pytest.fixture
def manager():
    """Keybinding manager fixture."""
    return KeybindingManager()

def test_action_registration(manager):
    """Test action registration."""
    action = ActionDefinition(
        id="test.action",
        description="Test",
        default_shortcut="Ctrl+T"
    )

    manager.register_action(action)
    binding = manager.get_binding("test.action")

    assert binding == "Ctrl+T"

def test_callback_execution(qapp, manager):
    """Test callback is called."""
    called = []

    manager.register_action(ActionDefinition(
        id="test.callback",
        description="Test",
        default_shortcut="Ctrl+T",
        callback=lambda: called.append(True)
    ))

    actions = manager.apply_shortcuts(qapp.activeWindow())
    actions["test.callback"].trigger()

    assert called == [True]
```

### Integration Testing

```python
def test_full_integration(qapp, tmp_path):
    """Test complete integration."""
    storage_path = tmp_path / "shortcuts.json"

    # Create manager with storage
    manager = KeybindingManager(str(storage_path), auto_save=True)

    # Register action
    manager.register_action(ActionDefinition(
        id="file.save",
        description="Save",
        default_shortcut="Ctrl+S"
    ))

    # Change binding
    manager.set_binding("file.save", "Ctrl+Alt+S")

    # Verify saved to file
    assert storage_path.exists()

    # Create new manager and load
    manager2 = KeybindingManager(str(storage_path))
    manager2.register_action(ActionDefinition(
        id="file.save",
        description="Save",
        default_shortcut="Ctrl+S"
    ))
    manager2.load_bindings()

    # Verify custom binding loaded
    assert manager2.get_binding("file.save") == "Ctrl+Alt+S"
```

---

## Best Practices

### 1. Use Meaningful Action IDs

✅ **Good:**
```python
"file.save"
"edit.copy"
"view.fullscreen"
```

❌ **Bad:**
```python
"action1"
"doSave"
"COPY_ACTION"
```

### 2. Organize with Categories

```python
# File operations
ActionDefinition(id="file.new", category="File", ...)
ActionDefinition(id="file.open", category="File", ...)

# Edit operations
ActionDefinition(id="edit.cut", category="Edit", ...)
ActionDefinition(id="edit.copy", category="Edit", ...)
```

### 3. Provide Clear Descriptions

```python
# Description shown in UI
ActionDefinition(
    id="file.saveas",
    description="Save As...",  # User-friendly
    ...
)
```

### 4. Use Standard Shortcuts

Follow platform conventions:
```python
# Cross-platform standards
"file.save": "Ctrl+S"
"file.open": "Ctrl+O"
"edit.copy": "Ctrl+C"
"edit.paste": "Ctrl+V"
```

### 5. Centralize Action Registration

```python
class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.manager = KeybindingManager()
        self._register_actions()  # Single method
        self.manager.apply_shortcuts(self)

    def _register_actions(self):
        """All action registration in one place."""
        self.manager.register_actions([
            # ... all actions here
        ])
```

### 6. Handle Missing Callbacks Gracefully

```python
def safe_callback(self):
    """Callback with error handling."""
    try:
        self.perform_action()
    except Exception as e:
        logger.error(f"Action failed: {e}")
        QMessageBox.warning(self, "Error", str(e))
```

### 7. Document Your Action IDs

```python
# In your README or docs
"""
Keyboard Shortcuts:

File Operations:
  - file.new (Ctrl+N): Create new document
  - file.save (Ctrl+S): Save document

Edit Operations:
  - edit.copy (Ctrl+C): Copy selection
  - edit.paste (Ctrl+V): Paste clipboard
"""
```

---

## Summary

**Quick Integration:**
1. Create `KeybindingManager` with storage path
2. Register `ActionDefinition`s with callbacks
3. Call `apply_shortcuts(window)`

**Key Benefits:**
- ✅ User-customizable shortcuts
- ✅ Persistent across sessions
- ✅ Type-safe with full IDE support
- ✅ Automatic menu integration
- ✅ No manual QAction wiring

**Next Steps:**
- See `examples/02_full_application.py` for complete example
- Read `user-guide-GUIDE.md` for end-user documentation
- Check `architecture-DESIGN.md` for system design
