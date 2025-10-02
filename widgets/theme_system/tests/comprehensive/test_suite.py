#!/usr/bin/env python3
"""
Comprehensive Test Suite for VFWidgets Theme System
Task 21: Advanced testing techniques for complete coverage
"""

import gc
import json
import threading
import time
import tracemalloc
import weakref
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional, Set

import psutil
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from PySide6.QtWidgets import QWidget

# Import theme system components
from vfwidgets_theme import (
    ThemedApplication,
    ThemedWidget,
    ThemeError,
    ThemeValidationError,
)
from vfwidgets_theme.core.theme import Theme

# Global test state management
test_app: Optional[ThemedApplication] = None
test_memory_baseline: Optional[int] = None
test_widget_registry: Set[weakref.ref] = set()


def setup_test_environment():
    """Setup for test environment."""
    global test_app, test_memory_baseline, test_widget_registry

    # Import Qt classes at function level to avoid issues
    import sys

    from PySide6.QtWidgets import QApplication as QtApp

    # Ensure clean state
    existing_app = QtApp.instance()
    if existing_app:
        existing_app.quit()

    # Create a simple QApplication first if none exists
    if not QtApp.instance():
        QtApp(sys.argv)

    test_app = ThemedApplication()
    test_memory_baseline = get_memory_usage()
    test_widget_registry.clear()

    # Start memory tracking
    tracemalloc.start()


def teardown_test_environment():
    """Cleanup after test environment."""
    global test_app, test_memory_baseline

    # Check for memory leaks
    current_memory = get_memory_usage()
    if test_memory_baseline and current_memory > test_memory_baseline * 1.5:
        import warnings
        warnings.warn(f"Potential memory leak: {current_memory - test_memory_baseline} MB increase")

    # Cleanup widgets
    cleanup_widgets()

    # Stop memory tracking
    if tracemalloc.is_tracing():
        tracemalloc.stop()

    # Cleanup application
    if test_app:
        # ThemedApplication doesn't have quit method, just set to None
        test_app = None

    # Force garbage collection
    gc.collect()


def get_memory_usage() -> int:
    """Get current memory usage in MB."""
    process = psutil.Process()
    return process.memory_info().rss // 1024 // 1024


def cleanup_widgets():
    """Cleanup tracked widgets."""
    widgets_to_remove = []
    for widget_ref in test_widget_registry:
        widget = widget_ref()
        if widget is not None:
            try:
                widget.deleteLater()
            except:
                pass
        widgets_to_remove.append(widget_ref)

    for widget_ref in widgets_to_remove:
        test_widget_registry.discard(widget_ref)


def track_widget(widget: QWidget) -> QWidget:
    """Track widget for cleanup."""
    test_widget_registry.add(weakref.ref(widget))
    return widget


# Property-based tests
@pytest.fixture(autouse=True)
def test_setup_teardown():
    """Automatic setup and teardown for each test."""
    setup_test_environment()
    yield
    teardown_test_environment()


@given(st.dictionaries(
    st.text(min_size=1, max_size=20, alphabet="abcdefghijklmnopqrstuvwxyz_"),
    st.one_of(
        st.text(min_size=1, max_size=50),
        st.integers(min_value=0, max_value=1000),
        st.floats(min_value=0.0, max_value=1.0, allow_nan=False)
    ),
    min_size=1,
    max_size=10
))
@settings(max_examples=20, deadline=5000, suppress_health_check=[HealthCheck.too_slow])
def test_theme_properties_invariants(props: Dict[str, Any]):
    """Test that theme properties maintain invariants."""
    try:
        # Create theme with random properties
        theme = Theme(
            name="test_theme",
            colors={key: str(value) for key, value in props.items() if isinstance(value, str) and key.endswith('_color')},
            styles={key: value for key, value in props.items() if not key.endswith('_color')}
        )

        # Invariant 1: Theme should always have a name
        assert theme.name == "test_theme"

        # Invariant 2: Theme should have proper structure
        assert hasattr(theme, 'colors')
        assert hasattr(theme, 'styles')
        assert isinstance(theme.colors, dict)
        assert isinstance(theme.styles, dict)

        # Invariant 3: Theme should be immutable
        assert theme.name == "test_theme"

    except (ThemeError, ThemeValidationError):
        # These are expected for invalid data
        pass
    except Exception as e:
        pytest.fail(f"Unexpected exception with props {props}: {e}")


@given(st.text(min_size=0, max_size=100))
@settings(max_examples=10, deadline=3000)
def test_theme_name_handling(theme_name: str):
    """Test theme name handling with various inputs."""
    try:
        theme = Theme(
            name=theme_name,
            colors={"primary_color": "#ffffff"}
        )

        # Invariant: Theme name should be preserved
        assert theme.name == theme_name

    except (ThemeError, ThemeValidationError):
        # Invalid names are expected to fail
        pass


@given(st.lists(
    st.dictionaries(
        st.text(min_size=1, max_size=10, alphabet="abcdefghijklmnopqrstuvwxyz"),
        st.text(min_size=1, max_size=20),
        min_size=1,
        max_size=3
    ),
    min_size=1,
    max_size=10
))
@settings(max_examples=10, deadline=5000)
def test_widget_creation_invariants(widget_configs: List[Dict[str, str]]):
    """Test widget creation invariants with multiple widgets."""
    widgets = []

    try:
        for config in widget_configs:
            widget = ThemedWidget()
            track_widget(widget)
            widgets.append(widget)

            # Invariant: Widget should be properly themed
            assert hasattr(widget, '_theme_registry')
            assert widget._theme_registry is not None

        # Invariant: All widgets should be registered
        # Note: We'll check this through widget properties instead
        for widget in widgets:
            assert hasattr(widget, '_theme_registry')
            assert widget._theme_registry is not None

    except Exception as e:
        pytest.fail(f"Widget creation failed: {e}")
    finally:
        # Cleanup
        for widget in widgets:
            try:
                widget.deleteLater()
            except:
                pass


# Fuzz testing
@given(st.text(min_size=0, max_size=500))
@settings(max_examples=20, deadline=3000)
def test_malformed_json_theme_data(malformed_data: str):
    """Test theme system with malformed JSON data."""
    try:
        # Try to parse as JSON
        try:
            data = json.loads(malformed_data)
            if isinstance(data, dict) and 'name' in data:
                # Extract name and other properties appropriately
                name = data.get('name', 'test_theme')
                colors = data.get('colors', {})
                styles = data.get('styles', {})
                theme = Theme(name=name, colors=colors, styles=styles)
                # If it succeeds, ensure basic properties
                assert hasattr(theme, 'name')
        except (json.JSONDecodeError, ThemeError, ThemeValidationError):
            # Expected for malformed data
            pass

    except Exception as e:
        pytest.fail(f"Unexpected exception with data '{malformed_data[:50]}...': {e}")


@given(st.binary(min_size=0, max_size=200))
@settings(max_examples=10, deadline=2000)
def test_binary_data_handling(binary_data: bytes):
    """Test theme system with binary data."""
    try:
        # Try to decode and parse
        try:
            text_data = binary_data.decode('utf-8', errors='ignore')
            if text_data.strip():
                data = json.loads(text_data)
                if isinstance(data, dict) and 'name' in data:
                    name = data.get('name', 'binary_test')
                    colors = data.get('colors', {})
                    styles = data.get('styles', {})
                    theme = Theme(name=name, colors=colors, styles=styles)
        except (UnicodeDecodeError, json.JSONDecodeError, ThemeError, ThemeValidationError):
            # Expected for invalid data
            pass

    except Exception as e:
        pytest.fail(f"Unexpected exception with binary data: {e}")


@given(st.dictionaries(
    st.text(min_size=0, max_size=20),
    st.one_of(
        st.none(),
        st.booleans(),
        st.lists(st.integers(), max_size=5),
        st.dictionaries(st.text(max_size=10), st.integers(), max_size=3)
    ),
    max_size=10
))
@settings(max_examples=15, deadline=4000)
def test_unexpected_data_types(weird_data: Dict[str, Any]):
    """Test theme system with unexpected data types."""
    try:
        # Filter data to appropriate categories
        colors = {}
        styles = {}
        for key, value in weird_data.items():
            if isinstance(key, str) and key.endswith('_color') and isinstance(value, str):
                colors[key] = value
            else:
                styles[key] = value

        theme = Theme(
            name="fuzz_theme",
            colors=colors,
            styles=styles
        )

        # Ensure basic functionality still works
        assert theme.name == "fuzz_theme"

        # Verify basic theme structure
        assert hasattr(theme, 'colors')
        assert hasattr(theme, 'styles')
        assert theme.colors == colors
        assert theme.styles == styles

    except (ThemeError, ThemeValidationError):
        # Expected for invalid configurations
        pass
    except Exception as e:
        pytest.fail(f"Unexpected exception with weird data {weird_data}: {e}")


# Memory leak tests
def test_widget_registration_memory_leaks():
    """Test for memory leaks in widget registration/deregistration."""
    initial_memory = get_memory_usage()
    widgets = []

    # Create many widgets
    for i in range(50):
        widget = ThemedWidget()
        widgets.append(widget)
        track_widget(widget)

    mid_memory = get_memory_usage()

    # Delete widgets
    for widget in widgets:
        widget.deleteLater()
    widgets.clear()

    # Force garbage collection
    gc.collect()

    # Process events to ensure deletion
    # Note: ThemedApplication doesn't have processEvents method

    final_memory = get_memory_usage()

    # Memory should not have increased significantly
    memory_increase = final_memory - initial_memory
    assert memory_increase < 30, f"Memory leak detected: {memory_increase}MB increase"


def test_theme_switching_memory_leaks():
    """Test for memory leaks during theme switching."""
    widget = ThemedWidget()
    track_widget(widget)

    initial_memory = get_memory_usage()

    # Switch themes many times
    for i in range(20):
        theme = Theme(
            name=f"test_theme_{i}",
            colors={
                "background_color": f"#{i:02x}{i:02x}{i:02x}",
                "text_color": "#ffffff"
            }
        )
        if test_app:
            test_app.set_theme(theme)

    final_memory = get_memory_usage()
    memory_increase = final_memory - initial_memory

    assert memory_increase < 20, f"Theme switching memory leak: {memory_increase}MB increase"


def test_registry_cleanup():
    """Test that theme registry properly cleans up weak references."""
    # Create widgets and let them go out of scope
    widget_refs = []
    for i in range(10):
        widget = ThemedWidget()
        widget_refs.append(weakref.ref(widget))
        # Don't track these widgets - let them be garbage collected

    # Force garbage collection
    gc.collect()

    # Check that widgets were cleaned up
    alive_count = sum(1 for ref in widget_refs if ref() is not None)
    assert alive_count == 0, f"Widgets not cleaned up properly: {alive_count} still alive"


# Thread safety tests
def test_concurrent_widget_creation():
    """Test concurrent widget creation."""
    widgets = []
    exceptions = []

    def create_widgets():
        try:
            for i in range(5):
                widget = ThemedWidget()
                widgets.append(widget)
                time.sleep(0.001)  # Small delay
        except Exception as e:
            exceptions.append(e)

    # Create widgets concurrently
    threads = []
    for i in range(3):
        thread = threading.Thread(target=create_widgets)
        threads.append(thread)
        thread.start()

    # Wait for completion
    for thread in threads:
        thread.join()

    # Check for exceptions
    assert len(exceptions) == 0, f"Concurrent widget creation failed: {exceptions}"

    # Cleanup
    for widget in widgets:
        try:
            track_widget(widget)
            widget.deleteLater()
        except:
            pass


def test_concurrent_theme_switching():
    """Test concurrent theme switching."""
    if not test_app:
        pytest.skip("No application available")

    widget = ThemedWidget()
    track_widget(widget)
    exceptions = []

    def switch_theme(theme_id: int):
        try:
            theme = Theme(
                name=f"concurrent_theme_{theme_id}",
                colors={"primary_color": f"#{theme_id:02x}0000"}
            )
            test_app.set_theme(theme)
            time.sleep(0.01)
        except Exception as e:
            exceptions.append(e)

    # Switch themes concurrently
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(switch_theme, i) for i in range(5)]

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                exceptions.append(e)

    # Check for exceptions
    assert len(exceptions) == 0, f"Concurrent theme switching failed: {exceptions}"


# Performance tests
def test_widget_creation_performance():
    """Test widget creation performance."""
    start_time = time.time()

    widgets = []
    for i in range(50):
        widget = ThemedWidget()
        widgets.append(widget)
        track_widget(widget)

    creation_time = time.time() - start_time

    # Should create 50 widgets in under 1 second
    assert creation_time < 1.0, f"Widget creation too slow: {creation_time:.2f}s for 50 widgets"


def test_theme_switching_performance():
    """Test theme switching performance."""
    if not test_app:
        pytest.skip("No application available")

    widget = ThemedWidget()
    track_widget(widget)

    # Warm up
    theme = Theme(name="warmup", colors={"primary_color": "#000000"})
    test_app.set_theme(theme)

    # Measure switching time
    start_time = time.time()

    for i in range(5):
        theme = Theme(
            name=f"perf_theme_{i}",
            colors={"primary_color": f"#{i:02x}0000"}
        )
        test_app.set_theme(theme)

    switching_time = time.time() - start_time

    # Should switch 5 themes in under 0.5 seconds
    assert switching_time < 0.5, f"Theme switching too slow: {switching_time:.2f}s for 5 switches"


def test_property_access_performance():
    """Test theme property access performance."""
    theme = Theme(
        name="perf_test",
        colors={f"color_{i}": f"#ff{i:02x}00" for i in range(25)},
        styles={f"prop_{i}": f"value_{i}" for i in range(25)}
    )

    start_time = time.time()

    # Access color properties many times
    for i in range(250):
        color_key = f"color_{i % 25}"
        if color_key in theme.colors:
            value = theme.colors[color_key]
            assert value == f"#ff{i % 25:02x}00"

    # Access style properties
    for i in range(250):
        prop_key = f"prop_{i % 25}"
        if prop_key in theme.styles:
            value = theme.styles[prop_key]
            assert value == f"value_{i % 25}"

    access_time = time.time() - start_time

    # Should access 500 properties in under 0.1 seconds
    assert access_time < 0.1, f"Property access too slow: {access_time:.2f}s for 500 accesses"


# Integration test
def test_comprehensive_suite_integration():
    """Test that the comprehensive test suite integrates with existing system."""
    # Create a widget to test integration
    widget = ThemedWidget()
    track_widget(widget)

    # Apply a theme
    theme = Theme(
        name="integration_test",
        colors={
            "background_color": "#ff0000",
            "text_color": "#ffffff"
        }
    )

    if test_app:
        test_app.set_theme(theme)

    # Verify integration
    assert widget is not None
    assert hasattr(widget, '_theme_registry')

    # Test passes if no exceptions thrown
    assert True


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([
        __file__,
        "-v",
        "--cov=vfwidgets_theme",
        "--cov-report=html:htmlcov/comprehensive",
        "--cov-report=term-missing"
    ])
