# Phase 1 Implementation Tasks

## Overview

Phase 1 builds the working core of the MultiSplit widget on top of Phase 0 foundations. This phase creates a functional split-pane widget with basic operations.

## Prerequisites

- ✅ Phase 0 Complete (ID generation, tree utils, signals, geometry, reconciler, transactions)
- ✅ All 41 Phase 0 tests passing
- ✅ Project structure established

## Task Structure

Each task includes:
- **Task ID**: Unique identifier (P1.X.Y)
- **Title**: Clear description
- **Dependencies**: Required prior tasks
- **Action**: CREATE/MODIFY/ENHANCE
- **File**: Target file path
- **Implementation**: Complete code
- **Tests**: Test cases to write first (TDD)
- **Validation**: Success criteria

---

## P1.1: Enhanced Type System

### Task P1.1.1: Add Missing Enums
**Title**: Add BEFORE and AFTER positions to WherePosition enum
**Dependencies**: Phase 0 complete
**Action**: MODIFY
**File**: `src/vfwidgets_multisplit/core/types.py`

**Current State**: WherePosition has LEFT, RIGHT, TOP, BOTTOM, REPLACE

**Implementation**:
Add to WherePosition enum after BOTTOM:
```python
    BEFORE = "before"  # Insert before target (same parent)
    AFTER = "after"    # Insert after target (same parent)
```

**Tests** (`tests/test_types.py`):
```python
def test_where_position_complete():
    """Test all WherePosition values are present."""
    positions = [WherePosition.LEFT, WherePosition.RIGHT,
                WherePosition.TOP, WherePosition.BOTTOM,
                WherePosition.BEFORE, WherePosition.AFTER,
                WherePosition.REPLACE]
    assert len(positions) == 7
    assert all(isinstance(p, WherePosition) for p in positions)
```

**Validation**:
- All 7 positions available
- to_orientation() method handles new positions correctly

---

### Task P1.1.2: Add Constraint Types
**Title**: Add constraint dataclasses for pane sizing
**Dependencies**: P1.1.1
**Action**: MODIFY
**File**: `src/vfwidgets_multisplit/core/types.py`

**Implementation**:
Add after Bounds class:
```python
@dataclass(frozen=True)
class SizeConstraints:
    """Size constraints for panes."""
    min_width: int = 50
    min_height: int = 50
    max_width: Optional[int] = None
    max_height: Optional[int] = None

    def __post_init__(self):
        """Validate constraints."""
        if self.min_width < 0 or self.min_height < 0:
            raise ValueError("Minimum sizes must be non-negative")
        if self.max_width and self.max_width < self.min_width:
            raise ValueError("Max width must be >= min width")
        if self.max_height and self.max_height < self.min_height:
            raise ValueError("Max height must be >= min height")

    def clamp_size(self, width: int, height: int) -> tuple[int, int]:
        """Clamp size to constraints."""
        w = max(self.min_width, width)
        h = max(self.min_height, height)
        if self.max_width:
            w = min(self.max_width, w)
        if self.max_height:
            h = min(self.max_height, h)
        return w, h
```

**Tests**:
```python
def test_size_constraints():
    """Test size constraints validation and clamping."""
    constraints = SizeConstraints(min_width=100, min_height=50)
    assert constraints.clamp_size(50, 25) == (100, 50)
    assert constraints.clamp_size(200, 100) == (200, 100)

    with pytest.raises(ValueError):
        SizeConstraints(min_width=-1)
```

---

## P1.2: Enhanced Node System

### Task P1.2.1: Add Parent References
**Title**: Add parent tracking to node classes
**Dependencies**: P1.1.2
**Action**: MODIFY
**File**: `src/vfwidgets_multisplit/core/nodes.py`

**Implementation**:
```python
from typing import Optional, List, TYPE_CHECKING
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from ..core.types import (
    PaneId, NodeId, WidgetId, Orientation,
    SizeConstraints, Bounds
)

if TYPE_CHECKING:
    from ..core.visitor import NodeVisitor

class PaneNode(ABC):
    """Abstract base class for tree nodes."""

    def __init__(self):
        """Initialize base node."""
        self.parent: Optional['SplitNode'] = None
        self._bounds: Optional[Bounds] = None

    @abstractmethod
    def accept(self, visitor: 'NodeVisitor'):
        """Accept visitor for tree traversal."""
        pass

    @property
    def bounds(self) -> Optional[Bounds]:
        """Get node bounds (set by geometry calculator)."""
        return self._bounds

    @bounds.setter
    def bounds(self, value: Bounds):
        """Set node bounds."""
        self._bounds = value

    def get_root(self) -> 'PaneNode':
        """Get tree root."""
        node = self
        while node.parent:
            node = node.parent
        return node

    def get_depth(self) -> int:
        """Get node depth from root."""
        depth = 0
        node = self
        while node.parent:
            depth += 1
            node = node.parent
        return depth


@dataclass
class LeafNode(PaneNode):
    """Terminal node containing a widget."""

    pane_id: PaneId
    widget_id: WidgetId
    constraints: SizeConstraints = field(default_factory=SizeConstraints)

    def __post_init__(self):
        """Initialize parent class."""
        super().__init__()

    def accept(self, visitor: 'NodeVisitor'):
        """Accept visitor."""
        return visitor.visit_leaf(self)


@dataclass
class SplitNode(PaneNode):
    """Container node with children."""

    node_id: NodeId
    orientation: Orientation
    children: List[PaneNode] = field(default_factory=list)
    ratios: List[float] = field(default_factory=list)

    def __post_init__(self):
        """Initialize parent class and set parent references."""
        super().__init__()
        for child in self.children:
            child.parent = self

    def accept(self, visitor: 'NodeVisitor'):
        """Accept visitor."""
        return visitor.visit_split(self)

    def add_child(self, child: PaneNode, ratio: float = None):
        """Add child node."""
        child.parent = self
        self.children.append(child)

        if ratio is not None:
            self.ratios.append(ratio)
        else:
            # Equal distribution
            count = len(self.children)
            self.ratios = [1.0 / count] * count

    def remove_child(self, child: PaneNode):
        """Remove child node."""
        if child in self.children:
            idx = self.children.index(child)
            self.children.remove(child)
            child.parent = None

            # Adjust ratios
            if self.ratios and idx < len(self.ratios):
                self.ratios.pop(idx)
                # Renormalize
                if self.ratios:
                    total = sum(self.ratios)
                    self.ratios = [r / total for r in self.ratios]

    def replace_child(self, old_child: PaneNode, new_child: PaneNode):
        """Replace child node."""
        if old_child in self.children:
            idx = self.children.index(old_child)
            old_child.parent = None
            new_child.parent = self
            self.children[idx] = new_child
```

**Tests**:
```python
def test_parent_references():
    """Test parent tracking in tree."""
    root = SplitNode(
        node_id=NodeId("root"),
        orientation=Orientation.HORIZONTAL
    )
    leaf1 = LeafNode(PaneId("p1"), WidgetId("w1"))
    leaf2 = LeafNode(PaneId("p2"), WidgetId("w2"))

    root.add_child(leaf1)
    root.add_child(leaf2)

    assert leaf1.parent == root
    assert leaf2.parent == root
    assert leaf1.get_root() == root
    assert leaf1.get_depth() == 1
```

---

## P1.3: Core Model

### Task P1.3.1: Create PaneModel
**Title**: Create the core model class
**Dependencies**: P1.2.1
**Action**: CREATE
**File**: `src/vfwidgets_multisplit/core/model.py`

**Implementation**:
```python
"""Core model for MultiSplit widget.

Pure Python implementation with no Qt dependencies.
Manages tree state and emits signals for changes.
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
import json

from .types import PaneId, WidgetId, NodeId, Orientation, WherePosition
from .nodes import PaneNode, LeafNode, SplitNode
from .utils import generate_pane_id, generate_node_id
from .signals import ModelSignals
from .tree_utils import find_node_by_id, validate_tree_structure


@dataclass
class PaneModel:
    """Core model managing pane tree state.

    This is the single source of truth for the pane structure.
    All mutations must go through the controller's commands.
    """

    root: Optional[PaneNode] = None
    focused_pane_id: Optional[PaneId] = None
    signals: ModelSignals = field(default_factory=ModelSignals)

    # Internal state
    _pane_registry: Dict[PaneId, PaneNode] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize model state."""
        if self.root:
            self._rebuild_registry()

    def _rebuild_registry(self):
        """Rebuild the pane ID registry."""
        self._pane_registry.clear()
        if not self.root:
            return

        from .tree_utils import get_all_leaves
        for leaf in get_all_leaves(self.root):
            self._pane_registry[leaf.pane_id] = leaf

    def get_pane(self, pane_id: PaneId) -> Optional[PaneNode]:
        """Get pane by ID."""
        return self._pane_registry.get(pane_id)

    def get_all_pane_ids(self) -> List[PaneId]:
        """Get all pane IDs."""
        return list(self._pane_registry.keys())

    def validate(self) -> tuple[bool, List[str]]:
        """Validate model state."""
        if not self.root:
            return True, []  # Empty is valid

        return validate_tree_structure(self.root)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize model to dictionary."""
        def node_to_dict(node: PaneNode) -> Dict[str, Any]:
            if isinstance(node, LeafNode):
                return {
                    'type': 'leaf',
                    'pane_id': str(node.pane_id),
                    'widget_id': str(node.widget_id),
                    'constraints': {
                        'min_width': node.constraints.min_width,
                        'min_height': node.constraints.min_height,
                        'max_width': node.constraints.max_width,
                        'max_height': node.constraints.max_height,
                    }
                }
            elif isinstance(node, SplitNode):
                return {
                    'type': 'split',
                    'node_id': str(node.node_id),
                    'orientation': node.orientation.value,
                    'ratios': node.ratios,
                    'children': [node_to_dict(child) for child in node.children]
                }
            return {}

        return {
            'root': node_to_dict(self.root) if self.root else None,
            'focused_pane_id': str(self.focused_pane_id) if self.focused_pane_id else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PaneModel':
        """Deserialize model from dictionary."""
        from .types import SizeConstraints

        def dict_to_node(node_dict: Dict[str, Any]) -> Optional[PaneNode]:
            if not node_dict:
                return None

            if node_dict['type'] == 'leaf':
                constraints_data = node_dict.get('constraints', {})
                return LeafNode(
                    pane_id=PaneId(node_dict['pane_id']),
                    widget_id=WidgetId(node_dict['widget_id']),
                    constraints=SizeConstraints(
                        min_width=constraints_data.get('min_width', 50),
                        min_height=constraints_data.get('min_height', 50),
                        max_width=constraints_data.get('max_width'),
                        max_height=constraints_data.get('max_height')
                    )
                )
            elif node_dict['type'] == 'split':
                children = [dict_to_node(child) for child in node_dict['children']]
                return SplitNode(
                    node_id=NodeId(node_dict['node_id']),
                    orientation=Orientation(node_dict['orientation']),
                    children=[c for c in children if c],
                    ratios=node_dict['ratios']
                )
            return None

        root = dict_to_node(data.get('root'))
        focused = data.get('focused_pane_id')

        model = cls(root=root)
        if focused:
            model.focused_pane_id = PaneId(focused)

        return model
```

**Tests**:
```python
def test_pane_model_creation():
    """Test model creation and registry."""
    model = PaneModel()
    assert model.root is None
    assert len(model.get_all_pane_ids()) == 0

    # Add root
    leaf = LeafNode(PaneId("p1"), WidgetId("w1"))
    model.root = leaf
    model._rebuild_registry()

    assert model.get_pane(PaneId("p1")) == leaf
    assert len(model.get_all_pane_ids()) == 1

def test_model_serialization():
    """Test model serialization/deserialization."""
    model = PaneModel(
        root=LeafNode(PaneId("p1"), WidgetId("editor:main.py"))
    )

    data = model.to_dict()
    assert data['root']['type'] == 'leaf'
    assert data['root']['widget_id'] == 'editor:main.py'

    model2 = PaneModel.from_dict(data)
    assert isinstance(model2.root, LeafNode)
    assert model2.root.widget_id == WidgetId("editor:main.py")
```

---

## P1.4: Core Commands

### Task P1.4.1: Create Command Base
**Title**: Create command base class and infrastructure
**Dependencies**: P1.3.1
**Action**: CREATE
**File**: `src/vfwidgets_multisplit/controller/commands.py`

**Implementation**:
```python
"""Command pattern implementation for MultiSplit.

All model mutations go through commands for undo/redo support.
"""

from abc import ABC, abstractmethod
from typing import Optional, Any, Dict
from dataclasses import dataclass

from ..core.types import PaneId, WidgetId, NodeId, Orientation, WherePosition
from ..core.model import PaneModel
from ..core.nodes import PaneNode, LeafNode, SplitNode


class Command(ABC):
    """Abstract base class for commands."""

    def __init__(self, model: PaneModel):
        """Initialize command with model reference."""
        self.model = model
        self.executed = False
        self._state_before: Optional[Dict[str, Any]] = None

    @abstractmethod
    def execute(self) -> bool:
        """Execute the command.

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def undo(self) -> bool:
        """Undo the command.

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def description(self) -> str:
        """Get human-readable description."""
        pass

    def can_execute(self) -> bool:
        """Check if command can be executed."""
        return not self.executed

    def can_undo(self) -> bool:
        """Check if command can be undone."""
        return self.executed and self._state_before is not None
```

---

### Task P1.4.2: Create SplitPaneCommand
**Title**: Implement pane splitting command
**Dependencies**: P1.4.1
**Action**: MODIFY (continue commands.py)
**File**: `src/vfwidgets_multisplit/controller/commands.py`

**Implementation** (add to commands.py):
```python
@dataclass
class SplitPaneCommand(Command):
    """Command to split a pane."""

    target_pane_id: PaneId
    new_widget_id: WidgetId
    position: WherePosition
    ratio: float = 0.5

    def __init__(self, model: PaneModel, target_pane_id: PaneId,
                 new_widget_id: WidgetId, position: WherePosition,
                 ratio: float = 0.5):
        """Initialize split command."""
        super().__init__(model)
        self.target_pane_id = target_pane_id
        self.new_widget_id = new_widget_id
        self.position = position
        self.ratio = ratio
        self._new_pane_id: Optional[PaneId] = None
        self._new_node_id: Optional[NodeId] = None

    def execute(self) -> bool:
        """Split the target pane."""
        if self.executed:
            return False

        # Find target
        target = self.model.get_pane(self.target_pane_id)
        if not target:
            return False

        # Save state
        self._state_before = self.model.to_dict()

        # Generate IDs
        from ..core.utils import generate_pane_id, generate_node_id
        self._new_pane_id = generate_pane_id()

        # Create new leaf
        new_leaf = LeafNode(
            pane_id=self._new_pane_id,
            widget_id=self.new_widget_id
        )

        # Handle different split positions
        if self.position == WherePosition.REPLACE:
            # Simple replacement
            if target.parent:
                target.parent.replace_child(target, new_leaf)
            else:
                self.model.root = new_leaf

        elif self.position in (WherePosition.BEFORE, WherePosition.AFTER):
            # Insert as sibling
            if not target.parent:
                return False  # Can't insert sibling to root

            parent = target.parent
            idx = parent.children.index(target)

            if self.position == WherePosition.AFTER:
                idx += 1

            parent.children.insert(idx, new_leaf)
            new_leaf.parent = parent

            # Adjust ratios
            count = len(parent.children)
            parent.ratios = [1.0 / count] * count

        else:
            # Create split (LEFT, RIGHT, TOP, BOTTOM)
            orientation = self.position.to_orientation()
            if not orientation:
                return False

            self._new_node_id = generate_node_id()

            # Create new split node
            new_split = SplitNode(
                node_id=self._new_node_id,
                orientation=orientation,
                children=[],
                ratios=[]
            )

            # Arrange children based on position
            if self.position in (WherePosition.LEFT, WherePosition.TOP):
                new_split.add_child(new_leaf, self.ratio)
                new_split.add_child(target, 1.0 - self.ratio)
            else:
                new_split.add_child(target, 1.0 - self.ratio)
                new_split.add_child(new_leaf, self.ratio)

            # Replace target with split
            if target.parent:
                target.parent.replace_child(target, new_split)
            else:
                self.model.root = new_split

        # Update registry and emit signals
        self.model._rebuild_registry()
        self.model.signals.structure_changed.emit()
        self.model.signals.pane_added.emit(self._new_pane_id)

        self.executed = True
        return True

    def undo(self) -> bool:
        """Undo the split."""
        if not self.can_undo():
            return False

        # Restore previous state
        restored_model = PaneModel.from_dict(self._state_before)
        self.model.root = restored_model.root
        self.model.focused_pane_id = restored_model.focused_pane_id

        # Update registry and emit signals
        self.model._rebuild_registry()
        self.model.signals.structure_changed.emit()

        if self._new_pane_id:
            self.model.signals.pane_removed.emit(self._new_pane_id)

        self.executed = False
        return True

    def description(self) -> str:
        """Get command description."""
        return f"Split pane {self.target_pane_id} {self.position.value}"
```

---

### Task P1.4.3: Create RemovePaneCommand
**Title**: Implement pane removal command
**Dependencies**: P1.4.2
**Action**: MODIFY (continue commands.py)
**File**: `src/vfwidgets_multisplit/controller/commands.py`

**Implementation** (add to commands.py):
```python
@dataclass
class RemovePaneCommand(Command):
    """Command to remove a pane."""

    pane_id: PaneId

    def __init__(self, model: PaneModel, pane_id: PaneId):
        """Initialize remove command."""
        super().__init__(model)
        self.pane_id = pane_id

    def execute(self) -> bool:
        """Remove the pane."""
        if self.executed:
            return False

        target = self.model.get_pane(self.pane_id)
        if not target:
            return False

        # Save state
        self._state_before = self.model.to_dict()

        # Handle removal based on parent
        if not target.parent:
            # Removing root
            self.model.root = None
        else:
            parent = target.parent
            parent.remove_child(target)

            # Handle parent with single child
            if len(parent.children) == 1:
                # Collapse: replace parent with remaining child
                remaining = parent.children[0]

                if parent.parent:
                    parent.parent.replace_child(parent, remaining)
                else:
                    self.model.root = remaining
                    remaining.parent = None

            elif len(parent.children) == 0:
                # Remove empty parent
                if parent.parent:
                    parent.parent.remove_child(parent)
                else:
                    self.model.root = None

        # Update state
        self.model._rebuild_registry()
        self.model.signals.structure_changed.emit()
        self.model.signals.pane_removed.emit(self.pane_id)

        self.executed = True
        return True

    def undo(self) -> bool:
        """Undo the removal."""
        if not self.can_undo():
            return False

        # Restore state
        restored_model = PaneModel.from_dict(self._state_before)
        self.model.root = restored_model.root
        self.model.focused_pane_id = restored_model.focused_pane_id

        # Update state
        self.model._rebuild_registry()
        self.model.signals.structure_changed.emit()
        self.model.signals.pane_added.emit(self.pane_id)

        self.executed = False
        return True

    def description(self) -> str:
        """Get command description."""
        return f"Remove pane {self.pane_id}"
```

---

## P1.5: Enhanced Controller

### Task P1.5.1: Add Command Execution
**Title**: Enhance controller with command execution and undo/redo
**Dependencies**: P1.4.3
**Action**: MODIFY
**File**: `src/vfwidgets_multisplit/controller/controller.py`

**Implementation**:
```python
"""Controller for MultiSplit widget.

Manages commands, transactions, and undo/redo stack.
"""

from typing import List, Optional
from dataclasses import dataclass, field

from ..core.model import PaneModel
from ..core.types import PaneId, WidgetId, WherePosition
from .commands import Command, SplitPaneCommand, RemovePaneCommand
from .transaction import TransactionContext


@dataclass
class PaneController:
    """Controller managing model mutations through commands."""

    model: PaneModel
    _undo_stack: List[Command] = field(default_factory=list)
    _redo_stack: List[Command] = field(default_factory=list)
    _transaction_depth: int = 0
    _transaction_commands: List[Command] = field(default_factory=list)

    # Configuration
    max_undo_levels: int = 100

    def execute_command(self, command: Command) -> bool:
        """Execute a command.

        Args:
            command: Command to execute

        Returns:
            True if successful
        """
        if not command.can_execute():
            return False

        success = command.execute()

        if success:
            if self._transaction_depth > 0:
                # Inside transaction
                self._transaction_commands.append(command)
            else:
                # Normal execution
                self._undo_stack.append(command)
                self._redo_stack.clear()

                # Limit undo stack
                if len(self._undo_stack) > self.max_undo_levels:
                    self._undo_stack.pop(0)

                # Emit signal
                self.model.signals.command_executed.emit(command.description())

        return success

    def undo(self) -> bool:
        """Undo last command."""
        if not self.can_undo():
            return False

        command = self._undo_stack.pop()
        success = command.undo()

        if success:
            self._redo_stack.append(command)
            self.model.signals.command_undone.emit(command.description())

        return success

    def redo(self) -> bool:
        """Redo last undone command."""
        if not self.can_redo():
            return False

        command = self._redo_stack.pop()
        success = command.execute()

        if success:
            self._undo_stack.append(command)
            self.model.signals.command_executed.emit(command.description())

        return success

    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self._undo_stack) > 0 and self._transaction_depth == 0

    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self._redo_stack) > 0 and self._transaction_depth == 0

    def clear_history(self):
        """Clear undo/redo history."""
        self._undo_stack.clear()
        self._redo_stack.clear()

    # High-level operations

    def split_pane(self, target_pane_id: PaneId, widget_id: WidgetId,
                   position: WherePosition, ratio: float = 0.5) -> bool:
        """Split a pane."""
        command = SplitPaneCommand(
            self.model, target_pane_id, widget_id, position, ratio
        )
        return self.execute_command(command)

    def remove_pane(self, pane_id: PaneId) -> bool:
        """Remove a pane."""
        command = RemovePaneCommand(self.model, pane_id)
        return self.execute_command(command)

    # Transaction support

    def _begin_transaction(self):
        """Begin a transaction."""
        self._transaction_depth += 1
        if self._transaction_depth == 1:
            self._transaction_commands.clear()

    def _commit_transaction(self):
        """Commit current transaction."""
        self._transaction_depth -= 1
        if self._transaction_depth == 0:
            # Create composite command
            if self._transaction_commands:
                # For now, just add all commands to undo stack
                self._undo_stack.extend(self._transaction_commands)
                self._redo_stack.clear()
            self._transaction_commands.clear()

    def _rollback_transaction(self):
        """Rollback current transaction."""
        self._transaction_depth -= 1
        if self._transaction_depth == 0:
            # Undo all transaction commands in reverse
            for command in reversed(self._transaction_commands):
                if command.executed:
                    command.undo()
            self._transaction_commands.clear()

    def transaction(self):
        """Create transaction context."""
        return TransactionContext(self)
```

**Tests**:
```python
def test_controller_command_execution():
    """Test command execution and undo/redo."""
    model = PaneModel(
        root=LeafNode(PaneId("p1"), WidgetId("w1"))
    )
    controller = PaneController(model)

    # Execute split
    success = controller.split_pane(
        PaneId("p1"), WidgetId("w2"),
        WherePosition.RIGHT
    )
    assert success
    assert len(model.get_all_pane_ids()) == 2

    # Undo
    assert controller.can_undo()
    controller.undo()
    assert len(model.get_all_pane_ids()) == 1

    # Redo
    assert controller.can_redo()
    controller.redo()
    assert len(model.get_all_pane_ids()) == 2
```

---

## P1.6: Basic Container Widget

### Task P1.6.1: Create Container Widget
**Title**: Create Qt container widget for rendering
**Dependencies**: P1.5.1
**Action**: CREATE
**File**: `src/vfwidgets_multisplit/view/container.py`

**Implementation**:
```python
"""Container widget for MultiSplit.

Qt widget that renders the pane tree.
"""

from typing import Optional, Dict, Protocol
from PySide6.QtWidgets import QWidget, QSplitter
from PySide6.QtCore import Qt, Signal

from ..core.types import PaneId, WidgetId
from ..core.nodes import PaneNode, LeafNode, SplitNode
from ..core.model import PaneModel
from ..view.tree_reconciler import TreeReconciler, ReconcilerOperations


class WidgetProvider(Protocol):
    """Protocol for widget provider."""

    def provide_widget(self, widget_id: WidgetId, pane_id: PaneId) -> QWidget:
        """Provide widget for pane."""
        ...


class PaneContainer(QWidget, ReconcilerOperations):
    """Qt container widget managing pane display."""

    # Signals
    widget_needed = Signal(str, str)  # widget_id, pane_id
    pane_focused = Signal(str)  # pane_id

    def __init__(self, model: PaneModel,
                 provider: Optional[WidgetProvider] = None,
                 parent: Optional[QWidget] = None):
        """Initialize container."""
        super().__init__(parent)

        self.model = model
        self.provider = provider
        self.reconciler = TreeReconciler()

        # Widget tracking
        self._widgets: Dict[PaneId, QWidget] = {}
        self._splitters: Dict[str, QSplitter] = {}
        self._current_tree: Optional[PaneNode] = None

        # Connect model signals
        self.model.signals.structure_changed.connect(self._on_structure_changed)

        # Initial render
        self._update_view()

    def _on_structure_changed(self):
        """Handle model structure changes."""
        self._update_view()

    def _update_view(self):
        """Update view to match model."""
        # Get differences
        diff = self.reconciler.diff_trees(self._current_tree, self.model.root)

        if not diff.has_changes():
            return

        # Apply changes
        for pane_id in diff.removed:
            self.remove_pane(pane_id)

        for pane_id in diff.added:
            self.add_pane(pane_id)

        # Rebuild layout
        self._rebuild_layout()

        # Update current tree
        self._current_tree = self.model.root

    def _rebuild_layout(self):
        """Rebuild widget layout from model."""
        if not self.model.root:
            # Clear everything
            for widget in self._widgets.values():
                widget.setParent(None)
            return

        # Build widget tree
        root_widget = self._build_widget_tree(self.model.root)

        # Set as main widget
        if self.layout():
            # Clear old layout
            old = self.layout().takeAt(0)
            if old and old.widget():
                old.widget().setParent(None)
        else:
            # Create layout
            from PySide6.QtWidgets import QVBoxLayout
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            self.setLayout(layout)

        if root_widget:
            self.layout().addWidget(root_widget)

    def _build_widget_tree(self, node: PaneNode) -> Optional[QWidget]:
        """Build Qt widget tree from node tree."""
        if isinstance(node, LeafNode):
            # Get or create widget
            if node.pane_id in self._widgets:
                return self._widgets[node.pane_id]
            else:
                # Request widget from provider
                if self.provider:
                    widget = self.provider.provide_widget(
                        node.widget_id, node.pane_id
                    )
                    self._widgets[node.pane_id] = widget
                    return widget
                else:
                    # Emit signal for widget
                    self.widget_needed.emit(
                        str(node.widget_id), str(node.pane_id)
                    )
                    # Create placeholder
                    placeholder = QWidget()
                    self._widgets[node.pane_id] = placeholder
                    return placeholder

        elif isinstance(node, SplitNode):
            # Create splitter
            orientation = (Qt.Orientation.Horizontal
                         if node.orientation.value == "horizontal"
                         else Qt.Orientation.Vertical)

            splitter = QSplitter(orientation)

            # Add children
            for child in node.children:
                child_widget = self._build_widget_tree(child)
                if child_widget:
                    splitter.addWidget(child_widget)

            # Set sizes based on ratios
            if node.ratios and len(node.ratios) == splitter.count():
                total = sum(node.ratios)
                sizes = [int(1000 * r / total) for r in node.ratios]
                splitter.setSizes(sizes)

            return splitter

        return None

    # ReconcilerOperations implementation

    def add_pane(self, pane_id: PaneId):
        """Add new pane (widget will be created during rebuild)."""
        # Widget creation happens in _build_widget_tree
        pass

    def remove_pane(self, pane_id: PaneId):
        """Remove pane widget."""
        if pane_id in self._widgets:
            widget = self._widgets[pane_id]
            widget.setParent(None)
            widget.deleteLater()
            del self._widgets[pane_id]

    def set_widget_provider(self, provider: WidgetProvider):
        """Set widget provider."""
        self.provider = provider
        self._update_view()
```

**Tests**:
```python
def test_container_creation(qtbot):
    """Test container widget creation."""
    model = PaneModel(
        root=LeafNode(PaneId("p1"), WidgetId("test"))
    )

    container = PaneContainer(model)
    qtbot.addWidget(container)

    assert container.model == model
    assert len(container._widgets) == 1
```

---

## Validation Criteria

### Phase 1 Complete When:

1. ✅ All type enhancements complete
2. ✅ Node system supports parent references
3. ✅ PaneModel manages tree state
4. ✅ Commands implement execute/undo
5. ✅ Controller manages command execution
6. ✅ Container renders tree using Qt
7. ✅ Widget provider pattern works
8. ✅ All Phase 1 tests passing

### Integration Test:

```python
def test_phase1_integration(qtbot):
    """Test complete Phase 1 functionality."""
    # Create model
    model = PaneModel()

    # Create controller
    controller = PaneController(model)

    # Create container
    container = PaneContainer(model)
    qtbot.addWidget(container)

    # Add initial pane
    leaf = LeafNode(PaneId("p1"), WidgetId("editor:main.py"))
    model.root = leaf
    model._rebuild_registry()

    # Split pane
    controller.split_pane(
        PaneId("p1"),
        WidgetId("terminal:1"),
        WherePosition.BOTTOM
    )

    # Verify structure
    assert isinstance(model.root, SplitNode)
    assert len(model.get_all_pane_ids()) == 2

    # Undo
    controller.undo()
    assert isinstance(model.root, LeafNode)
    assert len(model.get_all_pane_ids()) == 1
```

---

## Task Execution Order

1. P1.1.1 → P1.1.2 (Type enhancements)
2. P1.2.1 (Node enhancements)
3. P1.3.1 (Core model)
4. P1.4.1 → P1.4.2 → P1.4.3 (Commands)
5. P1.5.1 (Controller)
6. P1.6.1 (Container)

Each task should be implemented using TDD:
1. Write tests first
2. Implement functionality
3. Verify tests pass
4. Move to next task

---

## Success Metrics

- All 15+ Phase 1 tests passing
- Widget can display and split panes
- Undo/redo works correctly
- Widget provider pattern functional
- No Qt imports in Model layer
- Commands are atomic and reversible