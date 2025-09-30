"""
Testing infrastructure for VFWidgets Theme System.

This module provides comprehensive testing utilities including mock objects,
test fixtures, performance benchmarking, and memory profiling tools.

Key Components:
- Mock objects implementing all core protocols for isolated testing
- Performance benchmarking framework with strict validation
- Memory profiling utilities for leak detection
- ThemedTestCase base class for theme-aware unit tests
- Test fixtures for common theme scenarios

All testing components follow the same philosophy as the theme system:
"ThemedWidget is THE way" - make testing as simple as inheriting from ThemedTestCase.
"""

from .mocks import (
    MockThemeProvider,
    MockThemeableWidget,
    MockColorProvider,
    MockStyleGenerator,
    MockWidget,
    MockApplication,
    MockPainter,
)

from .utils import (
    ThemedTestCase,
    assert_theme_property,
    assert_performance_requirement,
    generate_test_theme,
    create_test_widget,
)

from .benchmarks import (
    ThemeBenchmark,
    benchmark_theme_switch,
    benchmark_property_access,
    benchmark_memory_usage,
    validate_performance_requirements,
    performance_test,
    memory_test,
)

from .memory import (
    MemoryProfiler,
    detect_memory_leaks,
    track_widget_lifecycle,
    validate_memory_requirements,
    memory_leak_test,
)

__all__ = [
    # Mock Objects
    "MockThemeProvider",
    "MockThemeableWidget",
    "MockColorProvider",
    "MockStyleGenerator",
    "MockWidget",
    "MockApplication",
    "MockPainter",

    # Testing Utilities
    "ThemedTestCase",
    "assert_theme_property",
    "assert_performance_requirement",
    "generate_test_theme",
    "create_test_widget",

    # Performance Benchmarking
    "ThemeBenchmark",
    "benchmark_theme_switch",
    "benchmark_property_access",
    "benchmark_memory_usage",
    "validate_performance_requirements",
    "performance_test",
    "memory_test",

    # Memory Profiling
    "MemoryProfiler",
    "detect_memory_leaks",
    "track_widget_lifecycle",
    "validate_memory_requirements",
    "memory_leak_test",
]