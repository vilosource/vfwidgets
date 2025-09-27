"""Geometry calculation for pane layout.

Calculates exact pixel positions for all panes from tree structure.
"""

from typing import Dict, List

from .nodes import LeafNode, PaneNode, SplitNode
from .types import Bounds, Orientation, PaneId


class GeometryCalculator:
    """Calculate pane positions from tree structure."""

    def __init__(self, divider_width: int = 4):
        """Initialize calculator with divider width.

        Args:
            divider_width: Width of dividers between panes in pixels
        """
        self.divider_width = divider_width

    def calculate_layout(self, root: PaneNode, bounds: Bounds,
                        divider_width: int = 6) -> Dict[PaneId, Bounds]:
        """Calculate pixel-perfect layout with constraint enforcement.

        Args:
            root: Root node of tree
            bounds: Available bounds for layout
            divider_width: Width of dividers in pixels

        Returns:
            Mapping of pane IDs to their bounds
        """
        self.divider_width = divider_width
        result = {}

        # Calculate initial layout
        self._calculate_node_bounds(root, bounds, result)

        # Apply constraints
        self._apply_constraints(root, result)

        return result

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

    def _calculate_node_bounds(self, node: PaneNode, bounds: Bounds,
                             result: Dict[PaneId, Bounds]):
        """Calculate bounds for nodes (alias for _calculate_recursive)."""
        self._calculate_recursive(node, bounds, result)

    def _apply_constraints(self, node: PaneNode,
                          layout: Dict[PaneId, Bounds]):
        """Apply size constraints to layout.

        Args:
            node: Node to apply constraints to
            layout: Current layout to modify
        """
        if isinstance(node, LeafNode):
            if node.pane_id in layout:
                bounds = layout[node.pane_id]

                # Apply constraints
                new_width, new_height = node.constraints.clamp_size(
                    bounds.width, bounds.height
                )

                if new_width != bounds.width or new_height != bounds.height:
                    # Update bounds with constrained size
                    layout[node.pane_id] = Bounds(
                        bounds.x, bounds.y, new_width, new_height
                    )

        elif isinstance(node, SplitNode):
            # Recursively apply to children
            for child in node.children:
                self._apply_constraints(child, layout)

            # Check if children meet minimum sizes
            self._propagate_constraints(node, layout)

    def _propagate_constraints(self, split_node: SplitNode,
                              layout: Dict[PaneId, Bounds]):
        """Propagate constraints through split node.

        Args:
            split_node: Split node to propagate through
            layout: Current layout
        """
        # Calculate minimum sizes for each child
        min_sizes = []
        for child in split_node.children:
            min_size = self._calculate_minimum_size(child)
            min_sizes.append(min_size)

        # Check if we can fit all minimums
        total_min = sum(min_sizes)
        available = (split_node.bounds.width if split_node.orientation == Orientation.HORIZONTAL
                    else split_node.bounds.height)

        if total_min > available:
            # Need to adjust ratios to meet constraints
            # This is complex - for now, just warn
            if hasattr(self, 'signals'):
                self.signals.validation_failed.emit(
                    ["Insufficient space for minimum sizes"]
                )

    def _calculate_minimum_size(self, node: PaneNode) -> int:
        """Calculate minimum size for node.

        Args:
            node: Node to calculate for

        Returns:
            Minimum size in pixels
        """
        if isinstance(node, LeafNode):
            return node.constraints.min_width  # or min_height based on orientation

        elif isinstance(node, SplitNode):
            # Sum of child minimums plus dividers
            child_mins = [self._calculate_minimum_size(child)
                         for child in node.children]
            divider_space = self.divider_width * (len(node.children) - 1)
            return sum(child_mins) + divider_space

        return 50  # Default minimum

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
