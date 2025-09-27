# Phase 0 Implementation Tasks (Updated)

## ⚠️ IMPORTANT: Existing Code Context

**Current State**: The project has some existing code that needs to be enhanced and reorganized.

### Existing Files:
- `src/vfwidgets_multisplit/core/types.py` - EXISTS with partial implementation
  - Has: PaneId, Orientation, WherePosition, Direction, exceptions, Size, Position, Rect
  - Missing: NodeId, WidgetId, Bounds
  - Has functions that need moving: generate_pane_id(), validate_ratio(), normalize_ratios()

### Migration Strategy:
1. **Enhance** existing files (don't delete)
2. **Move** misplaced functions to proper modules
3. **Add** new functionality incrementally
4. **Preserve** all existing functionality

---

## Task Structure

Each task contains:
- **Task ID**: Unique identifier for tracking
- **Title**: Clear, actionable description
- **Dependencies**: Required prior tasks
- **Current State**: What exists already
- **Action**: What to do (Create/Modify/Move)
- **Implementation**: Complete code specification
- **Validation**: How to verify correctness

---

## P0.1: ID Generation System

### Task P0.1.1: Enhance Type System
**Title**: Add NodeId and WidgetId types to existing core/types.py
**Dependencies**: None
**Action**: MODIFY existing file
**File**: `src/vfwidgets_multisplit/core/types.py`

**Current State**:
```python
# Line 14-15 currently has:
# Type aliases
PaneId = NewType('PaneId', str)
```

**Implementation**:
Add immediately after line 15:
```python
NodeId = NewType('NodeId', str)
WidgetId = NewType('WidgetId', str)
```

**Note**: Do NOT modify existing PaneId or other existing code.

**Validation**:
```python
from vfwidgets_multisplit.core.types import PaneId, NodeId, WidgetId
# All three types should import successfully
```

---

### Task P0.1.2: Create ID Generation Module
**Title**: Create core/utils.py and move generate_pane_id from types.py
**Dependencies**: P0.1.1
**Action**: CREATE new file + MOVE function
**File**: `src/vfwidgets_multisplit/core/utils.py`

**Current State**:
- `generate_pane_id()` currently exists in types.py (lines 96-99)
- This function needs to be moved to the new utils.py

**Implementation**:
1. Create new file `src/vfwidgets_multisplit/core/utils.py`:
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

2. Remove `generate_pane_id()` function from types.py (delete lines 96-99)

3. Update any imports if needed

**Validation**:
```python
from vfwidgets_multisplit.core.utils import generate_pane_id, generate_node_id, generate_widget_id
# All functions should import and work
```

---

### Task P0.1.3: Move Validation Functions
**Title**: Move validate_ratio functions from types.py to utils.py
**Dependencies**: P0.1.2
**Action**: MOVE functions
**Files**:
- `src/vfwidgets_multisplit/core/types.py` (remove from)
- `src/vfwidgets_multisplit/core/utils.py` (add to)

**Current State**:
- `validate_ratio()` exists in types.py (lines 102-105)
- `validate_ratios()` exists in types.py (lines 108-119)

**Implementation**:
1. Add to utils.py (after the generate functions):
```python
def validate_ratio(ratio: float) -> None:
    """Validate a single ratio value."""
    from .types import InvalidRatioError
    if not 0.0 < ratio < 1.0:
        raise InvalidRatioError([ratio], "Ratio must be between 0 and 1")


def validate_ratios(ratios: list[float]) -> None:
    """Validate a list of split ratios."""
    from .types import InvalidRatioError
    if len(ratios) < 2:
        raise InvalidRatioError(ratios, "At least 2 ratios required")

    total = sum(ratios)
    if abs(total - 1.0) > 0.001:  # Allow small floating point errors
        raise InvalidRatioError(ratios, f"Ratios must sum to 1.0, got {total}")

    for ratio in ratios:
        if ratio <= 0:
            raise InvalidRatioError(ratios, f"All ratios must be positive, got {ratio}")


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

2. Remove these functions from types.py (lines 102-105 and 108-119)

**Note**: Keep `normalize_ratios()` in types.py for now - it will be moved to tree_utils.py in P0.2.3.

**Validation**:
```python
from vfwidgets_multisplit.core.utils import validate_ratio, validate_ratios, validate_id_format
# Functions should work correctly
```

---

### Task P0.1.4: Create ID Tests
**Title**: Write comprehensive tests for ID generation
**Dependencies**: P0.1.1, P0.1.2, P0.1.3
**Action**: CREATE new file
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
**Action**: CREATE new file
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
```python
from vfwidgets_multisplit.core.nodes import PaneNode, LeafNode, SplitNode
# Classes should import successfully
```

---

### Task P0.2.2: Create Visitor Pattern
**Title**: Create core/visitor.py with visitor interface
**Dependencies**: P0.2.1
**Action**: CREATE new file
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
```python
from vfwidgets_multisplit.core.visitor import NodeVisitor
# Should import successfully
```

---

### Task P0.2.3: Create Tree Utilities Module
**Title**: Create core/tree_utils.py and move normalize_ratios from types.py
**Dependencies**: P0.2.1, P0.2.2
**Action**: CREATE new file + MOVE function
**File**: `src/vfwidgets_multisplit/core/tree_utils.py`

**Current State**:
- `normalize_ratios()` currently exists in types.py (lines 122-128)
- This function needs to be moved to the new tree_utils.py

**Implementation**:
1. Create new file with moved and new functions:
```python
"""Tree manipulation utilities.

Core tree operations and validation functions.
"""

from typing import Optional, List
from .types import PaneId, InvalidRatioError, InvalidStructureError
from .nodes import PaneNode, LeafNode, SplitNode
from .visitor import NodeVisitor


def normalize_ratios(ratios: List[float]) -> List[float]:
    """Normalize ratios to sum to 1.0.

    Note: This function was moved from types.py
    """
    total = sum(ratios)
    if total == 0:
        # Equal distribution if all zeros
        return [1.0 / len(ratios)] * len(ratios)
    return [r / total for r in ratios]


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
            self.errors.append("Invalid ratios in split node")

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

2. Remove `normalize_ratios()` from types.py (lines 122-128)

**Validation**:
```python
from vfwidgets_multisplit.core.tree_utils import normalize_ratios, find_node_by_id
# Functions should import and work
```

---

## P0.3: Signal Bridge

[Continue with same pattern - noting what exists, what to modify, what to create]

## P0.4: Geometry Calculator

### Task P0.4.1: Add Bounds to Type System
**Title**: Add Bounds class to existing core/types.py
**Dependencies**: P0.1.1
**Action**: MODIFY existing file
**File**: `src/vfwidgets_multisplit/core/types.py`

**Current State**:
- File has Size, Position, Rect dataclasses
- Missing Bounds dataclass

**Implementation**:
Add after Rect class (around line 169):
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
```python
from vfwidgets_multisplit.core.types import Bounds
# Should import and work
```

[Continue with remaining P0.4, P0.5, P0.6 tasks...]

## Summary of Changes from Original

### Key Differences:
1. **P0.1.1**: MODIFY existing types.py instead of assuming it's empty
2. **P0.1.2**: CREATE utils.py AND MOVE generate_pane_id from types.py
3. **P0.1.3**: NEW TASK - Move validation functions from types.py to utils.py
4. **P0.2.3**: MOVE normalize_ratios from types.py to tree_utils.py
5. **P0.4.1**: ADD Bounds to existing types.py (not create from scratch)

### Functions to Move:
- `generate_pane_id()` → utils.py (P0.1.2)
- `validate_ratio()` → utils.py (P0.1.3)
- `validate_ratios()` → utils.py (P0.1.3)
- `normalize_ratios()` → tree_utils.py (P0.2.3)

### What to Keep in types.py:
- All existing type definitions (PaneId)
- All enums (Orientation, WherePosition, Direction)
- All exceptions
- All existing dataclasses (Size, Position, Rect)

This ensures backward compatibility while achieving proper code organization.