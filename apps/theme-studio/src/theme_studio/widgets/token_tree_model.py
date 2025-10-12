"""Token Tree Model - QAbstractItemModel for hierarchical token display."""

from typing import Any

from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt
from PySide6.QtGui import QColor, QPainter, QPen, QPixmap
from vfwidgets_theme.core.tokens import ColorTokenRegistry, TokenCategory

from ..models import ThemeDocument


class TokenTreeNode:
    """Node in the token tree."""

    def __init__(self, name: str, value: str = None, is_category: bool = False, category: TokenCategory = None):
        """Initialize tree node.

        Args:
            name: Display name (category name or token name)
            value: Token value (for token nodes only)
            is_category: Whether this is a category node
            category: TokenCategory enum value
        """
        self.name = name
        self.value = value
        self.is_category = is_category
        self.category = category
        self.children: list[TokenTreeNode] = []
        self.parent: TokenTreeNode | None = None

    def add_child(self, child: "TokenTreeNode"):
        """Add child node.

        Args:
            child: Child node to add
        """
        child.parent = self
        self.children.append(child)

    def child_at(self, row: int) -> "TokenTreeNode | None":
        """Get child at row index.

        Args:
            row: Row index

        Returns:
            Child node or None if out of bounds
        """
        if 0 <= row < len(self.children):
            return self.children[row]
        return None

    def row(self) -> int:
        """Get row index of this node in parent's children.

        Returns:
            Row index, or 0 if no parent
        """
        if self.parent:
            return self.parent.children.index(self)
        return 0


class TokenTreeModel(QAbstractItemModel):
    """Hierarchical model for token browser.

    Structure:
        Root
        ├── Category 1 (base)
        │   ├── Token 1
        │   ├── Token 2
        │   └── ...
        ├── Category 2 (button)
        │   ├── Token 1
        │   └── ...
        └── ...
    """

    def __init__(self, document: ThemeDocument, parent=None):
        """Initialize token tree model.

        Args:
            document: ThemeDocument to display
            parent: Parent QObject
        """
        super().__init__(parent)
        self._document = document
        self._root = self._build_tree()

        # Connect to document changes
        document.token_changed.connect(self._on_token_changed)

    def _build_tree(self) -> TokenTreeNode:
        """Build hierarchical tree from ColorTokenRegistry.

        Returns:
            Root node with full tree structure
        """
        root = TokenTreeNode("Tokens", is_category=False)

        # Iterate through all categories
        for category in TokenCategory:
            # Create category node
            token_list = ColorTokenRegistry.get_tokens_by_category(category)
            category_display_name = category.value.replace('_', ' ').title()
            category_node = TokenTreeNode(
                name=category_display_name,
                is_category=True,
                category=category
            )
            category_node.parent = root
            root.children.append(category_node)

            # Get tokens for this category
            for token in token_list:
                # Get token value from document (token is a ColorToken object)
                token_name = token.name
                token_value = self._document.get_token(token_name)

                # If no user-defined value, use the default dark value for preview
                # This ensures all tokens show color icons, not just user-defined ones
                if not token_value and token.default_dark:
                    token_value = token.default_dark

                # Create token node
                token_node = TokenTreeNode(
                    name=token_name,
                    value=token_value,
                    is_category=False,
                    category=category
                )
                category_node.add_child(token_node)

        return root

    def _create_color_icon(self, color: QColor, size: int = 16) -> QPixmap:
        """Create a color icon with border for tree decoration.

        Creates a square pixmap filled with the given color and a subtle border
        to make it visible even for white/light colors.

        Args:
            color: QColor to display
            size: Icon size in pixels (default: 16)

        Returns:
            QPixmap icon with color fill and border
        """
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Fill with color
        painter.setBrush(color)

        # Draw border (darker for light colors, lighter for dark colors)
        # Calculate luminance to determine if color is light or dark
        luminance = (0.299 * color.red() + 0.587 * color.green() + 0.114 * color.blue())

        if luminance > 128:  # Light color
            border_color = QColor(100, 100, 100)  # Dark gray border
        else:  # Dark color
            border_color = QColor(180, 180, 180)  # Light gray border

        painter.setPen(QPen(border_color, 1))

        # Draw rounded rectangle
        painter.drawRoundedRect(0, 0, size - 1, size - 1, 2, 2)

        painter.end()

        return pixmap

    def _on_token_changed(self, token_name: str, token_value: str):
        """Handle token value change from document.

        Args:
            token_name: Changed token name
            token_value: New token value
        """
        # Find the token node and update its value
        def find_and_update_node(node: TokenTreeNode, path: list) -> tuple[bool, list]:
            """Recursively find and update token node.

            Returns:
                (found, path_to_node) where path_to_node is list of (parent, row) tuples
            """
            if not node.is_category and node.name == token_name:
                node.value = token_value
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
            for parent_node, row in path_to_node:
                parent_index = self.index(row, 0, parent_index)

            # Emit dataChanged for ONLY the changed row (both columns)
            # This is MUCH more efficient than layoutChanged and won't corrupt Qt state
            self.dataChanged.emit(
                parent_index,  # Top-left (Name column)
                self.index(parent_index.row(), 1, parent_index.parent()),  # Bottom-right (Value column)
            )

    # QAbstractItemModel interface implementation

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        """Create index for item at row/column under parent.

        Args:
            row: Row index
            column: Column index
            parent: Parent index

        Returns:
            Model index
        """
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
        """Get parent index of item.

        Args:
            index: Child index

        Returns:
            Parent index
        """
        if not index.isValid():
            return QModelIndex()

        child_node = index.internalPointer()
        parent_node = child_node.parent

        if parent_node == self._root or parent_node is None:
            return QModelIndex()

        return self.createIndex(parent_node.row(), 0, parent_node)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Get number of rows under parent.

        Args:
            parent: Parent index

        Returns:
            Number of child rows
        """
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parent_node = self._root
        else:
            parent_node = parent.internalPointer()

        return len(parent_node.children)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Get number of columns.

        Args:
            parent: Parent index

        Returns:
            Number of columns (always 1)
        """
        return 1

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        """Get data for index and role.

        Args:
            index: Model index
            role: Data role

        Returns:
            Data for role
        """
        if not index.isValid():
            return None

        node = index.internalPointer()

        if role == Qt.DisplayRole:
            # Display text
            if node.is_category:
                # Category: "Button (18)"
                count = len(node.children)
                return f"{node.name} ({count})"
            else:
                # Token: just the token name
                return node.name

        elif role == Qt.DecorationRole:
            # Color preview for token nodes (not categories)
            if not node.is_category and node.value:
                try:
                    color = QColor(node.value)
                    if color.isValid():
                        # Return pixmap icon instead of raw QColor to add border
                        return self._create_color_icon(color)
                except:
                    pass
            return None

        elif role == Qt.ToolTipRole:
            # Tooltip
            if node.is_category:
                return f"{node.name} category with {len(node.children)} tokens"
            else:
                value_display = node.value if node.value else "(using default)"
                return f"{node.name}\nValue: {value_display}"

        elif role == Qt.UserRole:
            # Custom data: return the node itself
            return node

        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """Get item flags.

        Args:
            index: Model index

        Returns:
            Item flags
        """
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def get_token_name(self, index: QModelIndex) -> str | None:
        """Get token name from index.

        Args:
            index: Model index

        Returns:
            Token name, or None if not a token node
        """
        if not index.isValid():
            return None

        node = index.internalPointer()
        if not node.is_category:
            return node.name
        return None

    def get_token_value(self, index: QModelIndex) -> str | None:
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
