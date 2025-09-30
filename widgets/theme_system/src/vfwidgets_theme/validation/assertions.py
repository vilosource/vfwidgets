#!/usr/bin/env python3
"""
VFWidgets Theme System - Runtime Assertions
Task 24: Runtime assertion system for theme validation

This module provides runtime assertion capabilities for validating
system state and invariants during theme operations.
"""

import functools
import threading
import time
import traceback
from typing import Any, Callable, Dict, List, Optional, Union
from contextlib import contextmanager
from .framework import ValidationFramework, ValidationMode, ValidationError, ValidationResult, ValidationType


class AssertionError(Exception):
    """Custom assertion error with context."""

    def __init__(self, message: str, context: Dict[str, Any] = None):
        super().__init__(message)
        self.context = context or {}
        self.stack_trace = traceback.format_stack()[:-1]  # Exclude current frame


class RuntimeAssertion:
    """Runtime assertion with context tracking."""

    def __init__(self, name: str, assertion_func: Callable[[Any], bool],
                 message: str = "", context: Dict[str, Any] = None):
        self.name = name
        self.assertion_func = assertion_func
        self.message = message or f"Assertion '{name}' failed"
        self.context = context or {}
        self.enabled = True
        self.call_count = 0
        self.failure_count = 0

    def check(self, obj: Any, raise_on_failure: bool = True) -> bool:
        """
        Check the assertion against an object.

        Args:
            obj: Object to validate
            raise_on_failure: Whether to raise exception on failure

        Returns:
            bool: True if assertion passes, False otherwise
        """
        self.call_count += 1

        if not self.enabled:
            return True

        try:
            result = self.assertion_func(obj)
            if not result:
                self.failure_count += 1
                if raise_on_failure:
                    raise AssertionError(self.message, self.context)
                return False
            return True
        except Exception as e:
            self.failure_count += 1
            if raise_on_failure:
                raise AssertionError(f"{self.message}: {e}", self.context)
            return False

    def reset_stats(self):
        """Reset assertion statistics."""
        self.call_count = 0
        self.failure_count = 0

    def get_stats(self) -> Dict[str, Any]:
        """Get assertion statistics."""
        return {
            'name': self.name,
            'call_count': self.call_count,
            'failure_count': self.failure_count,
            'success_rate': (self.call_count - self.failure_count) / max(1, self.call_count),
            'enabled': self.enabled
        }


class AssertionContext:
    """Context manager for grouped assertions."""

    def __init__(self, name: str, framework: ValidationFramework = None):
        self.name = name
        self.framework = framework or ValidationFramework.get_instance()
        self.assertions: List[RuntimeAssertion] = []
        self.start_time = None
        self.errors: List[str] = []

    def add_assertion(self, assertion: RuntimeAssertion):
        """Add an assertion to this context."""
        self.assertions.append(assertion)

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration_ms = (time.perf_counter() - self.start_time) * 1000

            # Log context completion
            if self.framework.mode == ValidationMode.DEBUG:
                success_count = len(self.assertions) - len(self.errors)
                print(f"AssertionContext '{self.name}': {success_count}/{len(self.assertions)} passed ({duration_ms:.2f}ms)")

            # In strict mode, re-raise any assertion errors
            if exc_type == AssertionError and self.framework.mode == ValidationMode.STRICT:
                return False  # Re-raise

        return exc_type is None  # Suppress non-assertion exceptions in non-strict mode

    def check_all(self, obj: Any, stop_on_first_failure: bool = False) -> bool:
        """
        Check all assertions in this context.

        Args:
            obj: Object to validate
            stop_on_first_failure: Whether to stop on first failure

        Returns:
            bool: True if all assertions pass
        """
        all_passed = True
        self.errors.clear()

        for assertion in self.assertions:
            try:
                if not assertion.check(obj, raise_on_failure=False):
                    all_passed = False
                    self.errors.append(f"Assertion '{assertion.name}' failed")
                    if stop_on_first_failure:
                        break
            except Exception as e:
                all_passed = False
                self.errors.append(f"Assertion '{assertion.name}' error: {e}")
                if stop_on_first_failure:
                    break

        return all_passed


class AssertionRegistry:
    """Registry for runtime assertions."""

    def __init__(self):
        self._assertions: Dict[str, RuntimeAssertion] = {}
        self._contexts: Dict[str, AssertionContext] = {}
        self._lock = threading.RLock()

    def register(self, assertion: RuntimeAssertion):
        """Register an assertion."""
        with self._lock:
            self._assertions[assertion.name] = assertion

    def unregister(self, name: str):
        """Unregister an assertion."""
        with self._lock:
            self._assertions.pop(name, None)

    def get(self, name: str) -> Optional[RuntimeAssertion]:
        """Get an assertion by name."""
        return self._assertions.get(name)

    def get_all(self) -> Dict[str, RuntimeAssertion]:
        """Get all registered assertions."""
        with self._lock:
            return self._assertions.copy()

    def enable_assertion(self, name: str):
        """Enable an assertion."""
        assertion = self.get(name)
        if assertion:
            assertion.enabled = True

    def disable_assertion(self, name: str):
        """Disable an assertion."""
        assertion = self.get(name)
        if assertion:
            assertion.enabled = False

    def reset_all_stats(self):
        """Reset statistics for all assertions."""
        with self._lock:
            for assertion in self._assertions.values():
                assertion.reset_stats()

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all assertions."""
        with self._lock:
            return {name: assertion.get_stats() for name, assertion in self._assertions.items()}

    def create_context(self, name: str) -> AssertionContext:
        """Create an assertion context."""
        context = AssertionContext(name)
        self._contexts[name] = context
        return context

    def get_context(self, name: str) -> Optional[AssertionContext]:
        """Get an assertion context by name."""
        return self._contexts.get(name)


# Global assertion registry
_assertion_registry = AssertionRegistry()


def register_assertion(name: str, assertion_func: Callable[[Any], bool],
                      message: str = "", context: Dict[str, Any] = None) -> RuntimeAssertion:
    """
    Register a runtime assertion.

    Args:
        name: Unique name for the assertion
        assertion_func: Function that returns True if assertion passes
        message: Error message for failures
        context: Additional context information

    Returns:
        RuntimeAssertion: The registered assertion
    """
    assertion = RuntimeAssertion(name, assertion_func, message, context)
    _assertion_registry.register(assertion)
    return assertion


def assert_runtime(name: str, obj: Any) -> bool:
    """
    Check a registered runtime assertion.

    Args:
        name: Name of the assertion to check
        obj: Object to validate

    Returns:
        bool: True if assertion passes

    Raises:
        AssertionError: If assertion fails in strict mode
    """
    assertion = _assertion_registry.get(name)
    if assertion:
        return assertion.check(obj)
    return True


@contextmanager
def assertion_context(name: str):
    """Create a context for grouped assertions."""
    context = _assertion_registry.create_context(name)
    with context:
        yield context


def assertion_decorator(assertion_name: str):
    """
    Decorator to check assertions before/after function execution.

    Args:
        assertion_name: Name of the assertion to check
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            framework = ValidationFramework.get_instance()

            if not framework.is_validation_enabled(ValidationType.RUNTIME):
                return func(*args, **kwargs)

            # Check pre-condition assertion on first argument (usually self)
            if args:
                assert_runtime(f"{assertion_name}_pre", args[0])

            result = func(*args, **kwargs)

            # Check post-condition assertion
            if args:
                assert_runtime(f"{assertion_name}_post", args[0])

            return result

        return wrapper
    return decorator


# Predefined theme system assertions
def _theme_has_required_structure(theme: Any) -> bool:
    """Assert theme has required structure."""
    return (hasattr(theme, 'name') and
            hasattr(theme, 'colors') and
            hasattr(theme, 'styles') and
            isinstance(theme.colors, dict) and
            isinstance(theme.styles, dict))


def _theme_has_valid_colors(theme: Any) -> bool:
    """Assert theme has valid color values."""
    if not hasattr(theme, 'colors') or not isinstance(theme.colors, dict):
        return False

    framework = ValidationFramework.get_instance()
    for color_name, color_value in theme.colors.items():
        if not isinstance(color_name, str):
            return False
        if not framework._is_valid_color(color_value):
            return False
    return True


def _widget_is_themeable(widget: Any) -> bool:
    """Assert widget is themeable."""
    required_methods = ['apply_theme']
    return all(hasattr(widget, method) and callable(getattr(widget, method))
               for method in required_methods)


def _widget_has_current_theme(widget: Any) -> bool:
    """Assert widget has a current theme set."""
    if not hasattr(widget, 'get_current_theme'):
        return False
    current_theme = widget.get_current_theme()
    return current_theme is not None


def _application_has_theme_manager(app: Any) -> bool:
    """Assert application has theme management capabilities."""
    required_attrs = ['set_theme', 'get_current_theme']
    return all(hasattr(app, attr) for attr in required_attrs)


# Theme system assertion groups
def theme_assertions() -> List[RuntimeAssertion]:
    """Get theme-related assertions."""
    return [
        RuntimeAssertion(
            "theme_structure",
            _theme_has_required_structure,
            "Theme must have name, colors, and styles attributes"
        ),
        RuntimeAssertion(
            "theme_valid_colors",
            _theme_has_valid_colors,
            "Theme colors must be valid color values"
        )
    ]


def widget_assertions() -> List[RuntimeAssertion]:
    """Get widget-related assertions."""
    return [
        RuntimeAssertion(
            "widget_themeable",
            _widget_is_themeable,
            "Widget must be themeable (have apply_theme method)"
        ),
        RuntimeAssertion(
            "widget_has_theme",
            _widget_has_current_theme,
            "Widget must have a current theme"
        )
    ]


def performance_assertions() -> List[RuntimeAssertion]:
    """Get performance-related assertions."""
    def _theme_switch_fast_enough(context: Dict[str, Any]) -> bool:
        """Assert theme switch completed within time limit."""
        duration_ms = context.get('duration_ms', 0)
        return duration_ms < 100  # 100ms threshold

    def _memory_usage_reasonable(context: Dict[str, Any]) -> bool:
        """Assert memory usage is within reasonable bounds."""
        memory_mb = context.get('memory_mb', 0)
        return memory_mb < 10  # 10MB threshold for theme operations

    return [
        RuntimeAssertion(
            "theme_switch_performance",
            _theme_switch_fast_enough,
            "Theme switch must complete within 100ms"
        ),
        RuntimeAssertion(
            "memory_usage",
            _memory_usage_reasonable,
            "Theme operations must use less than 10MB memory"
        )
    ]


# Initialize common assertions
def initialize_theme_assertions():
    """Initialize commonly used theme system assertions."""
    for assertion in theme_assertions():
        _assertion_registry.register(assertion)

    for assertion in widget_assertions():
        _assertion_registry.register(assertion)

    for assertion in performance_assertions():
        _assertion_registry.register(assertion)


# Performance monitoring with assertions
def monitor_theme_operation(operation_name: str):
    """Decorator to monitor theme operations with assertions."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            framework = ValidationFramework.get_instance()

            if not framework.is_validation_enabled(ValidationType.RUNTIME):
                return func(*args, **kwargs)

            start_time = time.perf_counter()
            start_memory = _get_memory_usage()

            result = func(*args, **kwargs)

            end_time = time.perf_counter()
            end_memory = _get_memory_usage()

            # Create performance context for assertions
            perf_context = {
                'operation': operation_name,
                'duration_ms': (end_time - start_time) * 1000,
                'memory_mb': max(0, end_memory - start_memory)
            }

            # Check performance assertions
            for assertion in performance_assertions():
                assertion.check(perf_context, raise_on_failure=False)

            return result

        return wrapper
    return decorator


def _get_memory_usage() -> float:
    """Get current memory usage in MB."""
    try:
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    except ImportError:
        return 0.0


# Utility functions
def get_assertion_registry() -> AssertionRegistry:
    """Get the global assertion registry."""
    return _assertion_registry


def reset_all_assertions():
    """Reset all assertion statistics."""
    _assertion_registry.reset_all_stats()


def get_assertion_stats() -> Dict[str, Dict[str, Any]]:
    """Get statistics for all assertions."""
    return _assertion_registry.get_all_stats()


def enable_assertion(name: str):
    """Enable a specific assertion."""
    _assertion_registry.enable_assertion(name)


def disable_assertion(name: str):
    """Disable a specific assertion."""
    _assertion_registry.disable_assertion(name)


# Initialize assertions when module is imported
initialize_theme_assertions()