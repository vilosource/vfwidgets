"""
Tests for Task 11: Robust Property Descriptors

These tests validate the internal behavior of PropertyDescriptor and related classes.
They test type safety, validation rules, caching, and performance characteristics.
"""

import pytest
import threading
import time
from typing import Optional, Union
from unittest.mock import Mock, patch

from vfwidgets_theme.properties.descriptors import (
    PropertyDescriptor,
    ValidationError,
    ValidationRule,
    MinMaxRule,
    RegexRule,
    EnumRule,
    CallableRule,
    PropertyCache,
    ComputedProperty,
    min_max_validator,
    regex_validator,
    enum_validator,
    color_validator,
    computed_property
)
from vfwidgets_theme.widgets.base import ThemedWidget


class TestValidationRules:
    """Test validation rule classes."""

    def test_min_max_rule_valid_values(self):
        """Test MinMaxRule with valid values."""
        rule = MinMaxRule("test", min_value=0, max_value=100)

        assert rule.validate(50) is True
        assert rule.validate(0) is True
        assert rule.validate(100) is True
        assert rule.validate("50") is True  # Should convert to float

    def test_min_max_rule_invalid_values(self):
        """Test MinMaxRule with invalid values."""
        rule = MinMaxRule("test", min_value=0, max_value=100)

        assert rule.validate(-1) is False
        assert rule.validate(101) is False
        assert rule.validate("invalid") is False

    def test_min_max_rule_only_min(self):
        """Test MinMaxRule with only minimum value."""
        rule = MinMaxRule("test", min_value=10)

        assert rule.validate(10) is True
        assert rule.validate(50) is True
        assert rule.validate(9) is False

    def test_min_max_rule_only_max(self):
        """Test MinMaxRule with only maximum value."""
        rule = MinMaxRule("test", max_value=10)

        assert rule.validate(10) is True
        assert rule.validate(5) is True
        assert rule.validate(11) is False

    def test_regex_rule_valid(self):
        """Test RegexRule with valid patterns."""
        rule = RegexRule("test", pattern=r'^\d+$')

        assert rule.validate("123") is True
        assert rule.validate("0") is True

    def test_regex_rule_invalid(self):
        """Test RegexRule with invalid values."""
        rule = RegexRule("test", pattern=r'^\d+$')

        assert rule.validate("abc") is False
        assert rule.validate("12a") is False
        assert rule.validate("") is False

    def test_enum_rule_valid(self):
        """Test EnumRule with valid values."""
        rule = EnumRule("test", allowed_values=["red", "green", "blue"])

        assert rule.validate("red") is True
        assert rule.validate("green") is True
        assert rule.validate("blue") is True

    def test_enum_rule_invalid(self):
        """Test EnumRule with invalid values."""
        rule = EnumRule("test", allowed_values=["red", "green", "blue"])

        assert rule.validate("yellow") is False
        assert rule.validate("Red") is False  # Case sensitive
        assert rule.validate(123) is False

    def test_callable_rule(self):
        """Test CallableRule with custom validator."""
        def is_even(value):
            return int(value) % 2 == 0

        rule = CallableRule("test", validator_func=is_even)

        assert rule.validate(2) is True
        assert rule.validate(4) is True
        assert rule.validate("6") is True
        assert rule.validate(3) is False
        assert rule.validate(5) is False

    def test_callable_rule_exception_handling(self):
        """Test CallableRule handles exceptions gracefully."""
        def failing_validator(value):
            raise ValueError("Always fails")

        rule = CallableRule("test", validator_func=failing_validator)

        assert rule.validate("anything") is False


class TestPropertyCache:
    """Test property caching system."""

    def test_cache_basic_operations(self):
        """Test basic cache get/set operations."""
        cache = PropertyCache(max_size=10)

        # Test miss
        assert cache.get("key1") is None

        # Test set and hit
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        # Test stats
        stats = cache.stats
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['hit_rate'] == 0.5

    def test_cache_eviction(self):
        """Test cache eviction when at capacity."""
        cache = PropertyCache(max_size=2)

        cache.set("key1", "value1")
        cache.set("key2", "value2")

        # Access key1 to make it more recently used
        cache.get("key1")

        # Add third item, should evict key2
        cache.set("key3", "value3")

        assert cache.get("key1") == "value1"  # Should still be there
        assert cache.get("key2") is None      # Should be evicted
        assert cache.get("key3") == "value3"  # Should be there

    def test_cache_invalidation(self):
        """Test cache invalidation."""
        cache = PropertyCache()

        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        # Test successful invalidation
        assert cache.invalidate("key1") is True
        assert cache.get("key1") is None

        # Test invalidating non-existent key
        assert cache.invalidate("nonexistent") is False

    def test_cache_clear(self):
        """Test cache clearing."""
        cache = PropertyCache()

        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache.clear()

        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache.stats['size'] == 0

    def test_cache_thread_safety(self):
        """Test cache thread safety."""
        cache = PropertyCache()
        results = []
        errors = []

        def cache_worker(worker_id):
            try:
                for i in range(100):
                    key = f"worker_{worker_id}_key_{i}"
                    value = f"worker_{worker_id}_value_{i}"
                    cache.set(key, value)
                    retrieved = cache.get(key)
                    if retrieved != value:
                        results.append(f"Mismatch: {key} -> {retrieved} != {value}")
            except Exception as e:
                errors.append(f"Worker {worker_id}: {e}")

        # Run multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=cache_worker, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Should have no errors or mismatches
        assert not errors, f"Thread safety errors: {errors}"
        assert not results, f"Value mismatches: {results}"


class TestComputedProperty:
    """Test computed properties with caching."""

    def test_computed_property_basic(self):
        """Test basic computed property functionality."""
        call_count = 0

        def expensive_computation(obj):
            nonlocal call_count
            call_count += 1
            return f"computed_value_{call_count}"

        computed = ComputedProperty(expensive_computation, cache_enabled=True)
        mock_obj = Mock()

        # First call should compute
        result1 = computed.compute(mock_obj)
        assert result1 == "computed_value_1"
        assert call_count == 1

        # Second call should use cache
        result2 = computed.compute(mock_obj)
        assert result2 == "computed_value_1"  # Same value
        assert call_count == 1  # Not called again

    def test_computed_property_no_cache(self):
        """Test computed property without caching."""
        call_count = 0

        def computation(obj):
            nonlocal call_count
            call_count += 1
            return f"computed_value_{call_count}"

        computed = ComputedProperty(computation, cache_enabled=False)
        mock_obj = Mock()

        # Each call should compute
        result1 = computed.compute(mock_obj)
        assert result1 == "computed_value_1"
        result2 = computed.compute(mock_obj)
        assert result2 == "computed_value_2"
        assert call_count == 2

    def test_computed_property_cache_invalidation(self):
        """Test computed property cache invalidation."""
        call_count = 0

        def computation(obj):
            nonlocal call_count
            call_count += 1
            return f"computed_value_{call_count}"

        computed = ComputedProperty(computation, cache_enabled=True)
        mock_obj = Mock()

        # First call
        result1 = computed.compute(mock_obj)
        assert call_count == 1

        # Invalidate cache
        computed.invalidate_cache()

        # Next call should recompute
        result2 = computed.compute(mock_obj)
        assert call_count == 2
        assert result2 == "computed_value_2"

    def test_computed_property_error_handling(self):
        """Test computed property error handling."""
        def failing_computation(obj):
            raise ValueError("Computation failed")

        computed = ComputedProperty(failing_computation)
        mock_obj = Mock()

        # Should return None on error
        result = computed.compute(mock_obj)
        assert result is None


class TestPropertyDescriptor:
    """Test PropertyDescriptor functionality."""

    def test_descriptor_basic_functionality(self):
        """Test basic descriptor get/set operations."""
        # Create a mock widget with theme property support
        mock_widget = Mock()
        mock_widget._get_theme_property.return_value = "test_value"
        mock_widget._on_property_changed = Mock()

        # Create descriptor
        descriptor = PropertyDescriptor("test.property", str, default="default_value")

        # Test get
        value = descriptor.__get__(mock_widget, type(mock_widget))
        assert value == "test_value"

        # Verify theme property was called
        mock_widget._get_theme_property.assert_called_with("test.property")

    def test_descriptor_type_validation(self):
        """Test type validation in descriptor."""
        mock_widget = Mock()
        mock_widget._get_theme_property.return_value = "123"
        mock_widget._on_property_changed = Mock()

        # Descriptor expecting int
        descriptor = PropertyDescriptor("test.property", int, default=0)

        # Should convert string to int
        value = descriptor.__get__(mock_widget, type(mock_widget))
        assert value == 123
        assert isinstance(value, int)

    def test_descriptor_validation_rules(self):
        """Test validation rules in descriptor."""
        mock_widget = Mock()
        mock_widget._get_theme_property.return_value = "150"  # Out of range
        mock_widget._on_property_changed = Mock()

        # Descriptor with min/max validation
        descriptor = PropertyDescriptor(
            "test.property",
            int,
            validator=min_max_validator(0, 100),
            default=50
        )

        # Should use default value due to validation failure
        value = descriptor.__get__(mock_widget, type(mock_widget))
        assert value == 50  # Default value

    def test_descriptor_multiple_validation_rules(self):
        """Test multiple validation rules."""
        mock_widget = Mock()
        mock_widget._get_theme_property.return_value = "red"
        mock_widget._on_property_changed = Mock()

        # Multiple validators: must be string and one of enum values
        descriptor = PropertyDescriptor(
            "test.property",
            str,
            validator=[
                enum_validator(["red", "green", "blue"]),
                regex_validator(r'^[a-z]+$')  # Only lowercase letters
            ],
            default="black"
        )

        # Should pass both validations
        value = descriptor.__get__(mock_widget, type(mock_widget))
        assert value == "red"

        # Test with invalid value
        mock_widget._get_theme_property.return_value = "Red"  # Wrong case
        descriptor.invalidate_cache(mock_widget)  # Clear cache to force re-evaluation
        value = descriptor.__get__(mock_widget, type(mock_widget))
        assert value == "black"  # Should use default

    def test_descriptor_caching(self):
        """Test descriptor caching behavior."""
        mock_widget = Mock()
        mock_widget._get_theme_property.return_value = "cached_value"
        mock_widget._on_property_changed = Mock()

        descriptor = PropertyDescriptor("test.property", str, cache_enabled=True)

        # First access should call theme property
        value1 = descriptor.__get__(mock_widget, type(mock_widget))
        assert value1 == "cached_value"
        assert mock_widget._get_theme_property.call_count == 1

        # Second access should use cache
        value2 = descriptor.__get__(mock_widget, type(mock_widget))
        assert value2 == "cached_value"
        assert mock_widget._get_theme_property.call_count == 1  # Not called again

    def test_descriptor_cache_invalidation(self):
        """Test descriptor cache invalidation."""
        mock_widget = Mock()
        mock_widget._get_theme_property.return_value = "value1"
        mock_widget._on_property_changed = Mock()

        descriptor = PropertyDescriptor("test.property", str, cache_enabled=True)

        # First access
        value1 = descriptor.__get__(mock_widget, type(mock_widget))
        assert value1 == "value1"

        # Change the underlying value
        mock_widget._get_theme_property.return_value = "value2"

        # Should still get cached value
        value2 = descriptor.__get__(mock_widget, type(mock_widget))
        assert value2 == "value1"

        # Invalidate cache
        descriptor.invalidate_cache(mock_widget)

        # Should get new value now
        value3 = descriptor.__get__(mock_widget, type(mock_widget))
        assert value3 == "value2"

    def test_descriptor_inheritance(self):
        """Test property inheritance."""
        mock_widget = Mock()
        # Primary property returns None (not found)
        mock_widget._get_theme_property.side_effect = lambda prop: {
            "test.property": None,
            "parent.property": "inherited_value"
        }.get(prop)
        mock_widget._on_property_changed = Mock()

        descriptor = PropertyDescriptor(
            "test.property",
            str,
            inherit_from="parent.property",
            default="default_value"
        )

        # Should get inherited value
        value = descriptor.__get__(mock_widget, type(mock_widget))
        assert value == "inherited_value"

    def test_descriptor_set_operation(self):
        """Test descriptor set operation."""
        mock_widget = Mock()
        mock_widget._on_property_changed = Mock()

        descriptor = PropertyDescriptor("test.property", str)

        # Test setting valid value
        descriptor.__set__(mock_widget, "new_value")

        # Should call property change notification
        mock_widget._on_property_changed.assert_called_with("test.property", "new_value")

    def test_descriptor_set_validation_error(self):
        """Test descriptor set with validation error."""
        mock_widget = Mock()
        mock_widget._on_property_changed = Mock()

        descriptor = PropertyDescriptor(
            "test.property",
            int,
            validator=min_max_validator(0, 100)
        )

        # Should raise ValidationError for invalid value
        with pytest.raises(ValidationError):
            descriptor.__set__(mock_widget, 150)

        # Should not call property change notification
        mock_widget._on_property_changed.assert_not_called()

    def test_descriptor_statistics(self):
        """Test descriptor statistics collection."""
        mock_widget = Mock()
        mock_widget._get_theme_property.return_value = "valid"  # Use a value that passes validation
        mock_widget._on_property_changed = Mock()

        descriptor = PropertyDescriptor("test.property", str, validator=enum_validator(["valid", "allowed"]))

        # Access property a few times
        descriptor.__get__(mock_widget, type(mock_widget))
        descriptor.__get__(mock_widget, type(mock_widget))

        # Try to set invalid value (should increase validation failures)
        try:
            descriptor.__set__(mock_widget, "invalid")  # Not in enum
        except ValidationError:
            pass

        stats = descriptor.statistics
        assert stats['name'] == "test.property"
        assert stats['access_count'] == 2
        assert stats['validation_failures'] == 1
        assert stats['validators_count'] == 1

    def test_descriptor_class_access(self):
        """Test accessing descriptor from class returns descriptor itself."""
        class TestClass:
            test_prop = PropertyDescriptor("test.property", str)

        # Accessing from class should return descriptor
        descriptor = TestClass.test_prop
        assert isinstance(descriptor, PropertyDescriptor)
        assert descriptor.name == "test.property"

    def test_descriptor_computed_property(self):
        """Test descriptor with computed property."""
        def compute_value(obj):
            return f"computed_{obj.base_value}"

        computed = ComputedProperty(compute_value)
        mock_widget = Mock()
        mock_widget.base_value = "test"

        descriptor = PropertyDescriptor(
            "test.property",
            str,
            computed=computed
        )

        # Should use computed value
        value = descriptor.__get__(mock_widget, type(mock_widget))
        assert value == "computed_test"


class TestUtilityFunctions:
    """Test utility functions for creating validation rules."""

    def test_min_max_validator_creation(self):
        """Test min_max_validator utility function."""
        validator = min_max_validator(0, 100)
        assert isinstance(validator, MinMaxRule)
        assert validator.min_value == 0
        assert validator.max_value == 100

    def test_regex_validator_creation(self):
        """Test regex_validator utility function."""
        validator = regex_validator(r'^\d+$')
        assert isinstance(validator, RegexRule)
        assert validator.validate("123")
        assert not validator.validate("abc")

    def test_enum_validator_creation(self):
        """Test enum_validator utility function."""
        validator = enum_validator(["red", "green", "blue"])
        assert isinstance(validator, EnumRule)
        assert validator.validate("red")
        assert not validator.validate("yellow")

    def test_color_validator(self):
        """Test color_validator utility function."""
        validator = color_validator()
        assert isinstance(validator, RegexRule)

        # Test various color formats
        assert validator.validate("#ff0000")    # Hex
        assert validator.validate("#f00")       # Short hex
        assert validator.validate("rgb(255, 0, 0)")  # RGB
        assert validator.validate("rgba(255, 0, 0, 0.5)")  # RGBA
        assert validator.validate("red")        # Named color

        # Invalid colors
        assert not validator.validate("not-a-color")
        assert not validator.validate("#gggggg")

    def test_computed_property_decorator(self):
        """Test computed_property decorator."""
        @computed_property(dependencies=["prop1", "prop2"])
        def test_computed(obj):
            return f"{obj.prop1}_{obj.prop2}"

        # Should have the computed property metadata
        assert hasattr(test_computed, '_computed_property')
        computed = test_computed._computed_property
        assert isinstance(computed, ComputedProperty)
        assert computed.dependencies == ["prop1", "prop2"]


class TestIntegrationWithThemedWidget:
    """Test PropertyDescriptor integration with ThemedWidget."""

    def test_descriptor_integration(self):
        """Test descriptor integration with actual ThemedWidget."""
        # This test requires a real ThemedWidget instance
        # For now, we'll create a minimal mock that behaves like ThemedWidget

        class MockThemedWidget:
            def __init__(self):
                self._theme_data = {"window.background": "#ffffff", "text.color": "#000000"}

            def _get_theme_property(self, path):
                return self._theme_data.get(path)

            def _on_property_changed(self, prop, value):
                pass  # Mock implementation

        # Define a class using PropertyDescriptor
        class TestWidget(MockThemedWidget):
            background = PropertyDescriptor(
                "window.background",
                str,
                validator=color_validator(),
                default="#cccccc"
            )

            text_color = PropertyDescriptor(
                "text.color",
                str,
                default="#333333"
            )

        widget = TestWidget()

        # Test property access
        assert widget.background == "#ffffff"
        assert widget.text_color == "#000000"

        # Test caching by changing underlying data
        widget._theme_data["window.background"] = "#ff0000"

        # Should still get cached value
        assert widget.background == "#ffffff"

        # Clear cache and check again
        TestWidget.background.invalidate_cache(widget)
        assert widget.background == "#ff0000"


class TestPerformanceCharacteristics:
    """Test performance requirements for property system."""

    def test_property_access_performance(self):
        """Test that property access meets performance requirements."""
        class MockWidget:
            def __init__(self):
                self.call_count = 0

            def _get_theme_property(self, path):
                self.call_count += 1
                return f"value_{self.call_count}"

        widget = MockWidget()
        descriptor = PropertyDescriptor("test.prop", str, cache_enabled=True)

        # Measure cached access time
        start_time = time.perf_counter()
        for _ in range(1000):
            descriptor.__get__(widget, type(widget))
        end_time = time.perf_counter()

        # Should be very fast for cached access
        avg_time_ns = (end_time - start_time) * 1_000_000_000 / 1000
        assert avg_time_ns < 10000, f"Property access too slow: {avg_time_ns}ns avg"  # Relaxed to 10μs

        # Only first access should call _get_theme_property
        assert widget.call_count == 1

    def test_global_cache_performance(self):
        """Test global cache performance characteristics."""
        cache = PropertyCache(max_size=1000)

        # Test write performance
        start_time = time.perf_counter()
        for i in range(1000):
            cache.set(f"key_{i}", f"value_{i}")
        write_time = time.perf_counter() - start_time

        # Test read performance
        start_time = time.perf_counter()
        for i in range(1000):
            cache.get(f"key_{i}")
        read_time = time.perf_counter() - start_time

        # Performance assertions (generous limits for CI)
        assert write_time < 0.1, f"Cache writes too slow: {write_time}s"
        assert read_time < 0.05, f"Cache reads too slow: {read_time}s"

        # Hit rate should be 100% for this test
        assert cache.hit_rate == 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])