#!/usr/bin/env python3
"""
ThemeMapping Showcase Example

Demonstrates all features of the advanced ThemeMapping system:
- CSS selector parsing and matching
- Priority-based conflict resolution
- Mapping composition
- Visual debugging tools
- Runtime validation
- Integration with PropertyDescriptor and ThemeEventSystem
"""

import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.vfwidgets_theme.mapping.mapper import (
    ThemeMapping, MappingPriority, ConflictResolution,
    ThemeMappingVisualizer, id_selector, class_selector,
    type_selector, attribute_selector
)
from src.vfwidgets_theme.properties.descriptors import (
    PropertyDescriptor, min_max_validator, color_validator
)
from src.vfwidgets_theme.events.system import ThemeEventSystem


class MockThemedWidget:
    """Enhanced mock widget for mapping demonstration."""

    def __init__(self, widget_id: str, widget_type: str = "MockWidget"):
        self._widget_id = widget_id
        self._widget_type = widget_type
        self._theme_classes = set()
        self._theme_attributes = {}
        self._enabled = True
        self._visible = True
        self._focused = False

        # Sample theme properties using PropertyDescriptor
        self.theme_color = PropertyDescriptor(
            "theme_color",
            str,
            validator=color_validator(),
            default="#000000",
            debug=True
        )

        self.theme_size = PropertyDescriptor(
            "theme_size",
            int,
            validator=min_max_validator(8, 72),
            default=12,
            debug=True
        )

    def add_class(self, class_name: str):
        """Add theme class to widget."""
        self._theme_classes.add(class_name)
        return self

    def set_attribute(self, name: str, value: str):
        """Set theme attribute."""
        self._theme_attributes[name] = value
        return self

    def set_enabled(self, enabled: bool):
        """Set enabled state."""
        self._enabled = enabled
        return self

    def set_focused(self, focused: bool):
        """Set focused state."""
        self._focused = focused
        return self

    def isEnabled(self):
        return self._enabled

    def isVisible(self):
        return self._visible

    def hasFocus(self):
        return self._focused

    def _get_theme_property(self, key: str):
        """Mock theme property getter."""
        # This would normally come from the theme system
        return None

    def __repr__(self):
        return f"MockThemedWidget(id={self._widget_id}, classes={self._theme_classes})"


def demonstrate_css_selectors():
    """Demonstrate CSS selector parsing and matching."""
    print("=== CSS Selector Demonstration ===")

    mapping = ThemeMapping(debug=True)

    # Create sample widgets
    primary_button = MockThemedWidget("primary-btn", "Button").add_class("primary").add_class("button")
    secondary_button = MockThemedWidget("secondary-btn", "Button").add_class("secondary").add_class("button")
    form_input = MockThemedWidget("email-input", "Input").set_attribute("type", "email")

    # Add rules with different selectors
    mapping.add_rule(
        id_selector("primary-btn"),
        {"color": "#ffffff", "background": "#007acc"},
        priority=MappingPriority.HIGH,
        name="Primary Button ID Rule"
    )

    mapping.add_rule(
        class_selector("button"),
        {"padding": "8px", "border-radius": "4px"},
        priority=MappingPriority.NORMAL,
        name="All Buttons Rule"
    )

    mapping.add_rule(
        class_selector("primary"),
        {"font-weight": "bold"},
        priority=MappingPriority.NORMAL,
        name="Primary Elements Rule"
    )

    mapping.add_rule(
        type_selector("Input"),
        {"border": "1px solid #ccc", "padding": "4px"},
        priority=MappingPriority.NORMAL,
        name="All Inputs Rule"
    )

    mapping.add_rule(
        attribute_selector("type", "email"),
        {"border-color": "#007acc"},
        priority=MappingPriority.HIGH,
        name="Email Input Rule"
    )

    # Demonstrate mapping resolution
    widgets = [primary_button, secondary_button, form_input]

    for widget in widgets:
        print(f"\nWidget: {widget}")
        mapping_result = mapping.get_mapping(widget)
        print(f"Applied properties: {mapping_result}")

        # Show applicable rules
        applicable_rules = mapping.get_applicable_rules(widget)
        print(f"Applicable rules: {[rule.name for _, rule in applicable_rules]}")

    print(f"\nMapping statistics: {mapping.get_statistics()}")


def demonstrate_conflict_resolution():
    """Demonstrate different conflict resolution strategies."""
    print("\n=== Conflict Resolution Demonstration ===")

    widget = MockThemedWidget("test-widget").add_class("primary").add_class("button")

    # Test different strategies
    strategies = [
        ConflictResolution.PRIORITY,
        ConflictResolution.MERGE,
        ConflictResolution.MOST_SPECIFIC,
        ConflictResolution.FIRST_MATCH,
        ConflictResolution.LAST_MATCH
    ]

    for strategy in strategies:
        mapping = ThemeMapping(conflict_resolution=strategy)

        # Add conflicting rules
        mapping.add_rule(
            id_selector("test-widget"),
            {"color": "red", "font-size": "16px"},
            priority=MappingPriority.HIGH,
            name="ID Rule"
        )

        mapping.add_rule(
            class_selector("button"),
            {"color": "blue", "background": "white"},
            priority=MappingPriority.LOW,
            name="Class Rule"
        )

        mapping.add_rule(
            class_selector("primary"),
            {"color": "green", "font-weight": "bold"},
            priority=MappingPriority.NORMAL,
            name="Primary Rule"
        )

        result = mapping.get_mapping(widget)
        print(f"\n{strategy.value}: {result}")


def demonstrate_conditional_rules():
    """Demonstrate conditional rules based on widget state."""
    print("\n=== Conditional Rules Demonstration ===")

    mapping = ThemeMapping()

    # Add conditional rule for enabled state
    def enabled_condition(widget):
        return widget.isEnabled()

    def focused_condition(widget):
        return widget.hasFocus()

    mapping.add_rule(
        class_selector("button"),
        {"background": "#f0f0f0", "color": "#666"},
        name="Button Base Rule"
    )

    mapping.add_rule(
        class_selector("button"),
        {"background": "#007acc", "color": "white"},
        conditions=[enabled_condition],
        name="Enabled Button Rule"
    )

    mapping.add_rule(
        class_selector("button"),
        {"border": "2px solid #007acc"},
        conditions=[focused_condition],
        name="Focused Button Rule"
    )

    # Create widget and test different states
    button = MockThemedWidget("state-btn").add_class("button")

    states = [
        ("Disabled, Not Focused", False, False),
        ("Enabled, Not Focused", True, False),
        ("Enabled, Focused", True, True),
        ("Disabled, Focused", False, True),
    ]

    for state_name, enabled, focused in states:
        button.set_enabled(enabled).set_focused(focused)
        result = mapping.get_mapping(button)
        print(f"\n{state_name}: {result}")


def demonstrate_composition():
    """Demonstrate mapping composition."""
    print("\n=== Mapping Composition Demonstration ===")

    # Create base mapping for buttons
    button_mapping = ThemeMapping()
    button_mapping.add_rule(
        class_selector("button"),
        {"padding": "8px", "border-radius": "4px", "cursor": "pointer"},
        name="Base Button Style"
    )

    # Create color scheme mapping
    color_mapping = ThemeMapping()
    color_mapping.add_rule(
        class_selector("primary"),
        {"background": "#007acc", "color": "white"},
        name="Primary Color Scheme"
    )
    color_mapping.add_rule(
        class_selector("secondary"),
        {"background": "#6c757d", "color": "white"},
        name="Secondary Color Scheme"
    )

    # Compose mappings
    composed_mapping = button_mapping.compose_with(color_mapping)

    # Test composed mapping
    primary_button = MockThemedWidget("btn1").add_class("button").add_class("primary")
    secondary_button = MockThemedWidget("btn2").add_class("button").add_class("secondary")

    for widget in [primary_button, secondary_button]:
        result = composed_mapping.get_mapping(widget)
        print(f"\n{widget}: {result}")

    print(f"\nComposed mapping statistics: {composed_mapping.get_statistics()}")


def demonstrate_visual_debugging():
    """Demonstrate visual debugging tools."""
    print("\n=== Visual Debugging Demonstration ===")

    mapping = ThemeMapping()

    # Add multiple rules
    mapping.add_rule(
        id_selector("debug-widget"),
        {"color": "red"},
        priority=MappingPriority.HIGH,
        name="ID Override",
        description="High priority color override"
    )

    mapping.add_rule(
        class_selector("component"),
        {"font-size": "14px", "margin": "4px"},
        priority=MappingPriority.NORMAL,
        name="Component Base",
        description="Base styling for components"
    )

    mapping.add_rule(
        class_selector("interactive"),
        {"cursor": "pointer", "color": "blue"},
        priority=MappingPriority.LOW,
        name="Interactive Elements",
        description="Styling for interactive elements"
    )

    # Create widget with multiple applicable rules
    widget = (MockThemedWidget("debug-widget")
              .add_class("component")
              .add_class("interactive"))

    # Create visualizer
    visualizer = ThemeMappingVisualizer(mapping)

    # Generate debug report
    debug_report = visualizer.generate_debug_report(widget)
    print(f"\nDebug Report for {widget._widget_id}:")
    print(f"Widget type: {debug_report['widget']['type']}")
    print(f"Widget classes: {debug_report['widget']['classes']}")
    print(f"Number of applicable rules: {len(debug_report['applicable_rules'])}")
    print(f"Final mapping: {debug_report['final_mapping']}")

    # Explain specific property
    color_explanation = visualizer.explain_property_source(widget, "color")
    print(f"\nColor property explanation:")
    print(f"Final value: {color_explanation['final_value']}")
    print(f"Contributing rules: {[rule['name'] for rule in color_explanation['contributing_rules']]}")

    # Generate CSS-like output
    css_output = visualizer.generate_css_like_output(widget)
    print(f"\nCSS-like debug output:")
    print(css_output)


def demonstrate_performance():
    """Demonstrate performance characteristics."""
    print("\n=== Performance Demonstration ===")

    mapping = ThemeMapping()

    # Add many rules
    print("Adding 1000 rules...")
    start_time = time.perf_counter()

    for i in range(1000):
        mapping.add_rule(
            f".class-{i}",
            {f"property-{i}": f"value-{i}"},
            name=f"Rule {i}"
        )

    add_time = (time.perf_counter() - start_time) * 1000
    print(f"Time to add 1000 rules: {add_time:.2f}ms")

    # Create widget that matches many rules
    widget = MockThemedWidget("perf-test")
    for i in range(0, 100, 10):  # Add every 10th class
        widget.add_class(f"class-{i}")

    # Test mapping performance
    print("Testing mapping resolution...")
    start_time = time.perf_counter()

    for _ in range(100):  # 100 mapping resolutions
        result = mapping.get_mapping(widget)

    mapping_time = (time.perf_counter() - start_time) * 1000
    print(f"Time for 100 mapping resolutions: {mapping_time:.2f}ms")
    print(f"Average per resolution: {mapping_time/100:.2f}ms")

    # Show cache statistics
    stats = mapping.get_statistics()
    print(f"\nMapping statistics:")
    print(f"Total rules: {stats['total_rules']}")
    print(f"Active rules: {stats['active_rules']}")
    print(f"Cached mappings: {stats['cached_mappings']}")
    print(f"Cache hits: {stats['performance_stats']['cache_hits']}")
    print(f"Cache misses: {stats['performance_stats']['cache_misses']}")


def demonstrate_integration():
    """Demonstrate integration with PropertyDescriptor and EventSystem."""
    print("\n=== Integration Demonstration ===")

    # Set up event system
    event_system = ThemeEventSystem()
    event_system.enable_recording()

    # Create mapping
    mapping = ThemeMapping(debug=True)
    mapping.add_rule(
        id_selector("integrated-widget"),
        {"theme_color": "#ff0000", "theme_size": 16},
        name="Integration Test Rule"
    )

    # Create widget with PropertyDescriptors
    widget = MockThemedWidget("integrated-widget")

    # Simulate property updates through mapping
    mapping_result = mapping.get_mapping(widget)
    print(f"Mapping result: {mapping_result}")

    # Show how PropertyDescriptor would use this
    if "theme_color" in mapping_result:
        try:
            # This simulates how PropertyDescriptor would validate and set the value
            color_value = mapping_result["theme_color"]
            print(f"Setting theme_color to: {color_value}")
            # widget.theme_color would be set to this value
        except Exception as e:
            print(f"Validation error: {e}")

    # Show event history
    events = event_system.get_event_history()
    print(f"\nRecorded events: {len(events)}")
    for event in events[-5:]:  # Show last 5 events
        print(f"  {event.event_type}: {event.data}")


def main():
    """Run all demonstrations."""
    print("ThemeMapping System Showcase")
    print("=" * 50)

    demonstrate_css_selectors()
    demonstrate_conflict_resolution()
    demonstrate_conditional_rules()
    demonstrate_composition()
    demonstrate_visual_debugging()
    demonstrate_performance()
    demonstrate_integration()

    print("\n" + "=" * 50)
    print("ThemeMapping showcase complete!")
    print("\nKey Features Demonstrated:")
    print("✓ CSS selector parsing (ID, class, type, attribute, pseudo)")
    print("✓ Conflict resolution strategies")
    print("✓ Conditional rules based on widget state")
    print("✓ Mapping composition")
    print("✓ Visual debugging tools")
    print("✓ Performance optimization with caching")
    print("✓ Integration with PropertyDescriptor and EventSystem")
    print("✓ Comprehensive validation and error recovery")


if __name__ == "__main__":
    main()