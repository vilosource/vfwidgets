"""Tree reconciliation for efficient updates.

Calculates minimal differences between tree states to
enable efficient UI updates without full rebuilds.
"""

from dataclasses import dataclass, field
from typing import Any, Optional

from ..core.nodes import LeafNode, PaneNode, SplitNode
from ..core.types import PaneId
from ..core.visitor import NodeVisitor


@dataclass
class DiffResult:
    """Result of tree diff operation."""

    removed: set[PaneId] = field(default_factory=set)
    added: set[PaneId] = field(default_factory=set)
    moved: set[PaneId] = field(default_factory=set)
    modified: set[PaneId] = field(default_factory=set)

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
        self.nodes: dict[PaneId, dict[str, Any]] = {}

    def visit_leaf(self, node: LeafNode) -> None:
        """Collect leaf node information."""
        self.nodes[node.pane_id] = {
            "type": "leaf",
            "widget_id": node.widget_id,
            "parent": node.parent.node_id if node.parent else None,
        }

    def visit_split(self, node: SplitNode) -> None:
        """Collect split node information and visit children."""
        # Split nodes don't have pane_id, only process children
        for child in node.children:
            child.accept(self)


class TreeReconciler:
    """Calculate minimal updates between tree states."""

    def diff(self, old_tree: Optional[PaneNode], new_tree: Optional[PaneNode]) -> DiffResult:
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
            if old_info["parent"] != new_info["parent"]:
                result.moved.add(pane_id)

            # Check if widget changed (modified)
            if old_info["widget_id"] != new_info["widget_id"]:
                result.modified.add(pane_id)

        return result

    def apply_diff(self, diff: DiffResult, operations: "ReconcilerOperations") -> None:
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
