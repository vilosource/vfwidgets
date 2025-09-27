# Phase 0 Implementation Tasks

## Overview

This document contains detailed, self-contained tasks for implementing Phase 0 foundations of the MultiSplit widget. Each task includes all information needed for implementation without requiring additional context.

## Task Structure

Each task contains:
- **Task ID**: Unique identifier for tracking
- **Title**: Clear, actionable description
- **Dependencies**: Required prior tasks
- **Files**: Exact file paths to create/modify
- **Implementation**: Complete code specification
- **Validation**: How to verify correctness
- **Tests**: Required unit tests

---

## P0.1: ID Generation System

### Task P0.1.1: Enhance Type System
**Title**: Add NodeId and WidgetId types to core/types.py
**Dependencies**: None
**File**: `src/vfwidgets_multisplit/core/types.py`

**Implementation**:
Add after existing PaneId definition (line 15):
```python
NodeId = NewType('NodeId', str)
WidgetId = NewType('WidgetId', str)
```

**Validation**:
- Types are importable: `from core.types import NodeId, WidgetId`
- Types are distinct from str in type checking

---

### Task P0.1.2: Create ID Generation Module
**Title**: Create core/utils.py with ID generation functions
**Dependencies**: P0.1.1
**File**: `src/vfwidgets_multisplit/core/utils.py`

**Implementation**:
```python
"""Utility functions for MultiSplit widget.

Pure Python utilities with no Qt dependencies.
"""

import uuid
from typing import Optional
from .types import PaneId, NodeId, WidgetId


def generate_pane_id(prefix: str = "pane") -> PaneId:
    """Generate unique pane ID that remains stable across sessions.

    Args:
        prefix: Optional prefix for the ID

    Returns:
        Unique PaneId like 'pane_a3f2b8c1'
    """
    return PaneId(f"{prefix}_{uuid.uuid4().hex[:8]}")


def generate_node_id(prefix: str = "node") -> NodeId:
    """Generate unique node ID for split nodes.

    Args:
        prefix: Optional prefix for the ID

    Returns:
        Unique NodeId like 'node_5d7e9a2f'
    """
    return NodeId(f"{prefix}_{uuid.uuid4().hex[:8]}")


def generate_widget_id(type_hint: str, identifier: str) -> WidgetId:
    """Generate widget ID from type and identifier.

    Args:
        type_hint: Widget type (e.g., 'editor', 'terminal')
        identifier: Unique identifier (e.g., 'main.py', 'session1')

    Returns:
        Formatted WidgetId like 'editor:main.py'
    """
    return WidgetId(f"{type_hint}:{identifier}")
```

**Validation**:
- Functions generate unique IDs on each call
- IDs follow expected format patterns
- No Qt imports in file

---

### Task P0.1.3: Add ID Validation Functions
**Title**: Add ID format validation to core/utils.py
**Dependencies**: P0.1.2
**File**: `src/vfwidgets_multisplit/core/utils.py`

**Implementation**:
Add to existing file:
```python
def validate_id_format(id_string: str, id_type: str) -> bool:
    """Validate ID format is correct for the given type.

    Args:
        id_string: ID string to validate
        id_type: Type of ID ('pane', 'node', 'widget')

    Returns:
        True if format is valid
    """
    if not id_string:
        return False

    if id_type == "widget":
        # Widget IDs must have format "type:identifier"
        parts = id_string.split(":")
        return len(parts) == 2 and all(parts)
    elif id_type in ["pane", "node"]:
        # Pane/node IDs must have format "prefix_8hexchars"
        parts = id_string.split("_")
        if len(parts) != 2:
            return False
        prefix, hex_part = parts
        return len(hex_part) == 8 and all(c in '0123456789abcdef' for c in hex_part)
    return False


def parse_widget_id(widget_id: WidgetId) -> tuple[str, str]:
    """Parse widget ID into type and identifier.

    Args:
        widget_id: Widget ID to parse

    Returns:
        Tuple of (type_hint, identifier)

    Raises:
        ValueError: If widget_id format is invalid
    """
    if not validate_id_format(str(widget_id), "widget"):
        raise ValueError(f"Invalid widget ID format: {widget_id}")

    type_hint, identifier = str(widget_id).split(":", 1)
    return type_hint, identifier
```

**Validation**:
- `validate_id_format("pane_12345678", "pane")` returns True
- `validate_id_format("editor:main.py", "widget")` returns True
- `validate_id_format("invalid", "pane")` returns False

---

### Task P0.1.4: Create ID Tests
**Title**: Write comprehensive tests for ID generation
**Dependencies**: P0.1.1, P0.1.2, P0.1.3
**File**: `tests/test_id_generation.py`

**Implementation**:
```python
"""Tests for ID generation system."""

import unittest
from vfwidgets_multisplit.core.types import PaneId, NodeId, WidgetId
from vfwidgets_multisplit.core.utils import (
    generate_pane_id,
    generate_node_id,
    generate_widget_id,
    validate_id_format,
    parse_widget_id
)


class TestIDGeneration(unittest.TestCase):
    """Test ID generation functions."""

    def test_pane_id_generation(self):
        """Test pane ID generation."""
        id1 = generate_pane_id()
        id2 = generate_pane_id()

        # IDs should be unique
        self.assertNotEqual(id1, id2)

        # IDs should follow format
        self.assertTrue(validate_id_format(str(id1), "pane"))
        self.assertTrue(str(id1).startswith("pane_"))

    def test_node_id_generation(self):
        """Test node ID generation."""
        id1 = generate_node_id()
        id2 = generate_node_id()

        self.assertNotEqual(id1, id2)
        self.assertTrue(validate_id_format(str(id1), "node"))

    def test_widget_id_generation(self):
        """Test widget ID generation."""
        widget_id = generate_widget_id("editor", "main.py")

        self.assertEqual(str(widget_id), "editor:main.py")
        self.assertTrue(validate_id_format(str(widget_id), "widget"))

    def test_widget_id_parsing(self):
        """Test widget ID parsing."""
        widget_id = generate_widget_id("terminal", "session1")
        type_hint, identifier = parse_widget_id(widget_id)

        self.assertEqual(type_hint, "terminal")
        self.assertEqual(identifier, "session1")

    def test_id_validation(self):
        """Test ID format validation."""
        # Valid formats
        self.assertTrue(validate_id_format("pane_12345678", "pane"))
        self.assertTrue(validate_id_format("node_abcdef01", "node"))
        self.assertTrue(validate_id_format("editor:file.txt", "widget"))

        # Invalid formats
        self.assertFalse(validate_id_format("invalid", "pane"))
        self.assertFalse(validate_id_format("pane-12345678", "pane"))
        self.assertFalse(validate_id_format("editor", "widget"))
        self.assertFalse(validate_id_format("", "pane"))


if __name__ == '__main__':
    unittest.main()
```

**Validation**:
Run tests: `python -m pytest tests/test_id_generation.py -v`
All tests should pass.

---

## P0.2: Tree Utilities

### Task P0.2.1: Create Node Base Classes
**Title**: Create core/nodes.py with PaneNode hierarchy
**Dependencies**: P0.1.1
**File**: `src/vfwidgets_multisplit/core/nodes.py`

**Implementation**:
```python
"""Tree node structures for MultiSplit widget.

Pure Python implementation with no Qt dependencies.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, List, Any, TYPE_CHECKING
from dataclasses import dataclass, field

from .types import PaneId, NodeId, WidgetId, Orientation

if TYPE_CHECKING:
    from .visitor import NodeVisitor


class PaneNode(ABC):
    """Abstract base class for tree nodes."""

    def __init__(self, node_id: NodeId):
        """Initialize node with unique ID.

        Args:
            node_id: Unique identifier for this node
        """
        self.node_id = node_id
        self.parent: Optional[PaneNode] = None

    @abstractmethod
    def accept(self, visitor: 'NodeVisitor') -> Any:
        """Accept a visitor for tree traversal.

        Args:
            visitor: Visitor to accept

        Returns:
            Result from visitor
        """
        pass

    @abstractmethod
    def clone(self) -> 'PaneNode':
        """Create a deep copy of this node.

        Returns:
            Cloned node with new IDs
        """
        pass


@dataclass
class LeafNode(PaneNode):
    """Terminal node containing a widget reference."""

    pane_id: PaneId
    widget_id: WidgetId
    node_id: NodeId = field(default_factory=lambda: NodeId(""))

    def __post_init__(self):
        """Initialize base class."""
        super().__init__(self.node_id)

    def accept(self, visitor: 'NodeVisitor') -> Any:
        """Accept visitor for leaf node."""
        return visitor.visit_leaf(self)

    def clone(self) -> 'LeafNode':
        """Clone leaf node."""
        return LeafNode(
            pane_id=self.pane_id,
            widget_id=self.widget_id,
            node_id=self.node_id
        )


@dataclass
class SplitNode(PaneNode):
    """Internal node that splits space among children."""

    orientation: Orientation
    children: List[PaneNode] = field(default_factory=list)
    ratios: List[float] = field(default_factory=list)
    node_id: NodeId = field(default_factory=lambda: NodeId(""))

    def __post_init__(self):
        """Initialize base class and validate."""
        super().__init__(self.node_id)
        # Set parent references
        for child in self.children:
            child.parent = self

    def accept(self, visitor: 'NodeVisitor') -> Any:
        """Accept visitor for split node."""
        return visitor.visit_split(self)

    def clone(self) -> 'SplitNode':
        """Clone split node and all children."""
        cloned_children = [child.clone() for child in self.children]
        return SplitNode(
            orientation=self.orientation,
            children=cloned_children,
            ratios=self.ratios.copy(),
            node_id=self.node_id
        )
```

**Validation**:
- Classes are importable
- LeafNode and SplitNode can be instantiated
- No Qt imports

---

### Task P0.2.2: Create Visitor Pattern
**Title**: Create core/visitor.py with visitor interface
**Dependencies**: P0.2.1
**File**: `src/vfwidgets_multisplit/core/visitor.py`

**Implementation**:
```python
"""Visitor pattern for tree traversal.

Pure Python implementation for tree operations.
"""

from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .nodes import LeafNode, SplitNode


class NodeVisitor(ABC):
    """Abstract visitor for tree nodes."""

    @abstractmethod
    def visit_leaf(self, node: 'LeafNode') -> Any:
        """Visit a leaf node.

        Args:
            node: Leaf node to visit

        Returns:
            Result of visiting
        """
        pass

    @abstractmethod
    def visit_split(self, node: 'SplitNode') -> Any:
        """Visit a split node.

        Args:
            node: Split node to visit

        Returns:
            Result of visiting
        """
        pass
```

**Validation**:
- Interface defines both visit methods
- Proper type hints with forward references

---

### Task P0.2.3: Create Tree Utilities Module
**Title**: Create core/tree_utils.py with tree manipulation functions
**Dependencies**: P0.2.1, P0.2.2
**File**: `src/vfwidgets_multisplit/core/tree_utils.py`

**Implementation**:
```python
"""Tree manipulation utilities.

Core tree operations and validation functions.
"""

from typing import Optional, List
from .types import PaneId, InvalidRatioError, InvalidStructureError
from .nodes import PaneNode, LeafNode, SplitNode
from .visitor import NodeVisitor


def normalize_ratios(ratios: List[float]) -> List[float]:
    """Ensure ratios sum to 1.0, handling edge cases.

    Args:
        ratios: List of ratio values

    Returns:
        Normalized ratios that sum to 1.0
    """
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


def validate_ratios(ratios: List[float], tolerance: float = 0.001) -> bool:
    """Check if ratios are valid (sum to 1.0 within tolerance).

    Args:
        ratios: List of ratio values
        tolerance: Acceptable deviation from 1.0

    Returns:
        True if ratios are valid
    """
    if not ratios:
        return False

    if any(r < 0 for r in ratios):
        return False

    total = sum(ratios)
    return abs(total - 1.0) <= tolerance


class NodeFinder(NodeVisitor):
    """Visitor that finds a node by pane ID."""

    def __init__(self, target_id: PaneId):
        """Initialize finder with target ID.

        Args:
            target_id: Pane ID to search for
        """
        self.target_id = target_id
        self.found_node: Optional[PaneNode] = None

    def visit_leaf(self, node: LeafNode) -> None:
        """Check if leaf matches target."""
        if node.pane_id == self.target_id:
            self.found_node = node

    def visit_split(self, node: SplitNode) -> None:
        """Recursively search split node children."""
        for child in node.children:
            if self.found_node is None:
                child.accept(self)


def find_node_by_id(root: PaneNode, pane_id: PaneId) -> Optional[PaneNode]:
    """Find node in tree by pane ID.

    Args:
        root: Root node to search from
        pane_id: ID to search for

    Returns:
        Found node or None
    """
    finder = NodeFinder(pane_id)
    root.accept(finder)
    return finder.found_node


class LeafCollector(NodeVisitor):
    """Visitor that collects all leaf nodes."""

    def __init__(self):
        """Initialize collector."""
        self.leaves: List[LeafNode] = []

    def visit_leaf(self, node: LeafNode) -> None:
        """Add leaf to collection."""
        self.leaves.append(node)

    def visit_split(self, node: SplitNode) -> None:
        """Recursively collect from children."""
        for child in node.children:
            child.accept(self)


def get_all_leaves(root: PaneNode) -> List[LeafNode]:
    """Get all leaf nodes in tree.

    Args:
        root: Root node of tree

    Returns:
        List of all leaf nodes
    """
    collector = LeafCollector()
    root.accept(collector)
    return collector.leaves


class DepthCalculator(NodeVisitor):
    """Visitor that calculates tree depth."""

    def visit_leaf(self, node: LeafNode) -> int:
        """Leaf has depth 1."""
        return 1

    def visit_split(self, node: SplitNode) -> int:
        """Split depth is 1 + max child depth."""
        if not node.children:
            return 1
        return 1 + max(child.accept(self) for child in node.children)


def get_tree_depth(root: PaneNode) -> int:
    """Calculate maximum tree depth.

    Args:
        root: Root node of tree

    Returns:
        Maximum depth of tree
    """
    calculator = DepthCalculator()
    return root.accept(calculator)


class StructureValidator(NodeVisitor):
    """Visitor that validates tree structure."""

    def __init__(self):
        """Initialize validator."""
        self.is_valid = True
        self.errors: List[str] = []

    def visit_leaf(self, node: LeafNode) -> None:
        """Validate leaf node."""
        if not node.pane_id:
            self.is_valid = False
            self.errors.append("Leaf node missing pane_id")

        if not node.widget_id:
            self.is_valid = False
            self.errors.append("Leaf node missing widget_id")

    def visit_split(self, node: SplitNode) -> None:
        """Validate split node."""
        if len(node.children) < 2:
            self.is_valid = False
            self.errors.append(f"Split node has {len(node.children)} children (minimum 2)")

        if len(node.ratios) != len(node.children):
            self.is_valid = False
            self.errors.append("Ratio count doesn't match child count")

        if not validate_ratios(node.ratios):
            self.is_valid = False
            self.errors.append(f"Invalid ratios: {node.ratios}")

        # Recursively validate children
        for child in node.children:
            child.accept(self)


def validate_tree_structure(root: PaneNode) -> tuple[bool, List[str]]:
    """Validate tree structure invariants.

    Args:
        root: Root node to validate

    Returns:
        Tuple of (is_valid, error_messages)
    """
    validator = StructureValidator()
    root.accept(validator)
    return validator.is_valid, validator.errors
```

**Validation**:
- All visitor classes implement NodeVisitor interface
- Functions handle edge cases correctly
- Tree traversal works recursively

---

### Task P0.2.4: Create Tree Utility Tests
**Title**: Write comprehensive tests for tree utilities
**Dependencies**: P0.2.1, P0.2.2, P0.2.3
**File**: `tests/test_tree_utils.py`

**Implementation**:
```python
"""Tests for tree manipulation utilities."""

import unittest
from vfwidgets_multisplit.core.types import PaneId, NodeId, WidgetId, Orientation
from vfwidgets_multisplit.core.nodes import LeafNode, SplitNode
from vfwidgets_multisplit.core.tree_utils import (
    normalize_ratios,
    validate_ratios,
    find_node_by_id,
    get_all_leaves,
    get_tree_depth,
    validate_tree_structure
)
from vfwidgets_multisplit.core.utils import generate_pane_id, generate_node_id, generate_widget_id


class TestTreeUtils(unittest.TestCase):
    """Test tree utility functions."""

    def test_normalize_ratios(self):
        """Test ratio normalization."""
        # Normal case
        ratios = normalize_ratios([1, 2, 3])
        self.assertAlmostEqual(sum(ratios), 1.0)
        self.assertAlmostEqual(ratios[0], 1/6)

        # All zeros
        ratios = normalize_ratios([0, 0, 0])
        self.assertEqual(ratios, [1/3, 1/3, 1/3])

        # Empty list
        ratios = normalize_ratios([])
        self.assertEqual(ratios, [])

    def test_validate_ratios(self):
        """Test ratio validation."""
        self.assertTrue(validate_ratios([0.3, 0.7]))
        self.assertTrue(validate_ratios([0.333, 0.333, 0.334]))

        self.assertFalse(validate_ratios([0.5, 0.6]))  # Sum > 1
        self.assertFalse(validate_ratios([-0.5, 1.5]))  # Negative
        self.assertFalse(validate_ratios([]))  # Empty

    def test_find_node_by_id(self):
        """Test finding nodes by ID."""
        # Create simple tree
        pane_id = generate_pane_id()
        leaf = LeafNode(
            pane_id=pane_id,
            widget_id=generate_widget_id("editor", "test.py"),
            node_id=generate_node_id()
        )

        root = SplitNode(
            orientation=Orientation.HORIZONTAL,
            children=[leaf],
            ratios=[1.0],
            node_id=generate_node_id()
        )

        # Should find the leaf
        found = find_node_by_id(root, pane_id)
        self.assertEqual(found, leaf)

        # Should return None for non-existent ID
        found = find_node_by_id(root, PaneId("nonexistent"))
        self.assertIsNone(found)

    def test_get_all_leaves(self):
        """Test collecting all leaves."""
        # Create tree with multiple leaves
        leaf1 = LeafNode(
            pane_id=generate_pane_id(),
            widget_id=generate_widget_id("editor", "file1.py"),
            node_id=generate_node_id()
        )
        leaf2 = LeafNode(
            pane_id=generate_pane_id(),
            widget_id=generate_widget_id("editor", "file2.py"),
            node_id=generate_node_id()
        )

        root = SplitNode(
            orientation=Orientation.HORIZONTAL,
            children=[leaf1, leaf2],
            ratios=[0.5, 0.5],
            node_id=generate_node_id()
        )

        leaves = get_all_leaves(root)
        self.assertEqual(len(leaves), 2)
        self.assertIn(leaf1, leaves)
        self.assertIn(leaf2, leaves)

    def test_get_tree_depth(self):
        """Test tree depth calculation."""
        # Single leaf
        leaf = LeafNode(
            pane_id=generate_pane_id(),
            widget_id=generate_widget_id("editor", "test.py"),
            node_id=generate_node_id()
        )
        self.assertEqual(get_tree_depth(leaf), 1)

        # Split with two leaves
        root = SplitNode(
            orientation=Orientation.HORIZONTAL,
            children=[
                LeafNode(generate_pane_id(), generate_widget_id("editor", "1.py"), generate_node_id()),
                LeafNode(generate_pane_id(), generate_widget_id("editor", "2.py"), generate_node_id())
            ],
            ratios=[0.5, 0.5],
            node_id=generate_node_id()
        )
        self.assertEqual(get_tree_depth(root), 2)

    def test_validate_tree_structure(self):
        """Test tree structure validation."""
        # Valid tree
        root = SplitNode(
            orientation=Orientation.HORIZONTAL,
            children=[
                LeafNode(generate_pane_id(), generate_widget_id("editor", "1.py"), generate_node_id()),
                LeafNode(generate_pane_id(), generate_widget_id("editor", "2.py"), generate_node_id())
            ],
            ratios=[0.5, 0.5],
            node_id=generate_node_id()
        )

        is_valid, errors = validate_tree_structure(root)
        self.assertTrue(is_valid)
        self.assertEqual(errors, [])

        # Invalid tree - wrong ratio count
        root.ratios = [0.5]  # Should have 2 ratios
        is_valid, errors = validate_tree_structure(root)
        self.assertFalse(is_valid)
        self.assertIn("Ratio count doesn't match child count", errors[0])


if __name__ == '__main__':
    unittest.main()
```

**Validation**:
Run tests: `python -m pytest tests/test_tree_utils.py -v`

---

## P0.3: Signal Bridge

### Task P0.3.1: Create Abstract Signal System
**Title**: Create core/signals.py with AbstractSignal class
**Dependencies**: None
**File**: `src/vfwidgets_multisplit/core/signals.py`

**Implementation**:
```python
"""Abstract signal system for Model layer.

Pure Python implementation with no Qt dependencies.
Provides signal/slot mechanism for the Model layer.
"""

import weakref
from typing import Callable, Any, List, Optional


class AbstractSignal:
    """Pure Python signal implementation with no Qt dependencies."""

    def __init__(self):
        """Initialize signal with empty handler list."""
        # Use weak references to prevent memory leaks
        self._handlers: List[weakref.ref] = []

    def connect(self, handler: Callable) -> None:
        """Connect a handler to this signal.

        Args:
            handler: Callable to invoke when signal is emitted
        """
        # Store as weak reference
        ref = weakref.ref(handler)
        if ref not in self._handlers:
            self._handlers.append(ref)

    def disconnect(self, handler: Callable) -> None:
        """Disconnect a handler from this signal.

        Args:
            handler: Handler to remove
        """
        ref = weakref.ref(handler)
        self._handlers = [h for h in self._handlers if h() != handler]

    def emit(self, *args, **kwargs) -> None:
        """Emit signal to all connected handlers.

        Args:
            *args: Positional arguments to pass to handlers
            **kwargs: Keyword arguments to pass to handlers
        """
        # Clean up dead references
        self._cleanup_handlers()

        # Call all live handlers
        for ref in self._handlers:
            handler = ref()
            if handler is not None:
                try:
                    handler(*args, **kwargs)
                except Exception as e:
                    # Don't let handler errors break signal emission
                    print(f"Signal handler error: {e}")

    def _cleanup_handlers(self) -> None:
        """Remove dead weak references."""
        self._handlers = [ref for ref in self._handlers if ref() is not None]

    def handler_count(self) -> int:
        """Get count of connected handlers.

        Returns:
            Number of live handlers
        """
        self._cleanup_handlers()
        return len(self._handlers)

    def clear(self) -> None:
        """Disconnect all handlers."""
        self._handlers.clear()


class ModelSignals:
    """Collection of signals for the Model layer."""

    def __init__(self):
        """Initialize all model signals."""
        # Structure signals
        self.about_to_change = AbstractSignal()
        self.changed = AbstractSignal()
        self.structure_changed = AbstractSignal()

        # Focus signals
        self.focus_changed = AbstractSignal()

        # Pane signals
        self.pane_added = AbstractSignal()
        self.pane_removed = AbstractSignal()

        # Error signals
        self.validation_failed = AbstractSignal()
```

**Validation**:
- AbstractSignal can connect/disconnect handlers
- Weak references prevent memory leaks
- Signal emission doesn't fail on handler errors

---

### Task P0.3.2: Create Signal Bridge
**Title**: Create core/signal_bridge.py to bridge Model and Qt signals
**Dependencies**: P0.3.1
**File**: `src/vfwidgets_multisplit/core/signal_bridge.py`

**Implementation**:
```python
"""Bridge between abstract model signals and Qt signals.

This module provides the connection between pure Python
signals in the Model layer and Qt signals in the View layer.
"""

from typing import Protocol, Any, List, Tuple
from .signals import AbstractSignal


class QtSignalProtocol(Protocol):
    """Protocol for Qt signals (without importing Qt)."""

    def emit(self, *args) -> None:
        """Emit the Qt signal."""
        ...

    def connect(self, slot: Any) -> None:
        """Connect to Qt signal."""
        ...

    def disconnect(self, slot: Any) -> None:
        """Disconnect from Qt signal."""
        ...


class SignalBridge:
    """Bridges abstract signals to Qt signals without Qt dependency in Model."""

    def __init__(self):
        """Initialize bridge with empty connections."""
        self._bridges: List[Tuple[AbstractSignal, QtSignalProtocol, Any]] = []

    def bridge_to_qt(self, abstract_signal: AbstractSignal,
                     qt_signal: QtSignalProtocol) -> None:
        """Create bridge from abstract signal to Qt signal.

        Args:
            abstract_signal: Source signal from Model
            qt_signal: Target Qt signal in View
        """
        # Create relay function
        def relay(*args, **kwargs):
            # Qt signals typically don't use kwargs
            qt_signal.emit(*args)

        # Connect abstract signal to relay
        abstract_signal.connect(relay)

        # Store bridge info for cleanup
        self._bridges.append((abstract_signal, qt_signal, relay))

    def bridge_from_qt(self, qt_signal: QtSignalProtocol,
                      abstract_signal: AbstractSignal) -> None:
        """Create bridge from Qt signal to abstract signal.

        Args:
            qt_signal: Source Qt signal from View
            abstract_signal: Target signal in Model
        """
        # Create relay function
        def relay(*args):
            abstract_signal.emit(*args)

        # Connect Qt signal to relay
        qt_signal.connect(relay)

        # Store bridge info for cleanup
        self._bridges.append((abstract_signal, qt_signal, relay))

    def cleanup(self) -> None:
        """Remove all signal bridges."""
        for bridge in self._bridges:
            if len(bridge) == 3:
                source, target, relay = bridge
                try:
                    # Try to disconnect
                    if hasattr(source, 'disconnect'):
                        source.disconnect(relay)
                    if hasattr(target, 'disconnect'):
                        target.disconnect(relay)
                except:
                    pass  # Ignore disconnect errors during cleanup

        self._bridges.clear()
```

**Validation**:
- Bridge can connect abstract signals to Qt signals
- No Qt imports in file
- Cleanup removes all connections

---

### Task P0.3.3: Create Signal Bridge Tests
**Title**: Write tests for signal system
**Dependencies**: P0.3.1, P0.3.2
**File**: `tests/test_signals.py`

**Implementation**:
```python
"""Tests for abstract signal system."""

import unittest
from vfwidgets_multisplit.core.signals import AbstractSignal, ModelSignals
from vfwidgets_multisplit.core.signal_bridge import SignalBridge


class TestAbstractSignal(unittest.TestCase):
    """Test abstract signal implementation."""

    def test_connect_and_emit(self):
        """Test connecting handlers and emitting signals."""
        signal = AbstractSignal()
        results = []

        def handler(value):
            results.append(value)

        signal.connect(handler)
        signal.emit(42)

        self.assertEqual(results, [42])

    def test_multiple_handlers(self):
        """Test multiple handlers on same signal."""
        signal = AbstractSignal()
        results = []

        def handler1(value):
            results.append(f"h1:{value}")

        def handler2(value):
            results.append(f"h2:{value}")

        signal.connect(handler1)
        signal.connect(handler2)
        signal.emit("test")

        self.assertIn("h1:test", results)
        self.assertIn("h2:test", results)

    def test_disconnect(self):
        """Test disconnecting handlers."""
        signal = AbstractSignal()
        results = []

        def handler(value):
            results.append(value)

        signal.connect(handler)
        signal.emit(1)

        signal.disconnect(handler)
        signal.emit(2)

        self.assertEqual(results, [1])  # 2 should not be added

    def test_weak_references(self):
        """Test that weak references don't prevent garbage collection."""
        signal = AbstractSignal()

        def create_handler():
            results = []
            def handler(value):
                results.append(value)
            signal.connect(handler)
            return handler

        handler = create_handler()
        self.assertEqual(signal.handler_count(), 1)

        # Delete handler - weak ref should be cleaned up
        del handler
        signal.emit("test")  # This triggers cleanup
        self.assertEqual(signal.handler_count(), 0)

    def test_handler_error_isolation(self):
        """Test that handler errors don't break signal emission."""
        signal = AbstractSignal()
        results = []

        def bad_handler(value):
            raise ValueError("Test error")

        def good_handler(value):
            results.append(value)

        signal.connect(bad_handler)
        signal.connect(good_handler)

        # Should not raise despite bad_handler error
        signal.emit("test")

        # Good handler should still be called
        self.assertEqual(results, ["test"])


class MockQtSignal:
    """Mock Qt signal for testing bridge."""

    def __init__(self):
        self.emitted_values = []
        self.handlers = []

    def emit(self, *args):
        self.emitted_values.append(args)
        for handler in self.handlers:
            handler(*args)

    def connect(self, slot):
        self.handlers.append(slot)

    def disconnect(self, slot):
        if slot in self.handlers:
            self.handlers.remove(slot)


class TestSignalBridge(unittest.TestCase):
    """Test signal bridge functionality."""

    def test_bridge_to_qt(self):
        """Test bridging from abstract signal to Qt signal."""
        abstract_signal = AbstractSignal()
        qt_signal = MockQtSignal()
        bridge = SignalBridge()

        bridge.bridge_to_qt(abstract_signal, qt_signal)

        # Emit on abstract signal should trigger Qt signal
        abstract_signal.emit("test", 42)

        self.assertEqual(qt_signal.emitted_values, [("test", 42)])

    def test_bridge_from_qt(self):
        """Test bridging from Qt signal to abstract signal."""
        abstract_signal = AbstractSignal()
        qt_signal = MockQtSignal()
        bridge = SignalBridge()
        results = []

        def handler(value):
            results.append(value)

        abstract_signal.connect(handler)
        bridge.bridge_from_qt(qt_signal, abstract_signal)

        # Emit on Qt signal should trigger abstract signal
        qt_signal.emit("test")

        self.assertEqual(results, ["test"])

    def test_bridge_cleanup(self):
        """Test bridge cleanup removes connections."""
        abstract_signal = AbstractSignal()
        qt_signal = MockQtSignal()
        bridge = SignalBridge()

        bridge.bridge_to_qt(abstract_signal, qt_signal)
        bridge.cleanup()

        # After cleanup, signals should not be connected
        abstract_signal.emit("test")
        self.assertEqual(qt_signal.emitted_values, [])


if __name__ == '__main__':
    unittest.main()
```

**Validation**:
Run tests: `python -m pytest tests/test_signals.py -v`

---

## P0.4: Geometry Calculator

### Task P0.4.1: Create Geometry Types
**Title**: Add Bounds class to core/types.py
**Dependencies**: P0.1.1
**File**: `src/vfwidgets_multisplit/core/types.py`

**Implementation**:
Add to existing types.py:
```python
@dataclass(frozen=True)
class Bounds:
    """Immutable bounds representation for geometry calculations."""
    x: int
    y: int
    width: int
    height: int

    def __post_init__(self):
        """Validate bounds values."""
        if self.width < 0 or self.height < 0:
            raise ValueError(f"Bounds dimensions must be non-negative: {self.width}x{self.height}")

    @property
    def right(self) -> int:
        """Get right edge coordinate."""
        return self.x + self.width

    @property
    def bottom(self) -> int:
        """Get bottom edge coordinate."""
        return self.y + self.height

    def contains_point(self, x: int, y: int) -> bool:
        """Check if point is within bounds.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            True if point is inside bounds
        """
        return (self.x <= x < self.right and
                self.y <= y < self.bottom)

    def intersects(self, other: 'Bounds') -> bool:
        """Check if bounds intersect with another.

        Args:
            other: Other bounds to check

        Returns:
            True if bounds overlap
        """
        return not (self.right <= other.x or
                   other.right <= self.x or
                   self.bottom <= other.y or
                   other.bottom <= self.y)
```

**Validation**:
- Bounds class is immutable (frozen dataclass)
- Negative dimensions raise ValueError
- Helper properties work correctly

---

### Task P0.4.2: Create Geometry Calculator
**Title**: Create core/geometry.py with GeometryCalculator class
**Dependencies**: P0.4.1, P0.2.1
**File**: `src/vfwidgets_multisplit/core/geometry.py`

**Implementation**:
```python
"""Geometry calculation for pane layout.

Calculates exact pixel positions for all panes from tree structure.
"""

from typing import Dict, List
from .types import PaneId, Bounds, Orientation
from .nodes import PaneNode, LeafNode, SplitNode


class GeometryCalculator:
    """Calculate pane positions from tree structure."""

    def __init__(self, divider_width: int = 4):
        """Initialize calculator with divider width.

        Args:
            divider_width: Width of dividers between panes in pixels
        """
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
        """Recursively calculate bounds for tree nodes.

        Args:
            node: Current node to process
            bounds: Available bounds for this node
            result: Dictionary to store results
        """
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
        """Split bounds according to orientation and ratios.

        Args:
            bounds: Bounds to split
            orientation: How to split (horizontal/vertical)
            ratios: Space distribution ratios
            child_count: Number of children

        Returns:
            List of bounds for each child
        """
        if child_count == 0:
            return []

        if child_count == 1:
            return [bounds]

        # Calculate space for dividers
        total_divider_space = (child_count - 1) * self.divider_width

        if orientation == Orientation.HORIZONTAL:
            return self._split_horizontal(bounds, ratios, total_divider_space)
        else:
            return self._split_vertical(bounds, ratios, total_divider_space)

    def _split_horizontal(self, bounds: Bounds, ratios: List[float],
                         divider_space: int) -> List[Bounds]:
        """Split bounds horizontally.

        Args:
            bounds: Bounds to split
            ratios: Width ratios for children
            divider_space: Total space used by dividers

        Returns:
            List of child bounds
        """
        available_width = bounds.width - divider_space
        if available_width <= 0:
            # Not enough space - give minimal bounds
            return [Bounds(bounds.x, bounds.y, 1, bounds.height)] * len(ratios)

        child_bounds = []
        current_x = bounds.x

        for i, ratio in enumerate(ratios):
            # Calculate child width
            if i == len(ratios) - 1:
                # Last child gets remaining space (handles rounding)
                child_width = bounds.x + bounds.width - current_x
            else:
                child_width = int(available_width * ratio)

            child_bounds.append(Bounds(
                current_x, bounds.y,
                child_width, bounds.height
            ))

            # Move past this child and divider
            current_x += child_width
            if i < len(ratios) - 1:
                current_x += self.divider_width

        return child_bounds

    def _split_vertical(self, bounds: Bounds, ratios: List[float],
                       divider_space: int) -> List[Bounds]:
        """Split bounds vertically.

        Args:
            bounds: Bounds to split
            ratios: Height ratios for children
            divider_space: Total space used by dividers

        Returns:
            List of child bounds
        """
        available_height = bounds.height - divider_space
        if available_height <= 0:
            # Not enough space - give minimal bounds
            return [Bounds(bounds.x, bounds.y, bounds.width, 1)] * len(ratios)

        child_bounds = []
        current_y = bounds.y

        for i, ratio in enumerate(ratios):
            # Calculate child height
            if i == len(ratios) - 1:
                # Last child gets remaining space (handles rounding)
                child_height = bounds.y + bounds.height - current_y
            else:
                child_height = int(available_height * ratio)

            child_bounds.append(Bounds(
                bounds.x, current_y,
                bounds.width, child_height
            ))

            # Move past this child and divider
            current_y += child_height
            if i < len(ratios) - 1:
                current_y += self.divider_width

        return child_bounds

    def calculate_divider_bounds(self, root: PaneNode,
                                container_bounds: Bounds) -> List[Bounds]:
        """Calculate bounds for all dividers in the tree.

        Args:
            root: Root node of tree
            container_bounds: Container bounds

        Returns:
            List of divider bounds
        """
        dividers = []
        self._collect_divider_bounds(root, container_bounds, dividers)
        return dividers

    def _collect_divider_bounds(self, node: PaneNode, bounds: Bounds,
                               dividers: List[Bounds]):
        """Collect divider bounds recursively.

        Args:
            node: Current node
            bounds: Node bounds
            dividers: List to collect divider bounds
        """
        if isinstance(node, SplitNode) and len(node.children) > 1:
            child_bounds = self._split_bounds(
                bounds, node.orientation, node.ratios, len(node.children)
            )

            # Add dividers between children
            for i in range(len(child_bounds) - 1):
                current_bounds = child_bounds[i]

                if node.orientation == Orientation.HORIZONTAL:
                    # Vertical divider between horizontal children
                    divider_x = current_bounds.right
                    dividers.append(Bounds(
                        divider_x, bounds.y,
                        self.divider_width, bounds.height
                    ))
                else:
                    # Horizontal divider between vertical children
                    divider_y = current_bounds.bottom
                    dividers.append(Bounds(
                        bounds.x, divider_y,
                        bounds.width, self.divider_width
                    ))

            # Recursively process children
            for child, child_bound in zip(node.children, child_bounds):
                self._collect_divider_bounds(child, child_bound, dividers)
```

**Validation**:
- Calculates pixel-perfect bounds
- Handles minimum size constraints
- No gaps or overlaps between panes

---

### Task P0.4.3: Create Geometry Tests
**Title**: Write tests for geometry calculator
**Dependencies**: P0.4.1, P0.4.2
**File**: `tests/test_geometry.py`

**Implementation**:
```python
"""Tests for geometry calculator."""

import unittest
from vfwidgets_multisplit.core.types import Bounds, Orientation
from vfwidgets_multisplit.core.nodes import LeafNode, SplitNode
from vfwidgets_multisplit.core.geometry import GeometryCalculator
from vfwidgets_multisplit.core.utils import generate_pane_id, generate_node_id, generate_widget_id


class TestGeometry(unittest.TestCase):
    """Test geometry calculation."""

    def test_single_leaf(self):
        """Test geometry for single leaf node."""
        calc = GeometryCalculator()
        pane_id = generate_pane_id()

        leaf = LeafNode(
            pane_id=pane_id,
            widget_id=generate_widget_id("editor", "test.py"),
            node_id=generate_node_id()
        )

        bounds = Bounds(0, 0, 800, 600)
        result = calc.calculate(leaf, bounds)

        # Single leaf gets full bounds
        self.assertEqual(result[pane_id], bounds)

    def test_horizontal_split(self):
        """Test horizontal split geometry."""
        calc = GeometryCalculator(divider_width=4)

        pane1_id = generate_pane_id()
        pane2_id = generate_pane_id()

        root = SplitNode(
            orientation=Orientation.HORIZONTAL,
            children=[
                LeafNode(pane1_id, generate_widget_id("editor", "1.py"), generate_node_id()),
                LeafNode(pane2_id, generate_widget_id("editor", "2.py"), generate_node_id())
            ],
            ratios=[0.5, 0.5],
            node_id=generate_node_id()
        )

        bounds = Bounds(0, 0, 804, 600)  # 804 = 400 + 4 + 400
        result = calc.calculate(root, bounds)

        # Check first pane
        self.assertEqual(result[pane1_id].x, 0)
        self.assertEqual(result[pane1_id].width, 400)

        # Check second pane (after divider)
        self.assertEqual(result[pane2_id].x, 404)
        self.assertEqual(result[pane2_id].width, 400)

    def test_vertical_split(self):
        """Test vertical split geometry."""
        calc = GeometryCalculator(divider_width=4)

        pane1_id = generate_pane_id()
        pane2_id = generate_pane_id()

        root = SplitNode(
            orientation=Orientation.VERTICAL,
            children=[
                LeafNode(pane1_id, generate_widget_id("editor", "1.py"), generate_node_id()),
                LeafNode(pane2_id, generate_widget_id("terminal", "bash"), generate_node_id())
            ],
            ratios=[0.7, 0.3],
            node_id=generate_node_id()
        )

        bounds = Bounds(0, 0, 800, 604)  # 604 = 420 + 4 + 180
        result = calc.calculate(root, bounds)

        # Check first pane (70% of available height)
        self.assertEqual(result[pane1_id].y, 0)
        self.assertEqual(result[pane1_id].height, 420)

        # Check second pane (30% of available height)
        self.assertEqual(result[pane2_id].y, 424)
        self.assertEqual(result[pane2_id].height, 180)

    def test_divider_bounds(self):
        """Test divider bounds calculation."""
        calc = GeometryCalculator(divider_width=4)

        root = SplitNode(
            orientation=Orientation.HORIZONTAL,
            children=[
                LeafNode(generate_pane_id(), generate_widget_id("editor", "1.py"), generate_node_id()),
                LeafNode(generate_pane_id(), generate_widget_id("editor", "2.py"), generate_node_id())
            ],
            ratios=[0.5, 0.5],
            node_id=generate_node_id()
        )

        bounds = Bounds(0, 0, 804, 600)
        dividers = calc.calculate_divider_bounds(root, bounds)

        # Should have one divider
        self.assertEqual(len(dividers), 1)

        # Divider should be vertical, in the middle
        divider = dividers[0]
        self.assertEqual(divider.x, 400)
        self.assertEqual(divider.width, 4)
        self.assertEqual(divider.height, 600)


if __name__ == '__main__':
    unittest.main()
```

**Validation**:
Run tests: `python -m pytest tests/test_geometry.py -v`

---

## P0.5: Tree Reconciler

### Task P0.5.1: Create Reconciler Module
**Title**: Create view/tree_reconciler.py with DiffResult and TreeReconciler
**Dependencies**: P0.2.1
**File**: `src/vfwidgets_multisplit/view/tree_reconciler.py`

**Implementation**:
```python
"""Tree reconciliation for efficient updates.

Calculates minimal differences between tree states to
enable efficient UI updates without full rebuilds.
"""

from typing import Optional, Set, Dict, Any
from dataclasses import dataclass, field

from ..core.types import PaneId
from ..core.nodes import PaneNode, LeafNode, SplitNode
from ..core.visitor import NodeVisitor


@dataclass
class DiffResult:
    """Result of tree diff operation."""
    removed: Set[PaneId] = field(default_factory=set)
    added: Set[PaneId] = field(default_factory=set)
    moved: Set[PaneId] = field(default_factory=set)
    modified: Set[PaneId] = field(default_factory=set)

    def has_changes(self) -> bool:
        """Check if any changes exist.

        Returns:
            True if there are any differences
        """
        return bool(self.removed or self.added or self.moved or self.modified)

    @property
    def total_changes(self) -> int:
        """Get total number of changes.

        Returns:
            Count of all changes
        """
        return len(self.removed) + len(self.added) + len(self.moved) + len(self.modified)


class NodeCollector(NodeVisitor):
    """Visitor that collects node information for comparison."""

    def __init__(self):
        """Initialize collector."""
        self.nodes: Dict[PaneId, Dict[str, Any]] = {}

    def visit_leaf(self, node: LeafNode) -> None:
        """Collect leaf node information."""
        self.nodes[node.pane_id] = {
            'type': 'leaf',
            'widget_id': node.widget_id,
            'node_id': node.node_id,
            'parent': node.parent.node_id if node.parent else None
        }

    def visit_split(self, node: SplitNode) -> None:
        """Collect split node information and visit children."""
        # Split nodes don't have pane_id, only process children
        for child in node.children:
            child.accept(self)


class TreeReconciler:
    """Calculate minimal updates between tree states."""

    def diff(self, old_tree: Optional[PaneNode],
            new_tree: Optional[PaneNode]) -> DiffResult:
        """Calculate differences between two trees.

        Args:
            old_tree: Previous tree state (None if first render)
            new_tree: New tree state (None if clearing)

        Returns:
            DiffResult with all changes
        """
        result = DiffResult()

        # Handle edge cases
        if old_tree is None and new_tree is None:
            return result

        if old_tree is None:
            # Everything is new
            collector = NodeCollector()
            new_tree.accept(collector)
            result.added = set(collector.nodes.keys())
            return result

        if new_tree is None:
            # Everything is removed
            collector = NodeCollector()
            old_tree.accept(collector)
            result.removed = set(collector.nodes.keys())
            return result

        # Collect information from both trees
        old_collector = NodeCollector()
        old_tree.accept(old_collector)
        old_nodes = old_collector.nodes

        new_collector = NodeCollector()
        new_tree.accept(new_collector)
        new_nodes = new_collector.nodes

        # Calculate differences
        old_ids = set(old_nodes.keys())
        new_ids = set(new_nodes.keys())

        # Removed panes
        result.removed = old_ids - new_ids

        # Added panes
        result.added = new_ids - old_ids

        # Check for moved and modified panes
        common_ids = old_ids & new_ids
        for pane_id in common_ids:
            old_info = old_nodes[pane_id]
            new_info = new_nodes[pane_id]

            # Check if parent changed (moved)
            if old_info['parent'] != new_info['parent']:
                result.moved.add(pane_id)

            # Check if widget changed (modified)
            if old_info['widget_id'] != new_info['widget_id']:
                result.modified.add(pane_id)

        return result

    def apply_diff(self, diff: DiffResult, operations: 'ReconcilerOperations') -> None:
        """Apply diff result using provided operations.

        Args:
            diff: Diff result to apply
            operations: Operations interface for applying changes
        """
        # Remove old panes
        for pane_id in diff.removed:
            operations.remove_pane(pane_id)

        # Add new panes
        for pane_id in diff.added:
            operations.add_pane(pane_id)

        # Move panes
        for pane_id in diff.moved:
            operations.move_pane(pane_id)

        # Update modified panes
        for pane_id in diff.modified:
            operations.update_pane(pane_id)


class ReconcilerOperations:
    """Interface for reconciler operations."""

    def add_pane(self, pane_id: PaneId) -> None:
        """Add a new pane.

        Args:
            pane_id: ID of pane to add
        """
        raise NotImplementedError

    def remove_pane(self, pane_id: PaneId) -> None:
        """Remove an existing pane.

        Args:
            pane_id: ID of pane to remove
        """
        raise NotImplementedError

    def move_pane(self, pane_id: PaneId) -> None:
        """Move a pane to new position.

        Args:
            pane_id: ID of pane to move
        """
        raise NotImplementedError

    def update_pane(self, pane_id: PaneId) -> None:
        """Update a pane's widget.

        Args:
            pane_id: ID of pane to update
        """
        raise NotImplementedError
```

**Validation**:
- Correctly identifies all types of changes
- Handles edge cases (null trees)
- Provides clean operations interface

---

### Task P0.5.2: Create Reconciler Tests
**Title**: Write tests for tree reconciler
**Dependencies**: P0.5.1
**File**: `tests/test_reconciler.py`

**Implementation**:
```python
"""Tests for tree reconciliation."""

import unittest
from vfwidgets_multisplit.core.types import Orientation
from vfwidgets_multisplit.core.nodes import LeafNode, SplitNode
from vfwidgets_multisplit.view.tree_reconciler import TreeReconciler, DiffResult
from vfwidgets_multisplit.core.utils import generate_pane_id, generate_node_id, generate_widget_id


class TestTreeReconciler(unittest.TestCase):
    """Test tree reconciliation."""

    def test_no_changes(self):
        """Test diff with identical trees."""
        reconciler = TreeReconciler()

        pane_id = generate_pane_id()
        tree = LeafNode(
            pane_id=pane_id,
            widget_id=generate_widget_id("editor", "test.py"),
            node_id=generate_node_id()
        )

        diff = reconciler.diff(tree, tree)
        self.assertFalse(diff.has_changes())

    def test_all_added(self):
        """Test diff when all panes are new."""
        reconciler = TreeReconciler()

        pane1_id = generate_pane_id()
        pane2_id = generate_pane_id()

        tree = SplitNode(
            orientation=Orientation.HORIZONTAL,
            children=[
                LeafNode(pane1_id, generate_widget_id("editor", "1.py"), generate_node_id()),
                LeafNode(pane2_id, generate_widget_id("editor", "2.py"), generate_node_id())
            ],
            ratios=[0.5, 0.5],
            node_id=generate_node_id()
        )

        diff = reconciler.diff(None, tree)

        self.assertEqual(diff.added, {pane1_id, pane2_id})
        self.assertEqual(len(diff.removed), 0)

    def test_all_removed(self):
        """Test diff when all panes are removed."""
        reconciler = TreeReconciler()

        pane1_id = generate_pane_id()
        pane2_id = generate_pane_id()

        tree = SplitNode(
            orientation=Orientation.HORIZONTAL,
            children=[
                LeafNode(pane1_id, generate_widget_id("editor", "1.py"), generate_node_id()),
                LeafNode(pane2_id, generate_widget_id("editor", "2.py"), generate_node_id())
            ],
            ratios=[0.5, 0.5],
            node_id=generate_node_id()
        )

        diff = reconciler.diff(tree, None)

        self.assertEqual(diff.removed, {pane1_id, pane2_id})
        self.assertEqual(len(diff.added), 0)

    def test_pane_modified(self):
        """Test detecting modified panes."""
        reconciler = TreeReconciler()

        pane_id = generate_pane_id()

        old_tree = LeafNode(
            pane_id=pane_id,
            widget_id=generate_widget_id("editor", "old.py"),
            node_id=generate_node_id()
        )

        new_tree = LeafNode(
            pane_id=pane_id,
            widget_id=generate_widget_id("editor", "new.py"),
            node_id=generate_node_id()
        )

        diff = reconciler.diff(old_tree, new_tree)

        self.assertIn(pane_id, diff.modified)
        self.assertEqual(len(diff.added), 0)
        self.assertEqual(len(diff.removed), 0)

    def test_mixed_changes(self):
        """Test diff with mixed changes."""
        reconciler = TreeReconciler()

        # Common pane that will be kept
        common_id = generate_pane_id()
        removed_id = generate_pane_id()
        added_id = generate_pane_id()

        old_tree = SplitNode(
            orientation=Orientation.HORIZONTAL,
            children=[
                LeafNode(common_id, generate_widget_id("editor", "common.py"), generate_node_id()),
                LeafNode(removed_id, generate_widget_id("editor", "old.py"), generate_node_id())
            ],
            ratios=[0.5, 0.5],
            node_id=generate_node_id()
        )

        new_tree = SplitNode(
            orientation=Orientation.HORIZONTAL,
            children=[
                LeafNode(common_id, generate_widget_id("editor", "common.py"), generate_node_id()),
                LeafNode(added_id, generate_widget_id("editor", "new.py"), generate_node_id())
            ],
            ratios=[0.5, 0.5],
            node_id=generate_node_id()
        )

        diff = reconciler.diff(old_tree, new_tree)

        self.assertIn(removed_id, diff.removed)
        self.assertIn(added_id, diff.added)
        self.assertNotIn(common_id, diff.removed)
        self.assertNotIn(common_id, diff.added)


if __name__ == '__main__':
    unittest.main()
```

**Validation**:
Run tests: `python -m pytest tests/test_reconciler.py -v`

---

## P0.6: Transaction Context

### Task P0.6.1: Create Transaction Module
**Title**: Create controller/transaction.py with TransactionContext
**Dependencies**: None
**File**: `src/vfwidgets_multisplit/controller/transaction.py`

**Implementation**:
```python
"""Transaction management for atomic operations.

Provides context managers for atomic command execution
with automatic rollback on failure.
"""

from typing import List, Optional, TYPE_CHECKING
from contextlib import contextmanager

if TYPE_CHECKING:
    from .controller import PaneController
    from .command import Command


class TransactionContext:
    """Context manager for atomic command transactions."""

    def __init__(self, controller: 'PaneController'):
        """Initialize transaction context.

        Args:
            controller: Controller managing this transaction
        """
        self.controller = controller
        self.commands: List['Command'] = []
        self.rolled_back = False
        self.committed = False
        self.savepoint = None

    def __enter__(self):
        """Begin transaction context."""
        # Save current state for potential rollback
        self.savepoint = self.controller._create_savepoint()
        self.controller._begin_transaction(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End transaction context.

        Args:
            exc_type: Exception type if error occurred
            exc_val: Exception value
            exc_tb: Exception traceback

        Returns:
            False to propagate exceptions
        """
        if exc_type or self.rolled_back:
            # Exception occurred or manual rollback
            self.controller._rollback_transaction(self)
            if self.savepoint:
                self.controller._restore_savepoint(self.savepoint)
        else:
            # Successful completion
            self.controller._commit_transaction(self)
            self.committed = True

        # Always cleanup
        self.controller._end_transaction(self)
        return False  # Don't suppress exceptions

    def add_command(self, command: 'Command'):
        """Add command to transaction.

        Args:
            command: Command executed within this transaction
        """
        self.commands.append(command)

    def rollback(self):
        """Mark transaction for rollback."""
        self.rolled_back = True


class NestedTransactionContext(TransactionContext):
    """Context for nested transactions."""

    def __init__(self, controller: 'PaneController', parent: TransactionContext):
        """Initialize nested transaction.

        Args:
            controller: Controller managing this transaction
            parent: Parent transaction context
        """
        super().__init__(controller)
        self.parent = parent

    def __enter__(self):
        """Begin nested transaction."""
        # Don't create new savepoint, use parent's
        self.controller._begin_nested_transaction(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End nested transaction."""
        if exc_type or self.rolled_back:
            # Propagate rollback to parent
            self.parent.rollback()
        else:
            # Add our commands to parent
            for cmd in self.commands:
                self.parent.add_command(cmd)

        self.controller._end_nested_transaction(self)
        return False


@contextmanager
def transaction(controller: 'PaneController'):
    """Convenience context manager for transactions.

    Args:
        controller: Controller to manage transaction

    Yields:
        TransactionContext for the transaction
    """
    context = TransactionContext(controller)
    try:
        with context:
            yield context
    except Exception:
        # Context handles rollback
        raise


@contextmanager
def atomic_operation(controller: 'PaneController', name: str):
    """Named atomic operation for better debugging.

    Args:
        controller: Controller to manage operation
        name: Name of the operation for logging

    Yields:
        TransactionContext for the operation
    """
    context = TransactionContext(controller)
    context.operation_name = name

    try:
        with context:
            yield context
    except Exception as e:
        # Log the failed operation
        print(f"Atomic operation '{name}' failed: {e}")
        raise
```

**Validation**:
- Transaction context properly manages enter/exit
- Rollback restores previous state
- Nested transactions supported

---

### Task P0.6.2: Create Basic Controller
**Title**: Create controller/controller.py with transaction support
**Dependencies**: P0.6.1
**File**: `src/vfwidgets_multisplit/controller/controller.py`

**Implementation**:
```python
"""Controller layer for MultiSplit widget.

Manages all model mutations through commands and transactions.
"""

from typing import Optional, List, Any, Dict
from ..core.signals import AbstractSignal


class PaneController:
    """Controller managing model mutations."""

    def __init__(self, model: Any):
        """Initialize controller with model.

        Args:
            model: PaneModel to control
        """
        self.model = model
        self._transaction_stack: List[Any] = []
        self._savepoints: List[Dict] = []

        # Signals for transaction events
        self.transaction_started = AbstractSignal()
        self.transaction_committed = AbstractSignal()
        self.transaction_rolled_back = AbstractSignal()

    def _begin_transaction(self, context: Any):
        """Begin a new transaction.

        Args:
            context: Transaction context
        """
        self._transaction_stack.append(context)
        self.transaction_started.emit()

    def _commit_transaction(self, context: Any):
        """Commit a transaction.

        Args:
            context: Transaction context to commit
        """
        if context in self._transaction_stack:
            self._transaction_stack.remove(context)
        self.transaction_committed.emit()

    def _rollback_transaction(self, context: Any):
        """Rollback a transaction.

        Args:
            context: Transaction context to rollback
        """
        if context in self._transaction_stack:
            self._transaction_stack.remove(context)

        # Undo all commands in reverse order
        for command in reversed(context.commands):
            try:
                command.undo(self.model)
            except Exception as e:
                print(f"Error during rollback: {e}")

        self.transaction_rolled_back.emit()

    def _end_transaction(self, context: Any):
        """Clean up after transaction ends.

        Args:
            context: Transaction context that ended
        """
        # Remove from stack if still there
        if context in self._transaction_stack:
            self._transaction_stack.remove(context)

    def _begin_nested_transaction(self, context: Any):
        """Begin a nested transaction.

        Args:
            context: Nested transaction context
        """
        self._transaction_stack.append(context)

    def _end_nested_transaction(self, context: Any):
        """End a nested transaction.

        Args:
            context: Nested transaction context
        """
        if context in self._transaction_stack:
            self._transaction_stack.remove(context)

    def _create_savepoint(self) -> Dict:
        """Create a savepoint of current state.

        Returns:
            Savepoint data
        """
        # For now, return empty dict
        # Real implementation would serialize model state
        return {}

    def _restore_savepoint(self, savepoint: Dict):
        """Restore from a savepoint.

        Args:
            savepoint: Savepoint data to restore
        """
        # Real implementation would deserialize and restore state
        pass

    @property
    def in_transaction(self) -> bool:
        """Check if currently in a transaction.

        Returns:
            True if in transaction
        """
        return len(self._transaction_stack) > 0
```

**Validation**:
- Controller tracks transaction stack
- Supports nested transactions
- Provides transaction status

---

### Task P0.6.3: Create Transaction Tests
**Title**: Write tests for transaction system
**Dependencies**: P0.6.1, P0.6.2
**File**: `tests/test_transactions.py`

**Implementation**:
```python
"""Tests for transaction management."""

import unittest
from vfwidgets_multisplit.controller.controller import PaneController
from vfwidgets_multisplit.controller.transaction import (
    TransactionContext,
    transaction,
    atomic_operation
)


class MockModel:
    """Mock model for testing."""
    def __init__(self):
        self.value = 0
        self.history = []


class MockCommand:
    """Mock command for testing."""
    def __init__(self, value):
        self.value = value
        self.executed = False
        self.undone = False

    def execute(self, model):
        model.value += self.value
        model.history.append(f"add {self.value}")
        self.executed = True
        return True

    def undo(self, model):
        model.value -= self.value
        model.history.append(f"undo add {self.value}")
        self.undone = True
        return True


class TestTransactions(unittest.TestCase):
    """Test transaction management."""

    def test_basic_transaction(self):
        """Test basic transaction commit."""
        model = MockModel()
        controller = PaneController(model)

        with TransactionContext(controller) as tx:
            cmd = MockCommand(5)
            cmd.execute(model)
            tx.add_command(cmd)

        # Transaction should be committed
        self.assertTrue(tx.committed)
        self.assertFalse(tx.rolled_back)
        self.assertEqual(model.value, 5)

    def test_transaction_rollback(self):
        """Test transaction rollback on exception."""
        model = MockModel()
        controller = PaneController(model)

        try:
            with TransactionContext(controller) as tx:
                cmd = MockCommand(5)
                cmd.execute(model)
                tx.add_command(cmd)
                raise ValueError("Test error")
        except ValueError:
            pass

        # Transaction should be rolled back
        self.assertFalse(tx.committed)
        self.assertTrue(tx.rolled_back)

        # Command should be undone
        self.assertTrue(cmd.undone)

    def test_manual_rollback(self):
        """Test manual transaction rollback."""
        model = MockModel()
        controller = PaneController(model)

        with TransactionContext(controller) as tx:
            cmd = MockCommand(5)
            cmd.execute(model)
            tx.add_command(cmd)

            # Manually rollback
            tx.rollback()

        self.assertTrue(tx.rolled_back)
        self.assertFalse(tx.committed)

    def test_transaction_context_manager(self):
        """Test transaction convenience function."""
        model = MockModel()
        controller = PaneController(model)

        with transaction(controller) as tx:
            cmd = MockCommand(10)
            cmd.execute(model)
            tx.add_command(cmd)

        self.assertTrue(tx.committed)
        self.assertEqual(model.value, 10)

    def test_atomic_operation(self):
        """Test named atomic operation."""
        model = MockModel()
        controller = PaneController(model)

        with atomic_operation(controller, "test_operation") as tx:
            cmd = MockCommand(15)
            cmd.execute(model)
            tx.add_command(cmd)

        self.assertTrue(tx.committed)
        self.assertEqual(tx.operation_name, "test_operation")

    def test_transaction_status(self):
        """Test transaction status tracking."""
        model = MockModel()
        controller = PaneController(model)

        # Not in transaction initially
        self.assertFalse(controller.in_transaction)

        with TransactionContext(controller):
            # In transaction within context
            self.assertTrue(controller.in_transaction)

        # Not in transaction after exit
        self.assertFalse(controller.in_transaction)


if __name__ == '__main__':
    unittest.main()
```

**Validation**:
Run tests: `python -m pytest tests/test_transactions.py -v`

---

## Task Validation Checklist

### Phase 0 Completion Criteria

- [ ] **P0.1: ID Generation System**
  - [ ] All ID types defined (PaneId, NodeId, WidgetId)
  - [ ] Generation functions create unique IDs
  - [ ] Validation functions work correctly
  - [ ] All tests pass

- [ ] **P0.2: Tree Utilities**
  - [ ] Node classes implement visitor pattern
  - [ ] Tree traversal functions work
  - [ ] Validation catches all invariant violations
  - [ ] All tests pass

- [ ] **P0.3: Signal Bridge**
  - [ ] Abstract signals work without Qt
  - [ ] Bridge connects to Qt signals
  - [ ] No memory leaks from references
  - [ ] All tests pass

- [ ] **P0.4: Geometry Calculator**
  - [ ] Calculates pixel-perfect bounds
  - [ ] Handles divider positioning
  - [ ] No gaps or overlaps
  - [ ] All tests pass

- [ ] **P0.5: Tree Reconciler**
  - [ ] Correctly identifies all changes
  - [ ] Minimizes widget recreation
  - [ ] Handles edge cases
  - [ ] All tests pass

- [ ] **P0.6: Transaction Context**
  - [ ] Atomic operations work
  - [ ] Rollback restores state
  - [ ] Nested transactions supported
  - [ ] All tests pass

### Integration Validation

Run all Phase 0 tests together:
```bash
python -m pytest tests/test_id_generation.py tests/test_tree_utils.py tests/test_signals.py tests/test_geometry.py tests/test_reconciler.py tests/test_transactions.py -v
```

All tests should pass before proceeding to Phase 1.