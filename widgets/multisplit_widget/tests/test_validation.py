"""Tests for validation system."""

import unittest

from vfwidgets_multisplit.core.model import PaneModel
from vfwidgets_multisplit.core.nodes import LeafNode
from vfwidgets_multisplit.core.types import PaneId, WherePosition, WidgetId
from vfwidgets_multisplit.core.validation import OperationValidator, ValidationResult


class TestOperationValidator(unittest.TestCase):
    """Test operation validation."""

    def setUp(self):
        """Set up test data."""
        self.model = PaneModel()
        self.validator = OperationValidator(self.model)

    def test_split_validation_empty_model(self):
        """Test split validation on empty model."""
        result = self.validator.validate_split(PaneId("invalid"), WherePosition.RIGHT)
        self.assertFalse(result.is_valid)
        self.assertIn("not found", result.errors[0])

    def test_split_validation_valid(self):
        """Test valid split operation."""
        # Add a pane
        self.model.root = LeafNode(PaneId("p1"), WidgetId("w1"))
        self.model._rebuild_registry()

        # Test valid split
        result = self.validator.validate_split(PaneId("p1"), WherePosition.RIGHT, 0.5)
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)

    def test_split_validation_invalid_ratio(self):
        """Test split with invalid ratio."""
        # Add a pane
        self.model.root = LeafNode(PaneId("p1"), WidgetId("w1"))
        self.model._rebuild_registry()

        # Test invalid ratio
        result = self.validator.validate_split(PaneId("p1"), WherePosition.RIGHT, 0.01)
        self.assertFalse(result.is_valid)
        self.assertIn("must be between", result.errors[0])

    def test_remove_validation_last_pane(self):
        """Test remove validation for last pane."""
        # Add a pane
        self.model.root = LeafNode(PaneId("p1"), WidgetId("w1"))
        self.model._rebuild_registry()

        result = self.validator.validate_remove(PaneId("p1"))
        self.assertTrue(result.is_valid)
        self.assertIn("last pane", result.warnings[0])

    def test_remove_validation_nonexistent(self):
        """Test remove validation for nonexistent pane."""
        result = self.validator.validate_remove(PaneId("invalid"))
        self.assertFalse(result.is_valid)
        self.assertIn("not found", result.errors[0])

    def test_ratios_validation_valid(self):
        """Test valid ratios validation."""
        result = self.validator.validate_ratios("node1", [0.3, 0.7])
        self.assertTrue(result.is_valid)

    def test_ratios_validation_invalid_sum(self):
        """Test ratios that don't sum to 1.0."""
        result = self.validator.validate_ratios("node1", [0.3, 0.5])
        self.assertFalse(result.is_valid)
        self.assertIn("must sum to 1.0", result.errors[0])

    def test_ratios_validation_too_small(self):
        """Test ratios that are too small."""
        result = self.validator.validate_ratios("node1", [0.01, 0.99])
        self.assertFalse(result.is_valid)
        self.assertIn("minimum is 0.05", result.errors[0])

    def test_model_state_validation_empty(self):
        """Test model state validation for empty model."""
        result = self.validator.validate_model_state()
        self.assertTrue(result.is_valid)

    def test_model_state_validation_valid(self):
        """Test model state validation for valid model."""
        self.model.root = LeafNode(PaneId("p1"), WidgetId("w1"))
        self.model._rebuild_registry()

        result = self.validator.validate_model_state()
        self.assertTrue(result.is_valid)


class TestValidationResult(unittest.TestCase):
    """Test validation result functionality."""

    def test_validation_result_creation(self):
        """Test validation result creation."""
        result = ValidationResult(is_valid=True, errors=[], warnings=[])
        self.assertTrue(result.is_valid)

    def test_add_error(self):
        """Test adding error makes result invalid."""
        result = ValidationResult(is_valid=True, errors=[], warnings=[])
        result.add_error("Test error")

        self.assertFalse(result.is_valid)
        self.assertIn("Test error", result.errors)

    def test_add_warning(self):
        """Test adding warning keeps result valid."""
        result = ValidationResult(is_valid=True, errors=[], warnings=[])
        result.add_warning("Test warning")

        self.assertTrue(result.is_valid)
        self.assertIn("Test warning", result.warnings)


if __name__ == '__main__':
    unittest.main()
