#!/usr/bin/env python3
"""VFWidgets Theme System - Validation Framework Core
Task 24: Core validation framework implementation.

This module implements the central validation framework with configurable
validation modes and comprehensive error handling.
"""

import json
import logging
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class ValidationMode(Enum):
    """Validation operating modes."""

    DEBUG = auto()  # Full validation, detailed logging
    PRODUCTION = auto()  # Essential validation only
    STRICT = auto()  # Maximum validation, fail fast
    DISABLED = auto()  # No validation (for performance)


class ValidationType(Enum):
    """Types of validation."""

    SCHEMA = auto()  # Data structure validation
    CONTRACT = auto()  # Protocol/interface validation
    RUNTIME = auto()  # Runtime state validation
    PERFORMANCE = auto()  # Performance constraint validation


class ValidationError(Exception):
    """Base exception for validation errors."""

    def __init__(
        self, message: str, validation_type: ValidationType = None, context: dict[str, Any] = None
    ):
        super().__init__(message)
        self.validation_type = validation_type
        self.context = context or {}
        self.timestamp = time.time()

    def __str__(self):
        context_str = f" Context: {self.context}" if self.context else ""
        type_str = f"[{self.validation_type.name}] " if self.validation_type else ""
        return f"{type_str}{super().__str__()}{context_str}"


@dataclass
class ValidationResult:
    """Result of a validation operation."""

    passed: bool
    validation_type: ValidationType
    message: str = ""
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0

    @property
    def has_errors(self) -> bool:
        """Check if validation has errors."""
        return not self.passed or bool(self.errors)

    @property
    def has_warnings(self) -> bool:
        """Check if validation has warnings."""
        return bool(self.warnings)

    def add_error(self, error: str):
        """Add an error to the result."""
        self.errors.append(error)
        self.passed = False

    def add_warning(self, warning: str):
        """Add a warning to the result."""
        self.warnings.append(warning)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "passed": self.passed,
            "validation_type": self.validation_type.name,
            "message": self.message,
            "errors": self.errors,
            "warnings": self.warnings,
            "context": self.context,
            "duration_ms": self.duration_ms,
        }


class ValidationContext:
    """Context manager for validation operations."""

    def __init__(
        self,
        framework: "ValidationFramework",
        validation_type: ValidationType,
        context: dict[str, Any] = None,
    ):
        self.framework = framework
        self.validation_type = validation_type
        self.context = context or {}
        self.start_time = None
        self.result = None

    def __enter__(self) -> ValidationResult:
        self.start_time = time.perf_counter()
        self.result = ValidationResult(
            passed=True, validation_type=self.validation_type, context=self.context.copy()
        )
        return self.result

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = (time.perf_counter() - self.start_time) * 1000
            self.result.duration_ms = duration

        if exc_type is not None:
            if isinstance(exc_val, ValidationError):
                self.result.add_error(str(exc_val))
            else:
                self.result.add_error(f"Unexpected error: {exc_val}")

        # Log result if framework is in debug mode
        if self.framework.mode == ValidationMode.DEBUG:
            self._log_result()

    def _log_result(self):
        """Log validation result."""
        level = (
            logging.ERROR
            if self.result.has_errors
            else (logging.WARNING if self.result.has_warnings else logging.DEBUG)
        )
        logger.log(
            level,
            f"Validation {self.validation_type.name}: "
            f"{'PASS' if self.result.passed else 'FAIL'} "
            f"({self.result.duration_ms:.2f}ms)",
        )


class ValidationFramework:
    """Runtime validation framework with configurable strictness.

    Provides comprehensive validation capabilities for the theme system
    with different operating modes for development vs production use.
    """

    _instance: Optional["ValidationFramework"] = None
    _lock = threading.Lock()

    def __new__(cls, mode: ValidationMode = ValidationMode.PRODUCTION):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, mode: ValidationMode = ValidationMode.PRODUCTION):
        if self._initialized:
            return

        self.mode = mode
        self._validators: dict[ValidationType, list[Callable]] = {
            ValidationType.SCHEMA: [],
            ValidationType.CONTRACT: [],
            ValidationType.RUNTIME: [],
            ValidationType.PERFORMANCE: [],
        }

        self._results: list[ValidationResult] = []
        self._performance_thresholds = {
            "property_access": 0.001,  # 1ms
            "theme_switch": 0.1,  # 100ms
            "widget_creation": 0.01,  # 10ms
        }

        self._validation_stats = {
            "total_validations": 0,
            "failed_validations": 0,
            "validation_time_ms": 0.0,
        }

        self._initialized = True
        logger.info(f"ValidationFramework initialized in {mode.name} mode")

    @classmethod
    def get_instance(cls) -> "ValidationFramework":
        """Get singleton instance of validation framework."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """Reset singleton instance (for testing)."""
        with cls._lock:
            cls._instance = None

    def set_mode(self, mode: ValidationMode):
        """Change validation mode."""
        old_mode = self.mode
        self.mode = mode
        logger.info(f"ValidationFramework mode changed from {old_mode.name} to {mode.name}")

    def is_validation_enabled(self, validation_type: ValidationType = None) -> bool:
        """Check if validation is enabled for the current mode."""
        if self.mode == ValidationMode.DISABLED:
            return False

        if validation_type == ValidationType.PERFORMANCE:
            # Performance validation only in DEBUG and STRICT modes
            return self.mode in (ValidationMode.DEBUG, ValidationMode.STRICT)

        # Other validations enabled in all modes except DISABLED
        return True

    def register_validator(self, validation_type: ValidationType, validator: Callable):
        """Register a custom validator function."""
        self._validators[validation_type].append(validator)
        logger.debug(f"Registered {validation_type.name} validator: {validator.__name__}")

    def unregister_validator(self, validation_type: ValidationType, validator: Callable):
        """Unregister a validator function."""
        if validator in self._validators[validation_type]:
            self._validators[validation_type].remove(validator)
            logger.debug(f"Unregistered {validation_type.name} validator: {validator.__name__}")

    @contextmanager
    def validation_context(self, validation_type: ValidationType, context: dict[str, Any] = None):
        """Create a validation context for tracking and logging."""
        if not self.is_validation_enabled(validation_type):
            # Create a no-op result when validation is disabled
            result = ValidationResult(
                passed=True, validation_type=validation_type, message="Validation disabled"
            )
            yield result
            return

        validation_ctx = ValidationContext(self, validation_type, context)
        with validation_ctx as result:
            yield result

        # Store result and update stats
        self._results.append(result)
        self._update_stats(result)

    def _update_stats(self, result: ValidationResult):
        """Update validation statistics."""
        self._validation_stats["total_validations"] += 1
        self._validation_stats["validation_time_ms"] += result.duration_ms

        if result.has_errors:
            self._validation_stats["failed_validations"] += 1

    def validate_theme_structure(self, theme: Any) -> ValidationResult:
        """Validate theme conforms to expected structure."""
        with self.validation_context(
            ValidationType.SCHEMA, {"theme_name": getattr(theme, "name", "unknown")}
        ) as result:
            try:
                # Check basic structure
                if not hasattr(theme, "name"):
                    result.add_error("Theme missing 'name' attribute")

                if not hasattr(theme, "colors"):
                    result.add_error("Theme missing 'colors' attribute")
                elif not isinstance(theme.colors, dict):
                    result.add_error("Theme 'colors' must be a dictionary")

                if not hasattr(theme, "styles"):
                    result.add_error("Theme missing 'styles' attribute")
                elif not isinstance(theme.styles, dict):
                    result.add_error("Theme 'styles' must be a dictionary")

                # Validate colors
                if hasattr(theme, "colors") and isinstance(theme.colors, dict):
                    for color_name, color_value in theme.colors.items():
                        if not isinstance(color_name, str):
                            result.add_error(f"Color name must be string, got {type(color_name)}")
                        if not self._is_valid_color(color_value):
                            result.add_warning(f"Questionable color value: {color_value}")

                # Validate styles
                if hasattr(theme, "styles") and isinstance(theme.styles, dict):
                    for style_name, _style_value in theme.styles.items():
                        if not isinstance(style_name, str):
                            result.add_error(f"Style name must be string, got {type(style_name)}")

                # Run custom validators
                for validator in self._validators[ValidationType.SCHEMA]:
                    try:
                        validator(theme, result)
                    except Exception as e:
                        result.add_error(f"Custom validator failed: {e}")

                if not result.errors:
                    result.message = "Theme structure validation passed"

            except Exception as e:
                result.add_error(f"Theme structure validation failed: {e}")

        return result

    def validate_contract_implementation(self, obj: Any, protocol: type) -> ValidationResult:
        """Validate object implements a protocol/contract."""
        with self.validation_context(
            ValidationType.CONTRACT,
            {"object_type": type(obj).__name__, "protocol": protocol.__name__},
        ) as result:
            try:
                # Basic protocol checking using hasattr
                if hasattr(protocol, "__annotations__"):
                    for attr_name in protocol.__annotations__:
                        if not hasattr(obj, attr_name):
                            result.add_error(f"Missing required attribute: {attr_name}")

                # Check for required methods (basic implementation)
                required_methods = [
                    name
                    for name in dir(protocol)
                    if not name.startswith("_") and callable(getattr(protocol, name, None))
                ]

                for method_name in required_methods:
                    if not hasattr(obj, method_name):
                        result.add_error(f"Missing required method: {method_name}")
                    elif not callable(getattr(obj, method_name)):
                        result.add_error(f"Attribute {method_name} is not callable")

                # Run custom contract validators
                for validator in self._validators[ValidationType.CONTRACT]:
                    try:
                        validator(obj, protocol, result)
                    except Exception as e:
                        result.add_error(f"Custom contract validator failed: {e}")

                if not result.errors:
                    result.message = f"Contract {protocol.__name__} validation passed"

            except Exception as e:
                result.add_error(f"Contract validation failed: {e}")

        return result

    def validate_runtime_state(self, obj: Any, expected_state: dict[str, Any]) -> ValidationResult:
        """Validate object runtime state against expectations."""
        with self.validation_context(
            ValidationType.RUNTIME, {"object_type": type(obj).__name__}
        ) as result:
            try:
                for state_name, expected_value in expected_state.items():
                    if not hasattr(obj, state_name):
                        result.add_error(f"Missing expected state attribute: {state_name}")
                        continue

                    actual_value = getattr(obj, state_name)

                    if callable(expected_value):
                        # Expected value is a validation function
                        if not expected_value(actual_value):
                            result.add_error(f"State validation failed for {state_name}")
                    elif actual_value != expected_value:
                        result.add_warning(
                            f"State mismatch for {state_name}: "
                            f"expected {expected_value}, got {actual_value}"
                        )

                # Run custom runtime validators
                for validator in self._validators[ValidationType.RUNTIME]:
                    try:
                        validator(obj, expected_state, result)
                    except Exception as e:
                        result.add_error(f"Custom runtime validator failed: {e}")

                if not result.errors:
                    result.message = "Runtime state validation passed"

            except Exception as e:
                result.add_error(f"Runtime state validation failed: {e}")

        return result

    def validate_performance_constraints(
        self, operation_name: str, duration_ms: float
    ) -> ValidationResult:
        """Validate operation performance against thresholds."""
        with self.validation_context(
            ValidationType.PERFORMANCE, {"operation": operation_name, "duration_ms": duration_ms}
        ) as result:
            try:
                threshold = self._performance_thresholds.get(operation_name)
                if threshold is None:
                    result.add_warning(
                        f"No performance threshold set for operation: {operation_name}"
                    )
                    return result

                threshold_ms = threshold * 1000  # Convert to milliseconds

                if duration_ms > threshold_ms:
                    result.add_error(
                        f"Performance violation: {operation_name} took {duration_ms:.2f}ms "
                        f"(threshold: {threshold_ms:.2f}ms)"
                    )
                elif duration_ms > threshold_ms * 0.8:  # 80% threshold warning
                    result.add_warning(
                        f"Performance warning: {operation_name} took {duration_ms:.2f}ms "
                        f"(80% of threshold: {threshold_ms:.2f}ms)"
                    )

                # Run custom performance validators
                for validator in self._validators[ValidationType.PERFORMANCE]:
                    try:
                        validator(operation_name, duration_ms, result)
                    except Exception as e:
                        result.add_error(f"Custom performance validator failed: {e}")

                if not result.errors:
                    result.message = f"Performance validation passed for {operation_name}"

            except Exception as e:
                result.add_error(f"Performance validation failed: {e}")

        return result

    def _is_valid_color(self, color_value: Any) -> bool:
        """Basic color validation."""
        if isinstance(color_value, str):
            # Check for hex colors
            if color_value.startswith("#") and len(color_value) in (4, 7, 9):
                try:
                    int(color_value[1:], 16)
                    return True
                except ValueError:
                    pass
            # Check for named colors (basic set)
            named_colors = {"red", "green", "blue", "white", "black", "transparent"}
            return color_value.lower() in named_colors

        return False

    def set_performance_threshold(self, operation_name: str, threshold_seconds: float):
        """Set performance threshold for an operation."""
        self._performance_thresholds[operation_name] = threshold_seconds
        logger.debug(f"Set performance threshold for {operation_name}: {threshold_seconds}s")

    def get_validation_stats(self) -> dict[str, Any]:
        """Get validation statistics."""
        stats = self._validation_stats.copy()
        if stats["total_validations"] > 0:
            stats["success_rate"] = (
                stats["total_validations"] - stats["failed_validations"]
            ) / stats["total_validations"]
            stats["average_validation_time_ms"] = (
                stats["validation_time_ms"] / stats["total_validations"]
            )
        else:
            stats["success_rate"] = 0.0
            stats["average_validation_time_ms"] = 0.0

        return stats

    def get_recent_results(self, limit: int = 100) -> list[ValidationResult]:
        """Get recent validation results."""
        return self._results[-limit:]

    def clear_results(self):
        """Clear stored validation results."""
        self._results.clear()
        self._validation_stats = {
            "total_validations": 0,
            "failed_validations": 0,
            "validation_time_ms": 0.0,
        }
        logger.debug("Cleared validation results and statistics")

    def export_results(self, filepath: Path) -> bool:
        """Export validation results to file."""
        try:
            results_data = {
                "stats": self.get_validation_stats(),
                "results": [result.to_dict() for result in self._results],
                "export_timestamp": time.time(),
            }

            with open(filepath, "w") as f:
                json.dump(results_data, f, indent=2)

            logger.info(f"Exported {len(self._results)} validation results to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to export validation results: {e}")
            return False

    def __repr__(self):
        stats = self.get_validation_stats()
        return (
            f"ValidationFramework(mode={self.mode.name}, "
            f"validations={stats['total_validations']}, "
            f"success_rate={stats['success_rate']:.1%})"
        )
