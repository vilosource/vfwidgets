# MVC Architecture

## Overview

MultiSplit uses a strict Model-View-Controller (MVC) architecture to ensure clean separation of concerns, testability, and maintainability. Each layer has specific responsibilities and enforced boundaries that prevent coupling and enable independent testing.

## Prerequisites

This architecture requires **Phase 0 foundations** to function properly:

- **ID Generation**: Unique, stable identifiers for panes and nodes
- **Signal Bridge**: Connect abstract model signals to Qt signals
- **Geometry Calculator**: Calculate pane positions from tree structure
- **Tree Reconciler**: Efficient diff and update algorithms
- **Transaction Context**: Manage atomic operations

See [MVP Implementation Plan](../../mvp-implementation-PLAN.md#phase-0-critical-foundations-must-have-first) for Phase 0 details.

---

## Layer Responsibilities

### Model Layer (Pure Python)

**What It Manages**
```python
# Tree structure and state
root: PaneNode                    # Binary tree of splits and leaves
focused_pane_id: PaneId           # Current focus
pane_registry: dict[PaneId, Node] # Fast lookup
constraints: dict[PaneId, SizeConstraints]  # Size limits

# Metadata
metadata: dict                    # Session-level data
locked_panes: set[PaneId]        # Locked against changes
```

**What It Does**
- Maintains tree structure invariants
- Validates all operations before applying
- Emits signals for structural changes
- Provides serialization/deserialization
- Calculates derived state (statistics, neighbors)

**What It NEVER Does**
```python
# ❌ FORBIDDEN in Model
from PySide6.QtWidgets import QWidget    # No Qt imports
widget = QLabel("text")                  # No widget creation
layout.addWidget(widget)                 # No layout operations
self.view.update()                       # No view interaction
```

### Controller Layer (Commands Only)

**What It Manages**
```python
# Command execution
undo_stack: list[Command]         # History for undo
redo_stack: list[Command]         # Undone operations
command_validator: Validator      # Pre-execution validation

# Transactions
transaction_stack: list[Command]  # Commands in transaction
in_transaction: bool             # Transaction state
```

**What It Does**
- Executes ALL model mutations via commands
- Manages undo/redo operations
- Provides transaction boundaries
- Validates commands before execution
- Merges compatible commands for efficiency

**What It NEVER Does**
```python
# ❌ FORBIDDEN in Controller
from view import MultiSplitView          # No view imports
model.root = new_node                    # No direct mutation
view.reconcile()                         # No view interaction
widget.setVisible(False)                 # No widget manipulation
```

### View Layer (Qt Integration)

**What It Manages**
```python
# Widget instances and layout
widget_map: dict[PaneId, QWidget]       # Active widgets
widget_containers: dict[PaneId, QWidget] # Widget containers
divider_widgets: list[DividerWidget]    # Split dividers

# Rendering and interaction
render_pipeline: RenderPipeline         # Composable rendering
drag_handler: DragHandler               # Divider dragging
focus_manager: FocusManager             # Focus tracking
```

**What It Does**
- Reconciles Qt layout with model tree
- Handles user input events
- Renders visual elements (focus, selection, errors)
- Manages widget lifecycle with provider
- Coordinates with application via signals

**What It NEVER Does**
```python
# ❌ FORBIDDEN in View
model.root.children.append(node)        # No direct mutation
model.focused_pane_id = "pane-1"       # No model changes
controller.execute_without_undo(cmd)    # No controller bypass
widget = QLabel("created internally")   # No widget creation
```

---

## Strict Import Rules

### Allowed Dependencies

```python
# Model (core/model.py)
# NO imports from other layers - pure Python only

# Controller (controller/controller.py)
from core.model import PaneModel, ModelSignals
from core.nodes import PaneNode, LeafNode, SplitNode
from controller.commands import Command, SplitCommand
# NO imports from view layer

# View (view/container.py)
from core.model import PaneModel  # Read-only access
from core.nodes import PaneNode   # Read-only access
from controller.controller import PaneController
from PySide6.QtWidgets import QWidget
# NO imports that create circular dependencies
```

### Forbidden Dependencies

```python
# ❌ Model cannot import
from PySide6.QtWidgets import *      # No Qt in model
from controller import *             # Model doesn't know controller
from view import *                   # Model doesn't know view

# ❌ Controller cannot import
from view import *                   # Controller doesn't know view
from PySide6.QtWidgets import *      # Controller is Qt-agnostic

# ❌ View cannot import
from controller.commands import *    # View doesn't create commands
```

---

## Signal Architecture

### Model Signals (Abstract)

```python
class ModelSignals:
    """Pure Python signals - no Qt dependency"""

    # Structure changes
    about_to_change = AbstractSignal()      # Before any mutation
    changed = AbstractSignal()              # After mutation complete
    structure_changed = AbstractSignal()    # Tree structure modified
    node_changed = AbstractSignal()         # Specific node updated

    # State changes
    focus_changed = AbstractSignal()        # Focus moved
    selection_changed = AbstractSignal()    # Selection updated
    constraint_changed = AbstractSignal()   # Size constraints modified

    # Validation
    validation_failed = AbstractSignal()    # Invalid operation attempted
```

### Signal Flow

```python
# Required signal order for ALL mutations
def execute_command(self, command: Command):
    # 1. Pre-mutation signal
    self.model.signals.about_to_change.emit()

    # 2. Perform mutation
    result = command.execute(self.model)

    # 3. Post-mutation signals
    self.model.signals.changed.emit()
    if result.structure_changed:
        self.model.signals.structure_changed.emit()
    if result.node_changed:
        self.model.signals.node_changed.emit(result.changed_nodes)
```

### Signal Bridge

```python
class SignalBridge:
    """Bridge abstract model signals to Qt signals"""

    def bridge_to_qt(self, abstract_signal: AbstractSignal, qt_signal):
        """Connect abstract signal to emit Qt signal"""
        abstract_signal.connect(lambda *args: qt_signal.emit(*args))

    def bridge_from_qt(self, qt_signal, abstract_signal: AbstractSignal):
        """Connect Qt signal to emit abstract signal"""
        qt_signal.connect(lambda *args: abstract_signal.emit(*args))
```

---

## Command Pattern Implementation

### Command Interface

```python
class Command(ABC):
    """Base class for all model mutations"""

    @abstractmethod
    def validate(self, model: PaneModel) -> ValidationResult:
        """Check if command can execute"""

    @abstractmethod
    def execute(self, model: PaneModel) -> CommandResult:
        """Apply changes to model"""

    @abstractmethod
    def undo(self, model: PaneModel) -> CommandResult:
        """Reverse changes"""

    @abstractmethod
    def can_merge_with(self, other: Command) -> bool:
        """Check if commands can be merged"""

    @abstractmethod
    def serialize(self) -> dict:
        """Convert to JSON-serializable dict"""
```

### Example Implementation

```python
class SplitCommand(Command):
    """Split a pane into two"""

    def __init__(self, pane_id: PaneId, where: WherePosition,
                 widget_id: WidgetId, ratio: float = 0.5):
        self.pane_id = pane_id
        self.where = where
        self.widget_id = widget_id
        self.ratio = ratio
        self.new_pane_id = None  # Generated during execute

    def validate(self, model: PaneModel) -> ValidationResult:
        """Check preconditions"""
        if not model.find_node(self.pane_id):
            return ValidationResult(False, ["Pane not found"])
        if not (0.1 <= self.ratio <= 0.9):
            return ValidationResult(False, ["Invalid ratio"])
        return ValidationResult(True, [])

    def execute(self, model: PaneModel) -> CommandResult:
        """Split the pane"""
        # Generate stable ID
        self.new_pane_id = model.generate_pane_id()

        # Find target node
        target = model.find_node(self.pane_id)

        # Create new leaf
        new_leaf = LeafNode(self.new_pane_id, self.widget_id)

        # Determine orientation
        orientation = (Orientation.HORIZONTAL if self.where in
                      [WherePosition.LEFT, WherePosition.RIGHT]
                      else Orientation.VERTICAL)

        # Create split
        children = ([target, new_leaf] if self.where in
                   [WherePosition.LEFT, WherePosition.TOP]
                   else [new_leaf, target])
        split = SplitNode(model.generate_node_id(), orientation, children)
        split.ratios = [self.ratio, 1.0 - self.ratio]

        # Replace in tree
        model.replace_node(target, split)

        return CommandResult(
            success=True,
            undo_id=str(uuid.uuid4()),
            changed_panes={self.pane_id, self.new_pane_id},
            structure_changed=True
        )
```

---

## Reconciliation Algorithm

### Tree Diffing

```python
class TreeReconciler:
    """Calculate minimal changes between trees"""

    def diff_trees(self, old_tree: PaneNode, new_tree: PaneNode) -> DiffResult:
        """Compare trees and identify changes"""

        result = DiffResult(
            removed=set(),
            added=set(),
            moved=set(),
            modified=set()
        )

        if old_tree is None and new_tree is None:
            return result

        # Collect all pane IDs from both trees
        old_panes = self._collect_pane_ids(old_tree)
        new_panes = self._collect_pane_ids(new_tree)

        # Calculate set differences
        result.removed = old_panes - new_panes
        result.added = new_panes - old_panes

        # Check for modifications in remaining panes
        for pane_id in old_panes & new_panes:
            old_node = self._find_node(old_tree, pane_id)
            new_node = self._find_node(new_tree, pane_id)

            if self._node_changed(old_node, new_node):
                result.modified.add(pane_id)

        return result
```

### View Reconciliation

```python
class PaneContainer(QWidget):
    """Main view container with reconciliation"""

    def reconcile(self, old_tree: PaneNode, new_tree: PaneNode):
        """Update view to match new tree state"""

        # Disable updates during reconciliation
        self.setUpdatesEnabled(False)
        try:
            # Calculate minimal changes
            diff = self.tree_reconciler.diff_trees(old_tree, new_tree)

            # Remove widgets for deleted panes
            for pane_id in diff.removed:
                self._remove_widget(pane_id)

            # Request widgets for new panes
            for pane_id in diff.added:
                self._request_widget(pane_id, new_tree)

            # Update modified panes
            for pane_id in diff.modified:
                self._update_widget(pane_id, new_tree)

            # Recalculate layout geometry
            self._update_geometry(new_tree)

        finally:
            # Re-enable updates
            self.setUpdatesEnabled(True)
```

---

## Transaction Management

### Transaction Context

```python
class TransactionContext:
    """Context manager for atomic operations"""

    def __init__(self, controller: PaneController):
        self.controller = controller
        self.commands: list[Command] = []

    def __enter__(self):
        self.controller.begin_transaction()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.controller.rollback_transaction()
        else:
            self.controller.commit_transaction()
```

### Usage Example

```python
# Atomic multi-operation
with controller.begin_transaction() as tx:
    controller.execute(SplitCommand(pane_id, WherePosition.RIGHT, widget_id))
    controller.execute(FocusCommand(new_pane_id))
    controller.execute(ResizeCommand(split_id, 0, 0.3))
    # All commands committed together or rolled back on error
```

---

## Validation System

### Validation Levels

```python
class ValidationMode(Enum):
    STRICT = "strict"      # All violations are errors
    PERMISSIVE = "permissive"  # Some violations are warnings
    DISABLED = "disabled"  # No validation (dangerous)
```

### Validation Points

```python
# Model invariant validation
def validate_tree(self, root: PaneNode) -> ValidationResult:
    """Validate entire tree structure"""
    errors = []

    # Check tree structure
    if not self._validate_binary_tree(root):
        errors.append("Tree is not binary")

    # Check ratio constraints
    if not self._validate_ratios(root):
        errors.append("Invalid ratios in tree")

    # Check unique IDs
    if not self._validate_unique_ids(root):
        errors.append("Duplicate pane IDs found")

    return ValidationResult(len(errors) == 0, errors)

# Command validation
def validate_command(self, command: Command) -> ValidationResult:
    """Validate command before execution"""

    # Basic validation
    basic_result = command.validate(self.model)
    if not basic_result.is_valid:
        return basic_result

    # Context validation
    if self.model.is_locked(command.target_pane_id):
        return ValidationResult(False, ["Target pane is locked"])

    return ValidationResult(True, [])
```

---

## Error Handling

### Exception Hierarchy

```python
class PaneError(Exception):
    """Base exception for all pane operations"""

class InvalidStructureError(PaneError):
    """Tree structure is invalid"""

class InvalidOperationError(PaneError):
    """Operation cannot be performed in current state"""

class PaneNotFoundError(PaneError):
    """Specified pane ID does not exist"""

class CommandExecutionError(PaneError):
    """Command failed during execution"""
```

### Error Recovery

```python
class PaneController:
    def execute_command(self, command: Command) -> CommandResult:
        """Execute command with full error handling"""

        try:
            # Validate command
            validation = self.validate_command(command)
            if not validation.is_valid:
                return CommandResult(False, None,
                    ValidationError(validation.messages), set())

            # Begin model transaction
            self.model.signals.about_to_change.emit()

            # Execute command
            result = command.execute(self.model)

            # Validate resulting state
            tree_validation = self.model.validate_tree()
            if not tree_validation.is_valid:
                # Rollback on corruption
                command.undo(self.model)
                raise StateCorruptionError(tree_validation.messages)

            # Commit transaction
            self.model.signals.changed.emit()
            self.undo_stack.append(command)

            return result

        except Exception as e:
            # Ensure clean state on any error
            self._ensure_valid_state()
            return CommandResult(False, None, e, set())
```

---

## Quick Reference

### Layer Boundaries

| Layer | Imports From | Mutates | Signals |
|-------|-------------|---------|---------|
| Model | None | Self only | Emits |
| Controller | Model | Model only | Listens |
| View | Model (read), Controller | None | Bridges |

### Command Lifecycle

1. **Create** → Validate preconditions
2. **Execute** → Apply to model + emit signals
3. **Store** → Add to undo stack
4. **Reconcile** → Update view via signals

### Signal Order

1. `about_to_change` → Before mutation
2. `command.execute()` → Apply changes
3. `changed` → After mutation
4. `structure_changed` → If tree modified
5. `node_changed` → If specific nodes modified

### Validation Checklist

- ✅ All model mutations via commands
- ✅ No Qt imports in model layer
- ✅ No direct model mutations in view
- ✅ Signal order maintained
- ✅ Tree invariants preserved
- ✅ PaneId stability maintained

## Related Documents

- **[Core Concepts](../01-overview/core-concepts.md)** - MVC overview and rationale
- **[Widget Provider](widget-provider.md)** - Provider pattern implementation
- **[Tree Structure](tree-structure.md)** - Tree data structures and operations
- **[MVP Implementation Plan](../../mvp-implementation-PLAN.md)** - Phase 0 foundations
- **[Development Rules](../../development-rules-GUIDE.md)** - MVC enforcement rules

---

This MVC architecture provides the clean separation and testability foundation that makes MultiSplit reliable and maintainable across all development phases.