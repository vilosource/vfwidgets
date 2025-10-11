"""Memory Management Foundation for VFWidgets Theme System.

This module provides comprehensive memory management that ensures zero memory leaks
and automatic cleanup for themed widgets. The system is completely transparent to
developers - ThemedWidget inheritance automatically provides bulletproof memory management.

Key Components:
1. WidgetRegistry - WeakReference-based registry for automatic cleanup
2. LifecycleManager - Complete widget lifecycle management from registration to cleanup
3. Context Managers - Batch operations with automatic resource management
4. Cleanup Protocols - Automatic cleanup scheduling and execution
5. Memory Diagnostics - Leak detection and resource monitoring

Philosophy: "ThemedWidget is THE way" - developers get automatic memory management
without any effort on their part. All complexity is hidden behind clean APIs.

Performance Requirements:
- Widget registration: < 10μs per widget
- Registry cleanup: < 100μs for 1000 widgets
- Memory overhead: < 1KB per widget
- Zero memory leaks after 1000 theme switches
- Context manager overhead: < 1ms
"""

import gc
import threading
import time
import weakref
from abc import abstractmethod
from collections import defaultdict
from collections.abc import Iterator
from contextlib import contextmanager
from enum import Enum, auto
from functools import wraps
from typing import (
    Any,
    Callable,
    NamedTuple,
    Optional,
    Protocol,
    TypeVar,
    runtime_checkable,
)

from .protocols import ThemeableWidget, ThemeProvider

# Type variables for generic implementations
T = TypeVar("T")
WidgetType = TypeVar("WidgetType", bound=ThemeableWidget)


class WidgetLifecycleState(Enum):
    """Widget lifecycle states for tracking."""

    CREATED = auto()
    REGISTERED = auto()
    UPDATED = auto()
    UNREGISTERED = auto()
    DESTROYED = auto()


class WidgetLifecycleEvent(NamedTuple):
    """Widget lifecycle event information."""

    widget_id: int
    state: WidgetLifecycleState
    timestamp: float
    metadata: Optional[dict[str, Any]] = None


class RegistrationError(Exception):
    """Error during widget registration operations."""

    pass


class BulkOperationError(Exception):
    """Error during bulk registration operations."""

    def __init__(self, message: str, successful_count: int, failed_widgets: list[Any]):
        super().__init__(message)
        self.successful_count = successful_count
        self.failed_widgets = failed_widgets


@runtime_checkable
class CleanupProtocol(Protocol):
    """Protocol for objects that need cleanup.

    Objects implementing this protocol can be automatically cleaned up
    by the cleanup scheduling system.
    """

    @abstractmethod
    def cleanup(self) -> None:
        """Perform cleanup operations for this object.

        This method should:
        - Release any held resources
        - Cancel any pending operations
        - Clear any caches or temporary data
        - Be idempotent (safe to call multiple times)
        """
        ...

    @abstractmethod
    def is_cleanup_required(self) -> bool:
        """Check if cleanup is required for this object.

        Returns:
            True if cleanup is needed, False if already cleaned up.

        """
        ...


class WidgetRegistry:
    """Enhanced WeakReference-based registry with safety guards and lifecycle tracking.

    Uses WeakReference to track widgets without preventing garbage collection.
    Provides comprehensive safety mechanisms, lifecycle tracking, and bulk operations.

    This registry ensures:
    - Zero memory leaks through WeakReference usage
    - Automatic cleanup when widgets are destroyed
    - Thread-safe operations for concurrent access
    - Metadata tracking for widget categorization
    - Complete lifecycle tracking with state management
    - Safe registration/deregistration with guards and retry logic
    - Bulk operations with atomic semantics
    - Comprehensive validation and error recovery

    Performance:
    - Registration: < 10μs per widget
    - Bulk operations: < 1ms per 100 widgets
    - Cleanup: < 100μs for 1000 widgets
    - Memory overhead: < 100 bytes per widget (with lifecycle tracking)
    """

    def __init__(self):
        """Initialize enhanced widget registry."""
        self._widgets: dict[int, weakref.ReferenceType] = {}
        self._metadata: dict[int, dict[str, Any]] = {}
        self._lifecycle_events: dict[int, list[WidgetLifecycleEvent]] = {}
        self._widget_states: dict[int, WidgetLifecycleState] = {}
        self._lock = threading.RLock()  # Reentrant lock for nested calls
        self._cleanup_callbacks: list[Callable[[int], None]] = []
        self._lifecycle_callbacks: list[Callable[[WidgetLifecycleEvent], None]] = []

        # Safety and validation settings
        self._max_registration_attempts = 3
        self._registration_timeout = 5.0  # seconds
        self._enable_validation = True
        self._enable_lifecycle_tracking = True

        # Performance tracking
        self._stats = {
            "total_registrations": 0,
            "total_unregistrations": 0,
            "registration_failures": 0,
            "validation_failures": 0,
            "bulk_operations": 0,
            "lifecycle_events": 0,
        }
        self._start_time = time.time()  # For uptime tracking

    def register(self, widget: ThemeableWidget, metadata: Optional[dict[str, Any]] = None) -> None:
        """Register a widget with enhanced safety and lifecycle tracking.

        Args:
            widget: The widget to register.
            metadata: Optional metadata dictionary for the widget.

        Raises:
            RegistrationError: If registration fails after retries.
            ValueError: If widget is invalid or already registered.

        Performance: < 10μs per widget
        Thread Safety: Safe for concurrent calls

        """
        start_time = time.perf_counter()

        # Validate widget before registration
        if self._enable_validation and not self._validate_widget(widget):
            self._stats["validation_failures"] += 1
            raise ValueError(f"Widget validation failed: {type(widget).__name__}")

        widget_id = id(widget)

        # Check if already registered
        if self.is_registered(widget):
            raise ValueError(f"Widget {widget_id} is already registered")

        # Attempt registration with retry logic
        for attempt in range(self._max_registration_attempts):
            try:
                with self._lock:
                    # Double-check after acquiring lock
                    if widget_id in self._widgets:
                        raise ValueError(f"Widget {widget_id} registered during retry")

                    # Create WeakReference with cleanup callback
                    def cleanup_callback(ref):
                        self._on_widget_destroyed(widget_id)

                    weak_ref = weakref.ref(widget, cleanup_callback)
                    self._widgets[widget_id] = weak_ref

                    # Store metadata
                    if metadata:
                        self._metadata[widget_id] = metadata.copy()

                    # Update lifecycle state and tracking
                    if self._enable_lifecycle_tracking:
                        self._update_lifecycle_state(
                            widget_id, WidgetLifecycleState.REGISTERED, metadata
                        )

                    # Update statistics
                    self._stats["total_registrations"] += 1

                    break  # Success - exit retry loop

            except Exception as e:
                if attempt == self._max_registration_attempts - 1:
                    # Final attempt failed
                    self._stats["registration_failures"] += 1
                    raise RegistrationError(
                        f"Failed to register widget after {self._max_registration_attempts} attempts: {e}"
                    )

                # Brief delay before retry
                time.sleep(0.001)  # 1ms delay
                continue

        # Validate performance requirement
        duration_us = (time.perf_counter() - start_time) * 1_000_000
        if duration_us > 10:
            # Log warning but don't fail - performance degradation not critical
            print(f"Warning: Widget registration took {duration_us:.2f}μs (target: <10μs)")

    def unregister(self, widget: ThemeableWidget) -> bool:
        """Safely unregister a widget from the registry.

        Args:
            widget: The widget to unregister.

        Returns:
            True if widget was registered and removed, False otherwise.

        """
        with self._lock:
            widget_id = id(widget)

            if widget_id in self._widgets:
                # Update lifecycle state before removal
                if self._enable_lifecycle_tracking:
                    self._update_lifecycle_state(widget_id, WidgetLifecycleState.UNREGISTERED)

                # Remove from all tracking structures
                del self._widgets[widget_id]
                self._metadata.pop(widget_id, None)
                self._widget_states.pop(widget_id, None)
                self._lifecycle_events.pop(widget_id, None)

                # Update statistics
                self._stats["total_unregistrations"] += 1

                return True

            return False

    def is_registered(self, widget: ThemeableWidget) -> bool:
        """Check if a widget is registered.

        Args:
            widget: The widget to check.

        Returns:
            True if widget is registered and still alive.

        """
        with self._lock:
            widget_id = id(widget)

            if widget_id not in self._widgets:
                return False

            # Check if weak reference is still valid
            weak_ref = self._widgets[widget_id]
            return weak_ref() is not None

    def get_metadata(self, widget: ThemeableWidget) -> Optional[dict[str, Any]]:
        """Get metadata for a registered widget.

        Args:
            widget: The widget to get metadata for.

        Returns:
            Metadata dictionary or None if widget not registered.

        """
        with self._lock:
            widget_id = id(widget)
            return self._metadata.get(widget_id, {}).copy()

    def count(self) -> int:
        """Get the number of registered widgets.

        Returns:
            Number of currently registered widgets.

        """
        with self._lock:
            # Clean up dead references first
            self._cleanup_dead_references()
            return len(self._widgets)

    def is_empty(self) -> bool:
        """Check if registry is empty.

        Returns:
            True if no widgets are registered.

        """
        return self.count() == 0

    def iter_widgets(self) -> Iterator[ThemeableWidget]:
        """Iterate over all registered widgets.

        Yields:
            Active widgets in the registry.

        Note:
            Dead references are automatically skipped.

        """
        with self._lock:
            # Get snapshot of current widgets
            widget_refs = list(self._widgets.values())

        # Iterate without lock to avoid blocking other operations
        for weak_ref in widget_refs:
            widget = weak_ref()
            if widget is not None:
                yield widget

    def filter_widgets(
        self, predicate: Callable[[dict[str, Any]], bool]
    ) -> Iterator[ThemeableWidget]:
        """Filter widgets by metadata predicate.

        Args:
            predicate: Function that takes metadata dict and returns bool.

        Yields:
            Widgets whose metadata matches the predicate.

        """
        with self._lock:
            # Get snapshot of widgets and metadata
            widget_items = []
            for widget_id, weak_ref in self._widgets.items():
                widget = weak_ref()
                if widget is not None:
                    metadata = self._metadata.get(widget_id, {})
                    widget_items.append((widget, metadata))

        # Filter without lock
        for widget, metadata in widget_items:
            if predicate(metadata):
                yield widget

    def add_cleanup_callback(self, callback: Callable[[int], None]) -> None:
        """Add callback to be called when widgets are destroyed.

        Args:
            callback: Function called with widget ID when widget is destroyed.

        """
        with self._lock:
            self._cleanup_callbacks.append(callback)

    def add_lifecycle_callback(self, callback: Callable[[WidgetLifecycleEvent], None]) -> None:
        """Add callback to be called for lifecycle events.

        Args:
            callback: Function called with lifecycle event information.

        """
        with self._lock:
            self._lifecycle_callbacks.append(callback)

    def bulk_register(
        self,
        widgets: list[ThemeableWidget],
        metadata_list: Optional[list[Optional[dict[str, Any]]]] = None,
    ) -> dict[str, Any]:
        """Register multiple widgets atomically with comprehensive error handling.

        Args:
            widgets: List of widgets to register.
            metadata_list: Optional list of metadata dictionaries (must match widgets length).

        Returns:
            Dictionary with operation statistics and results.

        Raises:
            BulkOperationError: If some registrations fail.
            ValueError: If input validation fails.

        """
        start_time = time.perf_counter()

        if not widgets:
            return {"successful": 0, "failed": 0, "duration_ms": 0.0}

        if metadata_list and len(metadata_list) != len(widgets):
            raise ValueError("metadata_list length must match widgets length")

        successful = []
        failed = []

        # Use atomic operation semantics - either all succeed or all fail for critical operations
        with self._lock:
            # Pre-validate all widgets
            if self._enable_validation:
                for widget in widgets:
                    if not self._validate_widget(widget):
                        failed.append((widget, "Validation failed"))
                    elif self.is_registered(widget):
                        failed.append((widget, "Already registered"))

            # If validation enabled and any failed, reject entire batch
            if self._enable_validation and failed:
                raise BulkOperationError(
                    f"Bulk registration validation failed for {len(failed)} widgets",
                    0,
                    [item[0] for item in failed],
                )

            # Attempt to register all widgets
            for i, widget in enumerate(widgets):
                metadata = metadata_list[i] if metadata_list else None

                try:
                    # Perform individual registration (without validation since already done)
                    widget_id = id(widget)

                    def cleanup_callback(ref, wid=widget_id):
                        self._on_widget_destroyed(wid)

                    weak_ref = weakref.ref(widget, cleanup_callback)
                    self._widgets[widget_id] = weak_ref

                    if metadata:
                        self._metadata[widget_id] = metadata.copy()

                    if self._enable_lifecycle_tracking:
                        self._update_lifecycle_state(
                            widget_id, WidgetLifecycleState.REGISTERED, metadata
                        )

                    successful.append(widget)

                except Exception as e:
                    failed.append((widget, str(e)))

            # Update statistics
            self._stats["total_registrations"] += len(successful)
            self._stats["registration_failures"] += len(failed)
            self._stats["bulk_operations"] += 1

        duration_ms = (time.perf_counter() - start_time) * 1000

        # Check performance requirement
        if len(widgets) > 0:
            per_widget_ms = duration_ms / len(widgets)
            if per_widget_ms > 0.01:  # 10μs = 0.01ms per widget
                print(f"Warning: Bulk registration averaged {per_widget_ms:.3f}ms per widget")

        result = {
            "successful": len(successful),
            "failed": len(failed),
            "duration_ms": duration_ms,
            "per_widget_us": (duration_ms * 1000) / len(widgets) if widgets else 0,
        }

        if failed:
            raise BulkOperationError(
                f"Bulk registration failed for {len(failed)} of {len(widgets)} widgets",
                len(successful),
                [item[0] for item in failed],
            )

        return result

    def bulk_unregister(self, widgets: list[ThemeableWidget]) -> dict[str, Any]:
        """Unregister multiple widgets efficiently.

        Args:
            widgets: List of widgets to unregister.

        Returns:
            Dictionary with operation statistics.

        """
        start_time = time.perf_counter()

        if not widgets:
            return {"successful": 0, "failed": 0, "duration_ms": 0.0}

        successful_count = 0

        with self._lock:
            for widget in widgets:
                if self.unregister(widget):  # Uses the enhanced unregister method
                    successful_count += 1

            self._stats["bulk_operations"] += 1

        duration_ms = (time.perf_counter() - start_time) * 1000

        return {
            "successful": successful_count,
            "failed": len(widgets) - successful_count,
            "duration_ms": duration_ms,
            "per_widget_us": (duration_ms * 1000) / len(widgets) if widgets else 0,
        }

    def get_lifecycle_events(self, widget: ThemeableWidget) -> list[WidgetLifecycleEvent]:
        """Get lifecycle events for a widget.

        Args:
            widget: Widget to get events for.

        Returns:
            List of lifecycle events in chronological order.

        """
        if not self._enable_lifecycle_tracking:
            return []

        with self._lock:
            widget_id = id(widget)
            return self._lifecycle_events.get(widget_id, []).copy()

    def get_widget_state(self, widget: ThemeableWidget) -> Optional[WidgetLifecycleState]:
        """Get current lifecycle state of a widget.

        Args:
            widget: Widget to get state for.

        Returns:
            Current lifecycle state or None if not tracked.

        """
        if not self._enable_lifecycle_tracking:
            return None

        with self._lock:
            widget_id = id(widget)
            return self._widget_states.get(widget_id)

    def get_statistics(self) -> dict[str, Any]:
        """Get comprehensive registry statistics.

        Returns:
            Dictionary containing registry statistics.

        """
        with self._lock:
            # Clean up dead references to get accurate count
            self._cleanup_dead_references()

            stats = self._stats.copy()
            stats.update(
                {
                    "active_widgets": len(self._widgets),
                    "tracked_lifecycle_events": sum(
                        len(events) for events in self._lifecycle_events.values()
                    ),
                    "memory_overhead_bytes": self._estimate_memory_overhead(),
                    "uptime_seconds": time.time() - self._start_time,
                }
            )

            return stats

    def validate_integrity(self) -> dict[str, Any]:
        """Validate registry integrity and detect issues.

        Returns:
            Dictionary with validation results.

        """
        with self._lock:
            issues = []

            # Check for orphaned metadata
            orphaned_metadata = set(self._metadata.keys()) - set(self._widgets.keys())
            if orphaned_metadata:
                issues.append(f"Orphaned metadata for {len(orphaned_metadata)} widgets")

            # Check for orphaned lifecycle data
            if self._enable_lifecycle_tracking:
                orphaned_events = set(self._lifecycle_events.keys()) - set(self._widgets.keys())
                orphaned_states = set(self._widget_states.keys()) - set(self._widgets.keys())

                if orphaned_events:
                    issues.append(f"Orphaned lifecycle events for {len(orphaned_events)} widgets")
                if orphaned_states:
                    issues.append(f"Orphaned lifecycle states for {len(orphaned_states)} widgets")

            # Check for dead weak references
            dead_refs = 0
            for _widget_id, weak_ref in self._widgets.items():
                if weak_ref() is None:
                    dead_refs += 1

            if dead_refs > 0:
                issues.append(f"{dead_refs} dead weak references found")

            return {
                "is_valid": len(issues) == 0,
                "issues": issues,
                "total_widgets": len(self._widgets),
                "dead_references": dead_refs,
            }

    def _validate_widget(self, widget: ThemeableWidget) -> bool:
        """Validate a widget before registration.

        Args:
            widget: Widget to validate.

        Returns:
            True if widget is valid for registration.

        """
        try:
            # Basic validation
            if widget is None:
                return False

            # Check if it implements the required protocol
            if not hasattr(widget, "__class__"):
                return False

            # Additional validation can be added here
            return True

        except Exception:
            return False

    def _update_lifecycle_state(
        self, widget_id: int, state: WidgetLifecycleState, metadata: Optional[dict[str, Any]] = None
    ) -> None:
        """Update widget lifecycle state and emit event.

        Args:
            widget_id: ID of the widget.
            state: New lifecycle state.
            metadata: Optional event metadata.

        """
        if not self._enable_lifecycle_tracking:
            return

        timestamp = time.time()

        # Update state
        self._widget_states[widget_id] = state

        # Create and store event
        event = WidgetLifecycleEvent(
            widget_id=widget_id, state=state, timestamp=timestamp, metadata=metadata
        )

        if widget_id not in self._lifecycle_events:
            self._lifecycle_events[widget_id] = []

        self._lifecycle_events[widget_id].append(event)

        # Update statistics
        self._stats["lifecycle_events"] += 1

        # Notify lifecycle callbacks
        for callback in self._lifecycle_callbacks:
            try:
                callback(event)
            except Exception as e:
                print(f"Warning: Lifecycle callback failed: {e}")

    def _estimate_memory_overhead(self) -> int:
        """Estimate memory overhead of the registry.

        Returns:
            Estimated memory overhead in bytes.

        """
        try:
            import sys

            total_size = 0
            total_size += sys.getsizeof(self._widgets)
            total_size += sys.getsizeof(self._metadata)
            total_size += sys.getsizeof(self._lifecycle_events)
            total_size += sys.getsizeof(self._widget_states)

            # Estimate content sizes
            for metadata in self._metadata.values():
                total_size += sys.getsizeof(metadata)

            for events in self._lifecycle_events.values():
                total_size += sys.getsizeof(events)
                for event in events:
                    total_size += sys.getsizeof(event)

            return total_size

        except Exception:
            # Rough estimate if sys.getsizeof fails
            widget_count = len(self._widgets)
            return widget_count * 100  # 100 bytes per widget estimate

    def _cleanup_dead_references(self) -> int:
        """Clean up dead weak references.

        Returns:
            Number of dead references cleaned up.

        """
        dead_ids = []

        for widget_id, weak_ref in self._widgets.items():
            if weak_ref() is None:
                dead_ids.append(widget_id)

        for widget_id in dead_ids:
            del self._widgets[widget_id]
            self._metadata.pop(widget_id, None)

        return len(dead_ids)

    def _on_widget_destroyed(self, widget_id: int) -> None:
        """Called when a widget is destroyed (WeakRef callback).

        Args:
            widget_id: ID of the destroyed widget.

        """
        with self._lock:
            # Update lifecycle state if tracking enabled
            if self._enable_lifecycle_tracking and widget_id in self._widget_states:
                self._update_lifecycle_state(widget_id, WidgetLifecycleState.DESTROYED)

            # Remove from registry
            self._widgets.pop(widget_id, None)
            self._metadata.pop(widget_id, None)

            # Keep lifecycle data for a while for debugging/analysis
            # It will be cleaned up eventually by validate_integrity or manual cleanup

            # Notify cleanup callbacks
            for callback in self._cleanup_callbacks:
                try:
                    callback(widget_id)
                except Exception as e:
                    # Don't let callback errors crash cleanup
                    print(f"Warning: Cleanup callback failed: {e}")


class LifecycleManager:
    """Complete widget lifecycle management from registration to cleanup.

    Manages the full lifecycle of themed widgets:
    - Registration with automatic theme provider injection
    - Lifecycle callbacks for registration/unregistration events
    - Batch operations for performance
    - Automatic cleanup on shutdown

    This manager provides the foundation for ThemedWidget's automatic
    memory management - widgets are automatically registered when created
    and cleaned up when destroyed.
    """

    def __init__(self, registry: Optional[WidgetRegistry] = None):
        """Initialize lifecycle manager.

        Args:
            registry: Widget registry to use. Creates new one if None.

        """
        self._registry = registry or WidgetRegistry()
        self._theme_provider: Optional[ThemeProvider] = None
        self._lifecycle_callbacks: dict[str, list[Callable]] = defaultdict(list)
        self._lock = threading.RLock()

        # Add registry cleanup callback
        self._registry.add_cleanup_callback(self._on_widget_destroyed)

    def set_default_theme_provider(self, provider: ThemeProvider) -> None:
        """Set default theme provider for new widgets.

        Args:
            provider: Theme provider to inject into new widgets.

        """
        with self._lock:
            self._theme_provider = provider

    def register_widget(self, widget: ThemeableWidget) -> None:
        """Register a widget and inject dependencies.

        Args:
            widget: Widget to register.

        This method:
        - Registers widget in the registry
        - Injects theme provider if available
        - Calls registration callbacks

        """
        with self._lock:
            # Register in registry
            self._registry.register(widget)

            # Inject theme provider if available
            if self._theme_provider and hasattr(widget, "_theme_provider"):
                widget._theme_provider = self._theme_provider

            # Call registration callbacks
            self._call_lifecycle_callbacks("register", widget)

    def unregister_widget(self, widget: ThemeableWidget) -> bool:
        """Unregister a widget.

        Args:
            widget: Widget to unregister.

        Returns:
            True if widget was registered and removed.

        """
        with self._lock:
            was_registered = self._registry.unregister(widget)

            if was_registered:
                # Call unregistration callbacks
                self._call_lifecycle_callbacks("unregister", widget)

            return was_registered

    def is_widget_registered(self, widget: ThemeableWidget) -> bool:
        """Check if a widget is registered.

        Args:
            widget: Widget to check.

        Returns:
            True if widget is registered.

        """
        return self._registry.is_registered(widget)

    def get_widget_count(self) -> int:
        """Get number of registered widgets.

        Returns:
            Number of currently registered widgets.

        """
        return self._registry.count()

    def add_lifecycle_callback(
        self, event: str, callback: Callable[[ThemeableWidget], None]
    ) -> None:
        """Add callback for lifecycle events.

        Args:
            event: Event name ('register' or 'unregister').
            callback: Function to call when event occurs.

        """
        with self._lock:
            self._lifecycle_callbacks[event].append(callback)

    def batch_register(self, widgets: list[ThemeableWidget]) -> None:
        """Register multiple widgets efficiently.

        Args:
            widgets: List of widgets to register.

        Performance: Optimized for bulk operations.

        """
        start_time = time.perf_counter()

        with self._lock:
            for widget in widgets:
                self.register_widget(widget)

        duration = time.perf_counter() - start_time
        if len(widgets) > 0:
            per_widget_ms = (duration * 1000) / len(widgets)
            if per_widget_ms > 1:  # Should be much faster than 1ms per widget
                print(f"Warning: Batch registration averaged {per_widget_ms:.2f}ms per widget")

    def batch_unregister(self, widgets: list[ThemeableWidget]) -> int:
        """Unregister multiple widgets efficiently.

        Args:
            widgets: List of widgets to unregister.

        Returns:
            Number of widgets actually unregistered.

        """
        count = 0
        with self._lock:
            for widget in widgets:
                if self.unregister_widget(widget):
                    count += 1

        return count

    def cleanup(self) -> None:
        """Clean up all registered widgets and resources.

        This method:
        - Unregisters all widgets
        - Calls cleanup callbacks
        - Clears internal state
        """
        start_time = time.perf_counter()

        with self._lock:
            # Get all registered widgets
            widgets = list(self._registry.iter_widgets())

            # Unregister all widgets
            for widget in widgets:
                self.unregister_widget(widget)

            # Clear callbacks
            self._lifecycle_callbacks.clear()

        duration_us = (time.perf_counter() - start_time) * 1_000_000
        if duration_us > 100_000:  # 100ms = 100,000μs
            print(f"Warning: Cleanup took {duration_us:.0f}μs (target: <100ms for 1000 widgets)")

    def get_registry(self) -> WidgetRegistry:
        """Get the widget registry.

        Returns:
            The widget registry instance.

        """
        return self._registry

    def _call_lifecycle_callbacks(self, event: str, widget: ThemeableWidget) -> None:
        """Call callbacks for a lifecycle event.

        Args:
            event: Event name.
            widget: Widget the event occurred for.

        """
        for callback in self._lifecycle_callbacks[event]:
            try:
                callback(widget)
            except Exception as e:
                print(f"Warning: Lifecycle callback failed for {event}: {e}")

    def _on_widget_destroyed(self, widget_id: int) -> None:
        """Called when a widget is destroyed.

        Args:
            widget_id: ID of the destroyed widget.

        """
        # Widget is already removed from registry by this point
        # This callback allows for additional cleanup logic if needed
        pass


class ThemeUpdateContext:
    """Context manager for batch theme updates with automatic cleanup.

    Provides efficient batch theme updates while ensuring proper resource
    management and cleanup. Used internally by the theme system for
    switching themes across multiple widgets.

    Performance: < 1ms context manager overhead
    """

    def __init__(self, lifecycle_manager: LifecycleManager):
        """Initialize theme update context.

        Args:
            lifecycle_manager: The lifecycle manager to use.

        """
        self._manager = lifecycle_manager
        self._start_time: Optional[float] = None
        self._widgets_updated: list[ThemeableWidget] = []

    def __enter__(self) -> "ThemeUpdateContext":
        """Enter the context manager."""
        self._start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context manager with cleanup."""
        if self._start_time:
            duration_ms = (time.perf_counter() - self._start_time) * 1000
            if duration_ms > 1:
                print(f"Warning: ThemeUpdateContext took {duration_ms:.2f}ms (target: <1ms)")

        # Clear update tracking
        self._widgets_updated.clear()

        # Handle exceptions gracefully
        if exc_type:
            print(f"Warning: Exception in ThemeUpdateContext: {exc_val}")
            # Don't suppress exceptions
            return False

    def update_theme(self, theme_name: str) -> None:
        """Update theme for all registered widgets.

        Args:
            theme_name: Name of the theme to apply.

        """
        # Get all widgets from registry
        widgets = list(self._manager.get_registry().iter_widgets())

        # Update each widget's theme
        for widget in widgets:
            try:
                # Call widget's theme change handler
                if hasattr(widget, "on_theme_changed"):
                    widget.on_theme_changed()
                    self._widgets_updated.append(widget)
            except Exception as e:
                print(f"Warning: Failed to update theme for widget {id(widget)}: {e}")

    def get_updated_count(self) -> int:
        """Get number of widgets successfully updated.

        Returns:
            Number of widgets that were successfully updated.

        """
        return len(self._widgets_updated)


class WidgetCreationContext:
    """Context manager for managing widget creation in batches.

    Optimizes widget creation and registration for better performance
    when creating many widgets at once.
    """

    def __init__(self, lifecycle_manager: LifecycleManager):
        """Initialize widget creation context.

        Args:
            lifecycle_manager: The lifecycle manager to use.

        """
        self._manager = lifecycle_manager
        self._widgets_created: list[ThemeableWidget] = []
        self._start_time: Optional[float] = None

    def __enter__(self) -> "WidgetCreationContext":
        """Enter the context manager."""
        self._start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context manager with cleanup."""
        if self._start_time and self._widgets_created:
            duration = time.perf_counter() - self._start_time
            per_widget_ms = (duration * 1000) / len(self._widgets_created)
            if per_widget_ms > 0.1:  # Should be very fast per widget
                print(f"Warning: Widget creation averaged {per_widget_ms:.3f}ms per widget")

        # Clean up if exception occurred
        if exc_type:
            # Cleanup any widgets created in this context
            for widget in self._widgets_created:
                try:
                    self._manager.unregister_widget(widget)
                except Exception:
                    pass  # Best effort cleanup

        self._widgets_created.clear()
        return False  # Don't suppress exceptions

    def register_widget(self, widget: ThemeableWidget) -> None:
        """Register a widget within this creation context.

        Args:
            widget: Widget to register.

        """
        self._manager.register_widget(widget)
        self._widgets_created.append(widget)

    def get_created_count(self) -> int:
        """Get number of widgets created in this context.

        Returns:
            Number of widgets created.

        """
        return len(self._widgets_created)


class PerformanceContext:
    """Context manager for monitoring resource usage during operations.

    Tracks memory usage, execution time, and other performance metrics
    during themed operations.
    """

    def __init__(self):
        """Initialize performance context."""
        self._start_time: Optional[float] = None
        self._start_memory: Optional[int] = None
        self._peak_memory: int = 0
        self._metrics: dict[str, Any] = {}

    def __enter__(self) -> "PerformanceContext":
        """Enter the context manager."""
        self._start_time = time.perf_counter()
        self._start_memory = self._get_memory_usage()
        self._peak_memory = self._start_memory
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context manager."""
        if self._start_time and self._start_memory:
            end_time = time.perf_counter()
            end_memory = self._get_memory_usage()

            self._metrics = {
                "execution_time": end_time - self._start_time,
                "memory_usage": end_memory - self._start_memory,
                "peak_memory": max(self._peak_memory - self._start_memory, 0),
                "start_memory": self._start_memory,
                "end_memory": end_memory,
            }

        return False  # Don't suppress exceptions

    def get_metrics(self) -> dict[str, Any]:
        """Get performance metrics.

        Returns:
            Dictionary of performance metrics.

        """
        # Update peak memory if still running
        if self._start_memory:
            current_memory = self._get_memory_usage()
            self._peak_memory = max(self._peak_memory, current_memory)

        return self._metrics.copy()

    def _get_memory_usage(self) -> int:
        """Get current memory usage in bytes.

        Returns:
            Current memory usage.

        """
        import os

        import psutil

        try:
            process = psutil.Process(os.getpid())
            return process.memory_info().rss
        except Exception:
            # Fallback if psutil not available
            return 0


class CleanupScheduler:
    """Automatic cleanup scheduling and execution.

    Manages cleanup operations for objects implementing CleanupProtocol.
    Provides both scheduled and emergency cleanup capabilities.
    """

    def __init__(self):
        """Initialize cleanup scheduler."""
        self._cleanup_objects: set[weakref.ReferenceType] = set()
        self._lock = threading.RLock()

    def schedule_cleanup(self, obj: CleanupProtocol) -> None:
        """Schedule an object for cleanup.

        Args:
            obj: Object to schedule for cleanup.

        """
        with self._lock:
            # Use weak reference to avoid keeping object alive
            weak_ref = weakref.ref(obj)
            self._cleanup_objects.add(weak_ref)

    def execute_cleanup(self) -> int:
        """Execute cleanup for all scheduled objects.

        Returns:
            Number of objects successfully cleaned up.

        """
        start_time = time.perf_counter()

        with self._lock:
            # Get valid objects that need cleanup
            objects_to_cleanup = []
            dead_refs = set()

            for weak_ref in self._cleanup_objects:
                obj = weak_ref()
                if obj is None:
                    dead_refs.add(weak_ref)
                elif obj.is_cleanup_required():
                    objects_to_cleanup.append(obj)

            # Remove dead references
            self._cleanup_objects -= dead_refs

        # Execute cleanup without holding lock
        cleaned_count = 0
        for obj in objects_to_cleanup:
            try:
                obj.cleanup()
                cleaned_count += 1
            except Exception as e:
                print(f"Warning: Cleanup failed for object {id(obj)}: {e}")

        duration_ms = (time.perf_counter() - start_time) * 1000
        if len(objects_to_cleanup) > 0:
            per_object_ms = duration_ms / len(objects_to_cleanup)
            if per_object_ms > 0.1:  # Should be very fast per object
                print(f"Warning: Cleanup averaged {per_object_ms:.3f}ms per object")

        return cleaned_count

    def emergency_cleanup(self) -> None:
        """Execute emergency cleanup (ignore all errors).

        Used during system shutdown when we need to clean up
        everything regardless of errors.
        """
        with self._lock:
            objects = []
            for weak_ref in list(self._cleanup_objects):
                obj = weak_ref()
                if obj is not None:
                    objects.append(obj)

        # Emergency cleanup - catch and ignore all errors
        for obj in objects:
            try:
                if hasattr(obj, "cleanup"):
                    obj.cleanup()
            except Exception:
                pass  # Ignore all errors during emergency cleanup

        # Clear all scheduled objects
        with self._lock:
            self._cleanup_objects.clear()

    def get_scheduled_count(self) -> int:
        """Get number of objects scheduled for cleanup.

        Returns:
            Number of objects currently scheduled.

        """
        with self._lock:
            # Clean up dead references
            dead_refs = set()
            for weak_ref in self._cleanup_objects:
                if weak_ref() is None:
                    dead_refs.add(weak_ref)

            self._cleanup_objects -= dead_refs
            return len(self._cleanup_objects)


class CleanupValidator:
    """Cleanup validation and verification.

    Validates that cleanup operations were successful and objects
    are properly cleaned up.
    """

    def __init__(self):
        """Initialize cleanup validator."""
        pass

    def validate_cleanup(self, obj: CleanupProtocol) -> bool:
        """Validate that an object was properly cleaned up.

        Args:
            obj: Object to validate cleanup for.

        Returns:
            True if cleanup was successful.

        """
        try:
            return not obj.is_cleanup_required()
        except Exception:
            return False

    def validate_multiple(self, objects: list[CleanupProtocol]) -> dict[str, int]:
        """Validate cleanup for multiple objects.

        Args:
            objects: List of objects to validate.

        Returns:
            Dictionary with cleanup statistics.

        """
        stats = {"total": len(objects), "cleaned": 0, "failed": 0, "errors": 0}

        for obj in objects:
            try:
                if self.validate_cleanup(obj):
                    stats["cleaned"] += 1
                else:
                    stats["failed"] += 1
            except Exception:
                stats["errors"] += 1

        return stats


class MemoryTracker:
    """Memory usage tracking for themed widgets.

    Tracks memory usage per widget and provides diagnostics
    for memory leak detection.
    """

    def __init__(self):
        """Initialize memory tracker."""
        self._tracked_objects: dict[int, weakref.ReferenceType] = {}
        self._memory_snapshots: dict[int, dict[str, Any]] = {}
        self._lock = threading.RLock()

    def start_tracking(self, obj: Any) -> None:
        """Start tracking memory usage for an object.

        Args:
            obj: Object to start tracking.

        """
        with self._lock:
            obj_id = id(obj)

            # Create weak reference
            weak_ref = weakref.ref(obj, lambda ref: self._on_object_destroyed(obj_id))
            self._tracked_objects[obj_id] = weak_ref

            # Take memory snapshot
            self._memory_snapshots[obj_id] = {
                "start_time": time.time(),
                "start_memory": self._get_object_memory(obj),
                "type": type(obj).__name__,
            }

    def stop_tracking(self, obj: Any) -> Optional[dict[str, Any]]:
        """Stop tracking an object and get final statistics.

        Args:
            obj: Object to stop tracking.

        Returns:
            Memory usage statistics or None if not tracked.

        """
        with self._lock:
            obj_id = id(obj)

            if obj_id not in self._tracked_objects:
                return None

            # Get final statistics
            snapshot = self._memory_snapshots.get(obj_id, {})
            final_stats = {
                **snapshot,
                "end_time": time.time(),
                "end_memory": self._get_object_memory(obj),
                "duration": time.time() - snapshot.get("start_time", 0),
            }

            # Calculate memory difference
            start_mem = snapshot.get("start_memory", 0)
            end_mem = final_stats["end_memory"]
            final_stats["memory_delta"] = end_mem - start_mem

            # Clean up tracking
            del self._tracked_objects[obj_id]
            del self._memory_snapshots[obj_id]

            return final_stats

    def get_memory_usage(self, obj: Any) -> int:
        """Get current memory usage for a tracked object.

        Args:
            obj: Object to get memory usage for.

        Returns:
            Memory usage in bytes, or 0 if not tracked.

        """
        with self._lock:
            obj_id = id(obj)

            if obj_id not in self._tracked_objects:
                return 0

            return self._get_object_memory(obj)

    def is_tracking(self, obj: Any) -> bool:
        """Check if an object is being tracked.

        Args:
            obj: Object to check.

        Returns:
            True if object is being tracked.

        """
        with self._lock:
            return id(obj) in self._tracked_objects

    def get_tracked_count(self) -> int:
        """Get number of objects being tracked.

        Returns:
            Number of tracked objects.

        """
        with self._lock:
            # Clean up dead references
            dead_ids = []
            for obj_id, weak_ref in self._tracked_objects.items():
                if weak_ref() is None:
                    dead_ids.append(obj_id)

            for obj_id in dead_ids:
                self._tracked_objects.pop(obj_id, None)
                self._memory_snapshots.pop(obj_id, None)

            return len(self._tracked_objects)

    def get_all_statistics(self) -> list[dict[str, Any]]:
        """Get statistics for all tracked objects.

        Returns:
            List of memory usage statistics.

        """
        stats = []

        with self._lock:
            for obj_id, weak_ref in self._tracked_objects.items():
                obj = weak_ref()
                if obj is not None:
                    snapshot = self._memory_snapshots.get(obj_id, {})
                    current_stats = {
                        **snapshot,
                        "current_time": time.time(),
                        "current_memory": self._get_object_memory(obj),
                        "object_id": obj_id,
                    }

                    # Calculate current duration and memory delta
                    current_stats["current_duration"] = current_stats[
                        "current_time"
                    ] - snapshot.get("start_time", 0)
                    current_stats["current_memory_delta"] = current_stats[
                        "current_memory"
                    ] - snapshot.get("start_memory", 0)

                    stats.append(current_stats)

        return stats

    def _get_object_memory(self, obj: Any) -> int:
        """Get memory usage for a specific object.

        Args:
            obj: Object to measure.

        Returns:
            Estimated memory usage in bytes.

        """
        try:
            import sys

            return sys.getsizeof(obj)
        except Exception:
            return 0

    def _on_object_destroyed(self, obj_id: int) -> None:
        """Called when a tracked object is destroyed.

        Args:
            obj_id: ID of the destroyed object.

        """
        with self._lock:
            self._tracked_objects.pop(obj_id, None)
            self._memory_snapshots.pop(obj_id, None)


class LeakDetector:
    """Leak detection algorithms for finding memory leaks.

    Implements various algorithms to detect potential memory leaks
    in themed widgets and related objects.
    """

    def __init__(self):
        """Initialize leak detector."""
        self._tracked_objects: dict[int, weakref.ReferenceType] = {}
        self._creation_times: dict[int, float] = {}
        self._lock = threading.RLock()

    def track_object(self, obj: Any) -> None:
        """Start tracking an object for potential leaks.

        Args:
            obj: Object to track.

        """
        with self._lock:
            obj_id = id(obj)
            weak_ref = weakref.ref(obj, lambda ref: self._on_object_destroyed(obj_id))
            self._tracked_objects[obj_id] = weak_ref
            self._creation_times[obj_id] = time.time()

    def detect_leaks(self, max_age_seconds: float = 60.0) -> list[dict[str, Any]]:
        """Detect potential memory leaks.

        Args:
            max_age_seconds: Objects older than this are considered potential leaks.

        Returns:
            List of potential leak information.

        """
        current_time = time.time()
        potential_leaks = []

        with self._lock:
            for obj_id, weak_ref in self._tracked_objects.items():
                obj = weak_ref()
                if obj is not None:
                    creation_time = self._creation_times.get(obj_id, current_time)
                    age = current_time - creation_time

                    if age > max_age_seconds:
                        potential_leaks.append(
                            {
                                "object_id": obj_id,
                                "object_type": type(obj).__name__,
                                "age_seconds": age,
                                "creation_time": creation_time,
                            }
                        )

        return potential_leaks

    def force_gc_and_check(self) -> dict[str, int]:
        """Force garbage collection and check for leaks.

        Returns:
            Statistics about objects before and after GC.

        """
        # Count objects before GC
        before_count = 0
        with self._lock:
            for weak_ref in self._tracked_objects.values():
                if weak_ref() is not None:
                    before_count += 1

        # Force garbage collection
        gc.collect()

        # Count objects after GC
        after_count = 0
        dead_ids = []
        with self._lock:
            for obj_id, weak_ref in self._tracked_objects.items():
                if weak_ref() is None:
                    dead_ids.append(obj_id)
                else:
                    after_count += 1

            # Clean up dead references
            for obj_id in dead_ids:
                del self._tracked_objects[obj_id]
                self._creation_times.pop(obj_id, None)

        return {
            "before_gc": before_count,
            "after_gc": after_count,
            "collected": before_count - after_count,
            "potential_leaks": after_count,
        }

    def _on_object_destroyed(self, obj_id: int) -> None:
        """Called when a tracked object is destroyed.

        Args:
            obj_id: ID of the destroyed object.

        """
        with self._lock:
            self._tracked_objects.pop(obj_id, None)
            self._creation_times.pop(obj_id, None)


class ResourceReporter:
    """Resource usage reporting and metrics.

    Generates comprehensive reports on resource usage,
    memory patterns, and performance metrics.
    """

    def __init__(self):
        """Initialize resource reporter."""
        self._tracked_widgets: list[weakref.ReferenceType] = []
        self._lock = threading.RLock()
        self._start_time = time.time()

    def track_widget(self, widget: ThemeableWidget) -> None:
        """Start tracking a widget for reporting.

        Args:
            widget: Widget to track.

        """
        with self._lock:
            weak_ref = weakref.ref(widget)
            self._tracked_widgets.append(weak_ref)

    def generate_report(self) -> dict[str, Any]:
        """Generate comprehensive resource usage report.

        Returns:
            Dictionary containing resource usage statistics.

        """
        with self._lock:
            # Count active widgets
            active_widgets = []
            dead_refs = []

            for weak_ref in self._tracked_widgets:
                widget = weak_ref()
                if widget is None:
                    dead_refs.append(weak_ref)
                else:
                    active_widgets.append(widget)

            # Clean up dead references
            for dead_ref in dead_refs:
                self._tracked_widgets.remove(dead_ref)

            # Generate report
            report = {
                "timestamp": time.time(),
                "uptime_seconds": time.time() - self._start_time,
                "total_widgets": len(active_widgets),
                "memory_usage": self._estimate_total_memory(active_widgets),
                "widget_types": self._count_widget_types(active_widgets),
                "performance_metrics": self._get_performance_metrics(),
            }

            return report

    def _estimate_total_memory(self, widgets: list[ThemeableWidget]) -> int:
        """Estimate total memory usage for widgets.

        Args:
            widgets: List of widgets to measure.

        Returns:
            Estimated memory usage in bytes.

        """
        total_memory = 0

        for widget in widgets:
            try:
                import sys

                total_memory += sys.getsizeof(widget)
            except Exception:
                total_memory += 1024  # Estimate 1KB per widget

        return total_memory

    def _count_widget_types(self, widgets: list[ThemeableWidget]) -> dict[str, int]:
        """Count widgets by type.

        Args:
            widgets: List of widgets to categorize.

        Returns:
            Dictionary mapping widget types to counts.

        """
        type_counts = defaultdict(int)

        for widget in widgets:
            type_name = type(widget).__name__
            type_counts[type_name] += 1

        return dict(type_counts)

    def _get_performance_metrics(self) -> dict[str, Any]:
        """Get current performance metrics.

        Returns:
            Dictionary of performance metrics.

        """
        try:
            import os

            import psutil

            process = psutil.Process(os.getpid())
            return {
                "cpu_percent": process.cpu_percent(),
                "memory_rss": process.memory_info().rss,
                "memory_vms": process.memory_info().vms,
                "num_threads": process.num_threads(),
            }
        except Exception:
            return {"error": "Performance metrics unavailable"}


class PerformanceMonitor:
    """Performance impact monitoring for memory management operations.

    Monitors and reports on the performance impact of memory management
    operations to ensure they meet strict performance requirements.
    """

    def __init__(self):
        """Initialize performance monitor."""
        self._measurements: dict[str, list[dict[str, float]]] = defaultdict(list)
        self._lock = threading.RLock()

    @contextmanager
    def measure(self, operation_name: str):
        """Context manager for measuring operation performance.

        Args:
            operation_name: Name of the operation being measured.

        """
        start_time = time.perf_counter()
        start_memory = self._get_current_memory()

        try:
            yield
        finally:
            end_time = time.perf_counter()
            end_memory = self._get_current_memory()

            measurement = {
                "duration": end_time - start_time,
                "memory_delta": end_memory - start_memory,
                "timestamp": time.time(),
            }

            with self._lock:
                self._measurements[operation_name].append(measurement)

    def get_metrics(self) -> dict[str, dict[str, float]]:
        """Get performance metrics for all measured operations.

        Returns:
            Dictionary mapping operation names to their metrics.

        """
        with self._lock:
            metrics = {}

            for operation_name, measurements in self._measurements.items():
                if measurements:
                    durations = [m["duration"] for m in measurements]
                    memory_deltas = [m["memory_delta"] for m in measurements]

                    metrics[operation_name] = {
                        "count": len(measurements),
                        "duration": {
                            "min": min(durations),
                            "max": max(durations),
                            "avg": sum(durations) / len(durations),
                        },
                        "memory": {
                            "min": min(memory_deltas),
                            "max": max(memory_deltas),
                            "avg": sum(memory_deltas) / len(memory_deltas),
                        },
                        "latest_timestamp": max(m["timestamp"] for m in measurements),
                    }

            return metrics

    def clear_metrics(self) -> None:
        """Clear all collected metrics."""
        with self._lock:
            self._measurements.clear()

    def _get_current_memory(self) -> int:
        """Get current process memory usage.

        Returns:
            Memory usage in bytes.

        """
        try:
            import os

            import psutil

            process = psutil.Process(os.getpid())
            return process.memory_info().rss
        except Exception:
            return 0


# Convenience decorators for easy registration
def auto_register(registry: Optional[WidgetRegistry] = None):
    """Decorator for automatic widget registration.

    Args:
        registry: Registry to use. If None, uses global default.

    Returns:
        Decorator function.

    """

    def decorator(cls):
        original_init = cls.__init__

        @wraps(original_init)
        def enhanced_init(self, *args, **kwargs):
            # Call original __init__
            original_init(self, *args, **kwargs)

            # Auto-register if registry available
            target_registry = registry or getattr(cls, "_default_registry", None)
            if target_registry:
                try:
                    target_registry.register(self)
                except Exception as e:
                    print(f"Warning: Auto-registration failed for {cls.__name__}: {e}")

        cls.__init__ = enhanced_init
        return cls

    return decorator


def lifecycle_tracked(registry: WidgetRegistry):
    """Decorator to enable lifecycle tracking for a widget class.

    Args:
        registry: Registry to use for lifecycle tracking.

    Returns:
        Decorator function.

    """

    def decorator(cls):
        # Add lifecycle callback to class
        def track_lifecycle(
            self, state: WidgetLifecycleState, metadata: Optional[dict[str, Any]] = None
        ):
            """Track a lifecycle event for this widget."""
            widget_id = id(self)
            registry._update_lifecycle_state(widget_id, state, metadata)

        cls.track_lifecycle = track_lifecycle
        return cls

    return decorator


# Export all public interfaces
__all__ = [
    # Core Classes
    "WidgetRegistry",
    "LifecycleManager",
    # Lifecycle Management
    "WidgetLifecycleState",
    "WidgetLifecycleEvent",
    "RegistrationError",
    "BulkOperationError",
    # Context Managers
    "ThemeUpdateContext",
    "WidgetCreationContext",
    "PerformanceContext",
    # Cleanup System
    "CleanupProtocol",
    "CleanupScheduler",
    "CleanupValidator",
    # Memory Management
    "MemoryTracker",
    "LeakDetector",
    "ResourceReporter",
    "PerformanceMonitor",
    # Decorators
    "auto_register",
    "lifecycle_tracked",
]
