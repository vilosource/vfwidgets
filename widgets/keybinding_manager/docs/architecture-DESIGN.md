# KeybindingManager Architecture Design

**Document Type**: DESIGN
**Status**: Draft
**Created**: 2025-10-03
**Purpose**: Define the architecture for a reusable keyboard shortcut management system for Qt applications

---

## Table of Contents

1. [Overview](#overview)
2. [Goals and Non-Goals](#goals-and-non-goals)
3. [Architecture](#architecture)
4. [Core Components](#core-components)
5. [Data Flow](#data-flow)
6. [Storage Format](#storage-format)
7. [Integration Patterns](#integration-patterns)
8. [Design Decisions](#design-decisions)
9. [Implementation Phases](#implementation-phases)

---

## Overview

KeybindingManager is a reusable widget library for PySide6/PyQt6 that provides:
- **Centralized action management** via command pattern
- **User-customizable keyboard shortcuts**
- **Persistent storage** of user preferences
- **Conflict detection** and resolution
- **UI for customization** (dialog widget)

### Problem Statement

Qt applications typically hardcode keyboard shortcuts:
```python
# ❌ Hardcoded - not user-customizable
action = QAction("Split Vertical", self)
action.setShortcut("Ctrl+Shift+V")
action.triggered.connect(self.split_vertical)
```

This approach has limitations:
- Users can't customize shortcuts
- No conflict detection
- Settings not persisted
- Each app reimplements customization

### Solution

Provide a reusable system that separates:
1. **Actions** (what can be done) - defined by app
2. **Keybindings** (how to trigger) - configurable by user
3. **Storage** (persistence) - automatic
4. **UI** (customization) - provided

---

## Goals and Non-Goals

### Goals

✅ **Reusable** - Works with any PySide6/PyQt6 application
✅ **Simple Integration** - Minimal changes to existing code
✅ **User-Friendly** - Clear UI for customization
✅ **Persistent** - Save/load user preferences automatically
✅ **Conflict-Aware** - Detect and warn about duplicate shortcuts
✅ **Well-Documented** - Clear examples and API reference
✅ **Theme-Compatible** - Works with VFWidgets theme system

### Non-Goals

❌ **Cross-Platform Shortcuts** - Platform-specific shortcuts not handled automatically
❌ **Macro System** - No macro recording/playback
❌ **Modal Keybindings** - No vim-style modal editing (future enhancement)
❌ **Global System Shortcuts** - Only app-level, not OS-level

---

## Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Code                          │
│                                                               │
│  ┌────────────────┐         ┌──────────────────┐            │
│  │ Register       │────────>│ ActionRegistry   │            │
│  │ Actions        │         │                  │            │
│  └────────────────┘         └──────────────────┘            │
│                                     ▲                         │
│                                     │                         │
│  ┌────────────────┐         ┌──────────────────┐            │
│  │ Show Dialog    │────────>│ KeybindingDialog │            │
│  │                │         │                  │            │
│  └────────────────┘         └──────────────────┘            │
└─────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  KeybindingManager Layer                      │
│                                                               │
│  ┌──────────────────────────────────────────────────┐       │
│  │             KeybindingManager                     │       │
│  │  ┌─────────────────┐  ┌────────────────────┐    │       │
│  │  │ Binding Map     │  │ QAction Cache      │    │       │
│  │  │ (key->action_id)│  │ (cached instances) │    │       │
│  │  └─────────────────┘  └────────────────────┘    │       │
│  │                                                   │       │
│  │  ┌─────────────────┐  ┌────────────────────┐    │       │
│  │  │ Conflict Detect │  │ Apply to Window    │    │       │
│  │  └─────────────────┘  └────────────────────┘    │       │
│  └──────────────────────────────────────────────────┘       │
│                           ▲                                   │
│                           │                                   │
│  ┌────────────────────────────────────────────┐             │
│  │          KeybindingStorage                 │             │
│  │  ┌──────────────┐    ┌──────────────┐     │             │
│  │  │ Load/Save    │    │ JSON Format  │     │             │
│  │  │ Settings     │    │ ~/.config/   │     │             │
│  │  └──────────────┘    └──────────────┘     │             │
│  └────────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────┘
```

### Component Relationships

```
ActionRegistry ←──── KeybindingManager ───→ QWindow
      ▲                     ▲
      │                     │
      │              KeybindingStorage
      │                     ▲
      │                     │
      └──── KeybindingDialog
```

---

## Core Components

### 1. ActionRegistry

**Purpose**: Central registry of all application actions (command pattern)

**Responsibilities**:
- Store action definitions (ID, name, handler, category, defaults)
- Provide lookup by action ID
- Execute actions by ID
- Enumerate all actions (for UI)

**API**:
```python
class ActionRegistry:
    def register(
        self,
        action_id: str,
        name: str,
        handler: Callable,
        default_shortcut: Optional[str] = None,
        category: str = "General",
        description: str = ""
    ) -> None:
        """Register an action."""

    def execute(self, action_id: str) -> bool:
        """Execute action by ID. Returns success."""

    def get_action(self, action_id: str) -> Optional[ActionDefinition]:
        """Get action definition."""

    def get_all_actions(self) -> List[ActionDefinition]:
        """Get all registered actions."""

    def get_categories(self) -> List[str]:
        """Get all categories."""
```

**Data Structure**:
```python
@dataclass
class ActionDefinition:
    action_id: str
    name: str
    handler: Callable
    default_shortcut: Optional[str]
    category: str
    description: str
    enabled: bool = True
```

### 2. KeybindingManager

**Purpose**: Manage keyboard shortcut mappings and QAction instances

**Responsibilities**:
- Map key sequences to action IDs
- Create and manage QAction instances
- Apply shortcuts to Qt windows
- Detect conflicts
- Coordinate with storage layer

**API**:
```python
class KeybindingManager:
    def __init__(
        self,
        registry: ActionRegistry,
        storage: Optional[KeybindingStorage] = None
    ):
        """Initialize with action registry."""

    def bind(self, action_id: str, key_sequence: str) -> bool:
        """Bind key sequence to action. Returns True if successful."""

    def unbind(self, action_id: str) -> None:
        """Remove keybinding for action."""

    def get_binding(self, action_id: str) -> Optional[str]:
        """Get current keybinding for action."""

    def apply_to_window(self, window: QWidget) -> None:
        """Apply all keybindings to window (creates QActions)."""

    def detect_conflicts(self, key_sequence: str) -> List[str]:
        """Returns list of action_ids that use this key."""

    def reset_to_defaults(self) -> None:
        """Reset all keybindings to defaults."""

    def save(self) -> None:
        """Save current bindings to storage."""

    def load(self) -> None:
        """Load bindings from storage."""
```

### 3. KeybindingStorage

**Purpose**: Persist keybinding preferences to disk

**Responsibilities**:
- Serialize/deserialize keybinding mappings
- Handle file I/O
- Merge user settings with defaults
- Provide settings file location

**API**:
```python
class KeybindingStorage:
    def __init__(self, settings_path: Optional[Path] = None):
        """Initialize storage with path (default: ~/.config/app/keybindings.json)."""

    def save(self, bindings: Dict[str, str]) -> None:
        """Save bindings to file."""

    def load(self) -> Dict[str, str]:
        """Load bindings from file. Returns empty dict if not found."""

    def exists(self) -> bool:
        """Check if settings file exists."""

    def reset(self) -> None:
        """Delete settings file."""
```

### 4. KeybindingDialog (Phase 2)

**Purpose**: UI for viewing and editing keybindings

**Responsibilities**:
- Display all actions with current shortcuts
- Capture new key sequences
- Show conflicts
- Reset to defaults
- Search/filter actions

**API**:
```python
class KeybindingDialog(QDialog):
    def __init__(
        self,
        manager: KeybindingManager,
        parent: Optional[QWidget] = None
    ):
        """Initialize dialog with keybinding manager."""

    # Standard QDialog exec() to show
```

---

## Data Flow

### Registration Flow

```
Application Code
    │
    ├─> registry.register("split_vertical", "Split Vertical", handler, "Ctrl+Shift+V")
    │
    └─> ActionRegistry stores action definition
```

### Initialization Flow

```
Application __init__
    │
    ├─> Create ActionRegistry
    ├─> Register all actions
    ├─> Create KeybindingManager(registry)
    │   └─> KeybindingManager.load() ──> KeybindingStorage.load()
    │       └─> Reads ~/.config/app/keybindings.json
    │       └─> Merges with defaults from ActionRegistry
    │
    └─> manager.apply_to_window(self)
        └─> Creates QAction for each binding
        └─> Adds QAction to window with self.addAction()
```

### User Customization Flow

```
User clicks "Preferences" → "Keyboard Shortcuts"
    │
    ├─> KeybindingDialog(manager).exec()
    │   └─> Shows table of actions + shortcuts
    │
    ├─> User clicks "Edit" on action
    │   └─> KeySequenceEdit captures key press
    │   └─> manager.bind(action_id, new_sequence)
    │       └─> Checks for conflicts
    │       └─> Updates internal binding map
    │
    └─> User clicks "Save"
        └─> manager.save()
            └─> storage.save(bindings)
                └─> Writes JSON to file
```

### Shortcut Execution Flow

```
User presses Ctrl+Shift+V
    │
    └─> Qt delivers to QAction (created by manager.apply_to_window())
        └─> QAction.triggered signal
            └─> Connected to ActionRegistry.execute(action_id)
                └─> Calls registered handler
```

---

## Storage Format

### JSON Structure

File location: `~/.config/{app_name}/keybindings.json`

```json
{
  "version": "1.0",
  "keybindings": {
    "split_vertical": "Ctrl+Shift+V",
    "split_horizontal": "Ctrl+Shift+H",
    "close_pane": "Ctrl+W",
    "close_tab": "Ctrl+Shift+W",
    "change_theme": null
  },
  "metadata": {
    "last_modified": "2025-10-03T12:34:56Z",
    "app_version": "1.0.0"
  }
}
```

### Design Rationale

- **Simple JSON** - Human-readable, easy to edit manually
- **action_id → key_sequence** - Direct mapping
- **null values** - Explicitly disabled shortcuts
- **Versioning** - Future schema changes
- **Metadata** - Debugging and migration

---

## Integration Patterns

### Pattern 1: Basic Usage (Recommended)

```python
from vfwidgets_keybinding import ActionRegistry, KeybindingManager

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # 1. Create registry
        self.registry = ActionRegistry()

        # 2. Register actions
        self.registry.register(
            action_id="split_vertical",
            name="Split Vertical",
            handler=self.on_split_vertical,
            default_shortcut="Ctrl+Shift+V",
            category="Panes"
        )

        # 3. Create manager (auto-loads settings)
        self.keybinding_manager = KeybindingManager(
            self.registry,
            settings_path=Path.home() / ".myapp" / "keybindings.json"
        )

        # 4. Apply to window
        self.keybinding_manager.apply_to_window(self)

    def on_split_vertical(self):
        print("Split vertical action!")
```

### Pattern 2: With Customization Dialog

```python
from vfwidgets_keybinding import KeybindingDialog

class MyApp(QMainWindow):
    def show_keybinding_preferences(self):
        dialog = KeybindingDialog(self.keybinding_manager, self)
        if dialog.exec():
            # User clicked OK
            self.keybinding_manager.save()
```

### Pattern 3: Migrating Existing QActions

```python
# Before
split_action = QAction("Split Vertical", self)
split_action.setShortcut("Ctrl+Shift+V")
split_action.triggered.connect(self.split_vertical)
self.addAction(split_action)

# After
self.registry.register(
    "split_vertical",
    "Split Vertical",
    self.split_vertical,
    "Ctrl+Shift+V"
)
# Manager handles QAction creation
```

---

## Design Decisions

### D1: Command Pattern vs Direct QAction References

**Decision**: Use command pattern with action IDs

**Rationale**:
- ✅ Decouples actions from shortcuts
- ✅ Enables runtime rebinding
- ✅ Simplifies persistence (store IDs not objects)
- ✅ Better for UI (list all actions by ID)

**Trade-off**: Extra indirection layer

---

### D2: JSON vs INI/YAML for Storage

**Decision**: JSON format

**Rationale**:
- ✅ Native Python support (no dependencies)
- ✅ Human-readable and editable
- ✅ Easy versioning/migration
- ✅ Standard for application settings
- ❌ Slightly more verbose than INI

---

### D3: QAction Creation - Eager vs Lazy

**Decision**: Eager creation in `apply_to_window()`

**Rationale**:
- ✅ Simpler implementation
- ✅ All shortcuts available immediately
- ✅ No runtime overhead on first use
- ❌ Slight startup cost (negligible for <100 actions)

---

### D4: Conflict Resolution Strategy

**Decision**: Warn but allow duplicates, last-wins behavior

**Rationale**:
- ✅ User has final control
- ✅ No blocking dialogs during setup
- ✅ Visual warning in customization UI
- ⚠️ May surprise users if duplicate shortcuts exist

Future: Add "strict mode" option to prevent conflicts

---

### D5: Storage Location

**Decision**: Platform-specific config directory

```python
# Linux: ~/.config/{app_name}/keybindings.json
# macOS: ~/Library/Application Support/{app_name}/keybindings.json
# Windows: %APPDATA%/{app_name}/keybindings.json
```

**Rationale**:
- ✅ Follows platform conventions
- ✅ Use Python's `platformdirs` library
- ✅ Respects user preferences

---

## Implementation Phases

### Phase 1: Core System (MVP)

**Goal**: Working action registry and keybinding management without UI

**Components**:
- `ActionRegistry` class
- `ActionDefinition` dataclass
- `KeybindingManager` class
- `KeybindingStorage` class
- Basic unit tests

**Deliverable**: Can register actions, bind shortcuts programmatically, persist to JSON

**Time Estimate**: 4-6 hours

---

### Phase 2: UI Components

**Goal**: User-facing dialog for customization

**Components**:
- `KeybindingDialog` widget
- `KeySequenceEdit` widget (captures keys)
- `BindingListWidget` (displays actions)
- Search/filter functionality
- Theme integration

**Deliverable**: Full UI for viewing/editing shortcuts

**Time Estimate**: 6-8 hours

---

### Phase 3: Advanced Features

**Goal**: Polish and advanced use cases

**Features**:
- Context-aware bindings (different shortcuts in different modes)
- Import/export profiles
- Keyboard shortcut cheat sheet generator
- Conflict resolution UI improvements
- Action grouping/hierarchy

**Deliverable**: Production-ready keybinding system

**Time Estimate**: 8-12 hours

---

## API Examples

### Example 1: Simple Application

```python
from PySide6.QtWidgets import QApplication, QMainWindow
from vfwidgets_keybinding import ActionRegistry, KeybindingManager

app = QApplication([])

# Create main window
window = QMainWindow()

# Setup actions
registry = ActionRegistry()
registry.register("quit", "Quit", app.quit, "Ctrl+Q", "Application")

# Setup keybindings
manager = KeybindingManager(registry)
manager.apply_to_window(window)

window.show()
app.exec()
```

### Example 2: Multi-Category Application

```python
registry = ActionRegistry()

# File actions
registry.register("file_new", "New", self.new_file, "Ctrl+N", "File")
registry.register("file_open", "Open", self.open_file, "Ctrl+O", "File")
registry.register("file_save", "Save", self.save_file, "Ctrl+S", "File")

# Edit actions
registry.register("edit_cut", "Cut", self.cut, "Ctrl+X", "Edit")
registry.register("edit_copy", "Copy", self.copy, "Ctrl+C", "Edit")
registry.register("edit_paste", "Paste", self.paste, "Ctrl+V", "Edit")

# View actions
registry.register("view_zoom_in", "Zoom In", self.zoom_in, "Ctrl++", "View")
registry.register("view_zoom_out", "Zoom Out", self.zoom_out, "Ctrl+-", "View")
```

---

## Future Considerations

### Multi-Stroke Shortcuts

Like Emacs: `Ctrl+X Ctrl+S` for save

**Challenge**: Qt's `QKeySequence` supports up to 4 keys in sequence
**Solution**: Extend with custom input handling layer

### Modal Keybindings

Like Vim: different shortcuts in Normal vs Insert mode

**Challenge**: Requires mode tracking and context switching
**Solution**: Add `context` parameter to action registration

### Chord Shortcuts

Like VS Code: `Ctrl+K, Ctrl+S` to show shortcuts

**Challenge**: Timing and state management
**Solution**: Phase 3 enhancement

---

## References

- Qt QAction documentation: https://doc.qt.io/qt-6/qaction.html
- Qt QKeySequence: https://doc.qt.io/qt-6/qkeysequence.html
- Command Pattern: https://refactoring.guru/design-patterns/command
- VS Code Keybindings: https://code.visualstudio.com/docs/getstarted/keybindings

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2025-10-03 | Initial architecture design |

