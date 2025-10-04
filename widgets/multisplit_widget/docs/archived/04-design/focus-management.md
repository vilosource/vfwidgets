# Focus Management Design

## Overview

Focus management in MultiSplit provides sophisticated tracking, spatial navigation, and focus chain algorithms while maintaining synchronization across model, controller, and view layers. The system supports both traditional tab-order traversal and advanced spatial navigation for intuitive pane-to-pane movement.

## What This Covers

- **Focus Chain Management**: Hierarchical focus order calculation
- **Spatial Navigation**: Geometric focus movement algorithms
- **Focus State Synchronization**: Cross-layer focus coordination
- **Focus Events**: Qt focus integration and event handling
- **Navigation Optimization**: Performance-optimized focus finding
- **Focus Restoration**: State persistence and recovery

## What This Doesn't Cover

- General model structures (see [Model Design](model-design.md))
- Command execution (see [Controller Design](controller-design.md))
- View reconciliation (see [View Design](view-design.md))
- Widget-specific focus behavior (application responsibility)

---

## Focus Chain Architecture

### Hierarchical Focus Order

```python
class FocusChainManager:
    """Manages hierarchical focus order calculation"""

    def __init__(self, model: PaneModel):
        self.model = model
        self.focus_order_cache: Optional[list[PaneId]] = None
        self.cache_valid = False
        self.spatial_cache: dict[PaneId, SpatialNeighbors] = {}

        # Connect to model changes
        self.model.signals.structure_changed.connect(self._invalidate_cache)
        self.model.signals.node_modified.connect(self._invalidate_cache)

    def get_focus_order(self) -> list[PaneId]:
        """Get panes in focus traversal order"""
        if not self.cache_valid or self.focus_order_cache is None:
            self._rebuild_focus_order()

        return self.focus_order_cache.copy()

    def _rebuild_focus_order(self):
        """Rebuild focus order from tree structure"""
        if not self.model.root:
            self.focus_order_cache = []
            self.cache_valid = True
            return

        # Use focus order visitor
        visitor = FocusOrderVisitor()
        self.model.root.accept(visitor)

        # Sort by focus hints if available
        panes_with_hints = [(pane_id, hint) for pane_id, hint in visitor.panes_with_hints]
        panes_without_hints = visitor.panes_without_hints

        # Sort panes with hints by hint value
        panes_with_hints.sort(key=lambda x: x[1] if x[1] is not None else float('inf'))

        # Combine ordered lists
        self.focus_order_cache = (
            [pane_id for pane_id, _ in panes_with_hints] +
            panes_without_hints
        )

        self.cache_valid = True

    def get_next_pane(self, current_pane: PaneId) -> Optional[PaneId]:
        """Get next pane in focus order"""
        order = self.get_focus_order()
        if not order or current_pane not in order:
            return order[0] if order else None

        current_index = order.index(current_pane)
        next_index = (current_index + 1) % len(order)
        return order[next_index]

    def get_previous_pane(self, current_pane: PaneId) -> Optional[PaneId]:
        """Get previous pane in focus order"""
        order = self.get_focus_order()
        if not order or current_pane not in order:
            return order[-1] if order else None

        current_index = order.index(current_pane)
        prev_index = (current_index - 1) % len(order)
        return order[prev_index]

    def _invalidate_cache(self):
        """Invalidate cached focus order"""
        self.cache_valid = False
        self.spatial_cache.clear()

class FocusOrderVisitor(NodeVisitor):
    """Visitor that calculates focus traversal order"""

    def __init__(self):
        self.panes_with_hints: list[tuple[PaneId, Optional[int]]] = []
        self.panes_without_hints: list[PaneId] = []
        self.current_path: list[PaneNode] = []

    def visit_leaf(self, node: LeafNode):
        """Process leaf node for focus order"""
        self.current_path.append(node)

        if node.focus_order_hint is not None:
            self.panes_with_hints.append((node.pane_id, node.focus_order_hint))
        else:
            # Use tree position for natural order
            self.panes_without_hints.append(node.pane_id)

        self.current_path.pop()

    def visit_split(self, node: SplitNode):
        """Process split node - traverse children left-to-right, top-to-bottom"""
        self.current_path.append(node)

        # For horizontal splits: left to right
        # For vertical splits: top to bottom
        for child in node.children:
            child.accept(self)

        self.current_path.pop()
```

---

## Spatial Navigation System

### Geometric Focus Movement

```python
class SpatialNavigator:
    """Advanced spatial focus navigation"""

    def __init__(self, model: PaneModel, geometry_provider: 'GeometryProvider'):
        self.model = model
        self.geometry_provider = geometry_provider
        self.neighbor_cache: dict[PaneId, SpatialNeighbors] = {}
        self.cache_valid = False

        # Navigation configuration
        self.config = SpatialNavigationConfig(
            overlap_threshold=0.1,  # Minimum overlap for adjacency
            distance_penalty=1.0,   # Weight for distance calculation
            alignment_bonus=0.5,    # Bonus for aligned panes
            max_search_distance=1000  # Maximum pixel distance
        )

    def find_neighbor(self, from_pane: PaneId, direction: Direction) -> Optional[PaneId]:
        """Find best neighbor in given direction"""
        if not self.cache_valid:
            self._rebuild_spatial_cache()

        neighbors = self.neighbor_cache.get(from_pane)
        if not neighbors:
            return None

        return neighbors.get_neighbor(direction)

    def _rebuild_spatial_cache(self):
        """Rebuild spatial neighbor cache"""
        self.neighbor_cache.clear()

        if not self.model.root:
            self.cache_valid = True
            return

        # Get all pane geometries
        pane_geometries = self._get_all_pane_geometries()

        # Calculate neighbors for each pane
        for pane_id, geometry in pane_geometries.items():
            neighbors = self._calculate_neighbors(pane_id, geometry, pane_geometries)
            self.neighbor_cache[pane_id] = neighbors

        self.cache_valid = True

    def _get_all_pane_geometries(self) -> dict[PaneId, QRect]:
        """Get geometries for all panes"""
        geometries = {}

        if self.geometry_provider:
            for pane_id in self.model.pane_registry.keys():
                geometry = self.geometry_provider.get_pane_geometry(pane_id)
                if geometry and not geometry.isEmpty():
                    geometries[pane_id] = geometry

        return geometries

    def _calculate_neighbors(self, source_pane: PaneId, source_rect: QRect,
                           all_geometries: dict[PaneId, QRect]) -> 'SpatialNeighbors':
        """Calculate spatial neighbors for a pane"""
        neighbors = SpatialNeighbors()

        for direction in [Direction.LEFT, Direction.RIGHT, Direction.UP, Direction.DOWN]:
            best_neighbor = self._find_best_neighbor(
                source_pane, source_rect, direction, all_geometries
            )
            if best_neighbor:
                neighbors.set_neighbor(direction, best_neighbor)

        return neighbors

    def _find_best_neighbor(self, source_pane: PaneId, source_rect: QRect,
                           direction: Direction,
                           all_geometries: dict[PaneId, QRect]) -> Optional[PaneId]:
        """Find best neighbor in specific direction"""
        candidates = []

        for pane_id, geometry in all_geometries.items():
            if pane_id == source_pane:
                continue

            # Check if pane is in the right direction
            if not self._is_in_direction(source_rect, geometry, direction):
                continue

            # Calculate score for this candidate
            score = self._calculate_navigation_score(
                source_rect, geometry, direction
            )

            if score > 0:
                candidates.append((pane_id, score))

        # Return best candidate
        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0][0]

        return None

    def _is_in_direction(self, source: QRect, target: QRect,
                        direction: Direction) -> bool:
        """Check if target is in the given direction from source"""
        if direction == Direction.LEFT:
            return target.right() <= source.left()
        elif direction == Direction.RIGHT:
            return target.left() >= source.right()
        elif direction == Direction.UP:
            return target.bottom() <= source.top()
        elif direction == Direction.DOWN:
            return target.top() >= source.bottom()

        return False

    def _calculate_navigation_score(self, source: QRect, target: QRect,
                                   direction: Direction) -> float:
        """Calculate navigation score for candidate pane"""
        # Base score starts at 1.0
        score = 1.0

        # Calculate overlap in perpendicular direction
        overlap = self._calculate_perpendicular_overlap(source, target, direction)
        if overlap < self.config.overlap_threshold:
            return 0.0  # Insufficient overlap

        # Overlap bonus
        overlap_ratio = overlap / self._get_perpendicular_size(source, direction)
        score += overlap_ratio * self.config.alignment_bonus

        # Distance penalty
        distance = self._calculate_direction_distance(source, target, direction)
        if distance > self.config.max_search_distance:
            return 0.0

        distance_penalty = distance / self.config.max_search_distance
        score -= distance_penalty * self.config.distance_penalty

        return max(0.0, score)

    def _calculate_perpendicular_overlap(self, source: QRect, target: QRect,
                                        direction: Direction) -> float:
        """Calculate overlap perpendicular to movement direction"""
        if direction in [Direction.LEFT, Direction.RIGHT]:
            # Vertical overlap for horizontal movement
            overlap_start = max(source.top(), target.top())
            overlap_end = min(source.bottom(), target.bottom())
        else:
            # Horizontal overlap for vertical movement
            overlap_start = max(source.left(), target.left())
            overlap_end = min(source.right(), target.right())

        return max(0.0, overlap_end - overlap_start)

    def _get_perpendicular_size(self, rect: QRect, direction: Direction) -> float:
        """Get size perpendicular to movement direction"""
        if direction in [Direction.LEFT, Direction.RIGHT]:
            return rect.height()
        else:
            return rect.width()

    def _calculate_direction_distance(self, source: QRect, target: QRect,
                                     direction: Direction) -> float:
        """Calculate distance in movement direction"""
        if direction == Direction.LEFT:
            return source.left() - target.right()
        elif direction == Direction.RIGHT:
            return target.left() - source.right()
        elif direction == Direction.UP:
            return source.top() - target.bottom()
        elif direction == Direction.DOWN:
            return target.top() - source.bottom()

        return 0.0

class SpatialNeighbors:
    """Container for spatial neighbors in all directions"""

    def __init__(self):
        self._neighbors: dict[Direction, Optional[PaneId]] = {
            Direction.LEFT: None,
            Direction.RIGHT: None,
            Direction.UP: None,
            Direction.DOWN: None
        }

    def get_neighbor(self, direction: Direction) -> Optional[PaneId]:
        """Get neighbor in given direction"""
        return self._neighbors.get(direction)

    def set_neighbor(self, direction: Direction, pane_id: Optional[PaneId]):
        """Set neighbor in given direction"""
        self._neighbors[direction] = pane_id

    def has_neighbor(self, direction: Direction) -> bool:
        """Check if neighbor exists in direction"""
        return self._neighbors.get(direction) is not None

    def get_all_neighbors(self) -> dict[Direction, PaneId]:
        """Get all non-None neighbors"""
        return {direction: pane_id for direction, pane_id in self._neighbors.items()
                if pane_id is not None}
```

---

## Focus State Synchronization

### Cross-Layer Coordination

```python
class FocusCoordinator:
    """Coordinates focus state across model, controller, and view"""

    def __init__(self, model: PaneModel, controller: 'PaneController',
                 view: 'PaneContainer'):
        self.model = model
        self.controller = controller
        self.view = view

        # Focus managers
        self.chain_manager = FocusChainManager(model)
        self.spatial_navigator = SpatialNavigator(model, view)

        # State tracking
        self.focus_locked = False
        self.focus_transition_in_progress = False
        self.pending_focus: Optional[PaneId] = None

        # Connect signals
        self._setup_signal_connections()

    def _setup_signal_connections(self):
        """Set up signal connections between layers"""
        # Model → Coordinator
        self.model.signals.focus_changed.connect(self._on_model_focus_changed)

        # View → Coordinator
        self.view.pane_focus_requested.connect(self._on_view_focus_requested)
        self.view.spatial_navigation_requested.connect(self._on_spatial_navigation)

        # Coordinator → Controller (via commands)
        # Coordinator → View (direct method calls)

    def focus_pane(self, pane_id: PaneId, reason: FocusReason = FocusReason.PROGRAMMATIC) -> bool:
        """Focus a specific pane"""
        if self.focus_locked:
            return False

        # Validate pane exists
        if pane_id not in self.model.pane_registry:
            return False

        # Create and execute focus command
        command = FocusCommand(pane_id, reason)
        result = self.controller.execute_command(command)

        return result.success

    def focus_next(self) -> bool:
        """Focus next pane in focus order"""
        current = self.model.focused_pane_id
        if not current:
            # No current focus, focus first pane
            order = self.chain_manager.get_focus_order()
            return self.focus_pane(order[0]) if order else False

        next_pane = self.chain_manager.get_next_pane(current)
        return self.focus_pane(next_pane) if next_pane else False

    def focus_previous(self) -> bool:
        """Focus previous pane in focus order"""
        current = self.model.focused_pane_id
        if not current:
            # No current focus, focus last pane
            order = self.chain_manager.get_focus_order()
            return self.focus_pane(order[-1]) if order else False

        prev_pane = self.chain_manager.get_previous_pane(current)
        return self.focus_pane(prev_pane) if prev_pane else False

    def focus_direction(self, direction: Direction) -> bool:
        """Focus pane in given spatial direction"""
        current = self.model.focused_pane_id
        if not current:
            return False

        target_pane = self.spatial_navigator.find_neighbor(current, direction)
        return self.focus_pane(target_pane, FocusReason.SPATIAL) if target_pane else False

    def _on_model_focus_changed(self, old_focus: Optional[PaneId],
                               new_focus: Optional[PaneId]):
        """Handle focus change from model"""
        if self.focus_transition_in_progress:
            return  # Avoid recursion

        self.focus_transition_in_progress = True
        try:
            # Update view to reflect model state
            self.view.set_focused_pane(new_focus)

            # Emit application-level signal
            self.view.pane_focused.emit(new_focus)

        finally:
            self.focus_transition_in_progress = False

    def _on_view_focus_requested(self, pane_id: PaneId):
        """Handle focus request from view (user input)"""
        if not self.focus_transition_in_progress:
            self.focus_pane(pane_id, FocusReason.USER_INPUT)

    def _on_spatial_navigation(self, direction: Direction):
        """Handle spatial navigation request from view"""
        self.focus_direction(direction)

    def lock_focus(self):
        """Lock focus to prevent changes"""
        self.focus_locked = True

    def unlock_focus(self):
        """Unlock focus to allow changes"""
        self.focus_locked = False

        # Process any pending focus change
        if self.pending_focus:
            pending = self.pending_focus
            self.pending_focus = None
            self.focus_pane(pending)

class FocusCommand(Command):
    """Command to change focus"""

    def __init__(self, pane_id: PaneId, reason: FocusReason = FocusReason.PROGRAMMATIC):
        super().__init__()
        self.pane_id = pane_id
        self.reason = reason
        self.previous_focus: Optional[PaneId] = None

    def validate(self, model: PaneModel) -> ValidationResult:
        """Validate focus command"""
        if self.pane_id not in model.pane_registry:
            return ValidationResult(False, [f"Pane {self.pane_id} not found"])

        return ValidationResult(True)

    def execute(self, model: PaneModel) -> CommandResult:
        """Execute focus change"""
        self.previous_focus = model.focused_pane_id

        if self.previous_focus == self.pane_id:
            return CommandResult(success=True)  # No change needed

        # Update model focus
        old_focus = model.focused_pane_id
        model.focused_pane_id = self.pane_id

        # Emit focus change signal
        model.signals.focus_changed.emit(old_focus, self.pane_id)

        return CommandResult(
            success=True,
            changed_panes={self.pane_id} | ({self.previous_focus} if self.previous_focus else set())
        )

    def undo(self, model: PaneModel) -> CommandResult:
        """Undo focus change"""
        current_focus = model.focused_pane_id
        model.focused_pane_id = self.previous_focus

        # Emit focus change signal
        model.signals.focus_changed.emit(current_focus, self.previous_focus)

        return CommandResult(
            success=True,
            changed_panes={current_focus} | ({self.previous_focus} if self.previous_focus else set())
        )

    def can_merge_with(self, other: Command) -> bool:
        """Focus commands can merge if within short time window"""
        return (isinstance(other, FocusCommand) and
                abs(other.timestamp - self.timestamp) < 0.1)  # 100ms window

    def merge_with(self, other: Command) -> Command:
        """Merge with another focus command"""
        if not isinstance(other, FocusCommand):
            raise ValueError("Cannot merge with non-focus command")

        # Create merged command with final target but original starting point
        merged = FocusCommand(other.pane_id, other.reason)
        merged.previous_focus = self.previous_focus
        return merged
```

---

## Qt Focus Integration

### Widget Focus Events

```python
class PaneWidget(QWidget):
    """Container widget for individual panes with focus handling"""

    focus_gained = Signal(str)  # pane_id
    focus_lost = Signal(str)    # pane_id

    def __init__(self, pane_id: PaneId, widget_id: WidgetId, content_widget: QWidget):
        super().__init__()
        self.pane_id = pane_id
        self.widget_id = widget_id
        self.content_widget = content_widget
        self.is_focused = False

        # Set up layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(content_widget)

        # Focus configuration
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocusProxy(content_widget)  # Forward focus to content

        # Monitor content widget focus
        content_widget.installEventFilter(self)

        # Initial styling
        self._update_focus_style()

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """Monitor focus events on content widget"""
        if obj == self.content_widget:
            if event.type() == QEvent.FocusIn:
                self._on_focus_gained()
            elif event.type() == QEvent.FocusOut:
                # Only emit if focus is moving outside this pane
                if not self._focus_staying_in_pane(event):
                    self._on_focus_lost()

        return super().eventFilter(obj, event)

    def focusInEvent(self, event: QFocusEvent):
        """Handle focus in on container"""
        super().focusInEvent(event)

        # Forward focus to content widget
        if self.content_widget and not self.content_widget.hasFocus():
            self.content_widget.setFocus(event.reason())

    def focusOutEvent(self, event: QFocusEvent):
        """Handle focus out on container"""
        super().focusOutEvent(event)

        # Only emit lost if focus is leaving this pane entirely
        if not self._focus_staying_in_pane(event):
            self._on_focus_lost()

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press to focus pane"""
        super().mousePressEvent(event)

        # Focus content widget on click
        if self.content_widget:
            self.content_widget.setFocus(Qt.MouseFocusReason)

    def _on_focus_gained(self):
        """Handle gaining focus"""
        if not self.is_focused:
            self.is_focused = True
            self._update_focus_style()
            self.focus_gained.emit(self.pane_id)

    def _on_focus_lost(self):
        """Handle losing focus"""
        if self.is_focused:
            self.is_focused = False
            self._update_focus_style()
            self.focus_lost.emit(self.pane_id)

    def _focus_staying_in_pane(self, event: QFocusEvent) -> bool:
        """Check if focus is staying within this pane"""
        if hasattr(event, 'nextFocusWidget'):
            next_widget = event.nextFocusWidget()
            return next_widget and self.isAncestorOf(next_widget)
        return False

    def _update_focus_style(self):
        """Update visual styling based on focus state"""
        if self.is_focused:
            self.setStyleSheet("""
                PaneWidget {
                    border: 2px solid palette(highlight);
                    border-radius: 4px;
                    background-color: palette(base);
                }
            """)
        else:
            self.setStyleSheet("""
                PaneWidget {
                    border: 1px solid palette(mid);
                    border-radius: 4px;
                    background-color: palette(window);
                }
            """)

    def set_focus_programmatically(self, reason: Qt.FocusReason = Qt.OtherFocusReason):
        """Set focus programmatically"""
        if self.content_widget:
            self.content_widget.setFocus(reason)
        else:
            self.setFocus(reason)

class FocusEventHandler:
    """Handles Qt focus events and translates to MultiSplit focus system"""

    def __init__(self, container: 'PaneContainer'):
        self.container = container
        self.focus_coordinator: Optional[FocusCoordinator] = None

        # Install global event filter to catch all focus events
        QApplication.instance().installEventFilter(self)

    def set_focus_coordinator(self, coordinator: FocusCoordinator):
        """Set focus coordinator reference"""
        self.focus_coordinator = coordinator

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """Global event filter for focus events"""
        if event.type() == QEvent.FocusIn:
            self._handle_global_focus_in(obj, event)
        elif event.type() == QEvent.KeyPress:
            if self._handle_navigation_keys(obj, event):
                return True

        return False

    def _handle_global_focus_in(self, widget: QObject, event: QFocusEvent):
        """Handle global focus in events"""
        # Find which pane this widget belongs to
        pane_id = self._find_pane_for_widget(widget)

        if pane_id and self.focus_coordinator:
            # Request focus change through coordinator
            self.focus_coordinator.focus_pane(pane_id, FocusReason.USER_INPUT)

    def _handle_navigation_keys(self, widget: QObject, event: QKeyEvent) -> bool:
        """Handle keyboard navigation keys"""
        if not self.focus_coordinator:
            return False

        # Check for spatial navigation keys
        key = event.key()
        modifiers = event.modifiers()

        if modifiers == Qt.AltModifier:
            if key == Qt.Key_Left:
                return self.focus_coordinator.focus_direction(Direction.LEFT)
            elif key == Qt.Key_Right:
                return self.focus_coordinator.focus_direction(Direction.RIGHT)
            elif key == Qt.Key_Up:
                return self.focus_coordinator.focus_direction(Direction.UP)
            elif key == Qt.Key_Down:
                return self.focus_coordinator.focus_direction(Direction.DOWN)

        # Check for tab navigation
        elif modifiers == Qt.NoModifier and key == Qt.Key_Tab:
            return self.focus_coordinator.focus_next()
        elif modifiers == Qt.ShiftModifier and key == Qt.Key_Tab:
            return self.focus_coordinator.focus_previous()

        return False

    def _find_pane_for_widget(self, widget: QObject) -> Optional[PaneId]:
        """Find which pane contains the given widget"""
        # Walk up parent hierarchy to find PaneWidget
        current = widget
        while current:
            if isinstance(current, PaneWidget):
                return current.pane_id
            current = current.parent()

        return None
```

---

## Focus Restoration and Persistence

### State Persistence

```python
class FocusStateManager:
    """Manages focus state persistence and restoration"""

    def __init__(self, focus_coordinator: FocusCoordinator):
        self.focus_coordinator = focus_coordinator
        self.saved_states: dict[str, FocusState] = {}
        self.restoration_policies = {
            'strict': self._restore_strict,
            'fallback': self._restore_with_fallback,
            'best_effort': self._restore_best_effort
        }

    def save_focus_state(self, state_id: str):
        """Save current focus state"""
        model = self.focus_coordinator.model

        state = FocusState(
            focused_pane_id=model.focused_pane_id,
            focus_order=self.focus_coordinator.chain_manager.get_focus_order(),
            spatial_neighbors=self.focus_coordinator.spatial_navigator.neighbor_cache.copy(),
            timestamp=time.time()
        )

        self.saved_states[state_id] = state

    def restore_focus_state(self, state_id: str,
                           policy: str = 'fallback') -> bool:
        """Restore saved focus state"""
        if state_id not in self.saved_states:
            return False

        state = self.saved_states[state_id]
        restore_func = self.restoration_policies.get(policy, self._restore_with_fallback)

        return restore_func(state)

    def _restore_strict(self, state: 'FocusState') -> bool:
        """Strict restoration - must match exactly"""
        if not state.focused_pane_id:
            return True  # No focus to restore

        model = self.focus_coordinator.model
        if state.focused_pane_id in model.pane_registry:
            return self.focus_coordinator.focus_pane(state.focused_pane_id)

        return False

    def _restore_with_fallback(self, state: 'FocusState') -> bool:
        """Restore with fallback to similar pane"""
        if not state.focused_pane_id:
            return True

        model = self.focus_coordinator.model

        # Try exact match first
        if state.focused_pane_id in model.pane_registry:
            return self.focus_coordinator.focus_pane(state.focused_pane_id)

        # Try to find a suitable fallback
        fallback_pane = self._find_fallback_pane(state)
        if fallback_pane:
            return self.focus_coordinator.focus_pane(fallback_pane)

        return False

    def _restore_best_effort(self, state: 'FocusState') -> bool:
        """Best effort restoration - always succeeds"""
        success = self._restore_with_fallback(state)

        if not success:
            # Last resort - focus first available pane
            order = self.focus_coordinator.chain_manager.get_focus_order()
            if order:
                return self.focus_coordinator.focus_pane(order[0])

        return True

    def _find_fallback_pane(self, state: 'FocusState') -> Optional[PaneId]:
        """Find suitable fallback pane"""
        model = self.focus_coordinator.model
        current_panes = set(model.pane_registry.keys())

        # Try panes that were in the original focus order
        for pane_id in state.focus_order:
            if pane_id in current_panes:
                return pane_id

        # Try any remaining pane
        if current_panes:
            return next(iter(current_panes))

        return None

class FocusState:
    """Snapshot of focus state for persistence"""

    def __init__(self, focused_pane_id: Optional[PaneId] = None,
                 focus_order: list[PaneId] = None,
                 spatial_neighbors: dict = None,
                 timestamp: float = None):
        self.focused_pane_id = focused_pane_id
        self.focus_order = focus_order or []
        self.spatial_neighbors = spatial_neighbors or {}
        self.timestamp = timestamp or time.time()

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            'focused_pane_id': self.focused_pane_id,
            'focus_order': self.focus_order,
            'spatial_neighbors': {
                str(pane_id): {
                    direction.value: neighbor_id
                    for direction, neighbor_id in neighbors.get_all_neighbors().items()
                }
                for pane_id, neighbors in self.spatial_neighbors.items()
            },
            'timestamp': self.timestamp
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'FocusState':
        """Create from dictionary"""
        # Reconstruct spatial neighbors
        spatial_neighbors = {}
        for pane_id_str, neighbor_data in data.get('spatial_neighbors', {}).items():
            pane_id = PaneId(pane_id_str)
            neighbors = SpatialNeighbors()

            for direction_str, neighbor_id in neighbor_data.items():
                direction = Direction(direction_str)
                neighbors.set_neighbor(direction, PaneId(neighbor_id))

            spatial_neighbors[pane_id] = neighbors

        return cls(
            focused_pane_id=PaneId(data['focused_pane_id']) if data.get('focused_pane_id') else None,
            focus_order=[PaneId(pid) for pid in data.get('focus_order', [])],
            spatial_neighbors=spatial_neighbors,
            timestamp=data.get('timestamp', time.time())
        )
```

---

## Focus Trap Management

### Modal Focus Scenarios

```python
class FocusTrapManager:
    """Manages focus trapping for modal scenarios"""

    def __init__(self, focus_coordinator: FocusCoordinator):
        self.coordinator = focus_coordinator
        self.trap_stack: list[FocusTrap] = []
        self.original_focus: Optional[PaneId] = None

    def create_trap(self, panes: list[PaneId],
                   restore_on_exit: bool = True) -> FocusTrap:
        """Create a focus trap for specified panes"""
        trap = FocusTrap(
            panes=panes,
            restore_focus=restore_on_exit,
            original_focus=self.coordinator.model.focused_pane_id
        )

        # Save current focus if needed
        if restore_on_exit and not self.original_focus:
            self.original_focus = self.coordinator.model.focused_pane_id

        self.trap_stack.append(trap)
        self._activate_trap(trap)
        return trap

    def release_trap(self, trap: FocusTrap):
        """Release a focus trap"""
        if trap in self.trap_stack:
            self.trap_stack.remove(trap)

            if trap.restore_focus and trap.original_focus:
                self.coordinator.focus_pane(trap.original_focus)

            # Activate previous trap if exists
            if self.trap_stack:
                self._activate_trap(self.trap_stack[-1])

    def _activate_trap(self, trap: FocusTrap):
        """Activate focus trap constraints"""
        # Limit focus navigation to trap panes
        self.coordinator.navigation_constraints = trap.panes

        # Focus first pane in trap if current is outside
        current = self.coordinator.model.focused_pane_id
        if current not in trap.panes and trap.panes:
            self.coordinator.focus_pane(trap.panes[0])

class FocusTrap:
    """Represents a focus trap configuration"""

    def __init__(self, panes: list[PaneId],
                 restore_focus: bool = True,
                 original_focus: Optional[PaneId] = None):
        self.panes = panes
        self.restore_focus = restore_focus
        self.original_focus = original_focus
        self.active = True

    def contains(self, pane_id: PaneId) -> bool:
        """Check if pane is within trap"""
        return pane_id in self.panes
```

### Focus Restoration After Errors

```python
class ErrorRecoveryFocus:
    """Handles focus recovery after errors"""

    def __init__(self, coordinator: FocusCoordinator):
        self.coordinator = coordinator
        self.checkpoint_stack: list[FocusCheckpoint] = []
        self.max_checkpoints = 10

    def create_checkpoint(self):
        """Create focus state checkpoint before risky operation"""
        checkpoint = FocusCheckpoint(
            focus_state=self.coordinator.save_state(),
            timestamp=time.time()
        )

        self.checkpoint_stack.append(checkpoint)
        if len(self.checkpoint_stack) > self.max_checkpoints:
            self.checkpoint_stack.pop(0)

    def restore_from_error(self, error: Exception) -> bool:
        """Restore focus after error"""
        if not self.checkpoint_stack:
            return self._fallback_recovery()

        # Try checkpoints from newest to oldest
        while self.checkpoint_stack:
            checkpoint = self.checkpoint_stack.pop()
            if self._try_restore_checkpoint(checkpoint):
                return True

        return self._fallback_recovery()

    def _try_restore_checkpoint(self, checkpoint: FocusCheckpoint) -> bool:
        """Attempt to restore from checkpoint"""
        try:
            self.coordinator.restore_state(checkpoint.focus_state)
            return True
        except:
            return False

    def _fallback_recovery(self) -> bool:
        """Last resort focus recovery"""
        # Find any valid pane to focus
        if self.coordinator.model.pane_registry:
            first_pane = next(iter(self.coordinator.model.pane_registry.keys()))
            return self.coordinator.focus_pane(first_pane)
        return False
```

---

## Performance Optimization

### Focus Operation Complexity

| Operation | Time Complexity | Space Complexity | Cache Strategy |
|-----------|----------------|------------------|----------------|
| Focus Next/Prev | O(1) | O(n) | Focus order cache |
| Spatial Navigation | O(log n) | O(n) | Spatial index |
| Find Pane by Widget | O(1) | O(n) | Widget-to-pane map |
| Focus Chain Rebuild | O(n) | O(n) | Invalidate on change |
| Focus History | O(1) | O(h) | Limited stack size |
| Trap Management | O(1) | O(t) | Active trap cache |

Where: n = number of panes, h = history depth, t = trap depth

### Focus Cache Management

```python
class FocusCacheOptimizer:
    """Optimizes focus operations through caching"""

    def __init__(self):
        self.order_cache: Optional[list[PaneId]] = None
        self.spatial_cache: dict[PaneId, SpatialNeighbors] = {}
        self.path_cache: dict[tuple[PaneId, PaneId], list[PaneId]] = {}
        self.cache_hits = 0
        self.cache_misses = 0

    def get_cached_order(self) -> Optional[list[PaneId]]:
        """Get cached focus order with statistics"""
        if self.order_cache is not None:
            self.cache_hits += 1
            return self.order_cache.copy()
        self.cache_misses += 1
        return None

    def cache_spatial_neighbors(self, pane_id: PaneId,
                              neighbors: SpatialNeighbors):
        """Cache spatial relationships"""
        self.spatial_cache[pane_id] = neighbors

    def get_cached_path(self, from_pane: PaneId,
                       to_pane: PaneId) -> Optional[list[PaneId]]:
        """Get cached navigation path"""
        key = (from_pane, to_pane)
        if key in self.path_cache:
            self.cache_hits += 1
            return self.path_cache[key].copy()
        self.cache_misses += 1
        return None

    def invalidate_all(self):
        """Clear all caches"""
        self.order_cache = None
        self.spatial_cache.clear()
        self.path_cache.clear()

    def get_cache_stats(self) -> dict:
        """Get cache performance statistics"""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total_requests if total_requests > 0 else 0

        return {
            'hit_rate': hit_rate,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'order_cache_size': len(self.order_cache) if self.order_cache else 0,
            'spatial_cache_size': len(self.spatial_cache),
            'path_cache_size': len(self.path_cache)
        }
```

---

## Common Pitfalls

### ❌ Direct Model Focus Mutation
```python
# DON'T: Mutate focus directly
model.focused_pane_id = "pane-123"

# DO: Use focus coordinator
focus_coordinator.focus_pane("pane-123")
```

### ❌ Ignoring Focus Event Recursion
```python
# DON'T: Allow focus event loops
def on_focus_changed(pane_id):
    self.view.set_focus(pane_id)  # May trigger another event!

# DO: Use transition guards
def on_focus_changed(pane_id):
    if not self.focus_transition_in_progress:
        self.focus_transition_in_progress = True
        self.view.set_focus(pane_id)
        self.focus_transition_in_progress = False
```

### ❌ Inefficient Spatial Calculation
```python
# DON'T: Recalculate on every navigation
def find_neighbor(direction):
    for pane in all_panes:  # O(n) every time!
        if is_neighbor(current, pane, direction):
            return pane

# DO: Cache spatial relationships
def find_neighbor(direction):
    if not self.cache_valid:
        self._rebuild_spatial_cache()
    return self.neighbor_cache[current][direction]
```

### ❌ Focus State Inconsistency
```python
# DON'T: Allow model and view focus to diverge
model.focused_pane_id = "pane-1"
view.focused_widget = widget_for_pane_2  # Inconsistent!

# DO: Maintain synchronization
focus_coordinator.focus_pane("pane-1")  # Updates both
```

### ❌ Missing Focus Restoration
```python
# DON'T: Lose focus on layout changes
def restore_layout(layout):
    self.clear_all_panes()
    self.create_panes(layout)
    # Focus is lost!

# DO: Preserve and restore focus
def restore_layout(layout):
    focus_state.save_focus_state("pre_restore")
    self.clear_all_panes()
    self.create_panes(layout)
    focus_state.restore_focus_state("pre_restore")
```

---

## Quick Reference

### Focus Movement Types
| Type | Method | Navigation Logic |
|------|--------|------------------|
| Sequential | `focus_next()` | Tree traversal order |
| Spatial | `focus_direction()` | Geometric adjacency |
| Direct | `focus_pane()` | Explicit pane target |
| Fallback | Auto-restore | Best available match |

### Spatial Navigation Scoring
| Factor | Weight | Purpose |
|--------|--------|---------|
| Overlap | High | Perpendicular alignment |
| Distance | Medium | Proximity preference |
| Direction | Critical | Must be in correct direction |
| Visibility | High | Skip hidden panes |

### Focus Event Flow
| Source | Handler | Target | Signal |
|--------|---------|--------|--------|
| Qt Widget | `eventFilter()` | Focus Coordinator | `focus_requested` |
| Model | Signal bridge | View | `focus_changed` |
| Keyboard | Key handler | Focus Coordinator | Navigation command |
| Application | Public API | Focus Coordinator | Direct focus |

### State Persistence
| Policy | Behavior | Use Case |
|--------|----------|----------|
| Strict | Exact match only | Critical applications |
| Fallback | Find similar pane | Most applications |
| Best Effort | Always focus something | User-friendly |

### Navigation Performance
| Operation | Complexity | Optimization |
|-----------|------------|-------------|
| Sequential navigation | O(1) | Cached focus order |
| Spatial navigation | O(1) | Cached neighbor map |
| Cache rebuild | O(n) | Only on structure change |
| Geometry lookup | O(1) | View provides cached rects |

---

## Validation Checklist

- ✅ Focus state synchronized across all layers
- ✅ Spatial navigation cache invalidated on structure changes
- ✅ Focus events don't create infinite loops
- ✅ Focus restoration handles missing panes gracefully
- ✅ Qt focus proxy correctly forwards to content widgets
- ✅ Keyboard navigation works in all directions
- ✅ Focus commands are properly undoable
- ✅ Focus order respects user-defined hints
- ✅ Spatial scoring algorithm handles edge cases
- ✅ Performance optimized with appropriate caching

## Related Documents

- **[Model Design](model-design.md)** - Model focus state management
- **[Controller Design](controller-design.md)** - Focus commands and undo
- **[View Design](view-design.md)** - Qt widget focus integration
- **[MVC Architecture](../02-architecture/mvc-architecture.md)** - Cross-layer coordination
- **[MVP Plan](../03-implementation/mvp-plan.md)** - Focus implementation phases
- **[Widget Provider](../02-architecture/widget-provider.md)** - Widget focus handling
- **[Tree Structure](../02-architecture/tree-structure.md)** - Focus traversal patterns
- **[Development Rules](../03-implementation/development-rules.md)** - Focus command patterns
- **[Focus Management](../../focus-management-DESIGN.md)** - Original focus design

---

The focus management design provides intuitive navigation and robust state management while maintaining the strict MVC separation that makes MultiSplit reliable and testable.