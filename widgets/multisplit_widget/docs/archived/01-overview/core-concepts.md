# MultiSplit Core Concepts

## Overview

MultiSplit is built on three fundamental concepts that work together to provide a clean, flexible, and powerful layout system. Understanding these concepts is essential for effective use of the widget.

---

## Concept 1: Tree Structure

### What It Is

MultiSplit organizes your interface as a **binary tree** where each node is either:
- **Leaf Node**: Contains a single widget
- **Split Node**: Contains two child nodes with an orientation (horizontal/vertical)

### Tree Example

```
Root Split (Horizontal, ratio=[0.3, 0.7])
├── Leaf: File Explorer (widget_id="explorer")
└── Split (Vertical, ratio=[0.6, 0.4])
    ├── Leaf: Code Editor (widget_id="editor:main.py")
    └── Split (Horizontal, ratio=[0.5, 0.5])
        ├── Leaf: Terminal (widget_id="terminal:1")
        └── Leaf: Output (widget_id="output:build")
```

### Visual Layout

```
┌─────────────┬─────────────────────────────────┐
│             │           Editor                │
│   Explorer  │                                 │
│             ├─────────────────┬───────────────┤
│             │    Terminal     │    Output     │
│             │                 │               │
└─────────────┴─────────────────┴───────────────┘
```

### Tree Properties

**Binary Structure**
- Every split has exactly 2 children
- No empty splits (automatically cleaned up)
- Balanced operations (split, merge, move)

**Hierarchical Ratios**
```python
# Each split defines how space is divided between its children
split_node = {
    "orientation": "horizontal",
    "ratios": [0.3, 0.7],  # Left: 30%, Right: 70%
    "children": [left_child, right_child]
}
```

**Immutable Identities**
```python
# PaneId never changes, even through operations
leaf_node = {
    "pane_id": "pane-001",      # Stable identity
    "widget_id": "editor:main.py"  # What widget to display
}
```

### Tree Operations

**Split Operation**
```python
# Before: Single leaf
leaf = {"pane_id": "pane-1", "widget_id": "editor"}

# After: Split with new leaf
split = {
    "orientation": "horizontal",
    "ratios": [0.5, 0.5],
    "children": [
        {"pane_id": "pane-1", "widget_id": "editor"},     # Original
        {"pane_id": "pane-2", "widget_id": "terminal"}    # New
    ]
}
```

**Close Operation**
```python
# Before: Split with two children
split = {
    "children": [leaf_a, leaf_b]
}

# After: Remaining child promoted
# Split is removed, leaf_a becomes the parent's child
remaining = leaf_a
```

### Why Tree Structure?

**Predictable Layout**
- Clear parent-child relationships
- No floating or overlapping windows
- Space always fully utilized

**Efficient Operations**
- O(log n) split/close operations
- O(n) serialization and reconciliation
- Minimal memory overhead

**Natural Persistence**
- Maps directly to JSON structures
- Hierarchical relationships preserved
- Easy to validate and debug

---

## Concept 2: Widget Provider Pattern

### What It Is

MultiSplit uses a **provider pattern** where:
- MultiSplit manages **where** widgets go (layout)
- Application manages **what** widgets are (creation/lifecycle)

### The Contract

```python
from typing import Protocol

class WidgetProvider(Protocol):
    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """
        Create or retrieve a widget for the given ID.

        Args:
            widget_id: Opaque identifier meaningful to application
            pane_id: Where the widget will be placed

        Returns:
            QWidget instance to display
        """
        ...

    def widget_closing(self, widget_id: str, widget: QWidget) -> None:
        """
        Notification that widget is being removed from layout.

        Args:
            widget_id: The widget's identifier
            widget: The actual widget instance being removed
        """
        ...
```

### Provider Flow

```python
# 1. User triggers split
self.splitter.split_with_widget(pane_id, WherePosition.RIGHT, widget, "editor:file.py")

# 2. MultiSplit stores the widget_id in its tree
tree_node = {"pane_id": new_pane_id, "widget_id": "editor:file.py"}

# 3. During restoration, MultiSplit requests widget
self.splitter.widget_needed.emit("editor:file.py", new_pane_id)

# 4. Application provides widget
def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
    filename = widget_id[7:]  # Remove "editor:" prefix
    return CodeEditor(filename)
```

### Widget ID Design

**Opaque to MultiSplit**
```python
# MultiSplit doesn't understand these formats
"editor:main.py"
"terminal:session-42"
"plot:dataset-1"
"uuid:550e8400-e29b-41d4"

# MultiSplit only stores and returns them unchanged
```

**Meaningful to Application**
```python
class MyProvider:
    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        # Parse application-specific format
        widget_type, param = widget_id.split(":", 1)

        if widget_type == "editor":
            editor = CodeEditor()
            editor.load_file(param)
            return editor
        elif widget_type == "terminal":
            return Terminal(session_id=int(param))
        elif widget_type == "plot":
            return PlotWidget(dataset_name=param)
        else:
            return QLabel(f"Unknown widget: {widget_id}")
```

### Provider Patterns

**Direct Creation**
```python
def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
    """Create fresh widget each time"""
    return self.create_widget_from_id(widget_id)
```

**Widget Pool**
```python
def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
    """Reuse existing widgets when possible"""
    if widget_id in self.widget_pool:
        return self.widget_pool[widget_id]

    widget = self.create_widget_from_id(widget_id)
    self.widget_pool[widget_id] = widget
    return widget
```

**Lazy Factory**
```python
def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
    """Use factories for different widget types"""
    widget_type = widget_id.split(":")[0]
    factory = self.widget_factories[widget_type]
    return factory(widget_id, pane_id)
```

### Why Provider Pattern?

**Clean Separation**
- MultiSplit: Focus on layout logic
- Application: Control widget creation
- No coupling between layout and widget types

**Maximum Flexibility**
- Application defines widget ID format
- Application controls widget lifecycle
- Application manages widget state

**Easy Testing**
- Mock provider for layout tests
- Mock widgets for integration tests
- No complex widget setup in MultiSplit tests

---

## Concept 3: MVC Architecture

### What It Is

MultiSplit uses strict **Model-View-Controller** separation:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    Model    │    │ Controller  │    │    View     │
│             │    │             │    │             │
│ Pure Python │◄───┤ Commands    │────┤ Qt Widgets  │
│ Tree State  │    │ Undo/Redo   │    │ Events      │
│ NO Qt       │    │ Mutations   │    │ Rendering   │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       └─── Signals ───────┴──── Queries ─────┘
```

### Model Layer (core/)

**What It Contains**
```python
# Pure Python data structures
class TreeNode:
    """Base class for tree nodes"""
    pass

class LeafNode(TreeNode):
    def __init__(self, pane_id: str, widget_id: str):
        self.pane_id = pane_id      # Immutable identity
        self.widget_id = widget_id  # What widget to show

class SplitNode(TreeNode):
    def __init__(self, orientation: Orientation, children: list[TreeNode]):
        self.orientation = orientation  # Horizontal or Vertical
        self.children = children       # Exactly 2 children
        self.ratios = [0.5, 0.5]      # Space allocation
```

**What It Does NOT Contain**
```python
# ❌ FORBIDDEN in Model
from PySide6.QtWidgets import QWidget  # No Qt imports
from view import MultiSplitView        # No view imports

class BadNode:
    def __init__(self, widget: QWidget):  # No widget references
        self.widget = widget
```

**Model Responsibilities**
- Tree structure and invariants
- Signal emission for changes
- State validation
- Serialization support

### Controller Layer (controller/)

**Command Pattern**
```python
from abc import ABC, abstractmethod

class Command(ABC):
    """Base class for all layout mutations"""

    @abstractmethod
    def execute(self, model: Model) -> None:
        """Apply the change to the model"""
        pass

    @abstractmethod
    def undo(self, model: Model) -> None:
        """Reverse the change"""
        pass

class SplitCommand(Command):
    def __init__(self, pane_id: str, where: WherePosition,
                 new_widget_id: str, ratio: float = 0.5):
        self.pane_id = pane_id
        self.where = where
        self.new_widget_id = new_widget_id
        self.ratio = ratio
        self.new_pane_id = None  # Generated during execute

    def execute(self, model: Model) -> None:
        # Generate new pane ID
        self.new_pane_id = model.generate_pane_id()

        # Find target node and split it
        target_node = model.find_node(self.pane_id)
        model.split_node(target_node, self.where, self.new_pane_id,
                        self.new_widget_id, self.ratio)
```

**Controller Responsibilities**
- All model mutations via commands
- Undo/redo stack management
- Transaction boundaries
- Command validation

### View Layer (view/)

**Reconciliation Pattern**
```python
class MultiSplitView(QWidget):
    def __init__(self):
        super().__init__()
        self._widget_map: dict[str, QWidget] = {}  # pane_id -> widget

    def _reconcile(self, old_tree: TreeNode, new_tree: TreeNode):
        """Update view to match new tree without rebuilding"""

        # Phase 1: Identify changes
        old_panes = self._extract_pane_ids(old_tree)
        new_panes = self._extract_pane_ids(new_tree)

        removed_panes = old_panes - new_panes
        added_panes = new_panes - old_panes
        existing_panes = old_panes & new_panes

        # Phase 2: Handle removals
        for pane_id in removed_panes:
            widget = self._widget_map.pop(pane_id)
            self.widget_closing.emit(widget_id, widget)

        # Phase 3: Request new widgets
        for pane_id in added_panes:
            widget_id = self._get_widget_id(new_tree, pane_id)
            self.widget_needed.emit(widget_id, pane_id)

        # Phase 4: Update layout structure
        self._update_layout_structure(new_tree)
```

**View Responsibilities**
- Qt widget management
- Event handling and forwarding
- Reconciliation (preserve widgets)
- Rendering coordination

### MVC Communication

**Signal Flow**
```python
# Model signals changes
model.tree_changed.emit(old_tree, new_tree)
model.pane_focused.emit(pane_id)

# Controller executes commands
controller.execute(SplitCommand(...))
controller.undo()

# View queries model (read-only)
current_tree = model.root
focused_pane = model.focused_pane_id
```

**No Circular Dependencies**
```python
# ✅ ALLOWED
model.py:       # No imports from other layers
controller.py:  from model import Model, Command
view.py:        from model import Model (read-only)

# ❌ FORBIDDEN
model.py:       from controller import ...  # Model knows nothing of controller
controller.py:  from view import ...        # Controller doesn't know about view
view.py:        # Direct model mutation      # View never mutates model
```

### Why MVC?

**Testability**
```python
# Test model without Qt
def test_split_operation():
    model = Model()
    model.set_root(LeafNode("pane-1", "editor"))

    # No Qt required
    assert model.root.pane_id == "pane-1"
```

**Persistence**
```python
# Model state is pure data
layout_data = model.serialize()
json.dump(layout_data, file)

# Restoration doesn't require view
new_model = Model()
new_model.deserialize(layout_data)
```

**Undo/Redo**
```python
# Commands are pure data operations
command = SplitCommand("pane-1", WherePosition.RIGHT, "editor:new.py")
controller.execute(command)  # Apply
controller.undo()           # Reverse
```

---

## How Concepts Work Together

### Example: Adding a Split

**1. User Action (View)**
```python
# User clicks "Split Right" button
def on_split_right_clicked():
    current_pane = self.model.focused_pane_id
    new_widget = CodeEditor()
    widget_id = "editor:new_file.py"

    # Create command
    command = SplitCommand(current_pane, WherePosition.RIGHT, widget_id)
    self.controller.execute(command)
```

**2. Command Execution (Controller)**
```python
def execute(self, model: Model):
    # Generate stable pane ID
    self.new_pane_id = model.generate_pane_id()

    # Mutate tree structure
    model.split_pane(self.pane_id, self.where, self.new_pane_id,
                    self.new_widget_id, self.ratio)

    # Model emits signals
    model.tree_changed.emit(old_tree, new_tree)
```

**3. Tree Update (Model)**
```python
def split_pane(self, pane_id, where, new_pane_id, new_widget_id, ratio):
    # Find node to split
    node = self.find_node(pane_id)

    # Create new structure
    new_leaf = LeafNode(new_pane_id, new_widget_id)
    split = SplitNode(orientation, [node, new_leaf])
    split.ratios = [ratio, 1.0 - ratio]

    # Replace in tree
    self.replace_node(node, split)
```

**4. View Reconciliation (View)**
```python
def on_tree_changed(self, old_tree, new_tree):
    # Identify what changed
    changes = self._diff_trees(old_tree, new_tree)

    # Request new widget
    if changes.added_panes:
        for pane_id in changes.added_panes:
            widget_id = new_tree.get_widget_id(pane_id)
            self.widget_needed.emit(widget_id, pane_id)
```

**5. Widget Provision (Application)**
```python
def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
    # Application creates widget
    if widget_id.startswith("editor:"):
        filename = widget_id[7:]
        editor = CodeEditor()
        editor.load_file(filename)
        return editor
```

**6. Layout Update (View)**
```python
def add_widget(self, pane_id: str, widget: QWidget):
    # Store widget reference
    self._widget_map[pane_id] = widget

    # Update Qt layout structure
    self._update_layout_to_match_tree()
```

### Complete Flow Summary

```
User Action → Command → Model Update → Signal → View Reconciliation → Widget Request → Application Response → Layout Update
```

This flow ensures:
- **Clean separation**: Each layer has clear responsibilities
- **Predictable state**: All changes go through the same path
- **Undoable operations**: Commands can be reversed
- **Widget preservation**: Reconciliation reuses existing widgets
- **Application control**: Provider pattern gives full widget control

## Related Documents

- **[Introduction](introduction.md)** - Overview and value proposition
- **[Quick Start](quick-start.md)** - Basic usage examples
- **[MVC Architecture](../02-architecture/mvc-architecture.md)** - Detailed MVC design
- **[Widget Provider](../02-architecture/widget-provider.md)** - Provider pattern details
- **[Tree Structure](../02-architecture/tree-structure.md)** - Tree implementation details

---

These three concepts - Tree Structure, Widget Provider Pattern, and MVC Architecture - form the foundation that makes MultiSplit both powerful and maintainable.