"""Focus management for MultiSplit widget.

Handles focus chain calculation and navigation.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from .model import PaneModel
from .nodes import LeafNode, SplitNode
from .types import Direction, PaneId
from .visitor import NodeVisitor


@dataclass
class FocusManager:
    """Manages focus chain and navigation."""

    model: PaneModel
    _focus_order_cache: Optional[List[PaneId]] = field(default=None, init=False)
    _cache_valid: bool = field(default=False, init=False)

    def __post_init__(self):
        """Connect to model signals."""
        # Store reference to avoid garbage collection of bound method
        self._invalidate_handler = self._invalidate_cache
        self.model.signals.structure_changed.connect(self._invalidate_handler)

    def _invalidate_cache(self):
        """Invalidate cached focus order."""
        self._cache_valid = False
        self._focus_order_cache = None

    def get_focus_order(self) -> List[PaneId]:
        """Get panes in focus traversal order.

        Returns:
            List of pane IDs in tab order
        """
        if not self._cache_valid or self._focus_order_cache is None:
            self._rebuild_focus_order()
        return self._focus_order_cache.copy() if self._focus_order_cache else []

    def _rebuild_focus_order(self):
        """Rebuild focus order from tree structure."""
        if not self.model.root:
            self._focus_order_cache = []
            self._cache_valid = True
            return

        # Collect panes in tree order
        visitor = FocusOrderVisitor()
        self.model.root.accept(visitor)
        self._focus_order_cache = visitor.pane_order
        self._cache_valid = True

    def get_next_pane(self, current: Optional[PaneId] = None) -> Optional[PaneId]:
        """Get next pane in focus order.

        Args:
            current: Current focused pane, or None to get first

        Returns:
            Next pane ID, or None if no panes
        """
        order = self.get_focus_order()
        if not order:
            return None

        if current is None or current not in order:
            return order[0]

        current_index = order.index(current)
        next_index = (current_index + 1) % len(order)
        return order[next_index]

    def get_previous_pane(self, current: Optional[PaneId] = None) -> Optional[PaneId]:
        """Get previous pane in focus order.

        Args:
            current: Current focused pane, or None to get last

        Returns:
            Previous pane ID, or None if no panes
        """
        order = self.get_focus_order()
        if not order:
            return None

        if current is None or current not in order:
            return order[-1] if order else None

        current_index = order.index(current)
        prev_index = (current_index - 1) % len(order)
        return order[prev_index]

    def navigate(self, direction: Direction) -> Optional[PaneId]:
        """Navigate focus in a direction.

        Args:
            direction: Direction to move focus

        Returns:
            Pane ID to focus, or None if can't navigate
        """
        current = self.model.focused_pane_id
        if not current:
            return self.get_next_pane()

        # For now, use simple tab order for left/right
        # TODO: Implement spatial navigation
        if direction in (Direction.LEFT, Direction.UP):
            return self.get_previous_pane(current)
        else:
            return self.get_next_pane(current)


class FocusOrderVisitor(NodeVisitor):
    """Visitor that collects panes in focus order."""

    def __init__(self):
        """Initialize visitor."""
        self.pane_order: List[PaneId] = []

    def visit_leaf(self, node: LeafNode):
        """Add leaf to focus order."""
        self.pane_order.append(node.pane_id)

    def visit_split(self, node: SplitNode):
        """Traverse children in order."""
        # Left-to-right, top-to-bottom traversal
        for child in node.children:
            child.accept(self)
