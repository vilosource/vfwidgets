# MultiSplit Widget Introduction

## Overview

MultiSplit is a **pure layout container widget** for PySide6/PyQt applications that enables sophisticated split-pane interfaces. It manages the spatial arrangement of widgets in a recursive tree structure without ever creating or managing the widgets themselves.

Think of MultiSplit as a choreographer that directs the dance of your widgets - it knows where each widget should be positioned, how much space they should occupy, and how they should move during layout changes, but it never creates the dancers themselves.

## What MultiSplit Is

### Core Capabilities

- **Recursive Split-Pane Layout**: Create infinite levels of horizontal and vertical splits
- **Tree-Based Structure**: Clean hierarchical organization that maps naturally to JSON
- **Widget-Agnostic**: Works with any QWidget - editors, terminals, plots, browsers, etc.
- **Full Undo/Redo**: Every layout operation is reversible via command pattern
- **Persistence**: Save and restore complete layout configurations
- **Focus Management**: Keyboard navigation and spatial focus movement
- **Reconciliation-Based**: Updates preserve widget instances and state

### Example Use Cases

```python
# IDE-style interface
├── File Tree (Left)
└── Split Vertical
    ├── Code Editor (Top Right)
    └── Split Horizontal
        ├── Terminal (Bottom Left)
        └── Debug Output (Bottom Right)

# Data analysis dashboard
├── Control Panel (Left)
└── Split Vertical
    ├── Plot Grid (Top)
    └── Data Table (Bottom)

# Terminal multiplexer
├── Shell 1 (Top Left)
├── Shell 2 (Top Right)
├── Shell 3 (Bottom Left)
└── Log Viewer (Bottom Right)
```

## What MultiSplit Is NOT

### Not a Widget Factory
```python
# ❌ MultiSplit does NOT do this
editor = multisplit.create_editor("main.py")
terminal = multisplit.create_terminal()

# ✅ Application provides widgets via provider pattern
def provide_widget(widget_id: str, pane_id: str) -> QWidget:
    if widget_id.startswith("editor:"):
        return CodeEditor(widget_id[7:])
    return Terminal()
```

### Not a Docking System
- **No floating windows** - Everything stays in the main tree
- **No tabs** - Each pane contains exactly one widget
- **No window management** - Pure layout container only

### Not a State Manager
- **Doesn't save widget state** - Application handles widget persistence
- **Doesn't manage widget data** - Only manages spatial arrangement
- **Doesn't control widget behavior** - Pure layout orchestration

### Not an MDI System
- **No overlapping windows** - Everything tiles cleanly
- **No manual positioning** - Tree structure determines layout
- **No window decorations** - Seamless widget integration

## Value Proposition

### For Application Developers

**Clean Separation of Concerns**
```python
# MultiSplit handles: WHERE widgets go
layout = {
    "type": "split",
    "orientation": "horizontal",
    "children": [...]
}

# Application handles: WHAT widgets are
def provide_widget(widget_id: str, pane_id: str) -> QWidget:
    return create_widget_for_id(widget_id)
```

**Predictable Behavior**
- Every operation is undoable
- Layout state is always serializable
- Widget reuse prevents flicker and state loss
- Clear widget lifecycle with explicit notifications

**Minimal Integration Effort**
```python
# Minimal setup required
self.splitter = MultiSplitWidget()
self.splitter.set_widget_provider(self)
self.setCentralWidget(self.splitter)

# Rich functionality available immediately
self.splitter.split_with_widget(pane_id, WherePosition.RIGHT, widget, "editor:file.py")
```

### For End Users

**Intuitive Layout Control**
- Familiar split-pane interaction model
- Keyboard navigation and spatial movement
- Resizable dividers with proportional scaling
- No complex window management

**Persistent Workspaces**
- Save and restore complete workspace layouts
- Consistent behavior across application sessions
- No lost windows or misplaced panels

## Comparison with Alternatives

### vs QSplitter
| Feature | MultiSplit | QSplitter |
|---------|------------|-----------|
| Nesting Depth | Infinite | Single level |
| Persistence | Built-in JSON | Manual state |
| Undo/Redo | Full support | None |
| Widget Lifecycle | Provider pattern | Manual creation |
| Focus Management | Spatial navigation | Basic |

### vs QDockWidget
| Feature | MultiSplit | QDockWidget |
|---------|------------|-------------|
| Layout Predictability | Tree structure | Complex state machine |
| Floating Windows | No (by design) | Yes |
| Tabbed Groups | No (pure splits) | Yes |
| Configuration Complexity | Minimal | High |
| State Management | Clean separation | Coupled |

### vs QMdiArea
| Feature | MultiSplit | QMdiArea |
|---------|------------|----------|
| Space Efficiency | 100% tiled | Overlapping windows |
| Navigation | Keyboard-friendly | Mouse-driven |
| Layout Control | Programmatic | Manual |
| Memory Usage | Efficient | Higher overhead |

## Architecture Overview

### MVC Pattern
```
Model (core/)
├── Pure Python tree structure
├── No Qt dependencies
└── Serializable state

Controller (controller/)
├── Command-based mutations
├── Undo/redo management
└── Transaction boundaries

View (view/)
├── Qt widget reconciliation
├── Event handling
└── Rendering coordination
```

### Widget Provider Pattern
```python
# MultiSplit requests widgets
widget_needed.emit(widget_id="editor:main.py", pane_id="pane-001")

# Application provides widgets
def provide_widget(widget_id: str, pane_id: str) -> QWidget:
    return CodeEditor("main.py")

# Clean lifecycle management
widget_closing.emit(widget_id="editor:main.py", widget=editor_instance)
```

### Tree Structure
```
Root Split (Horizontal)
├── Leaf: File Tree ("explorer")
└── Split (Vertical)
    ├── Leaf: Editor ("editor:main.py")
    └── Split (Horizontal)
        ├── Leaf: Terminal ("terminal:1")
        └── Leaf: Output ("output:build")
```

## Getting Started

### Basic Setup
```python
from vfwidgets_multisplit import MultiSplitWidget, WherePosition

class MyApplication(QMainWindow):
    def __init__(self):
        # Create layout manager
        self.splitter = MultiSplitWidget()
        self.splitter.set_widget_provider(self)
        self.setCentralWidget(self.splitter)

        # Add initial widget
        initial_widget = self.create_editor("untitled.txt")
        self.splitter.set_root_widget(initial_widget, "editor:untitled.txt")

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Called when layout restoration needs widgets"""
        if widget_id.startswith("editor:"):
            return self.create_editor(widget_id[7:])
        return QLabel(f"Unknown: {widget_id}")

    def widget_closing(self, widget_id: str, widget: QWidget):
        """Called before widget removal"""
        if hasattr(widget, 'save_state'):
            self.save_widget_state(widget_id, widget.save_state())
```

### Adding Splits
```python
# Split current pane horizontally
current_pane = self.splitter.current_pane_id
new_widget = self.create_terminal()
self.splitter.split_with_widget(
    current_pane,
    WherePosition.RIGHT,
    new_widget,
    "terminal:1"
)

# Split vertically
another_widget = self.create_output_panel()
self.splitter.split_with_widget(
    current_pane,
    WherePosition.BOTTOM,
    another_widget,
    "output:build"
)
```

### Persistence
```python
# Save workspace
workspace = {
    "layout": self.splitter.save_layout(),
    "widget_states": self.save_all_widget_states(),
    "app_preferences": self.get_preferences()
}
json.dump(workspace, open("workspace.json", "w"))

# Restore workspace
workspace = json.load(open("workspace.json"))
self.load_widget_states(workspace["widget_states"])
self.splitter.restore_layout(workspace["layout"])
```

## Quick Reference

### Core Methods
```python
# Layout operations
split_with_widget(pane_id, where, widget, widget_id)
close_pane(pane_id)
replace_widget(pane_id, widget, widget_id)

# Navigation
focus_pane(pane_id)
focus_next_pane()
focus_previous_pane()

# Persistence
save_layout() -> dict
restore_layout(layout: dict)

# Undo/Redo
undo()
redo()
can_undo() -> bool
can_redo() -> bool
```

### Key Signals
```python
# Widget lifecycle
widget_needed = Signal(str, str)      # widget_id, pane_id
widget_closing = Signal(str, QWidget)  # widget_id, widget

# Layout changes
layout_changed = Signal()
pane_focused = Signal(str)            # pane_id
pane_closed = Signal(str)             # pane_id
```

### Widget Provider Interface
```python
class WidgetProvider(Protocol):
    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Create or retrieve widget for the given ID"""
        ...

    def widget_closing(self, widget_id: str, widget: QWidget) -> None:
        """Notification that widget is being removed"""
        ...
```

## Related Documents

- **[Core Concepts](core-concepts.md)** - Deep dive into key concepts
- **[Quick Start](quick-start.md)** - Minimal working examples
- **[Widget Provider Architecture](../02-architecture/widget-provider.md)** - Provider pattern details
- **[Public API](../05-api/public-api.md)** - Complete API reference
- **[Usage Guide](../06-guides/usage-guide.md)** - Common patterns and examples

---

MultiSplit provides the foundation for building sophisticated, user-friendly split-pane interfaces while maintaining clean architecture and complete flexibility in widget management.