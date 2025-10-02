"""Container widget for MultiSplit.

Qt widget that renders the pane tree.
"""

from typing import Dict, Optional, Protocol

from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtWidgets import QSplitter, QVBoxLayout, QWidget

try:
    from vfwidgets_theme.widgets.base import ThemedWidget
    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False
    ThemedWidget = object

from ..core.logger import log_widget_creation, logger
from ..core.model import PaneModel
from ..core.nodes import LeafNode, PaneNode, SplitNode
from ..core.types import Direction, NodeId, PaneId, WidgetId
from ..view.tree_reconciler import ReconcilerOperations, TreeReconciler


if THEME_AVAILABLE:
    class StyledSplitter(ThemedWidget, QSplitter):
        """Splitter with hover states and theme-aware visuals."""

        # Theme configuration - maps theme tokens to splitter properties
        theme_config = {
            'handle_bg': 'widget.background',
            'handle_hover_bg': 'list.hoverBackground',
            'handle_border': 'widget.border',
        }

        def __init__(self, orientation, parent=None):
            """Initialize styled splitter."""
            super().__init__(orientation=orientation, parent=parent)
            self.setChildrenCollapsible(False)
            self.setHandleWidth(6)  # Wider for easier grabbing

            self._is_hovered = False
            self.on_theme_changed()  # Apply initial theme

        def createHandle(self):
            """Create custom handle with hover support."""
            handle = super().createHandle()
            handle.installEventFilter(self)
            return handle

        def on_theme_changed(self) -> None:
            """Called automatically when the theme changes."""
            self._update_style()

        def _update_style(self, hovered: bool = False):
            """Update splitter style based on theme and hover state."""
            bg = self.theme.handle_hover_bg if hovered else self.theme.handle_bg
            border = self.theme.handle_border if hovered else "transparent"

            self.setStyleSheet(f"""
                QSplitter::handle {{
                    background-color: {bg};
                    border: 1px solid {border};
                }}
                QSplitter::handle:horizontal {{
                    width: 6px;
                    margin: 2px 0px;
                }}
                QSplitter::handle:vertical {{
                    height: 6px;
                    margin: 0px 2px;
                }}
            """)

        def eventFilter(self, obj, event):
            """Handle hover events on splitter handles."""
            if event.type() == QEvent.Type.Enter:
                # Mouse entered handle
                self._is_hovered = True
                self._update_style(hovered=True)
                # Change cursor
                obj.setCursor(Qt.CursorShape.SplitHCursor if self.orientation() == Qt.Orientation.Horizontal
                            else Qt.CursorShape.SplitVCursor)

            elif event.type() == QEvent.Type.Leave:
                # Mouse left handle
                self._is_hovered = False
                self._update_style(hovered=False)
                obj.unsetCursor()

            return super().eventFilter(obj, event)

else:
    # Fallback when theme system is not available
    class StyledSplitter(QSplitter):
        """Splitter without theme support (theme system not installed)."""

        def __init__(self, orientation, parent=None):
            super().__init__(orientation, parent)
            raise ImportError(
                "vfwidgets-theme is required for StyledSplitter. "
                "Install with: pip install vfwidgets-theme"
            )


class WidgetProvider(Protocol):
    """Protocol for widget provider."""

    def provide_widget(self, widget_id: WidgetId, pane_id: PaneId) -> QWidget:
        """Provide widget for pane."""
        ...


class PaneContainer(QWidget, ReconcilerOperations):
    """Qt container widget managing pane display."""

    # Signals
    widget_needed = Signal(str, str)  # widget_id, pane_id
    pane_focused = Signal(str)  # pane_id
    splitter_moved = Signal(str, list)  # node_id, new_ratios

    def __init__(self, model: PaneModel,
                 provider: Optional[WidgetProvider] = None,
                 parent: Optional[QWidget] = None):
        """Initialize container."""
        super().__init__(parent)

        self.model = model
        self.provider = provider
        self.reconciler = TreeReconciler()

        # Widget tracking
        self._widgets: Dict[PaneId, QWidget] = {}
        self._splitters: Dict[str, QSplitter] = {}
        self._current_tree: Optional[PaneNode] = None
        self._focus_frames: Dict[PaneId, QWidget] = {}

        # Connect model signals
        logger.debug(f"Connecting to model signals: {self.model}")
        self.model.signals.structure_changed.connect(self._on_structure_changed)
        self.model.signals.focus_changed.connect(self._on_focus_changed)
        logger.debug("Model signals connected successfully")

        # Initial render
        self._update_view()

    def _on_structure_changed(self):
        """Handle model structure changes."""
        logger.info("=" * 60)
        logger.info("STRUCTURE CHANGED SIGNAL RECEIVED")
        logger.info(f"Current tree type: {type(self._current_tree).__name__ if self._current_tree else 'None'}")
        logger.info(f"New root type: {type(self.model.root).__name__ if self.model.root else 'None'}")
        logger.info("=" * 60)
        self._update_view()

    def _update_view(self):
        """Update view to match model."""
        logger.debug(f"_update_view: current_tree={type(self._current_tree).__name__ if self._current_tree else 'None'}, "
                    f"model.root={type(self.model.root).__name__ if self.model.root else 'None'}")

        # Get differences
        diff = self.reconciler.diff(self._current_tree, self.model.root)

        logger.debug(f"Reconciler diff: added={diff.added}, removed={diff.removed}, "
                    f"has_changes={diff.has_changes()}")

        # Log details if we have unexpected removals
        if diff.removed and self._current_tree and self.model.root:
            logger.warning(f"Unexpected removals detected: {diff.removed}")
            from ..core.logger import log_tree_structure
            log_tree_structure(self._current_tree, "Current tree (before update)")
            log_tree_structure(self.model.root, "New tree (model.root)")

        # IMPORTANT: Always rebuild layout when tree structure changes
        # The reconciler only tracks pane additions/removals, not structural changes
        # If the root type changed (e.g., Leaf -> Split), we must rebuild
        if self._current_tree is None or self.model.root is None:
            should_rebuild = True
        elif type(self._current_tree) != type(self.model.root):
            should_rebuild = True
            logger.info("Root node type changed - forcing rebuild")
        elif diff.has_changes():
            should_rebuild = True
        else:
            should_rebuild = False
            logger.debug("No changes detected, skipping update")

        if not should_rebuild:
            return

        # Apply changes
        for pane_id in diff.removed:
            logger.info(f"Removing pane from view: {pane_id}")
            self.remove_pane(pane_id)

        for pane_id in diff.added:
            logger.info(f"Adding pane to view: {pane_id}")
            self.add_pane(pane_id)

        # Rebuild layout
        logger.info("Rebuilding layout")
        self._rebuild_layout()

        # Update current tree - IMPORTANT: Store a deep copy to avoid reference issues
        # If we store a reference, future modifications to the model will affect our "old" tree
        self._current_tree = self.model.root.clone() if self.model.root else None

    def _rebuild_layout(self):
        """Rebuild widget layout from model."""
        if not self.model.root:
            # Clear everything
            for widget in self._widgets.values():
                widget.setParent(None)
            return

        # Build widget tree
        root_widget = self._build_widget_tree(self.model.root)

        # Set as main widget
        if self.layout():
            # Clear old layout
            old = self.layout().takeAt(0)
            if old and old.widget():
                old.widget().setParent(None)
        else:
            # Create layout
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            self.setLayout(layout)

        if root_widget:
            self.layout().addWidget(root_widget)

    def _build_widget_tree(self, node: PaneNode) -> Optional[QWidget]:
        """Build Qt widget tree from node tree."""
        if isinstance(node, LeafNode):
            # Check if we already have a frame container for this pane
            if node.pane_id in self._focus_frames:
                logger.debug(f"Reusing existing frame container for pane {node.pane_id}")
                frame = self._focus_frames[node.pane_id]

                # CRITICAL: Re-install comprehensive focus tracking when reusing frames
                # They may have been lost during previous rebuilds
                if not frame.property("event_filter_installed"):
                    logger.debug(f"Reinstalling comprehensive focus tracking for pane {node.pane_id}")

                    # Reinstall on frame
                    self._install_recursive_filters(frame, node.pane_id)

                    # Reinstall on child widget if it exists
                    if frame.layout() and frame.layout().count() > 0:
                        child_widget = frame.layout().itemAt(0).widget()
                        if child_widget:
                            self._install_recursive_filters(child_widget, node.pane_id)
                            self._handle_complex_widget(child_widget, node.pane_id)

                return frame

            # Get or create widget
            widget = None
            if node.pane_id in self._widgets:
                logger.debug(f"Reusing existing widget for pane {node.pane_id}")
                widget = self._widgets[node.pane_id]
            else:
                # Request widget from provider
                if self.provider:
                    logger.info(f"Requesting widget from provider: {node.widget_id} for pane {node.pane_id}")
                    widget = self.provider.provide_widget(
                        node.widget_id, node.pane_id
                    )
                    self._widgets[node.pane_id] = widget
                    log_widget_creation(node.widget_id, node.pane_id, type(widget))
                else:
                    # Emit signal for widget
                    logger.warning(f"No provider available, emitting widget_needed signal for {node.widget_id}")
                    self.widget_needed.emit(
                        str(node.widget_id), str(node.pane_id)
                    )
                    # Create placeholder
                    placeholder = QWidget()
                    placeholder.setStyleSheet("background-color: lightgray; border: 1px solid gray;")
                    self._widgets[node.pane_id] = placeholder
                    widget = placeholder
                    logger.debug(f"Created placeholder widget for pane {node.pane_id}")

            # Wrap in focus container (only if we don't have one already)
            return self._create_pane_container(node.pane_id, widget)

        elif isinstance(node, SplitNode):
            # Create styled splitter
            orientation = (Qt.Orientation.Horizontal
                         if node.orientation.value == "horizontal"
                         else Qt.Orientation.Vertical)

            splitter = StyledSplitter(orientation)  # Changed from QSplitter

            # Track splitter
            self._splitters[str(node.node_id)] = splitter

            # Add children
            for child in node.children:
                child_widget = self._build_widget_tree(child)
                if child_widget:
                    splitter.addWidget(child_widget)

            # Set sizes based on ratios
            if node.ratios and len(node.ratios) == splitter.count():
                total = sum(node.ratios)
                sizes = [int(1000 * r / total) for r in node.ratios]
                splitter.setSizes(sizes)

            # Connect splitter movement
            splitter.splitterMoved.connect(
                lambda pos, index: self._on_splitter_moved(node.node_id, splitter)
            )

            return splitter

        return None

    def _on_focus_changed(self, old_id: Optional[PaneId], new_id: Optional[PaneId]):
        """Handle focus changes."""
        # Clear old focus indicator
        if old_id and old_id in self._focus_frames:
            self._focus_frames[old_id].setStyleSheet("")

        # Set new focus indicator
        if new_id and new_id in self._focus_frames:
            self._focus_frames[new_id].setStyleSheet("""
                QFrame {
                    border: 2px solid #0078d4;
                    border-radius: 3px;
                }
            """)

            # Ensure widget has Qt focus
            if new_id in self._widgets:
                self._widgets[new_id].setFocus()

    def _create_pane_container(self, pane_id: PaneId, widget: QWidget) -> QWidget:
        """Create container with comprehensive focus tracking for pane widget."""
        from PySide6.QtWidgets import QFrame, QVBoxLayout

        # Create frame for focus indicator
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box)
        frame.setStyleSheet("")  # Start with no border

        # Layout to hold widget
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(widget)

        # Track frame for focus updates
        self._focus_frames[pane_id] = frame

        # COMPREHENSIVE FOCUS TRACKING SETUP

        # 1. Install recursive filters on frame and all children
        self._install_recursive_filters(frame, pane_id)
        self._install_recursive_filters(widget, pane_id)

        # 2. Handle complex widgets with special requirements
        self._handle_complex_widget(widget, pane_id)

        # 3. Monitor for dynamic children (optional for performance)
        widget_type = widget.__class__.__name__
        if any(complex_type in widget_type for complex_type in ["WebView", "WebEngine", "TabWidget"]):
            # Only monitor highly dynamic widgets
            self._monitor_widget_children(widget, pane_id)
            logger.info(f"Dynamic monitoring enabled for {widget_type} in pane {pane_id}")

        logger.debug(f"Created pane container with comprehensive focus tracking: {pane_id}")
        return frame

    def _on_pane_clicked(self, pane_id: PaneId, event):
        """Handle pane click for focus."""
        from PySide6.QtCore import Qt

        if event.button() == Qt.MouseButton.LeftButton:
            logger.debug(f"Pane clicked: {pane_id}")
            # Request focus through controller
            self.pane_focused.emit(str(pane_id))

    def eventFilter(self, obj, event):
        """Enhanced event filter for comprehensive focus tracking."""
        from PySide6.QtCore import QEvent, Qt

        # PRIMARY: Handle Qt focus events
        if event.type() == QEvent.Type.FocusIn:
            # Widget gained focus - find its pane
            pane_id = self._find_widget_pane(obj)
            if pane_id:
                logger.info(f"FocusIn event: widget {obj.__class__.__name__} in pane {pane_id} gained focus")
                self.pane_focused.emit(pane_id)
                return False

        # FALLBACK: Handle mouse clicks for widgets that don't participate in focus chain
        elif event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                # Get pane_id from the widget's property
                pane_id_str = obj.property("pane_id")
                if not pane_id_str:
                    # Try to find pane by traversing parents
                    pane_id_str = self._find_widget_pane(obj)

                if pane_id_str:
                    logger.info(f"Mouse click detected on {obj.__class__.__name__} in pane: {pane_id_str}")
                    self.pane_focused.emit(pane_id_str)
                    # Don't consume the event - let it propagate
                    return False

        # Let the event propagate normally
        return False

    def _find_widget_pane(self, widget: QWidget) -> Optional[str]:
        """Find which pane a widget belongs to by traversing parents."""
        current = widget
        max_depth = 20

        while current and max_depth > 0:
            # Check if widget has pane_id property
            pane_id = current.property("pane_id")
            if pane_id:
                return pane_id

            # Check if widget is in our tracking dict
            for pid, w in self._widgets.items():
                if w == current:
                    return str(pid)

            # Check frame containers
            for pid, frame in self._focus_frames.items():
                if frame == current or frame.isAncestorOf(current):
                    return str(pid)

            current = current.parent()
            max_depth -= 1

        return None

    def _install_recursive_filters(self, widget: QWidget, pane_id: PaneId, depth: int = 0):
        """Recursively install event filters on widget and all descendants."""
        if depth > 10:  # Prevent infinite recursion
            logger.warning(f"Max recursion depth reached for widget {widget.__class__.__name__}")
            return

        # Install filter on this widget
        if not widget.property("event_filter_installed"):
            widget.installEventFilter(self)
            widget.setProperty("event_filter_installed", True)
            widget.setProperty("pane_id", str(pane_id))

            logger.debug(f"Installed filter on {widget.__class__.__name__} at depth {depth} for pane {pane_id}")

        # Install on all children
        for child in widget.findChildren(QWidget):
            if child.parent() == widget:  # Direct children only
                self._install_recursive_filters(child, pane_id, depth + 1)

    def _handle_complex_widget(self, widget: QWidget, pane_id: PaneId):
        """Special handling for complex widget types."""
        widget_type = widget.__class__.__name__

        if "WebView" in widget_type or "WebEngine" in widget_type:
            # Web views need special handling
            logger.info(f"Installing web view focus handler for pane {pane_id}")
            # Web views often have a focusProxy
            focus_proxy = widget.focusProxy()
            if focus_proxy:
                self._install_recursive_filters(focus_proxy, pane_id)

        elif "Editor" in widget_type or "TextEdit" in widget_type or "PlainTextEdit" in widget_type:
            # Text editors may have viewport widgets
            logger.debug(f"Installing text editor focus handler for pane {pane_id}")
            if hasattr(widget, 'viewport'):
                viewport = widget.viewport()
                if viewport:
                    self._install_recursive_filters(viewport, pane_id)

            # Also handle document
            if hasattr(widget, 'document'):
                document = widget.document()
                if document and hasattr(document, 'contentsChanged'):
                    # Connect to document changes to update focus when typing
                    document.contentsChanged.connect(
                        lambda: self.pane_focused.emit(str(pane_id))
                    )

        elif "TabWidget" in widget_type:
            # Tab widgets need monitoring for tab changes
            logger.debug(f"Installing tab widget focus handler for pane {pane_id}")
            if hasattr(widget, 'currentChanged'):
                widget.currentChanged.connect(
                    lambda: self.pane_focused.emit(str(pane_id))
                )
            # Also handle individual tab widgets
            if hasattr(widget, 'count'):
                for i in range(widget.count()):
                    tab_widget = widget.widget(i)
                    if tab_widget:
                        self._install_recursive_filters(tab_widget, pane_id)

        # Handle any widget with focus policies
        if widget.focusPolicy() != Qt.FocusPolicy.NoFocus:
            logger.debug(f"Widget {widget_type} can accept focus, ensuring filter is installed")
            # Make sure the widget itself has focus handling
            if not widget.property("event_filter_installed"):
                widget.installEventFilter(self)
                widget.setProperty("event_filter_installed", True)
                widget.setProperty("pane_id", str(pane_id))

    def _monitor_widget_children(self, widget: QWidget, pane_id: PaneId):
        """Monitor widget for dynamically added children."""
        from PySide6.QtCore import QTimer

        def check_new_children():
            # Find children without filters
            for child in widget.findChildren(QWidget):
                if not child.property("event_filter_installed"):
                    logger.debug(f"Found new child widget: {child.__class__.__name__} in pane {pane_id}")
                    self._install_recursive_filters(child, pane_id, 0)

        # Check periodically for new children (for highly dynamic widgets)
        timer = QTimer()
        timer.timeout.connect(check_new_children)
        timer.start(2000)  # Check every 2 seconds

        # Store timer to prevent garbage collection
        widget.setProperty("child_monitor_timer", timer)

        logger.debug(f"Started child monitoring for {widget.__class__.__name__} in pane {pane_id}")

    def _on_splitter_moved(self, node_id: NodeId, splitter: QSplitter):
        """Handle splitter drag."""
        # Calculate new ratios from sizes
        sizes = splitter.sizes()
        total = sum(sizes)

        if total > 0:
            ratios = [s / total for s in sizes]

            # Emit signal for ratio change
            self.splitter_moved.emit(str(node_id), ratios)

    def keyPressEvent(self, event):
        """Handle keyboard events for navigation."""
        from PySide6.QtCore import Qt

        # Tab navigation
        if event.key() == Qt.Key.Key_Tab:
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                self._navigate_focus_previous()
            else:
                self._navigate_focus_next()
            event.accept()
            return

        # Arrow key navigation
        direction_map = {
            Qt.Key.Key_Left: Direction.LEFT,
            Qt.Key.Key_Right: Direction.RIGHT,
            Qt.Key.Key_Up: Direction.UP,
            Qt.Key.Key_Down: Direction.DOWN
        }

        if event.key() in direction_map:
            # Only navigate if Alt is held (Alt+Arrow)
            if event.modifiers() & Qt.KeyboardModifier.AltModifier:
                self._navigate_focus_direction(direction_map[event.key()])
                event.accept()
                return

        # Pass to parent
        super().keyPressEvent(event)

    def _navigate_focus_next(self):
        """Navigate to next pane."""
        from ..core.focus import FocusManager

        focus_mgr = FocusManager(self.model)
        next_pane = focus_mgr.get_next_pane(self.model.focused_pane_id)

        if next_pane:
            self.model.set_focused_pane(next_pane)

    def _navigate_focus_previous(self):
        """Navigate to previous pane."""
        from ..core.focus import FocusManager

        focus_mgr = FocusManager(self.model)
        prev_pane = focus_mgr.get_previous_pane(self.model.focused_pane_id)

        if prev_pane:
            self.model.set_focused_pane(prev_pane)

    def _navigate_focus_direction(self, direction: Direction):
        """Navigate focus in a direction."""
        from ..core.focus import FocusManager

        focus_mgr = FocusManager(self.model)
        target_pane = focus_mgr.navigate(direction)

        if target_pane:
            self.model.set_focused_pane(target_pane)

    # ReconcilerOperations implementation

    def add_pane(self, pane_id: PaneId):
        """Add new pane (widget will be created during rebuild)."""
        # Widget creation happens in _build_widget_tree
        pass

    def remove_pane(self, pane_id: PaneId):
        """Remove pane widget and clean up all associated resources."""
        if pane_id in self._widgets:
            widget = self._widgets[pane_id]

            # Clean up child monitoring timer if it exists
            timer = widget.property("child_monitor_timer")
            if timer:
                logger.debug(f"Stopping child monitor timer for pane {pane_id}")
                timer.stop()
                timer.deleteLater()
                widget.setProperty("child_monitor_timer", None)

            # Clean up the widget
            widget.setParent(None)
            widget.deleteLater()
            del self._widgets[pane_id]

        # Clean up focus frame and any associated timers
        if pane_id in self._focus_frames:
            frame = self._focus_frames[pane_id]

            # Check for any child monitor timers in the frame's children
            for child in frame.findChildren(QWidget):
                child_timer = child.property("child_monitor_timer")
                if child_timer:
                    logger.debug(f"Stopping child timer for widget {child.__class__.__name__} in pane {pane_id}")
                    child_timer.stop()
                    child_timer.deleteLater()

            del self._focus_frames[pane_id]
            logger.debug(f"Cleaned up all resources for pane {pane_id}")

    def set_widget_provider(self, provider: WidgetProvider):
        """Set widget provider."""
        self.provider = provider
        self._update_view()

    def provide_widget_for_pane(self, pane_id: PaneId, widget: QWidget):
        """Manually provide a widget for a pane."""
        self._widgets[pane_id] = widget
        self._update_view()
