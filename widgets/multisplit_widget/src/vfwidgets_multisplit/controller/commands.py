"""Command pattern implementation for MultiSplit.

All model mutations go through commands for undo/redo support.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..core.logger import log_split_operation, log_tree_structure, logger
from ..core.model import PaneModel
from ..core.nodes import LeafNode, SplitNode
from ..core.types import (
    Direction,
    NodeId,
    PaneId,
    SizeConstraints,
    WherePosition,
    WidgetId,
)


class Command(ABC):
    """Abstract base class for commands."""

    def __init__(self, model: PaneModel):
        """Initialize command with model reference."""
        self.model = model
        self.executed = False
        self._state_before: Optional[Dict[str, Any]] = None

    @abstractmethod
    def execute(self) -> bool:
        """Execute the command.

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def undo(self) -> bool:
        """Undo the command.

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def description(self) -> str:
        """Get human-readable description."""
        pass

    def can_execute(self) -> bool:
        """Check if command can be executed."""
        return not self.executed

    def can_undo(self) -> bool:
        """Check if command can be undone."""
        return self.executed and self._state_before is not None


@dataclass
class SplitPaneCommand(Command):
    """Command to split a pane."""

    target_pane_id: PaneId
    new_widget_id: WidgetId
    position: WherePosition
    ratio: float = 0.5

    def __init__(self, model: PaneModel, target_pane_id: PaneId,
                 new_widget_id: WidgetId, position: WherePosition,
                 ratio: float = 0.5):
        """Initialize split command."""
        super().__init__(model)
        self.target_pane_id = target_pane_id
        self.new_widget_id = new_widget_id
        self.position = position
        self.ratio = ratio
        self._new_pane_id: Optional[PaneId] = None
        self._new_node_id: Optional[NodeId] = None

    def execute(self) -> bool:
        """Split the target pane."""
        if self.executed:
            return False

        # Log operation start
        log_split_operation(self.target_pane_id, self.new_widget_id,
                          self.position, self.ratio)
        log_tree_structure(self.model.root, "Tree BEFORE split")

        # Find target
        target = self.model.get_pane(self.target_pane_id)
        if not target:
            logger.error(f"Target pane not found: {self.target_pane_id}")
            return False

        logger.debug(f"Found target pane: {target}")

        # Save state
        self._state_before = self.model.to_dict()

        # Generate IDs
        from ..core.utils import generate_node_id, generate_pane_id
        self._new_pane_id = generate_pane_id()
        logger.info(f"Generated new pane ID: {self._new_pane_id}")

        # Create new leaf
        new_leaf = LeafNode(
            pane_id=self._new_pane_id,
            widget_id=self.new_widget_id
        )
        logger.debug(f"Created new leaf node with widget: {self.new_widget_id}")

        # Handle different split positions
        if self.position == WherePosition.REPLACE:
            # Simple replacement
            if target.parent:
                target.parent.replace_child(target, new_leaf)
            else:
                self.model.root = new_leaf

        elif self.position in (WherePosition.BEFORE, WherePosition.AFTER):
            # Insert as sibling
            if not target.parent:
                return False  # Can't insert sibling to root

            parent = target.parent
            idx = parent.children.index(target)

            if self.position == WherePosition.AFTER:
                idx += 1

            parent.children.insert(idx, new_leaf)
            new_leaf.parent = parent

            # Adjust ratios
            count = len(parent.children)
            parent.ratios = [1.0 / count] * count

        else:
            # Create split (LEFT, RIGHT, TOP, BOTTOM)
            orientation = self.position.to_orientation()
            if not orientation:
                return False

            self._new_node_id = generate_node_id()

            # Remember original parent before modifying tree
            original_parent = target.parent

            # Create new split node
            new_split = SplitNode(
                node_id=self._new_node_id,
                orientation=orientation,
                children=[],
                ratios=[]
            )

            # CRITICAL: Don't modify target's parent until AFTER we replace it in the tree!
            # First, replace target with the split in its original position
            if original_parent:
                original_parent.replace_child(target, new_split)
            else:
                self.model.root = new_split

            # NOW we can safely add children to the split
            # Arrange children based on position
            if self.position in (WherePosition.LEFT, WherePosition.TOP):
                new_split.add_child(new_leaf, self.ratio)
                new_split.add_child(target, 1.0 - self.ratio)
            else:
                new_split.add_child(target, 1.0 - self.ratio)
                new_split.add_child(new_leaf, self.ratio)

        # Update registry and emit signals
        self.model._rebuild_registry()
        self.model.signals.structure_changed.emit()
        self.model.signals.pane_added.emit(self._new_pane_id)

        # Log final tree state
        log_tree_structure(self.model.root, "Tree AFTER split")
        logger.info(f"Split operation SUCCESSFUL - New pane: {self._new_pane_id}")

        self.executed = True
        return True

    def undo(self) -> bool:
        """Undo the split."""
        if not self.can_undo():
            return False

        # Restore previous state
        restored_model = PaneModel.from_dict(self._state_before)
        self.model.root = restored_model.root
        self.model.focused_pane_id = restored_model.focused_pane_id

        # Update registry and emit signals
        self.model._rebuild_registry()
        self.model.signals.structure_changed.emit()

        if self._new_pane_id:
            self.model.signals.pane_removed.emit(self._new_pane_id)

        self.executed = False
        return True

    def description(self) -> str:
        """Get command description."""
        return f"Split pane {self.target_pane_id} {self.position.value}"


@dataclass
class RemovePaneCommand(Command):
    """Command to remove a pane."""

    pane_id: PaneId

    def __init__(self, model: PaneModel, pane_id: PaneId):
        """Initialize remove command."""
        super().__init__(model)
        self.pane_id = pane_id

    def execute(self) -> bool:
        """Remove the pane."""
        if self.executed:
            return False

        target = self.model.get_pane(self.pane_id)
        if not target:
            return False

        # Save state
        self._state_before = self.model.to_dict()

        # Handle removal based on parent
        if not target.parent:
            # Removing root
            self.model.root = None
        else:
            parent = target.parent
            parent.remove_child(target)

            # Handle parent with single child
            if len(parent.children) == 1:
                # Collapse: replace parent with remaining child
                remaining = parent.children[0]

                if parent.parent:
                    parent.parent.replace_child(parent, remaining)
                else:
                    self.model.root = remaining
                    remaining.parent = None

            elif len(parent.children) == 0:
                # Remove empty parent
                if parent.parent:
                    parent.parent.remove_child(parent)
                else:
                    self.model.root = None

        # Update state
        self.model._rebuild_registry()
        self.model.signals.structure_changed.emit()
        self.model.signals.pane_removed.emit(self.pane_id)

        self.executed = True
        return True

    def undo(self) -> bool:
        """Undo the removal."""
        if not self.can_undo():
            return False

        # Restore state
        restored_model = PaneModel.from_dict(self._state_before)
        self.model.root = restored_model.root
        self.model.focused_pane_id = restored_model.focused_pane_id

        # Update state
        self.model._rebuild_registry()
        self.model.signals.structure_changed.emit()
        self.model.signals.pane_added.emit(self.pane_id)

        self.executed = False
        return True

    def description(self) -> str:
        """Get command description."""
        return f"Remove pane {self.pane_id}"


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

    def can_undo(self) -> bool:
        """Check if command can be undone."""
        return self.executed

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

    def can_undo(self) -> bool:
        """Check if command can be undone."""
        return self.executed

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

    def can_undo(self) -> bool:
        """Check if command can be undone."""
        return self.executed

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
        return "Adjust split ratios"


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
