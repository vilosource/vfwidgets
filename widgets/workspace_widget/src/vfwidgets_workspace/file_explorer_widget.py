"""File explorer widget (QTreeView wrapper with theming)."""

import logging
from typing import Optional

from PySide6.QtCore import QModelIndex, Qt, Signal
from PySide6.QtWidgets import QAbstractItemView, QTreeView, QVBoxLayout, QWidget

from .file_system_model import MultiRootFileSystemModel

logger = logging.getLogger(__name__)

# Check if theme system available
try:
    from vfwidgets_theme import ThemedWidget

    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False
    ThemedWidget = object  # type: ignore


# Conditional base class
if THEME_AVAILABLE:
    _BaseClass = type("_BaseClass", (ThemedWidget, QWidget), {})
else:
    _BaseClass = QWidget


class FileExplorerWidget(_BaseClass):  # type: ignore
    """File tree view with automatic theme integration.

    Wraps QTreeView and provides VS Code-style theming if vfwidgets-theme available.
    """

    # Signals
    file_clicked = Signal(str)  # file_path
    file_double_clicked = Signal(str)  # file_path
    folder_expanded = Signal(str)  # folder_path
    folder_collapsed = Signal(str)  # folder_path
    context_menu_requested = Signal(str, object)  # file_path, QPoint

    # Theme configuration mapping (if ThemedWidget available)
    if THEME_AVAILABLE:
        theme_config = {
            # Container
            "background": "sideBar.background",
            "foreground": "sideBar.foreground",
            # List selection
            "selection_bg": "list.activeSelectionBackground",
            "selection_fg": "list.activeSelectionForeground",
            "inactive_selection_bg": "list.inactiveSelectionBackground",
            "hover_bg": "list.hoverBackground",
            # Tree guides
            "indent_guide": "tree.indentGuidesStroke",
            # Icons
            "icon_fg": "icon.foreground",
        }

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize file explorer widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Track expanded state
        self._expanded_paths: set[str] = set()

        # Setup UI
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup widget UI."""
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Tree view
        self._tree_view = QTreeView(self)
        self._tree_view.setHeaderHidden(True)
        self._tree_view.setUniformRowHeights(True)
        self._tree_view.setAnimated(False)  # Performance
        self._tree_view.setIndentation(16)
        self._tree_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        # Connect signals
        self._tree_view.clicked.connect(self._on_clicked)
        self._tree_view.doubleClicked.connect(self._on_double_clicked)
        self._tree_view.expanded.connect(self._on_expanded)
        self._tree_view.collapsed.connect(self._on_collapsed)
        self._tree_view.customContextMenuRequested.connect(self._on_context_menu)

        layout.addWidget(self._tree_view)

        # Apply theme if available
        if THEME_AVAILABLE:
            # ThemedWidget will automatically apply colors via theme_config
            pass
        else:
            # Fallback to hardcoded dark theme
            self._apply_fallback_theme()

    def _apply_fallback_theme(self) -> None:
        """Fallback theme when vfwidgets-theme not available."""
        self._tree_view.setStyleSheet(
            """
            QTreeView {
                background-color: #252526;
                color: #cccccc;
                border: none;
                outline: none;
            }
            QTreeView::item {
                padding: 4px;
                border-radius: 2px;
            }
            QTreeView::item:hover {
                background-color: #2a2d2e;
            }
            QTreeView::item:selected:active {
                background-color: #094771;
                color: #ffffff;
            }
            QTreeView::item:selected:!active {
                background-color: #37373d;
                color: #cccccc;
            }
        """
        )

    def theme_changed(self) -> None:
        """Called by ThemedWidget when theme changes.

        Override to apply theme colors to QTreeView via stylesheet.
        """
        if not THEME_AVAILABLE:
            return

        # Get theme colors with fallbacks (in case tokens are missing)
        bg = self.get_theme_color("background") or "#ffffff"
        fg = self.get_theme_color("foreground") or "#333333"
        sel_bg = self.get_theme_color("selection_bg") or "#0078d4"
        sel_fg = self.get_theme_color("selection_fg") or "#ffffff"
        inactive_sel_bg = self.get_theme_color("inactive_selection_bg") or "#e0e0e0"
        hover_bg = self.get_theme_color("hover_bg") or "#f0f0f0"

        # Apply via stylesheet (QTreeView doesn't support Qt properties for all features)
        stylesheet = f"""
            QTreeView {{
                background-color: {bg};
                color: {fg};
                border: none;
                outline: none;
            }}
            QTreeView::item {{
                padding: 4px;
                border-radius: 2px;
            }}
            QTreeView::item:hover {{
                background-color: {hover_bg};
            }}
            QTreeView::item:selected:active {{
                background-color: {sel_bg};
                color: {sel_fg};
            }}
            QTreeView::item:selected:!active {{
                background-color: {inactive_sel_bg};
            }}
        """
        self._tree_view.setStyleSheet(stylesheet)

    def set_model(self, model: MultiRootFileSystemModel) -> None:
        """Set the filesystem model.

        Args:
            model: Multi-root filesystem model
        """
        self._tree_view.setModel(model)

    def model(self) -> Optional[MultiRootFileSystemModel]:
        """Get the filesystem model.

        Returns:
            Multi-root filesystem model or None
        """
        return self._tree_view.model()  # type: ignore

    def is_expanded(self, path: str) -> bool:
        """Check if path is currently expanded.

        Args:
            path: Absolute path

        Returns:
            True if expanded
        """
        return path in self._expanded_paths

    def _get_path_from_index(self, index: QModelIndex) -> Optional[str]:
        """Get absolute path from model index.

        Args:
            index: Model index

        Returns:
            Absolute path or None
        """
        if not index.isValid():
            return None

        model = self._tree_view.model()
        if not model:
            return None

        # Get FileInfo from UserRole
        file_info = index.data(Qt.ItemDataRole.UserRole)
        if file_info:
            return file_info.path

        return None

    def _on_clicked(self, index: QModelIndex) -> None:
        """Handle item clicked.

        Args:
            index: Clicked index
        """
        path = self._get_path_from_index(index)
        if path:
            self.file_clicked.emit(path)

    def _on_double_clicked(self, index: QModelIndex) -> None:
        """Handle item double-clicked.

        Args:
            index: Double-clicked index
        """
        path = self._get_path_from_index(index)
        if path:
            self.file_double_clicked.emit(path)

    def _on_expanded(self, index: QModelIndex) -> None:
        """Handle folder expanded.

        Args:
            index: Expanded index
        """
        path = self._get_path_from_index(index)
        if path:
            # Track in expanded paths
            self._expanded_paths.add(path)

            # Notify model (for icon updates)
            model = self.model()
            if model:
                model.set_expanded(path, True)

            # Emit signal
            self.folder_expanded.emit(path)

    def _on_collapsed(self, index: QModelIndex) -> None:
        """Handle folder collapsed.

        Args:
            index: Collapsed index
        """
        path = self._get_path_from_index(index)
        if path:
            # Remove from expanded paths
            self._expanded_paths.discard(path)

            # Notify model (for icon updates)
            model = self.model()
            if model:
                model.set_expanded(path, False)

            # Emit signal
            self.folder_collapsed.emit(path)

    def _on_context_menu(self, position) -> None:
        """Handle context menu request.

        Args:
            position: Position where menu requested
        """
        index = self._tree_view.indexAt(position)
        path = self._get_path_from_index(index)

        if path:
            global_pos = self._tree_view.viewport().mapToGlobal(position)
            self.context_menu_requested.emit(path, global_pos)

    def expand_path(self, path: str) -> None:
        """Expand a specific path.

        Args:
            path: Absolute path to expand
        """
        # TODO: Find index for path and expand
        # This requires implementing _find_index_by_path in the model
        pass

    def select_path(self, path: str) -> None:
        """Select a specific path.

        Args:
            path: Absolute path to select
        """
        # TODO: Find index for path and select
        pass
