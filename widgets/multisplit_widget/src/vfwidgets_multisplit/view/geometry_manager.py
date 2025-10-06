"""
GeometryManager - Production Implementation

Pure calculation layer that converts pane tree to widget geometries.
Part of the Fixed Container Architecture (Layer 2).
"""

from typing import Optional

from PySide6.QtCore import QRect

from ..core.nodes import LeafNode, PaneNode, SplitNode
from ..core.types import Orientation


class GeometryManager:
    """
    Pure calculation layer for converting tree structure to widget rectangles.

    This is the second layer of the Fixed Container Architecture.
    It performs ONLY mathematical calculations - no Qt widget operations.

    Architecture:
        - Layer 1: WidgetPool - Fixed container
        - Layer 2: GeometryManager (this class) - Pure calculation
        - Layer 3: VisualRenderer - Geometry application
    """

    def __init__(self, handle_width: int = 6):
        """Initialize geometry manager with configurable handle width.

        Args:
            handle_width: Width of splitter handles in pixels (default: 6)
        """
        self.HANDLE_WIDTH = handle_width  # Width of splitter handles (spacing between panes)

    def calculate_layout(self, tree: Optional[PaneNode], viewport: QRect) -> dict[str, QRect]:
        """
        Calculate widget geometries from pane tree.

        This is the main entry point. It recursively traverses the tree
        and calculates the geometry for each leaf pane.

        Args:
            tree: Root of the pane tree
            viewport: Available rectangle for layout

        Returns:
            Dictionary mapping pane IDs to their calculated geometries
        """
        if tree is None:
            return {}

        geometries: dict[str, QRect] = {}
        self._calculate_recursive(tree, viewport, geometries)
        return geometries

    def _calculate_recursive(
        self, node: PaneNode, rect: QRect, geometries: dict[str, QRect]
    ) -> None:
        """
        Recursively calculate geometries for a node and its children.

        Args:
            node: Current node in the tree
            rect: Rectangle available for this node
            geometries: Output dictionary to populate
        """
        if isinstance(node, LeafNode):
            # Base case: leaf node gets the entire rectangle
            geometries[node.pane_id] = rect

        elif isinstance(node, SplitNode):
            # Recursive case: split the rectangle and recurse to children
            if node.orientation == Orientation.HORIZONTAL:
                child_rects = self._split_horizontal(rect, node.ratios)
            else:  # VERTICAL
                child_rects = self._split_vertical(rect, node.ratios)

            # Recurse to each child with its calculated rectangle
            for child, child_rect in zip(node.children, child_rects):
                self._calculate_recursive(child, child_rect, geometries)

    def _split_horizontal(self, rect: QRect, ratios: list[float]) -> list[QRect]:
        """
        Split a rectangle horizontally (left-to-right) according to ratios.

        Args:
            rect: The rectangle to split
            ratios: List of width ratios (must sum to ~1.0)

        Returns:
            List of rectangles, one for each ratio

        Example:
            rect = QRect(0, 0, 1200, 800)
            ratios = [0.5, 0.5]
            Result:
                [QRect(0, 0, 597, 800),   # 600 - 3px handle spacing
                 QRect(603, 0, 597, 800)]  # 600 - 3px handle spacing
                Gap: 603 - 597 = 6px (handle width)
        """
        if not ratios:
            return []

        if abs(sum(ratios) - 1.0) > 0.001:
            # Normalize ratios if they don't sum to exactly 1.0
            total = sum(ratios)
            ratios = [r / total for r in ratios]

        sections = []
        current_x = rect.x()

        for i, ratio in enumerate(ratios):
            # Calculate width for this section
            if i == len(ratios) - 1:
                # Last section: use all remaining width (corrected formula)
                width = (rect.x() + rect.width()) - current_x
            else:
                # Other sections: proportional width
                width = int(rect.width() * ratio)

            # Subtract handle width from all but the last section
            # This creates the visual gap for the splitter handle
            section_width = width - (self.HANDLE_WIDTH if i < len(ratios) - 1 else 0)

            section_rect = QRect(current_x, rect.y(), section_width, rect.height())
            sections.append(section_rect)

            # Move to next section (width includes handle spacing)
            current_x += width

        return sections

    def _split_vertical(self, rect: QRect, ratios: list[float]) -> list[QRect]:
        """
        Split a rectangle vertically (top-to-bottom) according to ratios.

        Args:
            rect: The rectangle to split
            ratios: List of height ratios (must sum to ~1.0)

        Returns:
            List of rectangles, one for each ratio

        Example:
            rect = QRect(0, 0, 800, 600)
            ratios = [0.5, 0.5]
            Result:
                [QRect(0, 0, 800, 297),   # 300 - 3px handle spacing
                 QRect(0, 303, 800, 297)]  # 300 - 3px handle spacing
                Gap: 303 - 297 = 6px (handle height)
        """
        if not ratios:
            return []

        if abs(sum(ratios) - 1.0) > 0.001:
            # Normalize ratios if they don't sum to exactly 1.0
            total = sum(ratios)
            ratios = [r / total for r in ratios]

        sections = []
        current_y = rect.y()

        for i, ratio in enumerate(ratios):
            # Calculate height for this section
            if i == len(ratios) - 1:
                # Last section: use all remaining height (corrected formula)
                height = (rect.y() + rect.height()) - current_y
            else:
                # Other sections: proportional height
                height = int(rect.height() * ratio)

            # Subtract handle height from all but the last section
            # This creates the visual gap for the splitter handle
            section_height = height - (self.HANDLE_WIDTH if i < len(ratios) - 1 else 0)

            section_rect = QRect(rect.x(), current_y, rect.width(), section_height)
            sections.append(section_rect)

            # Move to next section (height includes handle spacing)
            current_y += height

        return sections

    def calculate_dividers(
        self, tree: Optional[PaneNode], viewport: QRect
    ) -> dict[str, list[QRect]]:
        """
        Calculate divider geometries for each SplitNode in the tree.

        Each SplitNode with N children has N-1 dividers positioned in the gaps
        between adjacent children.

        Args:
            tree: Root of the pane tree
            viewport: Available rectangle for layout

        Returns:
            Dictionary mapping node_id -> list of divider rectangles
            Each SplitNode gets a list of divider rects (one per gap between children)

        Example:
            For a SplitNode with 2 children (HORIZONTAL orientation):
            {
                "node_123": [QRect(597, 0, 6, 800)]  # One divider between 2 children
            }
        """
        if tree is None:
            return {}

        dividers: dict[str, list[QRect]] = {}
        self._calculate_dividers_recursive(tree, viewport, dividers)
        return dividers

    def _calculate_dividers_recursive(
        self, node: PaneNode, rect: QRect, dividers: dict[str, list[QRect]]
    ) -> None:
        """
        Recursively calculate divider geometries for a node and its children.

        Args:
            node: Current node in the tree
            rect: Rectangle available for this node
            dividers: Output dictionary to populate
        """
        if isinstance(node, LeafNode):
            # Leaf nodes have no dividers
            return

        elif isinstance(node, SplitNode):
            # Calculate child rectangles (same logic as layout calculation)
            if node.orientation == Orientation.HORIZONTAL:
                child_rects = self._split_horizontal(rect, node.ratios)
            else:  # VERTICAL
                child_rects = self._split_vertical(rect, node.ratios)

            # Calculate divider rects for gaps between children
            node_dividers = []
            for i in range(len(child_rects) - 1):
                # Divider sits between child[i] and child[i+1]
                left_child_rect = child_rects[i]

                if node.orientation == Orientation.HORIZONTAL:
                    # Horizontal split = vertical divider line
                    # Gap is between left_child's right edge and right_child's left edge
                    divider_rect = QRect(
                        left_child_rect.x() + left_child_rect.width(),  # Start after left child
                        rect.y(),
                        self.HANDLE_WIDTH,
                        rect.height(),
                    )
                else:  # VERTICAL
                    # Vertical split = horizontal divider line
                    # Gap is between top_child's bottom edge and bottom_child's top edge
                    divider_rect = QRect(
                        rect.x(),
                        left_child_rect.y() + left_child_rect.height(),  # Start after top child
                        rect.width(),
                        self.HANDLE_WIDTH,
                    )

                node_dividers.append(divider_rect)

            # Store dividers for this SplitNode
            if node_dividers:
                dividers[str(node.node_id)] = node_dividers

            # Recurse to children with their calculated rectangles
            for child, child_rect in zip(node.children, child_rects):
                self._calculate_dividers_recursive(child, child_rect, dividers)
