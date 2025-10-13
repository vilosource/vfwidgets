"""Token Browser Panel - Left panel for browsing theme tokens."""

from PySide6.QtCore import QModelIndex, QSortFilterProxyModel, Qt, Signal
from PySide6.QtWidgets import QCheckBox, QLineEdit, QTreeView, QVBoxLayout, QWidget

from ..widgets import TokenTreeModel


class TokenFilterProxyModel(QSortFilterProxyModel):
    """Custom proxy model that supports filtering by token paths."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._allowed_token_paths = None  # None means show all tokens
        self._source_model = None

    def setSourceModel(self, model):
        """Override to store source model reference."""
        self._source_model = model
        super().setSourceModel(model)

    def set_allowed_token_paths(self, token_paths: set[str] | None):
        """Set which token paths to show (None = show all).

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

        # Get token name for this index
        token_name = self._source_model.get_token_name(index)

        # If this is a category node (no token name), check if any children match
        if not token_name:
            # Category nodes are shown if they have any matching children
            # Qt's recursive filtering handles this automatically
            return super().filterAcceptsRow(source_row, source_parent)

        # This is a token node - check if it's in the allowed paths
        if self._allowed_token_paths is not None:
            if token_name not in self._allowed_token_paths:
                return False

        # Also apply text filter
        return super().filterAcceptsRow(source_row, source_parent)


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
        self._current_widget_tokens = None  # Token paths for current preview widget
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

        # Add checkbox to filter by current widget
        self.widget_filter_checkbox = QCheckBox("Show only current widget tokens")
        self.widget_filter_checkbox.setChecked(False)
        self.widget_filter_checkbox.stateChanged.connect(self._on_widget_filter_changed)
        self.widget_filter_checkbox.setEnabled(False)  # Disabled until widget is selected
        layout.addWidget(self.widget_filter_checkbox)

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

        # Create custom proxy model for filtering by token paths and text
        self._proxy_model = TokenFilterProxyModel()
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

    def set_current_widget_tokens(self, token_paths: set[str] | None):
        """Set the tokens used by the current preview widget.

        This enables the "Show only current widget tokens" checkbox and
        updates the filter if it's enabled.

        Args:
            token_paths: Set of token paths used by the widget, or None if no widget
        """
        self._current_widget_tokens = token_paths

        # Enable/disable the checkbox based on whether we have widget tokens
        self.widget_filter_checkbox.setEnabled(token_paths is not None)

        # Update the checkbox text to show token count
        if token_paths:
            count = len(token_paths)
            self.widget_filter_checkbox.setText(f"Show only current widget tokens ({count})")
        else:
            self.widget_filter_checkbox.setText("Show only current widget tokens")
            # Uncheck if no widget selected
            self.widget_filter_checkbox.setChecked(False)

        # Update filter if checkbox is currently enabled
        if self.widget_filter_checkbox.isChecked():
            self._apply_widget_filter()

    def _on_widget_filter_changed(self, state: int):
        """Handle widget filter checkbox state change.

        Args:
            state: Qt.CheckState value
        """
        self._apply_widget_filter()

    def _apply_widget_filter(self):
        """Apply the widget token filter based on checkbox state."""
        if not self._proxy_model:
            return

        if self.widget_filter_checkbox.isChecked() and self._current_widget_tokens:
            # Filter to show only current widget's tokens
            self._proxy_model.set_allowed_token_paths(self._current_widget_tokens)
            # Expand all to show filtered tokens
            self.tree_view.expandAll()
        else:
            # Show all tokens
            self._proxy_model.set_allowed_token_paths(None)
            # Expand all when removing filter
            self.tree_view.expandAll()
