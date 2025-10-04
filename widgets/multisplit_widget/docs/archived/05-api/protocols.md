# Protocols

## Overview

MultiSplit uses protocol-based interfaces to maintain clean separation between layout management and widget content. These protocols define the contracts for widget providers, visitors, and renderers, enabling flexible integration while preserving type safety and extensibility.

## What This Covers

- **Widget Provider Protocol**: Widget creation and lifecycle management
- **Visitor Pattern Protocols**: Tree traversal and transformation interfaces
- **Renderer Protocols**: Custom drawing and interaction handlers
- **Validation Protocols**: State checking and error detection interfaces
- **Event Handler Protocols**: User interaction and lifecycle events

## What This Doesn't Cover

- Concrete implementations (see [Usage Guide](../06-guides/usage-guide.md))
- Signal mechanics (see [Signals](signals.md))
- Public widget API (see [Public API](public-api.md))
- Internal model structures (handled by Model layer)

---

## Widget Provider Protocol

### Core Provider Interface

```python
from typing import Protocol, Optional
from PySide6.QtWidgets import QWidget

class WidgetProvider(Protocol):
    """Primary interface for widget creation and management"""

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """
        Create or retrieve widget for layout placement.

        Called when MultiSplit needs a widget instance, typically during:
        - Layout restoration from saved state
        - Undo/redo operations that recreate panes
        - Dynamic widget swapping operations

        Args:
            widget_id: Stable identifier meaningful to the application
            pane_id: Target pane ID where widget will be placed

        Returns:
            QWidget instance ready for display

        Raises:
            WidgetCreationError: If widget cannot be created
            InvalidWidgetIdError: If widget_id format is invalid

        Implementation Notes:
        - MUST return a valid QWidget instance
        - Widget should be ready for immediate display
        - Implementation should handle unknown widget_ids gracefully
        - Consider widget pooling for performance
        """

    def widget_closing(self, widget_id: str, widget: QWidget) -> None:
        """
        Notification that widget is being removed from layout.

        Called before widget is removed from layout, allowing applications to:
        - Save widget state for later restoration
        - Clean up resources or connections
        - Update application state
        - Cache widget instances for reuse

        Args:
            widget_id: The widget's identifier
            widget: The actual widget instance being removed

        Implementation Notes:
        - Widget is still valid and accessible during this call
        - This is the last chance to save widget state
        - Do NOT call deleteLater() on the widget - MultiSplit handles this
        - Exception in this method should not prevent layout operation
        """
```

### Extended Provider Interface

```python
class ExtendedWidgetProvider(Protocol):
    """Extended provider with additional lifecycle methods"""

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Core widget creation method (required)"""

    def widget_closing(self, widget_id: str, widget: QWidget) -> None:
        """Widget removal notification (required)"""

    def widget_focused(self, widget_id: str, widget: QWidget) -> None:
        """
        Notification that widget gained focus.

        Optional method called when pane containing widget becomes focused.

        Args:
            widget_id: The widget's identifier
            widget: The widget instance that gained focus

        Example:
            def widget_focused(self, widget_id: str, widget: QWidget) -> None:
                if isinstance(widget, CodeEditor):
                    self.update_statusbar(widget.current_file)
                    self.sync_project_tree(widget.current_file)
        """

    def widget_unfocused(self, widget_id: str, widget: QWidget) -> None:
        """
        Notification that widget lost focus.

        Optional method called when pane containing widget loses focus.

        Args:
            widget_id: The widget's identifier
            widget: The widget instance that lost focus
        """

    def validate_widget_id(self, widget_id: str) -> bool:
        """
        Check if widget ID is valid for this provider.

        Optional method to pre-validate widget IDs before use.

        Args:
            widget_id: Widget identifier to validate

        Returns:
            True if ID is valid and can create widget

        Example:
            def validate_widget_id(self, widget_id: str) -> bool:
                return widget_id.startswith(('editor:', 'terminal:', 'browser:'))
        """

    def get_widget_metadata(self, widget_id: str) -> dict:
        """
        Get metadata about widget without creating it.

        Optional method to get widget information for UI display.

        Args:
            widget_id: Widget identifier

        Returns:
            Metadata dictionary with optional keys:
            - 'title': Display title
            - 'icon': Icon name/path
            - 'tooltip': Tooltip text
            - 'modified': Boolean modification state
            - 'type': Widget type string

        Example:
            def get_widget_metadata(self, widget_id: str) -> dict:
                if widget_id.startswith('editor:'):
                    file_path = widget_id[7:]
                    return {
                        'title': os.path.basename(file_path),
                        'icon': 'text-editor',
                        'tooltip': file_path,
                        'modified': self.is_file_modified(file_path),
                        'type': 'editor'
                    }
                return {}
        """
```

### Async Provider Protocol

```python
import asyncio
from typing import Awaitable

class AsyncWidgetProvider(Protocol):
    """Provider supporting asynchronous widget creation"""

    async def provide_widget_async(self, widget_id: str, pane_id: str) -> QWidget:
        """
        Asynchronously create or retrieve widget.

        Used when widget creation involves async operations like:
        - Loading files from network
        - Database queries
        - Heavy computation

        Args:
            widget_id: Widget identifier
            pane_id: Target pane ID

        Returns:
            Widget instance

        Example:
            async def provide_widget_async(self, widget_id: str, pane_id: str) -> QWidget:
                if widget_id.startswith('remote:'):
                    url = widget_id[7:]
                    content = await self.fetch_remote_content(url)
                    editor = CodeEditor()
                    editor.setText(content)
                    return editor
                return self.provide_widget(widget_id, pane_id)
        """

    def widget_closing(self, widget_id: str, widget: QWidget) -> None:
        """Standard widget closing notification"""

    def cancel_widget_creation(self, widget_id: str) -> None:
        """
        Cancel pending widget creation.

        Optional method to cancel async widget creation.

        Args:
            widget_id: Widget ID for cancelled creation

        Example:
            def cancel_widget_creation(self, widget_id: str) -> None:
                if widget_id in self.pending_tasks:
                    self.pending_tasks[widget_id].cancel()
                    del self.pending_tasks[widget_id]
        """
```

---

## Visitor Pattern Protocols

### Base Visitor Interface

```python
from typing import Any, Generic, TypeVar
from abc import ABC, abstractmethod

T = TypeVar('T')

class NodeVisitor(Protocol[T]):
    """Base visitor for tree traversal operations"""

    def visit_leaf(self, node: LeafNode) -> T:
        """
        Process leaf node.

        Args:
            node: Leaf node containing widget reference

        Returns:
            Result of processing (type depends on visitor)

        Example:
            def visit_leaf(self, node: LeafNode) -> str:
                return f"Pane {node.pane_id}: {node.widget_id}"
        """

    def visit_split(self, node: SplitNode) -> T:
        """
        Process split node.

        Args:
            node: Split node containing child arrangement

        Returns:
            Result of processing (type depends on visitor)

        Example:
            def visit_split(self, node: SplitNode) -> str:
                return f"Split {node.orientation.value} ({len(node.children)} children)"
        """

    def visit_children(self, split: SplitNode) -> list[T]:
        """
        Visit all children of split node.

        Default implementation visits children in order.

        Args:
            split: Split node to process

        Returns:
            List of results from visiting each child

        Override to customize traversal order:
            def visit_children(self, split: SplitNode) -> list[T]:
                # Reverse order traversal
                return [child.accept(self) for child in reversed(split.children)]
        """
```

### Mutable Visitor Interface

```python
class MutableVisitor(Protocol[T]):
    """Visitor that can modify tree structure"""

    def visit_leaf(self, node: LeafNode) -> T:
        """Process and potentially modify leaf node"""

    def visit_split(self, node: SplitNode) -> T:
        """Process and potentially modify split node"""

    def will_modify_node(self, node: PaneNode) -> bool:
        """
        Check if visitor will modify node.

        Called before visiting to determine if mutations will occur.

        Args:
            node: Node about to be visited

        Returns:
            True if node will be modified

        Example:
            def will_modify_node(self, node: PaneNode) -> bool:
                if isinstance(node, LeafNode):
                    return node.widget_id in self.widgets_to_replace
                return False
        """

    def node_modified(self, old_node: PaneNode, new_node: PaneNode) -> None:
        """
        Notification that node was modified.

        Called after node modification to allow cleanup or notifications.

        Args:
            old_node: Original node before modification
            new_node: New node after modification

        Example:
            def node_modified(self, old_node: PaneNode, new_node: PaneNode) -> None:
                if isinstance(old_node, LeafNode) and isinstance(new_node, LeafNode):
                    self.widget_id_mappings[old_node.widget_id] = new_node.widget_id
        """
```

### Specialized Visitor Protocols

```python
class SearchVisitor(Protocol):
    """Visitor for finding nodes matching criteria"""

    def matches(self, node: PaneNode) -> bool:
        """
        Test if node matches search criteria.

        Args:
            node: Node to test

        Returns:
            True if node matches

        Example:
            def matches(self, node: PaneNode) -> bool:
                if isinstance(node, LeafNode):
                    return node.widget_id.startswith('editor:')
                return False
        """

    def visit_leaf(self, node: LeafNode) -> bool:
        """Visit leaf and return match status"""

    def visit_split(self, node: SplitNode) -> bool:
        """Visit split and return match status"""

    def get_matches(self) -> list[PaneNode]:
        """
        Get all matching nodes found during traversal.

        Returns:
            List of nodes that matched criteria
        """

    def get_paths_to_matches(self) -> dict[PaneNode, list[PaneNode]]:
        """
        Get paths from root to each matching node.

        Returns:
            Dictionary mapping matching nodes to their paths from root
        """

class CollectorVisitor(Protocol[T]):
    """Visitor for collecting data from tree"""

    def visit_leaf(self, node: LeafNode) -> T:
        """Collect data from leaf node"""

    def visit_split(self, node: SplitNode) -> T:
        """Collect data from split node"""

    def collect_all(self) -> list[T]:
        """
        Get all collected data.

        Returns:
            List of collected items in traversal order
        """

    def filter_collected(self, predicate: Callable[[T], bool]) -> list[T]:
        """
        Filter collected data by predicate.

        Args:
            predicate: Function to test each collected item

        Returns:
            Filtered list of collected items
        """

class TransformVisitor(Protocol):
    """Visitor for transforming tree structure"""

    def transform_leaf(self, node: LeafNode) -> LeafNode:
        """
        Transform leaf node.

        Args:
            node: Original leaf node

        Returns:
            Transformed leaf node (may be same instance if no change)

        Example:
            def transform_leaf(self, node: LeafNode) -> LeafNode:
                if node.widget_id in self.replacements:
                    new_widget_id = self.replacements[node.widget_id]
                    return LeafNode(node.node_id, node.pane_id, new_widget_id)
                return node
        """

    def transform_split(self, node: SplitNode,
                       transformed_children: list[PaneNode]) -> SplitNode:
        """
        Transform split node with already-transformed children.

        Args:
            node: Original split node
            transformed_children: Children after transformation

        Returns:
            Transformed split node

        Example:
            def transform_split(self, node: SplitNode,
                              transformed_children: list[PaneNode]) -> SplitNode:
                # Normalize ratios after transformation
                count = len(transformed_children)
                equal_ratios = [1.0 / count] * count
                return SplitNode(node.node_id, node.orientation,
                               transformed_children, equal_ratios)
        """

    def will_transform(self, node: PaneNode) -> bool:
        """
        Check if node will be transformed.

        Args:
            node: Node to check

        Returns:
            True if transformation will occur
        """
```

---

## Renderer Protocols

### Widget Renderer Interface

```python
class WidgetRenderer(Protocol):
    """Custom renderer for widget appearance and interaction"""

    def render_widget(self, widget: QWidget, pane_id: str,
                     painter: QPainter, rect: QRect) -> None:
        """
        Custom render widget in pane.

        Args:
            widget: Widget instance to render
            pane_id: Pane identifier
            painter: QPainter for drawing
            rect: Available drawing rectangle

        Example:
            def render_widget(self, widget: QWidget, pane_id: str,
                            painter: QPainter, rect: QRect) -> None:
                # Draw custom border around widget
                if pane_id == self.focused_pane_id:
                    painter.setPen(QPen(QColor(0, 120, 215), 2))
                    painter.drawRect(rect.adjusted(1, 1, -1, -1))
        """

    def render_pane_header(self, pane_id: str, widget_id: str,
                          painter: QPainter, rect: QRect,
                          is_focused: bool, is_modified: bool) -> None:
        """
        Render pane title/header area.

        Args:
            pane_id: Pane identifier
            widget_id: Widget identifier for the pane
            painter: QPainter for drawing
            rect: Header rectangle
            is_focused: Whether pane has focus
            is_modified: Whether widget content is modified

        Example:
            def render_pane_header(self, pane_id: str, widget_id: str,
                                 painter: QPainter, rect: QRect,
                                 is_focused: bool, is_modified: bool) -> None:
                # Draw tab-like header
                bg_color = QColor(0, 120, 215) if is_focused else QColor(128, 128, 128)
                painter.fillRect(rect, bg_color)

                title = self.get_display_title(widget_id)
                if is_modified:
                    title += " *"
                painter.setPen(QColor(255, 255, 255))
                painter.drawText(rect, Qt.AlignLeft | Qt.AlignVCenter, title)
        """

    def get_pane_margins(self, pane_id: str) -> QMargins:
        """
        Get custom margins for pane content.

        Args:
            pane_id: Pane identifier

        Returns:
            QMargins for pane content area

        Example:
            def get_pane_margins(self, pane_id: str) -> QMargins:
                # Leave space for header
                return QMargins(2, 20, 2, 2)
        """

    def handle_pane_interaction(self, pane_id: str, event: QEvent) -> bool:
        """
        Handle interaction with pane decorations.

        Args:
            pane_id: Pane identifier
            event: Mouse or key event

        Returns:
            True if event was handled, False to continue processing

        Example:
            def handle_pane_interaction(self, pane_id: str, event: QEvent) -> bool:
                if isinstance(event, QMouseEvent) and event.button() == Qt.RightButton:
                    self.show_pane_context_menu(pane_id, event.globalPos())
                    return True
                return False
        """
```

### Divider Renderer Interface

```python
class DividerRenderer(Protocol):
    """Custom renderer for split dividers"""

    def render_divider(self, split_id: str, divider_index: int,
                      painter: QPainter, rect: QRect,
                      orientation: Orientation, is_hovered: bool,
                      is_dragging: bool) -> None:
        """
        Render split divider.

        Args:
            split_id: Split node identifier
            divider_index: Index of divider in split
            painter: QPainter for drawing
            rect: Divider rectangle
            orientation: Split orientation
            is_hovered: Whether mouse is over divider
            is_dragging: Whether divider is being dragged

        Example:
            def render_divider(self, split_id: str, divider_index: int,
                             painter: QPainter, rect: QRect,
                             orientation: Orientation, is_hovered: bool,
                             is_dragging: bool) -> None:
                # Custom divider appearance
                if is_dragging:
                    color = QColor(0, 120, 215)
                elif is_hovered:
                    color = QColor(200, 200, 200)
                else:
                    color = QColor(160, 160, 160)

                painter.fillRect(rect, color)

                # Draw grip dots
                if orientation == Orientation.HORIZONTAL:
                    self.draw_horizontal_grip(painter, rect)
                else:
                    self.draw_vertical_grip(painter, rect)
        """

    def get_divider_width(self, orientation: Orientation) -> int:
        """
        Get custom divider width.

        Args:
            orientation: Split orientation

        Returns:
            Divider width in pixels

        Example:
            def get_divider_width(self, orientation: Orientation) -> int:
                return 8 if self.thick_dividers else 4
        """

    def get_divider_cursor(self, orientation: Orientation) -> QCursor:
        """
        Get cursor for divider hover/drag.

        Args:
            orientation: Split orientation

        Returns:
            QCursor for the divider

        Example:
            def get_divider_cursor(self, orientation: Orientation) -> QCursor:
                if orientation == Orientation.HORIZONTAL:
                    return QCursor(Qt.SplitVCursor)
                else:
                    return QCursor(Qt.SplitHCursor)
        """

    def handle_divider_interaction(self, split_id: str, divider_index: int,
                                 event: QEvent) -> bool:
        """
        Handle interaction with divider.

        Args:
            split_id: Split identifier
            divider_index: Divider index
            event: Mouse or key event

        Returns:
            True if handled, False for default behavior

        Example:
            def handle_divider_interaction(self, split_id: str, divider_index: int,
                                         event: QEvent) -> bool:
                if isinstance(event, QMouseEvent) and event.button() == Qt.MiddleButton:
                    # Middle-click resets to equal ratios
                    self.multisplit.reset_ratios(split_id)
                    return True
                return False
        """
```

### Layout Renderer Interface

```python
class LayoutRenderer(Protocol):
    """Custom renderer for overall layout appearance"""

    def render_background(self, painter: QPainter, rect: QRect) -> None:
        """
        Render layout background.

        Args:
            painter: QPainter for drawing
            rect: Full widget rectangle

        Example:
            def render_background(self, painter: QPainter, rect: QRect) -> None:
                # Gradient background
                gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
                gradient.setColorAt(0, QColor(240, 240, 240))
                gradient.setColorAt(1, QColor(220, 220, 220))
                painter.fillRect(rect, gradient)
        """

    def render_empty_state(self, painter: QPainter, rect: QRect) -> None:
        """
        Render empty layout state.

        Args:
            painter: QPainter for drawing
            rect: Available drawing area

        Example:
            def render_empty_state(self, painter: QPainter, rect: QRect) -> None:
                painter.setPen(QColor(128, 128, 128))
                painter.drawText(rect, Qt.AlignCenter,
                               "Drop files here or use File menu to open")
        """

    def render_drop_indicator(self, painter: QPainter, rect: QRect,
                            position: WherePosition) -> None:
        """
        Render drop target indicator.

        Args:
            painter: QPainter for drawing
            rect: Target area rectangle
            position: Where drop would occur

        Example:
            def render_drop_indicator(self, painter: QPainter, rect: QRect,
                                    position: WherePosition) -> None:
                # Highlight drop zone
                painter.setPen(QPen(QColor(0, 120, 215), 3, Qt.DashLine))
                painter.drawRect(rect.adjusted(2, 2, -2, -2))
        """

    def get_layout_margins(self) -> QMargins:
        """
        Get margins around entire layout.

        Returns:
            QMargins for layout container

        Example:
            def get_layout_margins(self) -> QMargins:
                return QMargins(4, 4, 4, 4)  # 4px border around layout
        """
```

---

## Validation Protocols

### State Validator Interface

```python
class StateValidator(Protocol):
    """Validator for model state integrity"""

    def validate_tree(self, root: Optional[PaneNode]) -> ValidationResult:
        """
        Validate tree structure.

        Args:
            root: Root node of tree (may be None)

        Returns:
            ValidationResult with errors and warnings

        Example:
            def validate_tree(self, root: Optional[PaneNode]) -> ValidationResult:
                errors = []
                if root is None:
                    return ValidationResult(True)  # Empty is valid

                # Check for cycles
                if self.has_cycle(root):
                    errors.append("Tree contains cycle")

                return ValidationResult(len(errors) == 0, errors)
        """

    def validate_pane(self, pane: LeafNode, context: ValidationContext) -> ValidationResult:
        """
        Validate individual pane.

        Args:
            pane: Leaf node to validate
            context: Validation context with model state

        Returns:
            ValidationResult for the pane

        Example:
            def validate_pane(self, pane: LeafNode,
                            context: ValidationContext) -> ValidationResult:
                errors = []

                # Check widget ID format
                if not pane.widget_id or ':' not in pane.widget_id:
                    errors.append(f"Invalid widget ID format: {pane.widget_id}")

                # Check for duplicates
                if context.widget_id_counts[pane.widget_id] > 1:
                    errors.append(f"Duplicate widget ID: {pane.widget_id}")

                return ValidationResult(len(errors) == 0, errors)
        """

    def validate_split(self, split: SplitNode, context: ValidationContext) -> ValidationResult:
        """
        Validate split node.

        Args:
            split: Split node to validate
            context: Validation context

        Returns:
            ValidationResult for the split

        Example:
            def validate_split(self, split: SplitNode,
                             context: ValidationContext) -> ValidationResult:
                errors = []

                # Check child count
                if len(split.children) < 2:
                    errors.append(f"Split has {len(split.children)} children, need >= 2")

                # Check ratios
                ratio_sum = sum(split.ratios)
                if abs(ratio_sum - 1.0) > 0.001:
                    errors.append(f"Ratios sum to {ratio_sum}, not 1.0")

                return ValidationResult(len(errors) == 0, errors)
        """

    def validate_focus_state(self, focused_pane_id: Optional[str],
                           available_panes: set[str]) -> ValidationResult:
        """
        Validate focus state consistency.

        Args:
            focused_pane_id: Currently focused pane
            available_panes: Set of valid pane IDs

        Returns:
            ValidationResult for focus state
        """

    def get_repair_suggestions(self, errors: list[str]) -> list[RepairAction]:
        """
        Get suggested repairs for validation errors.

        Args:
            errors: List of validation error messages

        Returns:
            List of possible repair actions

        Example:
            def get_repair_suggestions(self, errors: list[str]) -> list[RepairAction]:
                suggestions = []
                for error in errors:
                    if "ratios sum" in error:
                        suggestions.append(RepairAction("normalize_ratios",
                                         "Normalize split ratios to sum to 1.0"))
                return suggestions
        """
```

### Widget Validator Interface

```python
class WidgetValidator(Protocol):
    """Validator for widget provider compliance"""

    def validate_widget_id(self, widget_id: str) -> ValidationResult:
        """
        Validate widget ID format and content.

        Args:
            widget_id: Widget identifier to validate

        Returns:
            ValidationResult for the widget ID

        Example:
            def validate_widget_id(self, widget_id: str) -> ValidationResult:
                errors = []

                if not widget_id:
                    errors.append("Widget ID cannot be empty")
                elif ':' not in widget_id:
                    errors.append("Widget ID must contain ':' separator")
                elif len(widget_id) > 256:
                    errors.append("Widget ID too long (max 256 characters)")

                return ValidationResult(len(errors) == 0, errors)
        """

    def validate_widget_instance(self, widget: QWidget, widget_id: str) -> ValidationResult:
        """
        Validate widget instance from provider.

        Args:
            widget: Widget instance to validate
            widget_id: Expected widget identifier

        Returns:
            ValidationResult for the widget instance

        Example:
            def validate_widget_instance(self, widget: QWidget,
                                       widget_id: str) -> ValidationResult:
                errors = []

                if widget is None:
                    errors.append("Provider returned None widget")
                elif not isinstance(widget, QWidget):
                    errors.append(f"Provider returned non-QWidget: {type(widget)}")
                elif widget.parent() is not None:
                    errors.append("Widget already has parent")

                return ValidationResult(len(errors) == 0, errors)
        """

    def validate_provider_compliance(self, provider: WidgetProvider,
                                   test_widget_ids: list[str]) -> ValidationResult:
        """
        Validate provider implementation compliance.

        Args:
            provider: Provider to test
            test_widget_ids: Widget IDs to test with

        Returns:
            ValidationResult for provider compliance

        Example:
            def validate_provider_compliance(self, provider: WidgetProvider,
                                           test_widget_ids: list[str]) -> ValidationResult:
                errors = []

                for widget_id in test_widget_ids:
                    try:
                        widget = provider.provide_widget(widget_id, "test-pane")
                        if widget is None:
                            errors.append(f"Provider returned None for {widget_id}")
                        provider.widget_closing(widget_id, widget)
                    except Exception as e:
                        errors.append(f"Provider failed for {widget_id}: {e}")

                return ValidationResult(len(errors) == 0, errors)
        """
```

---

## Event Handler Protocols

### User Interaction Handlers

```python
class InteractionHandler(Protocol):
    """Handler for user interactions with layout"""

    def handle_pane_click(self, pane_id: str, event: QMouseEvent) -> bool:
        """
        Handle click on pane area.

        Args:
            pane_id: Clicked pane identifier
            event: Mouse click event

        Returns:
            True if handled, False for default behavior

        Example:
            def handle_pane_click(self, pane_id: str, event: QMouseEvent) -> bool:
                if event.button() == Qt.MiddleButton:
                    self.close_pane(pane_id)
                    return True
                return False
        """

    def handle_pane_double_click(self, pane_id: str, event: QMouseEvent) -> bool:
        """
        Handle double-click on pane.

        Args:
            pane_id: Double-clicked pane identifier
            event: Mouse double-click event

        Returns:
            True if handled, False for default behavior

        Example:
            def handle_pane_double_click(self, pane_id: str,
                                       event: QMouseEvent) -> bool:
                # Double-click maximizes/restores pane
                if self.is_maximized(pane_id):
                    self.restore_pane(pane_id)
                else:
                    self.maximize_pane(pane_id)
                return True
        """

    def handle_divider_drag(self, split_id: str, divider_index: int,
                          delta: QPoint, is_final: bool) -> bool:
        """
        Handle divider drag operation.

        Args:
            split_id: Split containing the divider
            divider_index: Index of dragged divider
            delta: Mouse movement delta
            is_final: True if this is the final position

        Returns:
            True if handled, False for default behavior

        Example:
            def handle_divider_drag(self, split_id: str, divider_index: int,
                                  delta: QPoint, is_final: bool) -> bool:
                # Snap to common ratios when close
                current_ratio = self.get_divider_ratio(split_id, divider_index)
                snap_points = [0.25, 0.33, 0.5, 0.67, 0.75]

                for snap in snap_points:
                    if abs(current_ratio - snap) < 0.05:
                        self.set_divider_ratio(split_id, divider_index, snap)
                        return True

                return False  # Use default behavior
        """

    def handle_keyboard_navigation(self, event: QKeyEvent) -> bool:
        """
        Handle keyboard navigation.

        Args:
            event: Key press event

        Returns:
            True if handled, False for default behavior

        Example:
            def handle_keyboard_navigation(self, event: QKeyEvent) -> bool:
                key = event.key()
                modifiers = event.modifiers()

                if modifiers == Qt.ControlModifier:
                    if key == Qt.Key_H:
                        self.focus_direction(Direction.LEFT)
                        return True
                    elif key == Qt.Key_L:
                        self.focus_direction(Direction.RIGHT)
                        return True

                return False
        """
```

### Lifecycle Event Handlers

```python
class LifecycleHandler(Protocol):
    """Handler for widget and layout lifecycle events"""

    def layout_about_to_change(self, operation: str, affected_panes: set[str]) -> None:
        """
        Notification before layout change.

        Args:
            operation: Description of pending operation
            affected_panes: Pane IDs that will be affected

        Example:
            def layout_about_to_change(self, operation: str,
                                     affected_panes: set[str]) -> None:
                # Save undo state
                self.save_undo_state()

                # Notify affected widgets
                for pane_id in affected_panes:
                    widget = self.get_widget(pane_id)
                    if hasattr(widget, 'prepare_for_layout_change'):
                        widget.prepare_for_layout_change()
        """

    def layout_changed(self, operation: str, changed_panes: set[str]) -> None:
        """
        Notification after layout change.

        Args:
            operation: Description of completed operation
            changed_panes: Pane IDs that were affected

        Example:
            def layout_changed(self, operation: str, changed_panes: set[str]) -> None:
                # Update UI state
                self.update_menu_actions()
                self.update_window_title()

                # Notify changed widgets
                for pane_id in changed_panes:
                    widget = self.get_widget(pane_id)
                    if hasattr(widget, 'layout_change_complete'):
                        widget.layout_change_complete()
        """

    def widget_about_to_close(self, widget_id: str, widget: QWidget,
                            can_cancel: bool) -> bool:
        """
        Notification before widget closure.

        Args:
            widget_id: Widget identifier
            widget: Widget instance
            can_cancel: Whether closure can be cancelled

        Returns:
            True to allow closure, False to cancel

        Example:
            def widget_about_to_close(self, widget_id: str, widget: QWidget,
                                    can_cancel: bool) -> bool:
                if hasattr(widget, 'is_modified') and widget.is_modified():
                    if can_cancel:
                        result = self.ask_save_changes(widget)
                        if result == QMessageBox.Cancel:
                            return False
                        elif result == QMessageBox.Save:
                            widget.save()
                return True
        """

    def widget_closed(self, widget_id: str, was_last: bool) -> None:
        """
        Notification after widget closure.

        Args:
            widget_id: Closed widget identifier
            was_last: Whether this was the last widget

        Example:
            def widget_closed(self, widget_id: str, was_last: bool) -> None:
                # Update recent files
                if widget_id.startswith('editor:'):
                    file_path = widget_id[7:]
                    self.add_to_recent_files(file_path)

                # Handle empty state
                if was_last:
                    self.show_welcome_screen()
        """

    def focus_about_to_change(self, old_pane_id: Optional[str],
                            new_pane_id: str) -> bool:
        """
        Notification before focus change.

        Args:
            old_pane_id: Currently focused pane (may be None)
            new_pane_id: Pane that will receive focus

        Returns:
            True to allow focus change, False to prevent

        Example:
            def focus_about_to_change(self, old_pane_id: Optional[str],
                                    new_pane_id: str) -> bool:
                # Validate focus change
                if old_pane_id:
                    old_widget = self.get_widget(old_pane_id)
                    if hasattr(old_widget, 'can_lose_focus'):
                        return old_widget.can_lose_focus()
                return True
        """

    def focus_changed(self, old_pane_id: Optional[str], new_pane_id: str) -> None:
        """
        Notification after focus change.

        Args:
            old_pane_id: Previously focused pane
            new_pane_id: Newly focused pane

        Example:
            def focus_changed(self, old_pane_id: Optional[str],
                            new_pane_id: str) -> None:
                # Update window title
                new_widget = self.get_widget(new_pane_id)
                if hasattr(new_widget, 'get_title'):
                    self.setWindowTitle(new_widget.get_title())

                # Update context-sensitive menus
                self.update_context_menus(new_widget)
        """
```

---

## Common Pitfalls

### ❌ Protocol Implementation Errors

```python
# DON'T: Incomplete protocol implementation
class BadProvider:
    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        return QLabel(widget_id)
    # Missing widget_closing method!

# DO: Implement complete protocol
class GoodProvider:
    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        return self.create_widget(widget_id)

    def widget_closing(self, widget_id: str, widget: QWidget) -> None:
        self.save_widget_state(widget_id, widget)
```

### ❌ Visitor State Corruption

```python
# DON'T: Modify visitor state incorrectly
class BadVisitor:
    def __init__(self):
        self.results = []

    def visit_leaf(self, node: LeafNode) -> str:
        self.results.clear()  # Corrupts previous results!
        self.results.append(node.pane_id)
        return node.pane_id

# DO: Maintain visitor state properly
class GoodVisitor:
    def __init__(self):
        self.results = []

    def visit_leaf(self, node: LeafNode) -> str:
        result = node.pane_id
        self.results.append(result)  # Accumulate results
        return result
```

### ❌ Renderer Performance Issues

```python
# DON'T: Expensive operations in render methods
def render_widget(self, widget: QWidget, pane_id: str,
                 painter: QPainter, rect: QRect) -> None:
    # Expensive database query on every paint!
    metadata = self.database.get_widget_metadata(widget.id)
    self.draw_metadata(painter, rect, metadata)

# DO: Cache expensive operations
def render_widget(self, widget: QWidget, pane_id: str,
                 painter: QPainter, rect: QRect) -> None:
    if widget.id not in self.metadata_cache:
        self.metadata_cache[widget.id] = self.database.get_widget_metadata(widget.id)
    metadata = self.metadata_cache[widget.id]
    self.draw_metadata(painter, rect, metadata)
```

### ❌ Validation Logic Errors

```python
# DON'T: Inconsistent validation results
def validate_tree(self, root: Optional[PaneNode]) -> ValidationResult:
    if root is None:
        return ValidationResult(False, ["No root node"])  # Inconsistent!
    # Empty should be valid, not an error

# DO: Consistent validation logic
def validate_tree(self, root: Optional[PaneNode]) -> ValidationResult:
    if root is None:
        return ValidationResult(True)  # Empty is valid
    return self.validate_tree_structure(root)
```

### ❌ Event Handler Side Effects

```python
# DON'T: Cause layout changes in event handlers
def handle_pane_click(self, pane_id: str, event: QMouseEvent) -> bool:
    # Direct layout modification can cause reentrancy!
    self.multisplit.close_pane(pane_id)
    return True

# DO: Use queued operations for layout changes
def handle_pane_click(self, pane_id: str, event: QMouseEvent) -> bool:
    # Queue operation for later execution
    QTimer.singleShot(0, lambda: self.multisplit.close_pane(pane_id))
    return True
```

---

## Quick Reference

### Core Protocols
| Protocol | Purpose | Required Methods |
|----------|---------|------------------|
| `WidgetProvider` | Widget creation/lifecycle | `provide_widget()`, `widget_closing()` |
| `NodeVisitor` | Tree traversal | `visit_leaf()`, `visit_split()` |
| `StateValidator` | State integrity | `validate_tree()`, `validate_pane()` |
| `InteractionHandler` | User interactions | `handle_pane_click()`, `handle_divider_drag()` |

### Visitor Types
| Visitor | Use Case | Return Type |
|---------|----------|-------------|
| `SearchVisitor` | Find matching nodes | `bool` |
| `CollectorVisitor` | Gather data | `T` (generic) |
| `TransformVisitor` | Modify structure | `PaneNode` |
| `MutableVisitor` | In-place changes | `T` (generic) |

### Renderer Types
| Renderer | Renders | Key Methods |
|----------|---------|-------------|
| `WidgetRenderer` | Widget appearance | `render_widget()`, `render_pane_header()` |
| `DividerRenderer` | Split dividers | `render_divider()`, `get_divider_width()` |
| `LayoutRenderer` | Overall layout | `render_background()`, `render_empty_state()` |

### Handler Categories
| Handler | Events | Purpose |
|---------|--------|---------|
| `InteractionHandler` | Mouse/keyboard | User input processing |
| `LifecycleHandler` | Widget/layout changes | State management |
| `ValidationHandler` | State checks | Error detection |

### Validation Protocols
| Validator | Validates | Returns |
|-----------|-----------|---------|
| `StateValidator` | Model integrity | `ValidationResult` |
| `WidgetValidator` | Provider compliance | `ValidationResult` |
| `TreeValidator` | Structure validity | `ValidationResult` |

---

## Validation Checklist

- ✅ All protocol methods are properly implemented
- ✅ Widget provider handles unknown IDs gracefully
- ✅ Visitors maintain proper state throughout traversal
- ✅ Renderers avoid expensive operations in paint methods
- ✅ Event handlers don't cause direct layout modifications
- ✅ Validation logic is consistent and comprehensive
- ✅ Async protocols handle cancellation properly
- ✅ Error handling covers all failure modes
- ✅ Protocol implementations are thread-safe where needed
- ✅ Memory usage is controlled in long-running operations

## Related Documents

- **[Public API](public-api.md)** - Widget methods and properties
- **[Signals](signals.md)** - Signal definitions and usage
- **[Widget Provider](../02-architecture/widget-provider.md)** - Provider pattern details
- **[Usage Guide](../06-guides/usage-guide.md)** - Implementation examples
- **[Integration Guide](../06-guides/integration-guide.md)** - Application integration
- **[Model Design](../04-design/model-design.md)** - Visitor pattern details
- **[View Design](../04-design/view-design.md)** - Rendering system
- **[Controller Design](../04-design/controller-design.md)** - Command validation

---

The protocol interfaces provide clean, extensible integration points for MultiSplit while maintaining type safety and clear separation of concerns.