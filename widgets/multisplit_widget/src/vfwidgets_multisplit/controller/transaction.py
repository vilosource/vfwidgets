"""Transaction management for atomic operations.

Provides context managers for atomic command execution
with automatic rollback on failure.
"""

from contextlib import contextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .command import Command
    from .controller import PaneController


class TransactionContext:
    """Context manager for atomic command transactions."""

    def __init__(self, controller: 'PaneController'):
        """Initialize transaction context.

        Args:
            controller: Controller managing this transaction
        """
        self.controller = controller
        self.commands: list[Command] = []
        self.rolled_back = False
        self.committed = False
        self.savepoint = None

    def __enter__(self):
        """Begin transaction context."""
        # Save current state for potential rollback
        self.savepoint = self.controller._create_savepoint()
        self.controller._begin_transaction(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End transaction context.

        Args:
            exc_type: Exception type if error occurred
            exc_val: Exception value
            exc_tb: Exception traceback

        Returns:
            False to propagate exceptions
        """
        if exc_type or self.rolled_back:
            # Exception occurred or manual rollback
            self.rolled_back = True
            self.controller._rollback_transaction(self)
            if self.savepoint:
                self.controller._restore_savepoint(self.savepoint)
        else:
            # Successful completion
            self.controller._commit_transaction(self)
            self.committed = True

        # Always cleanup
        self.controller._end_transaction(self)
        return False  # Don't suppress exceptions

    def add_command(self, command: 'Command'):
        """Add command to transaction.

        Args:
            command: Command executed within this transaction
        """
        self.commands.append(command)

    def rollback(self):
        """Mark transaction for rollback."""
        self.rolled_back = True


class NestedTransactionContext(TransactionContext):
    """Context for nested transactions."""

    def __init__(self, controller: 'PaneController', parent: TransactionContext):
        """Initialize nested transaction.

        Args:
            controller: Controller managing this transaction
            parent: Parent transaction context
        """
        super().__init__(controller)
        self.parent = parent

    def __enter__(self):
        """Begin nested transaction."""
        # Don't create new savepoint, use parent's
        self.controller._begin_nested_transaction(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End nested transaction."""
        if exc_type or self.rolled_back:
            # Propagate rollback to parent
            self.rolled_back = True
            self.parent.rollback()
        else:
            # Add our commands to parent
            for cmd in self.commands:
                self.parent.add_command(cmd)

        self.controller._end_nested_transaction(self)
        return False


@contextmanager
def transaction(controller: 'PaneController'):
    """Convenience context manager for transactions.

    Args:
        controller: Controller to manage transaction

    Yields:
        TransactionContext for the transaction
    """
    context = TransactionContext(controller)
    try:
        with context:
            yield context
    except Exception:
        # Context handles rollback
        raise


@contextmanager
def atomic_operation(controller: 'PaneController', name: str):
    """Named atomic operation for better debugging.

    Args:
        controller: Controller to manage operation
        name: Name of the operation for logging

    Yields:
        TransactionContext for the operation
    """
    context = TransactionContext(controller)
    context.operation_name = name

    try:
        with context:
            yield context
    except Exception as e:
        # Log the failed operation
        print(f"Atomic operation '{name}' failed: {e}")
        raise
