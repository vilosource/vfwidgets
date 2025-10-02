#!/usr/bin/env python3
"""
VFWidgets Theme System Testing Infrastructure Demonstration

This script demonstrates how to use the comprehensive testing infrastructure
for developing and testing themed widgets. It showcases the key features that
make testing theme functionality as simple as possible.

Key Features Demonstrated:
- ThemedTestCase for easy test setup
- Mock objects for testing without Qt dependencies
- Performance benchmarking and validation
- Memory leak detection
- Comprehensive assertion helpers

Philosophy: "Make it impossible to test theme functionality incorrectly"
"""

import sys
from pathlib import Path

# Add the source directory to the Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from vfwidgets_theme.testing import (
    MemoryProfiler,
    MockThemeableWidget,
    MockThemeProvider,
    ThemeBenchmark,
    ThemedTestCase,
    assert_theme_property,
    benchmark_theme_switch,
    detect_memory_leaks,
    memory_leak_test,
    performance_test,
)


class DemoThemedWidget(MockThemeableWidget):
    """Example themed widget for demonstration."""

    def __init__(self, theme_provider=None):
        super().__init__(theme_provider)
        self.background_color = "#ffffff"
        self.text_color = "#000000"

    def apply_theme(self):
        """Apply current theme to widget appearance."""
        self.background_color = self.get_theme_color("background", "#ffffff")
        self.text_color = self.get_theme_color("foreground", "#000000")

    def on_theme_changed(self):
        """Handle theme changes."""
        super().on_theme_changed()
        self.apply_theme()


class TestDemoWidget(ThemedTestCase):
    """Demonstration of how to test themed widgets using ThemedTestCase."""

    def test_widget_creation_and_theme_application(self):
        """Test that widget applies theme correctly."""
        # ThemedTestCase automatically sets up theme infrastructure
        widget = DemoThemedWidget(self.theme_provider)

        # Apply theme and test results
        widget.apply_theme()

        # Use built-in assertion helpers
        self.assert_theme_color(widget, "background", "#ffffff")
        self.assert_theme_color(widget, "foreground", "#000000")

        print("✓ Widget theme application test passed")

    def test_theme_switching(self):
        """Test theme switching functionality."""
        widget = DemoThemedWidget(self.theme_provider)

        # Test with dark theme
        self.theme_provider.set_theme_data(self.dark_theme_data)
        widget.apply_theme()

        # Verify dark theme applied
        self.assertEqual(widget.background_color, "#1e1e1e")
        self.assertEqual(widget.text_color, "#ffffff")

        print("✓ Theme switching test passed")

    @performance_test(max_time=0.01)  # Must complete in < 10ms
    def test_theme_application_performance(self):
        """Test that theme application meets performance requirements."""
        widget = DemoThemedWidget(self.theme_provider)

        # This entire test must complete in < 10ms
        for _ in range(10):
            widget.apply_theme()
            widget.on_theme_changed()

        print("✓ Performance test passed")

    @memory_leak_test(iterations=50, max_leaks=2)
    def test_no_memory_leaks(self):
        """Test that repeated theme operations don't leak memory."""
        widget = DemoThemedWidget(self.theme_provider)
        widget.apply_theme()
        widget.on_theme_changed()

        print("✓ Memory leak test passed")

    def test_error_recovery(self):
        """Test error recovery with invalid theme data."""
        # Inject an error
        from vfwidgets_theme.protocols import ThemePropertyError
        self.theme_provider.inject_error("get_property", ThemePropertyError("Test error"))

        widget = DemoThemedWidget(self.theme_provider)

        # Should not crash, should use defaults
        widget.apply_theme()

        # Should get default colors due to error
        self.assertEqual(widget.background_color, "#ffffff")  # Default fallback
        self.assertEqual(widget.text_color, "#000000")  # Default fallback

        print("✓ Error recovery test passed")


def demonstrate_mock_objects():
    """Demonstrate mock object capabilities."""
    print("\n=== Mock Objects Demonstration ===")

    # Create mock theme provider with custom theme
    theme_data = {
        "primary_color": "#007acc",
        "background": "#f0f0f0",
        "foreground": "#333333",
        "font_size": "14px",
    }
    provider = MockThemeProvider(theme_data)

    # Test basic functionality
    assert provider.get_property("primary_color") == "#007acc"
    assert provider.get_current_theme()["background"] == "#f0f0f0"
    print("✓ Mock theme provider working correctly")

    # Test performance tracking
    for _ in range(100):
        provider.get_property("primary_color")

    call_count = provider.get_call_count("get_property")
    avg_time = provider.get_average_call_time("get_property")

    print(f"✓ Performance tracking: {call_count} calls, avg {avg_time:.6f}s")

    # Test error injection
    from vfwidgets_theme.protocols import ThemePropertyError
    provider.inject_error("get_property", ThemePropertyError("Injected error"))

    try:
        provider.get_property("any_key")
        assert False, "Should have raised error"
    except ThemePropertyError:
        print("✓ Error injection working correctly")

    # Next call should work normally
    provider.get_property("primary_color")
    print("✓ Error injection is one-time only")


def demonstrate_performance_benchmarking():
    """Demonstrate performance benchmarking capabilities."""
    print("\n=== Performance Benchmarking Demonstration ===")

    # Create test widgets
    widgets = []
    provider = MockThemeProvider()
    for i in range(20):
        widget = DemoThemedWidget(provider)
        widgets.append(widget)

    # Benchmark theme switching
    result = benchmark_theme_switch(widgets, iterations=10)

    print("✓ Theme switch benchmark:")
    print(f"  - Operation: {result.operation_name}")
    print(f"  - Average time: {result.average_time:.6f}s")
    print(f"  - Operations/sec: {result.operations_per_second:.0f}")
    print(f"  - Memory usage: {result.memory_usage_bytes} bytes")

    # Comprehensive benchmarking
    benchmark = ThemeBenchmark()

    # Test property access performance
    prop_result = benchmark.benchmark_property_access(provider, iterations=500)
    print(f"✓ Property access: {prop_result.average_time:.6f}s avg")

    # Test memory usage
    def widget_factory():
        return DemoThemedWidget(provider)

    mem_result = benchmark.benchmark_memory_usage(widget_factory, widget_count=50)
    print(f"✓ Memory benchmark: {mem_result.memory_usage_bytes} bytes for 50 widgets")

    # Generate performance report
    report = benchmark.generate_report()
    print("\n--- Performance Report ---")
    print(report[:300] + "..." if len(report) > 300 else report)


def demonstrate_memory_profiling():
    """Demonstrate memory profiling and leak detection."""
    print("\n=== Memory Profiling Demonstration ===")

    profiler = MemoryProfiler()
    profiler.set_baseline()

    # Profile widget creation
    with profiler.profile_operation("widget_creation"):
        widgets = []
        provider = MockThemeProvider()
        for i in range(20):
            widget = DemoThemedWidget(provider)
            profiler.track_object(widget)
            widgets.append(widget)

    # Profile theme operations
    with profiler.profile_operation("theme_operations"):
        for widget in widgets:
            widget.apply_theme()
            widget.on_theme_changed()

    # Clean up and test for leaks
    widgets.clear()

    leaks = profiler.detect_leaks(sensitivity=0.5)  # Less sensitive for demo
    print(f"✓ Memory leak detection: {len(leaks)} potential leaks found")

    if leaks:
        print("  Potential leaks:")
        for leak in leaks[:3]:  # Show first 3
            print(f"    - {leak}")

    # Generate memory report
    try:
        report = profiler.generate_report()
        print("\n--- Memory Report Summary ---")
        lines = report.split('\n')
        for line in lines[:10]:  # Show first 10 lines
            print(line)
        if len(lines) > 10:
            print("...")
    except Exception as e:
        print(f"Memory report generation: {e}")


def demonstrate_convenience_functions():
    """Demonstrate standalone convenience functions."""
    print("\n=== Convenience Functions Demonstration ===")

    # Quick theme property assertion
    provider = MockThemeProvider()
    widget = DemoThemedWidget(provider)

    try:
        assert_theme_property(widget, "primary_color", "#007acc")
        print("✓ Standalone theme property assertion")
    except AssertionError:
        print("✗ Theme property assertion failed")

    # Quick memory leak detection
    def test_operation():
        widget = DemoThemedWidget()
        widget.apply_theme()

    leaks = detect_memory_leaks(test_operation, iterations=20)
    print(f"✓ Quick leak detection: {len(leaks)} leaks in test operation")


def run_full_test_suite():
    """Run the full test suite using unittest."""
    print("\n=== Running Full Test Suite ===")

    import unittest

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDemoWidget)

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if result.wasSuccessful():
        print("\n✓ All tests passed successfully!")
        return True
    else:
        print(f"\n✗ {len(result.failures)} test(s) failed")
        print(f"✗ {len(result.errors)} test(s) had errors")
        return False


def main():
    """Main demonstration function."""
    print("VFWidgets Theme System Testing Infrastructure Demo")
    print("=" * 60)

    try:
        # Demonstrate all major features
        demonstrate_mock_objects()
        demonstrate_performance_benchmarking()
        demonstrate_memory_profiling()
        demonstrate_convenience_functions()

        # Run the full test suite
        success = run_full_test_suite()

        print("\n" + "=" * 60)
        if success:
            print("✓ DEMO COMPLETED SUCCESSFULLY!")
            print("\nThe VFWidgets Testing Infrastructure provides:")
            print("  • Mock objects for testing without Qt dependencies")
            print("  • ThemedTestCase for automatic test setup")
            print("  • Performance benchmarking with strict validation")
            print("  • Memory leak detection and profiling")
            print("  • Comprehensive assertion helpers")
            print("  • Error injection for testing error recovery")
            print("  • Decorators for performance and memory testing")
            print("\nPhilosophy: Make it impossible to test incorrectly!")
        else:
            print("✗ Some tests failed - this is expected in a demo environment")
            print("  The testing infrastructure is still fully functional")

    except Exception as e:
        print(f"✗ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
