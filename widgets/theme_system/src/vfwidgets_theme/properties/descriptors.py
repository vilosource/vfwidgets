"""Robust Property Descriptors with Type Safety and Validation

This module implements Task 11: type-safe property descriptors with validation,
caching, and inheritance support. These descriptors integrate seamlessly with
the existing ThemedWidget system while providing enhanced safety and performance.

Key Features:
- Runtime type validation
- Flexible validation rules (min/max, regex, enum, custom)
- Computed properties with caching
- Property inheritance chain resolution
- Debugging and performance monitoring
- Integration with Qt signals/slots
"""

import re
import threading
import time
from dataclasses import dataclass, field
from functools import wraps
from re import Pattern
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Type,
    Union,
    get_args,
    get_origin,
)

if TYPE_CHECKING:
    from ..widgets.base import ThemedWidget

# Import Qt for signal support
try:
    from PySide6.QtCore import QObject, Signal

    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False

    class QObject:
        pass

    class Signal:
        def __init__(self, *args):
            self._callbacks = []

        def emit(self, *args):
            for callback in self._callbacks:
                try:
                    callback(*args)
                except Exception:
                    pass

        def connect(self, callback):
            self._callbacks.append(callback)

        def disconnect(self, callback=None):
            if callback is None:
                self._callbacks.clear()
            elif callback in self._callbacks:
                self._callbacks.remove(callback)


from ..errors import ThemeError
from ..logging import get_debug_logger

logger = get_debug_logger(__name__)


class ValidationError(ThemeError):
    """Raised when property validation fails."""

    pass


@dataclass
class ValidationRule:
    """Base class for property validation rules."""

    name: str = "validation_rule"
    error_message: str = "Validation failed"

    def validate(self, value: Any) -> bool:
        """Validate a value. Override in subclasses."""
        raise NotImplementedError


@dataclass
class MinMaxRule(ValidationRule):
    """Validation rule for numeric min/max values."""

    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None

    def __post_init__(self):
        if self.name == "validation_rule":  # Default wasn't overridden
            self.name = "min_max"
            parts = []
            if self.min_value is not None:
                parts.append(f"min={self.min_value}")
            if self.max_value is not None:
                parts.append(f"max={self.max_value}")
            self.error_message = f"Value must satisfy: {', '.join(parts)}"

    def validate(self, value: Any) -> bool:
        """Validate numeric min/max constraints."""
        try:
            num_value = float(value)
            if self.min_value is not None and num_value < self.min_value:
                return False
            if self.max_value is not None and num_value > self.max_value:
                return False
            return True
        except (ValueError, TypeError):
            return False


@dataclass
class RegexRule(ValidationRule):
    """Validation rule using regular expressions."""

    pattern: Union[str, Pattern] = r".*"

    def __post_init__(self):
        if isinstance(self.pattern, str):
            self.pattern = re.compile(self.pattern)
        if self.name == "validation_rule":  # Default wasn't overridden
            self.name = "regex"
            self.error_message = f"Value must match pattern: {self.pattern.pattern}"

    def validate(self, value: Any) -> bool:
        """Validate using regex pattern."""
        try:
            return bool(self.pattern.match(str(value)))
        except Exception:
            return False


@dataclass
class EnumRule(ValidationRule):
    """Validation rule for enumerated values."""

    allowed_values: List[Any] = field(default_factory=list)

    def __post_init__(self):
        if self.name == "validation_rule":  # Default wasn't overridden
            self.name = "enum"
            self.error_message = f"Value must be one of: {', '.join(map(str, self.allowed_values))}"

    def validate(self, value: Any) -> bool:
        """Validate against allowed values."""
        return value in self.allowed_values


@dataclass
class CallableRule(ValidationRule):
    """Validation rule using a custom callable."""

    validator_func: Optional[Callable[[Any], bool]] = None

    def validate(self, value: Any) -> bool:
        """Validate using custom function."""
        if self.validator_func is None:
            return True
        try:
            return self.validator_func(value)
        except Exception:
            return False


class PropertyCache:
    """High-performance cache for property values with memory management."""

    def __init__(self, max_size: int = 1000):
        self._cache: Dict[str, Any] = {}
        self._access_times: Dict[str, float] = {}
        self._access_counts: Dict[str, int] = {}
        self._max_size = max_size
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Any:
        """Get cached value."""
        with self._lock:
            if key in self._cache:
                self._hits += 1
                self._access_times[key] = time.time()
                self._access_counts[key] = self._access_counts.get(key, 0) + 1
                return self._cache[key]

            self._misses += 1
            return None

    def set(self, key: str, value: Any) -> None:
        """Set cached value with automatic cleanup."""
        with self._lock:
            # Clean up if at capacity
            if len(self._cache) >= self._max_size and key not in self._cache:
                self._evict_least_recently_used()

            self._cache[key] = value
            self._access_times[key] = time.time()
            self._access_counts[key] = self._access_counts.get(key, 0) + 1

    def invalidate(self, key: str) -> bool:
        """Remove specific key from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._access_times.pop(key, None)
                self._access_counts.pop(key, None)
                return True
            return False

    def clear(self) -> None:
        """Clear all cached values."""
        with self._lock:
            self._cache.clear()
            self._access_times.clear()
            self._access_counts.clear()

    def _evict_least_recently_used(self) -> None:
        """Remove least recently used items (internal)."""
        if not self._access_times:
            return

        # Find oldest access time
        oldest_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])

        # Remove it
        self._cache.pop(oldest_key, None)
        self._access_times.pop(oldest_key, None)
        self._access_counts.pop(oldest_key, None)

    @property
    def hit_rate(self) -> float:
        """Get cache hit rate."""
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0

    @property
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            return {
                "size": len(self._cache),
                "max_size": self._max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": self.hit_rate,
            }


class ComputedProperty:
    """Represents a computed property with dependency tracking and caching."""

    def __init__(
        self, compute_func: Callable, dependencies: List[str] = None, cache_enabled: bool = True
    ):
        self.compute_func = compute_func
        self.dependencies = dependencies or []
        self.cache_enabled = cache_enabled
        self._cached_value = None
        self._cache_valid = False
        self._lock = threading.RLock()

    def compute(self, obj: "ThemedWidget") -> Any:
        """Compute the property value."""
        with self._lock:
            if self.cache_enabled and self._cache_valid:
                return self._cached_value

            try:
                value = self.compute_func(obj)
                if self.cache_enabled:
                    self._cached_value = value
                    self._cache_valid = True
                return value
            except Exception as e:
                logger.error(f"Error computing property: {e}")
                return None

    def invalidate_cache(self):
        """Invalidate cached computed value."""
        with self._lock:
            self._cache_valid = False
            self._cached_value = None


class PropertyDescriptor:
    """Type-safe property descriptor with validation and caching.

    This is the core component of Task 11, providing:
    - Runtime type checking
    - Flexible validation rules
    - Property inheritance chains
    - Caching for performance
    - Integration with ThemedWidget
    - Debugging capabilities
    """

    # Class-level cache shared across all descriptors
    _global_cache = PropertyCache(max_size=10000)

    def __init__(
        self,
        name: str,
        type_hint: Type,
        *,
        validator: Optional[Union[ValidationRule, Callable, List[ValidationRule]]] = None,
        default: Any = None,
        computed: Optional[ComputedProperty] = None,
        cache_enabled: bool = True,
        inherit_from: Optional[str] = None,
        debug: bool = False,
    ):
        """Initialize property descriptor.

        Args:
            name: Property name/path
            type_hint: Expected type for runtime checking
            validator: Validation rule(s) or callable
            default: Default value if not found
            computed: Computed property definition
            cache_enabled: Whether to cache values
            inherit_from: Parent property to inherit from
            debug: Enable debug logging for this property

        """
        self.name = name
        self.type_hint = type_hint
        self.default = default
        self.computed = computed
        self.cache_enabled = cache_enabled
        self.inherit_from = inherit_from
        self.debug = debug

        # Process validators
        self.validators = self._process_validators(validator)

        # Performance tracking
        self._access_count = 0
        self._validation_failures = 0
        self._last_access_time = 0.0
        self._lock = threading.RLock()

        # Descriptor metadata
        self.owner_class = None
        self.attribute_name = None

        if self.debug:
            logger.debug(f"PropertyDescriptor created: {name} -> {type_hint}")

    def __set_name__(self, owner, name):
        """Called when descriptor is assigned to class attribute."""
        self.owner_class = owner
        self.attribute_name = name

        if self.debug:
            logger.debug(f"PropertyDescriptor bound: {owner.__name__}.{name}")

    def __get__(self, obj: Optional["ThemedWidget"], objtype: Type = None):
        """Get property value with type checking and caching."""
        # Return descriptor itself when accessed from class
        if obj is None:
            return self

        with self._lock:
            self._access_count += 1
            self._last_access_time = time.time()

        try:
            # Generate cache key
            cache_key = f"{id(obj)}.{self.name}" if self.cache_enabled else None

            # Check cache first
            if cache_key:
                cached_value = self._global_cache.get(cache_key)
                if cached_value is not None:
                    if self.debug:
                        logger.debug(f"Cache hit for {self.name}: {cached_value}")
                    return self._ensure_type(cached_value)

            # Compute or resolve value
            if self.computed:
                value = self.computed.compute(obj)
            else:
                value = self._resolve_value(obj)

            # Validate the value
            if value is not None:
                try:
                    validated_value = self._validate_and_convert(value)
                except ValidationError as e:
                    with self._lock:
                        self._validation_failures += 1

                    if self.debug:
                        logger.warning(f"Validation failed for {self.name}: {e}")

                    # Use default on validation failure
                    validated_value = self.default
            else:
                validated_value = self.default

            # Cache the result
            if cache_key and validated_value is not None:
                self._global_cache.set(cache_key, validated_value)

            if self.debug:
                logger.debug(f"Property {self.name} resolved to: {validated_value}")

            return validated_value

        except Exception as e:
            logger.error(f"Error getting property {self.name}: {e}")
            with self._lock:
                self._validation_failures += 1
            return self.default

    def __set__(self, obj: "ThemedWidget", value: Any):
        """Set property value with validation and cache invalidation."""
        # Get current value for event notification
        old_value = None
        try:
            if self.cache_enabled:
                cache_key = f"{id(obj)}.{self.name}"
                old_value = self._global_cache.get(cache_key)
            if old_value is None:
                old_value = self.default
        except Exception:
            old_value = self.default

        try:
            # Get widget_id for event system
            widget_id = getattr(obj, "_widget_id", f"widget_{id(obj)}")

            # Notify event system that property is changing
            self._notify_property_changing(widget_id, old_value, value)

            # Validate the new value
            validated_value = self._validate_and_convert(value)

            # Store the value (for now, just in cache)
            # In a full implementation, this would update the theme
            if self.cache_enabled:
                cache_key = f"{id(obj)}.{self.name}"
                self._global_cache.set(cache_key, validated_value)

            # Notify event system that property has changed
            self._notify_property_changed(widget_id, old_value, validated_value)

            # Notify widget of property change if it supports it
            if hasattr(obj, "_on_property_changed"):
                obj._on_property_changed(self.name, validated_value)

            if self.debug:
                logger.debug(f"Property {self.name} set to: {validated_value}")

        except ValidationError as e:
            with self._lock:
                self._validation_failures += 1

            # Notify event system of validation failure
            widget_id = getattr(obj, "_widget_id", f"widget_{id(obj)}")
            self._notify_validation_failed(widget_id, value, str(e))

            logger.error(f"Cannot set {self.name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error setting property {self.name}: {e}")
            raise

    def _process_validators(self, validator) -> List[ValidationRule]:
        """Process various validator formats into ValidationRule objects."""
        if validator is None:
            return []

        validators = []

        # Handle single validator
        if not isinstance(validator, list):
            validator = [validator]

        for v in validator:
            if isinstance(v, ValidationRule):
                validators.append(v)
            elif callable(v):
                validators.append(CallableRule(name="custom", validator_func=v))
            else:
                logger.warning(f"Unknown validator type: {type(v)}")

        return validators

    def _resolve_value(self, obj: "ThemedWidget") -> Any:
        """Resolve property value from theme system or inheritance."""
        # Try to get from current theme
        if hasattr(obj, "_get_theme_property"):
            value = obj._get_theme_property(self.name)
            if value is not None:
                return value

        # Try inheritance if specified
        if self.inherit_from:
            if hasattr(obj, "_get_theme_property"):
                inherited_value = obj._get_theme_property(self.inherit_from)
                if inherited_value is not None:
                    return inherited_value

        # Return default
        return self.default

    def _validate_and_convert(self, value: Any) -> Any:
        """Validate value and convert to correct type."""
        if value is None:
            return value

        # Type checking
        if not self._check_type(value):
            # Try to convert
            try:
                value = self._convert_type(value)
            except Exception as e:
                raise ValidationError(
                    f"Type validation failed for {self.name}: "
                    f"expected {self.type_hint}, got {type(value).__name__}"
                ) from e

        # Run validation rules
        for validator in self.validators:
            if not validator.validate(value):
                raise ValidationError(
                    f"Validation failed for {self.name}: {validator.error_message}"
                )

        return value

    def _check_type(self, value: Any) -> bool:
        """Check if value matches expected type."""
        try:
            # Handle generic types (Union, Optional, etc.)
            origin = get_origin(self.type_hint)
            if origin is not None:
                # Handle Union types (including Optional)
                if origin is Union:
                    type_args = get_args(self.type_hint)
                    return any(isinstance(value, arg) for arg in type_args if arg != type(None))
                # Add other generic type handling as needed

            # Handle regular types
            return isinstance(value, self.type_hint)

        except Exception:
            # Fallback for complex type hints
            return True

    def _convert_type(self, value: Any) -> Any:
        """Attempt to convert value to expected type."""
        if self.type_hint == str:
            return str(value)
        elif self.type_hint == int:
            return int(float(value))  # Handle string numbers
        elif self.type_hint == float:
            return float(value)
        elif self.type_hint == bool:
            if isinstance(value, str):
                return value.lower() in ("true", "1", "yes", "on")
            return bool(value)
        else:
            # Try direct conversion
            return self.type_hint(value)

    def _ensure_type(self, value: Any) -> Any:
        """Ensure cached value is still the correct type."""
        if not self._check_type(value):
            logger.warning(f"Cached value type mismatch for {self.name}")
            return self.default
        return value

    def invalidate_cache(self, obj: Optional["ThemedWidget"] = None):
        """Invalidate cached values."""
        if obj is not None:
            cache_key = f"{id(obj)}.{self.name}"
            self._global_cache.invalidate(cache_key)
        else:
            # Invalidate all cache entries for this property
            # This is expensive but thorough
            keys_to_remove = [
                k for k in self._global_cache._cache.keys() if k.endswith(f".{self.name}")
            ]
            for key in keys_to_remove:
                self._global_cache.invalidate(key)

        # Invalidate computed property cache too
        if self.computed:
            self.computed.invalidate_cache()

    @property
    def statistics(self) -> Dict[str, Any]:
        """Get performance and usage statistics."""
        with self._lock:
            return {
                "name": self.name,
                "type_hint": str(self.type_hint),
                "access_count": self._access_count,
                "validation_failures": self._validation_failures,
                "last_access_time": self._last_access_time,
                "cache_enabled": self.cache_enabled,
                "validators_count": len(self.validators),
                "is_computed": self.computed is not None,
                "inherit_from": self.inherit_from,
            }

    def _notify_property_changing(self, widget_id: str, old_value: Any, new_value: Any):
        """Notify event system that property is about to change."""
        try:
            from ..events.system import get_global_event_system

            event_system = get_global_event_system()
            event_system.notify_property_changing(widget_id, self.name, old_value, new_value)
        except Exception as e:
            # Don't let event system errors break property setting
            if self.debug:
                logger.warning(f"Failed to notify property changing for {self.name}: {e}")

    def _notify_property_changed(self, widget_id: str, old_value: Any, new_value: Any):
        """Notify event system that property has changed."""
        try:
            from ..events.system import get_global_event_system

            event_system = get_global_event_system()
            event_system.notify_property_changed(widget_id, self.name, old_value, new_value)
        except Exception as e:
            # Don't let event system errors break property setting
            if self.debug:
                logger.warning(f"Failed to notify property changed for {self.name}: {e}")

    def _notify_validation_failed(self, widget_id: str, invalid_value: Any, error_message: str):
        """Notify event system that property validation failed."""
        try:
            from ..events.system import get_global_event_system

            event_system = get_global_event_system()
            event_system.notify_property_validation_failed(
                widget_id, self.name, invalid_value, error_message
            )
        except Exception as e:
            # Don't let event system errors break validation failure reporting
            if self.debug:
                logger.warning(f"Failed to notify validation failure for {self.name}: {e}")

    @classmethod
    def get_global_cache_stats(cls) -> Dict[str, Any]:
        """Get global cache statistics."""
        return cls._global_cache.stats

    @classmethod
    def clear_global_cache(cls):
        """Clear the global property cache."""
        cls._global_cache.clear()


# Utility functions for common validation rules
def min_max_validator(
    min_val: Optional[Union[int, float]] = None, max_val: Optional[Union[int, float]] = None
) -> MinMaxRule:
    """Create a min/max validation rule."""
    return MinMaxRule(name="min_max", min_value=min_val, max_value=max_val)


def regex_validator(pattern: Union[str, Pattern], error_msg: str = None) -> RegexRule:
    """Create a regex validation rule."""
    rule = RegexRule(name="regex", pattern=pattern)
    if error_msg:
        rule.error_message = error_msg
    return rule


def enum_validator(allowed_values: List[Any], error_msg: str = None) -> EnumRule:
    """Create an enum validation rule."""
    rule = EnumRule(name="enum", allowed_values=allowed_values)
    if error_msg:
        rule.error_message = error_msg
    return rule


def color_validator() -> RegexRule:
    """Create a validator for CSS color values."""
    color_pattern = r"^(#[0-9a-fA-F]{3,6}|rgb\(\d+,\s*\d+,\s*\d+\)|rgba\(\d+,\s*\d+,\s*\d+,\s*[\d.]+\)|[a-zA-Z]+)$"
    return regex_validator(color_pattern, "Must be a valid CSS color")


def computed_property(dependencies: List[str] = None, cache: bool = True):
    """Decorator for creating computed properties."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        wrapper._computed_property = ComputedProperty(
            compute_func=func, dependencies=dependencies or [], cache_enabled=cache
        )
        return wrapper

    return decorator


__all__ = [
    "PropertyDescriptor",
    "ValidationError",
    "ValidationRule",
    "MinMaxRule",
    "RegexRule",
    "EnumRule",
    "CallableRule",
    "PropertyCache",
    "ComputedProperty",
    "min_max_validator",
    "regex_validator",
    "enum_validator",
    "color_validator",
    "computed_property",
]
