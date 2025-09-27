# Phase 2 Implementation Tasks - Essential Interactions

## Overview

Phase 2 adds essential user interactions to the MultiSplit widget: focus management, keyboard navigation, divider dragging, and persistence. These features make the widget fully interactive and production-ready.

## Prerequisites

- ✅ Phase 0 Complete (foundations)
- ✅ Phase 1 Complete (working core with 77 tests passing)
- ✅ Basic split/remove operations working
- ✅ Widget provider pattern functional

## Task Structure

Each task includes:
- **Task ID**: Unique identifier (P2.X.Y)
- **Title**: Clear description
- **Dependencies**: Required prior tasks
- **Action**: CREATE/MODIFY/ENHANCE
- **File**: Target file path
- **Implementation**: Complete code
- **Tests**: Test cases to write first (TDD)
- **Validation**: Success criteria

---

## P2.1: Focus Management System

### Task P2.1.1: Add Focus Tracking to Model
**Title**: Add focus state tracking to PaneModel
**Dependencies**: Phase 1 complete
**Action**: MODIFY
**File**: `src/vfwidgets_multisplit/core/model.py`

**Implementation**:
Add to PaneModel class:
```python
def set_focused_pane(self, pane_id: Optional[PaneId]) -> bool:
    """Set the focused pane.

    Args:
        pane_id: ID of pane to focus, or None to clear focus

    Returns:
        True if focus changed, False otherwise
    """
    if pane_id and pane_id not in self._pane_registry:
        return False

    if self.focused_pane_id != pane_id:
        old_id = self.focused_pane_id
        self.focused_pane_id = pane_id
        self.signals.focus_changed.emit(old_id, pane_id)
        return True
    return False

def get_focused_pane(self) -> Optional[PaneNode]:
    """Get the currently focused pane node."""
    if self.focused_pane_id:
        return self._pane_registry.get(self.focused_pane_id)
    return None

def focus_first_pane(self) -> bool:
    """Focus the first available pane."""
    pane_ids = self.get_all_pane_ids()
    if pane_ids:
        return self.set_focused_pane(pane_ids[0])
    return False
```

**Tests** (`tests/test_focus.py`):
```python
import pytest
from vfwidgets_multisplit.core.model import PaneModel
from vfwidgets_multisplit.core.nodes import LeafNode
from vfwidgets_multisplit.core.types import PaneId, WidgetId

def test_focus_tracking():
    """Test focus state tracking in model."""
    model = PaneModel()
    leaf1 = LeafNode(PaneId("p1"), WidgetId("w1"))
    leaf2 = LeafNode(PaneId("p2"), WidgetId("w2"))

    from vfwidgets_multisplit.core.nodes import SplitNode
    from vfwidgets_multisplit.core.types import NodeId, Orientation

    model.root = SplitNode(
        NodeId("split1"),
        Orientation.HORIZONTAL,
        [leaf1, leaf2],
        [0.5, 0.5]
    )
    model._rebuild_registry()

    # Test setting focus
    assert model.set_focused_pane(PaneId("p1"))
    assert model.focused_pane_id == PaneId("p1")
    assert model.get_focused_pane() == leaf1

    # Test changing focus
    assert model.set_focused_pane(PaneId("p2"))
    assert model.focused_pane_id == PaneId("p2")

    # Test no change
    assert not model.set_focused_pane(PaneId("p2"))

    # Test invalid pane
    assert not model.set_focused_pane(PaneId("invalid"))

    # Test clearing focus
    assert model.set_focused_pane(None)
    assert model.focused_pane_id is None

def test_focus_first_pane():
    """Test focusing first available pane."""
    model = PaneModel()
    assert not model.focus_first_pane()  # No panes

    model.root = LeafNode(PaneId("p1"), WidgetId("w1"))
    model._rebuild_registry()

    assert model.focus_first_pane()
    assert model.focused_pane_id == PaneId("p1")
```

---

### Task P2.1.2: Create Focus Manager
**Title**: Create focus chain and navigation manager
**Dependencies**: P2.1.1
**Action**: CREATE
**File**: `src/vfwidgets_multisplit/core/focus.py`

**Implementation**:
```python
"""Focus management for MultiSplit widget.

Handles focus chain calculation and navigation.
"""

from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass, field

from .types import PaneId, Direction
from .model import PaneModel
from .nodes import PaneNode, LeafNode, SplitNode
from .visitor import NodeVisitor


@dataclass
class FocusManager:
    """Manages focus chain and navigation."""

    model: PaneModel
    _focus_order_cache: Optional[List[PaneId]] = field(default=None, init=False)
    _cache_valid: bool = field(default=False, init=False)

    def __post_init__(self):
        """Connect to model signals."""
        self.model.signals.structure_changed.connect(self._invalidate_cache)

    def _invalidate_cache(self):
        """Invalidate cached focus order."""
        self._cache_valid = False
        self._focus_order_cache = None

    def get_focus_order(self) -> List[PaneId]:
        """Get panes in focus traversal order.

        Returns:
            List of pane IDs in tab order
        """
        if not self._cache_valid or self._focus_order_cache is None:
            self._rebuild_focus_order()
        return self._focus_order_cache.copy() if self._focus_order_cache else []

    def _rebuild_focus_order(self):
        """Rebuild focus order from tree structure."""
        if not self.model.root:
            self._focus_order_cache = []
            self._cache_valid = True
            return

        # Collect panes in tree order
        visitor = FocusOrderVisitor()
        self.model.root.accept(visitor)
        self._focus_order_cache = visitor.pane_order
        self._cache_valid = True

    def get_next_pane(self, current: Optional[PaneId] = None) -> Optional[PaneId]:
        """Get next pane in focus order.

        Args:
            current: Current focused pane, or None to get first

        Returns:
            Next pane ID, or None if no panes
        """
        order = self.get_focus_order()
        if not order:
            return None

        if current is None or current not in order:
            return order[0]

        current_index = order.index(current)
        next_index = (current_index + 1) % len(order)
        return order[next_index]

    def get_previous_pane(self, current: Optional[PaneId] = None) -> Optional[PaneId]:
        """Get previous pane in focus order.

        Args:
            current: Current focused pane, or None to get last

        Returns:
            Previous pane ID, or None if no panes
        """
        order = self.get_focus_order()
        if not order:
            return None

        if current is None or current not in order:
            return order[-1] if order else None

        current_index = order.index(current)
        prev_index = (current_index - 1) % len(order)
        return order[prev_index]

    def navigate(self, direction: Direction) -> Optional[PaneId]:
        """Navigate focus in a direction.

        Args:
            direction: Direction to move focus

        Returns:
            Pane ID to focus, or None if can't navigate
        """
        current = self.model.focused_pane_id
        if not current:
            return self.get_next_pane()

        # For now, use simple tab order for left/right
        # TODO: Implement spatial navigation
        if direction in (Direction.LEFT, Direction.UP):
            return self.get_previous_pane(current)
        else:
            return self.get_next_pane(current)


class FocusOrderVisitor(NodeVisitor):
    """Visitor that collects panes in focus order."""

    def __init__(self):
        """Initialize visitor."""
        self.pane_order: List[PaneId] = []

    def visit_leaf(self, node: LeafNode):
        """Add leaf to focus order."""
        self.pane_order.append(node.pane_id)

    def visit_split(self, node: SplitNode):
        """Traverse children in order."""
        # Left-to-right, top-to-bottom traversal
        for child in node.children:
            child.accept(self)
```

**Tests**:
```python
def test_focus_manager():
    """Test focus chain management."""
    from vfwidgets_multisplit.core.focus import FocusManager
    from vfwidgets_multisplit.core.nodes import SplitNode
    from vfwidgets_multisplit.core.types import NodeId, Orientation

    model = PaneModel()
    focus_mgr = FocusManager(model)

    # Empty tree
    assert focus_mgr.get_focus_order() == []
    assert focus_mgr.get_next_pane() is None

    # Build tree
    leaf1 = LeafNode(PaneId("p1"), WidgetId("w1"))
    leaf2 = LeafNode(PaneId("p2"), WidgetId("w2"))
    leaf3 = LeafNode(PaneId("p3"), WidgetId("w3"))

    model.root = SplitNode(
        NodeId("split1"),
        Orientation.HORIZONTAL,
        [leaf1, SplitNode(
            NodeId("split2"),
            Orientation.VERTICAL,
            [leaf2, leaf3],
            [0.5, 0.5]
        )],
        [0.5, 0.5]
    )
    model._rebuild_registry()

    # Check order
    order = focus_mgr.get_focus_order()
    assert order == [PaneId("p1"), PaneId("p2"), PaneId("p3")]

    # Test navigation
    assert focus_mgr.get_next_pane(PaneId("p1")) == PaneId("p2")
    assert focus_mgr.get_next_pane(PaneId("p3")) == PaneId("p1")  # Wrap
    assert focus_mgr.get_previous_pane(PaneId("p1")) == PaneId("p3")  # Wrap

    # Test with no current
    assert focus_mgr.get_next_pane() == PaneId("p1")
    assert focus_mgr.get_previous_pane() == PaneId("p3")
```

---

### Task P2.1.3: Add Focus Commands
**Title**: Create focus navigation commands
**Dependencies**: P2.1.2
**Action**: MODIFY
**File**: `src/vfwidgets_multisplit/controller/commands.py`

**Implementation**:
Add to commands.py:
```python
@dataclass
class FocusPaneCommand(Command):
    """Command to focus a pane."""

    pane_id: PaneId

    def __init__(self, model: PaneModel, pane_id: PaneId):
        """Initialize focus command."""
        super().__init__(model)
        self.pane_id = pane_id
        self._previous_focus: Optional[PaneId] = None

    def execute(self) -> bool:
        """Focus the pane."""
        if self.executed:
            return False

        self._previous_focus = self.model.focused_pane_id
        success = self.model.set_focused_pane(self.pane_id)

        if success:
            self.executed = True

        return success

    def undo(self) -> bool:
        """Restore previous focus."""
        if not self.can_undo():
            return False

        self.model.set_focused_pane(self._previous_focus)
        self.executed = False
        return True

    def description(self) -> str:
        """Get command description."""
        return f"Focus pane {self.pane_id}"


@dataclass
class NavigateFocusCommand(Command):
    """Command to navigate focus in a direction."""

    direction: Direction

    def __init__(self, model: PaneModel, direction: Direction):
        """Initialize navigation command."""
        super().__init__(model)
        self.direction = direction
        self._previous_focus: Optional[PaneId] = None
        self._new_focus: Optional[PaneId] = None

    def execute(self) -> bool:
        """Navigate focus."""
        if self.executed:
            return False

        from ..core.focus import FocusManager
        focus_mgr = FocusManager(self.model)

        self._previous_focus = self.model.focused_pane_id
        self._new_focus = focus_mgr.navigate(self.direction)

        if self._new_focus:
            self.model.set_focused_pane(self._new_focus)
            self.executed = True
            return True

        return False

    def undo(self) -> bool:
        """Restore previous focus."""
        if not self.can_undo():
            return False

        self.model.set_focused_pane(self._previous_focus)
        self.executed = False
        return True

    def description(self) -> str:
        """Get command description."""
        return f"Navigate focus {self.direction.value}"
```

---

### Task P2.1.4: Add Focus Visualization
**Title**: Add visual focus indicators to container
**Dependencies**: P2.1.3
**Action**: MODIFY
**File**: `src/vfwidgets_multisplit/view/container.py`

**Implementation**:
Add to PaneContainer class:
```python
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
    self._focus_frames: Dict[PaneId, QWidget] = {}  # NEW

    # Connect model signals
    self.model.signals.structure_changed.connect(self._on_structure_changed)
    self.model.signals.focus_changed.connect(self._on_focus_changed)  # NEW

    # Initial render
    self._update_view()

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
    """Create container with focus frame for pane widget."""
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

    # Connect click to focus
    frame.mousePressEvent = lambda e: self._on_pane_clicked(pane_id, e)

    return frame

def _on_pane_clicked(self, pane_id: PaneId, event):
    """Handle pane click for focus."""
    from PySide6.QtCore import Qt

    if event.button() == Qt.MouseButton.LeftButton:
        # Request focus through controller
        self.pane_focused.emit(str(pane_id))

# Modify _build_widget_tree to use containers
def _build_widget_tree(self, node: PaneNode) -> Optional[QWidget]:
    """Build Qt widget tree from node tree."""
    if isinstance(node, LeafNode):
        # Get or create widget
        if node.pane_id in self._widgets:
            widget = self._widgets[node.pane_id]
        else:
            # Request widget from provider
            if self.provider:
                widget = self.provider.provide_widget(
                    node.widget_id, node.pane_id
                )
                self._widgets[node.pane_id] = widget
            else:
                # Emit signal for widget
                self.widget_needed.emit(
                    str(node.widget_id), str(node.pane_id)
                )
                # Create placeholder
                from PySide6.QtWidgets import QLabel
                widget = QLabel(f"Pane: {node.pane_id}")
                self._widgets[node.pane_id] = widget

        # Wrap in focus container
        return self._create_pane_container(node.pane_id, widget)

    # Rest of method unchanged...
```

---

## P2.2: Keyboard Navigation

### Task P2.2.1: Add Keyboard Event Handler
**Title**: Add keyboard navigation to container
**Dependencies**: P2.1.4
**Action**: MODIFY
**File**: `src/vfwidgets_multisplit/view/container.py`

**Implementation**:
Add to PaneContainer class:
```python
def keyPressEvent(self, event):
    """Handle keyboard events for navigation."""
    from PySide6.QtCore import Qt
    from ..core.types import Direction

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

def _navigate_focus_direction(self, direction: 'Direction'):
    """Navigate focus in a direction."""
    from ..core.focus import FocusManager

    focus_mgr = FocusManager(self.model)
    target_pane = focus_mgr.navigate(direction)

    if target_pane:
        self.model.set_focused_pane(target_pane)
```

**Tests**:
```python
def test_keyboard_navigation(qtbot):
    """Test keyboard navigation."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    model = PaneModel()
    container = PaneContainer(model)
    qtbot.addWidget(container)

    # Add panes
    leaf1 = LeafNode(PaneId("p1"), WidgetId("w1"))
    leaf2 = LeafNode(PaneId("p2"), WidgetId("w2"))

    from vfwidgets_multisplit.core.nodes import SplitNode
    from vfwidgets_multisplit.core.types import NodeId, Orientation

    model.root = SplitNode(
        NodeId("split1"),
        Orientation.HORIZONTAL,
        [leaf1, leaf2],
        [0.5, 0.5]
    )
    model._rebuild_registry()
    model.set_focused_pane(PaneId("p1"))

    # Test Tab navigation
    QTest.keyClick(container, Qt.Key.Key_Tab)
    assert model.focused_pane_id == PaneId("p2")

    # Test Shift+Tab
    QTest.keyClick(container, Qt.Key.Key_Tab, Qt.KeyboardModifier.ShiftModifier)
    assert model.focused_pane_id == PaneId("p1")

    # Test Alt+Arrow
    QTest.keyClick(container, Qt.Key.Key_Right, Qt.KeyboardModifier.AltModifier)
    assert model.focused_pane_id == PaneId("p2")
```

---

## P2.3: Divider Dragging

### Task P2.3.1: Create SetRatiosCommand
**Title**: Create command to update split ratios
**Dependencies**: P2.2.1
**Action**: MODIFY
**File**: `src/vfwidgets_multisplit/controller/commands.py`

**Implementation**:
Add to commands.py:
```python
@dataclass
class SetRatiosCommand(Command):
    """Command to set split ratios."""

    node_id: NodeId
    ratios: List[float]

    def __init__(self, model: PaneModel, node_id: NodeId, ratios: List[float]):
        """Initialize set ratios command."""
        super().__init__(model)
        self.node_id = node_id
        self.ratios = ratios
        self._old_ratios: Optional[List[float]] = None

    def execute(self) -> bool:
        """Set the ratios."""
        if self.executed:
            return False

        # Find split node
        from ..core.tree_utils import find_split_by_id
        split_node = find_split_by_id(self.model.root, self.node_id)

        if not split_node:
            return False

        # Validate ratios
        from ..core.tree_utils import validate_ratios
        if not validate_ratios(self.ratios):
            return False

        if len(self.ratios) != len(split_node.children):
            return False

        # Save old ratios
        self._old_ratios = split_node.ratios.copy()

        # Set new ratios
        split_node.ratios = self.ratios.copy()

        # Emit signal
        self.model.signals.structure_changed.emit()

        self.executed = True
        return True

    def undo(self) -> bool:
        """Restore old ratios."""
        if not self.can_undo():
            return False

        from ..core.tree_utils import find_split_by_id
        split_node = find_split_by_id(self.model.root, self.node_id)

        if split_node and self._old_ratios:
            split_node.ratios = self._old_ratios.copy()
            self.model.signals.structure_changed.emit()
            self.executed = False
            return True

        return False

    def description(self) -> str:
        """Get command description."""
        return f"Adjust split ratios"
```

Also add helper function to tree_utils.py:
```python
def find_split_by_id(root: PaneNode, node_id: NodeId) -> Optional[SplitNode]:
    """Find split node by ID."""
    if isinstance(root, SplitNode):
        if root.node_id == node_id:
            return root
        for child in root.children:
            result = find_split_by_id(child, node_id)
            if result:
                return result
    return None
```

---

### Task P2.3.2: Add Splitter Tracking
**Title**: Track splitters and handle drag events
**Dependencies**: P2.3.1
**Action**: MODIFY
**File**: `src/vfwidgets_multisplit/view/container.py`

**Implementation**:
Modify _build_widget_tree in container.py:
```python
def _build_widget_tree(self, node: PaneNode) -> Optional[QWidget]:
    """Build Qt widget tree from node tree."""
    if isinstance(node, LeafNode):
        # ... existing leaf handling ...

    elif isinstance(node, SplitNode):
        # Create splitter
        orientation = (Qt.Orientation.Horizontal
                     if node.orientation.value == "horizontal"
                     else Qt.Orientation.Vertical)

        splitter = QSplitter(orientation)
        splitter.setChildrenCollapsible(False)  # Prevent collapse

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

def _on_splitter_moved(self, node_id: NodeId, splitter: QSplitter):
    """Handle splitter drag."""
    # Calculate new ratios from sizes
    sizes = splitter.sizes()
    total = sum(sizes)

    if total > 0:
        ratios = [s / total for s in sizes]

        # Emit signal for ratio change
        self.splitter_moved.emit(str(node_id), ratios)

# Add signal to class definition
splitter_moved = Signal(str, list)  # node_id, new_ratios
```

---

## P2.4: Persistence System

### Task P2.4.1: Add Serialization Methods
**Title**: Enhance model serialization with metadata
**Dependencies**: P2.3.2
**Action**: MODIFY
**File**: `src/vfwidgets_multisplit/core/model.py`

**Implementation**:
Already implemented in Phase 1! The to_dict() and from_dict() methods handle serialization.
We just need to add version and metadata:

```python
def to_dict(self, include_metadata: bool = True) -> Dict[str, Any]:
    """Serialize model to dictionary.

    Args:
        include_metadata: Whether to include metadata

    Returns:
        Serialized model state
    """
    # ... existing node_to_dict code ...

    data = {
        'root': node_to_dict(self.root) if self.root else None,
        'focused_pane_id': str(self.focused_pane_id) if self.focused_pane_id else None
    }

    if include_metadata:
        data['version'] = '1.0.0'
        data['widget_version'] = '0.1.0'

    return data

@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'PaneModel':
    """Deserialize model from dictionary.

    Args:
        data: Serialized model data

    Returns:
        Restored model instance
    """
    # Check version compatibility
    version = data.get('version', '1.0.0')
    if version.split('.')[0] != '1':
        raise ValueError(f"Incompatible version: {version}")

    # ... existing deserialization code ...
```

---

### Task P2.4.2: Create Session Manager
**Title**: Create session save/load manager
**Dependencies**: P2.4.1
**Action**: CREATE
**File**: `src/vfwidgets_multisplit/core/session.py`

**Implementation**:
```python
"""Session management for MultiSplit widget.

Handles saving and loading layout state.
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any

from .model import PaneModel


class SessionManager:
    """Manages session persistence."""

    def __init__(self, model: PaneModel):
        """Initialize session manager.

        Args:
            model: Model to manage
        """
        self.model = model

    def save_to_file(self, filepath: Path) -> bool:
        """Save session to file.

        Args:
            filepath: Path to save file

        Returns:
            True if successful
        """
        try:
            data = self.model.to_dict(include_metadata=True)

            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)

            return True
        except Exception as e:
            print(f"Failed to save session: {e}")
            return False

    def load_from_file(self, filepath: Path) -> bool:
        """Load session from file.

        Args:
            filepath: Path to load file

        Returns:
            True if successful
        """
        try:
            if not filepath.exists():
                return False

            with open(filepath, 'r') as f:
                data = json.load(f)

            # Create new model from data
            new_model = PaneModel.from_dict(data)

            # Update our model
            self.model.root = new_model.root
            self.model.focused_pane_id = new_model.focused_pane_id
            self.model._rebuild_registry()

            # Emit change signal
            self.model.signals.structure_changed.emit()

            return True
        except Exception as e:
            print(f"Failed to load session: {e}")
            return False

    def save_to_string(self) -> str:
        """Save session to JSON string.

        Returns:
            JSON string representation
        """
        data = self.model.to_dict(include_metadata=True)
        return json.dumps(data, indent=2)

    def load_from_string(self, json_str: str) -> bool:
        """Load session from JSON string.

        Args:
            json_str: JSON string to load

        Returns:
            True if successful
        """
        try:
            data = json.loads(json_str)
            new_model = PaneModel.from_dict(data)

            self.model.root = new_model.root
            self.model.focused_pane_id = new_model.focused_pane_id
            self.model._rebuild_registry()

            self.model.signals.structure_changed.emit()

            return True
        except Exception as e:
            print(f"Failed to load from string: {e}")
            return False
```

**Tests**:
```python
def test_session_manager():
    """Test session save/load."""
    from vfwidgets_multisplit.core.session import SessionManager
    from pathlib import Path
    import tempfile

    # Create model with structure
    model = PaneModel()
    leaf1 = LeafNode(PaneId("p1"), WidgetId("editor:main.py"))
    leaf2 = LeafNode(PaneId("p2"), WidgetId("terminal:1"))

    from vfwidgets_multisplit.core.nodes import SplitNode
    from vfwidgets_multisplit.core.types import NodeId, Orientation

    model.root = SplitNode(
        NodeId("split1"),
        Orientation.VERTICAL,
        [leaf1, leaf2],
        [0.7, 0.3]
    )
    model._rebuild_registry()
    model.set_focused_pane(PaneId("p1"))

    session = SessionManager(model)

    # Test string serialization
    json_str = session.save_to_string()
    assert "editor:main.py" in json_str
    assert "0.7" in json_str

    # Test file save/load
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
        filepath = Path(f.name)

    try:
        # Save
        assert session.save_to_file(filepath)
        assert filepath.exists()

        # Clear model
        model.root = None
        model._rebuild_registry()

        # Load
        assert session.load_from_file(filepath)
        assert isinstance(model.root, SplitNode)
        assert len(model.get_all_pane_ids()) == 2
        assert model.focused_pane_id == PaneId("p1")

    finally:
        filepath.unlink()  # Clean up
```

---

## Validation Criteria

### Phase 2 Complete When:

1. ✅ Focus tracking and visualization works
2. ✅ Keyboard navigation (Tab, Shift+Tab, Alt+Arrows)
3. ✅ Focus follows mouse clicks
4. ✅ Splitter dragging updates ratios
5. ✅ Session save/load preserves state
6. ✅ All Phase 2 tests passing (15+ new tests)
7. ✅ No regressions in Phase 0/1 tests

### Integration Test:

```python
def test_phase2_integration(qtbot):
    """Test complete Phase 2 functionality."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    from vfwidgets_multisplit.core.session import SessionManager

    # Create and populate model
    model = PaneModel()
    controller = PaneController(model)
    container = PaneContainer(model)
    qtbot.addWidget(container)

    # Build structure
    controller.split_pane(
        PaneId("p1"),
        WidgetId("editor:main.py"),
        WherePosition.LEFT
    )
    controller.split_pane(
        PaneId("p2"),
        WidgetId("terminal:1"),
        WherePosition.BOTTOM
    )

    # Test focus
    model.set_focused_pane(PaneId("p1"))
    assert model.focused_pane_id == PaneId("p1")

    # Test keyboard navigation
    QTest.keyClick(container, Qt.Key.Key_Tab)
    assert model.focused_pane_id == PaneId("p2")

    # Test session persistence
    session = SessionManager(model)
    saved = session.save_to_string()

    model.root = None
    model._rebuild_registry()

    session.load_from_string(saved)
    assert len(model.get_all_pane_ids()) == 3
```

---

## Task Execution Order

1. **P2.1: Focus Management**
   - P2.1.1 → P2.1.2 → P2.1.3 → P2.1.4

2. **P2.2: Keyboard Navigation**
   - P2.2.1 (builds on P2.1)

3. **P2.3: Divider Dragging**
   - P2.3.1 → P2.3.2

4. **P2.4: Persistence**
   - P2.4.1 → P2.4.2

Each task should be implemented using TDD:
1. Write tests first
2. Implement functionality
3. Verify tests pass
4. Move to next task

---

## Success Metrics

- All 15+ Phase 2 tests passing
- Total 90+ tests passing (Phase 0+1+2)
- Focus clearly visible and navigable
- Keyboard shortcuts intuitive
- Splitter dragging smooth
- Session persistence reliable
- No Qt imports in Model layer maintained
- All interactions feel responsive