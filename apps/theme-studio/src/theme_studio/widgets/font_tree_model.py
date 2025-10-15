"""Font Tree Model - QAbstractItemModel for hierarchical font token display.

Mirrors TokenTreeModel architecture for perfect consistency.
"""

from typing import Any

from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt
from PySide6.QtGui import QIcon

from ..metadata.font_token_metadata import FontTokenCategory, FontTokenMetadataRegistry
from ..models import ThemeDocument


class FontTreeNode:
    """Node in the font tree.

    Exactly mirrors TokenTreeNode structure.
    """

    def __init__(
        self,
        name: str,
        path: str = None,
        value: Any = None,
        is_category: bool = False,
        category: FontTokenCategory = None,
    ):
        """Initialize tree node.

        Args:
            name: Display name (category name or token label)
            path: Token path (for token nodes only, e.g., "terminal.fontSize")
            value: Token value (for token nodes only)
            is_category: Whether this is a category node
            category: FontTokenCategory enum value
        """
        self.name = name
        self.path = path
        self.value = value
        self.is_category = is_category
        self.category = category
        self.children: list[FontTreeNode] = []
        self.parent: FontTreeNode | None = None

    def add_child(self, child: "FontTreeNode"):
        """Add child node."""
        child.parent = self
        self.children.append(child)

    def child_at(self, row: int) -> "FontTreeNode | None":
        """Get child at row index."""
        if 0 <= row < len(self.children):
            return self.children[row]
        return None

    def row(self) -> int:
        """Get row index of this node in parent's children."""
        if self.parent:
            return self.parent.children.index(self)
        return 0


class FontTreeModel(QAbstractItemModel):
    """Hierarchical model for font token browser.

    Exactly mirrors TokenTreeModel architecture.

    Structure:
        Root
        ├── BASE FONTS (7)
        │   ├── Mono
        │   ├── Ui
        │   └── ...
        ├── TERMINAL (5)
        │   ├── Font Family
        │   └── ...
        └── ...
    """

    def __init__(self, document: ThemeDocument, parent=None):
        """Initialize font tree model.

        Args:
            document: ThemeDocument to display
            parent: Parent QObject
        """
        super().__init__(parent)
        self._document = document
        self._root = self._build_tree()

        # Connect to document changes
        document.font_changed.connect(self._on_font_changed)

    def _build_tree(self) -> FontTreeNode:
        """Build hierarchical tree from FontTokenMetadataRegistry.

        Returns:
            Root node with full tree structure
        """
        root = FontTreeNode("Font Tokens", is_category=False)

        # Iterate through all categories
        for category in FontTokenCategory:
            # Create category node
            token_list = FontTokenMetadataRegistry.get_tokens_by_category(category)
            category_display_name = category.value.replace("_", " ").upper()
            category_node = FontTreeNode(
                name=category_display_name,  # Don't add count here, data() will add it
                is_category=True,
                category=category,
            )
            category_node.parent = root
            root.children.append(category_node)

            # Get tokens for this category
            for token_info in token_list:
                # Get token value from document
                token_value = self._document.get_font(token_info.path)

                # If no user-defined value, use default for preview
                if token_value is None and token_info.default_value is not None:
                    token_value = token_info.default_value

                # Get display name from metadata
                display_name = FontTokenMetadataRegistry.get_display_name(token_info.path)

                # Create token node
                token_node = FontTreeNode(
                    name=display_name,
                    path=token_info.path,
                    value=token_value,
                    is_category=False,
                    category=category,
                )
                category_node.add_child(token_node)

        return root

    def _on_font_changed(self, token_path: str, new_value: Any):
        """Handle font token value change from document.

        Args:
            token_path: Changed token path
            new_value: New token value
        """

        # Find the token node and update its value
        def find_and_update_node(node: FontTreeNode, path: list) -> tuple[bool, list]:
            """Recursively find and update token node."""
            if not node.is_category and node.path == token_path:
                node.value = new_value
                return True, path

            for row, child in enumerate(node.children):
                found, result_path = find_and_update_node(child, path + [(node, row)])
                if found:
                    return True, result_path

            return False, []

        # Update the node value
        found, path_to_node = find_and_update_node(self._root, [])
        if found and path_to_node:
            # Build the QModelIndex for the changed node
            parent_index = QModelIndex()
            for _parent_node, row in path_to_node:
                parent_index = self.index(row, 0, parent_index)

            # Emit dataChanged for ONLY the changed row
            # This is efficient and won't corrupt Qt state
            self.dataChanged.emit(parent_index, parent_index)

    # QAbstractItemModel interface implementation

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        """Create index for item at row/column under parent."""
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        # Get parent node
        if not parent.isValid():
            parent_node = self._root
        else:
            parent_node = parent.internalPointer()

        # Get child node
        child_node = parent_node.child_at(row)
        if child_node:
            return self.createIndex(row, column, child_node)
        return QModelIndex()

    def parent(self, index: QModelIndex) -> QModelIndex:
        """Get parent index of item."""
        if not index.isValid():
            return QModelIndex()

        child_node = index.internalPointer()
        parent_node = child_node.parent

        if parent_node == self._root or parent_node is None:
            return QModelIndex()

        return self.createIndex(parent_node.row(), 0, parent_node)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Get row count under parent."""
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parent_node = self._root
        else:
            parent_node = parent.internalPointer()

        return len(parent_node.children)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Get column count.

        Returns 1 to match TokenTreeModel (single column display).
        """
        return 1  # CRITICAL: Must be 1, not 2!

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        """Get data for index and role."""
        if not index.isValid():
            return None

        node = index.internalPointer()

        if role == Qt.DisplayRole:
            # Display text
            if node.is_category:
                # Category: "BASE FONTS (7)"
                count = len(node.children)
                return f"{node.name} ({count})"
            else:
                # Token: just the display name (no value in tree!)
                return node.name

        elif role == Qt.DecorationRole:
            # Icons for visual hierarchy (mirrors color swatches)
            if node.is_category:
                return QIcon.fromTheme("folder")
            else:
                # Different icons based on token type
                if node.path and "Family" in node.path:
                    return QIcon.fromTheme("font")
                elif node.path and "Size" in node.path:
                    return QIcon.fromTheme("format-font-size-more")
                elif node.path and "Weight" in node.path:
                    return QIcon.fromTheme("format-text-bold")
                elif node.path and (
                    "lineHeight" in node.path or "letterSpacing" in node.path
                ):
                    return QIcon.fromTheme("format-line-spacing")
                else:
                    return QIcon.fromTheme("format-text")

        elif role == Qt.ToolTipRole:
            # Show full metadata in tooltip (mirrors color tooltips)
            if node.is_category:
                return f"{node.name} category with {len(node.children)} tokens"
            else:
                token_meta = FontTokenMetadataRegistry.get_token(node.path)
                if token_meta:
                    tooltip = f"<b>{token_meta.path}</b><br>"
                    tooltip += f"{token_meta.description}<br><br>"
                    tooltip += f"<b>Type:</b> {token_meta.value_type.__name__}"
                    if token_meta.unit:
                        tooltip += f" ({token_meta.unit})"
                    tooltip += "<br>"

                    if token_meta.default_value is not None:
                        if isinstance(token_meta.default_value, list):
                            families = ", ".join(token_meta.default_value[:3])
                            if len(token_meta.default_value) > 3:
                                families += "..."
                            tooltip += f"<b>Default:</b> {families}<br>"
                        else:
                            tooltip += f"<b>Default:</b> {token_meta.default_value}<br>"

                    if node.value is not None:
                        if isinstance(node.value, list):
                            current = ", ".join(str(v) for v in node.value[:3])
                            if len(node.value) > 3:
                                current += "..."
                            tooltip += f"<b>Current:</b> {current}"
                        else:
                            tooltip += f"<b>Current:</b> {node.value}"
                    else:
                        tooltip += "<i>Using fallback value</i>"

                    return tooltip
                else:
                    value_display = node.value if node.value else "(using fallback)"
                    return f"{node.name}\nValue: {value_display}"

        elif role == Qt.UserRole:
            # Custom data: return the node itself
            return node

        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """Get item flags."""
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    # Helper methods (CRITICAL - mirrors TokenTreeModel)

    def get_token_path(self, index: QModelIndex) -> str | None:
        """Get token path from index.

        Args:
            index: Model index

        Returns:
            Token path (e.g., "terminal.fontSize"), or None if not a token node
        """
        if not index.isValid():
            return None

        node = index.internalPointer()
        if not node.is_category:
            return node.path
        return None

    def get_token_value(self, index: QModelIndex) -> Any:
        """Get token value from index.

        Args:
            index: Model index

        Returns:
            Token value, or None if not a token node or value not set
        """
        if not index.isValid():
            return None

        node = index.internalPointer()
        if not node.is_category:
            return node.value
        return None


__all__ = ["FontTreeModel", "FontTreeNode"]
