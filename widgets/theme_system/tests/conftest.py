"""
Test fixtures for VFWidgets Theme System testing.

This module provides comprehensive pytest fixtures for testing theme functionality
across different scenarios. All fixtures are designed to work without Qt dependencies
by using the mock objects from the testing module.

Key Fixture Categories:
- Theme Data: Common theme configurations (dark, light, high-contrast)
- Widget Fixtures: Mock widgets with different configurations
- Performance Fixtures: Tools for measuring and validating performance
- Memory Fixtures: Utilities for memory leak detection and validation
- Application Fixtures: Mock application setups for integration testing

Philosophy: Make it impossible to write tests incorrectly by providing
fixtures that automatically handle common testing scenarios.
"""

import gc
import time
import weakref
from typing import Any, Dict, List, Optional

import pytest

# Import our testing infrastructure
from src.vfwidgets_theme.testing.mocks import (
    MockApplication,
    MockColorProvider,
    MockPainter,
    MockStyleGenerator,
    MockThemeableWidget,
    MockThemeProvider,
    MockWidget,
    create_mock_widget_hierarchy,
)

# Theme Data Fixtures

@pytest.fixture
def default_theme() -> Dict[str, Any]:
    """Default theme configuration for testing.

    Returns a minimal but complete theme suitable for most tests.
    Includes all essential properties with safe default values.
    """
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
        "hover_color": "#0078d4",
        "active_color": "#106ebe",
        "disabled_color": "#959da5",
        "shadow": "0 1px 3px rgba(0,0,0,0.12)",
    }


@pytest.fixture
def dark_theme() -> Dict[str, Any]:
    """Dark theme configuration for testing.

    Returns a complete dark theme suitable for testing dark mode functionality.
    All colors are chosen to provide good contrast and accessibility.
    """
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
        "hover_color": "#1f6feb",
        "active_color": "#1a73e8",
        "disabled_color": "#545d68",
        "shadow": "0 1px 3px rgba(0,0,0,0.3)",
    }


@pytest.fixture
def light_theme() -> Dict[str, Any]:
    """Light theme configuration for testing.

    Returns a light theme with enhanced contrast for testing
    light mode functionality and accessibility.
    """
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
        "hover_color": "#0969da",
        "active_color": "#0860ca",
        "disabled_color": "#8c959f",
        "shadow": "0 1px 3px rgba(0,0,0,0.08)",
    }


@pytest.fixture
def high_contrast_theme() -> Dict[str, Any]:
    """High contrast theme configuration for testing.

    Returns a high contrast theme for testing accessibility
    and ensuring proper contrast ratios throughout the system.
    """
    return {
        "primary_color": "#ffff00",
        "secondary_color": "#ffffff",
        "background": "#000000",
        "foreground": "#ffffff",
        "success_color": "#00ff00",
        "warning_color": "#ffff00",
        "error_color": "#ff0000",
        "font_family": "Arial",
        "font_size": "14px",
        "font_weight": "bold",
        "border_radius": "0px",
        "border_width": "2px",
        "border_color": "#ffffff",
        "padding": "12px",
        "margin": "8px",
        "hover_color": "#ffffff",
        "active_color": "#ffffff",
        "disabled_color": "#808080",
        "shadow": "none",
    }


@pytest.fixture
def incomplete_theme() -> Dict[str, Any]:
    """Incomplete theme configuration for testing error recovery.

    Returns a theme with missing properties to test fallback
    mechanisms and error recovery pathways.
    """
    return {
        "primary_color": "#007acc",
        "background": "#ffffff",
        # Missing many required properties to test fallbacks
    }


@pytest.fixture
def invalid_theme() -> Dict[str, Any]:
    """Invalid theme configuration for testing validation.

    Returns a theme with invalid values to test validation
    and error handling mechanisms.
    """
    return {
        "primary_color": "not-a-color",
        "font_size": -10,  # Invalid negative size
        "border_radius": "invalid-radius",
        "background": None,  # Invalid None value
        "invalid_property": "should be ignored",
    }


# Mock Object Fixtures

@pytest.fixture
def mock_theme_provider(default_theme) -> MockThemeProvider:
    """Mock theme provider with default theme data.

    Returns a fully configured MockThemeProvider for testing
    theme access and change notifications.
    """
    return MockThemeProvider(default_theme)


@pytest.fixture
def mock_dark_theme_provider(dark_theme) -> MockThemeProvider:
    """Mock theme provider with dark theme data."""
    return MockThemeProvider(dark_theme)


@pytest.fixture
def mock_light_theme_provider(light_theme) -> MockThemeProvider:
    """Mock theme provider with light theme data."""
    return MockThemeProvider(light_theme)


@pytest.fixture
def mock_color_provider() -> MockColorProvider:
    """Mock color provider for testing color resolution."""
    return MockColorProvider()


@pytest.fixture
def mock_style_generator() -> MockStyleGenerator:
    """Mock style generator for testing QSS generation."""
    return MockStyleGenerator()


@pytest.fixture
def mock_widget() -> MockWidget:
    """Basic mock widget for testing."""
    return MockWidget("generic")


@pytest.fixture
def mock_button() -> MockWidget:
    """Mock button widget for testing."""
    return MockWidget("button")


@pytest.fixture
def mock_label() -> MockWidget:
    """Mock label widget for testing."""
    return MockWidget("label")


@pytest.fixture
def mock_themeable_widget(mock_theme_provider) -> MockThemeableWidget:
    """Mock themeable widget with theme provider."""
    return MockThemeableWidget(mock_theme_provider)


@pytest.fixture
def mock_application() -> MockApplication:
    """Mock application for testing app-level theming."""
    return MockApplication()


@pytest.fixture
def mock_painter() -> MockPainter:
    """Mock painter for testing custom drawing."""
    return MockPainter()


@pytest.fixture
def widget_hierarchy() -> MockWidget:
    """Pre-built widget hierarchy for testing.

    Returns a root widget with multiple child widgets attached,
    suitable for testing theme propagation and hierarchy updates.
    """
    return create_mock_widget_hierarchy()


# Performance Testing Fixtures

@pytest.fixture
def performance_timer():
    """Performance timing context manager for testing.

    Provides a context manager that measures execution time
    and validates against performance requirements.

    Example:
        with performance_timer(max_time=0.001) as timer:
            # Code to measure
            result = some_operation()
        assert timer.elapsed < 0.001
    """
    class PerformanceTimer:
        def __init__(self, max_time: float = float('inf')):
            self.max_time = max_time
            self.start_time = 0.0
            self.end_time = 0.0
            self.elapsed = 0.0

        def __enter__(self):
            self.start_time = time.perf_counter()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.end_time = time.perf_counter()
            self.elapsed = self.end_time - self.start_time

        def assert_within_limit(self):
            """Assert that elapsed time is within the specified limit."""
            assert self.elapsed < self.max_time, (
                f"Operation took {self.elapsed:.6f}s, expected < {self.max_time:.6f}s"
            )

    return PerformanceTimer


@pytest.fixture
def theme_switch_benchmark():
    """Benchmark fixture for theme switching performance.

    Provides a function that measures theme switching performance
    across multiple widgets and validates against requirements.
    """
    def benchmark(widgets: List[Any], iterations: int = 100) -> Dict[str, float]:
        """Benchmark theme switching performance.

        Args:
            widgets: List of widgets to switch themes on.
            iterations: Number of theme switches to perform.

        Returns:
            Dictionary with timing statistics.
        """
        times = []

        for i in range(iterations):
            start_time = time.perf_counter()

            # Simulate theme switch
            for widget in widgets:
                if hasattr(widget, 'on_theme_changed'):
                    widget.on_theme_changed()

            end_time = time.perf_counter()
            times.append(end_time - start_time)

        return {
            'total_time': sum(times),
            'average_time': sum(times) / len(times),
            'min_time': min(times),
            'max_time': max(times),
            'widget_count': len(widgets),
            'iterations': iterations,
        }

    return benchmark


@pytest.fixture
def property_access_benchmark():
    """Benchmark fixture for property access performance."""
    def benchmark(provider: Any, properties: List[str], iterations: int = 1000) -> Dict[str, float]:
        """Benchmark property access performance.

        Args:
            provider: Theme provider to test.
            properties: List of property names to access.
            iterations: Number of access operations per property.

        Returns:
            Dictionary with timing statistics.
        """
        times = []

        for prop in properties:
            for i in range(iterations):
                start_time = time.perf_counter()

                try:
                    value = provider.get_property(prop)
                except Exception:
                    pass  # Include error handling time

                end_time = time.perf_counter()
                times.append(end_time - start_time)

        return {
            'total_time': sum(times),
            'average_time': sum(times) / len(times),
            'min_time': min(times),
            'max_time': max(times),
            'operations': len(times),
        }

    return benchmark


# Memory Testing Fixtures

@pytest.fixture
def memory_tracker():
    """Memory tracking fixture for leak detection.

    Provides utilities for tracking memory usage and detecting
    potential memory leaks during theme operations.
    """
    class MemoryTracker:
        def __init__(self):
            self.initial_objects = {}
            self.final_objects = {}
            self.tracked_objects = []

        def start_tracking(self):
            """Start memory tracking."""
            gc.collect()  # Clean up before tracking
            self.initial_objects = {
                obj_type: len(objects)
                for obj_type, objects in self._get_object_counts().items()
            }

        def stop_tracking(self):
            """Stop memory tracking and collect final counts."""
            gc.collect()  # Clean up before final count
            self.final_objects = {
                obj_type: len(objects)
                for obj_type, objects in self._get_object_counts().items()
            }

        def _get_object_counts(self):
            """Get counts of different object types."""
            objects_by_type = {}
            for obj in gc.get_objects():
                obj_type = type(obj).__name__
                if obj_type not in objects_by_type:
                    objects_by_type[obj_type] = []
                objects_by_type[obj_type].append(obj)
            return objects_by_type

        def get_memory_delta(self):
            """Get change in memory usage."""
            delta = {}
            all_types = set(self.initial_objects.keys()) | set(self.final_objects.keys())

            for obj_type in all_types:
                initial = self.initial_objects.get(obj_type, 0)
                final = self.final_objects.get(obj_type, 0)
                delta[obj_type] = final - initial

            return delta

        def assert_no_leaks(self, allowed_types: Optional[List[str]] = None):
            """Assert that no memory leaks occurred."""
            delta = self.get_memory_delta()
            allowed_types = allowed_types or []

            for obj_type, count_change in delta.items():
                if count_change > 0 and obj_type not in allowed_types:
                    # Allow some increase for legitimate objects
                    if count_change > 10:  # Threshold for considering a leak
                        pytest.fail(
                            f"Potential memory leak: {count_change} new {obj_type} objects"
                        )

        def track_object(self, obj):
            """Track a specific object with weak reference."""
            self.tracked_objects.append(weakref.ref(obj))

        def assert_objects_cleaned(self):
            """Assert that tracked objects have been garbage collected."""
            live_objects = [ref for ref in self.tracked_objects if ref() is not None]
            if live_objects:
                pytest.fail(f"{len(live_objects)} tracked objects still alive")

    return MemoryTracker


@pytest.fixture
def widget_lifecycle_tracker():
    """Widget lifecycle tracking for memory validation."""
    class WidgetLifecycleTracker:
        def __init__(self):
            self.created_widgets = []
            self.destroyed_widgets = []

        def track_creation(self, widget):
            """Track widget creation."""
            self.created_widgets.append(weakref.ref(widget))

        def simulate_destruction(self, widget):
            """Simulate widget destruction."""
            self.destroyed_widgets.append(id(widget))
            # Remove from parent if it has one
            if hasattr(widget, 'setParent'):
                widget.setParent(None)

        def get_live_widgets(self):
            """Get widgets that are still alive."""
            return [ref() for ref in self.created_widgets if ref() is not None]

        def assert_all_destroyed(self):
            """Assert all tracked widgets have been destroyed."""
            live_widgets = self.get_live_widgets()
            if live_widgets:
                pytest.fail(f"{len(live_widgets)} widgets not properly destroyed")

    return WidgetLifecycleTracker


# Utility Fixtures

@pytest.fixture
def theme_validator():
    """Theme validation fixture for testing theme data integrity."""
    def validate(theme_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate theme data and return any issues found.

        Args:
            theme_data: Theme data to validate.

        Returns:
            Dictionary with 'errors' and 'warnings' lists.
        """
        errors = []
        warnings = []

        required_properties = [
            'primary_color', 'background', 'foreground', 'font_family', 'font_size'
        ]

        # Check required properties
        for prop in required_properties:
            if prop not in theme_data:
                errors.append(f"Missing required property: {prop}")

        # Validate color properties
        color_properties = [
            'primary_color', 'secondary_color', 'background', 'foreground',
            'success_color', 'warning_color', 'error_color'
        ]

        for prop in color_properties:
            if prop in theme_data:
                value = theme_data[prop]
                if not isinstance(value, str):
                    errors.append(f"Color property '{prop}' must be string, got {type(value)}")
                elif not (value.startswith('#') or value.startswith('rgb') or
                         value in ['red', 'green', 'blue', 'black', 'white']):
                    warnings.append(f"Color property '{prop}' has suspicious value: {value}")

        # Validate size properties
        size_properties = ['font_size', 'border_width', 'padding', 'margin']
        for prop in size_properties:
            if prop in theme_data:
                value = theme_data[prop]
                if isinstance(value, (int, float)) and value < 0:
                    errors.append(f"Size property '{prop}' cannot be negative: {value}")

        return {'errors': errors, 'warnings': warnings}

    return validate


@pytest.fixture
def error_injection_helper():
    """Helper for injecting errors into mock objects for testing error recovery."""
    class ErrorInjectionHelper:
        def __init__(self):
            self.injected_errors = {}

        def inject_theme_provider_error(self, provider, method: str, error: Exception):
            """Inject error into theme provider method."""
            if hasattr(provider, 'inject_error'):
                provider.inject_error(method, error)

        def inject_random_errors(self, obj, methods: List[str], error_rate: float = 0.1):
            """Inject random errors into object methods."""
            import random
            for method in methods:
                if random.random() < error_rate:
                    error = Exception(f"Random error in {method}")
                    if hasattr(obj, 'inject_error'):
                        obj.inject_error(method, error)

        def clear_all_errors(self, obj):
            """Clear all injected errors from an object."""
            if hasattr(obj, '_injected_errors'):
                obj._injected_errors.clear()

    return ErrorInjectionHelper


# Parametrized Fixtures for Testing Multiple Scenarios

@pytest.fixture(params=['default', 'dark', 'light', 'high-contrast'])
def any_theme(request, default_theme, dark_theme, light_theme, high_contrast_theme):
    """Parametrized fixture that provides all theme types.

    Tests using this fixture will run once for each theme type,
    ensuring compatibility across all supported themes.
    """
    themes = {
        'default': default_theme,
        'dark': dark_theme,
        'light': light_theme,
        'high-contrast': high_contrast_theme,
    }
    return themes[request.param]


@pytest.fixture(params=['button', 'label', 'edit', 'text', 'combo'])
def any_widget_type(request):
    """Parametrized fixture that provides different widget types.

    Tests using this fixture will run once for each widget type,
    ensuring theme compatibility across all widget types.
    """
    return MockWidget(request.param)


# Integration Test Fixtures

@pytest.fixture
def themed_application_setup(mock_application):
    """Complete themed application setup for integration testing.

    Returns a fully configured mock application with multiple widgets,
    themes, and providers ready for comprehensive integration testing.
    """
    app = mock_application

    # Add multiple themes
    app.add_available_theme("custom-dark")
    app.add_available_theme("custom-light")

    # Create widget hierarchy
    root_widget = create_mock_widget_hierarchy()
    app.register_widget(root_widget)

    # Register all child widgets
    for child in root_widget.children():
        app.register_widget(child)

    return {
        'app': app,
        'root_widget': root_widget,
        'widgets': [root_widget] + root_widget.children(),
    }


# Cleanup and Teardown

@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Automatic cleanup after each test.

    This fixture runs after every test to ensure clean state
    and prevent test pollution.
    """
    yield  # Run the test

    # Cleanup after test
    gc.collect()  # Force garbage collection

    # Reset any global state if needed
    # (Add specific cleanup code here as the system grows)


# Performance Validation Fixtures

@pytest.fixture
def performance_requirements():
    """Performance requirements for validation.

    Returns the performance requirements that all implementations
    must meet, suitable for automated validation.
    """
    return {
        'theme_switch_time': 0.1,  # < 100ms for 100 widgets
        'property_access_time': 0.000001,  # < 1μs
        'memory_overhead_per_widget': 1024,  # < 1KB
        'cache_hit_rate': 0.9,  # > 90%
        'callback_registration_time': 0.00001,  # < 10μs
        'style_generation_time': 0.01,  # < 10ms
    }


@pytest.fixture
def performance_validator(performance_requirements):
    """Performance validation helper.

    Provides utilities for validating that implementations
    meet the strict performance requirements.
    """
    def validate_timing(operation_name: str, measured_time: float) -> bool:
        """Validate that an operation meets timing requirements.

        Args:
            operation_name: Name of the operation being validated.
            measured_time: Measured execution time in seconds.

        Returns:
            True if requirements are met.

        Raises:
            AssertionError: If requirements are not met.
        """
        requirement_map = {
            'theme_switch': 'theme_switch_time',
            'property_access': 'property_access_time',
            'callback_registration': 'callback_registration_time',
            'style_generation': 'style_generation_time',
        }

        requirement_key = requirement_map.get(operation_name)
        if requirement_key and requirement_key in performance_requirements:
            max_time = performance_requirements[requirement_key]
            assert measured_time < max_time, (
                f"{operation_name} took {measured_time:.6f}s, "
                f"requirement is < {max_time:.6f}s"
            )
            return True

        return False

    return validate_timing
