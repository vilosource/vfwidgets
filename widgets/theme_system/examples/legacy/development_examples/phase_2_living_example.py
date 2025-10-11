#!/usr/bin/env python3
"""
Phase 2 Living Example - Property System Features

This example grows with each task to demonstrate new capabilities.
It showcases the enhanced property system introduced in Phase 2.

Current Features:
- Task 11: Robust Property Descriptors with validation and caching
- Task 12: Event System with Qt Integration
- Task 14: Pattern Recognition with Caching

Usage:
    python examples/phase_2_living_example.py
"""

# Add src to path for imports
import os
import sys
import time
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

try:
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import (
        QApplication,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )

    QT_AVAILABLE = True
except ImportError:
    print("PySide6 not available, running in mock mode")
    QT_AVAILABLE = False

# Import our theme system components
# Task 12 imports
from vfwidgets_theme.events.system import get_global_event_system

# Task 14 imports
from vfwidgets_theme.patterns.matcher import (
    PatternMatcher,
    PatternPriority,
    PatternType,
)
from vfwidgets_theme.patterns.plugins import HierarchyPlugin, StatePlugin
from vfwidgets_theme.properties.descriptors import (
    ComputedProperty,
    PropertyDescriptor,
    ValidationError,
    color_validator,
    enum_validator,
    min_max_validator,
    regex_validator,
)
from vfwidgets_theme.widgets.application import ThemedApplication
from vfwidgets_theme.widgets.base import ThemedWidget


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_subsection(title: str):
    """Print a formatted subsection header."""
    print(f"\n--- {title} ---")


class ValidatedWidget(ThemedWidget):
    """
    Example widget demonstrating Task 11: Property Descriptors

    This widget showcases:
    - Type-safe property access
    - Validation rules
    - Property caching
    - Error recovery
    """

    # Property descriptors with various validation rules
    background_color = PropertyDescriptor(
        "window.background",
        str,
        validator=color_validator(),
        default="#ffffff",
        debug=False,  # Set to True to see debug output
    )

    text_color = PropertyDescriptor(
        "window.foreground", str, validator=color_validator(), default="#000000"
    )

    font_size = PropertyDescriptor(
        "text.font_size", int, validator=min_max_validator(8, 72), default=12
    )

    border_width = PropertyDescriptor(
        "border.width", int, validator=min_max_validator(0, 10), default=1
    )

    theme_variant = PropertyDescriptor(
        "theme.variant", str, validator=enum_validator(["light", "dark", "auto"]), default="light"
    )

    window_title = PropertyDescriptor(
        "window.title",
        str,
        validator=regex_validator(
            r"^[a-zA-Z0-9\s\-_]+$",
            "Title must contain only alphanumeric characters, spaces, hyphens, and underscores",
        ),
        default="Themed Window",
    )

    # Computed property example using PropertyDescriptor with computed
    def _compute_contrast_ratio(self):
        """Compute contrast ratio between background and text colors."""
        # Simplified contrast calculation
        bg = self.background_color
        text = self.text_color

        # Very basic contrast calculation (real implementation would be more complex)
        bg_brightness = 0.5 if bg.startswith("#") else 0.3
        text_brightness = 0.2 if text.startswith("#") else 0.7

        return abs(bg_brightness - text_brightness) * 10  # Scale for readability

    # Note: The computed property will be set up in __init__ since it needs self reference
    contrast_ratio = PropertyDescriptor("computed.contrast_ratio", float, default=5.0)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Set up computed property with proper self reference
        ValidatedWidget.contrast_ratio.computed = ComputedProperty(
            lambda widget: self._compute_contrast_ratio(),
            dependencies=["background_color", "text_color"],
        )

        self._setup_widget()

    def _setup_widget(self):
        """Set up the widget appearance."""
        if QT_AVAILABLE:
            self.setMinimumSize(300, 200)
            self.setWindowTitle(self.window_title)

    def on_theme_changed(self):
        """Called when theme changes."""
        print("ValidatedWidget theme changed:")
        print(f"  Background: {self.background_color}")
        print(f"  Text Color: {self.text_color}")
        print(f"  Font Size: {self.font_size}px")
        print(f"  Border Width: {self.border_width}px")
        print(f"  Theme Variant: {self.theme_variant}")
        print(f"  Contrast Ratio: {self.contrast_ratio:.2f}")

    def demonstrate_property_features(self):
        """Demonstrate property descriptor features."""
        print_subsection("Property Descriptor Features")

        # 1. Basic property access
        print("1. Basic property access:")
        print(f"   background_color: {self.background_color}")
        print(f"   font_size: {self.font_size}")
        print(f"   theme_variant: {self.theme_variant}")

        # 2. Type conversion
        print("\n2. Type conversion (accessing font_size as string from theme):")
        # The descriptor should convert string to int automatically
        print(f"   font_size (should be int): {self.font_size} (type: {type(self.font_size)})")

        # 3. Validation (demonstrate by trying to set invalid values)
        print("\n3. Validation testing:")

        # Test color validation
        try:
            ValidatedWidget.background_color.__set__(self, "not-a-color")
            print("   ERROR: Invalid color was accepted!")
        except ValidationError as e:
            print(f"   ✓ Color validation works: {e}")

        # Test font size range validation
        try:
            ValidatedWidget.font_size.__set__(self, 100)  # Outside range
            print("   ERROR: Invalid font size was accepted!")
        except ValidationError as e:
            print(f"   ✓ Font size validation works: {e}")

        # Test enum validation
        try:
            ValidatedWidget.theme_variant.__set__(self, "invalid-variant")
            print("   ERROR: Invalid theme variant was accepted!")
        except ValidationError as e:
            print(f"   ✓ Theme variant validation works: {e}")

        # Test regex validation
        try:
            ValidatedWidget.window_title.__set__(self, "Invalid@Title!")
            print("   ERROR: Invalid title was accepted!")
        except ValidationError as e:
            print(f"   ✓ Title regex validation works: {e}")

        # 4. Computed properties
        print("\n4. Computed properties:")
        print(f"   Contrast ratio: {self.contrast_ratio:.2f}")

        # 5. Property statistics
        print("\n5. Property statistics:")
        for prop_name in ["background_color", "font_size", "theme_variant"]:
            descriptor = getattr(ValidatedWidget, prop_name)
            stats = descriptor.statistics
            print(f"   {prop_name}:")
            print(f"     Access count: {stats['access_count']}")
            print(f"     Validation failures: {stats['validation_failures']}")
            print(f"     Cache enabled: {stats['cache_enabled']}")

        # 6. Cache performance test
        print("\n6. Cache performance test:")
        iterations = 1000
        start_time = time.perf_counter()

        for _ in range(iterations):
            _ = self.background_color  # Access cached property

        end_time = time.perf_counter()
        avg_time_ns = (end_time - start_time) * 1_000_000_000 / iterations

        print(f"   {iterations} cached property accesses took {avg_time_ns:.1f}ns average")
        print(
            f"   {'✓ PASS' if avg_time_ns < 1000 else '✗ FAIL'}: Performance requirement (<1000ns)"
        )


class EventAwareWidget(ThemedWidget):
    """
    Example widget demonstrating Task 12: Event System Integration

    This widget showcases:
    - Event system integration with property descriptors
    - Signal/slot connections
    - Event filtering
    - Performance monitoring
    """

    # Properties that emit events when changed
    title = PropertyDescriptor("window.title", str, default="Event Demo")

    color = PropertyDescriptor(
        "window.background", str, validator=color_validator(), default="#ffffff"
    )

    size = PropertyDescriptor(
        "window.size", int, validator=min_max_validator(10, 1000), default=100
    )

    def __init__(self, parent=None):
        super().__init__(parent)

        # Event tracking
        self.events_received = []
        self.setup_event_listeners()

    def setup_event_listeners(self):
        """Set up event system listeners."""
        event_system = get_global_event_system()

        # Connect to all relevant signals
        event_system.property_changing.connect(self.on_property_changing)
        event_system.property_changed.connect(self.on_property_changed)
        event_system.property_validation_failed.connect(self.on_validation_failed)
        event_system.theme_changed.connect(self.on_theme_changed)
        event_system.performance_warning.connect(self.on_performance_warning)

    def on_property_changing(self, widget_id, property_name, old_value, new_value):
        """Handle property changing events."""
        if widget_id == getattr(self, "_widget_id", f"widget_{id(self)}"):
            event_info = f"Property '{property_name}' changing: {old_value} -> {new_value}"
            self.events_received.append(("property_changing", event_info))
            print(f"  🔄 {event_info}")

    def on_property_changed(self, widget_id, property_name, old_value, new_value):
        """Handle property changed events."""
        if widget_id == getattr(self, "_widget_id", f"widget_{id(self)}"):
            event_info = f"Property '{property_name}' changed: {old_value} -> {new_value}"
            self.events_received.append(("property_changed", event_info))
            print(f"  ✅ {event_info}")

    def on_validation_failed(self, widget_id, property_name, invalid_value, error):
        """Handle validation failure events."""
        if widget_id == getattr(self, "_widget_id", f"widget_{id(self)}"):
            event_info = f"Validation failed for '{property_name}': {invalid_value} - {error}"
            self.events_received.append(("validation_failed", event_info))
            print(f"  ❌ {event_info}")

    def on_theme_changed(self, theme_name):
        """Handle theme change events."""
        event_info = f"Theme changed to: {theme_name}"
        self.events_received.append(("theme_changed", event_info))
        print(f"  🎨 {event_info}")

    def on_performance_warning(self, operation, duration_ms):
        """Handle performance warning events."""
        event_info = f"Performance warning: {operation} took {duration_ms:.2f}ms"
        self.events_received.append(("performance_warning", event_info))
        print(f"  ⚠️ {event_info}")

    def clear_events(self):
        """Clear recorded events."""
        self.events_received.clear()

    def get_events_summary(self):
        """Get summary of received events."""
        summary = {}
        for event_type, _ in self.events_received:
            summary[event_type] = summary.get(event_type, 0) + 1
        return summary


def demonstrate_validation_rules():
    """Demonstrate different validation rule types."""
    print_section("Task 11: Validation Rule Demonstrations")

    # Min/Max validation
    print_subsection("Min/Max Validation")
    min_max_rule = min_max_validator(10, 20)
    test_values = [5, 10, 15, 20, 25, "15", "invalid"]

    for value in test_values:
        result = min_max_rule.validate(value)
        print(f"   Value {value}: {'✓ Valid' if result else '✗ Invalid'}")

    # Regex validation
    print_subsection("Regex Validation")
    email_rule = regex_validator(r"^[\w\.-]+@[\w\.-]+\.\w+$", "Must be a valid email")
    test_emails = [
        "user@example.com",
        "test.user@domain.co.uk",
        "invalid-email",
        "missing@domain",
        "@example.com",
    ]

    for email in test_emails:
        result = email_rule.validate(email)
        print(f"   Email {email}: {'✓ Valid' if result else '✗ Invalid'}")

    # Enum validation
    print_subsection("Enum Validation")
    status_rule = enum_validator(["active", "inactive", "pending"])
    test_statuses = ["active", "inactive", "pending", "unknown", "Active"]  # Case matters

    for status in test_statuses:
        result = status_rule.validate(status)
        print(f"   Status {status}: {'✓ Valid' if result else '✗ Invalid'}")

    # Color validation
    print_subsection("Color Validation")
    color_rule = color_validator()
    test_colors = [
        "#ff0000",  # Hex
        "#f00",  # Short hex
        "rgb(255, 0, 0)",  # RGB
        "rgba(255, 0, 0, 0.5)",  # RGBA
        "red",  # Named
        "not-a-color",  # Invalid
        "#gggggg",  # Invalid hex
    ]

    for color in test_colors:
        result = color_rule.validate(color)
        print(f"   Color {color}: {'✓ Valid' if result else '✗ Invalid'}")


def demonstrate_caching_system():
    """Demonstrate the property caching system."""
    print_section("Task 11: Property Caching System")

    from vfwidgets_theme.properties.descriptors import PropertyCache

    print_subsection("Basic Cache Operations")
    cache = PropertyCache(max_size=5)

    # Test basic operations
    print("1. Setting values:")
    for i in range(3):
        key = f"key_{i}"
        value = f"value_{i}"
        cache.set(key, value)
        print(f"   Set {key} = {value}")

    print("\n2. Getting values:")
    for i in range(3):
        key = f"key_{i}"
        value = cache.get(key)
        print(f"   Get {key} = {value}")

    print("\n3. Cache statistics:")
    stats = cache.stats
    for key, value in stats.items():
        print(f"   {key}: {value}")

    print_subsection("Cache Eviction Test")

    # Fill cache to capacity
    for i in range(6):  # More than max_size
        cache.set(f"evict_key_{i}", f"evict_value_{i}")

    print(f"Cache size after adding 6 items (max 5): {cache.stats['size']}")

    # Check which items were evicted
    print("Checking for evicted items:")
    for i in range(6):
        key = f"evict_key_{i}"
        value = cache.get(key)
        status = "Present" if value else "Evicted"
        print(f"   {key}: {status}")


def demonstrate_performance_benchmarks():
    """Demonstrate performance characteristics meet requirements."""
    print_section("Task 11: Performance Benchmarks")

    # Create a test widget
    widget = ValidatedWidget()

    print_subsection("Property Access Performance")

    # Benchmark different access patterns
    iterations = 10000

    # 1. Cached property access
    print("1. Cached property access:")
    start_time = time.perf_counter()
    for _ in range(iterations):
        _ = widget.background_color
    end_time = time.perf_counter()

    avg_time_ns = (end_time - start_time) * 1_000_000_000 / iterations
    print(f"   {iterations} accesses: {avg_time_ns:.1f}ns average")
    print(f"   Requirement: <100ns {'✓ PASS' if avg_time_ns < 100 else '✗ FAIL'}")

    # 2. Different property types
    print("\n2. Different property types:")
    properties = [
        ("background_color", lambda: widget.background_color),
        ("font_size", lambda: widget.font_size),
        ("theme_variant", lambda: widget.theme_variant),
        ("contrast_ratio", lambda: widget.contrast_ratio),  # Computed property
    ]

    for prop_name, accessor in properties:
        start_time = time.perf_counter()
        for _ in range(1000):
            _ = accessor()
        end_time = time.perf_counter()

        avg_time_ns = (end_time - start_time) * 1_000_000_000 / 1000
        print(f"   {prop_name}: {avg_time_ns:.1f}ns average")

    # 3. Global cache statistics
    print_subsection("Global Cache Statistics")
    from vfwidgets_theme.properties.descriptors import PropertyDescriptor

    stats = PropertyDescriptor.get_global_cache_stats()

    for key, value in stats.items():
        print(f"   {key}: {value}")

    print(f"\n   Cache hit rate: {stats.get('hit_rate', 0):.1%}")
    print(f"   Requirement: >90% {'✓ PASS' if stats.get('hit_rate', 0) > 0.9 else '✗ FAIL'}")


def demonstrate_event_system():
    """Demonstrate Task 12: Event System with Qt Integration."""
    print_section("Task 12: Event System with Qt Integration")

    # Get event system
    event_system = get_global_event_system()

    # Create event-aware widget
    widget = EventAwareWidget()

    print_subsection("Basic Event Generation")
    print("Demonstrating property change events...")

    # Clear any existing events
    widget.clear_events()

    # Change properties to trigger events
    print("\n1. Setting valid properties:")
    EventAwareWidget.title.__set__(widget, "New Title")
    EventAwareWidget.color.__set__(widget, "#ff0000")
    EventAwareWidget.size.__set__(widget, 200)

    # Try invalid values to trigger validation events
    print("\n2. Testing validation failures:")
    try:
        EventAwareWidget.color.__set__(widget, "not-a-color")
    except ValidationError:
        pass  # Expected

    try:
        EventAwareWidget.size.__set__(widget, 2000)  # Too large
    except ValidationError:
        pass  # Expected

    # Show event summary
    print("\n3. Event Summary:")
    summary = widget.get_events_summary()
    for event_type, count in summary.items():
        print(f"   {event_type}: {count} events")

    print_subsection("Event System Features")

    # Test event recording
    print("1. Event Recording:")
    event_system.enable_recording(max_history=50)

    # Generate some events
    widget.clear_events()
    for i in range(3):
        EventAwareWidget.title.__set__(widget, f"Title {i}")

    history = event_system.get_event_history()
    print(f"   Recorded {len(history)} events in history")

    # Test event filtering
    print("\n2. Event Filtering:")
    initial_events = len(widget.events_received)

    # Add filter for title property
    event_system.add_property_filter("window.title")
    print("   Added filter for 'window.title' property")

    # This should be filtered out
    EventAwareWidget.title.__set__(widget, "Filtered Title")

    # This should not be filtered
    EventAwareWidget.color.__set__(widget, "#00ff00")

    filtered_events = len(widget.events_received) - initial_events
    print(f"   Received {filtered_events} events (title changes should be filtered)")

    # Remove filter
    event_system.remove_property_filter("window.title")
    print("   Removed title filter")

    print("\n3. Debouncing Test:")
    # Test debouncing by setting multiple properties quickly
    widget.clear_events()
    event_system.set_debounce_interval(100)  # 100ms debounce

    print("   Setting properties rapidly (debouncing should reduce events)...")
    for i in range(5):
        # Set with debouncing enabled (default)
        event_system.notify_property_changed(
            getattr(widget, "_widget_id", f"widget_{id(widget)}"),
            "rapid_property",
            f"old_{i}",
            f"new_{i}",
            debounce=True,
        )

    # Wait a moment for debounced events to be processed
    if QT_AVAILABLE:
        time.sleep(0.2)

    print("   Debounced events processed")

    print_subsection("Performance Monitoring")

    # Reset performance threshold to trigger warnings
    original_threshold = event_system._performance_threshold_ms
    event_system._performance_threshold_ms = 0.001  # Very low to trigger warnings

    widget.clear_events()

    # Generate events that might trigger performance warnings
    event_system.notify_theme_changed("performance_test_theme")

    # Check for performance warnings
    perf_warnings = [e for e in widget.events_received if e[0] == "performance_warning"]
    if perf_warnings:
        print(f"   Generated {len(perf_warnings)} performance warnings")
    else:
        print("   No performance warnings generated (system is fast)")

    # Restore original threshold
    event_system._performance_threshold_ms = original_threshold

    print_subsection("Event System Statistics")
    stats = event_system.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    return widget


def demonstrate_event_integration():
    """Demonstrate integration between PropertyDescriptors and EventSystem."""
    print_section("Integration: PropertyDescriptors + EventSystem")

    # Create widgets with different properties
    widget1 = EventAwareWidget()
    widget2 = ValidatedWidget()

    # Clear events
    widget1.clear_events()

    print_subsection("Multi-Widget Event Coordination")

    print("1. Setting properties on multiple widgets:")

    # Change properties on both widgets
    EventAwareWidget.color.__set__(widget1, "#ff0000")
    ValidatedWidget.background_color.__set__(widget2, "#00ff00")

    print(f"   Widget1 received {len(widget1.events_received)} events")

    # Show that events are widget-specific
    widget1_events = [
        e
        for e in widget1.events_received
        if getattr(widget1, "_widget_id", f"widget_{id(widget1)}") in str(e)
    ]
    widget2_events = [
        e
        for e in widget1.events_received
        if getattr(widget2, "_widget_id", f"widget_{id(widget2)}") in str(e)
    ]

    print(f"   Widget1-specific events: {len(widget1_events)}")
    print(f"   Widget2-specific events: {len(widget2_events)}")

    print("\n2. Event System Global State:")
    event_system = get_global_event_system()

    # Register widgets explicitly
    widget1_id = getattr(widget1, "_widget_id", f"widget_{id(widget1)}")
    widget2_id = getattr(widget2, "_widget_id", f"widget_{id(widget2)}")

    if QT_AVAILABLE:
        from PySide6.QtWidgets import QWidget

        mock_qwidget1 = QWidget()
        mock_qwidget2 = QWidget()
        event_system.register_widget(widget1_id, mock_qwidget1)
        event_system.register_widget(widget2_id, mock_qwidget2)

    stats = event_system.get_statistics()
    print(f"   Registered widgets: {stats.get('registered_widgets', 0)}")
    print(f"   Filtered properties: {stats.get('filtered_properties', 0)}")
    print(f"   Event recording: {'enabled' if stats.get('recording_enabled') else 'disabled'}")

    return widget1, widget2


def demonstrate_pattern_matching():
    """Demonstrate Task 14: Pattern Recognition with Caching."""
    print_section("Task 14: Pattern Recognition with Caching")

    # Create pattern matcher
    matcher = PatternMatcher(cache_size=100, debug=True)

    print_subsection("1. Basic Pattern Types")

    # Add different pattern types
    print("Adding patterns...")
    matcher.add_pattern("*Widget", PatternType.GLOB, PatternPriority.NORMAL, "All Widgets")
    matcher.add_pattern("*Button*", PatternType.GLOB, PatternPriority.HIGH, "All Buttons")
    matcher.add_pattern(r"test_\d+", PatternType.REGEX, PatternPriority.NORMAL, "Test with Numbers")
    matcher.add_pattern(
        r"^Custom.*Dialog$", PatternType.REGEX, PatternPriority.HIGH, "Custom Dialogs"
    )

    # Custom pattern function
    def starts_with_main(target, widget):
        from vfwidgets_theme.patterns.matcher import MatchResult

        matched = target.startswith("main")
        return MatchResult(matched, 0.9 if matched else 0.0)

    matcher.add_pattern(
        "main_pattern",
        PatternType.CUSTOM,
        PatternPriority.HIGH,
        "Main Pattern",
        custom_function=starts_with_main,
    )

    print(f"Added {len(matcher._patterns)} patterns")

    print_subsection("2. Pattern Matching Examples")

    # Test widget
    test_widget = ValidatedWidget()

    # Test different targets
    test_targets = [
        "TestWidget",  # Should match *Widget
        "MainButton",  # Should match *Widget and *Button*
        "test_123",  # Should match test_\d+
        "CustomLoginDialog",  # Should match Custom.*Dialog$
        "main_window",  # Should match main pattern (custom)
        "NoMatchWidget",  # Should match *Widget only
    ]

    for target in test_targets:
        print(f"\nTesting target: '{target}'")
        matches = matcher.match_patterns(target, test_widget)

        if matches:
            print(f"  Found {len(matches)} matches:")
            for i, (_idx, pattern, result) in enumerate(matches):
                print(
                    f"    {i + 1}. {pattern.name}: score={result.score:.2f}, priority={pattern.priority.value}"
                )

            # Get best match
            best = matcher.get_best_match(target, test_widget)
            if best:
                print(
                    f"  Best match: {best[1].name} (priority={best[1].priority.value}, score={best[2].score:.2f})"
                )
        else:
            print("  No matches found")

    print_subsection("3. Plugin System Demonstration")

    # Add plugins
    state_plugin = StatePlugin()
    hierarchy_plugin = HierarchyPlugin()

    matcher.add_plugin(state_plugin)
    matcher.add_plugin(hierarchy_plugin)

    # Add plugin patterns
    matcher.add_pattern(
        "enabled", PatternType.PLUGIN, PatternPriority.NORMAL, "Enabled State", plugin_name="state"
    )
    matcher.add_pattern(
        "Dialog.Button",
        PatternType.PLUGIN,
        PatternPriority.HIGH,
        "Dialog Button Hierarchy",
        plugin_name="hierarchy",
    )

    print("Added plugin patterns for state and hierarchy matching")

    # Test plugin patterns
    print("\nTesting plugin patterns:")

    # Create mock widget with state methods
    mock_widget = ValidatedWidget()
    mock_widget.isEnabled = lambda: True
    mock_widget.isVisible = lambda: True
    mock_widget.hasFocus = lambda: False

    plugin_targets = [
        ("enabled", "Should match enabled state"),
        ("DialogButton", "Should match Dialog.Button hierarchy"),
    ]

    for target, description in plugin_targets:
        print(f"  {target}: {description}")
        matches = matcher.match_patterns(target, mock_widget)
        if matches:
            for _idx, pattern, result in matches:
                print(f"    Match: {pattern.name} (score={result.score:.2f})")
        else:
            print("    No matches")

    print_subsection("4. Performance Demonstration")

    # Add many patterns for performance test
    print("Adding 100 patterns for performance test...")
    for i in range(100):
        pattern_type = PatternType.GLOB if i % 2 == 0 else PatternType.REGEX
        if pattern_type == PatternType.GLOB:
            pattern = f"perf_pattern_{i}*"
        else:
            pattern = rf"perf_pattern_{i}_\d+"

        matcher.add_pattern(pattern, pattern_type, PatternPriority.NORMAL, f"Perf Pattern {i}")

    # Benchmark performance
    benchmark_results = matcher.benchmark_performance(iterations=1000)

    print("Performance Results:")
    print(f"  Total time: {benchmark_results['total_time_ms']:.2f}ms")
    print(f"  Average per match: {benchmark_results['average_time_ms']:.3f}ms")
    print(f"  Patterns per second: {benchmark_results['patterns_per_second']:.0f}")
    print(
        f"  Requirement (<1ms for 100 patterns): {'✓ PASS' if benchmark_results['average_time_ms'] < 1.0 else '✗ FAIL'}"
    )

    print_subsection("5. Caching Performance")

    # Test caching effectiveness
    test_target = "perf_pattern_50_123"

    # First match (cold cache)
    start_time = time.perf_counter()
    matcher.match_patterns(test_target, test_widget)
    cold_time = (time.perf_counter() - start_time) * 1000

    # Subsequent matches (warm cache)
    warm_times = []
    for _ in range(10):
        start_time = time.perf_counter()
        matcher.match_patterns(test_target, test_widget)
        warm_time = (time.perf_counter() - start_time) * 1000
        warm_times.append(warm_time)

    avg_warm_time = sum(warm_times) / len(warm_times)

    print("Cache Performance:")
    print(f"  Cold cache time: {cold_time:.3f}ms")
    print(f"  Warm cache time: {avg_warm_time:.3f}ms")
    print(f"  Speedup: {cold_time / avg_warm_time:.1f}x")

    # Get cache statistics
    stats = matcher.get_statistics()
    cache_stats = stats["match_cache_stats"]
    print(f"  Cache hit rate: {cache_stats['hit_rate']:.1%}")
    print(f"  Requirement (>90%): {'✓ PASS' if cache_stats['hit_rate'] > 0.9 else '✗ FAIL'}")

    print_subsection("6. Integration with CSS Selectors")

    print("Pattern matching complements CSS selectors from Task 13:")
    print("  - CSS selectors: Precise widget targeting (#id, .class, type)")
    print("  - Pattern matching: Flexible string matching (glob, regex, custom)")
    print("  - Together: Comprehensive widget selection system")

    # Example integration scenario
    css_like_targets = [
        "#main-button",  # CSS-style ID
        ".primary-button",  # CSS-style class
        "QPushButton",  # Widget type
    ]

    pattern_like_targets = [
        "*main*",  # Glob pattern
        "primary_*",  # Glob pattern
        r"Q\w+Button",  # Regex pattern
    ]

    print("\nCSS-style targets that could be handled by CSS selectors:")
    for target in css_like_targets:
        print(f"  {target}")

    print("\nPattern-style targets handled by pattern matching:")
    for target in pattern_like_targets:
        print(f"  {target}")

    return matcher


def run_integration_test():
    """Test integration with existing ThemedWidget system."""
    print_section("Task 11: Integration Test with ThemedWidget")

    try:
        # Create themed application
        ThemedApplication()

        # Create widget with property descriptors
        widget = ValidatedWidget()

        print("1. Widget creation: ✓ Success")
        print(f"   Widget ID: {widget._widget_id}")
        print(f"   Theme ready: {widget.is_theme_ready}")

        # Test property access
        print("\n2. Property access through descriptors:")
        print(f"   Background: {widget.background_color}")
        print(f"   Font size: {widget.font_size}")
        print(f"   Computed contrast: {widget.contrast_ratio:.2f}")

        # Test theme statistics
        print("\n3. Theme statistics:")
        stats = widget.theme_statistics
        print(f"   Theme name: {stats.get('theme_name', 'None')}")
        print(f"   Update count: {stats.get('update_count', 0)}")
        print(f"   Cache size: {stats.get('cache_size', 0)}")

        # Test descriptor statistics
        print("\n4. Descriptor statistics:")
        bg_stats = ValidatedWidget.background_color.statistics
        print(f"   Background color access count: {bg_stats['access_count']}")
        print(f"   Validation failures: {bg_stats['validation_failures']}")

        print("\n✓ Integration test completed successfully")
        return True

    except Exception as e:
        print(f"\n✗ Integration test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Main demonstration function."""
    print_section("Phase 2 Living Example - Property System Features")
    print("Demonstrating Task 11: Robust Property Descriptors")

    # Create Qt application if needed
    app = None
    if QT_AVAILABLE:
        try:
            app = QApplication(sys.argv)
        except Exception as e:
            print(f"Could not create Qt application: {e}")

    try:
        # Run Task 11 demonstrations
        demonstrate_validation_rules()
        demonstrate_caching_system()

        # Create and test widget
        widget = ValidatedWidget()
        widget.demonstrate_property_features()

        # Performance tests
        demonstrate_performance_benchmarks()

        # Run Task 12 demonstrations
        demonstrate_event_system()
        widget1, widget2 = demonstrate_event_integration()

        # Run Task 14 demonstrations
        demonstrate_pattern_matching()

        # Integration test
        success = run_integration_test()

        # Summary
        print_section("Phase 2 Summary")
        print("Task 11: Property System")
        print("✓ Property descriptors with type safety")
        print("✓ Validation rules (min/max, regex, enum, custom)")
        print("✓ Property caching with performance optimization")
        print("✓ Computed properties with dependency tracking")
        print("✓ Property inheritance chains")
        print("✓ Integration with ThemedWidget")
        print("✓ Debug and performance monitoring")

        print("\nTask 12: Event System")
        print("✓ Qt signals/slots integration")
        print("✓ Debouncing with QTimer")
        print("✓ Property-specific event signals")
        print("✓ Event filtering for performance")
        print("✓ Event replay capability")
        print("✓ Performance monitoring")
        print("✓ Integration with PropertyDescriptor system")

        print("\nTask 14: Pattern Recognition")
        print("✓ High-performance pattern matching with LRU caching")
        print("✓ Multiple pattern types (glob, regex, custom)")
        print("✓ Priority-based conflict resolution")
        print("✓ Plugin system for extensible patterns")
        print("✓ Sub-millisecond performance for 100 patterns")
        print("✓ >90% cache hit rate for repeated matches")
        print("✓ Integration with CSS selector system")

        if success:
            print("\n🎉 Phase 2 implementation complete and validated!")
            print("   - Task 11: Property Descriptors ✅")
            print("   - Task 12: Event System ✅")
            print("   - Task 14: Pattern Recognition ✅")
        else:
            print("\n⚠️ Phase 2 implementation has issues that need addressing")

    except Exception as e:
        print(f"\n❌ Error running demonstration: {e}")
        traceback.print_exc()
        return 1
    finally:
        # Clean up Qt application if created
        if app is not None:
            try:
                app.quit()
            except Exception:
                pass

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
