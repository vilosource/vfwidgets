"""Tree manipulation utilities.

Core tree operations and validation functions.
"""

from typing import Optional

from .nodes import LeafNode, PaneNode, SplitNode
from .types import NodeId, PaneId
from .visitor import NodeVisitor


def normalize_ratios(ratios: list[float]) -> list[float]:
    """Normalize ratios to sum to 1.0.

    Note: This function was moved from types.py
    """
    total = sum(ratios)
    if total == 0:
        # Equal distribution if all zeros
        return [1.0 / len(ratios)] * len(ratios)
    return [r / total for r in ratios]


def validate_ratios(ratios: list[float], tolerance: float = 0.001) -> bool:
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


# Alias for compatibility
find_node = find_node_by_id


class LeafCollector(NodeVisitor):
    """Visitor that collects all leaf nodes."""

    def __init__(self):
        """Initialize collector."""
        self.leaves: list[LeafNode] = []

    def visit_leaf(self, node: LeafNode) -> None:
        """Add leaf to collection."""
        self.leaves.append(node)

    def visit_split(self, node: SplitNode) -> None:
        """Recursively collect from children."""
        for child in node.children:
            child.accept(self)


def get_all_leaves(root: PaneNode) -> list[LeafNode]:
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
        self.errors: list[str] = []

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


def validate_tree_structure(root: PaneNode) -> tuple[bool, list[str]]:
    """Validate tree structure invariants.

    Args:
        root: Root node to validate

    Returns:
        Tuple of (is_valid, error_messages)
    """
    validator = StructureValidator()
    root.accept(validator)
    return validator.is_valid, validator.errors


def find_split_by_id(root: Optional[PaneNode], node_id: NodeId) -> Optional[SplitNode]:
    """Find split node by ID.

    Args:
        root: Root of tree to search
        node_id: Node ID to find

    Returns:
        SplitNode if found, None otherwise
    """
    if not root:
        return None

    if isinstance(root, SplitNode):
        if root.node_id == node_id:
            return root
        for child in root.children:
            result = find_split_by_id(child, node_id)
            if result:
                return result
    return None


# Aliases for compatibility with documentation
collect_leaves = get_all_leaves
calculate_depth = get_tree_depth
validate_structure = validate_tree_structure
