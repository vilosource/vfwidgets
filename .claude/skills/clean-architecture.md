---
name: clean-architecture
description: Enforce MVC and clean architecture patterns for complex widgets. Use when implementing model-view-controller separation, protocols, dependency injection, or designing complex widget architectures.
allowed-tools:
  - Read
  - Edit
  - Grep
---

# Clean Architecture Skill

When implementing complex widgets, follow VFWidgets clean architecture patterns to ensure maintainability, testability, and separation of concerns.

## When to Use Clean Architecture

Use MVC/clean architecture for:
- ✅ **Complex widgets** with significant business logic
- ✅ **Stateful widgets** with complex data models
- ✅ **Multi-view widgets** (split panes, tabs, etc.)
- ✅ **Undo/redo support** required
- ✅ **Command pattern** needed

Simple widgets (buttons, labels, basic inputs) can use simpler patterns.

## Core Principles

### 1. Layer Separation

**Model Layer** (Pure Python, No Qt):
- Data structures and business logic
- No Qt dependencies (`QObject`, `Signal`, etc.)
- Should be testable without Qt

**View Layer** (Qt Widgets):
- UI rendering and user interaction
- Qt widgets, painting, events
- No business logic

**Controller Layer** (Coordination):
- Command pattern for operations
- Undo/redo stack management
- Coordinates Model and View

**Bridge Layer** (Signal Translation):
- Translates Model events to Qt signals
- Allows View to react to Model changes
- Keeps Model Qt-free

### 2. Protocol-Based Design

Use Python protocols for dependency injection:

```python
from typing import Protocol

class WidgetProvider(Protocol):
    """Protocol for providing widgets to panes."""

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Create widget for pane."""
        ...

    def widget_closing(self, widget_id: str, pane_id: str, widget: QWidget) -> None:
        """Clean up widget on close."""
        ...
```

**Benefits**:
- Loose coupling
- Easy testing (mock implementations)
- Clear contracts
- No inheritance required

## Canonical Example: MultisplitWidget

Reference: `widgets/multisplit_widget/`

### Directory Structure

```
widgets/multisplit_widget/src/vfwidgets_multisplit/
├── model/              # MODEL LAYER (Pure Python)
│   ├── nodes.py       # Node data structures
│   ├── model.py       # Tree model logic
│   └── protocols.py   # Abstract protocols
├── controller/         # CONTROLLER LAYER
│   ├── controller.py  # Main controller
│   └── commands.py    # Command pattern (undo/redo)
├── view/              # VIEW LAYER (Qt Widgets)
│   ├── container.py   # Main widget container
│   └── visual_renderer.py  # Split bar rendering
├── bridge/            # BRIDGE LAYER
│   └── signal_bridge.py    # Model → Qt signals
└── __init__.py        # Public API
```

## Model Layer (Pure Python)

### Example: Node Data Structure

```python
"""Pure Python data structures - NO Qt dependencies."""

from dataclasses import dataclass
from typing import Optional, List
from uuid import uuid4


@dataclass
class PaneNode:
    """Represents a single pane in the tree."""

    id: str
    widget_id: Optional[str] = None
    parent: Optional['SplitNode'] = None

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid4())


@dataclass
class SplitNode:
    """Represents a split container."""

    id: str
    orientation: str  # "horizontal" or "vertical"
    children: List['Node']
    split_ratios: List[float]
    parent: Optional['SplitNode'] = None

    def add_child(self, node: 'Node', index: int = -1) -> None:
        """Add child node at index."""
        if index == -1:
            self.children.append(node)
        else:
            self.children.insert(index, node)
        node.parent = self


# Type alias for tree nodes
Node = PaneNode | SplitNode
```

**Key points**:
- ✅ Uses `dataclass` (Python stdlib)
- ✅ No Qt imports
- ✅ Pure business logic
- ✅ Easily testable

### Example: Model Logic

```python
"""Pure Python model logic."""

from typing import Optional, List
from .nodes import Node, PaneNode, SplitNode


class MultisplitModel:
    """Pure Python model for multisplit tree."""

    def __init__(self, root: Node):
        self._root = root
        self._observers: List[ModelObserver] = []

    def find_node(self, node_id: str) -> Optional[Node]:
        """Find node by ID (pure traversal logic)."""
        def search(node: Node) -> Optional[Node]:
            if node.id == node_id:
                return node
            if isinstance(node, SplitNode):
                for child in node.children:
                    result = search(child)
                    if result:
                        return result
            return None
        return search(self._root)

    def split_pane(self, pane_id: str, orientation: str) -> Optional[SplitNode]:
        """Split pane into two - pure business logic."""
        pane = self.find_node(pane_id)
        if not isinstance(pane, PaneNode):
            return None

        # Create new split node
        split = SplitNode(
            id=str(uuid4()),
            orientation=orientation,
            children=[pane, PaneNode(id=str(uuid4()))],
            split_ratios=[0.5, 0.5],
            parent=pane.parent
        )

        # Update tree structure
        if pane.parent:
            index = pane.parent.children.index(pane)
            pane.parent.children[index] = split

        # Notify observers (still no Qt!)
        self._notify_split(split)

        return split

    def _notify_split(self, split: SplitNode) -> None:
        """Notify observers of split (no Qt signals here)."""
        for observer in self._observers:
            observer.on_split_created(split)
```

**Key points**:
- ✅ No Qt dependencies
- ✅ Observable pattern (not Qt signals)
- ✅ Pure business logic
- ✅ Testable without GUI

## Bridge Layer (Signal Translation)

The bridge translates Model events to Qt signals:

```python
"""Bridge between pure model and Qt view."""

from PySide6.QtCore import QObject, Signal
from typing import Protocol


class ModelObserver(Protocol):
    """Observer protocol for model changes."""

    def on_split_created(self, split: SplitNode) -> None:
        """Called when split is created."""
        ...


class SignalBridge(QObject, ModelObserver):
    """Translates model events to Qt signals."""

    # Qt signals
    split_created = Signal(object)  # SplitNode
    pane_removed = Signal(str)      # pane_id

    def on_split_created(self, split: SplitNode) -> None:
        """Translate model event to Qt signal."""
        self.split_created.emit(split)

    def on_pane_removed(self, pane_id: str) -> None:
        """Translate model event to Qt signal."""
        self.pane_removed.emit(pane_id)
```

**Key points**:
- ✅ Implements model observer protocol
- ✅ Inherits from `QObject` for signals
- ✅ Bridges pure Python model to Qt view
- ✅ View can connect to Qt signals

## Controller Layer (Command Pattern)

Commands enable undo/redo:

```python
"""Command pattern for undoable operations."""

from typing import Protocol


class Command(Protocol):
    """Protocol for undoable commands."""

    def execute(self) -> None:
        """Execute the command."""
        ...

    def undo(self) -> None:
        """Undo the command."""
        ...


class SplitPaneCommand:
    """Command to split a pane."""

    def __init__(self, model: MultisplitModel, pane_id: str, orientation: str):
        self._model = model
        self._pane_id = pane_id
        self._orientation = orientation
        self._split_id: Optional[str] = None

    def execute(self) -> None:
        """Execute split operation."""
        split = self._model.split_pane(self._pane_id, self._orientation)
        if split:
            self._split_id = split.id

    def undo(self) -> None:
        """Undo split operation."""
        if self._split_id:
            self._model.remove_split(self._split_id)


class Controller:
    """Controller with undo/redo stack."""

    def __init__(self, model: MultisplitModel):
        self._model = model
        self._undo_stack: List[Command] = []
        self._redo_stack: List[Command] = []

    def execute(self, command: Command) -> None:
        """Execute command and add to undo stack."""
        command.execute()
        self._undo_stack.append(command)
        self._redo_stack.clear()

    def undo(self) -> None:
        """Undo last command."""
        if self._undo_stack:
            command = self._undo_stack.pop()
            command.undo()
            self._redo_stack.append(command)

    def redo(self) -> None:
        """Redo last undone command."""
        if self._redo_stack:
            command = self._redo_stack.pop()
            command.execute()
            self._undo_stack.append(command)
```

## View Layer (Qt Widgets)

View only handles rendering and user interaction:

```python
"""Qt view layer - no business logic."""

from PySide6.QtWidgets import QWidget, QSplitter
from PySide6.QtCore import Signal, Slot


class MultisplitContainer(QWidget):
    """Main widget container (View layer)."""

    # Signals to controller
    split_requested = Signal(str, str)  # pane_id, orientation
    pane_close_requested = Signal(str)  # pane_id

    def __init__(self, controller: Controller, bridge: SignalBridge):
        super().__init__()
        self._controller = controller
        self._bridge = bridge

        # Connect to model updates via bridge
        self._bridge.split_created.connect(self._on_split_created)
        self._bridge.pane_removed.connect(self._on_pane_removed)

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up UI (pure rendering logic)."""
        # Create UI components
        pass

    @Slot(object)
    def _on_split_created(self, split: SplitNode) -> None:
        """Update UI when split is created in model."""
        # Create QSplitter widget to match model structure
        splitter = QSplitter(Qt.Horizontal if split.orientation == "horizontal" else Qt.Vertical)
        # Render split in UI
        pass

    def split_pane_horizontal(self, pane_id: str) -> None:
        """Request horizontal split (delegates to controller)."""
        command = SplitPaneCommand(self._controller.model, pane_id, "horizontal")
        self._controller.execute(command)
```

**Key points**:
- ✅ No business logic (delegates to controller)
- ✅ Connects to bridge signals for model updates
- ✅ Emits signals for user actions
- ✅ Only rendering and interaction

## Testing Each Layer

### Testing Model (No Qt Required)

```python
def test_split_pane():
    """Test model logic without Qt."""
    model = MultisplitModel(PaneNode(id="root"))

    # Split pane
    split = model.split_pane("root", "horizontal")

    # Verify structure
    assert split is not None
    assert split.orientation == "horizontal"
    assert len(split.children) == 2
```

### Testing Controller

```python
def test_undo_redo():
    """Test undo/redo logic."""
    model = MultisplitModel(PaneNode(id="root"))
    controller = Controller(model)

    # Execute command
    command = SplitPaneCommand(model, "root", "horizontal")
    controller.execute(command)

    # Verify executed
    assert model.find_node(command._split_id) is not None

    # Undo
    controller.undo()
    assert model.find_node(command._split_id) is None

    # Redo
    controller.redo()
    assert model.find_node(command._split_id) is not None
```

### Testing View (With Qt)

```python
def test_view_updates(qtbot):
    """Test view updates when model changes."""
    model = MultisplitModel(PaneNode(id="root"))
    bridge = SignalBridge()
    model.add_observer(bridge)

    controller = Controller(model)
    view = MultisplitContainer(controller, bridge)
    qtbot.addWidget(view)

    # Listen for signal
    with qtbot.waitSignal(bridge.split_created):
        command = SplitPaneCommand(model, "root", "horizontal")
        controller.execute(command)
```

## Dependency Injection Pattern

Use protocols for dependencies:

```python
class MultisplitWidget(QWidget):
    """Public API widget with dependency injection."""

    def __init__(self, provider: WidgetProvider, parent=None):
        super().__init__(parent)

        # Create layers
        self._model = MultisplitModel(PaneNode(id="root"))
        self._bridge = SignalBridge()
        self._model.add_observer(self._bridge)
        self._controller = Controller(self._model)
        self._provider = provider  # Injected dependency

        # Create view
        self._view = MultisplitContainer(self._controller, self._bridge)

    def split_horizontal(self) -> None:
        """Public API method."""
        # Delegate to controller
        command = SplitPaneCommand(self._controller.model, current_pane_id, "horizontal")
        self._controller.execute(command)
```

## Benefits of Clean Architecture

### Testability
- ✅ Model testable without Qt
- ✅ Controller testable independently
- ✅ View can be mocked

### Maintainability
- ✅ Clear separation of concerns
- ✅ Changes isolated to specific layers
- ✅ Easy to understand data flow

### Reusability
- ✅ Model can be used in different UIs
- ✅ Controller logic shareable
- ✅ View can be swapped

## Documentation Reference

For detailed architecture guidance:
- **Main architecture doc**: `CleanArchitectureAsTheWay.md` (root)
- **Multisplit source**: `widgets/multisplit_widget/src/vfwidgets_multisplit/`

## Architecture Checklist

Before marking architecture as complete:

- [ ] Model layer has no Qt dependencies
- [ ] Model is testable without Qt
- [ ] View contains no business logic
- [ ] Controller uses command pattern
- [ ] Bridge translates model events to Qt signals
- [ ] Dependencies injected via protocols
- [ ] Tests exist for each layer independently
- [ ] Clear data flow: User → View → Controller → Model → Bridge → View
