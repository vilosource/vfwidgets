"""Tests for transaction management."""

import unittest

from vfwidgets_multisplit.controller.controller import PaneController
from vfwidgets_multisplit.controller.transaction import (
    TransactionContext,
    atomic_operation,
    transaction,
)


class MockModel:
    """Mock model for testing."""
    def __init__(self):
        self.value = 0
        self.history = []


class MockCommand:
    """Mock command for testing."""
    def __init__(self, value):
        self.value = value
        self.executed = False
        self.undone = False

    def execute(self, model):
        model.value += self.value
        model.history.append(f"add {self.value}")
        self.executed = True
        return True

    def undo(self, model):
        model.value -= self.value
        model.history.append(f"undo add {self.value}")
        self.undone = True
        return True


class TestTransactions(unittest.TestCase):
    """Test transaction management."""

    def test_basic_transaction(self):
        """Test basic transaction commit."""
        model = MockModel()
        controller = PaneController(model)

        with TransactionContext(controller) as tx:
            cmd = MockCommand(5)
            cmd.execute(model)
            tx.add_command(cmd)

        # Transaction should be committed
        self.assertTrue(tx.committed)
        self.assertFalse(tx.rolled_back)
        self.assertEqual(model.value, 5)

    def test_transaction_rollback(self):
        """Test transaction rollback on exception."""
        model = MockModel()
        controller = PaneController(model)

        try:
            with TransactionContext(controller) as tx:
                cmd = MockCommand(5)
                cmd.execute(model)
                tx.add_command(cmd)
                raise ValueError("Test error")
        except ValueError:
            pass

        # Transaction should be rolled back
        self.assertFalse(tx.committed)
        self.assertTrue(tx.rolled_back)

        # Command should be undone
        self.assertTrue(cmd.undone)

    def test_manual_rollback(self):
        """Test manual transaction rollback."""
        model = MockModel()
        controller = PaneController(model)

        with TransactionContext(controller) as tx:
            cmd = MockCommand(5)
            cmd.execute(model)
            tx.add_command(cmd)

            # Manually rollback
            tx.rollback()

        self.assertTrue(tx.rolled_back)
        self.assertFalse(tx.committed)

    def test_transaction_context_manager(self):
        """Test transaction convenience function."""
        model = MockModel()
        controller = PaneController(model)

        with transaction(controller) as tx:
            cmd = MockCommand(10)
            cmd.execute(model)
            tx.add_command(cmd)

        self.assertTrue(tx.committed)
        self.assertEqual(model.value, 10)

    def test_atomic_operation(self):
        """Test named atomic operation."""
        model = MockModel()
        controller = PaneController(model)

        with atomic_operation(controller, "test_operation") as tx:
            cmd = MockCommand(15)
            cmd.execute(model)
            tx.add_command(cmd)

        self.assertTrue(tx.committed)
        self.assertEqual(tx.operation_name, "test_operation")

    def test_transaction_status(self):
        """Test transaction status tracking."""
        model = MockModel()
        controller = PaneController(model)

        # Not in transaction initially
        self.assertFalse(controller.in_transaction)

        with TransactionContext(controller):
            # In transaction within context
            self.assertTrue(controller.in_transaction)

        # Not in transaction after exit
        self.assertFalse(controller.in_transaction)


if __name__ == '__main__':
    unittest.main()
