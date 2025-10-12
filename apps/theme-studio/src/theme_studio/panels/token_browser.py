"""Token Browser Panel - Left panel for browsing theme tokens."""

from PySide6.QtCore import QSortFilterProxyModel, Qt, Signal
from PySide6.QtWidgets import QLineEdit, QTreeView, QVBoxLayout, QWidget

from ..widgets import TokenTreeModel


class TokenBrowserPanel(QWidget):
    """Token browser panel - displays hierarchical token tree.

    Uses OS/system theme - no custom theming applied.

    Phase 1: Read-only tree view with categories and color preview
    Phase 2: Add token value editing

    Signals:
        token_selected(str): Emitted when a token is selected (token name)
        token_edit_requested(str, str): Emitted when user double-clicks token (token_name, current_value)
    """

    # Signals
    token_selected = Signal(str)  # token_name
    token_edit_requested = Signal(str, str)  # token_name, current_value

    def __init__(self, parent=None):
        super().__init__(parent)
        self._model = None
        self._proxy_model = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup UI with search bar and tree view."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # Create search bar (Task 3.3)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search tokens...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self._on_search_text_changed)
        layout.addWidget(self.search_input)

        # Create tree view
        self.tree_view = QTreeView()
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setRootIsDecorated(True)
        self.tree_view.setAnimated(True)
        self.tree_view.setUniformRowHeights(True)

        # Single selection mode
        self.tree_view.setSelectionMode(QTreeView.SingleSelection)

        # Enable alternating row colors - now automatically themed via QPalette
        self.tree_view.setAlternatingRowColors(True)

        layout.addWidget(self.tree_view)

    def set_model(self, model: TokenTreeModel):
        """Set the token tree model.

        Args:
            model: TokenTreeModel to display
        """
        self._model = model

        # Create proxy model for filtering (Task 3.3)
        self._proxy_model = QSortFilterProxyModel()
        self._proxy_model.setSourceModel(model)
        self._proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self._proxy_model.setRecursiveFilteringEnabled(True)  # Filter child items
        self._proxy_model.setFilterRole(Qt.DisplayRole)

        # Set proxy model on tree view
        self.tree_view.setModel(self._proxy_model)

        # Expand all categories
        self.tree_view.expandAll()

        # Connect selection signal now that model is set
        if self.tree_view.selectionModel():
            self.tree_view.selectionModel().selectionChanged.connect(self._on_selection_changed)

        # Connect double-click for quick editing
        self.tree_view.doubleClicked.connect(self._on_item_double_clicked)

    def _on_search_text_changed(self, text: str):
        """Handle search text change.

        Args:
            text: Search text
        """
        if self._proxy_model:
            # Set filter pattern
            self._proxy_model.setFilterWildcard(f"*{text}*")

            # Expand all if filtering, collapse if no filter
            if text:
                self.tree_view.expandAll()
            else:
                self.tree_view.expandAll()  # Keep expanded for now

    def _on_selection_changed(self, selected, deselected):
        """Handle selection change in tree view.

        Args:
            selected: QItemSelection of selected items
            deselected: QItemSelection of deselected items
        """
        if not self._model or not self._proxy_model:
            return

        indexes = selected.indexes()
        if not indexes:
            return

        # Map proxy index to source index
        proxy_index = indexes[0]
        source_index = self._proxy_model.mapToSource(proxy_index)

        token_name = self._model.get_token_name(source_index)

        if token_name:
            # This is a token node, emit signal
            self.token_selected.emit(token_name)

    def _on_item_double_clicked(self, proxy_index):
        """Handle double-click on tree item - open color editor.

        Args:
            proxy_index: QModelIndex from proxy model
        """
        if not self._model or not self._proxy_model:
            return

        # Map proxy index to source index
        source_index = self._proxy_model.mapToSource(proxy_index)

        # Get token name and value
        token_name = self._model.get_token_name(source_index)
        if not token_name:
            # Category node - expand/collapse instead
            if self.tree_view.isExpanded(proxy_index):
                self.tree_view.collapse(proxy_index)
            else:
                self.tree_view.expand(proxy_index)
            return

        # Get current token value
        token_value = self._model.get_token_value(source_index)

        # Emit edit request signal
        self.token_edit_requested.emit(token_name, token_value if token_value else "")
