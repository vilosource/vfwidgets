"""Testing utilities and ThemedTestCase base class for VFWidgets Theme System.

This module provides essential testing utilities that make it easy to write
comprehensive tests for themed widgets and components. The ThemedTestCase
base class provides automatic setup and validation for theme-related testing.

Key Features:
- ThemedTestCase: Base class with automatic theme setup and validation
- Assertion helpers for theme property validation
- Performance decorators with built-in validation
- Test data generators for comprehensive testing scenarios
- Widget factory functions for consistent test object creation

Philosophy: Make it impossible to write theme tests incorrectly while
providing maximum convenience and validation for developers.
"""

import gc
import time
import unittest
from contextlib import contextmanager
from typing import Any, Callable, Dict, List, Optional

from ..protocols import ColorValue, ThemeData
from .benchmarks import ThemeBenchmark
from .memory import MemoryProfiler
from .mocks import (
    MockApplication,
    MockColorProvider,
    MockStyleGenerator,
    MockThemeableWidget,
    MockThemeProvider,
    MockWidget,
    create_mock_widget_hierarchy,
)


class ThemedTestCase(unittest.TestCase):
    """Base test case class for theme system testing.

    Provides automatic setup of theme infrastructure, common assertion methods,
    and validation utilities. All theme-related tests should inherit from this
    class to ensure consistent testing patterns and automatic validation.

    Example:
        class TestMyThemedWidget(ThemedTestCase):
            def test_widget_applies_theme(self):
                widget = self.create_test_widget("button")
                self.assert_theme_property(widget, "primary_color", "#007acc")

            def test_performance_requirements(self):
                with self.assert_performance(max_time=0.001):
                    widget.on_theme_changed()

            def test_no_memory_leaks(self):
                with self.assert_no_memory_leaks():
                    for _ in range(100):
                        widget = self.create_test_widget("button")
                        widget.on_theme_changed()

    Automatic Features:
    - Theme provider setup with default themes
    - Performance benchmarking utilities
    - Memory leak detection
    - Common assertion helpers
    - Test data generators

    """

    def setUp(self) -> None:
        """Set up theme testing infrastructure."""
        super().setUp()

        # Create mock theme infrastructure
        self.default_theme_data = self._get_default_theme_data()
        self.dark_theme_data = self._get_dark_theme_data()
        self.light_theme_data = self._get_light_theme_data()

        self.theme_provider = MockThemeProvider(self.default_theme_data)
        self.color_provider = MockColorProvider()
        self.style_generator = MockStyleGenerator()
        self.mock_application = MockApplication()

        # Performance and memory tracking
        self.benchmark = ThemeBenchmark()
        self.memory_profiler = MemoryProfiler()
        self.memory_profiler.set_baseline()

        # Track created widgets for cleanup
        self._created_widgets: List[Any] = []

    def tearDown(self) -> None:
        """Clean up after theme testing."""
        # Clean up created widgets
        for widget in self._created_widgets:
            if hasattr(widget, 'setParent'):
                widget.setParent(None)
        self._created_widgets.clear()

        # Clean up profiling resources
        self.memory_profiler.cleanup()

        # Force garbage collection
        gc.collect()

        super().tearDown()

    def _get_default_theme_data(self) -> Dict[str, Any]:
        """Get default theme data for testing."""
        return {
            "primary_color": "#007acc",
            "secondary_color": "#6f6f6f",
            "background": "#ffffff",
            "foreground": "#000000",
            "success_color": "#28a745",
            "warning_color": "#ffc107",
            "error_color": "#dc3545",
            "font_family": "Segoe UI",
            "font_size": "12px",
            "font_weight": "normal",
            "border_radius": "4px",
            "border_width": "1px",
            "border_color": "#d0d7de",
            "padding": "8px",
            "margin": "4px",
        }

    def _get_dark_theme_data(self) -> Dict[str, Any]:
        """Get dark theme data for testing."""
        return {
            "primary_color": "#0078d4",
            "secondary_color": "#8a8a8a",
            "background": "#1e1e1e",
            "foreground": "#ffffff",
            "success_color": "#2ea043",
            "warning_color": "#fb8500",
            "error_color": "#f85149",
            "font_family": "Segoe UI",
            "font_size": "12px",
            "font_weight": "normal",
            "border_radius": "4px",
            "border_width": "1px",
            "border_color": "#444c56",
            "padding": "8px",
            "margin": "4px",
        }

    def _get_light_theme_data(self) -> Dict[str, Any]:
        """Get light theme data for testing."""
        return {
            "primary_color": "#0066cc",
            "secondary_color": "#6f7883",
            "background": "#f8f9fa",
            "foreground": "#24292f",
            "success_color": "#1a7f37",
            "warning_color": "#9a6700",
            "error_color": "#cf222e",
            "font_family": "Segoe UI",
            "font_size": "12px",
            "font_weight": "normal",
            "border_radius": "4px",
            "border_width": "1px",
            "border_color": "#d0d7de",
            "padding": "8px",
            "margin": "4px",
        }

    # Widget creation utilities

    def create_test_widget(self, widget_type: str = "generic") -> MockWidget:
        """Create a test widget with automatic cleanup tracking.

        Args:
            widget_type: Type of widget to create.

        Returns:
            MockWidget instance tracked for cleanup.

        """
        widget = MockWidget(widget_type)
        self._created_widgets.append(widget)
        self.memory_profiler.track_object(widget)
        return widget

    def create_test_themeable_widget(
        self,
        theme_provider: Optional[MockThemeProvider] = None
    ) -> MockThemeableWidget:
        """Create a test themeable widget with automatic cleanup tracking.

        Args:
            theme_provider: Theme provider to use. Uses default if None.

        Returns:
            MockThemeableWidget instance tracked for cleanup.

        """
        provider = theme_provider or self.theme_provider
        widget = MockThemeableWidget(provider)
        self._created_widgets.append(widget)
        self.memory_profiler.track_object(widget)
        return widget

    def create_test_widget_hierarchy(self) -> MockWidget:
        """Create a test widget hierarchy with automatic cleanup tracking.

        Returns:
            Root MockWidget with children attached.

        """
        hierarchy = create_mock_widget_hierarchy()
        self._created_widgets.append(hierarchy)
        self.memory_profiler.track_object(hierarchy)

        # Track all children too
        for child in hierarchy.children():
            self._created_widgets.append(child)
            self.memory_profiler.track_object(child)

        return hierarchy

    # Theme assertion utilities

    def assert_theme_property(
        self,
        widget: Any,
        property_key: str,
        expected_value: Any,
        msg: Optional[str] = None
    ) -> None:
        """Assert that a widget has the expected theme property value.

        Args:
            widget: Widget to check property on.
            property_key: Theme property key to check.
            expected_value: Expected property value.
            msg: Optional assertion message.

        """
        if hasattr(widget, 'get_theme_property'):
            actual_value = widget.get_theme_property(property_key)
        elif hasattr(widget, 'get_property'):
            actual_value = widget.get_property(property_key)
        else:
            self.fail(f"Widget {widget} does not support theme property access")

        self.assertEqual(
            actual_value,
            expected_value,
            msg or f"Theme property '{property_key}' mismatch"
        )

    def assert_theme_color(
        self,
        widget: Any,
        color_key: str,
        expected_color: ColorValue,
        msg: Optional[str] = None
    ) -> None:
        """Assert that a widget has the expected theme color.

        Args:
            widget: Widget to check color on.
            color_key: Theme color key to check.
            expected_color: Expected color value.
            msg: Optional assertion message.

        """
        if hasattr(widget, 'get_theme_color'):
            actual_color = widget.get_theme_color(color_key)
        else:
            self.fail(f"Widget {widget} does not support theme color access")

        self.assertEqual(
            actual_color,
            expected_color,
            msg or f"Theme color '{color_key}' mismatch"
        )

    def assert_valid_theme_data(
        self,
        theme_data: ThemeData,
        required_properties: Optional[List[str]] = None,
        msg: Optional[str] = None
    ) -> None:
        """Assert that theme data is valid and complete.

        Args:
            theme_data: Theme data dictionary to validate.
            required_properties: List of required property keys.
            msg: Optional assertion message.

        """
        self.assertIsInstance(theme_data, dict, "Theme data must be a dictionary")

        required_properties = required_properties or [
            'primary_color', 'background', 'foreground', 'font_family', 'font_size'
        ]

        for prop in required_properties:
            self.assertIn(
                prop,
                theme_data,
                msg or f"Required theme property '{prop}' missing"
            )

        # Validate color properties
        color_properties = [
            'primary_color', 'secondary_color', 'background', 'foreground',
            'success_color', 'warning_color', 'error_color'
        ]

        for prop in color_properties:
            if prop in theme_data:
                value = theme_data[prop]
                self.assertIsInstance(
                    value,
                    str,
                    f"Color property '{prop}' must be string"
                )
                self.assertTrue(
                    value.startswith('#') or value.startswith('rgb') or
                    value in ['red', 'green', 'blue', 'black', 'white'],
                    f"Color property '{prop}' has invalid value: {value}"
                )

    def assert_stylesheet_valid(
        self,
        stylesheet: str,
        widget_type: Optional[str] = None,
        msg: Optional[str] = None
    ) -> None:
        """Assert that a QSS stylesheet is valid.

        Args:
            stylesheet: QSS stylesheet string to validate.
            widget_type: Expected widget type in stylesheet.
            msg: Optional assertion message.

        """
        self.assertIsInstance(stylesheet, str, "Stylesheet must be string")
        self.assertTrue(stylesheet.strip(), "Stylesheet cannot be empty")

        if widget_type:
            # Simple validation that widget type appears in stylesheet
            widget_selectors = {
                'button': 'QPushButton',
                'label': 'QLabel',
                'edit': 'QLineEdit',
                'text': 'QTextEdit',
                'combo': 'QComboBox',
            }

            expected_selector = widget_selectors.get(widget_type, f'Q{widget_type.title()}')
            self.assertIn(
                expected_selector,
                stylesheet,
                msg or f"Stylesheet missing selector for {widget_type}"
            )

    # Performance assertion utilities

    @contextmanager
    def assert_performance(self, max_time: float, operation_name: str = "test_operation"):
        """Context manager for asserting performance requirements.

        Args:
            max_time: Maximum allowed execution time in seconds.
            operation_name: Name of operation for reporting.

        Example:
            with self.assert_performance(max_time=0.001):
                widget.on_theme_changed()

        """
        start_time = time.perf_counter()

        try:
            yield
        finally:
            end_time = time.perf_counter()
            elapsed = end_time - start_time

            self.assertLess(
                elapsed,
                max_time,
                f"Operation '{operation_name}' took {elapsed:.6f}s, "
                f"expected < {max_time:.6f}s"
            )

    def assert_performance_requirement(
        self,
        operation: Callable[[], Any],
        requirement_type: str,
        iterations: int = 100
    ) -> None:
        """Assert that an operation meets specific performance requirements.

        Args:
            operation: Function to test performance of.
            requirement_type: Type of requirement to validate.
            iterations: Number of iterations to run.

        """
        requirements = {
            'theme_switch': 0.1,  # 100ms for 100 widgets
            'property_access': 0.0001,  # 100μs (more realistic for test environment with mocks)
            'callback_registration': 0.001,  # 1ms (more realistic for test environment)
            'style_generation': 0.01,  # 10ms
        }

        if requirement_type not in requirements:
            self.fail(f"Unknown performance requirement: {requirement_type}")

        max_time = requirements[requirement_type]

        # Run operation multiple times and check average
        times = []
        for _ in range(iterations):
            start_time = time.perf_counter()
            operation()
            end_time = time.perf_counter()
            times.append(end_time - start_time)

        avg_time = sum(times) / len(times)
        self.assertLess(
            avg_time,
            max_time,
            f"Performance requirement '{requirement_type}' not met: "
            f"avg {avg_time:.6f}s > {max_time:.6f}s"
        )

    # Memory assertion utilities

    @contextmanager
    def assert_no_memory_leaks(self, max_leaks: int = 0):
        """Context manager for asserting no memory leaks occur.

        Args:
            max_leaks: Maximum allowed number of potential leaks.

        Example:
            with self.assert_no_memory_leaks():
                for _ in range(100):
                    widget = self.create_test_widget()
                    widget.on_theme_changed()

        """
        with self.memory_profiler.profile_operation("leak_test") as profiler:
            yield profiler

        leaks = self.memory_profiler.detect_leaks()
        self.assertLessEqual(
            len(leaks),
            max_leaks,
            f"Memory leaks detected: {leaks}"
        )

    def assert_memory_requirement(
        self,
        operation: Callable[[], Any],
        max_memory_mb: float,
        iterations: int = 10
    ) -> None:
        """Assert that an operation meets memory requirements.

        Args:
            operation: Function to test memory usage of.
            max_memory_mb: Maximum allowed memory usage in megabytes.
            iterations: Number of iterations to run.

        """
        import tracemalloc

        tracemalloc.start()

        try:
            for _ in range(iterations):
                operation()

            current, peak = tracemalloc.get_traced_memory()
            peak_mb = peak / (1024 * 1024)

            self.assertLess(
                peak_mb,
                max_memory_mb,
                f"Memory usage {peak_mb:.2f}MB exceeds limit {max_memory_mb:.2f}MB"
            )

        finally:
            tracemalloc.stop()

    # Test data generation utilities

    def generate_test_theme(
        self,
        base_theme: str = "default",
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate test theme data with optional overrides.

        Args:
            base_theme: Base theme to start with.
            overrides: Properties to override in base theme.

        Returns:
            Complete theme data dictionary.

        """
        base_themes = {
            'default': self.default_theme_data,
            'dark': self.dark_theme_data,
            'light': self.light_theme_data,
        }

        if base_theme not in base_themes:
            raise ValueError(f"Unknown base theme: {base_theme}")

        theme_data = base_themes[base_theme].copy()

        if overrides:
            theme_data.update(overrides)

        return theme_data

    def generate_test_widgets(
        self,
        widget_types: List[str],
        count_per_type: int = 1
    ) -> List[MockWidget]:
        """Generate multiple test widgets of different types.

        Args:
            widget_types: List of widget types to create.
            count_per_type: Number of widgets to create per type.

        Returns:
            List of created widgets.

        """
        widgets = []

        for widget_type in widget_types:
            for _ in range(count_per_type):
                widget = self.create_test_widget(widget_type)
                widgets.append(widget)

        return widgets

    def simulate_theme_switch(
        self,
        widgets: List[Any],
        theme_name: str = "dark"
    ) -> float:
        """Simulate theme switching on multiple widgets.

        Args:
            widgets: List of widgets to switch themes on.
            theme_name: Name of theme to switch to.

        Returns:
            Total time taken for theme switch in seconds.

        """
        start_time = time.perf_counter()

        for widget in widgets:
            if hasattr(widget, 'on_theme_changed'):
                widget.on_theme_changed()
            elif hasattr(widget, 'setStyleSheet'):
                # Simulate QSS update
                new_style = f"color: {theme_name};"
                widget.setStyleSheet(new_style)

        end_time = time.perf_counter()
        return end_time - start_time

    # Utility assertion helpers

    def assert_color_valid(self, color: ColorValue, msg: Optional[str] = None) -> None:
        """Assert that a color value is valid.

        Args:
            color: Color value to validate.
            msg: Optional assertion message.

        """
        self.assertIsInstance(color, str, "Color must be string")

        # Basic color validation
        valid_color = (
            color.startswith('#') and len(color) in [4, 7] or
            color.startswith('rgb') or
            color.lower() in ['red', 'green', 'blue', 'black', 'white', 'transparent']
        )

        self.assertTrue(
            valid_color,
            msg or f"Invalid color value: {color}"
        )

    def assert_font_valid(self, font: str, msg: Optional[str] = None) -> None:
        """Assert that a font specification is valid.

        Args:
            font: Font specification to validate.
            msg: Optional assertion message.

        """
        self.assertIsInstance(font, str, "Font must be string")
        self.assertTrue(font.strip(), "Font cannot be empty")

        # Basic font validation - should contain at least a family name
        parts = font.split()
        self.assertGreaterEqual(
            len(parts),
            1,
            msg or f"Invalid font specification: {font}"
        )

    def assert_size_valid(self, size: str, msg: Optional[str] = None) -> None:
        """Assert that a size specification is valid.

        Args:
            size: Size specification to validate.
            msg: Optional assertion message.

        """
        self.assertIsInstance(size, str, "Size must be string")

        # Should contain number and unit
        valid_units = ['px', 'pt', 'em', 'rem', '%']
        has_valid_unit = any(size.endswith(unit) for unit in valid_units)

        self.assertTrue(
            has_valid_unit,
            msg or f"Invalid size specification: {size}"
        )


# Utility functions for testing

def assert_theme_property(widget: Any, property_key: str, expected_value: Any) -> None:
    """Standalone assertion for theme property values.

    Args:
        widget: Widget to check property on.
        property_key: Theme property key to check.
        expected_value: Expected property value.

    """
    if hasattr(widget, 'get_theme_property'):
        actual_value = widget.get_theme_property(property_key)
    elif hasattr(widget, 'get_property'):
        actual_value = widget.get_property(property_key)
    else:
        raise AssertionError(f"Widget {widget} does not support theme property access")

    assert actual_value == expected_value, (
        f"Theme property '{property_key}' mismatch: "
        f"expected {expected_value}, got {actual_value}"
    )


def assert_performance_requirement(
    operation: Callable[[], Any],
    max_time: float,
    iterations: int = 100
) -> None:
    """Standalone assertion for performance requirements.

    Args:
        operation: Function to test performance of.
        max_time: Maximum allowed execution time in seconds.
        iterations: Number of iterations to run.

    """
    times = []
    for _ in range(iterations):
        start_time = time.perf_counter()
        operation()
        end_time = time.perf_counter()
        times.append(end_time - start_time)

    avg_time = sum(times) / len(times)
    assert avg_time < max_time, (
        f"Performance requirement not met: avg {avg_time:.6f}s > {max_time:.6f}s"
    )


def generate_test_theme(
    base_theme: str = "default",
    overrides: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Generate test theme data with optional overrides.

    Args:
        base_theme: Base theme to start with.
        overrides: Properties to override in base theme.

    Returns:
        Complete theme data dictionary.

    """
    base_themes = {
        'default': {
            "primary_color": "#007acc",
            "background": "#ffffff",
            "foreground": "#000000",
            "font_family": "Segoe UI",
            "font_size": "12px",
        },
        'dark': {
            "primary_color": "#0078d4",
            "background": "#1e1e1e",
            "foreground": "#ffffff",
            "font_family": "Segoe UI",
            "font_size": "12px",
        },
        'light': {
            "primary_color": "#0066cc",
            "background": "#f8f9fa",
            "foreground": "#24292f",
            "font_family": "Segoe UI",
            "font_size": "12px",
        },
    }

    if base_theme not in base_themes:
        raise ValueError(f"Unknown base theme: {base_theme}")

    theme_data = base_themes[base_theme].copy()

    if overrides:
        theme_data.update(overrides)

    return theme_data


def create_test_widget(widget_type: str = "generic") -> MockWidget:
    """Create a test widget without automatic cleanup.

    Args:
        widget_type: Type of widget to create.

    Returns:
        MockWidget instance.

    """
    return MockWidget(widget_type)
