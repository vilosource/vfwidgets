"""Memory profiling utilities for VFWidgets Theme System leak detection.

This module provides comprehensive memory profiling tools to ensure the theme system
has zero memory leaks and maintains optimal memory usage. All utilities are designed
to catch memory issues early and validate that the WeakRef registry system works
correctly.

Key Memory Requirements:
- Zero memory leaks after 1000 theme switches
- < 1KB overhead per widget
- Automatic cleanup through WeakRef registry
- No circular references in theme components
- Proper cleanup when widgets are destroyed

Philosophy: Memory leaks are unacceptable. The theme system must provide
perfect memory management so developers never have to worry about leaks
when using ThemedWidget.
"""

import gc
import sys
import threading
import time
import tracemalloc
import weakref
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set


@dataclass
class MemorySnapshot:
    """Snapshot of memory usage at a specific point in time.

    Contains comprehensive memory statistics for analysis and comparison.
    Used to detect memory leaks and validate memory requirements.
    """

    timestamp: float
    total_memory: int
    peak_memory: int
    object_counts: Dict[str, int]
    reference_counts: Dict[int, int]
    tracked_objects: int
    weakref_count: int
    metadata: Dict[str, Any] = field(default_factory=dict)

    def compare_to(self, other: 'MemorySnapshot') -> 'MemoryDelta':
        """Compare this snapshot to another and return the delta.

        Args:
            other: Earlier snapshot to compare against.

        Returns:
            MemoryDelta showing changes between snapshots.

        """
        return MemoryDelta(
            time_delta=self.timestamp - other.timestamp,
            memory_delta=self.total_memory - other.total_memory,
            peak_delta=self.peak_memory - other.peak_memory,
            object_deltas={
                obj_type: self.object_counts.get(obj_type, 0) - other.object_counts.get(obj_type, 0)
                for obj_type in set(self.object_counts.keys()) | set(other.object_counts.keys())
            },
            tracked_objects_delta=self.tracked_objects - other.tracked_objects,
            weakref_delta=self.weakref_count - other.weakref_count,
        )


@dataclass
class MemoryDelta:
    """Difference between two memory snapshots.

    Shows how memory usage changed between two points in time,
    useful for detecting leaks and validating cleanup.
    """

    time_delta: float
    memory_delta: int
    peak_delta: int
    object_deltas: Dict[str, int]
    tracked_objects_delta: int
    weakref_delta: int

    def has_potential_leak(self, threshold_objects: int = 10, threshold_memory: int = 1024) -> bool:
        """Check if delta indicates a potential memory leak.

        Args:
            threshold_objects: Maximum allowed object count increase.
            threshold_memory: Maximum allowed memory increase in bytes.

        Returns:
            True if potential leak detected.

        """
        # Check memory growth
        if self.memory_delta > threshold_memory:
            return True

        # Check object count growth
        for obj_type, delta in self.object_deltas.items():
            if delta > threshold_objects and obj_type not in ['str', 'int', 'float']:
                return True

        return False

    def get_leak_summary(self) -> List[str]:
        """Get summary of potential leak indicators.

        Returns:
            List of human-readable leak indicators.

        """
        indicators = []

        if self.memory_delta > 1024:
            indicators.append(f"Memory increased by {self.memory_delta} bytes")

        for obj_type, delta in self.object_deltas.items():
            if delta > 10:
                indicators.append(f"{obj_type} objects increased by {delta}")

        if self.tracked_objects_delta > 0:
            indicators.append(f"Tracked objects increased by {self.tracked_objects_delta}")

        return indicators


class MemoryProfiler:
    """Comprehensive memory profiler for theme system validation.

    Tracks memory usage, object creation/destruction, and reference counts
    to detect memory leaks and validate memory requirements.

    Example:
        profiler = MemoryProfiler()

        with profiler.profile_operation("widget_creation"):
            widgets = [create_themed_widget() for _ in range(100)]

        with profiler.profile_operation("theme_switching"):
            for widget in widgets:
                widget.on_theme_changed()

        # Check for leaks
        leaks = profiler.detect_leaks()
        assert len(leaks) == 0, f"Memory leaks detected: {leaks}"

        # Validate memory requirements
        assert profiler.validate_memory_requirements()

    """

    def __init__(self, track_weakrefs: bool = True):
        """Initialize memory profiler.

        Args:
            track_weakrefs: Whether to track WeakRef usage.

        """
        self.track_weakrefs = track_weakrefs
        self._snapshots: List[MemorySnapshot] = []
        self._tracked_objects: Set[int] = set()
        self._weakrefs: List[weakref.ReferenceType] = []
        self._operation_profiles: Dict[str, List[MemoryDelta]] = defaultdict(list)
        self._baseline_snapshot: Optional[MemorySnapshot] = None
        self._lock = threading.Lock()

        # Start memory tracking
        if not tracemalloc.is_tracing():
            tracemalloc.start()

    def take_snapshot(self, label: str = "") -> MemorySnapshot:
        """Take a memory snapshot at current point in time.

        Args:
            label: Optional label for the snapshot.

        Returns:
            MemorySnapshot with current memory state.

        """
        with self._lock:
            gc.collect()  # Force garbage collection for accurate measurement

            # Get memory statistics
            current, peak = tracemalloc.get_traced_memory()

            # Count objects by type
            object_counts = defaultdict(int)
            for obj in gc.get_objects():
                obj_type = type(obj).__name__
                object_counts[obj_type] += 1

            # Count reference counts for tracked objects
            ref_counts = {}
            for obj_id in self._tracked_objects:
                try:
                    # Find object by id (this is not perfect but works for testing)
                    for obj in gc.get_objects():
                        if id(obj) == obj_id:
                            ref_counts[obj_id] = sys.getrefcount(obj)
                            break
                except:
                    pass  # Object may have been garbage collected

            # Count live weakrefs
            live_weakrefs = sum(1 for ref in self._weakrefs if ref() is not None)

            snapshot = MemorySnapshot(
                timestamp=time.time(),
                total_memory=current,
                peak_memory=peak,
                object_counts=dict(object_counts),
                reference_counts=ref_counts,
                tracked_objects=len(self._tracked_objects),
                weakref_count=live_weakrefs,
                metadata={'label': label}
            )

            self._snapshots.append(snapshot)
            return snapshot

    @contextmanager
    def profile_operation(self, operation_name: str):
        """Context manager for profiling a specific operation.

        Args:
            operation_name: Name of the operation being profiled.

        Yields:
            The memory profiler instance for additional tracking.

        """
        before_snapshot = self.take_snapshot(f"{operation_name}_before")

        try:
            yield self
        finally:
            after_snapshot = self.take_snapshot(f"{operation_name}_after")
            delta = after_snapshot.compare_to(before_snapshot)
            self._operation_profiles[operation_name].append(delta)

    def track_object(self, obj: Any) -> None:
        """Track a specific object for memory profiling.

        Args:
            obj: Object to track for lifecycle and reference counting.

        """
        with self._lock:
            self._tracked_objects.add(id(obj))

            if self.track_weakrefs:
                try:
                    weak_ref = weakref.ref(obj)
                    self._weakrefs.append(weak_ref)
                except TypeError:
                    # Object doesn't support weak references
                    pass

    def track_widget_lifecycle(self, widget_factory: Callable[[], Any], count: int = 100) -> Dict[str, Any]:
        """Track widget creation and destruction lifecycle.

        Args:
            widget_factory: Function that creates widgets to track.
            count: Number of widgets to create and track.

        Returns:
            Dictionary with lifecycle statistics.

        """
        with self.profile_operation("widget_lifecycle"):
            # Create widgets and track them
            widgets = []
            for i in range(count):
                widget = widget_factory()
                self.track_object(widget)
                widgets.append(widget)

            created_snapshot = self.take_snapshot("widgets_created")

            # Simulate some theme operations
            for widget in widgets:
                if hasattr(widget, 'on_theme_changed'):
                    widget.on_theme_changed()

            operated_snapshot = self.take_snapshot("theme_operations_done")

            # Clear widgets and force cleanup
            widget_ids = [id(w) for w in widgets]
            widgets.clear()
            gc.collect()

            cleaned_snapshot = self.take_snapshot("widgets_cleaned")

            # Check how many objects are still alive
            live_objects = 0
            for obj_id in widget_ids:
                for obj in gc.get_objects():
                    if id(obj) == obj_id:
                        live_objects += 1
                        break

            return {
                'widgets_created': count,
                'widgets_still_alive': live_objects,
                'creation_memory_delta': operated_snapshot.compare_to(created_snapshot),
                'cleanup_memory_delta': cleaned_snapshot.compare_to(operated_snapshot),
                'total_memory_delta': cleaned_snapshot.compare_to(created_snapshot),
            }

    def detect_leaks(self, sensitivity: float = 1.0) -> List[str]:
        """Detect potential memory leaks from collected data.

        Args:
            sensitivity: Sensitivity for leak detection (1.0 = normal, higher = more sensitive).

        Returns:
            List of potential leak descriptions.

        """
        leaks = []

        if len(self._snapshots) < 2:
            return leaks

        # Compare latest snapshot to baseline or earliest snapshot
        baseline = self._baseline_snapshot or self._snapshots[0]
        latest = self._snapshots[-1]

        delta = latest.compare_to(baseline)

        # Adjust thresholds based on sensitivity
        memory_threshold = int(1024 / sensitivity)  # 1KB default
        object_threshold = int(10 / sensitivity)  # 10 objects default

        if delta.has_potential_leak(object_threshold, memory_threshold):
            leak_summary = delta.get_leak_summary()
            leaks.extend(leak_summary)

        # Check operation profiles for consistent leaks
        for operation_name, deltas in self._operation_profiles.items():
            if len(deltas) > 1:
                # Look for consistent memory growth across operations
                memory_deltas = [d.memory_delta for d in deltas]
                avg_growth = sum(memory_deltas) / len(memory_deltas)

                if avg_growth > memory_threshold:
                    leaks.append(
                        f"Operation '{operation_name}' shows consistent memory growth: "
                        f"avg +{avg_growth:.0f} bytes per operation"
                    )

        # Check for objects that should have been garbage collected
        dead_weakrefs = sum(1 for ref in self._weakrefs if ref() is None)
        live_weakrefs = len(self._weakrefs) - dead_weakrefs

        if live_weakrefs > len(self._tracked_objects) * 0.1:  # More than 10% still alive
            leaks.append(
                f"Potential object leak: {live_weakrefs} objects still referenced "
                f"out of {len(self._weakrefs)} tracked"
            )

        return leaks

    def validate_memory_requirements(self) -> bool:
        """Validate that memory usage meets system requirements.

        Returns:
            True if all memory requirements are met.

        """
        requirements = {
            'max_memory_per_widget': 1024,  # 1KB per widget
            'max_memory_growth_per_operation': 512,  # 512 bytes per operation
            'max_object_growth_per_operation': 5,  # 5 objects per operation
        }

        # Check memory per widget from operation profiles
        widget_operations = ['widget_creation', 'widget_lifecycle']
        for operation_name in widget_operations:
            if operation_name in self._operation_profiles:
                deltas = self._operation_profiles[operation_name]
                for delta in deltas:
                    avg_memory_per_widget = abs(delta.memory_delta) / max(1, abs(delta.tracked_objects_delta))
                    if avg_memory_per_widget > requirements['max_memory_per_widget']:
                        return False

        # Check memory growth per operation
        for operation_name, deltas in self._operation_profiles.items():
            for delta in deltas:
                if delta.memory_delta > requirements['max_memory_growth_per_operation']:
                    return False

                # Check object growth
                total_object_growth = sum(
                    count for count in delta.object_deltas.values() if count > 0
                )
                if total_object_growth > requirements['max_object_growth_per_operation']:
                    return False

        return True

    def set_baseline(self) -> MemorySnapshot:
        """Set current memory state as baseline for leak detection.

        Returns:
            Baseline snapshot.

        """
        self._baseline_snapshot = self.take_snapshot("baseline")
        return self._baseline_snapshot

    def generate_report(self) -> str:
        """Generate comprehensive memory usage report.

        Returns:
            Formatted string report of memory analysis.

        """
        if not self._snapshots:
            return "No memory snapshots available."

        report_lines = [
            "VFWidgets Theme System Memory Report",
            "=" * 50,
            "",
        ]

        # Overall statistics
        first_snapshot = self._snapshots[0]
        last_snapshot = self._snapshots[-1]
        overall_delta = last_snapshot.compare_to(first_snapshot)

        report_lines.extend([
            f"Time Period: {overall_delta.time_delta:.2f} seconds",
            f"Total Memory Change: {overall_delta.memory_delta:+} bytes",
            f"Peak Memory Change: {overall_delta.peak_delta:+} bytes",
            f"Tracked Objects Change: {overall_delta.tracked_objects_delta:+}",
            f"WeakRef Count Change: {overall_delta.weakref_delta:+}",
            "",
        ])

        # Object type changes
        if overall_delta.object_deltas:
            report_lines.extend([
                "Object Count Changes:",
                "-" * 25,
            ])

            for obj_type, delta in sorted(overall_delta.object_deltas.items()):
                if delta != 0:
                    report_lines.append(f"  {obj_type}: {delta:+}")

            report_lines.append("")

        # Operation profiles
        if self._operation_profiles:
            report_lines.extend([
                "Operation Memory Profiles:",
                "-" * 30,
            ])

            for operation_name, deltas in self._operation_profiles.items():
                if deltas:
                    avg_memory = sum(d.memory_delta for d in deltas) / len(deltas)
                    avg_objects = sum(
                        sum(d.object_deltas.values()) for d in deltas
                    ) / len(deltas)

                    report_lines.extend([
                        f"  {operation_name}:",
                        f"    Executions: {len(deltas)}",
                        f"    Avg Memory Delta: {avg_memory:+.0f} bytes",
                        f"    Avg Object Delta: {avg_objects:+.0f}",
                        "",
                    ])

        # Leak detection results
        leaks = self.detect_leaks()
        if leaks:
            report_lines.extend([
                "Potential Memory Leaks:",
                "-" * 25,
            ])
            for leak in leaks:
                report_lines.append(f"  ⚠️  {leak}")
            report_lines.append("")
        else:
            report_lines.extend([
                "Memory Leak Detection: ✓ CLEAN",
                "",
            ])

        # Requirements validation
        meets_requirements = self.validate_memory_requirements()
        report_lines.extend([
            f"Memory Requirements: {'✓ PASS' if meets_requirements else '✗ FAIL'}",
            "",
        ])

        # Live object summary
        live_weakrefs = sum(1 for ref in self._weakrefs if ref() is not None)
        report_lines.extend([
            f"Live Tracked Objects: {live_weakrefs}/{len(self._weakrefs)}",
            "=" * 50,
        ])

        return "\n".join(report_lines)

    def cleanup(self) -> None:
        """Clean up profiler resources."""
        with self._lock:
            self._snapshots.clear()
            self._tracked_objects.clear()
            self._weakrefs.clear()
            self._operation_profiles.clear()
            self._baseline_snapshot = None

        # Stop tracemalloc if we started it
        if tracemalloc.is_tracing():
            tracemalloc.stop()


# Convenience functions for common memory testing patterns

def detect_memory_leaks(operation: Callable[[], None], iterations: int = 100) -> List[str]:
    """Detect memory leaks in a repeated operation.

    Args:
        operation: Function to test for memory leaks.
        iterations: Number of times to repeat the operation.

    Returns:
        List of potential leak descriptions.

    """
    profiler = MemoryProfiler()

    try:
        profiler.set_baseline()

        for i in range(iterations):
            with profiler.profile_operation(f"iteration_{i}"):
                operation()

        return profiler.detect_leaks()

    finally:
        profiler.cleanup()


def track_widget_lifecycle(widget_factory: Callable[[], Any], count: int = 100) -> Dict[str, Any]:
    """Track widget creation and cleanup lifecycle.

    Args:
        widget_factory: Function that creates widgets.
        count: Number of widgets to create and track.

    Returns:
        Dictionary with lifecycle statistics.

    """
    profiler = MemoryProfiler()

    try:
        return profiler.track_widget_lifecycle(widget_factory, count)
    finally:
        profiler.cleanup()


def validate_memory_requirements(test_function: Callable[[], None]) -> bool:
    """Validate that a test function meets memory requirements.

    Args:
        test_function: Function to validate memory usage for.

    Returns:
        True if memory requirements are met.

    """
    profiler = MemoryProfiler()

    try:
        with profiler.profile_operation("validation"):
            test_function()

        return profiler.validate_memory_requirements()

    finally:
        profiler.cleanup()


# Memory testing decorators

def memory_leak_test(iterations: int = 100, max_leaks: int = 0):
    """Decorator for memory leak testing.

    Args:
        iterations: Number of iterations to run.
        max_leaks: Maximum allowed number of potential leaks.

    Example:
        @memory_leak_test(iterations=1000, max_leaks=0)
        def test_no_memory_leaks():
            widget = create_themed_widget()
            widget.on_theme_changed()

    """
    def decorator(test_func):
        def wrapper(*args, **kwargs):
            def test_operation():
                return test_func(*args, **kwargs)

            leaks = detect_memory_leaks(test_operation, iterations)
            assert len(leaks) <= max_leaks, (
                f"Memory leaks detected in {test_func.__name__}: {leaks}"
            )

        return wrapper
    return decorator


def widget_lifecycle_test(widget_count: int = 100, max_alive_percent: float = 10.0):
    """Decorator for widget lifecycle testing.

    Args:
        widget_count: Number of widgets to create in test.
        max_alive_percent: Maximum percentage of widgets allowed to remain alive.

    Example:
        @widget_lifecycle_test(widget_count=1000, max_alive_percent=5.0)
        def test_widget_cleanup():
            return MockWidget()  # Return widget factory

    """
    def decorator(test_func):
        def wrapper(*args, **kwargs):
            widget_factory = lambda: test_func(*args, **kwargs)
            stats = track_widget_lifecycle(widget_factory, widget_count)

            alive_percent = (stats['widgets_still_alive'] / widget_count) * 100
            assert alive_percent <= max_alive_percent, (
                f"Too many widgets still alive in {test_func.__name__}: "
                f"{alive_percent:.1f}% (max {max_alive_percent}%)"
            )

        return wrapper
    return decorator
