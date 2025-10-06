# KeybindingManager Implementation Tasks

**Document Type**: IMPLEMENTATION
**Status**: Active
**Created**: 2025-10-03
**Purpose**: Step-by-step implementation checklist for KeybindingManager widget

---

## Table of Contents

1. [Using This Document](#using-this-document)
2. [Phase 1: MVP + Core Developer Experience](#phase-1-mvp--core-developer-experience)
   - [Core Implementation](#core-implementation)
   - [Developer Experience](#developer-experience)
3. [Phase 2: UI + Polish](#phase-2-ui--polish)
4. [Phase 3: Advanced Features](#phase-3-advanced-features)
5. [References](#references)

---

## Using This Document

### How to Use This Task List

1. **Work sequentially** through tasks in each phase
2. **Check prerequisites** before starting each task
3. **Run tests** after completing each component
4. **Update documentation** as you implement features
5. **Mark tasks complete** only when acceptance criteria are met

### Task Format

Each task includes:
- **Prerequisites**: What must be done before starting
- **Files to Create/Modify**: Specific file paths
- **Acceptance Criteria**: How to know when it's complete
- **Estimated Time**: Time budget for planning
- **Dependencies**: Related tasks or components

### Status Indicators

- ⬜ Not Started
- 🔄 In Progress
- ✅ Complete
- ⚠️ Blocked (waiting on dependency)

---

## Phase 1: MVP + Core Developer Experience

**Goal**: Working keybinding system with exceptional DX for integration

**Duration**: 8-12 hours

**Exit Criteria**:
- [ ] All unit tests passing
- [ ] Type hints verified with `mypy --strict`
- [ ] Examples run without errors
- [ ] Documentation reviewed for clarity
- [ ] Integration test with ViloxTerm works

---

### Core Implementation

#### Task 1: Create ActionDefinition Dataclass

**Status**: ⬜ Not Started

**Prerequisites**: None

**Estimated Time**: 30 minutes

**Files to Create**:
- `widgets/keybinding_manager/src/vfwidgets_keybinding/registry.py`

**Implementation Steps**:

1. Create `registry.py` file with proper module docstring
2. Import required dependencies:
   ```python
   from dataclasses import dataclass
   from typing import Optional, Callable
   from PySide6.QtGui import QAction
   ```

3. Implement `ActionDefinition` dataclass:
   ```python
   @dataclass(frozen=True)
   class ActionDefinition:
       """Definition of an action that can be bound to keyboard shortcuts.

       An action represents a command that can be triggered by the user,
       either through keyboard shortcuts, menus, or buttons.

       Attributes:
           id: Unique identifier for the action (e.g., "file.save", "edit.copy")
           description: Human-readable description shown in UI
           default_shortcut: Default keyboard shortcut (e.g., "Ctrl+S")
           category: Category for grouping actions (e.g., "File", "Edit")
           callback: Optional function to execute when triggered

       Example:
           >>> save_action = ActionDefinition(
           ...     id="file.save",
           ...     description="Save File",
           ...     default_shortcut="Ctrl+S",
           ...     category="File"
           ... )
       """
       id: str
       description: str
       default_shortcut: Optional[str] = None
       category: Optional[str] = None
       callback: Optional[Callable[[], None]] = None

       def __post_init__(self):
           """Validate action definition after initialization."""
           if not self.id:
               raise ValueError("Action ID cannot be empty")
           if not self.description:
               raise ValueError("Action description cannot be empty")
   ```

4. Add validation for action ID format (dot-separated):
   ```python
   if "." not in self.id:
       raise ValueError(f"Action ID must be dot-separated (e.g., 'category.action'), got: {self.id}")
   ```

**Acceptance Criteria**:
- [ ] `ActionDefinition` dataclass created with all required fields
- [ ] Validation raises `ValueError` for empty ID/description
- [ ] Validation enforces dot-separated ID format
- [ ] Dataclass is frozen (immutable)
- [ ] Comprehensive docstring with example
- [ ] Type hints for all fields

**Testing**:
```python
# Quick test in Python REPL
from vfwidgets_keybinding.registry import ActionDefinition

# Valid action
action = ActionDefinition(id="file.save", description="Save File")
assert action.id == "file.save"

# Invalid action (should raise ValueError)
try:
    ActionDefinition(id="", description="Test")
    assert False, "Should have raised ValueError"
except ValueError:
    pass  # Expected
```

---

#### Task 2: Create ActionRegistry Class

**Status**: ⬜ Not Started

**Prerequisites**: Task 1 complete

**Estimated Time**: 2 hours

**Files to Modify**:
- `widgets/keybinding_manager/src/vfwidgets_keybinding/registry.py`

**Implementation Steps**:

1. Add imports at top of `registry.py`:
   ```python
   from typing import Dict, List, Optional
   import logging
   ```

2. Create logger:
   ```python
   logger = logging.getLogger(__name__)
   ```

3. Implement `ActionRegistry` class:
   ```python
   class ActionRegistry:
       """Registry for managing application actions.

       The ActionRegistry maintains a central database of all available actions
       in the application. It supports registering, unregistering, querying, and
       grouping actions by category.

       This follows the Command Pattern, decoupling action definitions from
       their keybindings.

       Example:
           >>> registry = ActionRegistry()
           >>> registry.register(ActionDefinition(
           ...     id="file.save",
           ...     description="Save File",
           ...     default_shortcut="Ctrl+S",
           ...     category="File"
           ... ))
           >>> action = registry.get("file.save")
           >>> print(action.description)
           Save File
       """

       def __init__(self):
           """Initialize empty action registry."""
           self._actions: Dict[str, ActionDefinition] = {}
           logger.info("ActionRegistry initialized")
   ```

4. Implement `register()` method:
   ```python
   def register(self, action: ActionDefinition) -> None:
       """Register a new action.

       Args:
           action: Action definition to register

       Raises:
           ValueError: If action ID is already registered

       Example:
           >>> registry.register(ActionDefinition(
           ...     id="edit.copy",
           ...     description="Copy",
           ...     default_shortcut="Ctrl+C"
           ... ))
       """
       if action.id in self._actions:
           raise ValueError(f"Action '{action.id}' is already registered")

       self._actions[action.id] = action
       logger.debug(f"Registered action: {action.id}")
   ```

5. Implement `unregister()` method:
   ```python
   def unregister(self, action_id: str) -> None:
       """Unregister an action.

       Args:
           action_id: ID of action to remove

       Raises:
           KeyError: If action ID is not registered

       Example:
           >>> registry.unregister("edit.copy")
       """
       if action_id not in self._actions:
           raise KeyError(f"Action '{action_id}' is not registered")

       del self._actions[action_id]
       logger.debug(f"Unregistered action: {action_id}")
   ```

6. Implement `get()` method:
   ```python
   def get(self, action_id: str) -> Optional[ActionDefinition]:
       """Get action definition by ID.

       Args:
           action_id: ID of action to retrieve

       Returns:
           ActionDefinition if found, None otherwise

       Example:
           >>> action = registry.get("file.save")
           >>> if action:
           ...     print(action.description)
       """
       return self._actions.get(action_id)
   ```

7. Implement `get_all()` method:
   ```python
   def get_all(self) -> List[ActionDefinition]:
       """Get all registered actions.

       Returns:
           List of all action definitions

       Example:
           >>> actions = registry.get_all()
           >>> print(f"Total actions: {len(actions)}")
       """
       return list(self._actions.values())
   ```

8. Implement `get_by_category()` method:
   ```python
   def get_by_category(self, category: str) -> List[ActionDefinition]:
       """Get all actions in a specific category.

       Args:
           category: Category name to filter by

       Returns:
           List of actions in the specified category

       Example:
           >>> file_actions = registry.get_by_category("File")
           >>> for action in file_actions:
           ...     print(action.description)
       """
       return [
           action for action in self._actions.values()
           if action.category == category
       ]
   ```

9. Implement `get_categories()` method:
   ```python
   def get_categories(self) -> List[str]:
       """Get all unique categories.

       Returns:
           Sorted list of category names

       Example:
           >>> categories = registry.get_categories()
           >>> print(", ".join(categories))
           Edit, File, View
       """
       categories = {
           action.category
           for action in self._actions.values()
           if action.category is not None
       }
       return sorted(categories)
   ```

10. Implement `clear()` method:
    ```python
    def clear(self) -> None:
        """Remove all registered actions.

        Warning:
            This will clear ALL actions. Use with caution.

        Example:
            >>> registry.clear()
            >>> assert len(registry.get_all()) == 0
        """
        self._actions.clear()
        logger.info("Cleared all actions from registry")
    ```

**Acceptance Criteria**:
- [ ] `ActionRegistry` class created with all methods
- [ ] `register()` prevents duplicate IDs
- [ ] `unregister()` raises `KeyError` for missing actions
- [ ] `get()` returns `None` for missing actions (no exception)
- [ ] `get_by_category()` filters correctly
- [ ] `get_categories()` returns sorted unique categories
- [ ] All methods have comprehensive docstrings with examples
- [ ] Type hints for all method signatures
- [ ] Logging for important operations

**Testing**:
```python
# Quick test in Python REPL
from vfwidgets_keybinding.registry import ActionRegistry, ActionDefinition

registry = ActionRegistry()

# Register actions
registry.register(ActionDefinition(
    id="file.save",
    description="Save File",
    category="File",
    default_shortcut="Ctrl+S"
))

registry.register(ActionDefinition(
    id="edit.copy",
    description="Copy",
    category="Edit",
    default_shortcut="Ctrl+C"
))

# Test retrieval
assert registry.get("file.save").description == "Save File"
assert len(registry.get_all()) == 2
assert len(registry.get_by_category("File")) == 1
assert "File" in registry.get_categories()

# Test duplicate registration (should fail)
try:
    registry.register(ActionDefinition(id="file.save", description="Duplicate"))
    assert False, "Should have raised ValueError"
except ValueError:
    pass  # Expected

print("✅ ActionRegistry tests passed!")
```

---

#### Task 3: Create KeybindingStorage Class

**Status**: ⬜ Not Started

**Prerequisites**: None (independent of ActionRegistry)

**Estimated Time**: 2 hours

**Files to Create**:
- `widgets/keybinding_manager/src/vfwidgets_keybinding/storage.py`

**Implementation Steps**:

1. Create `storage.py` with module docstring and imports:
   ```python
   """Persistent storage for keyboard shortcuts.

   Provides JSON-based storage for saving and loading user-customized
   keyboard shortcuts. Supports default keybindings, user overrides,
   and validation.
   """

   import json
   import logging
   from pathlib import Path
   from typing import Dict, Optional

   logger = logging.getLogger(__name__)
   ```

2. Implement `KeybindingStorage` class:
   ```python
   class KeybindingStorage:
       """Manages persistent storage of keyboard shortcuts.

       Stores keybindings in JSON format with support for:
       - Default keybindings (application-defined)
       - User overrides (user-customized)
       - Validation on load
       - Atomic writes (prevents corruption)

       File Format:
           {
               "file.save": "Ctrl+S",
               "edit.copy": "Ctrl+C",
               "custom.action": null  // Unbound action
           }

       Example:
           >>> storage = KeybindingStorage("~/.config/myapp/keybindings.json")
           >>> storage.save({"file.save": "Ctrl+S"})
           >>> bindings = storage.load()
           >>> print(bindings.get("file.save"))
           Ctrl+S
       """

       def __init__(self, file_path: Optional[str] = None):
           """Initialize keybinding storage.

           Args:
               file_path: Path to JSON file for storage. If None, uses in-memory only.

           Example:
               >>> storage = KeybindingStorage("~/.config/myapp/keybindings.json")
           """
           self._file_path = Path(file_path).expanduser() if file_path else None
           self._in_memory_bindings: Dict[str, Optional[str]] = {}
           logger.info(f"KeybindingStorage initialized: {self._file_path or 'in-memory'}")
   ```

3. Implement `load()` method:
   ```python
   def load(self) -> Dict[str, Optional[str]]:
       """Load keybindings from file.

       Returns:
           Dictionary mapping action IDs to shortcuts.
           Returns empty dict if file doesn't exist or is invalid.

       Example:
           >>> bindings = storage.load()
           >>> if "file.save" in bindings:
           ...     print(f"Save is bound to: {bindings['file.save']}")
       """
       # If no file path, return in-memory bindings
       if not self._file_path:
           logger.debug("No file path - returning in-memory bindings")
           return self._in_memory_bindings.copy()

       # If file doesn't exist, return empty dict
       if not self._file_path.exists():
           logger.debug(f"Keybinding file not found: {self._file_path}")
           return {}

       try:
           with open(self._file_path, 'r', encoding='utf-8') as f:
               bindings = json.load(f)

           # Validate format
           if not isinstance(bindings, dict):
               logger.error(f"Invalid keybinding file format: expected dict, got {type(bindings)}")
               return {}

           # Validate keys and values
           validated_bindings = {}
           for action_id, shortcut in bindings.items():
               if not isinstance(action_id, str):
                   logger.warning(f"Skipping non-string action ID: {action_id}")
                   continue

               if shortcut is not None and not isinstance(shortcut, str):
                   logger.warning(f"Skipping invalid shortcut for '{action_id}': {shortcut}")
                   continue

               validated_bindings[action_id] = shortcut

           logger.info(f"Loaded {len(validated_bindings)} keybindings from {self._file_path}")
           return validated_bindings

       except json.JSONDecodeError as e:
           logger.error(f"Failed to parse keybinding file: {e}")
           return {}
       except Exception as e:
           logger.error(f"Failed to load keybindings: {e}")
           return {}
   ```

4. Implement `save()` method:
   ```python
   def save(self, bindings: Dict[str, Optional[str]]) -> bool:
       """Save keybindings to file.

       Uses atomic write (write to temp file, then rename) to prevent corruption.

       Args:
           bindings: Dictionary mapping action IDs to shortcuts

       Returns:
           True if save succeeded, False otherwise

       Example:
           >>> success = storage.save({
           ...     "file.save": "Ctrl+S",
           ...     "edit.copy": "Ctrl+C"
           ... })
           >>> if success:
           ...     print("Keybindings saved!")
       """
       # If no file path, store in memory
       if not self._file_path:
           self._in_memory_bindings = bindings.copy()
           logger.debug("Saved bindings to in-memory storage")
           return True

       try:
           # Ensure parent directory exists
           self._file_path.parent.mkdir(parents=True, exist_ok=True)

           # Atomic write: write to temp file, then rename
           temp_file = self._file_path.with_suffix('.tmp')

           with open(temp_file, 'w', encoding='utf-8') as f:
               json.dump(bindings, f, indent=2, sort_keys=True)

           # Atomic rename (overwrites existing file)
           temp_file.replace(self._file_path)

           logger.info(f"Saved {len(bindings)} keybindings to {self._file_path}")
           return True

       except Exception as e:
           logger.error(f"Failed to save keybindings: {e}")
           return False
   ```

5. Implement `merge()` helper method:
   ```python
   def merge(
       self,
       defaults: Dict[str, Optional[str]],
       overrides: Optional[Dict[str, Optional[str]]] = None
   ) -> Dict[str, Optional[str]]:
       """Merge default keybindings with user overrides.

       User overrides take precedence. Use None value to unbind an action.

       Args:
           defaults: Default keybindings (from ActionRegistry)
           overrides: User-customized keybindings (from file)

       Returns:
           Merged keybindings

       Example:
           >>> defaults = {"file.save": "Ctrl+S", "edit.copy": "Ctrl+C"}
           >>> overrides = {"file.save": "Ctrl+Alt+S"}  # User changed this
           >>> merged = storage.merge(defaults, overrides)
           >>> print(merged["file.save"])
           Ctrl+Alt+S
       """
       merged = defaults.copy()

       if overrides:
           merged.update(overrides)

       logger.debug(f"Merged {len(defaults)} defaults with {len(overrides or {})} overrides")
       return merged
   ```

6. Implement `reset()` method:
   ```python
   def reset(self) -> bool:
       """Delete stored keybindings file.

       This will reset to application defaults on next load.

       Returns:
           True if file was deleted or doesn't exist, False on error

       Example:
           >>> storage.reset()  # Delete custom keybindings
           >>> bindings = storage.load()  # Will be empty
       """
       if not self._file_path:
           self._in_memory_bindings.clear()
           logger.info("Cleared in-memory bindings")
           return True

       try:
           if self._file_path.exists():
               self._file_path.unlink()
               logger.info(f"Deleted keybinding file: {self._file_path}")
           return True
       except Exception as e:
           logger.error(f"Failed to delete keybinding file: {e}")
           return False
   ```

**Acceptance Criteria**:
- [ ] `KeybindingStorage` class created with all methods
- [ ] `load()` returns empty dict for missing file (no exception)
- [ ] `load()` validates JSON format and skips invalid entries
- [ ] `save()` uses atomic write (temp file + rename)
- [ ] `save()` creates parent directories if needed
- [ ] `merge()` correctly prioritizes user overrides
- [ ] `reset()` deletes file safely
- [ ] In-memory mode works when `file_path=None`
- [ ] All methods have comprehensive docstrings with examples
- [ ] Type hints for all method signatures
- [ ] Logging for important operations

**Testing**:
```python
# Quick test in Python REPL
import tempfile
from pathlib import Path
from vfwidgets_keybinding.storage import KeybindingStorage

# Create temp file for testing
temp_dir = Path(tempfile.mkdtemp())
storage = KeybindingStorage(temp_dir / "test_keybindings.json")

# Test save and load
bindings = {"file.save": "Ctrl+S", "edit.copy": "Ctrl+C"}
assert storage.save(bindings) == True

loaded = storage.load()
assert loaded == bindings

# Test merge
defaults = {"file.save": "Ctrl+S", "edit.paste": "Ctrl+V"}
overrides = {"file.save": "Ctrl+Alt+S"}
merged = storage.merge(defaults, overrides)
assert merged["file.save"] == "Ctrl+Alt+S"
assert merged["edit.paste"] == "Ctrl+V"

# Test reset
assert storage.reset() == True
loaded = storage.load()
assert loaded == {}

print("✅ KeybindingStorage tests passed!")

# Cleanup
import shutil
shutil.rmtree(temp_dir)
```

---

#### Task 4: Create KeybindingManager Class

**Status**: ⬜ Not Started

**Prerequisites**: Task 2 and Task 3 complete

**Estimated Time**: 3 hours

**Files to Create**:
- `widgets/keybinding_manager/src/vfwidgets_keybinding/manager.py`

**Implementation Steps**:

1. Create `manager.py` with module docstring and imports:
   ```python
   """Central manager for keyboard shortcuts.

   The KeybindingManager is the main API for integrating keyboard shortcuts
   into your application. It orchestrates the ActionRegistry and KeybindingStorage
   to provide a complete keybinding solution.
   """

   import logging
   from typing import Dict, List, Optional, Callable
   from PySide6.QtWidgets import QWidget
   from PySide6.QtGui import QAction, QKeySequence

   from .registry import ActionRegistry, ActionDefinition
   from .storage import KeybindingStorage

   logger = logging.getLogger(__name__)
   ```

2. Implement `KeybindingManager` class constructor:
   ```python
   class KeybindingManager:
       """Central manager for keyboard shortcuts.

       The KeybindingManager provides a high-level API for:
       - Registering actions
       - Loading/saving keybindings
       - Applying shortcuts to widgets
       - Querying bindings

       This is the main entry point for integrating keybinding management
       into your application.

       Example:
           >>> manager = KeybindingManager(storage_path="~/.config/myapp/keys.json")
           >>>
           >>> # Register actions
           >>> manager.register_action(ActionDefinition(
           ...     id="file.save",
           ...     description="Save File",
           ...     default_shortcut="Ctrl+S",
           ...     category="File"
           ... ))
           >>>
           >>> # Apply shortcuts to widget
           >>> manager.apply_shortcuts(main_window)
       """

       def __init__(
           self,
           storage_path: Optional[str] = None,
           auto_save: bool = True
       ):
           """Initialize keybinding manager.

           Args:
               storage_path: Path to JSON file for persistent storage.
                           If None, keybindings are not persisted.
               auto_save: If True, automatically save when bindings change

           Example:
               >>> manager = KeybindingManager("~/.config/myapp/keybindings.json")
           """
           self._registry = ActionRegistry()
           self._storage = KeybindingStorage(storage_path)
           self._auto_save = auto_save
           self._current_bindings: Dict[str, Optional[str]] = {}
           self._applied_actions: Dict[str, QAction] = {}  # Track created QActions

           logger.info(f"KeybindingManager initialized (auto_save={auto_save})")
   ```

3. Implement `register_action()` method:
   ```python
   def register_action(self, action: ActionDefinition) -> None:
       """Register a new action.

       Args:
           action: Action definition to register

       Raises:
           ValueError: If action ID is already registered

       Example:
           >>> manager.register_action(ActionDefinition(
           ...     id="file.save",
           ...     description="Save File",
           ...     default_shortcut="Ctrl+S",
           ...     category="File"
           ... ))
       """
       self._registry.register(action)

       # Add default binding to current bindings if not already set
       if action.id not in self._current_bindings:
           self._current_bindings[action.id] = action.default_shortcut

       logger.debug(f"Registered action: {action.id}")
   ```

4. Implement `register_actions()` batch method:
   ```python
   def register_actions(self, actions: List[ActionDefinition]) -> None:
       """Register multiple actions at once.

       Args:
           actions: List of action definitions to register

       Example:
           >>> manager.register_actions([
           ...     ActionDefinition(id="file.save", description="Save", default_shortcut="Ctrl+S"),
           ...     ActionDefinition(id="file.open", description="Open", default_shortcut="Ctrl+O"),
           ... ])
       """
       for action in actions:
           self.register_action(action)

       logger.info(f"Registered {len(actions)} actions")
   ```

5. Implement `load_bindings()` method:
   ```python
   def load_bindings(self) -> None:
       """Load keybindings from storage.

       Merges stored user customizations with registered action defaults.

       Example:
           >>> manager.load_bindings()  # Load from storage file
       """
       # Get default bindings from registry
       defaults = {
           action.id: action.default_shortcut
           for action in self._registry.get_all()
       }

       # Load user overrides
       overrides = self._storage.load()

       # Merge (user overrides take precedence)
       self._current_bindings = self._storage.merge(defaults, overrides)

       logger.info(f"Loaded {len(self._current_bindings)} keybindings")
   ```

6. Implement `save_bindings()` method:
   ```python
   def save_bindings(self) -> bool:
       """Save current keybindings to storage.

       Returns:
           True if save succeeded, False otherwise

       Example:
           >>> manager.save_bindings()
       """
       success = self._storage.save(self._current_bindings)

       if success:
           logger.info("Keybindings saved successfully")
       else:
           logger.error("Failed to save keybindings")

       return success
   ```

7. Implement `set_binding()` method:
   ```python
   def set_binding(self, action_id: str, shortcut: Optional[str]) -> bool:
       """Change the keyboard shortcut for an action.

       Args:
           action_id: ID of action to bind
           shortcut: New keyboard shortcut (e.g., "Ctrl+S"), or None to unbind

       Returns:
           True if binding was changed, False if action doesn't exist

       Example:
           >>> manager.set_binding("file.save", "Ctrl+Alt+S")  # Change binding
           >>> manager.set_binding("file.close", None)  # Unbind action
       """
       # Check if action exists
       action = self._registry.get(action_id)
       if not action:
           logger.warning(f"Cannot set binding: action '{action_id}' not registered")
           return False

       # Update binding
       old_shortcut = self._current_bindings.get(action_id)
       self._current_bindings[action_id] = shortcut

       # Update existing QAction if it exists
       if action_id in self._applied_actions:
           qaction = self._applied_actions[action_id]
           if shortcut:
               qaction.setShortcut(QKeySequence(shortcut))
           else:
               qaction.setShortcut(QKeySequence())

       logger.info(f"Changed binding for '{action_id}': {old_shortcut} → {shortcut}")

       # Auto-save if enabled
       if self._auto_save:
           self.save_bindings()

       return True
   ```

8. Implement `get_binding()` method:
   ```python
   def get_binding(self, action_id: str) -> Optional[str]:
       """Get current keyboard shortcut for an action.

       Args:
           action_id: ID of action to query

       Returns:
           Current shortcut string, or None if unbound/not found

       Example:
           >>> shortcut = manager.get_binding("file.save")
           >>> print(f"Save is bound to: {shortcut}")
       """
       return self._current_bindings.get(action_id)
   ```

9. Implement `apply_shortcuts()` method:
   ```python
   def apply_shortcuts(
       self,
       widget: QWidget,
       action_ids: Optional[List[str]] = None
   ) -> Dict[str, QAction]:
       """Apply keyboard shortcuts to a widget.

       Creates QAction objects for each action and adds them to the widget.
       The shortcuts will work globally within the widget's context.

       Args:
           widget: Widget to apply shortcuts to (usually main window)
           action_ids: Specific action IDs to apply. If None, applies all registered actions.

       Returns:
           Dictionary mapping action IDs to created QAction objects

       Example:
           >>> actions = manager.apply_shortcuts(main_window)
           >>> save_action = actions.get("file.save")
           >>> if save_action:
           ...     save_action.triggered.connect(save_file)
       """
       # Determine which actions to apply
       if action_ids is None:
           actions_to_apply = self._registry.get_all()
       else:
           actions_to_apply = [
               self._registry.get(action_id)
               for action_id in action_ids
               if self._registry.get(action_id) is not None
           ]

       created_actions = {}

       for action_def in actions_to_apply:
           # Create QAction
           qaction = QAction(action_def.description, widget)

           # Set shortcut if bound
           shortcut = self._current_bindings.get(action_def.id)
           if shortcut:
               qaction.setShortcut(QKeySequence(shortcut))

           # Connect callback if provided
           if action_def.callback:
               qaction.triggered.connect(action_def.callback)

           # Add to widget
           widget.addAction(qaction)

           # Track created action
           self._applied_actions[action_def.id] = qaction
           created_actions[action_def.id] = qaction

           logger.debug(f"Applied shortcut for '{action_def.id}': {shortcut}")

       logger.info(f"Applied {len(created_actions)} shortcuts to {widget.__class__.__name__}")
       return created_actions
   ```

10. Implement `get_all_bindings()` method:
    ```python
    def get_all_bindings(self) -> Dict[str, Optional[str]]:
        """Get all current keybindings.

        Returns:
            Dictionary mapping action IDs to shortcuts

        Example:
            >>> bindings = manager.get_all_bindings()
            >>> for action_id, shortcut in bindings.items():
            ...     print(f"{action_id}: {shortcut}")
        """
        return self._current_bindings.copy()
    ```

11. Implement `reset_to_defaults()` method:
    ```python
    def reset_to_defaults(self) -> None:
        """Reset all keybindings to application defaults.

        This will:
        1. Clear all user customizations
        2. Restore default shortcuts from ActionRegistry
        3. Save to storage (if auto_save enabled)
        4. Update applied QActions

        Example:
            >>> manager.reset_to_defaults()  # Restore all defaults
        """
        # Delete stored customizations
        self._storage.reset()

        # Reload defaults
        self.load_bindings()

        # Update all applied QActions
        for action_id, qaction in self._applied_actions.items():
            shortcut = self._current_bindings.get(action_id)
            if shortcut:
                qaction.setShortcut(QKeySequence(shortcut))
            else:
                qaction.setShortcut(QKeySequence())

        logger.info("Reset all keybindings to defaults")

        # Auto-save if enabled
        if self._auto_save:
            self.save_bindings()
    ```

12. Implement `get_actions_by_category()` method:
    ```python
    def get_actions_by_category(self, category: str) -> List[ActionDefinition]:
        """Get all actions in a specific category.

        Args:
            category: Category name to filter by

        Returns:
            List of action definitions in the category

        Example:
            >>> file_actions = manager.get_actions_by_category("File")
            >>> for action in file_actions:
            ...     print(f"{action.description}: {manager.get_binding(action.id)}")
        """
        return self._registry.get_by_category(category)
    ```

13. Implement `get_categories()` method:
    ```python
    def get_categories(self) -> List[str]:
        """Get all action categories.

        Returns:
            Sorted list of unique category names

        Example:
            >>> categories = manager.get_categories()
            >>> print(", ".join(categories))
        """
        return self._registry.get_categories()
    ```

**Acceptance Criteria**:
- [ ] `KeybindingManager` class created with all methods
- [ ] `register_action()` adds action to registry and initializes binding
- [ ] `load_bindings()` merges defaults with user overrides
- [ ] `set_binding()` updates both internal state and applied QActions
- [ ] `apply_shortcuts()` creates QActions and adds to widget
- [ ] `reset_to_defaults()` clears customizations and reloads
- [ ] Auto-save works when enabled
- [ ] All methods have comprehensive docstrings with examples
- [ ] Type hints for all method signatures
- [ ] Logging for important operations

**Testing**:
```python
# Quick test in Python REPL (requires Qt application)
from PySide6.QtWidgets import QApplication, QMainWindow
import sys

app = QApplication(sys.argv)
window = QMainWindow()

from vfwidgets_keybinding.manager import KeybindingManager
from vfwidgets_keybinding.registry import ActionDefinition

# Create manager
manager = KeybindingManager()

# Register action
manager.register_action(ActionDefinition(
    id="file.save",
    description="Save File",
    default_shortcut="Ctrl+S",
    category="File"
))

# Apply shortcuts
actions = manager.apply_shortcuts(window)
assert "file.save" in actions

# Test binding changes
assert manager.get_binding("file.save") == "Ctrl+S"
manager.set_binding("file.save", "Ctrl+Alt+S")
assert manager.get_binding("file.save") == "Ctrl+Alt+S"

# Test reset
manager.reset_to_defaults()
assert manager.get_binding("file.save") == "Ctrl+S"

print("✅ KeybindingManager tests passed!")
```

---

#### Task 5: Create Package Exports

**Status**: ⬜ Not Started

**Prerequisites**: Tasks 1-4 complete

**Estimated Time**: 15 minutes

**Files to Modify**:
- `widgets/keybinding_manager/src/vfwidgets_keybinding/__init__.py`

**Implementation Steps**:

1. Update `__init__.py` with proper exports:
   ```python
   """VFWidgets KeybindingManager - Configurable keyboard shortcuts for Qt applications.

   A reusable widget library for managing customizable keyboard shortcuts in PySide6/PyQt6
   applications. Provides action registry, keybinding management, persistence, and UI.

   Quick Start:
       >>> from vfwidgets_keybinding import KeybindingManager, ActionDefinition
       >>>
       >>> manager = KeybindingManager("~/.config/myapp/keybindings.json")
       >>> manager.register_action(ActionDefinition(
       ...     id="file.save",
       ...     description="Save File",
       ...     default_shortcut="Ctrl+S",
       ...     category="File"
       ... ))
       >>> manager.apply_shortcuts(main_window)

   Version: 0.1.0 (Development)
   """

   __version__ = "0.1.0"

   from .manager import KeybindingManager
   from .registry import ActionDefinition, ActionRegistry
   from .storage import KeybindingStorage

   __all__ = [
       # Main API (most users only need this)
       "KeybindingManager",
       "ActionDefinition",

       # Advanced usage
       "ActionRegistry",
       "KeybindingStorage",

       # Version
       "__version__",
   ]
   ```

**Acceptance Criteria**:
- [ ] All core classes exported in `__all__`
- [ ] Module docstring with quick start example
- [ ] Version number updated
- [ ] Imports work correctly

**Testing**:
```python
# Quick test in Python REPL
from vfwidgets_keybinding import (
    KeybindingManager,
    ActionDefinition,
    ActionRegistry,
    KeybindingStorage,
    __version__
)

assert __version__ == "0.1.0"
print("✅ Package exports working!")
```

---

#### Task 6: Write Unit Tests

**Status**: ⬜ Not Started

**Prerequisites**: Tasks 1-5 complete

**Estimated Time**: 2 hours

**Files to Create**:
- `widgets/keybinding_manager/tests/unit/test_registry.py`
- `widgets/keybinding_manager/tests/unit/test_storage.py`
- `widgets/keybinding_manager/tests/unit/test_manager.py`
- `widgets/keybinding_manager/tests/conftest.py`

**Implementation Steps**:

1. Create `tests/conftest.py` with shared fixtures:
   ```python
   """Shared pytest fixtures for KeybindingManager tests."""

   import pytest
   import tempfile
   from pathlib import Path
   from PySide6.QtWidgets import QApplication

   @pytest.fixture(scope="session")
   def qapp():
       """Create Qt application for testing."""
       app = QApplication.instance()
       if app is None:
           app = QApplication([])
       yield app

   @pytest.fixture
   def temp_storage_file():
       """Create temporary file for storage tests."""
       with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
           file_path = Path(f.name)

       yield file_path

       # Cleanup
       if file_path.exists():
           file_path.unlink()
   ```

2. Create `tests/unit/test_registry.py`:
   ```python
   """Unit tests for ActionRegistry and ActionDefinition."""

   import pytest
   from vfwidgets_keybinding.registry import ActionDefinition, ActionRegistry


   class TestActionDefinition:
       """Test ActionDefinition dataclass."""

       def test_create_minimal_action(self):
           """Test creating action with minimal fields."""
           action = ActionDefinition(
               id="test.action",
               description="Test Action"
           )
           assert action.id == "test.action"
           assert action.description == "Test Action"
           assert action.default_shortcut is None
           assert action.category is None
           assert action.callback is None

       def test_create_full_action(self):
           """Test creating action with all fields."""
           callback = lambda: None
           action = ActionDefinition(
               id="file.save",
               description="Save File",
               default_shortcut="Ctrl+S",
               category="File",
               callback=callback
           )
           assert action.id == "file.save"
           assert action.description == "Save File"
           assert action.default_shortcut == "Ctrl+S"
           assert action.category == "File"
           assert action.callback is callback

       def test_empty_id_raises_error(self):
           """Test that empty ID raises ValueError."""
           with pytest.raises(ValueError, match="Action ID cannot be empty"):
               ActionDefinition(id="", description="Test")

       def test_empty_description_raises_error(self):
           """Test that empty description raises ValueError."""
           with pytest.raises(ValueError, match="Action description cannot be empty"):
               ActionDefinition(id="test.action", description="")

       def test_invalid_id_format_raises_error(self):
           """Test that non-dot-separated ID raises ValueError."""
           with pytest.raises(ValueError, match="must be dot-separated"):
               ActionDefinition(id="invalid", description="Test")

       def test_action_is_immutable(self):
           """Test that ActionDefinition is frozen."""
           action = ActionDefinition(id="test.action", description="Test")
           with pytest.raises(AttributeError):
               action.id = "new.id"


   class TestActionRegistry:
       """Test ActionRegistry class."""

       @pytest.fixture
       def registry(self):
           """Create fresh registry for each test."""
           return ActionRegistry()

       @pytest.fixture
       def sample_action(self):
           """Create sample action for tests."""
           return ActionDefinition(
               id="file.save",
               description="Save File",
               default_shortcut="Ctrl+S",
               category="File"
           )

       def test_register_action(self, registry, sample_action):
           """Test registering an action."""
           registry.register(sample_action)
           assert registry.get("file.save") == sample_action

       def test_register_duplicate_raises_error(self, registry, sample_action):
           """Test that registering duplicate ID raises ValueError."""
           registry.register(sample_action)

           duplicate = ActionDefinition(
               id="file.save",
               description="Different Description"
           )

           with pytest.raises(ValueError, match="already registered"):
               registry.register(duplicate)

       def test_unregister_action(self, registry, sample_action):
           """Test unregistering an action."""
           registry.register(sample_action)
           registry.unregister("file.save")
           assert registry.get("file.save") is None

       def test_unregister_nonexistent_raises_error(self, registry):
           """Test that unregistering missing action raises KeyError."""
           with pytest.raises(KeyError, match="not registered"):
               registry.unregister("nonexistent.action")

       def test_get_returns_none_for_missing(self, registry):
           """Test that get() returns None for missing actions."""
           assert registry.get("missing.action") is None

       def test_get_all(self, registry):
           """Test getting all actions."""
           action1 = ActionDefinition(id="file.save", description="Save")
           action2 = ActionDefinition(id="edit.copy", description="Copy")

           registry.register(action1)
           registry.register(action2)

           all_actions = registry.get_all()
           assert len(all_actions) == 2
           assert action1 in all_actions
           assert action2 in all_actions

       def test_get_by_category(self, registry):
           """Test filtering actions by category."""
           file_action = ActionDefinition(
               id="file.save",
               description="Save",
               category="File"
           )
           edit_action = ActionDefinition(
               id="edit.copy",
               description="Copy",
               category="Edit"
           )
           no_category = ActionDefinition(
               id="other.action",
               description="Other"
           )

           registry.register(file_action)
           registry.register(edit_action)
           registry.register(no_category)

           file_actions = registry.get_by_category("File")
           assert len(file_actions) == 1
           assert file_actions[0] == file_action

       def test_get_categories(self, registry):
           """Test getting unique categories."""
           registry.register(ActionDefinition(
               id="file.save",
               description="Save",
               category="File"
           ))
           registry.register(ActionDefinition(
               id="file.open",
               description="Open",
               category="File"
           ))
           registry.register(ActionDefinition(
               id="edit.copy",
               description="Copy",
               category="Edit"
           ))
           registry.register(ActionDefinition(
               id="other.action",
               description="Other"
           ))

           categories = registry.get_categories()
           assert categories == ["Edit", "File"]  # Sorted, excludes None

       def test_clear(self, registry, sample_action):
           """Test clearing all actions."""
           registry.register(sample_action)
           registry.clear()
           assert len(registry.get_all()) == 0
   ```

3. Create `tests/unit/test_storage.py`:
   ```python
   """Unit tests for KeybindingStorage."""

   import pytest
   import json
   from pathlib import Path
   from vfwidgets_keybinding.storage import KeybindingStorage


   class TestKeybindingStorage:
       """Test KeybindingStorage class."""

       def test_in_memory_storage(self):
           """Test storage without file path."""
           storage = KeybindingStorage(file_path=None)

           bindings = {"file.save": "Ctrl+S"}
           assert storage.save(bindings) is True

           loaded = storage.load()
           assert loaded == bindings

       def test_save_and_load(self, temp_storage_file):
           """Test saving and loading from file."""
           storage = KeybindingStorage(str(temp_storage_file))

           bindings = {"file.save": "Ctrl+S", "edit.copy": "Ctrl+C"}
           assert storage.save(bindings) is True

           loaded = storage.load()
           assert loaded == bindings

       def test_load_nonexistent_file(self, temp_storage_file):
           """Test loading from file that doesn't exist."""
           # Don't create the file
           temp_storage_file.unlink()

           storage = KeybindingStorage(str(temp_storage_file))
           loaded = storage.load()
           assert loaded == {}

       def test_load_invalid_json(self, temp_storage_file):
           """Test loading file with invalid JSON."""
           temp_storage_file.write_text("invalid json {")

           storage = KeybindingStorage(str(temp_storage_file))
           loaded = storage.load()
           assert loaded == {}  # Returns empty dict, doesn't crash

       def test_load_validates_format(self, temp_storage_file):
           """Test that load validates key/value types."""
           # Write file with invalid entries
           temp_storage_file.write_text(json.dumps({
               "valid.action": "Ctrl+S",
               123: "Invalid Key",  # Non-string key
               "invalid.value": 123  # Non-string value
           }))

           storage = KeybindingStorage(str(temp_storage_file))
           loaded = storage.load()

           # Only valid entry should be loaded
           assert loaded == {"valid.action": "Ctrl+S"}

       def test_save_creates_parent_directory(self, temp_storage_file):
           """Test that save creates parent directories."""
           nested_path = temp_storage_file.parent / "subdir" / "keys.json"
           storage = KeybindingStorage(str(nested_path))

           assert storage.save({"test": "Ctrl+T"}) is True
           assert nested_path.exists()

           # Cleanup
           nested_path.unlink()
           nested_path.parent.rmdir()

       def test_save_is_atomic(self, temp_storage_file):
           """Test that save uses atomic write."""
           storage = KeybindingStorage(str(temp_storage_file))
           storage.save({"initial": "Ctrl+I"})

           # Verify temp file doesn't exist after save
           temp_file = temp_storage_file.with_suffix('.tmp')
           assert not temp_file.exists()

       def test_merge_defaults_and_overrides(self):
           """Test merging default and override bindings."""
           storage = KeybindingStorage()

           defaults = {
               "file.save": "Ctrl+S",
               "file.open": "Ctrl+O",
               "edit.copy": "Ctrl+C"
           }

           overrides = {
               "file.save": "Ctrl+Alt+S",  # Override
               "custom.action": "Ctrl+X"   # New binding
           }

           merged = storage.merge(defaults, overrides)

           assert merged["file.save"] == "Ctrl+Alt+S"  # Overridden
           assert merged["file.open"] == "Ctrl+O"  # Default
           assert merged["edit.copy"] == "Ctrl+C"  # Default
           assert merged["custom.action"] == "Ctrl+X"  # New

       def test_merge_with_none_overrides(self):
           """Test merge when overrides is None."""
           storage = KeybindingStorage()

           defaults = {"file.save": "Ctrl+S"}
           merged = storage.merge(defaults, None)

           assert merged == defaults

       def test_reset_deletes_file(self, temp_storage_file):
           """Test that reset deletes storage file."""
           storage = KeybindingStorage(str(temp_storage_file))
           storage.save({"test": "Ctrl+T"})

           assert temp_storage_file.exists()
           assert storage.reset() is True
           assert not temp_storage_file.exists()

       def test_reset_in_memory(self):
           """Test reset with in-memory storage."""
           storage = KeybindingStorage()
           storage.save({"test": "Ctrl+T"})

           assert storage.reset() is True
           assert storage.load() == {}
   ```

4. Create `tests/unit/test_manager.py`:
   ```python
   """Unit tests for KeybindingManager."""

   import pytest
   from PySide6.QtWidgets import QMainWindow
   from vfwidgets_keybinding.manager import KeybindingManager
   from vfwidgets_keybinding.registry import ActionDefinition


   class TestKeybindingManager:
       """Test KeybindingManager class."""

       @pytest.fixture
       def manager(self):
           """Create manager with in-memory storage."""
           return KeybindingManager(storage_path=None, auto_save=False)

       @pytest.fixture
       def sample_actions(self):
           """Create sample actions for testing."""
           return [
               ActionDefinition(
                   id="file.save",
                   description="Save File",
                   default_shortcut="Ctrl+S",
                   category="File"
               ),
               ActionDefinition(
                   id="edit.copy",
                   description="Copy",
                   default_shortcut="Ctrl+C",
                   category="Edit"
               )
           ]

       def test_register_action(self, manager, sample_actions):
           """Test registering a single action."""
           manager.register_action(sample_actions[0])
           assert manager.get_binding("file.save") == "Ctrl+S"

       def test_register_actions_batch(self, manager, sample_actions):
           """Test registering multiple actions."""
           manager.register_actions(sample_actions)
           assert len(manager.get_all_bindings()) == 2

       def test_load_bindings(self, manager, sample_actions):
           """Test loading bindings merges defaults."""
           manager.register_actions(sample_actions)
           manager.load_bindings()

           assert manager.get_binding("file.save") == "Ctrl+S"
           assert manager.get_binding("edit.copy") == "Ctrl+C"

       def test_set_binding(self, manager, sample_actions):
           """Test changing a keybinding."""
           manager.register_action(sample_actions[0])

           assert manager.set_binding("file.save", "Ctrl+Alt+S") is True
           assert manager.get_binding("file.save") == "Ctrl+Alt+S"

       def test_set_binding_nonexistent_action(self, manager):
           """Test setting binding for unregistered action."""
           assert manager.set_binding("missing.action", "Ctrl+M") is False

       def test_set_binding_to_none(self, manager, sample_actions):
           """Test unbinding an action."""
           manager.register_action(sample_actions[0])

           assert manager.set_binding("file.save", None) is True
           assert manager.get_binding("file.save") is None

       def test_apply_shortcuts(self, qapp, manager, sample_actions):
           """Test applying shortcuts to widget."""
           window = QMainWindow()
           manager.register_actions(sample_actions)

           actions = manager.apply_shortcuts(window)

           assert len(actions) == 2
           assert "file.save" in actions
           assert actions["file.save"].shortcut().toString() == "Ctrl+S"

       def test_apply_shortcuts_specific_actions(self, qapp, manager, sample_actions):
           """Test applying only specific shortcuts."""
           window = QMainWindow()
           manager.register_actions(sample_actions)

           actions = manager.apply_shortcuts(window, action_ids=["file.save"])

           assert len(actions) == 1
           assert "file.save" in actions
           assert "edit.copy" not in actions

       def test_apply_shortcuts_with_callback(self, qapp, manager):
           """Test that callbacks are connected."""
           callback_called = []

           def test_callback():
               callback_called.append(True)

           action = ActionDefinition(
               id="test.action",
               description="Test",
               callback=test_callback
           )
           manager.register_action(action)

           window = QMainWindow()
           actions = manager.apply_shortcuts(window)

           # Trigger the action
           actions["test.action"].trigger()
           assert callback_called == [True]

       def test_reset_to_defaults(self, manager, sample_actions):
           """Test resetting keybindings to defaults."""
           manager.register_actions(sample_actions)
           manager.set_binding("file.save", "Ctrl+Alt+S")

           assert manager.get_binding("file.save") == "Ctrl+Alt+S"

           manager.reset_to_defaults()

           assert manager.get_binding("file.save") == "Ctrl+S"

       def test_get_actions_by_category(self, manager, sample_actions):
           """Test getting actions by category."""
           manager.register_actions(sample_actions)

           file_actions = manager.get_actions_by_category("File")
           assert len(file_actions) == 1
           assert file_actions[0].id == "file.save"

       def test_get_categories(self, manager, sample_actions):
           """Test getting all categories."""
           manager.register_actions(sample_actions)

           categories = manager.get_categories()
           assert categories == ["Edit", "File"]

       def test_auto_save(self, temp_storage_file, sample_actions):
           """Test auto-save functionality."""
           manager = KeybindingManager(
               storage_path=str(temp_storage_file),
               auto_save=True
           )
           manager.register_action(sample_actions[0])

           # Change binding (should auto-save)
           manager.set_binding("file.save", "Ctrl+Alt+S")

           # Create new manager and load
           manager2 = KeybindingManager(storage_path=str(temp_storage_file))
           manager2.register_action(sample_actions[0])
           manager2.load_bindings()

           assert manager2.get_binding("file.save") == "Ctrl+Alt+S"
   ```

5. Create `pyproject.toml` test configuration:
   ```toml
   [tool.pytest.ini_options]
   testpaths = ["tests"]
   python_files = "test_*.py"
   python_classes = "Test*"
   python_functions = "test_*"
   addopts = "-v --tb=short"

   [tool.coverage.run]
   source = ["src/vfwidgets_keybinding"]
   omit = ["*/tests/*"]

   [tool.coverage.report]
   precision = 2
   show_missing = true
   skip_covered = false
   ```

**Acceptance Criteria**:
- [ ] All test files created
- [ ] Test coverage > 80% for all core classes
- [ ] All tests pass: `pytest tests/unit/`
- [ ] Tests cover happy paths and error cases
- [ ] Fixtures properly clean up resources
- [ ] Tests are independent (can run in any order)

**Testing**:
```bash
# Run tests
cd widgets/keybinding_manager
pytest tests/unit/ -v

# Check coverage
pytest tests/unit/ --cov=src/vfwidgets_keybinding --cov-report=term-missing

# Expected output: > 80% coverage
```

---

### Developer Experience

#### Task 7: Add Type Hints (100% Public API)

**Status**: ⬜ Not Started

**Prerequisites**: Tasks 1-4 complete

**Estimated Time**: 1 hour

**Files to Modify**:
- `widgets/keybinding_manager/src/vfwidgets_keybinding/registry.py`
- `widgets/keybinding_manager/src/vfwidgets_keybinding/storage.py`
- `widgets/keybinding_manager/src/vfwidgets_keybinding/manager.py`

**Implementation Steps**:

1. Verify all public methods have type hints (already done in Tasks 1-4)

2. Create `pyproject.toml` mypy configuration:
   ```toml
   [tool.mypy]
   python_version = "3.11"
   strict = true
   warn_return_any = true
   warn_unused_configs = true
   disallow_untyped_defs = true
   disallow_any_generics = true
   check_untyped_defs = true
   no_implicit_optional = true
   warn_redundant_casts = true
   warn_unused_ignores = true
   warn_no_return = true

   [[tool.mypy.overrides]]
   module = "PySide6.*"
   ignore_missing_imports = true
   ```

3. Run type checking:
   ```bash
   cd widgets/keybinding_manager
   mypy --strict src/vfwidgets_keybinding
   ```

4. Fix any type errors found

**Acceptance Criteria**:
- [ ] All public methods have type hints
- [ ] `mypy --strict` passes with zero errors
- [ ] Return types specified for all methods
- [ ] Parameter types specified for all parameters
- [ ] Optional types used correctly

**Testing**:
```bash
cd widgets/keybinding_manager
mypy --strict src/vfwidgets_keybinding

# Expected: Success: no issues found in X source files
```

---

#### Task 8: Enhance Error Messages

**Status**: ⬜ Not Started

**Prerequisites**: Tasks 1-4 complete

**Estimated Time**: 1 hour

**Files to Modify**:
- All core implementation files

**Implementation Steps**:

1. Review all error messages for clarity and actionability

2. Update error messages to include:
   - What went wrong
   - Why it's a problem
   - How to fix it

3. Example improvements:
   ```python
   # Before
   raise ValueError("Invalid action ID")

   # After
   raise ValueError(
       f"Invalid action ID: '{action_id}'. "
       f"Action IDs must be dot-separated (e.g., 'file.save', 'edit.copy'). "
       f"Did you mean '{category}.{action_name}'?"
   )
   ```

4. Add helpful suggestions where possible:
   ```python
   # Check for common mistakes
   if action_id in self._actions:
       raise ValueError(
           f"Action '{action_id}' is already registered. "
           f"Use unregister() first if you want to replace it."
       )
   ```

**Acceptance Criteria**:
- [ ] All error messages are clear and actionable
- [ ] Error messages suggest fixes where possible
- [ ] Error messages include context (what value caused the error)
- [ ] No generic error messages like "Invalid input"

**Testing**:
Manually trigger errors and verify messages are helpful:
```python
from vfwidgets_keybinding import KeybindingManager, ActionDefinition

manager = KeybindingManager()

# Test error messages
try:
    ActionDefinition(id="invalid", description="Test")
except ValueError as e:
    print(e)  # Should suggest using dot-separated format

try:
    manager.set_binding("missing.action", "Ctrl+M")
except Exception as e:
    print(e)  # Should explain action doesn't exist
```

---

#### Task 9: Write Comprehensive Docstrings

**Status**: ⬜ Not Started

**Prerequisites**: Tasks 1-4 complete

**Estimated Time**: 1 hour

**Files to Modify**:
- All core implementation files

**Implementation Steps**:

1. Verify all docstrings are complete (already done in Tasks 1-4)

2. Ensure docstrings follow Google style:
   ```python
   def method_name(self, param1: str, param2: int = 0) -> bool:
       """Short one-line description.

       Longer description with more details about what the method does,
       when to use it, and any important caveats.

       Args:
           param1: Description of param1
           param2: Description of param2 (default: 0)

       Returns:
           Description of return value

       Raises:
           ValueError: When something goes wrong

       Example:
           >>> result = obj.method_name("test", 42)
           >>> print(result)
           True
       """
   ```

3. Add examples to every public method

4. Document edge cases and gotchas

**Acceptance Criteria**:
- [ ] All public classes have docstrings
- [ ] All public methods have docstrings
- [ ] All docstrings include examples
- [ ] Args, Returns, and Raises sections complete
- [ ] Examples are runnable and tested

---

#### Task 10: Create Minimal Usage Example

**Status**: ⬜ Not Started

**Prerequisites**: Tasks 1-9 complete

**Estimated Time**: 30 minutes

**Files to Create**:
- `widgets/keybinding_manager/examples/01_minimal_usage.py`

**Implementation Steps**:

1. Create minimal example (< 20 lines):
   ```python
   """Minimal KeybindingManager example.

   This example shows the absolute minimum code needed to use
   the KeybindingManager. You can run this in under 5 minutes.
   """

   import sys
   from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit
   from vfwidgets_keybinding import KeybindingManager, ActionDefinition


   def main():
       app = QApplication(sys.argv)
       window = QMainWindow()
       window.setWindowTitle("Minimal KeybindingManager Example")
       window.resize(800, 600)

       # Create text editor
       editor = QTextEdit()
       window.setCentralWidget(editor)

       # Create keybinding manager
       manager = KeybindingManager()

       # Register actions
       manager.register_action(ActionDefinition(
           id="file.quit",
           description="Quit Application",
           default_shortcut="Ctrl+Q",
           callback=app.quit
       ))

       # Apply shortcuts to window
       manager.apply_shortcuts(window)

       window.show()
       sys.exit(app.exec())


   if __name__ == "__main__":
       main()
   ```

**Acceptance Criteria**:
- [ ] Example is < 20 lines (excluding imports/comments)
- [ ] Example runs without errors
- [ ] Example demonstrates core workflow
- [ ] Example includes helpful comments
- [ ] Example can be run in < 5 minutes

**Testing**:
```bash
cd widgets/keybinding_manager
python examples/01_minimal_usage.py

# Press Ctrl+Q to verify shortcut works
```

---

#### Task 11: Create Full Application Example

**Status**: ⬜ Not Started

**Prerequisites**: Task 10 complete

**Estimated Time**: 1 hour

**Files to Create**:
- `widgets/keybinding_manager/examples/02_full_application.py`

**Implementation Steps**:

1. Create comprehensive example showing:
   - Multiple action categories
   - Persistent storage
   - Custom callbacks
   - Querying bindings
   - Resetting to defaults

2. Example structure (see implementation-roadmap-PLAN.md for details):
   ```python
   """Full KeybindingManager application example.

   Demonstrates:
   - Action registration with categories
   - Persistent storage
   - Custom callbacks
   - Querying keybindings
   - Resetting to defaults
   """

   # [Implementation here - see roadmap document]
   ```

**Acceptance Criteria**:
- [ ] Example demonstrates all major features
- [ ] Example includes multiple categories
- [ ] Example shows persistent storage
- [ ] Example includes helpful comments
- [ ] Example runs without errors

**Testing**:
```bash
python examples/02_full_application.py

# Test all shortcuts work
# Verify persistence across restarts
```

---

#### Task 12: Write Getting Started Guide

**Status**: ⬜ Not Started

**Prerequisites**: Tasks 10-11 complete

**Estimated Time**: 1 hour

**Files to Create**:
- `widgets/keybinding_manager/docs/getting-started-GUIDE.md`

**Implementation Steps**:

1. Create getting started guide covering:
   - Installation
   - 5-minute quick start
   - Core concepts
   - Common use cases
   - Next steps

2. Follow this outline:
   ```markdown
   # Getting Started with KeybindingManager

   ## Installation
   ## Quick Start (5 minutes)
   ## Core Concepts
   ## Common Use Cases
   ## Next Steps
   ```

3. Include copy-paste-ready code snippets

4. Link to other documentation

**Acceptance Criteria**:
- [ ] Guide enables complete novice to get started in 5 minutes
- [ ] All code examples are tested and work
- [ ] Guide links to API reference
- [ ] Guide includes troubleshooting section
- [ ] Guide follows VFWidgets documentation style

---

#### Task 13: Write API Reference

**Status**: ⬜ Not Started

**Prerequisites**: Tasks 1-9 complete

**Estimated Time**: 2 hours

**Files to Create**:
- `widgets/keybinding_manager/docs/api-reference-GUIDE.md`

**Implementation Steps**:

1. Document every public class and method

2. Follow this structure for each class:
   ```markdown
   ## ClassName

   Brief description.

   ### Constructor

   #### `__init__(param1, param2)`

   Description, parameters, example.

   ### Methods

   #### `method_name(param)`

   Description, parameters, returns, raises, example.
   ```

3. Include examples for every method

4. Cross-reference related methods

**Acceptance Criteria**:
- [ ] Every public class documented
- [ ] Every public method documented
- [ ] All examples tested
- [ ] Cross-references added
- [ ] Searchable structure

---

#### Task 14: Update Main README

**Status**: ⬜ Not Started

**Prerequisites**: Tasks 12-13 complete

**Estimated Time**: 30 minutes

**Files to Create/Modify**:
- `widgets/keybinding_manager/README.md`

**Implementation Steps**:

1. Create comprehensive README:
   ```markdown
   # VFWidgets KeybindingManager

   Configurable keyboard shortcuts for PySide6/PyQt6 applications.

   ## Features
   ## Installation
   ## Quick Start
   ## Documentation
   ## Examples
   ## License
   ```

2. Link to documentation files

3. Add badges (version, build status, etc.)

**Acceptance Criteria**:
- [ ] README provides clear overview
- [ ] Links to getting started guide
- [ ] Links to API reference
- [ ] Lists key features
- [ ] Includes quick start example

---

#### Task 15: Start CHANGELOG

**Status**: ⬜ Not Started

**Prerequisites**: None

**Estimated Time**: 15 minutes

**Files to Create**:
- `widgets/keybinding_manager/CHANGELOG.md`

**Implementation Steps**:

1. Create CHANGELOG following Keep a Changelog format:
   ```markdown
   # Changelog

   All notable changes to this project will be documented in this file.

   The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
   and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

   ## [Unreleased]

   ### Added
   - ActionRegistry for managing application actions
   - KeybindingStorage for persistent keybinding storage
   - KeybindingManager for orchestrating keybindings
   - Unit tests with 80%+ coverage
   - Comprehensive documentation
   - Minimal and full application examples

   ## [0.1.0] - 2025-10-03

   ### Added
   - Initial Phase 1 implementation
   ```

**Acceptance Criteria**:
- [ ] CHANGELOG created
- [ ] Follows Keep a Changelog format
- [ ] Documents all Phase 1 features
- [ ] Ready for future updates

---

### Phase 1 Completion Checklist

Before moving to Phase 2, verify:

- [ ] **All Core Implementation Tasks Complete** (Tasks 1-6)
  - [ ] ActionDefinition dataclass
  - [ ] ActionRegistry class
  - [ ] KeybindingStorage class
  - [ ] KeybindingManager class
  - [ ] Package exports
  - [ ] Unit tests (80%+ coverage)

- [ ] **All Developer Experience Tasks Complete** (Tasks 7-15)
  - [ ] Type hints (mypy --strict passes)
  - [ ] Error messages enhanced
  - [ ] Docstrings comprehensive
  - [ ] Minimal example works
  - [ ] Full application example works
  - [ ] Getting started guide complete
  - [ ] API reference complete
  - [ ] README updated
  - [ ] CHANGELOG started

- [ ] **Quality Gates Passed**
  - [ ] All unit tests passing: `pytest tests/unit/`
  - [ ] Type checking clean: `mypy --strict src/`
  - [ ] Examples run without errors
  - [ ] Documentation reviewed for clarity

- [ ] **Integration Tested**
  - [ ] Integrated with ViloxTerm successfully
  - [ ] No known critical bugs

**When all boxes checked**: Phase 1 is complete! Create git tag `v0.1.0` and proceed to Phase 2.

---

## Phase 2: UI + Polish

**Status**: Not Started (Phase 1 must complete first)

**Goal**: User-facing customization dialog and comprehensive documentation

**Tasks**: See implementation-roadmap-PLAN.md for Phase 2 details

**Will include**:
- KeySequenceEdit widget
- BindingListWidget
- KeybindingDialog
- Theme integration
- Additional documentation guides

---

## Phase 3: Advanced Features

**Status**: Not Started (Phase 2 must complete first)

**Goal**: Polish, performance, and advanced use cases

**Tasks**: See implementation-roadmap-PLAN.md for Phase 3 details

**Will include**:
- Context-aware bindings
- Import/export profiles
- Debug helpers
- Performance benchmarks

---

## References

### Related Documents

- **Architecture Design**: `architecture-DESIGN.md`
- **Developer Experience Plan**: `developer-experience-PLAN.md`
- **Implementation Roadmap**: `implementation-roadmap-PLAN.md`

### Useful Links

- PySide6 QKeySequence: https://doc.qt.io/qtforpython-6/PySide6/QtGui/QKeySequence.html
- PySide6 QAction: https://doc.qt.io/qtforpython-6/PySide6/QtGui/QAction.html
- pytest-qt: https://pytest-qt.readthedocs.io/

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2025-10-03 | Initial task breakdown for Phase 1 |
