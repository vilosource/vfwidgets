#!/usr/bin/env python3
"""VFWidgets Theme System - Validation Decorators
Task 24: Validation decorators for easy integration

This module provides decorators that integrate validation seamlessly
into the theme system components.
"""

import functools
import time
from typing import Any, Callable, Dict, Optional, Type

from .framework import ValidationFramework, ValidationMode, ValidationType


def validation_decorator(validation_type: ValidationType,
                        enabled_modes: Optional[set] = None):
    """Base validation decorator factory.

    Args:
        validation_type: Type of validation to perform
        enabled_modes: Validation modes where this decorator is active

    """
    if enabled_modes is None:
        enabled_modes = {ValidationMode.DEBUG, ValidationMode.STRICT}

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            framework = ValidationFramework.get_instance()

            # Skip validation if not in enabled modes
            if framework.mode not in enabled_modes:
                return func(*args, **kwargs)

            # Execute function with validation context
            with framework.validation_context(validation_type,
                                            {'function': func.__name__}) as result:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    result.add_error(f"Function execution failed: {e}")
                    raise

        return wrapper
    return decorator


def validate_theme(func: Callable = None, *,
                   strict: bool = False,
                   theme_arg: str = 'theme'):
    """Decorator to validate theme objects passed to functions.

    Args:
        strict: If True, validation runs in all modes
        theme_arg: Name of the theme argument to validate

    """
    enabled_modes = {ValidationMode.DEBUG, ValidationMode.STRICT}
    if strict:
        enabled_modes.add(ValidationMode.PRODUCTION)

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            framework = ValidationFramework.get_instance()

            if framework.mode not in enabled_modes:
                return func(*args, **kwargs)

            # Find theme argument
            theme = None
            if theme_arg in kwargs:
                theme = kwargs[theme_arg]
            else:
                # Try to find theme in positional arguments
                import inspect
                sig = inspect.signature(func)
                param_names = list(sig.parameters.keys())
                if theme_arg in param_names:
                    theme_index = param_names.index(theme_arg)
                    if theme_index < len(args):
                        theme = args[theme_index]

            # Validate theme if found
            if theme is not None:
                validation_result = framework.validate_theme_structure(theme)
                if validation_result.has_errors:
                    error_msg = f"Theme validation failed in {func.__name__}: {validation_result.errors}"
                    if framework.mode == ValidationMode.STRICT:
                        raise ValueError(error_msg)
                    else:
                        import logging
                        logging.warning(error_msg)

            return func(*args, **kwargs)

        return wrapper

    if func is None:
        return decorator
    else:
        return decorator(func)


def validate_contract(protocol: Type):
    """Decorator to validate that objects implement required protocols.

    Args:
        protocol: Protocol/interface that objects should implement

    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            framework = ValidationFramework.get_instance()

            if not framework.is_validation_enabled(ValidationType.CONTRACT):
                return func(*args, **kwargs)

            # Validate all arguments against the protocol
            for i, arg in enumerate(args[1:], 1):  # Skip 'self' if present
                if hasattr(arg, '__class__') and not isinstance(arg, (str, int, float, bool, type(None))):
                    validation_result = framework.validate_contract_implementation(arg, protocol)
                    if validation_result.has_errors:
                        error_msg = f"Contract validation failed for arg {i} in {func.__name__}: {validation_result.errors}"
                        if framework.mode == ValidationMode.STRICT:
                            raise TypeError(error_msg)

            return func(*args, **kwargs)

        return wrapper
    return decorator


def require_valid_color(color_arg: str = 'color'):
    """Decorator to validate color values.

    Args:
        color_arg: Name of the color argument to validate

    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            framework = ValidationFramework.get_instance()

            if not framework.is_validation_enabled(ValidationType.SCHEMA):
                return func(*args, **kwargs)

            # Find color argument
            color = None
            if color_arg in kwargs:
                color = kwargs[color_arg]
            else:
                # Try to find color in positional arguments
                import inspect
                sig = inspect.signature(func)
                param_names = list(sig.parameters.keys())
                if color_arg in param_names:
                    color_index = param_names.index(color_arg)
                    if color_index < len(args):
                        color = args[color_index]

            # Validate color if found
            if color is not None:
                if not framework._is_valid_color(color):
                    error_msg = f"Invalid color value '{color}' in {func.__name__}"
                    if framework.mode == ValidationMode.STRICT:
                        raise ValueError(error_msg)
                    else:
                        import logging
                        logging.warning(error_msg)

            return func(*args, **kwargs)

        return wrapper
    return decorator


def require_theme_structure(required_attrs: Optional[set] = None):
    """Decorator to validate theme has required structure.

    Args:
        required_attrs: Set of required attribute names

    """
    if required_attrs is None:
        required_attrs = {'name', 'colors', 'styles'}

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            framework = ValidationFramework.get_instance()

            if not framework.is_validation_enabled(ValidationType.SCHEMA):
                return func(*args, **kwargs)

            # Find theme in arguments
            theme = None
            if 'theme' in kwargs:
                theme = kwargs['theme']
            elif len(args) > 1:  # Assume theme is second argument after self
                theme = args[1]

            # Validate theme structure
            if theme is not None:
                missing_attrs = []
                for attr in required_attrs:
                    if not hasattr(theme, attr):
                        missing_attrs.append(attr)

                if missing_attrs:
                    error_msg = f"Theme missing required attributes {missing_attrs} in {func.__name__}"
                    if framework.mode == ValidationMode.STRICT:
                        raise AttributeError(error_msg)
                    else:
                        import logging
                        logging.warning(error_msg)

            return func(*args, **kwargs)

        return wrapper
    return decorator


def require_widget_state(expected_state: Dict[str, Any]):
    """Decorator to validate widget runtime state.

    Args:
        expected_state: Dictionary of expected state values

    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            framework = ValidationFramework.get_instance()

            if not framework.is_validation_enabled(ValidationType.RUNTIME):
                return func(*args, **kwargs)

            # Find widget/object in arguments (usually first argument or self)
            obj = None
            if args:
                obj = args[0]

            # Validate state if object found
            if obj is not None:
                validation_result = framework.validate_runtime_state(obj, expected_state)
                if validation_result.has_errors:
                    error_msg = f"Widget state validation failed in {func.__name__}: {validation_result.errors}"
                    if framework.mode == ValidationMode.STRICT:
                        raise RuntimeError(error_msg)

            return func(*args, **kwargs)

        return wrapper
    return decorator


def performance_monitor(operation_name: Optional[str] = None,
                       threshold_ms: Optional[float] = None):
    """Decorator to monitor function performance and validate against thresholds.

    Args:
        operation_name: Name for the operation (defaults to function name)
        threshold_ms: Performance threshold in milliseconds

    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            framework = ValidationFramework.get_instance()

            if not framework.is_validation_enabled(ValidationType.PERFORMANCE):
                return func(*args, **kwargs)

            op_name = operation_name or func.__name__

            # Set threshold if provided
            if threshold_ms is not None:
                framework.set_performance_threshold(op_name, threshold_ms / 1000)

            # Monitor execution time
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_time = time.perf_counter()
                duration_ms = (end_time - start_time) * 1000

                # Validate performance
                validation_result = framework.validate_performance_constraints(op_name, duration_ms)
                if validation_result.has_errors:
                    error_msg = f"Performance validation failed: {validation_result.errors}"
                    if framework.mode == ValidationMode.STRICT:
                        raise PerformanceError(error_msg)
                    else:
                        import logging
                        logging.warning(error_msg)

        return wrapper
    return decorator


def validate_return_type(expected_type: Type):
    """Decorator to validate function return type.

    Args:
        expected_type: Expected return type

    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            framework = ValidationFramework.get_instance()
            if framework.mode == ValidationMode.DEBUG or framework.mode == ValidationMode.STRICT:
                if not isinstance(result, expected_type):
                    error_msg = f"Return type validation failed in {func.__name__}: "
                    error_msg += f"expected {expected_type}, got {type(result)}"
                    if framework.mode == ValidationMode.STRICT:
                        raise TypeError(error_msg)
                    else:
                        import logging
                        logging.warning(error_msg)

            return result

        return wrapper
    return decorator


def validate_arguments(**type_hints):
    """Decorator to validate function argument types.

    Args:
        **type_hints: Mapping of argument names to expected types

    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            framework = ValidationFramework.get_instance()

            if framework.mode not in (ValidationMode.DEBUG, ValidationMode.STRICT):
                return func(*args, **kwargs)

            # Get function signature
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Validate argument types
            for arg_name, expected_type in type_hints.items():
                if arg_name in bound_args.arguments:
                    value = bound_args.arguments[arg_name]
                    if value is not None and not isinstance(value, expected_type):
                        error_msg = f"Argument type validation failed in {func.__name__}: "
                        error_msg += f"{arg_name} expected {expected_type}, got {type(value)}"
                        if framework.mode == ValidationMode.STRICT:
                            raise TypeError(error_msg)
                        else:
                            import logging
                            logging.warning(error_msg)

            return func(*args, **kwargs)

        return wrapper
    return decorator


class PerformanceError(Exception):
    """Exception raised for performance validation failures."""

    pass


# Convenience decorators for common use cases
debug_only = functools.partial(validation_decorator,
                              enabled_modes={ValidationMode.DEBUG})

strict_only = functools.partial(validation_decorator,
                               enabled_modes={ValidationMode.STRICT})

production_safe = functools.partial(validation_decorator,
                                   enabled_modes={ValidationMode.DEBUG,
                                                ValidationMode.PRODUCTION,
                                                ValidationMode.STRICT})
