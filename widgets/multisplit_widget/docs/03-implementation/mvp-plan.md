# MVP Implementation Plan

## Overview

This document provides the complete implementation roadmap for the MultiSplit widget MVP. It consolidates all Phase 0 foundations and implementation details from the authoritative planning document, providing concrete algorithms and code specifications for building a production-ready widget.

## What This Covers

- **Complete Phase 0 algorithms** with implementation details
- **Phase 1-3 component specifications** with code templates
- **Task breakdown structure** for development
- **Validation criteria** for each component
- **Integration testing plan** for MVP completion

## What This Doesn't Cover

- Advanced features beyond MVP scope (defer to Phase 4+ planning)
- Detailed UI theming (covered in [04-design/view-design.md](../04-design/view-design.md))
- Performance optimizations (covered in advanced guides)

---

## Core Philosophy

Build a **complete skeleton** with **minimal meat** - all structural elements in place, but only essential functionality implemented. This ensures we can extend without modification (Open/Closed Principle).

### Critical Success Factors

1. **Phase 0 foundations are MANDATORY** - No skipping allowed
2. **Complete interfaces upfront** - All methods defined, even if raising NotImplementedError
3. **Strict layer separation** - Model testable without Qt
4. **Widget provider pattern** - No internal widget creation
5. **Reconciliation over rebuild** - No flicker, maximum widget reuse

---

## Phase 0: Critical Foundations (MUST HAVE FIRST)

These components provide the algorithmic foundation that makes everything else possible. **ALL must be implemented before Phase 1.**

### 0.1 ID Generation System (`core/utils.py`)

**Purpose**: Generate unique, stable identifiers for all system components.

**Complete Implementation**:
```python
import uuid
from typing import Optional
from core.types import PaneId, NodeId, WidgetId

def generate_pane_id(prefix: str = "pane") -> PaneId:
    """Generate unique pane ID that remains stable across sessions."""
    return PaneId(f"{prefix}_{uuid.uuid4().hex[:8]}")

def generate_node_id(prefix: str = "node") -> NodeId:
    """Generate unique node ID for split nodes."""
    return NodeId(f"{prefix}_{uuid.uuid4().hex[:8]}")

def generate_widget_id(type_hint: str, identifier: str) -> WidgetId:
    """Generate widget ID from type and identifier.

    Args:
        type_hint: Widget type (e.g., 'editor', 'terminal')
        identifier: Unique identifier (e.g., 'main.py', 'session1')

    Returns:
        Formatted widget ID like 'editor:main.py'
    """
    return WidgetId(f"{type_hint}:{identifier}")

def validate_id_format(id_string: str, id_type: str) -> bool:
    """Validate ID format is correct for the given type."""
    if id_type == "widget":
        return ":" in id_string and len(id_string.split(":")) == 2
    elif id_type in ["pane", "node"]:
        parts = id_string.split("_")
        return len(parts) == 2 and len(parts[1]) == 8
    return False
```

**Success Criteria**:
- ✅ Generates unique IDs across process restarts
- ✅ IDs remain stable during serialization/deserialization
- ✅ Widget IDs are opaque to MultiSplit
- ✅ All validation functions work correctly

### 0.2 Tree Utilities (`core/tree_utils.py`)

**Purpose**: Core tree manipulation and validation utilities.

**Complete Implementation**:
```python
from typing import Optional, List
from core.types import PaneId, Ratio
from core.nodes import PaneNode, LeafNode, SplitNode
from core.exceptions import InvalidStructureError

def normalize_ratios(ratios: List[float]) -> List[float]:
    """Ensure ratios sum to 1.0, handling edge cases."""
    if not ratios:
        return []

    total = sum(ratios)
    if total == 0:
        # Equal distribution for zero ratios
        equal_ratio = 1.0 / len(ratios)
        return [equal_ratio] * len(ratios)

    # Normalize to sum to 1.0
    normalized = [r / total for r in ratios]

    # Handle floating point precision issues
    diff = 1.0 - sum(normalized)
    if abs(diff) > 1e-10:
        normalized[-1] += diff

    return normalized

def validate_ratios(ratios: List[float], tolerance: float = 0.01) -> bool:
    """Check if ratios are valid (sum to 1.0 within tolerance)."""
    if not ratios:
        return False

    total = sum(ratios)
    return abs(total - 1.0) <= tolerance and all(r >= 0 for r in ratios)

def find_node_by_id(root: PaneNode, pane_id: PaneId) -> Optional[PaneNode]:
    """Find node in tree by ID using visitor pattern."""
    class NodeFinder:
        def __init__(self, target_id: PaneId):
            self.target_id = target_id
            self.found_node = None

        def visit_leaf(self, node: LeafNode):
            if node.pane_id == self.target_id:
                self.found_node = node

        def visit_split(self, node: SplitNode):
            if hasattr(node, 'pane_id') and node.pane_id == self.target_id:
                self.found_node = node
            else:
                for child in node.children:
                    if self.found_node is None:
                        child.accept(self)

    finder = NodeFinder(pane_id)
    root.accept(finder)
    return finder.found_node

def get_all_leaves(root: PaneNode) -> List[LeafNode]:
    """Get all leaf nodes in tree."""
    class LeafCollector:
        def __init__(self):
            self.leaves = []

        def visit_leaf(self, node: LeafNode):
            self.leaves.append(node)

        def visit_split(self, node: SplitNode):
            for child in node.children:
                child.accept(self)

    collector = LeafCollector()
    root.accept(collector)
    return collector.leaves

def get_tree_depth(root: PaneNode) -> int:
    """Calculate maximum tree depth."""
    class DepthCalculator:
        def visit_leaf(self, node: LeafNode) -> int:
            return 1

        def visit_split(self, node: SplitNode) -> int:
            if not node.children:
                return 1
            return 1 + max(child.accept(self) for child in node.children)

    calculator = DepthCalculator()
    return root.accept(calculator)

def validate_tree_structure(root: PaneNode) -> bool:
    """Validate tree structure invariants."""
    class StructureValidator:
        def __init__(self):
            self.is_valid = True
            self.errors = []

        def visit_leaf(self, node: LeafNode):
            if not node.pane_id:
                self.is_valid = False
                self.errors.append("Leaf node missing pane_id")

        def visit_split(self, node: SplitNode):
            if len(node.children) < 2:
                self.is_valid = False
                self.errors.append(f"Split node has {len(node.children)} children (minimum 2)")

            if len(node.ratios) != len(node.children):
                self.is_valid = False
                self.errors.append("Ratio count doesn't match child count")

            if not validate_ratios(node.ratios):
                self.is_valid = False
                self.errors.append("Invalid ratios in split node")

            for child in node.children:
                child.accept(self)

    validator = StructureValidator()
    root.accept(validator)
    return validator.is_valid
```

**Success Criteria**:
- ✅ Ratio normalization handles all edge cases
- ✅ Tree traversal works for any valid tree
- ✅ Validation catches all structural violations
- ✅ All operations preserve tree invariants

### 0.3 Signal Bridge (`core/signal_bridge.py`)

**Purpose**: Bridge between abstract model signals and Qt signals.

**Complete Implementation**:
```python
from typing import Protocol, Callable, Any, List
import weakref

class AbstractSignal:
    """Pure Python signal implementation with no Qt dependencies."""

    def __init__(self):
        # Use weak references to prevent memory leaks
        self._handlers: List[weakref.ref] = []

    def connect(self, handler: Callable):
        """Connect a handler to this signal."""
        if not callable(handler):
            raise ValueError("Handler must be callable")

        # Store weak reference to handler
        self._handlers.append(weakref.ref(handler))

    def disconnect(self, handler: Callable):
        """Disconnect a handler from this signal."""
        # Find and remove the handler's weak reference
        to_remove = []
        for weak_handler in self._handlers:
            if weak_handler() is handler:
                to_remove.append(weak_handler)

        for weak_handler in to_remove:
            self._handlers.remove(weak_handler)

    def emit(self, *args, **kwargs):
        """Emit signal to all connected handlers."""
        # Clean up dead weak references and call live handlers
        alive_handlers = []
        for weak_handler in self._handlers:
            handler = weak_handler()
            if handler is not None:
                alive_handlers.append(weak_handler)
                try:
                    handler(*args, **kwargs)
                except Exception as e:
                    # Log error but don't break other handlers
                    print(f"Signal handler error: {e}")

        # Update handler list to remove dead references
        self._handlers = alive_handlers

    def clear(self):
        """Remove all handlers."""
        self._handlers.clear()

class SignalBridge:
    """Bridge abstract signals to Qt signals for View layer."""

    def __init__(self):
        self._bridges = []

    def bridge_to_qt(self, abstract_signal: AbstractSignal, qt_signal):
        """Connect abstract signal to emit Qt signal."""
        def relay(*args):
            qt_signal.emit(*args)

        abstract_signal.connect(relay)
        self._bridges.append((abstract_signal, qt_signal, relay))

    def bridge_from_qt(self, qt_signal, abstract_signal: AbstractSignal):
        """Connect Qt signal to emit abstract signal."""
        def relay(*args):
            abstract_signal.emit(*args)

        qt_signal.connect(relay)
        self._bridges.append((qt_signal, abstract_signal, relay))

    def disconnect_all(self):
        """Disconnect all bridges."""
        for bridge in self._bridges:
            if len(bridge) == 3:
                source, target, relay = bridge
                try:
                    if hasattr(source, 'disconnect'):
                        source.disconnect(relay)
                except:
                    pass  # Ignore disconnect errors during cleanup
        self._bridges.clear()
```

**Success Criteria**:
- ✅ Abstract signals work without Qt imports
- ✅ Memory leaks prevented with weak references
- ✅ Qt signal bridging works bidirectionally
- ✅ Error handling doesn't break signal emission

### 0.4 Geometry Calculator (`core/geometry.py`)

**Purpose**: Calculate exact pixel positions for all panes from tree structure.

**Complete Implementation**:
```python
from typing import Dict
from core.types import PaneId, Bounds, Orientation
from core.nodes import PaneNode, LeafNode, SplitNode

class GeometryCalculator:
    """Calculate pane positions from tree structure."""

    def __init__(self, divider_width: int = 4):
        self.divider_width = divider_width

    def calculate(self, root: PaneNode, container_bounds: Bounds) -> Dict[PaneId, Bounds]:
        """Calculate all pane positions within container bounds.

        Args:
            root: Root node of pane tree
            container_bounds: Available space for layout

        Returns:
            Dictionary mapping pane IDs to their bounds
        """
        if root is None:
            return {}

        result = {}
        self._calculate_recursive(root, container_bounds, result)
        return result

    def _calculate_recursive(self, node: PaneNode, bounds: Bounds,
                           result: Dict[PaneId, Bounds]):
        """Recursively calculate bounds for tree nodes."""
        if isinstance(node, LeafNode):
            # Leaf nodes get the full bounds
            result[node.pane_id] = bounds

        elif isinstance(node, SplitNode):
            # Split nodes divide space among children
            child_bounds = self._split_bounds(
                bounds,
                node.orientation,
                node.ratios,
                len(node.children)
            )

            # Recursively calculate for each child
            for child, child_bound in zip(node.children, child_bounds):
                self._calculate_recursive(child, child_bound, result)

    def _split_bounds(self, bounds: Bounds, orientation: Orientation,
                     ratios: List[float], child_count: int) -> List[Bounds]:
        """Split bounds according to orientation and ratios."""
        if child_count == 0:
            return []

        if child_count == 1:
            return [bounds]

        # Calculate space for dividers
        total_divider_space = (child_count - 1) * self.divider_width

        if orientation == Orientation.HORIZONTAL:
            # Split horizontally (side by side)
            available_width = bounds.width - total_divider_space
            if available_width <= 0:
                # Not enough space - give minimal bounds
                return [Bounds(bounds.x, bounds.y, 1, bounds.height)] * child_count

            child_bounds = []
            current_x = bounds.x

            for i, ratio in enumerate(ratios):
                child_width = int(available_width * ratio)

                # Last child gets remaining space to handle rounding
                if i == len(ratios) - 1:
                    child_width = bounds.x + bounds.width - current_x

                child_bounds.append(Bounds(
                    current_x, bounds.y,
                    child_width, bounds.height
                ))

                current_x += child_width + self.divider_width

            return child_bounds

        else:  # VERTICAL
            # Split vertically (stacked)
            available_height = bounds.height - total_divider_space
            if available_height <= 0:
                # Not enough space - give minimal bounds
                return [Bounds(bounds.x, bounds.y, bounds.width, 1)] * child_count

            child_bounds = []
            current_y = bounds.y

            for i, ratio in enumerate(ratios):
                child_height = int(available_height * ratio)

                # Last child gets remaining space to handle rounding
                if i == len(ratios) - 1:
                    child_height = bounds.y + bounds.height - current_y

                child_bounds.append(Bounds(
                    bounds.x, current_y,
                    bounds.width, child_height
                ))

                current_y += child_height + self.divider_width

            return child_bounds

    def calculate_divider_bounds(self, root: PaneNode, container_bounds: Bounds) -> List[Bounds]:
        """Calculate bounds for all dividers in the tree."""
        dividers = []
        self._collect_divider_bounds(root, container_bounds, dividers)
        return dividers

    def _collect_divider_bounds(self, node: PaneNode, bounds: Bounds,
                               dividers: List[Bounds]):
        """Collect divider bounds recursively."""
        if isinstance(node, SplitNode) and len(node.children) > 1:
            child_bounds = self._split_bounds(
                bounds, node.orientation, node.ratios, len(node.children)
            )

            # Add dividers between children
            for i in range(len(child_bounds) - 1):
                current_bounds = child_bounds[i]
                next_bounds = child_bounds[i + 1]

                if node.orientation == Orientation.HORIZONTAL:
                    # Vertical divider between horizontal children
                    divider_x = current_bounds.x + current_bounds.width
                    dividers.append(Bounds(
                        divider_x, bounds.y,
                        self.divider_width, bounds.height
                    ))
                else:
                    # Horizontal divider between vertical children
                    divider_y = current_bounds.y + current_bounds.height
                    dividers.append(Bounds(
                        bounds.x, divider_y,
                        bounds.width, self.divider_width
                    ))

            # Recursively process children
            for child, child_bound in zip(node.children, child_bounds):
                self._collect_divider_bounds(child, child_bound, dividers)
```

**Success Criteria**:
- ✅ Pixel-perfect calculations with no gaps or overlaps
- ✅ Handles floating-point precision issues
- ✅ Works correctly with minimum size constraints
- ✅ Divider positioning is accurate

### 0.5 Tree Reconciler (`view/tree_reconciler.py`)

**Purpose**: Calculate minimal differences between tree states for efficient updates.

**Complete Implementation**:
```python
from typing import Optional, Set, Dict, Any
from dataclasses import dataclass
from core.types import PaneId
from core.nodes import PaneNode, LeafNode, SplitNode

@dataclass
class DiffResult:
    """Result of tree diff operation."""
    removed: Set[PaneId]
    added: Set[PaneId]
    moved: Set[PaneId]
    modified: Set[PaneId]

    def has_changes(self) -> bool:
        """Check if any changes exist."""
        return bool(self.removed or self.added or self.moved or self.modified)

class TreeReconciler:
    """Calculate minimal diff between tree states."""

    def diff_trees(self, old_tree: Optional[PaneNode],
                  new_tree: Optional[PaneNode]) -> DiffResult:
        """Calculate differences between two trees.

        This is the core algorithm that enables flicker-free updates
        by determining exactly what widgets need to be added, removed,
        or repositioned.
        """
        result = DiffResult(
            removed=set(),
            added=set(),
            moved=set(),
            modified=set()
        )

        if old_tree is None and new_tree is None:
            return result

        if old_tree is None:
            # Everything is new
            self._collect_all_panes(new_tree, result.added)
            return result

        if new_tree is None:
            # Everything is removed
            self._collect_all_panes(old_tree, result.removed)
            return result

        # Compare trees to find differences
        old_panes = self._build_pane_map(old_tree)
        new_panes = self._build_pane_map(new_tree)

        # Find removed panes
        result.removed = set(old_panes.keys()) - set(new_panes.keys())

        # Find added panes
        result.added = set(new_panes.keys()) - set(old_panes.keys())

        # Find modified panes (same ID but different properties)
        common_panes = set(old_panes.keys()) & set(new_panes.keys())
        for pane_id in common_panes:
            old_node = old_panes[pane_id]
            new_node = new_panes[pane_id]

            if self._nodes_differ(old_node, new_node):
                result.modified.add(pane_id)

        return result

    def _collect_all_panes(self, root: PaneNode, pane_set: Set[PaneId]):
        """Collect all pane IDs from a tree."""
        class PaneCollector:
            def __init__(self, pane_set: Set[PaneId]):
                self.pane_set = pane_set

            def visit_leaf(self, node: LeafNode):
                self.pane_set.add(node.pane_id)

            def visit_split(self, node: SplitNode):
                for child in node.children:
                    child.accept(self)

        collector = PaneCollector(pane_set)
        root.accept(collector)

    def _build_pane_map(self, root: PaneNode) -> Dict[PaneId, PaneNode]:
        """Build a map of pane ID to node for efficient lookup."""
        pane_map = {}

        class MapBuilder:
            def visit_leaf(self, node: LeafNode):
                pane_map[node.pane_id] = node

            def visit_split(self, node: SplitNode):
                for child in node.children:
                    child.accept(self)

        builder = MapBuilder()
        root.accept(builder)
        return pane_map

    def _nodes_differ(self, old_node: PaneNode, new_node: PaneNode) -> bool:
        """Check if two nodes are meaningfully different."""
        # Different types means different
        if type(old_node) != type(new_node):
            return True

        if isinstance(old_node, LeafNode):
            # For leaves, check widget ID and constraints
            return (old_node.widget_id != new_node.widget_id or
                   old_node.constraints != new_node.constraints)

        elif isinstance(old_node, SplitNode):
            # For splits, check orientation, ratios, and child count
            return (old_node.orientation != new_node.orientation or
                   old_node.ratios != new_node.ratios or
                   len(old_node.children) != len(new_node.children))

        return False
```

**Success Criteria**:
- ✅ Correctly identifies minimal change set
- ✅ Handles all tree transformation cases
- ✅ Preserves maximum number of existing widgets
- ✅ No false positives in difference detection

### 0.6 Transaction Context (`controller/transaction.py`)

**Purpose**: Manage atomic operations and rollback capabilities.

**Complete Implementation**:
```python
from typing import List, Optional
from contextlib import contextmanager
from core.exceptions import CommandExecutionError

class TransactionContext:
    """Context manager for atomic command transactions."""

    def __init__(self, controller: 'PaneController'):
        self.controller = controller
        self.commands: List['Command'] = []
        self.rolled_back = False
        self.committed = False

    def __enter__(self):
        """Begin transaction context."""
        self.controller._begin_transaction()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End transaction context."""
        if exc_type or self.rolled_back:
            # Exception occurred or manual rollback
            self.controller._rollback_transaction()
            return False  # Don't suppress exception
        else:
            # Successful completion
            self.controller._commit_transaction()
            return False

    def add_command(self, command: 'Command'):
        """Add command to transaction."""
        self.commands.append(command)

    def rollback(self):
        """Mark transaction for rollback."""
        self.rolled_back = True

@contextmanager
def transaction(controller: 'PaneController'):
    """Convenience context manager for transactions."""
    context = TransactionContext(controller)
    try:
        with context:
            yield context
    except Exception:
        context.rollback()
        raise
```

**Success Criteria**:
- ✅ Atomic operations work correctly
- ✅ Rollback restores exact previous state
- ✅ Exception handling preserves integrity
- ✅ Nested transactions are handled properly

---

## Phase 1: Working Core (MUST HAVE)

With Phase 0 foundations in place, implement the minimal working system.

### 1.1 Complete Type System (`core/types.py`)

**All fundamental types and enums**:
```python
from typing import NewType
from enum import Enum
from dataclasses import dataclass

# Type aliases for type safety
PaneId = NewType('PaneId', str)
WidgetId = NewType('WidgetId', str)
NodeId = NewType('NodeId', str)
Ratio = float  # 0.0-1.0 with validation

# Core enums
class Orientation(Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"

class WherePosition(Enum):
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"
    BEFORE = "before"
    AFTER = "after"
    REPLACE = "replace"

class Direction(Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"

# Data structures
@dataclass
class Bounds:
    x: int
    y: int
    width: int
    height: int

    def contains_point(self, x: int, y: int) -> bool:
        return (self.x <= x <= self.x + self.width and
                self.y <= y <= self.y + self.height)

@dataclass
class SizeConstraints:
    min_width: int = 50
    min_height: int = 50
    max_width: Optional[int] = None
    max_height: Optional[int] = None
    min_ratio: float = 0.1
    max_ratio: float = 0.9
```

### 1.2 Node System (`core/nodes.py`)

**Complete node hierarchy**:
```python
from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict
from core.types import PaneId, NodeId, WidgetId, Orientation, SizeConstraints

class PaneNode(ABC):
    """Abstract base for all tree nodes."""

    @abstractmethod
    def accept(self, visitor) -> Any:
        """Visitor pattern support."""
        pass

    @abstractmethod
    def clone(self) -> 'PaneNode':
        """Deep clone of node."""
        pass

    @abstractmethod
    def validate(self) -> bool:
        """Validate node structure."""
        pass

class LeafNode(PaneNode):
    """Leaf node containing a widget reference."""

    def __init__(self, pane_id: PaneId, widget_id: WidgetId,
                 constraints: Optional[SizeConstraints] = None):
        self.pane_id = pane_id
        self.widget_id = widget_id
        self.constraints = constraints or SizeConstraints()

    def accept(self, visitor) -> Any:
        return visitor.visit_leaf(self)

    def clone(self) -> 'LeafNode':
        return LeafNode(
            self.pane_id,
            self.widget_id,
            self.constraints
        )

    def validate(self) -> bool:
        return bool(self.pane_id and self.widget_id)

class SplitNode(PaneNode):
    """Split node containing child nodes."""

    def __init__(self, node_id: NodeId, orientation: Orientation,
                 children: List[PaneNode], ratios: Optional[List[float]] = None):
        self.node_id = node_id
        self.orientation = orientation
        self.children = children
        self.ratios = ratios or self._equal_ratios(len(children))

    def accept(self, visitor) -> Any:
        return visitor.visit_split(self)

    def clone(self) -> 'SplitNode':
        return SplitNode(
            self.node_id,
            self.orientation,
            [child.clone() for child in self.children],
            self.ratios.copy()
        )

    def validate(self) -> bool:
        return (len(self.children) >= 2 and
                len(self.ratios) == len(self.children) and
                abs(sum(self.ratios) - 1.0) < 0.01 and
                all(child.validate() for child in self.children))

    def _equal_ratios(self, count: int) -> List[float]:
        return [1.0 / count] * count if count > 0 else []
```

### 1.3 Core Commands

**Implement the four essential commands**:

#### Split Command (`controller/commands/split_command.py`)
```python
from core.commands import Command, CommandResult
from core.types import PaneId, WidgetId, WherePosition, Orientation
from core.nodes import LeafNode, SplitNode

class SplitCommand(Command):
    """Split a pane to add a new widget."""

    def __init__(self, pane_id: PaneId, where: WherePosition,
                 widget_id: WidgetId, ratio: float = 0.5):
        self.pane_id = pane_id
        self.where = where
        self.widget_id = widget_id
        self.ratio = ratio
        self.undo_data = None

    def validate(self, model) -> bool:
        """Check if split is possible."""
        node = model.find_node(self.pane_id)
        return (node is not None and
                isinstance(node, LeafNode) and
                0.1 <= self.ratio <= 0.9)

    def execute(self, model) -> CommandResult:
        """Perform the split operation."""
        # Find the target node
        target_node = model.find_node(self.pane_id)
        parent = model.find_parent(self.pane_id)

        # Store undo data
        self.undo_data = {
            'target_node': target_node.clone(),
            'parent': parent,
            'parent_index': parent.children.index(target_node) if parent else None
        }

        # Create new leaf for the new widget
        new_pane_id = generate_pane_id()
        new_leaf = LeafNode(new_pane_id, self.widget_id)

        # Determine orientation and order
        orientation = (Orientation.HORIZONTAL if self.where in [WherePosition.LEFT, WherePosition.RIGHT]
                      else Orientation.VERTICAL)

        if self.where in [WherePosition.LEFT, WherePosition.TOP, WherePosition.BEFORE]:
            children = [new_leaf, target_node]
            ratios = [self.ratio, 1.0 - self.ratio]
        else:
            children = [target_node, new_leaf]
            ratios = [1.0 - self.ratio, self.ratio]

        # Create new split node
        split_id = generate_node_id()
        split_node = SplitNode(split_id, orientation, children, ratios)

        # Replace target node with split node
        if parent:
            parent_index = parent.children.index(target_node)
            parent.children[parent_index] = split_node
        else:
            model.root = split_node

        # Update registries
        model.pane_registry[new_pane_id] = new_leaf

        return CommandResult(success=True, changed_panes={self.pane_id, new_pane_id})

    def undo(self, model) -> CommandResult:
        """Reverse the split operation."""
        # Implementation details...
        pass
```

#### Close Command (`controller/commands/close_command.py`)
```python
class CloseCommand(Command):
    """Close a pane and merge with sibling."""

    def __init__(self, pane_id: PaneId):
        self.pane_id = pane_id
        self.undo_data = None

    def validate(self, model) -> bool:
        """Check if close is possible."""
        if model.pane_count <= 1:
            return False  # Can't close last pane

        node = model.find_node(self.pane_id)
        parent = model.find_parent(self.pane_id)
        return node is not None and parent is not None

    def execute(self, model) -> CommandResult:
        """Close the pane and merge parent with sibling."""
        # Store undo data and perform closure
        # Implementation details...
        pass
```

### 1.4 Basic Controller (`controller/controller.py`)

**Core command execution and undo/redo**:
```python
class PaneController:
    """Controller coordinates model and view."""

    def __init__(self, model):
        self.model = model
        self.undo_stack = []
        self.redo_stack = []
        self.in_transaction = False
        self.transaction_commands = []

    def execute_command(self, command: Command) -> CommandResult:
        """Execute a command with validation and undo support."""
        # Validate command
        if not command.validate(self.model):
            return CommandResult(success=False, error="Validation failed")

        # Execute
        self.model.signals.about_to_change.emit()
        result = command.execute(self.model)

        if result.success:
            # Add to undo stack
            self.undo_stack.append(command)
            self.redo_stack.clear()

            # Emit change signals
            self.model.signals.changed.emit()
            if result.changed_panes:
                self.model.signals.structure_changed.emit()

        return result

    def undo(self) -> bool:
        """Undo last command."""
        if not self.undo_stack:
            return False

        command = self.undo_stack.pop()
        self.model.signals.about_to_change.emit()
        result = command.undo(self.model)

        if result.success:
            self.redo_stack.append(command)
            self.model.signals.changed.emit()

        return result.success

    def redo(self) -> bool:
        """Redo last undone command."""
        if not self.redo_stack:
            return False

        command = self.redo_stack.pop()
        return self.execute_command(command).success
```

### 1.5 Basic Container (`view/container.py`)

**Core view with reconciliation**:
```python
class PaneContainer(QWidget):
    """Main view container with reconciliation."""

    def __init__(self, model, controller):
        super().__init__()
        self.model = model
        self.controller = controller
        self.widget_map = {}  # PaneId -> QWidget
        self.current_tree = None

        # Setup reconciliation
        self.reconciler = TreeReconciler()
        self.geometry_calc = GeometryCalculator()

        # Connect signals
        self.model.signals.structure_changed.connect(self.on_structure_changed)

    def on_structure_changed(self):
        """Handle model changes through reconciliation."""
        old_tree = self.current_tree
        new_tree = self.model.root

        # Calculate diff
        diff = self.reconciler.diff_trees(old_tree, new_tree)

        # Apply changes atomically
        self.setUpdatesEnabled(False)
        try:
            self._apply_diff(diff)
            self._update_geometry()
            self.current_tree = new_tree.clone() if new_tree else None
        finally:
            self.setUpdatesEnabled(True)

    def _apply_diff(self, diff: DiffResult):
        """Apply reconciliation changes."""
        # Remove widgets
        for pane_id in diff.removed:
            self._remove_widget(pane_id)

        # Add widgets
        for pane_id in diff.added:
            self._add_widget(pane_id)

        # Update modified widgets
        for pane_id in diff.modified:
            self._update_widget(pane_id)
```

**Success Criteria for Phase 1**:
- ✅ Can create root widget
- ✅ Can split panes horizontally/vertically
- ✅ Can close panes
- ✅ Focus tracking works
- ✅ Undo/redo works for basic operations
- ✅ No flicker during updates
- ✅ All MVC rules followed

---

## Phase 2: Essential Interactions

### 2.1 Focus Management
- Visual focus indicators
- Keyboard navigation (tab, shift+tab)
- Directional navigation (arrow keys)
- Focus follows operations

### 2.2 Divider Dragging
- Hit testing for dividers
- Drag preview and constraints
- Resize command execution
- Visual feedback

### 2.3 Persistence
- Layout serialization/deserialization
- Widget state coordination with provider
- Session restoration

**Success Criteria for Phase 2**:
- ✅ Focus indicators visible and accurate
- ✅ Keyboard navigation works in all directions
- ✅ Dividers can be dragged smoothly
- ✅ Layout saves and restores correctly

---

## Phase 3: Polish

### 3.1 Visual Polish
- Hover states for dividers
- Smooth transitions (optional)
- Error state indicators

### 3.2 Validation System
- Real-time constraint checking
- User feedback for invalid operations
- Graceful error recovery

### 3.3 Size Constraints
- Minimum pane sizes
- Constraint propagation
- Resize boundary enforcement

**Success Criteria for Phase 3**:
- ✅ All interactions feel polished
- ✅ Invalid operations are prevented/explained
- ✅ Size constraints work correctly
- ✅ No unexpected behavior in edge cases

---

## Common Pitfalls

### Pitfall 1: Skipping Phase 0
**Problem**: Attempting to implement Phase 1 without Phase 0 foundations.
**Symptom**: Reconciliation doesn't work, geometry calculations fail.
**Solution**: Complete ALL Phase 0 components before proceeding.

### Pitfall 2: Breaking MVC Rules
**Problem**: Direct model mutation from view, Qt imports in model.
**Symptom**: Tests fail, coupling increases, hard to maintain.
**Solution**: Strict layer validation, automated rule checking.

### Pitfall 3: Widget Creation in MultiSplit
**Problem**: Creating widgets internally instead of using provider.
**Symptom**: Tight coupling, hard to test, no flexibility.
**Solution**: Always emit widget_needed signal, never instantiate widgets.

### Pitfall 4: Rebuild Instead of Reconcile
**Problem**: Clearing all widgets and rebuilding from scratch.
**Symptom**: Flicker, performance issues, lost widget state.
**Solution**: Always use tree reconciler, preserve existing widgets.

### Pitfall 5: Incomplete Undo Support
**Problem**: Commands that can't be properly undone.
**Symptom**: Undo stack corruption, inconsistent state.
**Solution**: Store complete undo data, test round-trip operations.

---

## Validation Checklist

### Phase 0 Complete
- [ ] All ID generation functions work correctly
- [ ] Tree utilities handle all edge cases
- [ ] Signal bridge works without Qt in model
- [ ] Geometry calculator produces pixel-perfect layouts
- [ ] Tree reconciler minimizes widget recreation
- [ ] Transaction context provides atomicity

### Phase 1 Complete
- [ ] Type system covers all use cases
- [ ] Node hierarchy validates correctly
- [ ] Split command works in all directions
- [ ] Close command preserves tree structure
- [ ] Controller enforces command pattern
- [ ] Container reconciles without flicker

### Phase 2 Complete
- [ ] Focus indicators are visible and accurate
- [ ] Keyboard navigation works spatially
- [ ] Divider dragging feels responsive
- [ ] Persistence preserves all state

### Phase 3 Complete
- [ ] Visual polish is consistent
- [ ] Validation prevents all invalid operations
- [ ] Size constraints are enforced
- [ ] Error handling is graceful

### Integration Testing
- [ ] All operations can be undone/redone
- [ ] No memory leaks during extensive use
- [ ] Performance acceptable for 50+ panes
- [ ] Works correctly with various widget types
- [ ] State consistency maintained across all operations

---

## Related Documents

- [Development Protocol](development-protocol.md) - How to execute this plan
- [Development Rules](development-rules.md) - Critical rules to follow
- [MVC Architecture](../02-architecture/mvc-architecture.md) - Layer specifications
- [Widget Provider](../02-architecture/widget-provider.md) - Provider pattern details
- [Tree Structure](../02-architecture/tree-structure.md) - Layout system design

---

## Quick Reference

### Phase Order (STRICT)
```
Phase 0 → Phase 1 → Phase 2 → Phase 3
(No skipping allowed)
```

### Success Definition
```
MVP = All Phase 0-3 complete + All validation criteria met + All integration tests pass
```

### Key Metrics
- **Model tests**: Must run without Qt imports
- **Reconciliation**: < 16ms for typical operations
- **Memory**: No leaks during 1000+ operations
- **Compatibility**: Works with any QWidget subclass

This plan provides the complete roadmap for building a production-ready MultiSplit widget that can be extended without modification.