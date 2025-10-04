# Tree Structure Architecture

## Overview

MultiSplit organizes layout as a **binary tree** where each node represents either a split container or a leaf pane. This tree structure provides predictable layout behavior, efficient operations, and natural persistence while maintaining clean invariants.

## Prerequisites

The tree structure requires **Phase 0 foundations**:

- **ID Generation**: Unique, stable identifiers for panes and nodes
- **Tree Utilities**: Validation, traversal, and manipulation functions
- **Geometry Calculator**: Convert tree structure to pixel positions
- **Reconciliation Types**: Data structures for tree comparison and updates

See [MVP Implementation Plan](../../mvp-implementation-PLAN.md#phase-0-critical-foundations-must-have-first) for Phase 0 details.

---

## Tree Fundamentals

### Binary Tree Structure

Every MultiSplit layout is a **strict binary tree** where:

- **Leaf nodes** contain exactly one widget (terminal nodes)
- **Split nodes** contain exactly two children (internal nodes)
- **No empty splits** - splits with one child are automatically collapsed
- **Root can be either** - single widget (leaf) or split container

```
Tree Example:
                Split(H, [0.3, 0.7])
               /                    \
    Leaf(explorer)              Split(V, [0.6, 0.4])
                               /                    \
                    Leaf(editor)                Split(H, [0.5, 0.5])
                                               /                    \
                                    Leaf(terminal)             Leaf(output)
```

### Visual Layout Result

```
┌─────────────┬─────────────────────────────────┐
│             │           Editor                │
│   Explorer  │                                 │
│             ├─────────────────┬───────────────┤
│             │    Terminal     │    Output     │
│             │                 │               │
└─────────────┴─────────────────┴───────────────┘
```

---

## Node Types

### Abstract Base Node

```python
from abc import ABC, abstractmethod
from typing import Any, Optional
from core.types import PaneId, NodeId, Bounds
from core.visitor import NodeVisitor

class PaneNode(ABC):
    """Abstract base class for all tree nodes"""

    @abstractmethod
    def accept(self, visitor: NodeVisitor) -> Any:
        """Visitor pattern support for tree operations"""

    @abstractmethod
    def clone(self) -> 'PaneNode':
        """Create deep copy of node and subtree"""

    @abstractmethod
    def validate(self) -> ValidationResult:
        """Validate node structure and constraints"""

    @abstractmethod
    def get_all_pane_ids(self) -> set[PaneId]:
        """Get all pane IDs in this subtree"""

    @abstractmethod
    def serialize(self) -> dict:
        """Convert to JSON-serializable dictionary"""

    @classmethod
    @abstractmethod
    def deserialize(cls, data: dict) -> 'PaneNode':
        """Create node from serialized data"""
```

### Leaf Node (Widget Container)

```python
@dataclass
class LeafNode(PaneNode):
    """Terminal node containing a single widget"""

    # Identity (immutable after creation)
    pane_id: PaneId           # Stable pane identifier
    widget_id: WidgetId       # Opaque widget identifier

    # Constraints (mutable)
    constraints: SizeConstraints = field(default_factory=SizeConstraints)

    # State (mutable)
    state: NodeState = field(default_factory=NodeState)

    # Metadata (mutable)
    metadata: dict = field(default_factory=dict)

    def accept(self, visitor: NodeVisitor) -> Any:
        """Visitor pattern implementation"""
        return visitor.visit_leaf(self)

    def validate(self) -> ValidationResult:
        """Validate leaf node"""
        errors = []

        if not self.pane_id:
            errors.append("Leaf node missing pane_id")

        if not self.widget_id:
            errors.append("Leaf node missing widget_id")

        # Validate constraints
        if self.constraints.min_width < 0:
            errors.append("Invalid minimum width")

        return ValidationResult(len(errors) == 0, errors)

    def get_all_pane_ids(self) -> set[PaneId]:
        """Return own pane ID"""
        return {self.pane_id}

    def serialize(self) -> dict:
        """Convert to dictionary"""
        return {
            "type": "leaf",
            "pane_id": self.pane_id,
            "widget_id": self.widget_id,
            "constraints": self.constraints.serialize() if self.constraints else None,
            "state": self.state.serialize() if self.state else None,
            "metadata": self.metadata
        }

    @classmethod
    def deserialize(cls, data: dict) -> 'LeafNode':
        """Create from dictionary"""
        return cls(
            pane_id=PaneId(data["pane_id"]),
            widget_id=WidgetId(data["widget_id"]),
            constraints=SizeConstraints.deserialize(data.get("constraints")),
            state=NodeState.deserialize(data.get("state")),
            metadata=data.get("metadata", {})
        )
```

### Split Node (Container)

```python
@dataclass
class SplitNode(PaneNode):
    """Internal node containing exactly two children"""

    # Identity (immutable after creation)
    node_id: NodeId           # Stable node identifier

    # Structure (mutable)
    orientation: Orientation  # HORIZONTAL or VERTICAL
    children: list[PaneNode]  # Exactly 2 children
    ratios: list[float]       # Space allocation [0.0-1.0], sums to 1.0

    # Layout cache (mutable)
    divider_positions: list[int] = field(default_factory=list)

    # Constraints (mutable)
    constraints: SizeConstraints = field(default_factory=SizeConstraints)

    # State (mutable)
    state: NodeState = field(default_factory=NodeState)

    # Metadata (mutable)
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        """Validate and normalize after creation"""
        if len(self.children) != 2:
            raise InvalidStructureError(f"SplitNode must have exactly 2 children, got {len(self.children)}")

        if len(self.ratios) != 2:
            self.ratios = [0.5, 0.5]  # Default equal split

        # Normalize ratios to sum to 1.0
        self.ratios = normalize_ratios(self.ratios)

    def accept(self, visitor: NodeVisitor) -> Any:
        """Visitor pattern implementation"""
        return visitor.visit_split(self)

    def validate(self) -> ValidationResult:
        """Validate split node and children"""
        errors = []

        # Validate basic structure
        if not self.node_id:
            errors.append("Split node missing node_id")

        if len(self.children) != 2:
            errors.append(f"Split node must have exactly 2 children, got {len(self.children)}")

        if len(self.ratios) != 2:
            errors.append(f"Split node must have exactly 2 ratios, got {len(self.ratios)}")

        # Validate ratios
        if not validate_ratios(self.ratios):
            errors.append(f"Invalid ratios: {self.ratios} (must sum to 1.0)")

        for ratio in self.ratios:
            if not (0.0 < ratio < 1.0):
                errors.append(f"Ratio {ratio} out of range (0.0, 1.0)")

        # Validate children recursively
        for i, child in enumerate(self.children):
            child_result = child.validate()
            if not child_result.is_valid:
                errors.extend([f"Child {i}: {error}" for error in child_result.messages])

        # Check for duplicate pane IDs
        all_pane_ids = self.get_all_pane_ids()
        if len(all_pane_ids) != len(set(all_pane_ids)):
            errors.append("Duplicate pane IDs found in subtree")

        return ValidationResult(len(errors) == 0, errors)

    def get_all_pane_ids(self) -> set[PaneId]:
        """Get all pane IDs from children"""
        all_ids = set()
        for child in self.children:
            all_ids.update(child.get_all_pane_ids())
        return all_ids

    def serialize(self) -> dict:
        """Convert to dictionary"""
        return {
            "type": "split",
            "node_id": self.node_id,
            "orientation": self.orientation.value,
            "ratios": self.ratios,
            "children": [child.serialize() for child in self.children],
            "constraints": self.constraints.serialize() if self.constraints else None,
            "state": self.state.serialize() if self.state else None,
            "metadata": self.metadata
        }

    @classmethod
    def deserialize(cls, data: dict) -> 'SplitNode':
        """Create from dictionary"""
        children = [PaneNode.deserialize_node(child_data)
                   for child_data in data["children"]]

        return cls(
            node_id=NodeId(data["node_id"]),
            orientation=Orientation(data["orientation"]),
            children=children,
            ratios=data["ratios"],
            constraints=SizeConstraints.deserialize(data.get("constraints")),
            state=NodeState.deserialize(data.get("state")),
            metadata=data.get("metadata", {})
        )
```

---

## Tree Operations

### Finding Nodes

```python
class TreeOperations:
    """Core tree manipulation operations"""

    @staticmethod
    def find_node_by_id(root: PaneNode, pane_id: PaneId) -> Optional[PaneNode]:
        """Find node with specific pane ID"""

        class FindVisitor(NodeVisitor):
            def __init__(self, target_id: PaneId):
                self.target_id = target_id
                self.found_node = None

            def visit_leaf(self, node: LeafNode) -> None:
                if node.pane_id == target_id:
                    self.found_node = node

            def visit_split(self, node: SplitNode) -> None:
                for child in node.children:
                    if self.found_node is None:
                        child.accept(self)

        visitor = FindVisitor(pane_id)
        root.accept(visitor)
        return visitor.found_node

    @staticmethod
    def find_parent(root: PaneNode, target_node: PaneNode) -> Optional[SplitNode]:
        """Find parent of target node"""

        class ParentFinder(NodeVisitor):
            def __init__(self, target: PaneNode):
                self.target = target
                self.parent = None

            def visit_leaf(self, node: LeafNode) -> None:
                # Leaves have no children
                pass

            def visit_split(self, node: SplitNode) -> None:
                # Check if any child matches target
                if self.target in node.children:
                    self.parent = node
                else:
                    # Recurse to children
                    for child in node.children:
                        if self.parent is None:
                            child.accept(self)

        visitor = ParentFinder(target_node)
        root.accept(visitor)
        return visitor.parent

    @staticmethod
    def get_path_to_node(root: PaneNode, target_id: PaneId) -> list[PaneNode]:
        """Get path from root to target node"""

        class PathFinder(NodeVisitor):
            def __init__(self, target_id: PaneId):
                self.target_id = target_id
                self.path = []
                self.found = False

            def visit_leaf(self, node: LeafNode) -> list[PaneNode]:
                current_path = self.path + [node]
                if node.pane_id == self.target_id:
                    self.found = True
                    return current_path
                return []

            def visit_split(self, node: SplitNode) -> list[PaneNode]:
                current_path = self.path + [node]
                self.path = current_path

                for child in node.children:
                    result = child.accept(self)
                    if self.found:
                        return result

                # Backtrack
                self.path = self.path[:-1]
                return []

        visitor = PathFinder(target_id)
        return root.accept(visitor)
```

### Splitting Operations

```python
class SplittingOperations:
    """Operations for splitting panes"""

    @staticmethod
    def split_leaf(leaf: LeafNode, where: WherePosition, new_widget_id: WidgetId,
                   ratio: float, new_pane_id: PaneId, split_id: NodeId) -> SplitNode:
        """Split a leaf node into two leaves"""

        # Create new leaf
        new_leaf = LeafNode(new_pane_id, new_widget_id)

        # Determine orientation based on split direction
        if where in [WherePosition.LEFT, WherePosition.RIGHT]:
            orientation = Orientation.HORIZONTAL
        else:  # TOP, BOTTOM
            orientation = Orientation.VERTICAL

        # Determine child order
        if where in [WherePosition.LEFT, WherePosition.TOP]:
            children = [new_leaf, leaf]  # New first
            ratios = [ratio, 1.0 - ratio]
        else:  # RIGHT, BOTTOM
            children = [leaf, new_leaf]  # Original first
            ratios = [1.0 - ratio, ratio]

        # Create split node
        split = SplitNode(
            node_id=split_id,
            orientation=orientation,
            children=children,
            ratios=ratios
        )

        return split

    @staticmethod
    def close_leaf(split: SplitNode, leaf_to_close: LeafNode) -> PaneNode:
        """Remove leaf from split, return remaining child"""

        if leaf_to_close not in split.children:
            raise InvalidOperationError("Leaf not found in split")

        # Find remaining child
        remaining_child = None
        for child in split.children:
            if child != leaf_to_close:
                remaining_child = child
                break

        if remaining_child is None:
            raise InvalidStructureError("No remaining child found")

        # Return the remaining child to replace the split
        return remaining_child

    @staticmethod
    def resize_split(split: SplitNode, child_index: int, new_ratio: float) -> None:
        """Resize split by changing ratios"""

        if not (0.0 < new_ratio < 1.0):
            raise InvalidOperationError(f"Invalid ratio: {new_ratio}")

        if child_index not in [0, 1]:
            raise InvalidOperationError(f"Invalid child index: {child_index}")

        # Update ratios
        split.ratios[child_index] = new_ratio
        split.ratios[1 - child_index] = 1.0 - new_ratio

        # Clear cached positions
        split.divider_positions.clear()
```

---

## Geometric Calculations

### Bounds Calculation

```python
class GeometryCalculator:
    """Calculate pixel positions from tree structure"""

    def calculate_bounds(self, root: PaneNode, container_bounds: Bounds) -> dict[PaneId, Bounds]:
        """Calculate bounds for all panes in tree"""

        result = {}
        self._calculate_recursive(root, container_bounds, result)
        return result

    def _calculate_recursive(self, node: PaneNode, bounds: Bounds,
                           result: dict[PaneId, Bounds]) -> None:
        """Recursive bounds calculation"""

        if isinstance(node, LeafNode):
            # Leaf node gets the full bounds
            result[node.pane_id] = bounds

        elif isinstance(node, SplitNode):
            # Split bounds between children
            child_bounds = self._split_bounds(bounds, node.orientation, node.ratios)

            for child, child_bound in zip(node.children, child_bounds):
                self._calculate_recursive(child, child_bound, result)

    def _split_bounds(self, bounds: Bounds, orientation: Orientation,
                     ratios: list[float]) -> list[Bounds]:
        """Split bounds according to orientation and ratios"""

        if orientation == Orientation.HORIZONTAL:
            # Split horizontally (left/right)
            left_width = int(bounds.width * ratios[0])
            right_width = bounds.width - left_width

            return [
                Bounds(bounds.x, bounds.y, left_width, bounds.height),
                Bounds(bounds.x + left_width, bounds.y, right_width, bounds.height)
            ]

        else:  # VERTICAL
            # Split vertically (top/bottom)
            top_height = int(bounds.height * ratios[0])
            bottom_height = bounds.height - top_height

            return [
                Bounds(bounds.x, bounds.y, bounds.width, top_height),
                Bounds(bounds.x, bounds.y + top_height, bounds.width, bottom_height)
            ]

    def calculate_divider_positions(self, root: PaneNode, container_bounds: Bounds) -> dict[NodeId, list[int]]:
        """Calculate divider positions for all splits"""

        result = {}
        self._calculate_dividers_recursive(root, container_bounds, result)
        return result

    def _calculate_dividers_recursive(self, node: PaneNode, bounds: Bounds,
                                    result: dict[NodeId, list[int]]) -> None:
        """Calculate divider positions recursively"""

        if isinstance(node, SplitNode):
            # Calculate divider position
            if node.orientation == Orientation.HORIZONTAL:
                divider_x = bounds.x + int(bounds.width * node.ratios[0])
                result[node.node_id] = [divider_x]
            else:  # VERTICAL
                divider_y = bounds.y + int(bounds.height * node.ratios[0])
                result[node.node_id] = [divider_y]

            # Recurse to children
            child_bounds = self._split_bounds(bounds, node.orientation, node.ratios)
            for child, child_bound in zip(node.children, child_bounds):
                self._calculate_dividers_recursive(child, child_bound, result)
```

---

## Tree Navigation

### Neighbor Finding

```python
class NavigationOperations:
    """Operations for navigating between panes"""

    @staticmethod
    def find_neighbor(root: PaneNode, pane_id: PaneId, direction: Direction) -> Optional[PaneId]:
        """Find neighboring pane in given direction"""

        # Get path to current pane
        path = TreeOperations.get_path_to_node(root, pane_id)
        if not path:
            return None

        # Start from current pane and walk up tree
        for i in range(len(path) - 2, -1, -1):  # Skip leaf, walk up
            current_node = path[i]

            if isinstance(current_node, SplitNode):
                # Check if this split can provide neighbor in direction
                neighbor_id = NavigationOperations._check_split_neighbor(
                    current_node, path[i + 1], direction
                )
                if neighbor_id:
                    return neighbor_id

        return None  # No neighbor found

    @staticmethod
    def _check_split_neighbor(split: SplitNode, from_child: PaneNode,
                            direction: Direction) -> Optional[PaneId]:
        """Check if split can provide neighbor in direction"""

        # Find index of child we came from
        from_index = split.children.index(from_child)

        # Check if split orientation matches direction
        if direction in [Direction.LEFT, Direction.RIGHT]:
            if split.orientation != Orientation.HORIZONTAL:
                return None  # Can't go left/right in vertical split

            if direction == Direction.LEFT and from_index == 1:
                # Can go left to first child
                return NavigationOperations._get_rightmost_pane(split.children[0])
            elif direction == Direction.RIGHT and from_index == 0:
                # Can go right to second child
                return NavigationOperations._get_leftmost_pane(split.children[1])

        elif direction in [Direction.UP, Direction.DOWN]:
            if split.orientation != Orientation.VERTICAL:
                return None  # Can't go up/down in horizontal split

            if direction == Direction.UP and from_index == 1:
                # Can go up to first child
                return NavigationOperations._get_bottommost_pane(split.children[0])
            elif direction == Direction.DOWN and from_index == 0:
                # Can go down to second child
                return NavigationOperations._get_topmost_pane(split.children[1])

        return None

    @staticmethod
    def _get_leftmost_pane(node: PaneNode) -> PaneId:
        """Get leftmost pane in subtree"""
        if isinstance(node, LeafNode):
            return node.pane_id
        elif isinstance(node, SplitNode):
            if node.orientation == Orientation.HORIZONTAL:
                return NavigationOperations._get_leftmost_pane(node.children[0])
            else:
                # For vertical splits, just pick first child
                return NavigationOperations._get_leftmost_pane(node.children[0])

    @staticmethod
    def get_pane_sequence(root: PaneNode) -> list[PaneId]:
        """Get all panes in left-to-right, top-to-bottom order"""

        class SequenceVisitor(NodeVisitor):
            def __init__(self):
                self.sequence = []

            def visit_leaf(self, node: LeafNode) -> None:
                self.sequence.append(node.pane_id)

            def visit_split(self, node: SplitNode) -> None:
                # Visit children in order
                for child in node.children:
                    child.accept(self)

        visitor = SequenceVisitor()
        root.accept(visitor)
        return visitor.sequence
```

---

## Tree Validation

### Comprehensive Validation

```python
class TreeValidator:
    """Comprehensive tree structure validation"""

    @staticmethod
    def validate_tree(root: PaneNode) -> ValidationResult:
        """Validate entire tree structure"""

        validator = TreeValidator()
        return validator._validate_recursive(root, set())

    def _validate_recursive(self, node: PaneNode, seen_pane_ids: set[PaneId]) -> ValidationResult:
        """Validate node and all children"""

        errors = []

        # Validate this node
        node_result = node.validate()
        if not node_result.is_valid:
            errors.extend(node_result.messages)

        # Check for duplicate pane IDs
        if isinstance(node, LeafNode):
            if node.pane_id in seen_pane_ids:
                errors.append(f"Duplicate pane ID: {node.pane_id}")
            seen_pane_ids.add(node.pane_id)

        elif isinstance(node, SplitNode):
            # Validate children recursively
            for i, child in enumerate(node.children):
                child_result = self._validate_recursive(child, seen_pane_ids)
                if not child_result.is_valid:
                    errors.extend([f"Child {i}: {error}" for error in child_result.messages])

        return ValidationResult(len(errors) == 0, errors)

    @staticmethod
    def validate_ratios(ratios: list[float], tolerance: float = 0.01) -> bool:
        """Validate that ratios sum to approximately 1.0"""
        if not ratios:
            return False

        total = sum(ratios)
        return abs(total - 1.0) <= tolerance

    @staticmethod
    def check_tree_balance(root: PaneNode) -> dict:
        """Check tree balance and return statistics"""

        class BalanceChecker(NodeVisitor):
            def __init__(self):
                self.leaf_depths = []
                self.split_count = 0
                self.leaf_count = 0
                self.current_depth = 0

            def visit_leaf(self, node: LeafNode) -> None:
                self.leaf_depths.append(self.current_depth)
                self.leaf_count += 1

            def visit_split(self, node: SplitNode) -> None:
                self.split_count += 1
                self.current_depth += 1

                for child in node.children:
                    child.accept(self)

                self.current_depth -= 1

        checker = BalanceChecker()
        root.accept(checker)

        return {
            "leaf_count": checker.leaf_count,
            "split_count": checker.split_count,
            "max_depth": max(checker.leaf_depths) if checker.leaf_depths else 0,
            "min_depth": min(checker.leaf_depths) if checker.leaf_depths else 0,
            "average_depth": sum(checker.leaf_depths) / len(checker.leaf_depths) if checker.leaf_depths else 0,
            "is_balanced": max(checker.leaf_depths) - min(checker.leaf_depths) <= 1 if checker.leaf_depths else True
        }
```

---

## Serialization Format

### JSON Structure

```json
{
  "version": 1,
  "root": {
    "type": "split",
    "node_id": "split-001",
    "orientation": "horizontal",
    "ratios": [0.3, 0.7],
    "children": [
      {
        "type": "leaf",
        "pane_id": "pane-001",
        "widget_id": "file_tree",
        "constraints": {
          "min_width": 200,
          "min_height": 100
        },
        "metadata": {
          "title": "File Explorer"
        }
      },
      {
        "type": "split",
        "node_id": "split-002",
        "orientation": "vertical",
        "ratios": [0.7, 0.3],
        "children": [
          {
            "type": "leaf",
            "pane_id": "pane-002",
            "widget_id": "editor:main.py",
            "constraints": {
              "min_width": 300,
              "min_height": 200
            }
          },
          {
            "type": "leaf",
            "pane_id": "pane-003",
            "widget_id": "terminal:1",
            "constraints": {
              "min_width": 300,
              "min_height": 100
            }
          }
        ]
      }
    ]
  },
  "metadata": {
    "created": "2024-01-01T00:00:00Z",
    "focused_pane_id": "pane-002"
  }
}
```

### Serialization Implementation

```python
class TreeSerializer:
    """Convert tree to/from JSON format"""

    @staticmethod
    def serialize_tree(root: PaneNode, metadata: dict = None) -> dict:
        """Convert tree to JSON-serializable dict"""

        return {
            "version": 1,
            "root": root.serialize(),
            "metadata": metadata or {}
        }

    @staticmethod
    def deserialize_tree(data: dict) -> tuple[PaneNode, dict]:
        """Convert dict back to tree"""

        # Check version compatibility
        version = data.get("version", 1)
        if version > 1:
            raise LayoutVersionError(f"Unsupported layout version: {version}")

        # Deserialize root node
        root_data = data["root"]
        root = PaneNode.deserialize_node(root_data)

        # Extract metadata
        metadata = data.get("metadata", {})

        return root, metadata

    @staticmethod
    def migrate_layout(data: dict, target_version: int = 1) -> dict:
        """Migrate layout data between versions"""

        current_version = data.get("version", 1)

        if current_version == target_version:
            return data

        # Add migration logic as needed
        # For now, only version 1 exists

        return data
```

---

## Quick Reference

### Tree Invariants

| Invariant | Description | Enforcement |
|-----------|-------------|-------------|
| **Binary Structure** | Every split has exactly 2 children | Validated in `__post_init__` |
| **No Empty Splits** | Splits with <2 children are removed | Automatic cleanup in operations |
| **Ratio Sum** | Split ratios always sum to 1.0 | Normalized in `__post_init__` |
| **Unique Pane IDs** | No duplicate pane IDs in tree | Validated recursively |
| **Valid Ratios** | All ratios in range (0.0, 1.0) | Validated in operations |

### Node Type Quick Reference

| Node Type | Contains | Purpose | Children |
|-----------|----------|---------|----------|
| **LeafNode** | Widget ID | Display widget | None |
| **SplitNode** | Children + Ratios | Layout container | Exactly 2 |

### Common Operations

```python
# Find node by pane ID
node = TreeOperations.find_node_by_id(root, pane_id)

# Find parent of node
parent = TreeOperations.find_parent(root, node)

# Split a leaf
new_split = SplittingOperations.split_leaf(leaf, WherePosition.RIGHT, new_widget_id, 0.5, new_pane_id, split_id)

# Navigate to neighbor
neighbor_id = NavigationOperations.find_neighbor(root, pane_id, Direction.RIGHT)

# Calculate bounds
bounds_map = geometry_calc.calculate_bounds(root, container_bounds)

# Validate tree
result = TreeValidator.validate_tree(root)
```

### Validation Checklist

- ✅ All splits have exactly 2 children
- ✅ All ratios sum to 1.0 ± tolerance
- ✅ No duplicate pane IDs
- ✅ All references are valid
- ✅ Tree structure is acyclic
- ✅ Constraints are reasonable

## Related Documents

- **[Core Concepts](../01-overview/core-concepts.md)** - Tree structure overview
- **[MVC Architecture](mvc-architecture.md)** - How tree fits in model layer
- **[Widget Provider](widget-provider.md)** - How widget IDs are used
- **[MVP Implementation Plan](../../mvp-implementation-PLAN.md)** - Phase 0 tree utilities
- **[Splitting Algorithm Design](../../splitting-algorithm-DESIGN.md)** - Detailed splitting logic

---

The tree structure is the foundation that makes MultiSplit's layout predictable, efficient, and persistent while maintaining clean invariants throughout all operations.