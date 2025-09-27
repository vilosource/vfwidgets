"""Visitor pattern for tree traversal.

Pure Python implementation for tree operations.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

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


# Alias for compatibility with documentation
PaneVisitor = NodeVisitor
