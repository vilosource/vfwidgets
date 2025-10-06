"""Token Browser Widget - Theme Editor Component.

This module provides the TokenBrowserWidget for browsing and selecting theme tokens
in the theme editor. Tokens are organized into categories for easy navigation.

Phase 1: Core Infrastructure
"""

from typing import Dict, List, Optional, Set

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QLineEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QTreeWidgetItemIterator,
    QVBoxLayout,
    QWidget,
)

from ..core.token_constants import Tokens
from ..logging import get_debug_logger
from .base import ThemedWidget

logger = get_debug_logger(__name__)


class TokenBrowserWidget(ThemedWidget, QWidget):
    """Tree browser for theme tokens organized by category.

    Displays all 200 theme tokens organized into categories like:
    - BASE COLORS (11 tokens)
    - BUTTON COLORS (18 tokens)
    - INPUT/DROPDOWN COLORS (18 tokens)
    - etc.

    Features:
    - Hierarchical tree view with categories
    - Search/filter functionality
    - Token selection with signals
    - Display token paths (e.g., "button.background")

    Signals:
        token_selected(str): Emitted when a token is selected (token path)
        category_changed(str): Emitted when category selection changes
    """

    # Signals
    token_selected = Signal(str)  # Token path like "button.background"
    category_changed = Signal(str)  # Category name like "BUTTON COLORS"

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize token browser.

        Args:
            parent: Parent widget

        """
        super().__init__(parent)

        # Token organization
        self._categories: Dict[str, List[tuple[str, str]]] = {}
        self._all_tokens: Set[str] = set()
        self._current_filter: str = ""

        # Build token database
        self._build_token_database()

        # Setup UI
        self._setup_ui()

        # Populate tree
        self._populate_tree()

        logger.debug(f"TokenBrowserWidget initialized with {len(self._all_tokens)} tokens")

    def _build_token_database(self) -> None:
        """Build token database from Tokens class."""
        # Token categories with their tokens
        # Format: Category Name -> [(CONSTANT_NAME, token.path), ...]

        self._categories = {
            "BASE COLORS": [],
            "BUTTON COLORS": [],
            "INPUT/DROPDOWN COLORS": [],
            "LIST/TREE COLORS": [],
            "EDITOR COLORS": [],
            "SIDEBAR COLORS": [],
            "PANEL COLORS": [],
            "TAB COLORS": [],
            "ACTIVITY BAR COLORS": [],
            "STATUS BAR COLORS": [],
            "TITLE BAR COLORS": [],
            "MENU COLORS": [],
            "SCROLLBAR COLORS": [],
            "TERMINAL COLORS": [],
            "MISCELLANEOUS COLORS": [],
        }

        # Extract all tokens from Tokens class
        for attr_name in dir(Tokens):
            if attr_name.startswith("_"):
                continue

            token_value = getattr(Tokens, attr_name)
            if not isinstance(token_value, str):
                continue

            # Categorize token based on prefix
            if attr_name.startswith("COLORS_"):
                category = "BASE COLORS"
            elif attr_name.startswith("BUTTON_"):
                category = "BUTTON COLORS"
            elif attr_name.startswith(("INPUT_", "DROPDOWN_", "COMBOBOX_")):
                category = "INPUT/DROPDOWN COLORS"
            elif attr_name.startswith(("LIST_", "TREE_", "TABLE_")):
                category = "LIST/TREE COLORS"
            elif attr_name.startswith("EDITOR_"):
                category = "EDITOR COLORS"
            elif attr_name.startswith("SIDEBAR_"):
                category = "SIDEBAR COLORS"
            elif attr_name.startswith("PANEL_"):
                category = "PANEL COLORS"
            elif attr_name.startswith("TAB_"):
                category = "TAB COLORS"
            elif attr_name.startswith("ACTIVITYBAR_"):
                category = "ACTIVITY BAR COLORS"
            elif attr_name.startswith("STATUSBAR_"):
                category = "STATUS BAR COLORS"
            elif attr_name.startswith("TITLEBAR_"):
                category = "TITLE BAR COLORS"
            elif attr_name.startswith(("MENU_", "MENUBAR_")):
                category = "MENU COLORS"
            elif attr_name.startswith("SCROLLBAR_"):
                category = "SCROLLBAR COLORS"
            elif attr_name.startswith("TERMINAL_"):
                category = "TERMINAL COLORS"
            else:
                category = "MISCELLANEOUS COLORS"

            # Add to category
            if category in self._categories:
                self._categories[category].append((attr_name, token_value))
                self._all_tokens.add(token_value)

        # Sort tokens within each category
        for category in self._categories:
            self._categories[category].sort(key=lambda x: x[1])  # Sort by token path

    def _setup_ui(self) -> None:
        """Setup user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Search box
        self._search_box = QLineEdit()
        self._search_box.setPlaceholderText("Search tokens...")
        self._search_box.textChanged.connect(self._on_search_changed)
        layout.addWidget(self._search_box)

        # Token tree
        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(["Token", "Path"])
        self._tree.setColumnWidth(0, 200)
        self._tree.itemSelectionChanged.connect(self._on_selection_changed)
        self._tree.itemExpanded.connect(self._on_category_expanded)
        layout.addWidget(self._tree)

    def _populate_tree(self, filter_text: str = "") -> None:
        """Populate tree with tokens, optionally filtered.

        Args:
            filter_text: Search filter text

        """
        self._tree.clear()
        filter_lower = filter_text.lower()

        for category_name, tokens in self._categories.items():
            # Filter tokens if search text provided
            if filter_text:
                filtered_tokens = [
                    (name, path)
                    for name, path in tokens
                    if filter_lower in name.lower() or filter_lower in path.lower()
                ]
            else:
                filtered_tokens = tokens

            # Skip empty categories when filtering
            if not filtered_tokens:
                continue

            # Create category item
            category_item = QTreeWidgetItem(self._tree)
            category_item.setText(0, f"{category_name} ({len(filtered_tokens)})")
            category_item.setData(0, Qt.ItemDataRole.UserRole, category_name)
            category_item.setExpanded(bool(filter_text))  # Expand if filtering

            # Add tokens to category
            for const_name, token_path in filtered_tokens:
                token_item = QTreeWidgetItem(category_item)
                token_item.setText(0, const_name)
                token_item.setText(1, token_path)
                token_item.setData(0, Qt.ItemDataRole.UserRole, token_path)

    def _on_search_changed(self, text: str) -> None:
        """Handle search text changes.

        Args:
            text: New search text

        """
        self._current_filter = text
        self._populate_tree(text)

        logger.debug(f"Token search filter: '{text}'")

    def _on_selection_changed(self) -> None:
        """Handle token selection changes."""
        selected_items = self._tree.selectedItems()
        if not selected_items:
            return

        item = selected_items[0]

        # Get token path from user data
        token_path = item.data(0, Qt.ItemDataRole.UserRole)

        # Check if it's a token (not a category)
        if token_path and token_path in self._all_tokens:
            logger.debug(f"Token selected: {token_path}")
            self.token_selected.emit(token_path)

    def _on_category_expanded(self, item: QTreeWidgetItem) -> None:
        """Handle category expansion.

        Args:
            item: Expanded tree item

        """
        category_name = item.data(0, Qt.ItemDataRole.UserRole)
        if category_name and category_name in self._categories:
            logger.debug(f"Category expanded: {category_name}")
            self.category_changed.emit(category_name)

    def get_selected_token(self) -> Optional[str]:
        """Get currently selected token path.

        Returns:
            Selected token path or None

        """
        selected_items = self._tree.selectedItems()
        if not selected_items:
            return None

        item = selected_items[0]
        token_path = item.data(0, Qt.ItemDataRole.UserRole)

        return token_path if token_path in self._all_tokens else None

    def select_token(self, token_path: str) -> bool:
        """Programmatically select a token.

        Args:
            token_path: Token path to select (e.g., "button.background")

        Returns:
            True if token found and selected

        """
        if token_path not in self._all_tokens:
            logger.warning(f"Token not found: {token_path}")
            return False

        # Find and select the token item
        iterator = QTreeWidgetItemIterator(self._tree)
        while iterator.value():
            item = iterator.value()
            if item.data(0, Qt.ItemDataRole.UserRole) == token_path:
                # Expand parent if needed
                if item.parent():
                    item.parent().setExpanded(True)

                # Select item
                self._tree.setCurrentItem(item)
                return True

            iterator += 1

        return False

    def clear_filter(self) -> None:
        """Clear search filter."""
        self._search_box.clear()

    def get_token_count(self) -> int:
        """Get total number of tokens.

        Returns:
            Total token count

        """
        return len(self._all_tokens)

    def get_category_count(self) -> int:
        """Get number of categories.

        Returns:
            Category count

        """
        return len([cat for cat, tokens in self._categories.items() if tokens])
