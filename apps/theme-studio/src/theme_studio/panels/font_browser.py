"""Font Browser Panel - Left panel for browsing font tokens.

Mirrors TokenBrowserPanel architecture for perfect consistency.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QCheckBox, QLineEdit, QTreeView, QVBoxLayout, QWidget

from ..models import ThemeDocument
from ..widgets.font_filter_proxy_model import FontFilterProxyModel
from ..widgets.font_tree_model import FontTreeModel


class FontBrowserPanel(QWidget):
    """Font token browser panel with search and widget filtering.

    Uses 3-layer architecture (model → proxy → view) exactly like TokenBrowserPanel.

    Signals:
        font_token_selected(str): Emitted when a token is selected (token path)
        font_token_edit_requested(str, value): Emitted on double-click (path, current_value)
    """

    # Signals
    font_token_selected = Signal(str)  # token_path
    font_token_edit_requested = Signal(str, object)  # token_path, current_value

    def __init__(self, parent=None):
        super().__init__(parent)
        self._model = None
        self._proxy_model = None
        self._current_widget_tokens = None  # Token paths for current preview widget
        self._setup_ui()

    def _setup_ui(self):
        """Setup UI with search bar, widget filter, and tree view."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # Create search bar (mirrors color browser)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search font tokens...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self._on_search_text_changed)
        layout.addWidget(self.search_input)

        # Add checkbox to filter by current widget (CRITICAL - was missing!)
        self.widget_filter_checkbox = QCheckBox("Show only current widget fonts")
        self.widget_filter_checkbox.setChecked(False)
        self.widget_filter_checkbox.stateChanged.connect(self._on_widget_filter_changed)
        self.widget_filter_checkbox.setEnabled(False)  # Disabled until widget selected
        layout.addWidget(self.widget_filter_checkbox)

        # Create tree view
        self.tree_view = QTreeView()
        self.tree_view.setHeaderHidden(True)  # CRITICAL: Hide header (single column)
        self.tree_view.setRootIsDecorated(True)
        self.tree_view.setAnimated(True)
        self.tree_view.setUniformRowHeights(True)

        # Single selection mode
        self.tree_view.setSelectionMode(QTreeView.SingleSelection)

        # Enable alternating row colors
        self.tree_view.setAlternatingRowColors(True)

        layout.addWidget(self.tree_view)

    def set_document(self, document: ThemeDocument):
        """Set the document to display.

        Args:
            document: ThemeDocument to display
        """
        # Create source model
        self._model = FontTreeModel(document, self)

        # Create proxy model for filtering (CRITICAL - was missing!)
        self._proxy_model = FontFilterProxyModel()
        self._proxy_model.setSourceModel(self._model)
        self._proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self._proxy_model.setRecursiveFilteringEnabled(True)  # Hide empty categories
        self._proxy_model.setFilterRole(Qt.DisplayRole)

        # Set proxy model on tree view (NOT source model!)
        self.tree_view.setModel(self._proxy_model)

        # Expand all categories
        self.tree_view.expandAll()

        # Connect selection signal now that model is set
        if self.tree_view.selectionModel():
            self.tree_view.selectionModel().selectionChanged.connect(
                self._on_selection_changed
            )

        # Connect double-click for editing
        self.tree_view.doubleClicked.connect(self._on_item_double_clicked)

    def _on_search_text_changed(self, text: str):
        """Handle search text change.

        Args:
            text: Search text
        """
        if self._proxy_model:
            # Set filter pattern
            self._proxy_model.setFilterWildcard(f"*{text}*")

            # Expand all if filtering
            if text:
                self.tree_view.expandAll()
            else:
                self.tree_view.expandAll()  # Keep expanded

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

        token_path = self._model.get_token_path(source_index)

        if token_path:
            # This is a token node, emit signal
            self.font_token_selected.emit(token_path)

    def _on_item_double_clicked(self, proxy_index):
        """Handle double-click on tree item - open font editor.

        Args:
            proxy_index: QModelIndex from proxy model
        """
        if not self._model or not self._proxy_model:
            return

        # Map proxy index to source index
        source_index = self._proxy_model.mapToSource(proxy_index)

        # Get token path and value
        token_path = self._model.get_token_path(source_index)
        if not token_path:
            # Category node - expand/collapse instead
            if self.tree_view.isExpanded(proxy_index):
                self.tree_view.collapse(proxy_index)
            else:
                self.tree_view.expand(proxy_index)
            return

        # Get current token value
        token_value = self._model.get_token_value(source_index)

        # Emit edit request signal
        self.font_token_edit_requested.emit(token_path, token_value)

    def set_current_widget_tokens(self, token_paths: set[str] | None):
        """Set the font tokens used by the current preview widget.

        This enables the "Show only current widget fonts" checkbox and
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
            self.widget_filter_checkbox.setText(
                f"Show only current widget fonts ({count})"
            )
        else:
            self.widget_filter_checkbox.setText("Show only current widget fonts")
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


__all__ = ["FontBrowserPanel"]
