"""Main MultiSplit widget implementation.

This is the public API for the MultiSplit widget.
"""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from .controller.controller import PaneController
from .core.focus import FocusManager
from .core.model import PaneModel
from .core.nodes import LeafNode
from .core.session import SessionManager
from .core.types import Direction, PaneId, SizeConstraints, SplitterStyle, WherePosition, WidgetId
from .view.container import PaneContainer, WidgetProvider

__all__ = ["MultisplitWidget"]


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
    focus_changed = Signal(str, str)  # old_pane_id, new_pane_id
    layout_changed = Signal()
    validation_failed = Signal(list)  # error messages

    # Private attributes (internal implementation)
    _model: PaneModel
    _controller: PaneController
    _container: PaneContainer
    _focus_manager: FocusManager
    _session_manager: SessionManager

    def __init__(self, provider: Optional[WidgetProvider] = None,
                 splitter_style: Optional[SplitterStyle] = None,
                 parent: Optional[QWidget] = None):
        """Initialize MultiSplit widget.

        Args:
            provider: Widget provider for on-demand widget creation.
                     MUST be provided in constructor - there is no setter method.
                     If None, placeholder widgets will be used.
                     See examples/01_basic_text_editor.py for correct usage.
            splitter_style: Splitter style configuration (None = use comfortable defaults).
                          Use SplitterStyle.minimal() for 1px borders (terminal emulators),
                          SplitterStyle.compact() for 3px borders, or customize fully.
            parent: Parent widget

        Warning:
            The provider parameter must be passed during initialization.
            There is NO set_widget_provider() method. Attempting to set
            the provider after construction will fail.

        Example - Basic usage:
            >>> from vfwidgets_multisplit.view.container import WidgetProvider
            >>> class MyProvider(WidgetProvider):
            ...     def provide_widget(self, widget_id, pane_id):
            ...         return QTextEdit()
            >>> provider = MyProvider()
            >>> multisplit = MultisplitWidget(provider=provider)  # Correct!

        Example - Minimal style for terminals:
            >>> from vfwidgets_multisplit import MultisplitWidget, SplitterStyle
            >>> style = SplitterStyle.minimal()  # 1px borders
            >>> multisplit = MultisplitWidget(provider=provider, splitter_style=style)

        Example - Custom style:
            >>> style = SplitterStyle(
            ...     handle_width=2,
            ...     handle_margin_horizontal=1,
            ...     handle_bg="#1e1e1e"
            ... )
            >>> multisplit = MultisplitWidget(provider=provider, splitter_style=style)
        """
        super().__init__(parent)

        # Core components (private - internal implementation)
        self._model = PaneModel()
        self._controller = PaneController(self._model)
        self._container = PaneContainer(self._model, provider, self)
        self._focus_manager = FocusManager(self._model)
        self._session_manager = SessionManager(self._model)

        # Setup layout
        from PySide6.QtWidgets import QVBoxLayout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._container)

        # Connect signals
        self._connect_signals()

        # Initialize with single pane if empty
        if not self._model.root:
            self.initialize_empty()

    def _connect_signals(self):
        """Connect internal signals to public signals."""
        # Forward container signals
        self._container.widget_needed.connect(self.widget_needed.emit)
        self._container.pane_focused.connect(
            lambda pane_id: self._model.set_focused_pane(PaneId(pane_id))
        )

        # Forward model signals
        self._model.signals.pane_added.connect(self._forward_pane_added)
        self._model.signals.pane_removed.connect(
            lambda pane_id: self.pane_removed.emit(str(pane_id))
        )
        self._model.signals.focus_changed.connect(self._forward_focus_changed)
        self._model.signals.structure_changed.connect(
            lambda: self.layout_changed.emit()
        )
        self._model.signals.validation_failed.connect(
            lambda errors: self.validation_failed.emit(errors)
        )

        # Handle splitter moves
        self._container.splitter_moved.connect(self._on_splitter_moved)

    def _forward_pane_added(self, pane_id):
        """Forward pane_added signal from model to public signal."""
        self.pane_added.emit(str(pane_id))

    def _forward_focus_changed(self, old_pane_id, new_pane_id):
        """Forward focus_changed signal from model to public signal."""
        old_id_str = str(old_pane_id) if old_pane_id else ""
        new_id_str = str(new_pane_id) if new_pane_id else ""
        self.focus_changed.emit(old_id_str, new_id_str)

    def _on_splitter_moved(self, node_id: str, ratios: list[float]):
        """Handle splitter movement."""
        from .controller.commands import SetRatiosCommand
        from .core.types import NodeId

        command = SetRatiosCommand(self._model, NodeId(node_id), ratios)
        self._controller.execute_command(command)

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

        self._model.root = leaf
        self._model._rebuild_registry()
        self._model.set_focused_pane(pane_id)

        # Emit signals to update view
        logger.debug("Emitting structure_changed signal for initial setup")
        self._model.signals.structure_changed.emit()
        self._model.signals.pane_added.emit(pane_id)

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
        success, validation = self._controller.split_pane(
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
        success, validation = self._controller.remove_pane(PaneId(pane_id))

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
        return self._model.set_focused_pane(PaneId(pane_id))

    def navigate_focus(self, direction: Direction) -> bool:
        """Navigate focus in a direction.

        Args:
            direction: Direction to navigate

        Returns:
            True if focus moved
        """
        target = self._focus_manager.navigate(direction)
        if target:
            return self._model.set_focused_pane(target)
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
            self._model, PaneId(pane_id), constraints
        )
        return self._controller.execute_command(command)

    def undo(self) -> bool:
        """Undo last operation."""
        return self._controller.undo()

    def redo(self) -> bool:
        """Redo last undone operation."""
        return self._controller.redo()

    def can_undo(self) -> bool:
        """Check if undo is available."""
        return self._controller.can_undo()

    def can_redo(self) -> bool:
        """Check if redo is available."""
        return self._controller.can_redo()

    def save_layout(self, filepath: Path) -> bool:
        """Save layout to file.

        Args:
            filepath: Path to save file

        Returns:
            True if successful
        """
        return self._session_manager.save_to_file(filepath)

    def load_layout(self, filepath: Path) -> bool:
        """Load layout from file.

        Args:
            filepath: Path to load file

        Returns:
            True if successful
        """
        return self._session_manager.load_from_file(filepath)

    def get_layout_json(self) -> str:
        """Get layout as JSON string."""
        return self._session_manager.save_to_string()

    def set_layout_json(self, json_str: str) -> bool:
        """Set layout from JSON string."""
        return self._session_manager.load_from_string(json_str)

    def get_pane_ids(self) -> list[str]:
        """Get all pane IDs."""
        return [str(pane_id) for pane_id in self._model.get_all_pane_ids()]

    def get_focused_pane(self) -> Optional[str]:
        """Get currently focused pane ID."""
        if self._model.focused_pane_id:
            return str(self._model.focused_pane_id)
        return None

    def set_widget_provider(self, provider: WidgetProvider):
        """Set widget provider.

        Args:
            provider: Widget provider to use
        """
        self._container.set_widget_provider(provider)

    def get_widget(self, pane_id: str) -> Optional[QWidget]:
        """Get the widget instance for a specific pane.

        Args:
            pane_id: ID of the pane

        Returns:
            The widget instance, or None if pane not found

        Example:
            >>> widget = multisplit.get_widget(pane_id)
            >>> if widget:
            ...     widget.setText("New content")
        """
        from .core.types import PaneId
        return self._container._widget_pool.get_widget(PaneId(pane_id))

    def get_all_widgets(self) -> dict[str, QWidget]:
        """Get all pane widgets as a dictionary.

        Returns:
            Dictionary mapping pane IDs to their widget instances

        Example:
            >>> for pane_id, widget in multisplit.get_all_widgets().items():
            ...     print(f"Pane {pane_id}: {widget}")
        """
        result = {}
        for pane_id in self._container._widget_pool.get_all_pane_ids():
            widget = self._container._widget_pool.get_widget(pane_id)
            if widget:
                result[str(pane_id)] = widget
        return result

    def find_pane_by_widget(self, widget: QWidget) -> Optional[str]:
        """Find which pane contains a specific widget.

        This searches for the widget either as a direct pane widget or
        as a child/descendant of a pane widget.

        Args:
            widget: The widget to search for

        Returns:
            The pane ID containing the widget, or None if not found

        Example:
            >>> text_edit = QTextEdit()
            >>> # ... add to pane somehow ...
            >>> pane_id = multisplit.find_pane_by_widget(text_edit)
            >>> if pane_id:
            ...     print(f"Widget is in pane {pane_id}")
        """

        # Check all panes
        for pane_id in self._container._widget_pool.get_all_pane_ids():
            pane_widget = self._container._widget_pool.get_widget(pane_id)
            if pane_widget:
                # Direct match
                if pane_widget == widget:
                    return str(pane_id)
                # Check if widget is a descendant
                if pane_widget.isAncestorOf(widget):
                    return str(pane_id)

        return None
