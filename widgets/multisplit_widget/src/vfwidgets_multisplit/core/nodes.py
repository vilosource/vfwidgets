"""Tree node structures for MultiSplit widget.

Pure Python implementation with no Qt dependencies.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, List, Optional

from .types import Bounds, NodeId, Orientation, PaneId, SizeConstraints, WidgetId

if TYPE_CHECKING:
    from .visitor import NodeVisitor


class PaneNode(ABC):
    """Abstract base class for tree nodes."""

    def __init__(self):
        """Initialize base node."""
        self.parent: Optional[SplitNode] = None
        self._bounds: Optional[Bounds] = None

    @abstractmethod
    def accept(self, visitor: NodeVisitor) -> Any:
        """Accept a visitor for tree traversal.

        Args:
            visitor: Visitor to accept

        Returns:
            Result from visitor
        """
        pass

    @property
    def bounds(self) -> Optional[Bounds]:
        """Get node bounds (set by geometry calculator)."""
        return self._bounds

    @bounds.setter
    def bounds(self, value: Bounds):
        """Set node bounds."""
        self._bounds = value

    def get_root(self) -> PaneNode:
        """Get tree root."""
        node = self
        while node.parent:
            node = node.parent
        return node

    def get_depth(self) -> int:
        """Get node depth from root."""
        depth = 0
        node = self
        while node.parent:
            depth += 1
            node = node.parent
        return depth

    @abstractmethod
    def clone(self) -> PaneNode:
        """Create a deep copy of this node.

        Returns:
            Cloned node with new IDs
        """
        pass


@dataclass
class LeafNode(PaneNode):
    """Terminal node containing a widget."""

    pane_id: PaneId
    widget_id: WidgetId
    constraints: SizeConstraints = field(default_factory=SizeConstraints)

    def __post_init__(self):
        """Initialize parent class."""
        super().__init__()

    def accept(self, visitor: NodeVisitor) -> Any:
        """Accept visitor for leaf node."""
        return visitor.visit_leaf(self)

    def clone(self) -> LeafNode:
        """Clone leaf node."""
        return LeafNode(
            pane_id=self.pane_id,
            widget_id=self.widget_id,
            constraints=self.constraints
        )


@dataclass
class SplitNode(PaneNode):
    """Container node with children."""

    node_id: NodeId
    orientation: Orientation
    children: List[PaneNode] = field(default_factory=list)
    ratios: List[float] = field(default_factory=list)

    def __post_init__(self):
        """Initialize parent class and set parent references."""
        super().__init__()
        for child in self.children:
            child.parent = self

    def accept(self, visitor: NodeVisitor) -> Any:
        """Accept visitor for split node."""
        return visitor.visit_split(self)

    def add_child(self, child: PaneNode, ratio: float = None):
        """Add child node."""
        child.parent = self
        self.children.append(child)

        if ratio is not None:
            self.ratios.append(ratio)
        else:
            # Equal distribution
            count = len(self.children)
            self.ratios = [1.0 / count] * count

    def remove_child(self, child: PaneNode):
        """Remove child node."""
        if child in self.children:
            idx = self.children.index(child)
            self.children.remove(child)
            child.parent = None

            # Adjust ratios
            if self.ratios and idx < len(self.ratios):
                self.ratios.pop(idx)
                # Renormalize
                if self.ratios:
                    total = sum(self.ratios)
                    self.ratios = [r / total for r in self.ratios]

    def replace_child(self, old_child: PaneNode, new_child: PaneNode):
        """Replace child node."""
        if old_child in self.children:
            idx = self.children.index(old_child)
            old_child.parent = None
            new_child.parent = self
            self.children[idx] = new_child

    def clone(self) -> SplitNode:
        """Clone split node and all children."""
        cloned_children = [child.clone() for child in self.children]
        return SplitNode(
            node_id=self.node_id,
            orientation=self.orientation,
            children=cloned_children,
            ratios=self.ratios.copy()
        )
