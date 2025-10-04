# View Design

## Overview

The MultiSplit view layer provides efficient reconciliation between the model tree and Qt widget layout, sophisticated rendering pipeline, and optimized performance for large pane hierarchies. It maintains strict separation from model mutations while delivering responsive user experience through smart update strategies.

## What This Covers

- **Reconciliation Algorithm**: Efficient tree-to-layout synchronization
- **Render Pipeline**: Composable rendering with performance optimization
- **Widget Lifecycle**: Provider-based widget management
- **Event Handling**: Input processing and focus coordination
- **Performance Optimization**: Update batching and smart invalidation
- **Visual Effects**: Animations, transitions, and feedback systems

## What This Doesn't Cover

- Model data structures (see [Model Design](model-design.md))
- Command execution (see [Controller Design](controller-design.md))
- Focus algorithms (see [Focus Management](focus-management.md))
- Widget provider implementation (application responsibility)

---

## Reconciliation Algorithm

### Tree Differ Engine

```python
class TreeDiffer:
    """Calculates minimal changes between tree states"""

    def __init__(self):
        self.node_cache: dict[NodeId, NodeSnapshot] = {}
        self.pane_cache: dict[PaneId, PaneSnapshot] = {}

    def diff_trees(self, old_root: Optional[PaneNode],
                   new_root: Optional[PaneNode]) -> DiffResult:
        """Calculate tree differences for reconciliation"""

        if old_root is None and new_root is None:
            return DiffResult.empty()

        if old_root is None:
            return DiffResult.full_addition(new_root)

        if new_root is None:
            return DiffResult.full_removal(old_root)

        # Collect node information from both trees
        old_nodes = self._collect_node_info(old_root)
        new_nodes = self._collect_node_info(new_root)

        # Calculate changes
        diff = DiffResult()

        # Find removed nodes
        diff.removed_nodes = set(old_nodes.keys()) - set(new_nodes.keys())

        # Find added nodes
        diff.added_nodes = set(new_nodes.keys()) - set(old_nodes.keys())

        # Find modified nodes
        for node_id in set(old_nodes.keys()) & set(new_nodes.keys()):
            old_info = old_nodes[node_id]
            new_info = new_nodes[node_id]

            if self._node_changed(old_info, new_info):
                diff.modified_nodes.add(node_id)

        # Calculate pane changes
        old_panes = self._extract_pane_info(old_nodes)
        new_panes = self._extract_pane_info(new_nodes)

        diff.removed_panes = set(old_panes.keys()) - set(new_panes.keys())
        diff.added_panes = set(new_panes.keys()) - set(old_panes.keys())

        # Find panes that moved to different positions
        for pane_id in set(old_panes.keys()) & set(new_panes.keys()):
            old_path = old_panes[pane_id].path
            new_path = new_panes[pane_id].path

            if old_path != new_path:
                diff.moved_panes.add(pane_id)

        return diff

    def _collect_node_info(self, root: PaneNode) -> dict[NodeId, NodeInfo]:
        """Collect information about all nodes in tree"""
        collector = NodeInfoCollector()
        root.accept(collector)
        return collector.node_info

    def _node_changed(self, old: NodeInfo, new: NodeInfo) -> bool:
        """Check if node properties changed"""
        if old.node_type != new.node_type:
            return True

        if old.node_type == 'split':
            return (old.orientation != new.orientation or
                    old.ratios != new.ratios or
                    old.children_ids != new.children_ids)
        elif old.node_type == 'leaf':
            return (old.widget_id != new.widget_id or
                    old.constraints != new.constraints)

        return False

class DiffResult:
    """Results of tree comparison"""

    def __init__(self):
        self.removed_nodes: set[NodeId] = set()
        self.added_nodes: set[NodeId] = set()
        self.modified_nodes: set[NodeId] = set()

        self.removed_panes: set[PaneId] = set()
        self.added_panes: set[PaneId] = set()
        self.moved_panes: set[PaneId] = set()

        self.geometry_changed = False
        self.structure_changed = False

    @property
    def has_changes(self) -> bool:
        """Check if any changes exist"""
        return (bool(self.removed_nodes) or bool(self.added_nodes) or
                bool(self.modified_nodes) or bool(self.removed_panes) or
                bool(self.added_panes) or bool(self.moved_panes))

    @property
    def needs_layout_update(self) -> bool:
        """Check if layout geometry needs update"""
        return (bool(self.modified_nodes) or bool(self.added_nodes) or
                bool(self.removed_nodes) or self.geometry_changed)

class NodeInfoCollector(NodeVisitor):
    """Visitor that collects node information for diffing"""

    def __init__(self):
        self.node_info: dict[NodeId, NodeInfo] = {}
        self.current_path: list[NodeId] = []

    def visit_leaf(self, node: LeafNode) -> None:
        self.node_info[node.node_id] = NodeInfo(
            node_id=node.node_id,
            node_type='leaf',
            widget_id=node.widget_id,
            pane_id=node.pane_id,
            path=self.current_path.copy(),
            constraints=node.size_constraints
        )

    def visit_split(self, node: SplitNode) -> None:
        self.current_path.append(node.node_id)

        self.node_info[node.node_id] = NodeInfo(
            node_id=node.node_id,
            node_type='split',
            orientation=node.orientation,
            ratios=node.ratios.copy(),
            children_ids=[child.node_id for child in node.children],
            path=self.current_path.copy()
        )

        # Visit children
        for child in node.children:
            child.accept(self)

        self.current_path.pop()
```

### Reconciliation Engine

```python
class PaneReconciler:
    """Synchronizes model tree with Qt layout"""

    def __init__(self, container: 'PaneContainer'):
        self.container = container
        self.tree_differ = TreeDiffer()
        self.geometry_calculator = GeometryCalculator()
        self.update_scheduler = UpdateScheduler()

        # State tracking
        self.current_tree: Optional[PaneNode] = None
        self.reconciling = False
        self.pending_updates: set[PaneId] = set()

    def reconcile(self, new_tree: Optional[PaneNode], force: bool = False):
        """Reconcile view with new tree state"""

        if self.reconciling and not force:
            # Queue update for later
            self.update_scheduler.schedule_reconcile(new_tree)
            return

        self.reconciling = True
        try:
            # Calculate differences
            diff = self.tree_differ.diff_trees(self.current_tree, new_tree)

            if not diff.has_changes and not force:
                return  # No changes needed

            # Apply changes in optimal order
            self._apply_diff(diff, new_tree)

            # Update current state
            self.current_tree = new_tree

        finally:
            self.reconciling = False

            # Process any queued updates
            self.update_scheduler.process_queued()

    def _apply_diff(self, diff: DiffResult, new_tree: Optional[PaneNode]):
        """Apply calculated differences to view"""

        # Disable updates during reconciliation
        self.container.setUpdatesEnabled(False)
        try:
            # 1. Remove widgets for deleted panes
            for pane_id in diff.removed_panes:
                self._remove_pane_widget(pane_id)

            # 2. Request widgets for new panes
            for pane_id in diff.added_panes:
                self._request_pane_widget(pane_id, new_tree)

            # 3. Update modified nodes
            for node_id in diff.modified_nodes:
                self._update_node_layout(node_id, new_tree)

            # 4. Handle moved panes
            for pane_id in diff.moved_panes:
                self._move_pane_widget(pane_id, new_tree)

            # 5. Recalculate layout if needed
            if diff.needs_layout_update:
                self._update_layout_geometry(new_tree)

        finally:
            self.container.setUpdatesEnabled(True)
            self.container.update()  # Trigger repaint

    def _remove_pane_widget(self, pane_id: PaneId):
        """Remove widget for deleted pane"""
        widget_container = self.container.pane_containers.get(pane_id)
        if widget_container:
            # Notify provider that widget is no longer needed
            widget = widget_container.widget
            if widget and self.container.widget_provider:
                self.container.widget_provider.release_widget(
                    widget_container.widget_id, widget
                )

            # Remove from layout
            widget_container.setParent(None)
            widget_container.deleteLater()

            # Clean up tracking
            del self.container.pane_containers[pane_id]
            if pane_id in self.container.widget_map:
                del self.container.widget_map[pane_id]

    def _request_pane_widget(self, pane_id: PaneId, tree: PaneNode):
        """Request widget for new pane"""
        # Find the leaf node
        leaf_node = self._find_leaf_in_tree(tree, pane_id)
        if not leaf_node:
            logger.error(f"Leaf node not found for pane {pane_id}")
            return

        # Request widget from provider
        if self.container.widget_provider:
            try:
                widget = self.container.widget_provider.provide_widget(
                    leaf_node.widget_id, pane_id
                )

                if widget:
                    self._create_pane_container(pane_id, leaf_node.widget_id, widget)
                else:
                    self._create_error_widget(pane_id, f"Failed to provide widget: {leaf_node.widget_id}")

            except Exception as e:
                logger.error(f"Widget provider error for {leaf_node.widget_id}: {e}")
                self._create_error_widget(pane_id, str(e))

    def _create_pane_container(self, pane_id: PaneId, widget_id: WidgetId,
                              widget: QWidget):
        """Create container for pane widget"""
        container = PaneContainer(pane_id, widget_id, widget)

        # Set up focus handling
        container.focus_gained.connect(
            lambda: self.container.pane_focused.emit(pane_id)
        )

        # Add to tracking
        self.container.pane_containers[pane_id] = container
        self.container.widget_map[pane_id] = widget

        # Add to layout (will be positioned by geometry calculation)
        container.setParent(self.container)

    def _update_layout_geometry(self, tree: Optional[PaneNode]):
        """Recalculate and apply layout geometry"""
        if not tree:
            return

        # Calculate layout
        layout = self.geometry_calculator.calculate_layout(
            tree, self.container.rect()
        )

        # Apply geometry to all pane containers
        for pane_id, geometry in layout.pane_geometries.items():
            container = self.container.pane_containers.get(pane_id)
            if container:
                container.setGeometry(geometry)

        # Update dividers
        self.container.divider_manager.update_dividers(layout.divider_geometries)
```

---

## Render Pipeline

### Composable Rendering System

```python
class RenderPipeline:
    """Composable rendering pipeline for visual effects"""

    def __init__(self, container: 'PaneContainer'):
        self.container = container
        self.stages: list[RenderStage] = []
        self.render_cache: dict[str, QPixmap] = {}
        self.dirty_regions: set[QRect] = set()

        # Standard stages
        self.add_stage(BackgroundRenderStage())
        self.add_stage(PaneRenderStage())
        self.add_stage(DividerRenderStage())
        self.add_stage(FocusRenderStage())
        self.add_stage(SelectionRenderStage())
        self.add_stage(OverlayRenderStage())

    def add_stage(self, stage: 'RenderStage'):
        """Add a render stage to the pipeline"""
        stage.set_container(self.container)
        self.stages.append(stage)

    def remove_stage(self, stage_type: type):
        """Remove render stage by type"""
        self.stages = [s for s in self.stages if not isinstance(s, stage_type)]

    def render(self, painter: QPainter, rect: QRect, force: bool = False):
        """Execute full render pipeline"""

        # Check if render is needed
        if not force and not self._needs_render(rect):
            return

        # Prepare render context
        context = RenderContext(
            painter=painter,
            rect=rect,
            container=self.container,
            timestamp=time.time()
        )

        # Execute stages in order
        for stage in self.stages:
            if stage.enabled:
                try:
                    stage.render(context)
                except Exception as e:
                    logger.warning(f"Render stage {stage.__class__.__name__} failed: {e}")

        # Clear dirty regions
        self.dirty_regions.clear()

    def invalidate_region(self, rect: QRect):
        """Mark region as needing redraw"""
        self.dirty_regions.add(rect)
        self.container.update(rect)

    def invalidate_all(self):
        """Mark entire view as needing redraw"""
        self.dirty_regions.clear()
        self.dirty_regions.add(self.container.rect())
        self.container.update()

    def _needs_render(self, rect: QRect) -> bool:
        """Check if given rect needs rendering"""
        return any(dirty.intersects(rect) for dirty in self.dirty_regions)

class RenderStage(ABC):
    """Abstract base for render pipeline stages"""

    def __init__(self):
        self.enabled = True
        self.container: Optional['PaneContainer'] = None

    def set_container(self, container: 'PaneContainer'):
        """Set container reference"""
        self.container = container

    @abstractmethod
    def render(self, context: 'RenderContext'):
        """Render this stage"""

    def should_render(self, context: 'RenderContext') -> bool:
        """Check if this stage should render"""
        return self.enabled

class PaneRenderStage(RenderStage):
    """Renders pane backgrounds and borders"""

    def render(self, context: RenderContext):
        """Render pane visual elements"""
        if not self.container:
            return

        # Render each pane container
        for pane_id, container in self.container.pane_containers.items():
            pane_rect = container.geometry()

            if not pane_rect.intersects(context.rect):
                continue  # Skip panes outside render area

            # Save painter state
            context.painter.save()

            try:
                # Translate to pane coordinates
                context.painter.translate(pane_rect.topLeft())

                # Render pane background
                self._render_pane_background(context, container, pane_id)

                # Render pane border
                self._render_pane_border(context, container, pane_id)

            finally:
                context.painter.restore()

    def _render_pane_background(self, context: RenderContext,
                               container: PaneContainer, pane_id: PaneId):
        """Render pane background"""
        rect = QRect(0, 0, container.width(), container.height())

        # Get background color based on state
        if pane_id == self.container.focused_pane_id:
            color = self.container.theme.focused_pane_background
        elif pane_id in self.container.selected_panes:
            color = self.container.theme.selected_pane_background
        else:
            color = self.container.theme.pane_background

        context.painter.fillRect(rect, color)

    def _render_pane_border(self, context: RenderContext,
                           container: PaneContainer, pane_id: PaneId):
        """Render pane border"""
        rect = QRect(0, 0, container.width(), container.height())

        # Get border style based on state
        if pane_id == self.container.focused_pane_id:
            pen = QPen(self.container.theme.focused_pane_border, 2)
        elif pane_id in self.container.selected_panes:
            pen = QPen(self.container.theme.selected_pane_border, 1)
        else:
            pen = QPen(self.container.theme.pane_border, 1)

        context.painter.setPen(pen)
        context.painter.drawRect(rect.adjusted(0, 0, -1, -1))

class DividerRenderStage(RenderStage):
    """Renders split dividers"""

    def render(self, context: RenderContext):
        """Render all dividers"""
        if not self.container.divider_manager:
            return

        for divider in self.container.divider_manager.dividers:
            if divider.geometry.intersects(context.rect):
                self._render_divider(context, divider)

    def _render_divider(self, context: RenderContext, divider: 'Divider'):
        """Render a single divider"""
        rect = divider.geometry

        # Get divider color based on state
        if divider.is_dragging:
            color = self.container.theme.divider_dragging
        elif divider.is_hovered:
            color = self.container.theme.divider_hover
        else:
            color = self.container.theme.divider_normal

        context.painter.fillRect(rect, color)

        # Render grab handle if enabled
        if self.container.theme.show_divider_handles:
            self._render_divider_handle(context, divider)

    def _render_divider_handle(self, context: RenderContext, divider: 'Divider'):
        """Render divider grab handle"""
        handle_rect = divider.get_handle_rect()

        # Draw handle pattern
        context.painter.setPen(self.container.theme.divider_handle_color)

        if divider.orientation == Orientation.HORIZONTAL:
            # Vertical dots for horizontal divider
            center_x = handle_rect.center().x()
            for i in range(3):
                y = handle_rect.top() + 6 + i * 6
                context.painter.drawEllipse(center_x - 1, y, 3, 3)
        else:
            # Horizontal dots for vertical divider
            center_y = handle_rect.center().y()
            for i in range(3):
                x = handle_rect.left() + 6 + i * 6
                context.painter.drawEllipse(x, center_y - 1, 3, 3)

class FocusRenderStage(RenderStage):
    """Renders focus indicators"""

    def render(self, context: RenderContext):
        """Render focus indicators"""
        if not self.container.focused_pane_id:
            return

        container = self.container.pane_containers.get(
            self.container.focused_pane_id
        )
        if not container:
            return

        # Render focus ring
        rect = container.geometry()
        if rect.intersects(context.rect):
            self._render_focus_ring(context, rect)

    def _render_focus_ring(self, context: RenderContext, rect: QRect):
        """Render focus ring around pane"""
        pen = QPen(self.container.theme.focus_ring_color, 3)
        pen.setStyle(Qt.DashLine)

        context.painter.setPen(pen)
        context.painter.setBrush(Qt.NoBrush)
        context.painter.drawRect(rect.adjusted(1, 1, -2, -2))
```

---

## Performance Optimization

### Update Scheduling and Batching

```python
class UpdateScheduler:
    """Schedules and batches view updates for performance"""

    def __init__(self, container: 'PaneContainer'):
        self.container = container
        self.pending_reconciles: list[PaneNode] = []
        self.pending_geometry_updates: set[PaneId] = set()
        self.pending_repaints: set[QRect] = set()

        # Timers for batching
        self.reconcile_timer = QTimer()
        self.reconcile_timer.setSingleShot(True)
        self.reconcile_timer.timeout.connect(self._process_reconciles)

        self.geometry_timer = QTimer()
        self.geometry_timer.setSingleShot(True)
        self.geometry_timer.timeout.connect(self._process_geometry_updates)

        self.repaint_timer = QTimer()
        self.repaint_timer.setSingleShot(True)
        self.repaint_timer.timeout.connect(self._process_repaints)

        # Timing configuration
        self.reconcile_delay = 16  # ~60 FPS
        self.geometry_delay = 8    # Faster for smooth resize
        self.repaint_delay = 4     # Fastest for visual updates

    def schedule_reconcile(self, tree: PaneNode):
        """Schedule tree reconciliation"""
        self.pending_reconciles.append(tree)

        if not self.reconcile_timer.isActive():
            self.reconcile_timer.start(self.reconcile_delay)

    def schedule_geometry_update(self, pane_id: PaneId):
        """Schedule geometry update for specific pane"""
        self.pending_geometry_updates.add(pane_id)

        if not self.geometry_timer.isActive():
            self.geometry_timer.start(self.geometry_delay)

    def schedule_repaint(self, rect: QRect):
        """Schedule repaint of specific region"""
        self.pending_repaints.add(rect)

        if not self.repaint_timer.isActive():
            self.repaint_timer.start(self.repaint_delay)

    def _process_reconciles(self):
        """Process batched reconciliation requests"""
        if not self.pending_reconciles:
            return

        # Use the most recent tree state
        latest_tree = self.pending_reconciles[-1]
        self.pending_reconciles.clear()

        # Perform reconciliation
        self.container.reconciler.reconcile(latest_tree, force=False)

    def _process_geometry_updates(self):
        """Process batched geometry updates"""
        if not self.pending_geometry_updates:
            return

        pane_ids = self.pending_geometry_updates.copy()
        self.pending_geometry_updates.clear()

        # Update geometry for affected panes
        for pane_id in pane_ids:
            container = self.container.pane_containers.get(pane_id)
            if container:
                self._update_pane_geometry(container)

    def _process_repaints(self):
        """Process batched repaint requests"""
        if not self.pending_repaints:
            return

        # Merge overlapping rects
        merged_rects = self._merge_rects(list(self.pending_repaints))
        self.pending_repaints.clear()

        # Trigger updates
        for rect in merged_rects:
            self.container.update(rect)

    def _merge_rects(self, rects: list[QRect]) -> list[QRect]:
        """Merge overlapping rectangles to reduce update regions"""
        if not rects:
            return []

        # Sort by area for better merging
        rects.sort(key=lambda r: r.width() * r.height(), reverse=True)

        merged = []
        for rect in rects:
            merged_with_existing = False

            for i, existing in enumerate(merged):
                if rect.intersects(existing):
                    # Merge rectangles
                    merged[i] = rect.united(existing)
                    merged_with_existing = True
                    break

            if not merged_with_existing:
                merged.append(rect)

        return merged

class ViewportOptimizer:
    """Optimizes rendering based on visible viewport"""

    def __init__(self, container: 'PaneContainer'):
        self.container = container
        self.viewport_rect = QRect()
        self.visible_panes: set[PaneId] = set()
        self.culling_enabled = True

    def update_viewport(self, rect: QRect):
        """Update viewport information"""
        if rect == self.viewport_rect:
            return

        self.viewport_rect = rect
        self._update_visible_panes()

    def _update_visible_panes(self):
        """Update set of visible panes"""
        new_visible = set()

        for pane_id, container in self.container.pane_containers.items():
            if container.geometry().intersects(self.viewport_rect):
                new_visible.add(pane_id)

        # Handle visibility changes
        newly_visible = new_visible - self.visible_panes
        newly_hidden = self.visible_panes - new_visible

        for pane_id in newly_visible:
            self._on_pane_visible(pane_id)

        for pane_id in newly_hidden:
            self._on_pane_hidden(pane_id)

        self.visible_panes = new_visible

    def _on_pane_visible(self, pane_id: PaneId):
        """Handle pane becoming visible"""
        container = self.container.pane_containers.get(pane_id)
        if container:
            # Ensure widget is properly initialized
            if hasattr(container.widget, 'on_visible'):
                container.widget.on_visible()

    def _on_pane_hidden(self, pane_id: PaneId):
        """Handle pane becoming hidden"""
        container = self.container.pane_containers.get(pane_id)
        if container:
            # Allow widget to optimize for hidden state
            if hasattr(container.widget, 'on_hidden'):
                container.widget.on_hidden()

    def should_render_pane(self, pane_id: PaneId) -> bool:
        """Check if pane should be rendered"""
        if not self.culling_enabled:
            return True

        return pane_id in self.visible_panes
```

---

## Widget Lifecycle Management

### Provider Integration

```python
class WidgetLifecycleManager:
    """Manages widget creation, lifecycle, and cleanup"""

    def __init__(self, container: 'PaneContainer'):
        self.container = container
        self.widget_provider: Optional[WidgetProvider] = None
        self.pending_requests: dict[PaneId, WidgetRequest] = {}
        self.widget_cache: dict[WidgetId, list[QWidget]] = {}
        self.cleanup_queue: list[QWidget] = []

        # Cleanup timer
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self._process_cleanup)
        self.cleanup_timer.start(5000)  # Cleanup every 5 seconds

    def set_provider(self, provider: WidgetProvider):
        """Set the widget provider"""
        self.widget_provider = provider

    def request_widget(self, pane_id: PaneId, widget_id: WidgetId) -> bool:
        """Request widget from provider"""
        if not self.widget_provider:
            logger.error("No widget provider set")
            return False

        if pane_id in self.pending_requests:
            return True  # Already requested

        # Check cache first
        cached_widget = self._get_cached_widget(widget_id)
        if cached_widget:
            self._provide_widget(pane_id, widget_id, cached_widget)
            return True

        # Create request
        request = WidgetRequest(
            pane_id=pane_id,
            widget_id=widget_id,
            timestamp=time.time()
        )

        self.pending_requests[pane_id] = request

        # Request from provider (async)
        try:
            if hasattr(self.widget_provider, 'provide_widget_async'):
                # Async provider
                future = self.widget_provider.provide_widget_async(widget_id, pane_id)
                future.finished.connect(
                    lambda: self._on_widget_provided(pane_id, future.result())
                )
            else:
                # Sync provider - run in thread to avoid blocking
                self._request_widget_threaded(pane_id, widget_id)

        except Exception as e:
            logger.error(f"Widget request failed: {e}")
            self._on_widget_error(pane_id, e)
            return False

        return True

    def _request_widget_threaded(self, pane_id: PaneId, widget_id: WidgetId):
        """Request widget in background thread"""
        def worker():
            try:
                widget = self.widget_provider.provide_widget(widget_id, pane_id)
                QMetaObject.invokeMethod(
                    self.container,
                    "_on_widget_provided",
                    Qt.QueuedConnection,
                    Q_ARG("PaneId", pane_id),
                    Q_ARG("QWidget*", widget)
                )
            except Exception as e:
                QMetaObject.invokeMethod(
                    self.container,
                    "_on_widget_error",
                    Qt.QueuedConnection,
                    Q_ARG("PaneId", pane_id),
                    Q_ARG("str", str(e))
                )

        thread = threading.Thread(target=worker)
        thread.daemon = True
        thread.start()

    def _on_widget_provided(self, pane_id: PaneId, widget: QWidget):
        """Handle widget provided by provider"""
        request = self.pending_requests.pop(pane_id, None)
        if not request:
            return  # Request was cancelled

        if widget:
            self._provide_widget(pane_id, request.widget_id, widget)
        else:
            self._on_widget_error(pane_id, "Provider returned None")

    def _on_widget_error(self, pane_id: PaneId, error):
        """Handle widget provision error"""
        request = self.pending_requests.pop(pane_id, None)
        if not request:
            return

        # Create error widget
        error_widget = self._create_error_widget(request.widget_id, str(error))
        self._provide_widget(pane_id, request.widget_id, error_widget)

    def _provide_widget(self, pane_id: PaneId, widget_id: WidgetId,
                       widget: QWidget):
        """Provide widget to pane"""
        # Create pane container
        container = PaneContainer(pane_id, widget_id, widget)

        # Set up container
        container.setParent(self.container)
        container.focus_gained.connect(
            lambda: self.container.pane_focused.emit(pane_id)
        )

        # Add to tracking
        self.container.pane_containers[pane_id] = container
        self.container.widget_map[pane_id] = widget

        # Signal completion
        self.container.widget_provided.emit(pane_id, widget_id)

    def release_widget(self, pane_id: PaneId):
        """Release widget for pane"""
        container = self.container.pane_containers.get(pane_id)
        if not container:
            return

        widget = container.widget
        widget_id = container.widget_id

        # Notify provider
        if self.widget_provider and widget:
            try:
                self.widget_provider.release_widget(widget_id, widget)
            except Exception as e:
                logger.warning(f"Widget release error: {e}")

        # Queue for cleanup
        self.cleanup_queue.append(widget)

        # Remove from tracking
        container.setParent(None)
        del self.container.pane_containers[pane_id]
        if pane_id in self.container.widget_map:
            del self.container.widget_map[pane_id]

    def _get_cached_widget(self, widget_id: WidgetId) -> Optional[QWidget]:
        """Get cached widget if available"""
        cached_list = self.widget_cache.get(widget_id, [])
        if cached_list:
            return cached_list.pop()
        return None

    def _cache_widget(self, widget_id: WidgetId, widget: QWidget):
        """Cache widget for reuse"""
        if widget_id not in self.widget_cache:
            self.widget_cache[widget_id] = []

        cache_list = self.widget_cache[widget_id]
        if len(cache_list) < 3:  # Limit cache size
            cache_list.append(widget)
        else:
            # Cache full, delete widget
            widget.deleteLater()

    def _process_cleanup(self):
        """Process queued widget cleanup"""
        while self.cleanup_queue:
            widget = self.cleanup_queue.pop(0)
            try:
                if not widget.parent():  # Only delete orphaned widgets
                    widget.deleteLater()
            except Exception as e:
                logger.warning(f"Widget cleanup error: {e}")

    def _create_error_widget(self, widget_id: WidgetId, error: str) -> QWidget:
        """Create error placeholder widget"""
        widget = QWidget()
        widget.setStyleSheet("background-color: #ffeeee; color: #cc0000;")

        layout = QVBoxLayout(widget)

        # Error icon
        icon_label = QLabel()
        icon_label.setPixmap(
            widget.style().standardIcon(QStyle.SP_MessageBoxCritical).pixmap(32, 32)
        )

        # Error message
        message_label = QLabel(f"Failed to load widget:\n{widget_id}\n\nError: {error}")
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setWordWrap(True)

        # Retry button
        retry_button = QPushButton("Retry")
        retry_button.clicked.connect(
            lambda: self.container.retry_widget_load(widget_id)
        )

        layout.addWidget(icon_label, alignment=Qt.AlignCenter)
        layout.addWidget(message_label)
        layout.addWidget(retry_button)

        return widget
```

---

## Accessibility Support

### Screen Reader Integration

```python
class AccessibilityManager:
    """Manages accessibility features for MultiSplit"""

    def __init__(self, view: MultiSplitView):
        self.view = view
        self.announcer = ScreenReaderAnnouncer()
        self.navigation = AccessibleNavigation()

    def setup_pane_accessibility(self, pane_widget: QWidget,
                                pane_id: PaneId, leaf: LeafNode):
        """Configure accessibility for a pane"""
        # Set ARIA-like properties
        pane_widget.setAccessibleName(f"Pane {pane_id}")
        pane_widget.setAccessibleDescription(
            f"Content pane containing {leaf.widget_id}"
        )

        # Set navigation hints
        pane_widget.setProperty("role", "region")
        pane_widget.setProperty("aria-label", f"Split pane {pane_id}")
        pane_widget.setProperty("aria-live", "polite")

        # Focus indicator for screen readers
        if self.view.model.focused_pane_id == pane_id:
            pane_widget.setProperty("aria-current", "true")

    def announce_structure_change(self, change_type: str, details: dict):
        """Announce structural changes to screen readers"""
        if change_type == "split":
            self.announcer.announce(
                f"Pane split into {details['orientation']} layout"
            )
        elif change_type == "close":
            self.announcer.announce(f"Pane closed")
        elif change_type == "focus":
            self.announcer.announce(
                f"Focus moved to {details['pane_id']}"
            )

    def provide_navigation_hints(self) -> list[str]:
        """Generate keyboard navigation hints"""
        return [
            "Ctrl+Arrow: Navigate between panes",
            "Ctrl+Enter: Split current pane",
            "Ctrl+W: Close current pane",
            "Ctrl+Tab: Cycle through panes",
            "F6: Jump to next pane group"
        ]

class ScreenReaderAnnouncer:
    """Announces changes to screen readers"""

    def announce(self, message: str, priority: str = "polite"):
        """Send announcement to screen reader"""
        # Create invisible announcement widget
        announcer = QLabel(message)
        announcer.setAccessibleName(message)
        announcer.setAttribute(Qt.WA_TransparentForMouseEvents)
        announcer.setProperty("aria-live", priority)
        announcer.setProperty("aria-atomic", "true")

        # Trigger screen reader
        QAccessible.updateAccessibility(
            QAccessibleEvent(announcer,
                            QAccessible.Event.NameChanged)
        )

### High Contrast Mode

```python
class ContrastThemeManager:
    """Manages high contrast themes"""

    def __init__(self):
        self.themes = {
            'high_contrast_dark': {
                'background': '#000000',
                'foreground': '#FFFFFF',
                'border': '#FFFF00',
                'focus': '#00FFFF',
                'divider': '#808080'
            },
            'high_contrast_light': {
                'background': '#FFFFFF',
                'foreground': '#000000',
                'border': '#0000FF',
                'focus': '#FF00FF',
                'divider': '#404040'
            }
        }

    def apply_theme(self, view: QWidget, theme_name: str):
        """Apply high contrast theme"""
        if theme_name not in self.themes:
            return

        theme = self.themes[theme_name]
        stylesheet = f"""
        QWidget {{
            background-color: {theme['background']};
            color: {theme['foreground']};
        }}
        QSplitter::handle {{
            background-color: {theme['divider']};
            border: 2px solid {theme['border']};
        }}
        QWidget:focus {{
            border: 3px solid {theme['focus']};
        }}
        """
        view.setStyleSheet(stylesheet)
```

---

## Widget Pooling & Progressive Rendering

### Widget Pool Management

```python
class WidgetPool:
    """Efficient widget pooling system"""

    def __init__(self, max_pool_size: int = 50):
        self.pools: dict[str, list[QWidget]] = {}
        self.max_pool_size = max_pool_size
        self.statistics = PoolStatistics()

    def acquire(self, widget_type: str) -> Optional[QWidget]:
        """Get widget from pool"""
        pool = self.pools.get(widget_type, [])
        if pool:
            widget = pool.pop()
            self.statistics.record_hit(widget_type)
            self._reset_widget(widget)
            return widget

        self.statistics.record_miss(widget_type)
        return None

    def release(self, widget: QWidget, widget_type: str):
        """Return widget to pool"""
        if widget_type not in self.pools:
            self.pools[widget_type] = []

        pool = self.pools[widget_type]
        if len(pool) < self.max_pool_size:
            self._prepare_for_pool(widget)
            pool.append(widget)
            self.statistics.record_release(widget_type)
        else:
            widget.deleteLater()
            self.statistics.record_overflow(widget_type)

    def _reset_widget(self, widget: QWidget):
        """Reset widget state for reuse"""
        widget.setParent(None)
        widget.hide()
        widget.setProperty("pooled", False)

        # Clear connections
        try:
            widget.disconnect()
        except:
            pass

    def _prepare_for_pool(self, widget: QWidget):
        """Prepare widget for pooling"""
        widget.setParent(None)
        widget.hide()
        widget.setProperty("pooled", True)

### Progressive Rendering

```python
class ProgressiveRenderer:
    """Render large trees progressively"""

    def __init__(self, view: MultiSplitView):
        self.view = view
        self.render_queue = deque()
        self.batch_size = 10
        self.timer = QTimer()
        self.timer.timeout.connect(self._process_batch)
        self.timer.setInterval(16)  # 60 FPS

    def schedule_render(self, nodes: list[PaneNode]):
        """Schedule nodes for progressive rendering"""
        # Prioritize visible nodes
        visible = []
        offscreen = []

        for node in nodes:
            bounds = self.view.geometry_calculator.calculate_bounds(node)
            if self._is_visible(bounds):
                visible.append((0, node))  # High priority
            else:
                offscreen.append((1, node))  # Low priority

        # Add to queue in priority order
        self.render_queue.extend(visible)
        self.render_queue.extend(offscreen)

        if not self.timer.isActive():
            self.timer.start()

    def _process_batch(self):
        """Process a batch of render operations"""
        processed = 0

        while self.render_queue and processed < self.batch_size:
            _, node = self.render_queue.popleft()
            self._render_node(node)
            processed += 1

        if not self.render_queue:
            self.timer.stop()

    def _is_visible(self, bounds: Bounds) -> bool:
        """Check if bounds are in viewport"""
        viewport = self.view.viewport().geometry()
        return bounds.intersects(viewport)
```

---

## Animation Frame Scheduling

```python
class AnimationScheduler:
    """Optimized animation frame scheduling"""

    def __init__(self):
        self.animations: dict[str, Animation] = {}
        self.frame_timer = QElapsedTimer()
        self.target_fps = 60
        self.frame_budget = 1000 / self.target_fps

    def schedule_animation(self, animation: Animation):
        """Schedule animation for execution"""
        self.animations[animation.id] = animation
        if len(self.animations) == 1:
            self._start_animation_loop()

    def _start_animation_loop(self):
        """Start the animation loop"""
        self.frame_timer.start()
        QTimer.singleShot(0, self._animation_frame)

    def _animation_frame(self):
        """Process one animation frame"""
        frame_start = self.frame_timer.elapsed()

        # Update all animations
        completed = []
        for anim_id, animation in self.animations.items():
            if animation.update(frame_start):
                completed.append(anim_id)

        # Remove completed animations
        for anim_id in completed:
            del self.animations[anim_id]

        # Schedule next frame if needed
        if self.animations:
            frame_duration = self.frame_timer.elapsed() - frame_start
            next_frame_delay = max(0, self.frame_budget - frame_duration)
            QTimer.singleShot(int(next_frame_delay), self._animation_frame)
```

---

## Performance Benchmarks

### Rendering Performance Targets

| Operation | Target | Maximum | Notes |
|-----------|--------|---------|-------|
| Tree Diff (100 nodes) | < 2ms | 5ms | O(n) complexity |
| Reconciliation (10 changes) | < 5ms | 10ms | Reuse widgets |
| Layout Update | < 10ms | 20ms | Batch geometry |
| Widget Provision | < 1ms | 50ms | Use pooling |
| Frame Render | < 16ms | 33ms | 60/30 FPS |
| Focus Change | < 1ms | 5ms | Cached paths |

### Memory Usage Guidelines

| Component | Per-Instance | Maximum | Strategy |
|-----------|-------------|---------|----------|
| Widget Pool | ~1MB | 50MB | Limit pool size |
| Render Cache | ~100KB | 10MB | LRU eviction |
| Geometry Cache | ~10KB | 1MB | Invalidate on change |
| Animation State | ~1KB | 100KB | Cleanup on complete |

---

## Common Pitfalls

### ❌ Direct Model Mutation from View
```python
# DON'T: Mutate model from view
def mousePressEvent(self, event):
    self.model.focused_pane_id = self.pane_under_mouse()
    self.model.root.children.append(new_node)

# DO: Emit signals for controller to handle
def mousePressEvent(self, event):
    pane_id = self.pane_under_mouse()
    self.pane_focus_requested.emit(pane_id)
```

### ❌ Inefficient Reconciliation
```python
# DON'T: Recreate all widgets on every change
def update_layout(self, new_tree):
    self.clear_all_widgets()  # Destroys everything!
    self.create_all_widgets(new_tree)

# DO: Use differential reconciliation
def update_layout(self, new_tree):
    diff = self.reconciler.diff_trees(self.current_tree, new_tree)
    self.reconciler.apply_diff(diff, new_tree)
```

### ❌ Blocking UI with Synchronous Operations
```python
# DON'T: Block UI for widget creation
widget = provider.provide_widget(widget_id)  # May take time!
self.add_widget_to_layout(widget)

# DO: Use async widget provision
future = provider.provide_widget_async(widget_id)
future.finished.connect(self.on_widget_ready)
```

### ❌ Memory Leaks from Widget References
```python
# DON'T: Keep strong references to released widgets
self.released_widgets.append(widget)  # Memory leak!

# DO: Properly clean up widget references
widget.setParent(None)
widget.deleteLater()
del self.widget_map[pane_id]
```

### ❌ Ignoring Performance Optimization
```python
# DON'T: Update immediately on every change
def on_model_changed(self):
    self.reconcile()  # Called many times per second!

# DO: Batch updates for performance
def on_model_changed(self):
    self.update_scheduler.schedule_reconcile(self.model.root)
```

---

## Quick Reference

### Reconciliation Phases
| Phase | Purpose | Performance |
|-------|---------|-------------|
| Diff Calculation | Find minimal changes | O(n) tree traversal |
| Widget Removal | Clean up deleted panes | O(1) per removed pane |
| Widget Addition | Request new widgets | Async provider calls |
| Layout Update | Apply geometry changes | O(n) pane containers |

### Render Pipeline Stages
| Stage | Purpose | Performance Impact |
|-------|---------|-------------------|
| Background | Basic pane background | Low |
| Pane | Pane borders and styling | Medium |
| Divider | Split dividers | Low |
| Focus | Focus indicators | Low |
| Selection | Selection highlights | Medium |
| Overlay | Custom overlays | Variable |

### Update Batching
| Update Type | Batch Window | Priority |
|-------------|--------------|----------|
| Reconciliation | 16ms | Normal |
| Geometry | 8ms | High |
| Repaint | 4ms | Highest |

### Widget Lifecycle
| Phase | Responsibility | Error Handling |
|-------|----------------|---------------|
| Request | View → Provider | Fallback to error widget |
| Provision | Provider → View | Async completion |
| Integration | View internal | Container setup |
| Release | View → Provider | Best effort cleanup |

### Performance Optimization
| Technique | Benefit | Cost |
|-----------|---------|------|
| Viewport Culling | Skip hidden panes | Geometry calculations |
| Update Batching | Reduce UI churn | Slight latency |
| Widget Caching | Faster provision | Memory usage |
| Dirty Region Tracking | Minimize repaints | Tracking overhead |

---

## Validation Checklist

- ✅ Reconciliation preserves widget instances when possible
- ✅ Tree differences calculated efficiently
- ✅ Widget lifecycle properly managed
- ✅ Memory leaks prevented through proper cleanup
- ✅ Performance optimized with batching and culling
- ✅ Error widgets provided for provision failures
- ✅ Render pipeline is composable and extensible
- ✅ Viewport optimization reduces unnecessary work
- ✅ Update scheduling prevents UI thread blocking
- ✅ Widget provider integration is robust

## Related Documents

- **[Model Design](model-design.md)** - Model structures and validation
- **[Controller Design](controller-design.md)** - Command execution patterns
- **[Focus Management](focus-management.md)** - Focus tracking and navigation
- **[Widget Provider](../02-architecture/widget-provider.md)** - Provider pattern details
- **[MVC Architecture](../02-architecture/mvc-architecture.md)** - Layer separation
- **[MVP Plan](../03-implementation/mvp-plan.md)** - Reconciler implementation
- **[Tree Structure](../02-architecture/tree-structure.md)** - Tree traversal patterns
- **[Development Rules](../03-implementation/development-rules.md)** - View layer constraints

---

The view design ensures efficient, responsive rendering while maintaining clean separation from business logic and providing robust error handling for complex widget hierarchies.