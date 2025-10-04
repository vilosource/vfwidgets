"""Controller for MultiSplit widget.

Manages commands, transactions, and undo/redo stack.
"""

from dataclasses import dataclass, field

from ..core.model import PaneModel
from ..core.types import PaneId, WherePosition, WidgetId
from ..core.validation import OperationValidator, ValidationResult
from .commands import Command, RemovePaneCommand, SplitPaneCommand
from .transaction import TransactionContext


@dataclass
class PaneController:
    """Controller managing model mutations through commands."""

    model: PaneModel
    _undo_stack: list[Command] = field(default_factory=list)
    _redo_stack: list[Command] = field(default_factory=list)
    _transaction_depth: int = 0
    _transaction_commands: list[Command] = field(default_factory=list)
    _validator: OperationValidator = field(init=False)  # NEW

    # Configuration
    max_undo_levels: int = 100
    enable_validation: bool = True  # NEW

    def __post_init__(self):
        """Initialize controller."""
        self._validator = OperationValidator(self.model)

    def validate_and_execute(self, command: Command) -> tuple[bool, ValidationResult]:
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
        from .commands import SetRatiosCommand

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

    def execute_command(self, command: Command) -> bool:
        """Execute a command.

        Args:
            command: Command to execute

        Returns:
            True if successful
        """
        if not command.can_execute():
            return False

        success = command.execute()

        if success:
            if self._transaction_depth > 0:
                # Inside transaction
                self._transaction_commands.append(command)
            else:
                # Normal execution
                self._undo_stack.append(command)
                self._redo_stack.clear()

                # Limit undo stack
                if len(self._undo_stack) > self.max_undo_levels:
                    self._undo_stack.pop(0)

                # Emit signal
                self.model.signals.command_executed.emit(command.description())

        return success

    def undo(self) -> bool:
        """Undo last command."""
        if not self.can_undo():
            return False

        command = self._undo_stack.pop()
        success = command.undo()

        if success:
            self._redo_stack.append(command)
            self.model.signals.command_undone.emit(command.description())

        return success

    def redo(self) -> bool:
        """Redo last undone command."""
        if not self.can_redo():
            return False

        command = self._redo_stack.pop()
        success = command.execute()

        if success:
            self._undo_stack.append(command)
            self.model.signals.command_executed.emit(command.description())

        return success

    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self._undo_stack) > 0 and self._transaction_depth == 0

    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self._redo_stack) > 0 and self._transaction_depth == 0

    def clear_history(self):
        """Clear undo/redo history."""
        self._undo_stack.clear()
        self._redo_stack.clear()

    # High-level operations

    def split_pane(self, target_pane_id: PaneId, widget_id: WidgetId,
                   position: WherePosition, ratio: float = 0.5) -> tuple[bool, ValidationResult]:
        """Split a pane with validation.

        Returns:
            Tuple of (success, validation_result)
        """
        command = SplitPaneCommand(
            self.model, target_pane_id, widget_id, position, ratio
        )
        return self.validate_and_execute(command)

    def remove_pane(self, pane_id: PaneId) -> tuple[bool, ValidationResult]:
        """Remove a pane with validation.

        Returns:
            Tuple of (success, validation_result)
        """
        command = RemovePaneCommand(self.model, pane_id)
        return self.validate_and_execute(command)

    # Transaction support

    def _begin_transaction(self, context=None):
        """Begin a transaction."""
        self._transaction_depth += 1
        if self._transaction_depth == 1:
            self._transaction_commands.clear()

    def _commit_transaction(self, context=None):
        """Commit current transaction."""
        self._transaction_depth -= 1
        if self._transaction_depth == 0:
            # Create composite command
            if self._transaction_commands:
                # For now, just add all commands to undo stack
                self._undo_stack.extend(self._transaction_commands)
                self._redo_stack.clear()
            self._transaction_commands.clear()

    def _rollback_transaction(self, context=None):
        """Rollback current transaction."""
        self._transaction_depth -= 1
        if self._transaction_depth == 0:
            # Handle commands stored in transaction context (Phase 0 style)
            if context and hasattr(context, 'commands'):
                for command in reversed(context.commands):
                    try:
                        # Try Phase 0 style undo with model parameter
                        if hasattr(command, 'undo') and hasattr(self.model, 'value'):
                            command.undo(self.model)
                        # Try Phase 1 style undo without parameters
                        elif hasattr(command, 'undo') and hasattr(command, 'executed'):
                            if command.executed:
                                command.undo()
                    except Exception as e:
                        print(f"Error during rollback: {e}")

            # Handle commands stored in controller (Phase 1 style)
            for command in reversed(self._transaction_commands):
                if command.executed:
                    command.undo()
            self._transaction_commands.clear()

    def transaction(self):
        """Create transaction context."""
        return TransactionContext(self)

    def _end_transaction(self, context=None):
        """Clean up after transaction ends.

        Args:
            context: Transaction context that ended
        """
        # Already handled in commit/rollback, nothing additional needed
        pass

    # Compatibility methods for Phase 0 transaction system

    def _create_savepoint(self) -> dict:
        """Create a savepoint of current state.

        Returns:
            Savepoint data
        """
        # Check if model has to_dict method (PaneModel)
        if hasattr(self.model, 'to_dict'):
            return self.model.to_dict()
        else:
            # For mock models or other types, create simple savepoint
            return {'model_state': getattr(self.model, '__dict__', {})}

    def _restore_savepoint(self, savepoint: dict):
        """Restore from a savepoint.

        Args:
            savepoint: Savepoint data to restore
        """
        # Check if model has from_dict method (PaneModel)
        if hasattr(self.model, 'to_dict') and 'root' in savepoint:
            restored_model = PaneModel.from_dict(savepoint)
            self.model.root = restored_model.root
            self.model.focused_pane_id = restored_model.focused_pane_id
            self.model._rebuild_registry()
        else:
            # For mock models, try to restore basic state
            if 'model_state' in savepoint:
                for key, value in savepoint['model_state'].items():
                    setattr(self.model, key, value)

    @property
    def in_transaction(self) -> bool:
        """Check if currently in a transaction.

        Returns:
            True if in transaction
        """
        return self._transaction_depth > 0
