"""Main MultiSplit widget implementation.

This is the public API for the MultiSplit widget.
"""

from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from .controller.controller import PaneController
from .core.focus import FocusManager
from .core.model import PaneModel
from .core.nodes import LeafNode
from .core.session import SessionManager
from .core.types import Direction, PaneId, SizeConstraints, WherePosition, WidgetId
from .view.container import PaneContainer, WidgetProvider


class MultisplitWidget(QWidget):
    """Main MultiSplit widget with complete public API.

    This widget provides a recursive split-pane interface with:
    - Dynamic splitting in any direction
    - Focus management and keyboard navigation
    - Drag-to-resize dividers
    - Session persistence
    - Undo/redo support
    - Widget provider pattern for flexibility
    """

    # Signals
    widget_needed = Signal(str, str)  # widget_id, pane_id
    pane_added = Signal(str)  # pane_id
    pane_removed = Signal(str)  # pane_id
    pane_focused = Signal(str)  # pane_id
    layout_changed = Signal()
    validation_failed = Signal(list)  # error messages

    def __init__(self, provider: Optional[WidgetProvider] = None,
                 parent: Optional[QWidget] = None):
        """Initialize MultiSplit widget.

        Args:
            provider: Optional widget provider
            parent: Parent widget
        """
        super().__init__(parent)

        # Core components
        self.model = PaneModel()
        self.controller = PaneController(self.model)
        self.container = PaneContainer(self.model, provider, self)
        self.focus_manager = FocusManager(self.model)
        self.session_manager = SessionManager(self.model)

        # Setup layout
        from PySide6.QtWidgets import QVBoxLayout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.container)

        # Connect signals
        self._connect_signals()

        # Initialize with single pane if empty
        if not self.model.root:
            self.initialize_empty()

    def _connect_signals(self):
        """Connect internal signals to public signals."""
        # Forward container signals
        self.container.widget_needed.connect(self.widget_needed.emit)
        self.container.pane_focused.connect(
            lambda pane_id: self.model.set_focused_pane(PaneId(pane_id))
        )

        # Forward model signals
        self.model.signals.pane_added.connect(
            lambda pane_id: self.pane_added.emit(str(pane_id))
        )
        self.model.signals.pane_removed.connect(
            lambda pane_id: self.pane_removed.emit(str(pane_id))
        )
        self.model.signals.focus_changed.connect(
            lambda old, new: self.pane_focused.emit(str(new)) if new else None
        )
        self.model.signals.structure_changed.connect(
            lambda: self.layout_changed.emit()
        )
        self.model.signals.validation_failed.connect(
            lambda errors: self.validation_failed.emit(errors)
        )

        # Handle splitter moves
        self.container.splitter_moved.connect(self._on_splitter_moved)

    def _on_splitter_moved(self, node_id: str, ratios: List[float]):
        """Handle splitter movement."""
        from .controller.commands import SetRatiosCommand
        from .core.types import NodeId

        command = SetRatiosCommand(self.model, NodeId(node_id), ratios)
        self.controller.execute_command(command)

    # Public API

    def initialize_empty(self, widget_id: str = "default"):
        """Initialize with a single pane.

        Args:
            widget_id: Widget ID for initial pane
        """
        from .core.logger import logger
        from .core.utils import generate_pane_id

        pane_id = generate_pane_id()
        leaf = LeafNode(pane_id, WidgetId(widget_id))

        logger.info(f"Initializing empty with widget: {widget_id}, pane: {pane_id}")

        self.model.root = leaf
        self.model._rebuild_registry()
        self.model.set_focused_pane(pane_id)

        # Emit signals to update view
        logger.debug("Emitting structure_changed signal for initial setup")
        self.model.signals.structure_changed.emit()
        self.model.signals.pane_added.emit(pane_id)

    def split_pane(self, pane_id: str, widget_id: str,
                  position: WherePosition, ratio: float = 0.5) -> bool:
        """Split a pane.

        Args:
            pane_id: ID of pane to split
            widget_id: Widget ID for new pane
            position: Where to place new pane
            ratio: Split ratio (0.0-1.0)

        Returns:
            True if successful
        """
        success, validation = self.controller.split_pane(
            PaneId(pane_id), WidgetId(widget_id), position, ratio
        )

        if not success and validation.errors:
            self.validation_failed.emit(validation.errors)

        return success

    def remove_pane(self, pane_id: str) -> bool:
        """Remove a pane.

        Args:
            pane_id: ID of pane to remove

        Returns:
            True if successful
        """
        success, validation = self.controller.remove_pane(PaneId(pane_id))

        if not success and validation.errors:
            self.validation_failed.emit(validation.errors)

        return success

    def focus_pane(self, pane_id: str) -> bool:
        """Focus a pane.

        Args:
            pane_id: ID of pane to focus

        Returns:
            True if successful
        """
        return self.model.set_focused_pane(PaneId(pane_id))

    def navigate_focus(self, direction: Direction) -> bool:
        """Navigate focus in a direction.

        Args:
            direction: Direction to navigate

        Returns:
            True if focus moved
        """
        target = self.focus_manager.navigate(direction)
        if target:
            return self.model.set_focused_pane(target)
        return False

    def set_constraints(self, pane_id: str,
                       min_width: int = 50,
                       min_height: int = 50,
                       max_width: Optional[int] = None,
                       max_height: Optional[int] = None) -> bool:
        """Set size constraints for a pane.

        Args:
            pane_id: ID of pane
            min_width: Minimum width in pixels
            min_height: Minimum height in pixels
            max_width: Maximum width (None = no limit)
            max_height: Maximum height (None = no limit)

        Returns:
            True if successful
        """
        from .controller.commands import SetConstraintsCommand

        constraints = SizeConstraints(
            min_width, min_height, max_width, max_height
        )
        command = SetConstraintsCommand(
            self.model, PaneId(pane_id), constraints
        )
        return self.controller.execute_command(command)

    def undo(self) -> bool:
        """Undo last operation."""
        return self.controller.undo()

    def redo(self) -> bool:
        """Redo last undone operation."""
        return self.controller.redo()

    def can_undo(self) -> bool:
        """Check if undo is available."""
        return self.controller.can_undo()

    def can_redo(self) -> bool:
        """Check if redo is available."""
        return self.controller.can_redo()

    def save_layout(self, filepath: Path) -> bool:
        """Save layout to file.

        Args:
            filepath: Path to save file

        Returns:
            True if successful
        """
        return self.session_manager.save_to_file(filepath)

    def load_layout(self, filepath: Path) -> bool:
        """Load layout from file.

        Args:
            filepath: Path to load file

        Returns:
            True if successful
        """
        return self.session_manager.load_from_file(filepath)

    def get_layout_json(self) -> str:
        """Get layout as JSON string."""
        return self.session_manager.save_to_string()

    def set_layout_json(self, json_str: str) -> bool:
        """Set layout from JSON string."""
        return self.session_manager.load_from_string(json_str)

    def get_pane_ids(self) -> List[str]:
        """Get all pane IDs."""
        return [str(pane_id) for pane_id in self.model.get_all_pane_ids()]

    def get_focused_pane(self) -> Optional[str]:
        """Get currently focused pane ID."""
        if self.model.focused_pane_id:
            return str(self.model.focused_pane_id)
        return None

    def set_widget_provider(self, provider: WidgetProvider):
        """Set widget provider.

        Args:
            provider: Widget provider to use
        """
        self.container.set_widget_provider(provider)
