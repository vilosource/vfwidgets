"""Container widget for MultiSplit.

Qt widget that renders the pane tree.
"""

from typing import Optional, Protocol

from PySide6.QtCore import QEvent, QRect, Qt, Signal
from PySide6.QtWidgets import QSplitter, QWidget

try:
    from vfwidgets_theme.widgets.base import ThemedWidget
    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False
    ThemedWidget = object

from ..core.logger import log_widget_creation, logger
from ..core.model import PaneModel
from ..core.nodes import LeafNode, PaneNode
from ..core.types import Direction, Orientation, PaneId, SplitterStyle, WidgetId
from ..view.geometry_manager import GeometryManager
from ..view.tree_reconciler import ReconcilerOperations, TreeReconciler
from ..view.visual_renderer import VisualRenderer
from ..view.widget_pool import WidgetPool

if THEME_AVAILABLE:
    class StyledSplitter(ThemedWidget, QSplitter):
        """Splitter with hover states and theme-aware visuals."""

        # Theme configuration - maps theme tokens to splitter properties
        theme_config = {
            'handle_bg': 'widget.background',
            'handle_hover_bg': 'list.hoverBackground',
            'handle_border': 'widget.border',
        }

        def __init__(self, orientation, parent=None, style: Optional[SplitterStyle] = None):
            """Initialize styled splitter.

            Args:
                orientation: Qt.Orientation (Horizontal or Vertical)
                parent: Parent widget
                style: SplitterStyle configuration (None = use comfortable defaults)
            """
            super().__init__(orientation=orientation, parent=parent)
            self.setChildrenCollapsible(False)

            # Use style parameters or comfortable defaults
            if style is None:
                style = SplitterStyle.comfortable()
            self.style = style
            self.setHandleWidth(style.handle_width)

            # Prevent white flash when splitter is created before children are added
            from PySide6.QtCore import Qt
            self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)

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
            # Use custom colors from style if provided, otherwise use theme tokens
            if hovered:
                bg = self.style.handle_hover_bg or self.theme.handle_hover_bg
                border = self.style.handle_hover_border or self.theme.handle_border
            else:
                bg = self.style.handle_bg or self.theme.handle_bg
                border = self.style.handle_border or "transparent"

            # Use style dimensions
            handle_width = self.style.handle_width
            margin_h = self.style.handle_margin_horizontal
            margin_v = self.style.handle_margin_vertical
            border_width = self.style.border_width
            border_radius = self.style.border_radius

            self.setStyleSheet(f"""
                QSplitter::handle {{
                    background-color: {bg};
                    border: {border_width}px solid {border};
                    border-radius: {border_radius}px;
                }}
                QSplitter::handle:horizontal {{
                    width: {handle_width}px;
                    margin: {margin_h}px 0px;
                }}
                QSplitter::handle:vertical {{
                    height: {handle_width}px;
                    margin: 0px {margin_v}px;
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

    def widget_closing(self, widget_id: WidgetId, pane_id: PaneId, widget: QWidget) -> None:
        """
        Called BEFORE a widget is removed from a pane.

        This lifecycle hook allows providers to clean up resources, save state,
        or perform any necessary teardown before the widget is destroyed.

        Args:
            widget_id: The widget ID that was used to create the widget
            pane_id: The pane ID that contained the widget
            widget: The widget instance being removed

        Note:
            This is an optional hook. If not implemented, no action is taken.
        """
        ...


class PaneContainer(QWidget, ReconcilerOperations):
    """Qt container widget managing pane display."""

    # Signals
    widget_needed = Signal(str, str)  # widget_id, pane_id
    pane_focused = Signal(str)  # pane_id
    splitter_moved = Signal(str, list)  # node_id, new_ratios

    def __init__(self, model: PaneModel,
                 provider: Optional[WidgetProvider] = None,
                 parent: Optional[QWidget] = None,
                 splitter_style: Optional['SplitterStyle'] = None):
        """Initialize container."""
        super().__init__(parent)

        self.model = model
        self.provider = provider
        self.splitter_style = splitter_style  # Store for splitter creation
        self.reconciler = TreeReconciler()

        self._current_tree: Optional[PaneNode] = None  # Needed for reconciliation

        # Fixed Container Architecture (Layer 1-3)
        self._widget_pool = WidgetPool(self)  # Layer 1: Fixed container
        # Layer 2: Pure calculation - pass handle_width from splitter_style
        handle_width = splitter_style.handle_width if splitter_style else 6
        self._geometry_manager = GeometryManager(handle_width=handle_width)
        self._visual_renderer = VisualRenderer(self._widget_pool)  # Layer 3: Geometry application

        # Divider management (for drag-to-resize)
        self._dividers: dict[str, list[QWidget]] = {}  # node_id -> list of DividerWidget instances

        # Prevent white flash during layout rebuilds using Qt widget attributes
        # WA_NoSystemBackground: Prevent Qt from erasing widget background (prevents white flash)
        # This is the proper Qt way to prevent flashing when widgets aren't ready to paint yet
        from PySide6.QtCore import Qt
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)

        # Enable mouse tracking to receive mouse move events for divider drag
        self.setMouseTracking(True)

        # Connect model signals
        logger.debug(f"Connecting to model signals: {self.model}")
        self.model.signals.structure_changed.connect(self._on_structure_changed)
        self.model.signals.focus_changed.connect(self._on_focus_changed)
        logger.debug("Model signals connected successfully")

        # Initial render
        self._update_view()

    def _on_structure_changed(self):
        """Handle model structure changes."""
        logger.debug("Structure changed - updating view")
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
        elif not isinstance(self._current_tree, type(self.model.root)):
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
        """
        Rebuild widget layout from model using Fixed Container Architecture.

        NEW APPROACH (Geometry-Based):
            - No widget tree building
            - No splitter hierarchy
            - No reparenting (except when first adding widgets to pool)
            - Pure geometry calculations + setGeometry() updates

        This eliminates white flashes by avoiding reparenting of QWebEngineView widgets.
        """
        logger.info("Rebuilding layout using geometry-based architecture")

        if not self.model.root:
            # No panes - hide all widgets
            self._visual_renderer.hide_all()
            return

        # Calculate geometries from tree
        viewport = self.rect()
        geometries = self._geometry_manager.calculate_layout(self.model.root, viewport)

        logger.debug(f"Calculated geometries for {len(geometries)} panes")
        for pane_id, geometry in geometries.items():
            logger.debug(f"  {pane_id}: {geometry}")

        # Apply geometries (NO REPARENTING - only setGeometry() calls)
        self._visual_renderer.render(geometries)

        # Calculate and render dividers
        divider_geometries = self._geometry_manager.calculate_dividers(self.model.root, viewport)
        self._update_dividers(divider_geometries)

    def _update_dividers(self, divider_geometries: dict[str, list['QRect']]):
        """Create/update/remove divider widgets to match tree structure.

        Args:
            divider_geometries: Dict mapping node_id -> list of divider rectangles
        """
        from ..core.nodes import SplitNode
        from ..core.tree_utils import find_split_by_id
        from .divider_widget import DividerWidget

        # Remove dividers for nodes that no longer exist
        nodes_to_remove = []
        for node_id in list(self._dividers.keys()):
            if node_id not in divider_geometries:
                # Remove all dividers for this node
                for divider in self._dividers[node_id]:
                    divider.hide()
                    divider.deleteLater()
                nodes_to_remove.append(node_id)

        for node_id in nodes_to_remove:
            del self._dividers[node_id]

        # Create/update dividers for each SplitNode
        for node_id, rects in divider_geometries.items():
            # Find the SplitNode to get its orientation
            split_node = find_split_by_id(self.model.root, node_id)
            if not split_node or not isinstance(split_node, SplitNode):
                continue

            # Ensure we have the right number of dividers
            if node_id not in self._dividers:
                self._dividers[node_id] = []

            current_dividers = self._dividers[node_id]

            # Remove excess dividers if we have too many
            while len(current_dividers) > len(rects):
                divider = current_dividers.pop()
                divider.hide()
                divider.deleteLater()

            # Create new dividers if we need more
            while len(current_dividers) < len(rects):
                divider_index = len(current_dividers)
                divider = DividerWidget(
                    node_id=node_id,
                    divider_index=divider_index,
                    orientation=split_node.orientation,
                    style=self.splitter_style,
                    parent=self
                )
                # Connect signals
                divider.resize_requested.connect(self._on_divider_resize)  # LIVE preview
                divider.resize_committed.connect(self._on_divider_commit)  # Final model update
                current_dividers.append(divider)

            # Update geometries for all dividers
            for i, rect in enumerate(rects):
                if i < len(current_dividers):
                    # Expand rect to include hit area padding for easier grabbing
                    expanded_rect = self._expand_divider_rect(rect, split_node.orientation)
                    current_dividers[i].setGeometry(expanded_rect)
                    current_dividers[i].show()
                    current_dividers[i].raise_()  # Ensure dividers are on top

        # Force IMMEDIATE repaint of container (repaint() is synchronous, update() is async)
        self.repaint()

    def _expand_divider_rect(self, rect: QRect, orientation: Orientation) -> QRect:
        """Expand divider rectangle to include hit area padding.

        Args:
            rect: Base divider rectangle (just the visible handle width)
            orientation: Split orientation (determines which dimension to expand)

        Returns:
            Expanded rectangle with hit area padding for easier mouse interaction
        """
        if not self.splitter_style or self.splitter_style.hit_area_padding == 0:
            return rect  # No expansion needed

        padding = self.splitter_style.hit_area_padding

        if orientation == Orientation.HORIZONTAL:
            # Horizontal split = vertical divider = expand width (left/right)
            return QRect(
                rect.x() - padding,
                rect.y(),
                rect.width() + (2 * padding),
                rect.height()
            )
        else:  # VERTICAL
            # Vertical split = horizontal divider = expand height (top/bottom)
            return QRect(
                rect.x(),
                rect.y() - padding,
                rect.width(),
                rect.height() + (2 * padding)
            )

    def _on_divider_resize(self, node_id: str, divider_index: int, delta_pixels: int):
        """Handle divider drag - DIRECT geometry update for live feedback.

        This method provides IMMEDIATE visual feedback during drag by directly
        updating widget geometries WITHOUT going through the model/command pattern.

        The model is only updated when the drag completes (in divider mouseReleaseEvent).

        Args:
            node_id: ID of the SplitNode being resized
            divider_index: Which divider was moved (0 = first gap, etc.)
            delta_pixels: How many pixels the divider moved from drag start
        """
        from ..core.nodes import SplitNode
        from ..core.tree_utils import find_split_by_id
        from ..core.types import Orientation

        # Find the SplitNode
        split_node = find_split_by_id(self.model.root, node_id)
        if not split_node or not isinstance(split_node, SplitNode):
            logger.warning(f"Cannot resize: SplitNode {node_id} not found")
            return

        # Calculate total size (width for horizontal, height for vertical)
        viewport = self.rect()
        if split_node.orientation == Orientation.HORIZONTAL:
            total_size = viewport.width()
        else:
            total_size = viewport.height()

        # Calculate new ratios for PREVIEW
        new_ratios = self._calculate_new_ratios(
            split_node.ratios,
            divider_index,
            delta_pixels,
            total_size
        )

        # CRITICAL: Create a TEMPORARY modified tree for preview calculation
        # We temporarily modify the ratios in the node for geometry calculation ONLY
        # The actual model is NOT changed until drag completes
        old_ratios = split_node.ratios
        split_node.ratios = new_ratios

        # Recalculate geometries with preview ratios
        geometries = self._geometry_manager.calculate_layout(self.model.root, viewport)
        divider_geometries = self._geometry_manager.calculate_dividers(self.model.root, viewport)

        # Restore original ratios (preview only - don't modify model)
        split_node.ratios = old_ratios

        # Apply preview geometries DIRECTLY (no model update, no structure_changed signal)
        self._visual_renderer.render(geometries)
        self._update_dividers(divider_geometries)

    def _on_divider_commit(self, node_id: str, divider_index: int, delta_pixels: int):
        """Handle divider drag completion - update model via command pattern.

        This is called when the drag completes (mouseRelease). It updates the model
        which triggers structure_changed and a full layout rebuild.

        Args:
            node_id: ID of the SplitNode being resized
            divider_index: Which divider was moved
            delta_pixels: Final delta from drag start
        """
        from ..core.nodes import SplitNode
        from ..core.tree_utils import find_split_by_id
        from ..core.types import Orientation

        # Find the SplitNode
        split_node = find_split_by_id(self.model.root, node_id)
        if not split_node or not isinstance(split_node, SplitNode):
            logger.warning(f"Cannot commit resize: SplitNode {node_id} not found")
            return

        # Calculate total size
        viewport = self.rect()
        if split_node.orientation == Orientation.HORIZONTAL:
            total_size = viewport.width()
        else:
            total_size = viewport.height()

        # Calculate final ratios
        new_ratios = self._calculate_new_ratios(
            split_node.ratios,
            divider_index,
            delta_pixels,
            total_size
        )

        # Emit signal to trigger SetRatiosCommand (updates model, triggers structure_changed)
        logger.debug(f"Committing resize: node={node_id}, ratios={new_ratios}")
        self.splitter_moved.emit(node_id, new_ratios)

    def _calculate_new_ratios(
        self,
        old_ratios: list[float],
        divider_index: int,
        delta_pixels: int,
        total_size: int
    ) -> list[float]:
        """Convert pixel delta to new ratio distribution.

        Args:
            old_ratios: Current ratio distribution
            divider_index: Index of divider that moved (between child[i] and child[i+1])
            delta_pixels: How many pixels the divider moved (positive = right/down)
            total_size: Total available size in pixels

        Returns:
            New ratio distribution (normalized to sum to 1.0)
        """
        # Convert ratios to pixel sizes
        sizes = [ratio * total_size for ratio in old_ratios]

        # Account for handle widths (N-1 handles for N children)
        num_handles = len(sizes) - 1
        available_size = total_size - (num_handles * self._geometry_manager.HANDLE_WIDTH)
        sizes = [ratio * available_size for ratio in old_ratios]

        # Apply delta to adjacent panes
        # Divider between child[divider_index] and child[divider_index + 1]
        sizes[divider_index] += delta_pixels
        sizes[divider_index + 1] -= delta_pixels

        # Clamp to minimum sizes (e.g., 50px)
        MIN_SIZE = 50
        sizes = [max(MIN_SIZE, s) for s in sizes]

        # Convert back to ratios
        new_total = sum(sizes)
        if new_total > 0:
            new_ratios = [s / new_total for s in sizes]
        else:
            # Fallback to equal distribution
            new_ratios = [1.0 / len(sizes)] * len(sizes)

        return new_ratios

    def _on_focus_changed(self, old_id: Optional[PaneId], new_id: Optional[PaneId]):
        """Handle focus changes."""
        # Use visual renderer to manage focus
        self._visual_renderer.set_focused_pane(new_id)

        # Ensure widget has Qt focus
        if new_id:
            widget = self._widget_pool.get_widget(new_id)
            if widget:
                widget.setFocus()

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

                    # CRITICAL: Find the actual focusable widget and give it focus
                    # The pane widget is often just a container - we need to focus the child
                    pane_widget = self._widget_pool.get_widget(pane_id_str)
                    if pane_widget:
                        # If the clicked widget itself can take focus, use it
                        if obj.focusPolicy() != Qt.FocusPolicy.NoFocus:
                            obj.setFocus(Qt.FocusReason.MouseFocusReason)
                        # Otherwise try to find a focusable child in the pane
                        else:
                            focusable = self._find_focusable_widget(pane_widget)
                            if focusable:
                                focusable.setFocus(Qt.FocusReason.MouseFocusReason)

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

            # Check widget pool
            for pool_pane_id in self._widget_pool.get_all_pane_ids():
                pool_widget = self._widget_pool.get_widget(pool_pane_id)
                if pool_widget == current or (pool_widget and pool_widget.isAncestorOf(current)):
                    return str(pool_pane_id)

            current = current.parent()
            max_depth -= 1

        return None

    def _find_focusable_widget(self, widget: QWidget) -> Optional[QWidget]:
        """Find the first focusable child widget in the pane.

        This is needed because pane widgets are often just containers,
        and the actual focusable widget (like QTextEdit, terminal, etc.)
        is a child of the pane widget.
        """
        # Check if the widget itself can take focus
        if widget.focusPolicy() not in (Qt.FocusPolicy.NoFocus, Qt.FocusPolicy.TabFocus):
            return widget

        # Search children for a focusable widget
        for child in widget.findChildren(QWidget):
            if child.focusPolicy() not in (Qt.FocusPolicy.NoFocus, Qt.FocusPolicy.TabFocus):
                return child

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
        """
        Add new pane to the widget pool.

        Creates widget and adds to pool immediately.
        Widget stays in pool for its entire lifetime.
        """
        # Check if already in pool
        if self._widget_pool.has_widget(pane_id):
            logger.debug(f"Pane {pane_id} already in pool, skipping")
            return

        # Get the leaf node from model to find widget_id
        pane_node = self.model.get_pane(pane_id)
        if not pane_node or not isinstance(pane_node, LeafNode):
            logger.warning(f"Cannot add pane {pane_id}: not found in model or not a leaf")
            return

        # Create widget via provider
        widget = None
        if self.provider:
            logger.info(f"Requesting widget from provider: {pane_node.widget_id} for pane {pane_id}")
            widget = self.provider.provide_widget(pane_node.widget_id, pane_id)
            log_widget_creation(pane_node.widget_id, pane_id, type(widget))
        else:
            # Emit signal or create placeholder
            logger.warning(f"No provider available, emitting widget_needed signal for {pane_node.widget_id}")
            self.widget_needed.emit(str(pane_node.widget_id), str(pane_id))
            # Create placeholder
            placeholder = QWidget()
            placeholder.setStyleSheet("background-color: lightgray; border: 1px solid gray;")
            widget = placeholder
            logger.debug(f"Created placeholder widget for pane {pane_id}")

        # Add to pool (ONLY reparenting point)
        self._widget_pool.add_widget(pane_id, widget)
        logger.info(f"Added widget for pane {pane_id} to pool")

        # Install event filters for focus tracking
        self._install_recursive_filters(widget, pane_id)
        self._handle_complex_widget(widget, pane_id)

    def remove_pane(self, pane_id: PaneId):
        """Remove pane widget from pool and clean up resources."""
        # Get pane info before removal
        pane_node = self.model.get_pane(pane_id)
        widget_id = pane_node.widget_id if (pane_node and isinstance(pane_node, LeafNode)) else None

        # Remove from pool
        if self._widget_pool.has_widget(pane_id):
            widget = self._widget_pool.get_widget(pane_id)

            # Call lifecycle hook BEFORE removing widget
            if widget and widget_id and self.provider and hasattr(self.provider, 'widget_closing'):
                try:
                    logger.debug(f"Calling widget_closing() for {widget_id} in pane {pane_id}")
                    self.provider.widget_closing(widget_id, pane_id, widget)
                except Exception as e:
                    logger.warning(f"Error in widget_closing() hook: {e}")

            # Clean up child monitoring timer if it exists
            if widget:
                timer = widget.property("child_monitor_timer")
                if timer:
                    logger.debug(f"Stopping child monitor timer for pane {pane_id}")
                    timer.stop()
                    timer.deleteLater()
                    widget.setProperty("child_monitor_timer", None)

            self._widget_pool.remove_widget(pane_id)
            logger.info(f"Removed pane {pane_id} from pool")

        logger.debug(f"Cleaned up all resources for pane {pane_id}")

    def set_widget_provider(self, provider: WidgetProvider):
        """Set widget provider."""
        self.provider = provider
        self._update_view()

    def provide_widget_for_pane(self, pane_id: PaneId, widget: QWidget):
        """Manually provide a widget for a pane."""
        self._widget_pool.add_widget(pane_id, widget)
        self._update_view()

    def resizeEvent(self, event):
        """
        Handle window resize using geometry recalculation.

        Recalculates geometries and applies them - no widget reparenting needed.
        """
        super().resizeEvent(event)

        if not self.model.root:
            return

        # Recalculate geometries for new viewport size
        viewport = self.rect()
        geometries = self._geometry_manager.calculate_layout(self.model.root, viewport)

        # Apply new geometries (NO REPARENTING)
        self._visual_renderer.render(geometries)

        # CRITICAL: Update divider positions after window resize
        # Without this, dividers stay at old positions and become ungrabbable
        divider_geometries = self._geometry_manager.calculate_dividers(self.model.root, viewport)
        self._update_dividers(divider_geometries)


__all__ = ["WidgetProvider", "PaneContainer"]
