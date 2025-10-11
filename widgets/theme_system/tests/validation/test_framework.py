#!/usr/bin/env python3
"""
Test suite for validation framework - Task 24
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from vfwidgets_theme.validation import (
    ThemeProtocol,
    ThemeSchema,
    ValidationFramework,
    ValidationMode,
    ValidationType,
    validate_protocol_implementation,
    validate_theme,
)


class TestValidationFramework:
    """Test the core validation framework."""

    def setup_method(self):
        """Reset validation framework for each test."""
        ValidationFramework.reset_instance()

    def test_singleton_pattern(self):
        """Test that ValidationFramework follows singleton pattern."""
        framework1 = ValidationFramework()
        framework2 = ValidationFramework()
        assert framework1 is framework2

    def test_mode_switching(self):
        """Test validation mode switching."""
        framework = ValidationFramework(ValidationMode.DEBUG)
        assert framework.mode == ValidationMode.DEBUG

        framework.set_mode(ValidationMode.PRODUCTION)
        assert framework.mode == ValidationMode.PRODUCTION

    def test_validation_enabled_check(self):
        """Test validation enablement checks."""
        framework = ValidationFramework(ValidationMode.DISABLED)
        assert not framework.is_validation_enabled()

        framework.set_mode(ValidationMode.DEBUG)
        assert framework.is_validation_enabled()
        assert framework.is_validation_enabled(ValidationType.PERFORMANCE)

        framework.set_mode(ValidationMode.PRODUCTION)
        assert framework.is_validation_enabled()
        assert not framework.is_validation_enabled(ValidationType.PERFORMANCE)

    def test_theme_structure_validation(self):
        """Test theme structure validation."""
        framework = ValidationFramework(ValidationMode.DEBUG)

        # Valid theme
        class ValidTheme:
            def __init__(self):
                self.name = "test_theme"
                self.colors = {"primary": "#007acc"}
                self.styles = {"font_size": "12px"}

        result = framework.validate_theme_structure(ValidTheme())
        assert result.passed
        assert not result.has_errors

        # Invalid theme - missing name
        class InvalidTheme:
            def __init__(self):
                self.colors = {"primary": "#007acc"}
                self.styles = {"font_size": "12px"}

        result = framework.validate_theme_structure(InvalidTheme())
        assert not result.passed
        assert result.has_errors
        assert any("missing 'name' attribute" in error for error in result.errors)

    def test_contract_validation(self):
        """Test contract validation."""
        framework = ValidationFramework(ValidationMode.DEBUG)

        # Mock theme protocol
        class MockProtocol:
            name: str
            colors: dict

            def get_color(self, name: str) -> str:
                pass

        # Valid implementation
        class ValidTheme:
            def __init__(self):
                self.name = "test"
                self.colors = {}

            def get_color(self, name: str) -> str:
                return self.colors.get(name)

        result = framework.validate_contract_implementation(ValidTheme(), MockProtocol)
        assert result.passed or not result.has_errors  # Basic implementation may have warnings

    def test_runtime_state_validation(self):
        """Test runtime state validation."""
        framework = ValidationFramework(ValidationMode.DEBUG)

        class TestObject:
            def __init__(self):
                self.value = 42
                self.name = "test"

        obj = TestObject()
        expected_state = {"value": 42, "name": "test"}

        result = framework.validate_runtime_state(obj, expected_state)
        assert result.passed
        assert not result.has_errors

        # Test with validation function
        expected_state_func = {"value": lambda x: x > 0, "name": lambda x: isinstance(x, str)}

        result = framework.validate_runtime_state(obj, expected_state_func)
        assert result.passed

    def test_performance_validation(self):
        """Test performance validation."""
        framework = ValidationFramework(ValidationMode.DEBUG)

        # Set threshold
        framework.set_performance_threshold("test_operation", 0.1)  # 100ms

        # Test within threshold
        result = framework.validate_performance_constraints("test_operation", 50.0)  # 50ms
        assert result.passed
        assert not result.has_errors

        # Test exceeding threshold
        result = framework.validate_performance_constraints("test_operation", 150.0)  # 150ms
        assert not result.passed
        assert result.has_errors

    def test_validation_context(self):
        """Test validation context manager."""
        framework = ValidationFramework(ValidationMode.DEBUG)

        with framework.validation_context(ValidationType.SCHEMA) as result:
            assert result.passed
            # Context should track timing
            pass

        assert result.duration_ms >= 0
        assert len(framework._results) == 1

    def test_custom_validator_registration(self):
        """Test custom validator registration."""
        framework = ValidationFramework(ValidationMode.DEBUG)

        def custom_validator(theme, result):
            if not hasattr(theme, "custom_property"):
                result.add_error("Missing custom property")

        framework.register_validator(ValidationType.SCHEMA, custom_validator)

        class ThemeWithoutCustom:
            def __init__(self):
                self.name = "test"
                self.colors = {}
                self.styles = {}

        result = framework.validate_theme_structure(ThemeWithoutCustom())
        assert result.has_errors
        assert any("custom property" in error.lower() for error in result.errors)


class TestValidationDecorators:
    """Test validation decorators."""

    def test_validate_theme_decorator(self):
        """Test theme validation decorator."""
        ValidationFramework.reset_instance()
        ValidationFramework(ValidationMode.DEBUG)

        @validate_theme
        def process_theme(theme):
            return f"Processing {theme.name}"

        # Valid theme
        class ValidTheme:
            def __init__(self):
                self.name = "test"
                self.colors = {"primary": "#007acc"}
                self.styles = {"font_size": "12px"}

        # Should work without errors
        result = process_theme(ValidTheme())
        assert result == "Processing test"

        # Invalid theme in non-strict mode should warn but not raise
        class InvalidTheme:
            def __init__(self):
                self.colors = {}
                self.styles = {}

        # Should work but log warning
        result = process_theme(InvalidTheme())
        assert "Processing" in result


class TestSchemaValidation:
    """Test schema validation."""

    def test_theme_schema(self):
        """Test theme schema validation."""
        schema = ThemeSchema()

        # Valid theme data
        valid_data = {
            "name": "test_theme",
            "colors": {"primary": "#007acc"},
            "styles": {"font_size": "12px"},
        }

        result = schema.validate(valid_data)
        assert result.passed
        assert not result.has_errors

        # Invalid theme data
        invalid_data = {
            "colors": {"primary": "#007acc"},
            "styles": {"font_size": "12px"},
            # Missing required 'name'
        }

        result = schema.validate(invalid_data)
        assert not result.passed
        assert result.has_errors


class TestContractValidation:
    """Test contract validation."""

    def test_theme_protocol_validation(self):
        """Test theme protocol validation."""

        # Create mock theme that implements protocol
        class MockTheme:
            def __init__(self):
                self.name = "mock"
                self.colors = {"primary": "#007acc"}
                self.styles = {"font_size": "12px"}

            def get_color(self, color_name: str) -> str:
                return self.colors.get(color_name)

            def get_style(self, style_name: str):
                return self.styles.get(style_name)

            def to_dict(self):
                return {"name": self.name, "colors": self.colors, "styles": self.styles}

        theme = MockTheme()
        result = validate_protocol_implementation(theme, ThemeProtocol)

        # Should pass basic validation (may have warnings)
        assert not result.has_errors or len(result.errors) == 0


if __name__ == "__main__":
    # Run basic tests
    test_framework = TestValidationFramework()
    test_framework.setup_method()

    print("Testing ValidationFramework...")

    # Test singleton
    test_framework.test_singleton_pattern()
    print("✓ Singleton pattern works")

    # Test mode switching
    test_framework.test_mode_switching()
    print("✓ Mode switching works")

    # Test validation enablement
    test_framework.test_validation_enabled_check()
    print("✓ Validation enablement check works")

    # Test theme validation
    test_framework.test_theme_structure_validation()
    print("✓ Theme structure validation works")

    # Test performance validation
    test_framework.test_performance_validation()
    print("✓ Performance validation works")

    print("\nAll validation framework tests passed!")
