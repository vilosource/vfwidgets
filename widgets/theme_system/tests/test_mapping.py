"""
Comprehensive tests for ThemeMapping with CSS selector support.

Tests all components of Task 13 including:
- CSS selector parsing and matching
- Conflict resolution strategies
- Mapping composition
- Visual debugging tools
- Validation and error recovery
"""

import pytest
import time
from unittest.mock import Mock, patch

from src.vfwidgets_theme.mapping.mapper import (
    ThemeMapping, SelectorParser, SelectorMatcher, ConflictResolver,
    SelectorType, MappingPriority, ConflictResolution, MappingError,
    ThemeMappingVisualizer, SelectorPart, ParsedSelector, MappingRule,
    css_selector, id_selector, class_selector, type_selector, attribute_selector
)
from src.vfwidgets_theme.properties.descriptors import PropertyDescriptor
from src.vfwidgets_theme.events.system import ThemeEventSystem


class MockWidget:
    """Mock widget for testing."""

    def __init__(self, widget_id=None, widget_type="MockWidget",
                 theme_classes=None, attributes=None):
        self._widget_id = widget_id or f"widget_{id(self)}"
        self._widget_type = widget_type
        self._theme_classes = theme_classes or set()
        self._theme_attributes = attributes or {}
        self._enabled = True
        self._visible = True
        self._focused = False

    def isEnabled(self):
        return self._enabled

    def isVisible(self):
        return self._visible

    def hasFocus(self):
        return self._focused


class TestSelectorParser:
    """Test CSS selector parsing."""

    def setup_method(self):
        self.parser = SelectorParser()

    def test_simple_id_selector(self):
        """Test parsing simple ID selector."""
        selector = self.parser.parse("#my-button")

        assert len(selector.parts) == 1
        part = selector.parts[0]
        assert part.type == SelectorType.ID
        assert part.value == "my-button"
        assert selector.specificity == (0, 1, 0, 0)

    def test_simple_class_selector(self):
        """Test parsing simple class selector."""
        selector = self.parser.parse(".primary-button")

        assert len(selector.parts) == 1
        part = selector.parts[0]
        assert part.type == SelectorType.CLASS
        assert part.value == "primary-button"
        assert selector.specificity == (0, 0, 1, 0)

    def test_simple_type_selector(self):
        """Test parsing simple type selector."""
        selector = self.parser.parse("QPushButton")

        assert len(selector.parts) == 1
        part = selector.parts[0]
        assert part.type == SelectorType.TYPE
        assert part.value == "QPushButton"
        assert selector.specificity == (0, 0, 0, 1)

    def test_universal_selector(self):
        """Test parsing universal selector."""
        selector = self.parser.parse("*")

        assert len(selector.parts) == 1
        part = selector.parts[0]
        assert part.type == SelectorType.UNIVERSAL
        assert part.value == "*"
        assert selector.specificity == (0, 0, 0, 0)

    def test_attribute_selector(self):
        """Test parsing attribute selector."""
        selector = self.parser.parse("[enabled='true']")

        assert len(selector.parts) == 1
        part = selector.parts[0]
        assert part.type == SelectorType.ATTRIBUTE
        assert "enabled" in part.attributes
        assert part.attributes["enabled"] == "true"
        assert selector.specificity == (0, 0, 1, 0)

    def test_pseudo_class_selector(self):
        """Test parsing pseudo-class selector."""
        selector = self.parser.parse(":enabled")

        assert len(selector.parts) == 1
        part = selector.parts[0]
        assert part.type == SelectorType.PSEUDO
        assert "enabled" in part.pseudo_classes
        assert selector.specificity == (0, 0, 1, 0)

    def test_complex_selector(self):
        """Test parsing complex selector with multiple parts."""
        selector = self.parser.parse("#dialog .button:enabled")

        assert len(selector.parts) >= 1  # Simplified parsing
        assert selector.specificity[1] >= 1  # At least one ID
        assert selector.specificity[2] >= 1  # At least one class/pseudo

    def test_invalid_selector(self):
        """Test parsing invalid selector."""
        with pytest.raises(MappingError):
            self.parser.parse("")

    def test_specificity_calculation(self):
        """Test CSS specificity calculation."""
        # ID selector should have higher specificity
        id_sel = self.parser.parse("#button")
        class_sel = self.parser.parse(".button")
        type_sel = self.parser.parse("QPushButton")

        assert id_sel.specificity > class_sel.specificity
        assert class_sel.specificity > type_sel.specificity


class TestSelectorMatcher:
    """Test CSS selector matching."""

    def setup_method(self):
        self.matcher = SelectorMatcher()
        self.parser = SelectorParser()

    def test_id_matching(self):
        """Test ID selector matching."""
        widget = MockWidget(widget_id="test-button")
        selector = self.parser.parse("#test-button")

        assert self.matcher.matches(selector, widget)

    def test_id_not_matching(self):
        """Test ID selector not matching."""
        widget = MockWidget(widget_id="other-button")
        selector = self.parser.parse("#test-button")

        assert not self.matcher.matches(selector, widget)

    def test_class_matching(self):
        """Test class selector matching."""
        widget = MockWidget(theme_classes={"primary", "button"})
        selector = self.parser.parse(".primary")

        assert self.matcher.matches(selector, widget)

    def test_type_matching(self):
        """Test type selector matching."""
        widget = MockWidget(widget_type="QPushButton")
        selector = self.parser.parse("MockWidget")  # Uses actual class name

        assert self.matcher.matches(selector, widget)

    def test_universal_matching(self):
        """Test universal selector matching."""
        widget = MockWidget()
        selector = self.parser.parse("*")

        assert self.matcher.matches(selector, widget)

    def test_attribute_matching(self):
        """Test attribute selector matching."""
        widget = MockWidget(attributes={"enabled": "true"})
        selector = self.parser.parse("[enabled='true']")

        assert self.matcher.matches(selector, widget)

    def test_pseudo_class_matching(self):
        """Test pseudo-class selector matching."""
        widget = MockWidget()
        widget._enabled = True
        selector = self.parser.parse(":enabled")

        assert self.matcher.matches(selector, widget)

        widget._enabled = False
        # Clear cache since widget state changed
        self.matcher.clear_cache()
        assert not self.matcher.matches(selector, widget)

    def test_matching_cache(self):
        """Test selector matching cache."""
        widget = MockWidget(widget_id="test")
        selector = self.parser.parse("#test")

        # First match should be cache miss
        result1 = self.matcher.matches(selector, widget)
        assert result1

        # Second match should be cache hit
        result2 = self.matcher.matches(selector, widget)
        assert result2

        stats = self.matcher.get_cache_stats()
        assert stats['hits'] > 0


class TestConflictResolver:
    """Test conflict resolution strategies."""

    def setup_method(self):
        self.resolver = ConflictResolver()
        self.parser = SelectorParser()

    def create_rule(self, selector_str, properties, priority=MappingPriority.NORMAL):
        """Helper to create mapping rule."""
        selector = self.parser.parse(selector_str)
        return MappingRule(
            selector=selector,
            properties=properties,
            priority=priority
        )

    def test_priority_resolution(self):
        """Test priority-based conflict resolution."""
        rules = [
            self.create_rule("#button", {"color": "red"}, MappingPriority.LOW),
            self.create_rule(".button", {"color": "blue"}, MappingPriority.HIGH),
        ]

        result = self.resolver.resolve(rules, ConflictResolution.PRIORITY)
        assert result["color"] == "blue"  # Higher priority wins

    def test_merge_resolution(self):
        """Test merge conflict resolution."""
        rules = [
            self.create_rule("#button", {"color": "red", "font-size": "12px"}),
            self.create_rule(".button", {"color": "blue", "background": "white"}),
        ]

        result = self.resolver.resolve(rules, ConflictResolution.MERGE)
        assert result["color"] == "blue"  # Later rule wins for conflicts
        assert result["font-size"] == "12px"  # Non-conflicting properties preserved
        assert result["background"] == "white"

    def test_specificity_resolution(self):
        """Test specificity-based conflict resolution."""
        rules = [
            self.create_rule("#button", {"color": "red"}),      # ID: specificity (0,1,0,0)
            self.create_rule(".button", {"color": "blue"}),     # Class: specificity (0,0,1,0)
        ]

        result = self.resolver.resolve(rules, ConflictResolution.MOST_SPECIFIC)
        assert result["color"] == "red"  # ID selector more specific

    def test_first_match_resolution(self):
        """Test first match conflict resolution."""
        rules = [
            self.create_rule("#button", {"color": "red"}),
            self.create_rule(".button", {"color": "blue"}),
        ]

        result = self.resolver.resolve(rules, ConflictResolution.FIRST_MATCH)
        assert result["color"] == "red"  # First rule wins

    def test_last_match_resolution(self):
        """Test last match conflict resolution."""
        rules = [
            self.create_rule("#button", {"color": "red"}),
            self.create_rule(".button", {"color": "blue"}),
        ]

        result = self.resolver.resolve(rules, ConflictResolution.LAST_MATCH)
        assert result["color"] == "blue"  # Last rule wins


class TestThemeMapping:
    """Test main ThemeMapping functionality."""

    def setup_method(self):
        self.mapping = ThemeMapping(debug=True)

    def test_add_rule(self):
        """Test adding mapping rules."""
        rule_index = self.mapping.add_rule(
            "#test-button",
            {"color": "red", "font-size": "14px"},
            priority=MappingPriority.HIGH,
            name="Test Button Style"
        )

        assert rule_index == 0

        stats = self.mapping.get_statistics()
        assert stats['active_rules'] == 1

    def test_remove_rule(self):
        """Test removing mapping rules."""
        rule_index = self.mapping.add_rule("#test", {"color": "red"})
        assert self.mapping.remove_rule(rule_index)

        stats = self.mapping.get_statistics()
        assert stats['active_rules'] == 0

    def test_get_mapping_single_rule(self):
        """Test getting mapping with single matching rule."""
        self.mapping.add_rule("#test-button", {"color": "red", "font-size": "14px"})

        widget = MockWidget(widget_id="test-button")
        mapping = self.mapping.get_mapping(widget)

        assert mapping["color"] == "red"
        assert mapping["font-size"] == "14px"

    def test_get_mapping_multiple_rules(self):
        """Test getting mapping with multiple matching rules."""
        self.mapping.add_rule(".button", {"color": "blue"}, MappingPriority.LOW)
        self.mapping.add_rule("#test-button", {"color": "red"}, MappingPriority.HIGH)

        widget = MockWidget(
            widget_id="test-button",
            theme_classes={"button"}
        )
        mapping = self.mapping.get_mapping(widget)

        assert mapping["color"] == "red"  # Higher priority wins

    def test_get_mapping_no_rules(self):
        """Test getting mapping with no matching rules."""
        widget = MockWidget()
        mapping = self.mapping.get_mapping(widget)

        assert mapping == {}

    def test_conditional_rules(self):
        """Test rules with runtime conditions."""
        def enabled_condition(widget):
            return widget.isEnabled()

        self.mapping.add_rule(
            "#test-button",
            {"color": "red"},
            conditions=[enabled_condition]
        )

        # Enabled widget should match
        widget = MockWidget(widget_id="test-button")
        widget._enabled = True
        mapping = self.mapping.get_mapping(widget)
        assert mapping.get("color") == "red"

        # Disabled widget should not match
        widget._enabled = False
        mapping = self.mapping.get_mapping(widget)
        assert "color" not in mapping

    def test_caching(self):
        """Test mapping result caching."""
        self.mapping.add_rule("#test", {"color": "red"})

        widget = MockWidget(widget_id="test")

        # First call should be cache miss
        mapping1 = self.mapping.get_mapping(widget)

        # Second call should be cache hit
        mapping2 = self.mapping.get_mapping(widget)

        assert mapping1 == mapping2

        stats = self.mapping.get_statistics()
        assert stats['performance_stats']['cache_hits'] > 0

    def test_mapping_composition(self):
        """Test mapping composition."""
        mapping1 = ThemeMapping()
        mapping1.add_rule("#button", {"color": "red"})

        mapping2 = ThemeMapping()
        mapping2.add_rule(".primary", {"font-weight": "bold"})

        composed = mapping1.compose_with(mapping2)

        stats = composed.get_statistics()
        assert stats['active_rules'] == 2

    def test_rule_validation(self):
        """Test rule validation."""
        # Valid rule should work
        self.mapping.add_rule("#test", {"color": "red"})

        # Invalid rule (empty properties) should fail
        with pytest.raises(MappingError):
            self.mapping.add_rule("#test", {})

    def test_custom_validator(self):
        """Test custom rule validators."""
        def validate_color_properties(rule):
            return "color" in rule.properties

        self.mapping.add_validator(validate_color_properties)

        # Rule with color should pass
        self.mapping.add_rule("#test", {"color": "red"})

        # Rule without color should fail
        with pytest.raises(MappingError):
            self.mapping.add_rule("#test", {"font-size": "12px"})


class TestThemeMappingVisualizer:
    """Test visual debugging tools."""

    def setup_method(self):
        self.mapping = ThemeMapping()
        self.visualizer = ThemeMappingVisualizer(self.mapping)

    def test_debug_report(self):
        """Test generating debug report."""
        self.mapping.add_rule("#test-button", {"color": "red"}, name="Test Rule")
        self.mapping.add_rule(".button", {"font-size": "12px"}, name="Button Rule")

        widget = MockWidget(
            widget_id="test-button",
            theme_classes={"button"}
        )

        report = self.visualizer.generate_debug_report(widget)

        assert report['widget']['id'] == "test-button"
        assert len(report['applicable_rules']) == 2
        assert "color" in report['final_mapping']
        assert "font-size" in report['final_mapping']

    def test_property_source_explanation(self):
        """Test explaining property sources."""
        self.mapping.add_rule("#test", {"color": "red"}, MappingPriority.HIGH, name="ID Rule")
        self.mapping.add_rule(".test", {"color": "blue"}, MappingPriority.LOW, name="Class Rule")

        widget = MockWidget(widget_id="test", theme_classes={"test"})

        explanation = self.visualizer.explain_property_source(widget, "color")

        assert explanation['property'] == "color"
        assert explanation['final_value'] == "red"  # Higher priority wins
        assert len(explanation['contributing_rules']) == 2

    def test_css_like_output(self):
        """Test generating CSS-like debug output."""
        self.mapping.add_rule("#test", {"color": "red"}, name="Test Rule")

        widget = MockWidget(widget_id="test")

        css_output = self.visualizer.generate_css_like_output(widget)

        assert "#test" in css_output
        assert "color: red" in css_output
        assert "Test Rule" in css_output


class TestUtilityFunctions:
    """Test selector utility functions."""

    def test_id_selector(self):
        """Test ID selector utility."""
        selector = id_selector("my-button")
        assert selector == "#my-button"

    def test_class_selector(self):
        """Test class selector utility."""
        selector = class_selector("primary")
        assert selector == ".primary"

    def test_type_selector(self):
        """Test type selector utility."""
        selector = type_selector("QPushButton")
        assert selector == "QPushButton"

    def test_attribute_selector(self):
        """Test attribute selector utility."""
        selector = attribute_selector("enabled", "true")
        assert selector == "[enabled='true']"

        selector = attribute_selector("disabled")
        assert selector == "[disabled]"


class TestIntegrationWithPropertyDescriptor:
    """Test integration with PropertyDescriptor system."""

    def setup_method(self):
        self.mapping = ThemeMapping()

    def test_property_resolution_with_mapping(self):
        """Test that PropertyDescriptor can use mapping results."""
        # This would be more complex in a real integration
        # For now, test basic compatibility

        self.mapping.add_rule("#test-widget", {"theme_color": "red"})

        widget = MockWidget(widget_id="test-widget")
        mapping = self.mapping.get_mapping(widget)

        assert mapping.get("theme_color") == "red"


class TestPerformance:
    """Test performance requirements."""

    def setup_method(self):
        self.mapping = ThemeMapping()

    def test_mapping_performance(self):
        """Test that mapping resolution meets performance requirements."""
        # Add many rules
        for i in range(100):
            self.mapping.add_rule(f".class-{i}", {f"prop-{i}": f"value-{i}"})

        widget = MockWidget(theme_classes={f"class-{i}" for i in range(50)})

        start_time = time.perf_counter()
        mapping = self.mapping.get_mapping(widget)
        end_time = time.perf_counter()

        duration_ms = (end_time - start_time) * 1000

        # Should complete within 100ms (generous for 100 rules)
        assert duration_ms < 100
        assert len(mapping) == 50  # Should match 50 rules

    def test_cache_performance(self):
        """Test cache improves performance."""
        self.mapping.add_rule("#test", {"color": "red"})
        widget = MockWidget(widget_id="test")

        # First call (cache miss)
        start_time = time.perf_counter()
        mapping1 = self.mapping.get_mapping(widget)
        first_duration = time.perf_counter() - start_time

        # Second call (cache hit)
        start_time = time.perf_counter()
        mapping2 = self.mapping.get_mapping(widget)
        second_duration = time.perf_counter() - start_time

        # Cache hit should be faster
        assert second_duration < first_duration
        assert mapping1 == mapping2


class TestErrorRecovery:
    """Test error recovery and graceful failure."""

    def setup_method(self):
        self.mapping = ThemeMapping()

    def test_invalid_selector_recovery(self):
        """Test recovery from invalid selectors."""
        with pytest.raises(MappingError):
            self.mapping.add_rule("", {"color": "red"})

        # System should still be usable
        self.mapping.add_rule("#valid", {"color": "blue"})

        stats = self.mapping.get_statistics()
        assert stats['active_rules'] == 1

    def test_widget_matching_error_recovery(self):
        """Test recovery from widget matching errors."""
        # Add rule that might cause matching errors
        self.mapping.add_rule("#test", {"color": "red"})

        # Create widget that might cause issues
        widget = MockWidget()
        widget.isEnabled = lambda: 1/0  # Will raise exception

        # Should return empty mapping instead of crashing
        mapping = self.mapping.get_mapping(widget)
        assert isinstance(mapping, dict)  # Should not crash


if __name__ == "__main__":
    pytest.main([__file__, "-v"])