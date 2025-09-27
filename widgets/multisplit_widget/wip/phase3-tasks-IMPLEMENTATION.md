# Phase 3 Implementation Tasks - Polish & Completion

## Overview

Phase 3 adds the final polish to make the MultiSplit widget production-ready. This includes visual polish, validation system, size constraints, and complete integration testing to ensure MVP completion.

## Prerequisites

- ✅ Phase 0 Complete (foundations - 38 tests)
- ✅ Phase 1 Complete (working core - 77 tests total)
- ✅ Phase 2 Complete (interactions - 89 tests total)
- ✅ Full MVC separation maintained
- ✅ Widget provider pattern working

## Task Structure

Each task includes:
- **Task ID**: Unique identifier (P3.X.Y)
- **Title**: Clear description
- **Dependencies**: Required prior tasks
- **Action**: CREATE/MODIFY/ENHANCE
- **File**: Target file path
- **Implementation**: Complete code
- **Tests**: Test cases to write first (TDD)
- **Validation**: Success criteria

---

## P3.1: Visual Polish

### Task P3.1.1: Add Hover States for Dividers
**Title**: Add visual feedback for splitter hover
**Dependencies**: Phase 2 complete
**Action**: MODIFY
**File**: `src/vfwidgets_multisplit/view/container.py`

**Implementation**:
Add custom splitter class to container.py:
```python
from PySide6.QtWidgets import QSplitter
from PySide6.QtCore import QEvent
from PySide6.QtGui import QEnterEvent

class StyledSplitter(QSplitter):
    """Splitter with hover states and improved visuals."""

    def __init__(self, orientation, parent=None):
        """Initialize styled splitter."""
        super().__init__(orientation, parent)
        self.setChildrenCollapsible(False)
        self.setHandleWidth(6)  # Wider for easier grabbing

        # Apply base style
        self.setStyleSheet("""
            QSplitter::handle {
                background-color: #e0e0e0;
                border: 1px solid transparent;
            }
            QSplitter::handle:horizontal {
                width: 6px;
                margin: 2px 0px;
            }
            QSplitter::handle:vertical {
                height: 6px;
                margin: 0px 2px;
            }
        """)

    def createHandle(self):
        """Create custom handle with hover support."""
        handle = super().createHandle()
        handle.installEventFilter(self)
        return handle

    def eventFilter(self, obj, event):
        """Handle hover events on splitter handles."""
        if event.type() == QEvent.Type.Enter:
            # Mouse entered handle
            self.setStyleSheet("""
                QSplitter::handle {
                    background-color: #b0b0b0;
                    border: 1px solid #808080;
                }
                QSplitter::handle:horizontal {
                    width: 6px;
                    margin: 2px 0px;
                }
                QSplitter::handle:vertical {
                    height: 6px;
                    margin: 0px 2px;
                }
            """)
            # Change cursor
            from PySide6.QtCore import Qt
            obj.setCursor(Qt.CursorShape.SplitHCursor if self.orientation() == Qt.Orientation.Horizontal
                        else Qt.CursorShape.SplitVCursor)

        elif event.type() == QEvent.Type.Leave:
            # Mouse left handle
            self.setStyleSheet("""
                QSplitter::handle {
                    background-color: #e0e0e0;
                    border: 1px solid transparent;
                }
                QSplitter::handle:horizontal {
                    width: 6px;
                    margin: 2px 0px;
                }
                QSplitter::handle:vertical {
                    height: 6px;
                    margin: 0px 2px;
                }
            """)
            obj.unsetCursor()

        return super().eventFilter(obj, event)
```

Modify _build_widget_tree to use StyledSplitter:
```python
def _build_widget_tree(self, node: PaneNode) -> Optional[QWidget]:
    """Build Qt widget tree from node tree."""
    if isinstance(node, LeafNode):
        # ... existing leaf handling ...

    elif isinstance(node, SplitNode):
        # Create styled splitter
        orientation = (Qt.Orientation.Horizontal
                     if node.orientation.value == "horizontal"
                     else Qt.Orientation.Vertical)

        splitter = StyledSplitter(orientation)  # Changed from QSplitter

        # ... rest of method unchanged ...
```

**Tests**:
```python
def test_splitter_styling(qtbot):
    """Test splitter has proper styling."""
    from vfwidgets_multisplit.view.container import StyledSplitter
    from PySide6.QtCore import Qt

    splitter = StyledSplitter(Qt.Orientation.Horizontal)
    qtbot.addWidget(splitter)

    # Check handle width
    assert splitter.handleWidth() == 6

    # Check children not collapsible
    assert not splitter.childrenCollapsible()
```

---

### Task P3.1.2: Add Error State Indicators
**Title**: Add visual feedback for error states
**Dependencies**: P3.1.1
**Action**: CREATE
**File**: `src/vfwidgets_multisplit/view/error_widget.py`

**Implementation**:
```python
"""Error display widget for MultiSplit.

Shows error states when operations fail.
"""

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPalette, QFont


class ErrorWidget(QWidget):
    """Widget to display error states."""

    # Signals
    retry_clicked = Signal()

    def __init__(self, error_message: str = "An error occurred",
                 parent: QWidget = None):
        """Initialize error widget.

        Args:
            error_message: Message to display
            parent: Parent widget
        """
        super().__init__(parent)

        self.setup_ui(error_message)

    def setup_ui(self, message: str):
        """Set up the error UI."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Error icon
        icon_label = QLabel("⚠️")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        font = QFont()
        font.setPointSize(32)
        icon_label.setFont(font)

        # Error message
        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setWordWrap(True)

        # Style with error colors
        message_label.setStyleSheet("""
            QLabel {
                color: #d32f2f;
                padding: 10px;
                font-size: 14px;
            }
        """)

        # Retry button (optional)
        from PySide6.QtWidgets import QPushButton
        retry_button = QPushButton("Retry")
        retry_button.clicked.connect(self.retry_clicked.emit)
        retry_button.setMaximumWidth(100)

        # Add to layout
        layout.addWidget(icon_label)
        layout.addWidget(message_label)
        layout.addWidget(retry_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Set background
        self.setStyleSheet("""
            ErrorWidget {
                background-color: #ffebee;
                border: 1px solid #ffcdd2;
                border-radius: 4px;
            }
        """)

    def set_error(self, message: str):
        """Update error message.

        Args:
            message: New error message
        """
        # Find message label and update
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if isinstance(widget, QLabel) and widget.text() != "⚠️":
                widget.setText(message)
                break


class ValidationOverlay(QWidget):
    """Overlay to show validation errors."""

    def __init__(self, parent: QWidget = None):
        """Initialize validation overlay."""
        super().__init__(parent)

        self.setAutoFillBackground(True)

        # Semi-transparent background
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window,
                        Qt.GlobalColor.transparent)
        self.setPalette(palette)

        # Layout for messages
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop |
                                Qt.AlignmentFlag.AlignRight)

        self.messages = []

    def show_validation_error(self, message: str, duration: int = 3000):
        """Show validation error message.

        Args:
            message: Error message to show
            duration: How long to show (ms)
        """
        from PySide6.QtWidgets import QFrame
        from PySide6.QtCore import QTimer

        # Create message frame
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #f44336;
                color: white;
                padding: 8px 12px;
                border-radius: 4px;
                margin: 4px;
            }
        """)

        label = QLabel(message)
        label.setStyleSheet("color: white;")

        frame_layout = QVBoxLayout(frame)
        frame_layout.addWidget(label)
        frame_layout.setContentsMargins(8, 4, 8, 4)

        self.layout.addWidget(frame)
        self.messages.append(frame)

        # Auto-hide after duration
        QTimer.singleShot(duration, lambda: self.hide_message(frame))

    def hide_message(self, frame: QWidget):
        """Hide and remove message frame."""
        if frame in self.messages:
            self.messages.remove(frame)
            frame.deleteLater()
```

---

## P3.2: Validation System

### Task P3.2.1: Create Validation Framework
**Title**: Create comprehensive validation system
**Dependencies**: P3.1.2
**Action**: CREATE
**File**: `src/vfwidgets_multisplit/core/validation.py`

**Implementation**:
```python
"""Validation system for MultiSplit operations.

Provides real-time constraint checking and validation.
"""

from typing import List, Optional, Tuple
from dataclasses import dataclass

from .types import PaneId, WherePosition, SizeConstraints
from .model import PaneModel
from .nodes import PaneNode, LeafNode, SplitNode
from .tree_utils import validate_tree_structure


@dataclass
class ValidationResult:
    """Result of validation check."""

    is_valid: bool
    errors: List[str]
    warnings: List[str]

    def add_error(self, message: str):
        """Add error message."""
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str):
        """Add warning message."""
        self.warnings.append(message)


class OperationValidator:
    """Validates operations before execution."""

    def __init__(self, model: PaneModel):
        """Initialize validator.

        Args:
            model: Model to validate against
        """
        self.model = model

    def validate_split(self, target_pane_id: PaneId,
                      position: WherePosition,
                      ratio: float = 0.5) -> ValidationResult:
        """Validate split operation.

        Args:
            target_pane_id: Pane to split
            position: Where to place new pane
            ratio: Split ratio

        Returns:
            Validation result
        """
        result = ValidationResult(is_valid=True, errors=[], warnings=[])

        # Check target exists
        target = self.model.get_pane(target_pane_id)
        if not target:
            result.add_error(f"Target pane {target_pane_id} not found")
            return result

        # Check ratio validity
        if not 0.1 <= ratio <= 0.9:
            result.add_error(f"Split ratio {ratio} must be between 0.1 and 0.9")

        # Check for maximum depth
        from .tree_utils import get_tree_depth
        if self.model.root:
            current_depth = get_tree_depth(self.model.root)
            if current_depth >= 10:
                result.add_warning("Tree depth exceeds 10 levels")

        # Check for too many panes
        pane_count = len(self.model.get_all_pane_ids())
        if pane_count >= 50:
            result.add_warning(f"Large number of panes ({pane_count}) may impact performance")

        # Position-specific checks
        if position in (WherePosition.BEFORE, WherePosition.AFTER):
            if not target.parent:
                result.add_error(f"Cannot insert {position.value} root pane")

        return result

    def validate_remove(self, pane_id: PaneId) -> ValidationResult:
        """Validate remove operation.

        Args:
            pane_id: Pane to remove

        Returns:
            Validation result
        """
        result = ValidationResult(is_valid=True, errors=[], warnings=[])

        # Check pane exists
        pane = self.model.get_pane(pane_id)
        if not pane:
            result.add_error(f"Pane {pane_id} not found")
            return result

        # Check if removing last pane
        if len(self.model.get_all_pane_ids()) == 1:
            result.add_warning("Removing last pane will leave empty workspace")

        # Check if pane is focused
        if self.model.focused_pane_id == pane_id:
            result.add_warning("Removing focused pane")

        return result

    def validate_ratios(self, node_id: str, ratios: List[float]) -> ValidationResult:
        """Validate ratio adjustment.

        Args:
            node_id: Split node ID
            ratios: New ratios

        Returns:
            Validation result
        """
        result = ValidationResult(is_valid=True, errors=[], warnings=[])

        # Check ratios sum to 1.0
        from .tree_utils import validate_ratios
        if not validate_ratios(ratios):
            result.add_error("Ratios must sum to 1.0")

        # Check minimum sizes
        for ratio in ratios:
            if ratio < 0.05:
                result.add_error("Ratio too small - minimum is 0.05")
            elif ratio < 0.1:
                result.add_warning(f"Small ratio {ratio:.2f} may create unusable pane")

        return result

    def validate_model_state(self) -> ValidationResult:
        """Validate entire model state.

        Returns:
            Validation result
        """
        result = ValidationResult(is_valid=True, errors=[], warnings=[])

        if not self.model.root:
            # Empty model is valid
            return result

        # Check tree structure
        is_valid, errors = validate_tree_structure(self.model.root)
        if not is_valid:
            for error in errors:
                result.add_error(error)

        # Check registry consistency
        from .tree_utils import get_all_leaves
        leaves = get_all_leaves(self.model.root)
        registry_ids = set(self.model.get_all_pane_ids())
        tree_ids = {leaf.pane_id for leaf in leaves}

        if registry_ids != tree_ids:
            result.add_error("Pane registry inconsistent with tree")

        # Check focus validity
        if self.model.focused_pane_id and self.model.focused_pane_id not in registry_ids:
            result.add_error(f"Focused pane {self.model.focused_pane_id} not in tree")

        return result
```

**Tests**:
```python
def test_operation_validator():
    """Test operation validation."""
    from vfwidgets_multisplit.core.validation import OperationValidator
    from vfwidgets_multisplit.core.types import WherePosition

    model = PaneModel()
    validator = OperationValidator(model)

    # Test split validation on empty model
    result = validator.validate_split(PaneId("invalid"), WherePosition.RIGHT)
    assert not result.is_valid
    assert "not found" in result.errors[0]

    # Add a pane
    model.root = LeafNode(PaneId("p1"), WidgetId("w1"))
    model._rebuild_registry()

    # Test valid split
    result = validator.validate_split(PaneId("p1"), WherePosition.RIGHT, 0.5)
    assert result.is_valid
    assert len(result.errors) == 0

    # Test invalid ratio
    result = validator.validate_split(PaneId("p1"), WherePosition.RIGHT, 0.01)
    assert not result.is_valid
    assert "must be between" in result.errors[0]

    # Test remove validation
    result = validator.validate_remove(PaneId("p1"))
    assert result.is_valid
    assert "last pane" in result.warnings[0]
```

---

### Task P3.2.2: Integrate Validation with Commands
**Title**: Add validation checks to commands
**Dependencies**: P3.2.1
**Action**: MODIFY
**File**: `src/vfwidgets_multisplit/controller/controller.py`

**Implementation**:
Add validation to PaneController:
```python
from ..core.validation import OperationValidator, ValidationResult

@dataclass
class PaneController:
    """Controller managing model mutations through commands."""

    model: PaneModel
    _undo_stack: List[Command] = field(default_factory=list)
    _redo_stack: List[Command] = field(default_factory=list)
    _transaction_depth: int = 0
    _transaction_commands: List[Command] = field(default_factory=list)
    _validator: OperationValidator = field(init=False)  # NEW

    # Configuration
    max_undo_levels: int = 100
    enable_validation: bool = True  # NEW

    def __post_init__(self):
        """Initialize controller."""
        self._validator = OperationValidator(self.model)

    def validate_and_execute(self, command: Command) -> Tuple[bool, ValidationResult]:
        """Validate and execute command if valid.

        Args:
            command: Command to validate and execute

        Returns:
            Tuple of (success, validation_result)
        """
        if not self.enable_validation:
            # Skip validation
            success = self.execute_command(command)
            return success, ValidationResult(is_valid=True, errors=[], warnings=[])

        # Perform validation based on command type
        from .commands import SplitPaneCommand, RemovePaneCommand, SetRatiosCommand

        validation_result = ValidationResult(is_valid=True, errors=[], warnings=[])

        if isinstance(command, SplitPaneCommand):
            validation_result = self._validator.validate_split(
                command.target_pane_id,
                command.position,
                command.ratio
            )
        elif isinstance(command, RemovePaneCommand):
            validation_result = self._validator.validate_remove(
                command.pane_id
            )
        elif isinstance(command, SetRatiosCommand):
            validation_result = self._validator.validate_ratios(
                str(command.node_id),
                command.ratios
            )

        # Execute if valid
        if validation_result.is_valid:
            success = self.execute_command(command)
            return success, validation_result
        else:
            # Emit validation failed signal
            self.model.signals.validation_failed.emit(validation_result.errors)
            return False, validation_result

    # Update high-level operations to use validation

    def split_pane(self, target_pane_id: PaneId, widget_id: WidgetId,
                   position: WherePosition, ratio: float = 0.5) -> Tuple[bool, ValidationResult]:
        """Split a pane with validation.

        Returns:
            Tuple of (success, validation_result)
        """
        command = SplitPaneCommand(
            self.model, target_pane_id, widget_id, position, ratio
        )
        return self.validate_and_execute(command)

    def remove_pane(self, pane_id: PaneId) -> Tuple[bool, ValidationResult]:
        """Remove a pane with validation.

        Returns:
            Tuple of (success, validation_result)
        """
        command = RemovePaneCommand(self.model, pane_id)
        return self.validate_and_execute(command)
```

---

## P3.3: Size Constraints

### Task P3.3.1: Implement Constraint Enforcement
**Title**: Add size constraint checking to geometry calculator
**Dependencies**: P3.2.2
**Action**: MODIFY
**File**: `src/vfwidgets_multisplit/core/geometry.py`

**Implementation**:
Enhance GeometryCalculator:
```python
def calculate_layout(self, root: PaneNode, bounds: Bounds,
                    divider_width: int = 6) -> Dict[PaneId, Bounds]:
    """Calculate pixel-perfect layout with constraint enforcement.

    Args:
        root: Root node of tree
        bounds: Available bounds for layout
        divider_width: Width of dividers in pixels

    Returns:
        Mapping of pane IDs to their bounds
    """
    self.divider_width = divider_width
    result = {}

    # Calculate initial layout
    self._calculate_node_bounds(root, bounds, result)

    # Apply constraints
    self._apply_constraints(root, result)

    return result

def _apply_constraints(self, node: PaneNode,
                       layout: Dict[PaneId, Bounds]):
    """Apply size constraints to layout.

    Args:
        node: Node to apply constraints to
        layout: Current layout to modify
    """
    if isinstance(node, LeafNode):
        if node.pane_id in layout:
            bounds = layout[node.pane_id]

            # Apply constraints
            new_width, new_height = node.constraints.clamp_size(
                bounds.width, bounds.height
            )

            if new_width != bounds.width or new_height != bounds.height:
                # Update bounds with constrained size
                layout[node.pane_id] = Bounds(
                    bounds.x, bounds.y, new_width, new_height
                )

    elif isinstance(node, SplitNode):
        # Recursively apply to children
        for child in node.children:
            self._apply_constraints(child, layout)

        # Check if children meet minimum sizes
        self._propagate_constraints(node, layout)

def _propagate_constraints(self, split_node: SplitNode,
                          layout: Dict[PaneId, Bounds]):
    """Propagate constraints through split node.

    Args:
        split_node: Split node to propagate through
        layout: Current layout
    """
    # Calculate minimum sizes for each child
    min_sizes = []
    for child in split_node.children:
        min_size = self._calculate_minimum_size(child)
        min_sizes.append(min_size)

    # Check if we can fit all minimums
    total_min = sum(min_sizes)
    available = (split_node.bounds.width if split_node.orientation == Orientation.HORIZONTAL
                else split_node.bounds.height)

    if total_min > available:
        # Need to adjust ratios to meet constraints
        # This is complex - for now, just warn
        from ..core.signals import ModelSignals
        if hasattr(self, 'signals'):
            self.signals.validation_failed.emit(
                ["Insufficient space for minimum sizes"]
            )

def _calculate_minimum_size(self, node: PaneNode) -> int:
    """Calculate minimum size for node.

    Args:
        node: Node to calculate for

    Returns:
        Minimum size in pixels
    """
    if isinstance(node, LeafNode):
        return node.constraints.min_width  # or min_height based on orientation

    elif isinstance(node, SplitNode):
        # Sum of child minimums plus dividers
        child_mins = [self._calculate_minimum_size(child)
                     for child in node.children]
        divider_space = self.divider_width * (len(node.children) - 1)
        return sum(child_mins) + divider_space

    return 50  # Default minimum
```

---

### Task P3.3.2: Add Constraint Commands
**Title**: Create commands for updating constraints
**Dependencies**: P3.3.1
**Action**: MODIFY
**File**: `src/vfwidgets_multisplit/controller/commands.py`

**Implementation**:
Add to commands.py:
```python
@dataclass
class SetConstraintsCommand(Command):
    """Command to set pane constraints."""

    pane_id: PaneId
    constraints: SizeConstraints

    def __init__(self, model: PaneModel, pane_id: PaneId,
                 constraints: SizeConstraints):
        """Initialize constraints command."""
        super().__init__(model)
        self.pane_id = pane_id
        self.constraints = constraints
        self._old_constraints: Optional[SizeConstraints] = None

    def execute(self) -> bool:
        """Set the constraints."""
        if self.executed:
            return False

        pane = self.model.get_pane(self.pane_id)
        if not pane or not isinstance(pane, LeafNode):
            return False

        # Save old constraints
        self._old_constraints = pane.constraints

        # Set new constraints
        pane.constraints = self.constraints

        # Trigger re-layout
        self.model.signals.structure_changed.emit()

        self.executed = True
        return True

    def undo(self) -> bool:
        """Restore old constraints."""
        if not self.can_undo():
            return False

        pane = self.model.get_pane(self.pane_id)
        if pane and isinstance(pane, LeafNode) and self._old_constraints:
            pane.constraints = self._old_constraints
            self.model.signals.structure_changed.emit()
            self.executed = False
            return True

        return False

    def description(self) -> str:
        """Get command description."""
        return f"Set constraints for pane {self.pane_id}"
```

---

## P3.4: Integration & Polish

### Task P3.4.1: Create Public API
**Title**: Create the main MultiSplit widget class
**Dependencies**: P3.3.2
**Action**: MODIFY
**File**: `src/vfwidgets_multisplit/multisplit.py`

**Implementation**:
```python
"""Main MultiSplit widget implementation.

This is the public API for the MultiSplit widget.
"""

from typing import Optional, Protocol, List, Dict, Any
from pathlib import Path

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal

from .core.types import PaneId, WidgetId, WherePosition, Direction, SizeConstraints
from .core.model import PaneModel
from .core.nodes import LeafNode
from .core.focus import FocusManager
from .core.session import SessionManager
from .controller.controller import PaneController
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
            self.layout_changed.emit
        )
        self.model.signals.validation_failed.connect(
            self.validation_failed.emit
        )

        # Handle splitter moves
        self.container.splitter_moved.connect(self._on_splitter_moved)

    def _on_splitter_moved(self, node_id: str, ratios: List[float]):
        """Handle splitter movement."""
        from .core.types import NodeId
        from .controller.commands import SetRatiosCommand

        command = SetRatiosCommand(self.model, NodeId(node_id), ratios)
        self.controller.execute_command(command)

    # Public API

    def initialize_empty(self, widget_id: str = "default"):
        """Initialize with a single pane.

        Args:
            widget_id: Widget ID for initial pane
        """
        from .core.utils import generate_pane_id

        pane_id = generate_pane_id()
        leaf = LeafNode(pane_id, WidgetId(widget_id))

        self.model.root = leaf
        self.model._rebuild_registry()
        self.model.set_focused_pane(pane_id)

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
```

---

## Validation Criteria

### Phase 3 Complete When:

1. ✅ Splitter hover states visible
2. ✅ Error widgets display properly
3. ✅ Validation prevents invalid operations
4. ✅ Size constraints enforced
5. ✅ Public API fully functional
6. ✅ All Phase 3 tests passing (10+ new tests)
7. ✅ Total 100+ tests passing
8. ✅ No regressions in previous phases

### MVP Integration Test:

```python
def test_mvp_complete(qtbot):
    """Test complete MVP functionality."""
    from vfwidgets_multisplit import MultisplitWidget
    from vfwidgets_multisplit.core.types import WherePosition, Direction
    from pathlib import Path
    import tempfile

    # Create widget
    widget = MultisplitWidget()
    qtbot.addWidget(widget)

    # Test initialization
    assert len(widget.get_pane_ids()) == 1

    # Test splitting
    pane_id = widget.get_pane_ids()[0]
    assert widget.split_pane(pane_id, "editor:test.py", WherePosition.RIGHT)
    assert len(widget.get_pane_ids()) == 2

    # Test focus
    widget.focus_pane(widget.get_pane_ids()[0])
    assert widget.get_focused_pane() == widget.get_pane_ids()[0]

    # Test navigation
    widget.navigate_focus(Direction.RIGHT)
    assert widget.get_focused_pane() == widget.get_pane_ids()[1]

    # Test constraints
    widget.set_constraints(widget.get_pane_ids()[0], min_width=100)

    # Test undo/redo
    assert widget.can_undo()
    widget.undo()
    assert len(widget.get_pane_ids()) == 1
    assert widget.can_redo()
    widget.redo()
    assert len(widget.get_pane_ids()) == 2

    # Test persistence
    with tempfile.NamedTemporaryFile(suffix='.json') as f:
        filepath = Path(f.name)
        assert widget.save_layout(filepath)

        # Clear and reload
        widget.initialize_empty()
        assert len(widget.get_pane_ids()) == 1

        assert widget.load_layout(filepath)
        assert len(widget.get_pane_ids()) == 2

    print("✅ MVP COMPLETE - All features working!")
```

---

## Task Execution Order

1. **P3.1: Visual Polish**
   - P3.1.1 → P3.1.2

2. **P3.2: Validation System**
   - P3.2.1 → P3.2.2

3. **P3.3: Size Constraints**
   - P3.3.1 → P3.3.2

4. **P3.4: Integration**
   - P3.4.1 (Final integration)

---

## Success Metrics

- All 10+ Phase 3 tests passing
- Total 100+ tests passing (all phases)
- Visual feedback smooth and responsive
- Validation messages clear and helpful
- Constraints properly enforced
- Public API intuitive and complete
- No memory leaks during extended use
- Performance acceptable for 50+ panes
- MVP fully functional and production-ready