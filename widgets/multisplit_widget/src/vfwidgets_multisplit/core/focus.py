"""Focus management for MultiSplit widget.

Handles focus chain calculation and navigation.
"""

from dataclasses import dataclass, field
from typing import Optional

from PySide6.QtCore import QRect

from .model import PaneModel
from .nodes import LeafNode, SplitNode
from .types import Direction, PaneId
from .visitor import NodeVisitor


@dataclass
class FocusManager:
    """Manages focus chain and navigation."""

    model: PaneModel
    _focus_order_cache: Optional[list[PaneId]] = field(default=None, init=False)
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

    def get_focus_order(self) -> list[PaneId]:
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

    def navigate(
        self, direction: Direction, geometries: Optional[dict[PaneId, QRect]] = None
    ) -> Optional[PaneId]:
        """Navigate focus in a direction.

        Args:
            direction: Direction to move focus
            geometries: Optional pane geometries for spatial navigation.
                       If None, falls back to tab order navigation.

        Returns:
            Pane ID to focus, or None if can't navigate
        """
        current = self.model.focused_pane_id
        if not current:
            return self.get_next_pane()

        # Use spatial navigation if geometries provided
        if geometries and current in geometries:
            return self._find_spatial_neighbor(current, direction, geometries)

        # Fallback to tab order (for backward compatibility)
        if direction in (Direction.LEFT, Direction.UP):
            return self.get_previous_pane(current)
        else:
            return self.get_next_pane(current)

    def _find_spatial_neighbor(
        self, current_id: PaneId, direction: Direction, geometries: dict[PaneId, QRect]
    ) -> Optional[PaneId]:
        """Find nearest pane in given direction using geometry.

        Algorithm:
        1. Filter candidates in target direction
        2. Keep only those with overlap on perpendicular axis
        3. Choose closest by edge distance
        4. Tie-break by center-to-center distance
        5. Final tie-break by tab order

        Args:
            current_id: Current pane ID
            direction: Direction to navigate
            geometries: Pane geometries

        Returns:
            Pane ID to navigate to, or None if at edge
        """
        current_rect = geometries[current_id]
        candidates: list[tuple[PaneId, QRect, float]] = []

        for pane_id, rect in geometries.items():
            if pane_id == current_id:
                continue

            # Check if pane is in target direction
            if not self._is_in_direction(current_rect, rect, direction):
                continue

            # Check for overlap on perpendicular axis
            if not self._has_perpendicular_overlap(current_rect, rect, direction):
                continue

            # Calculate edge distance (primary metric)
            edge_dist = self._calculate_edge_distance(current_rect, rect, direction)
            candidates.append((pane_id, rect, edge_dist))

        if not candidates:
            return None  # At edge, no valid target

        # Sort by edge distance (closest first)
        candidates.sort(key=lambda x: x[2])

        # If multiple candidates at same edge distance, use center distance
        min_edge_dist = candidates[0][2]
        tied = [c for c in candidates if abs(c[2] - min_edge_dist) < 1.0]  # 1px tolerance

        if len(tied) > 1:
            # Tie-break by center-to-center distance
            current_center = self._get_center(current_rect)
            tied.sort(
                key=lambda x: self._distance_between_centers(current_center, self._get_center(x[1]))
            )

        return tied[0][0]  # Return pane_id of winner

    def _is_in_direction(self, current: QRect, target: QRect, direction: Direction) -> bool:
        """Check if target is in the given direction from current.

        Note: QRect.right() returns x + width - 1, not x + width.
        We need actual edges, so we use x() + width() and y() + height().
        """
        current_right = current.x() + current.width()
        current_bottom = current.y() + current.height()
        target_right = target.x() + target.width()
        target_bottom = target.y() + target.height()

        if direction == Direction.LEFT:
            return target_right <= current.x()
        elif direction == Direction.RIGHT:
            return target.x() >= current_right
        elif direction == Direction.UP:
            return target_bottom <= current.y()
        elif direction == Direction.DOWN:
            return target.y() >= current_bottom
        return False

    def _has_perpendicular_overlap(
        self, current: QRect, target: QRect, direction: Direction
    ) -> bool:
        """Check if rects overlap on axis perpendicular to direction.

        Note: QRect.right() returns x + width - 1, not x + width.
        We need actual edges, so we use x() + width() and y() + height().
        """
        current_right = current.x() + current.width()
        current_bottom = current.y() + current.height()
        target_right = target.x() + target.width()
        target_bottom = target.y() + target.height()

        if direction in (Direction.LEFT, Direction.RIGHT):
            # Check vertical overlap
            return not (target_bottom <= current.y() or target.y() >= current_bottom)
        else:  # UP or DOWN
            # Check horizontal overlap
            return not (target_right <= current.x() or target.x() >= current_right)

    def _calculate_edge_distance(
        self, current: QRect, target: QRect, direction: Direction
    ) -> float:
        """Calculate edge-to-edge distance in direction.

        Note: QRect.right() returns x + width - 1, not x + width.
        We need actual edges, so we use x() + width() and y() + height().
        """
        current_right = current.x() + current.width()
        current_bottom = current.y() + current.height()
        target_right = target.x() + target.width()
        target_bottom = target.y() + target.height()

        if direction == Direction.LEFT:
            return current.x() - target_right
        elif direction == Direction.RIGHT:
            return target.x() - current_right
        elif direction == Direction.UP:
            return current.y() - target_bottom
        elif direction == Direction.DOWN:
            return target.y() - current_bottom
        return float("inf")

    def _get_center(self, rect: QRect) -> tuple[float, float]:
        """Get center point of rectangle."""
        return (rect.x() + rect.width() / 2, rect.y() + rect.height() / 2)

    def _distance_between_centers(
        self, center1: tuple[float, float], center2: tuple[float, float]
    ) -> float:
        """Calculate Euclidean distance between centers."""
        dx = center1[0] - center2[0]
        dy = center1[1] - center2[1]
        return (dx * dx + dy * dy) ** 0.5


class FocusOrderVisitor(NodeVisitor):
    """Visitor that collects panes in focus order."""

    def __init__(self):
        """Initialize visitor."""
        self.pane_order: list[PaneId] = []

    def visit_leaf(self, node: LeafNode):
        """Add leaf to focus order."""
        self.pane_order.append(node.pane_id)

    def visit_split(self, node: SplitNode):
        """Traverse children in order."""
        # Left-to-right, top-to-bottom traversal
        for child in node.children:
            child.accept(self)
