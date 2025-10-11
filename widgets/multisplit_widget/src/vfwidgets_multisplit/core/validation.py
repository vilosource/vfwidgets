"""Validation system for MultiSplit operations.

Provides real-time constraint checking and validation.
"""

from dataclasses import dataclass

from .model import PaneModel
from .tree_utils import validate_tree_structure
from .types import PaneId, WherePosition


@dataclass
class ValidationResult:
    """Result of validation check."""

    is_valid: bool
    errors: list[str]
    warnings: list[str]

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

    def validate_split(
        self, target_pane_id: PaneId, position: WherePosition, ratio: float = 0.5
    ) -> ValidationResult:
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

    def validate_ratios(self, node_id: str, ratios: list[float]) -> ValidationResult:
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
