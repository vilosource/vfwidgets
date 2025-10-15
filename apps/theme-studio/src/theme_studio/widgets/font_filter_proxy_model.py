"""Font Filter Proxy Model - Custom filtering for font token tree.

Mirrors TokenFilterProxyModel for architectural consistency.
"""

from PySide6.QtCore import QModelIndex, QSortFilterProxyModel


class FontFilterProxyModel(QSortFilterProxyModel):
    """Custom proxy model that supports filtering by token paths.

    Provides:
    - Search filtering (by token name)
    - Widget filtering (show only tokens used by current widget)
    - Recursive filtering (hides empty categories)

    Exactly mirrors TokenFilterProxyModel architecture.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._allowed_token_paths = None  # None means show all tokens
        self._source_model = None

    def setSourceModel(self, model):
        """Override to store source model reference.

        Args:
            model: Source model (FontTreeModel)
        """
        self._source_model = model
        super().setSourceModel(model)

    def set_allowed_token_paths(self, token_paths: set[str] | None):
        """Set which token paths to show (None = show all).

        This enables the "Show only current widget fonts" feature.

        Args:
            token_paths: Set of token paths to show, or None to show all
        """
        self._allowed_token_paths = token_paths
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        """Override to filter by token paths and search text.

        Args:
            source_row: Row in source model
            source_parent: Parent index in source model

        Returns:
            True if row should be shown
        """
        if not self._source_model:
            return True

        # Get the index for this row
        index = self._source_model.index(source_row, 0, source_parent)
        if not index.isValid():
            return False

        # Get token path for this index
        token_path = self._source_model.get_token_path(index)

        # If this is a category node (no token path), check if any children match
        if not token_path:
            # Category nodes are shown if they have any matching children
            # Qt's recursive filtering handles this automatically
            return super().filterAcceptsRow(source_row, source_parent)

        # This is a token node - check if it's in the allowed paths
        if self._allowed_token_paths is not None:
            if token_path not in self._allowed_token_paths:
                return False

        # Also apply text filter (search box)
        return super().filterAcceptsRow(source_row, source_parent)


__all__ = ["FontFilterProxyModel"]
