"""
Performance benchmarking framework for VFWidgets Theme System.

This module provides comprehensive performance testing and validation tools
to ensure all components meet the strict performance requirements defined
in the protocols. All benchmarks are designed to validate real-world usage
patterns and catch performance regressions early.

Key Performance Requirements:
- Theme Switch: < 100ms for 100 widgets
- Property Access: < 1μs
- Memory Overhead: < 1KB per widget
- Cache Hit Rate: > 90%
- Callback Registration: < 10μs
- Style Generation: < 10ms

Philosophy: Performance is not optional. Every component must meet these
requirements or the theme system fails to provide the "ThemedWidget is THE way"
experience we promise to developers.
"""

import gc
import time
import statistics
import tracemalloc
from typing import Dict, List, Any, Callable, Optional, Tuple, Union
from dataclasses import dataclass, field
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


@dataclass
class BenchmarkResult:
    """Results from a performance benchmark.

    Contains comprehensive timing and performance statistics
    for analysis and validation against requirements.
    """
    operation_name: str
    total_time: float
    iterations: int
    min_time: float
    max_time: float
    average_time: float
    median_time: float
    p95_time: float
    p99_time: float
    operations_per_second: float
    memory_usage_bytes: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate as percentage."""
        total_requests = self.cache_hits + self.cache_misses
        if total_requests == 0:
            return 0.0
        return (self.cache_hits / total_requests) * 100.0

    def meets_requirements(self, requirements: Dict[str, float]) -> bool:
        """Check if benchmark results meet performance requirements.

        Args:
            requirements: Dictionary of requirement thresholds.

        Returns:
            True if all applicable requirements are met.
        """
        operation_type = self.operation_name.lower().replace(' ', '_')

        # Check timing requirements
        timing_map = {
            'theme_switch': 'theme_switch_time',
            'property_access': 'property_access_time',
            'callback_registration': 'callback_registration_time',
            'style_generation': 'style_generation_time',
        }

        for pattern, req_key in timing_map.items():
            if pattern in operation_type and req_key in requirements:
                if self.average_time > requirements[req_key]:
                    self.errors.append(
                        f"Average time {self.average_time:.6f}s exceeds "
                        f"requirement {requirements[req_key]:.6f}s"
                    )
                    return False

        # Check memory requirements
        if 'memory_overhead_per_widget' in requirements:
            max_memory = requirements['memory_overhead_per_widget']
            if self.memory_usage_bytes > max_memory:
                self.errors.append(
                    f"Memory usage {self.memory_usage_bytes} bytes exceeds "
                    f"requirement {max_memory} bytes"
                )
                return False

        # Check cache hit rate
        if 'cache_hit_rate' in requirements:
            min_hit_rate = requirements['cache_hit_rate'] * 100  # Convert to percentage
            if self.cache_hit_rate < min_hit_rate:
                self.errors.append(
                    f"Cache hit rate {self.cache_hit_rate:.1f}% below "
                    f"requirement {min_hit_rate:.1f}%"
                )
                return False

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert benchmark result to dictionary for serialization."""
        return {
            'operation_name': self.operation_name,
            'total_time': self.total_time,
            'iterations': self.iterations,
            'min_time': self.min_time,
            'max_time': self.max_time,
            'average_time': self.average_time,
            'median_time': self.median_time,
            'p95_time': self.p95_time,
            'p99_time': self.p99_time,
            'operations_per_second': self.operations_per_second,
            'memory_usage_bytes': self.memory_usage_bytes,
            'cache_hit_rate': self.cache_hit_rate,
            'errors': self.errors,
            'warnings': self.warnings,
            'metadata': self.metadata,
        }


class ThemeBenchmark:
    """Comprehensive benchmarking framework for theme system performance.

    Provides standardized benchmarking methods for all theme system operations
    with built-in validation against performance requirements.

    Example:
        benchmark = ThemeBenchmark()

        # Test theme switching performance
        widgets = [MockWidget() for _ in range(100)]
        result = benchmark.benchmark_theme_switch(widgets, iterations=50)
        assert result.meets_requirements(PERFORMANCE_REQUIREMENTS)

        # Test property access performance
        provider = MockThemeProvider()
        result = benchmark.benchmark_property_access(provider, iterations=1000)
        assert result.average_time < 0.000001  # < 1μs
    """

    def __init__(self, enable_memory_tracking: bool = True):
        """Initialize benchmark framework.

        Args:
            enable_memory_tracking: Whether to track memory usage during benchmarks.
        """
        self.enable_memory_tracking = enable_memory_tracking
        self._results: List[BenchmarkResult] = []
        self._performance_requirements = {
            'theme_switch_time': 0.1,  # 100ms for 100 widgets
            'property_access_time': 0.000001,  # 1μs
            'memory_overhead_per_widget': 1024,  # 1KB
            'cache_hit_rate': 0.9,  # 90%
            'callback_registration_time': 0.00001,  # 10μs
            'style_generation_time': 0.01,  # 10ms
        }

    @contextmanager
    def _measure_performance(self, operation_name: str):
        """Context manager for measuring operation performance.

        Args:
            operation_name: Name of the operation being measured.

        Yields:
            Dictionary to store measurement data.
        """
        measurement_data = {
            'times': [],
            'memory_start': 0,
            'memory_peak': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'errors': [],
            'warnings': [],
        }

        # Start memory tracking
        if self.enable_memory_tracking:
            tracemalloc.start()
            measurement_data['memory_start'] = tracemalloc.get_traced_memory()[0]

        gc.collect()  # Clean slate for memory measurements

        try:
            yield measurement_data
        finally:
            # Stop memory tracking
            if self.enable_memory_tracking:
                current, peak = tracemalloc.get_traced_memory()
                measurement_data['memory_peak'] = peak - measurement_data['memory_start']
                tracemalloc.stop()

    def benchmark_theme_switch(
        self,
        widgets: List[Any],
        iterations: int = 50,
        themes: Optional[List[str]] = None
    ) -> BenchmarkResult:
        """Benchmark theme switching performance across multiple widgets.

        Args:
            widgets: List of widgets to test theme switching on.
            iterations: Number of theme switch cycles to perform.
            themes: List of theme names to cycle through.

        Returns:
            BenchmarkResult with comprehensive timing statistics.
        """
        themes = themes or ['default', 'dark', 'light']
        operation_name = f"Theme Switch ({len(widgets)} widgets)"

        with self._measure_performance(operation_name) as data:
            for i in range(iterations):
                theme_name = themes[i % len(themes)]

                start_time = time.perf_counter()

                # Simulate theme switch by calling on_theme_changed on all widgets
                for widget in widgets:
                    try:
                        if hasattr(widget, 'on_theme_changed'):
                            widget.on_theme_changed()
                        elif hasattr(widget, 'setStyleSheet'):
                            # Simulate QSS update
                            widget.setStyleSheet(f"color: {theme_name};")
                    except Exception as e:
                        data['errors'].append(f"Widget update error: {str(e)}")

                end_time = time.perf_counter()
                data['times'].append(end_time - start_time)

                # Validate performance requirement during benchmark
                elapsed = end_time - start_time
                if elapsed > self._performance_requirements['theme_switch_time']:
                    data['warnings'].append(
                        f"Iteration {i} exceeded time limit: {elapsed:.3f}s"
                    )

        return self._create_benchmark_result(operation_name, data, iterations)

    def benchmark_property_access(
        self,
        provider: Any,
        properties: Optional[List[str]] = None,
        iterations: int = 1000
    ) -> BenchmarkResult:
        """Benchmark theme property access performance.

        Args:
            provider: Theme provider to test property access on.
            properties: List of property names to access.
            iterations: Number of property access operations per property.

        Returns:
            BenchmarkResult with property access timing statistics.
        """
        properties = properties or [
            'primary_color', 'background', 'foreground', 'font_size', 'border_radius'
        ]
        operation_name = f"Property Access ({len(properties)} properties)"

        with self._measure_performance(operation_name) as data:
            for prop in properties:
                for i in range(iterations):
                    start_time = time.perf_counter()

                    try:
                        value = provider.get_property(prop)
                        # Track cache statistics if available
                        if hasattr(provider, '_cache_hits'):
                            data['cache_hits'] += getattr(provider, '_cache_hits', 0)
                        if hasattr(provider, '_cache_misses'):
                            data['cache_misses'] += getattr(provider, '_cache_misses', 0)
                    except Exception as e:
                        data['errors'].append(f"Property access error for {prop}: {str(e)}")

                    end_time = time.perf_counter()
                    data['times'].append(end_time - start_time)

        total_operations = len(properties) * iterations
        return self._create_benchmark_result(operation_name, data, total_operations)

    def benchmark_memory_usage(
        self,
        widget_factory: Callable[[], Any],
        widget_count: int = 100,
        theme_switches: int = 10
    ) -> BenchmarkResult:
        """Benchmark memory usage during widget creation and theme switching.

        Args:
            widget_factory: Function that creates a themed widget.
            widget_count: Number of widgets to create.
            theme_switches: Number of theme switches to perform.

        Returns:
            BenchmarkResult with memory usage statistics.
        """
        operation_name = f"Memory Usage ({widget_count} widgets, {theme_switches} switches)"

        with self._measure_performance(operation_name) as data:
            widgets = []

            # Create widgets and measure memory growth
            for i in range(widget_count):
                start_time = time.perf_counter()

                try:
                    widget = widget_factory()
                    widgets.append(widget)
                except Exception as e:
                    data['errors'].append(f"Widget creation error: {str(e)}")

                end_time = time.perf_counter()
                data['times'].append(end_time - start_time)

            # Perform theme switches and measure memory stability
            for switch in range(theme_switches):
                switch_start = time.perf_counter()

                for widget in widgets:
                    try:
                        if hasattr(widget, 'on_theme_changed'):
                            widget.on_theme_changed()
                    except Exception as e:
                        data['errors'].append(f"Theme switch error: {str(e)}")

                switch_end = time.perf_counter()
                data['times'].append(switch_end - switch_start)

            # Clean up and measure memory release
            widgets.clear()
            gc.collect()

        total_operations = widget_count + theme_switches
        result = self._create_benchmark_result(operation_name, data, total_operations)

        # Calculate memory per widget
        if widget_count > 0:
            result.metadata['memory_per_widget'] = result.memory_usage_bytes / widget_count

        return result

    def benchmark_callback_registration(
        self,
        provider: Any,
        callback_count: int = 100,
        iterations: int = 10
    ) -> BenchmarkResult:
        """Benchmark callback registration and unregistration performance.

        Args:
            provider: Theme provider to test callback registration on.
            callback_count: Number of callbacks to register/unregister.
            iterations: Number of registration cycles to perform.

        Returns:
            BenchmarkResult with callback registration timing statistics.
        """
        operation_name = f"Callback Registration ({callback_count} callbacks)"

        def dummy_callback(theme_name: str):
            pass

        with self._measure_performance(operation_name) as data:
            for iteration in range(iterations):
                callbacks = []

                # Registration phase
                for i in range(callback_count):
                    callback = lambda name, i=i: None  # Unique callback per iteration

                    start_time = time.perf_counter()
                    try:
                        provider.subscribe(callback)
                        callbacks.append(callback)
                    except Exception as e:
                        data['errors'].append(f"Callback registration error: {str(e)}")
                    end_time = time.perf_counter()

                    data['times'].append(end_time - start_time)

                # Unregistration phase
                for callback in callbacks:
                    start_time = time.perf_counter()
                    try:
                        provider.unsubscribe(callback)
                    except Exception as e:
                        data['errors'].append(f"Callback unregistration error: {str(e)}")
                    end_time = time.perf_counter()

                    data['times'].append(end_time - start_time)

        total_operations = callback_count * iterations * 2  # registration + unregistration
        return self._create_benchmark_result(operation_name, data, total_operations)

    def benchmark_style_generation(
        self,
        generator: Any,
        theme_data: Dict[str, Any],
        widget_types: Optional[List[str]] = None,
        iterations: int = 100
    ) -> BenchmarkResult:
        """Benchmark QSS style generation performance.

        Args:
            generator: Style generator to test.
            theme_data: Theme data to generate styles from.
            widget_types: List of widget types to generate styles for.
            iterations: Number of style generation operations per widget type.

        Returns:
            BenchmarkResult with style generation timing statistics.
        """
        widget_types = widget_types or ['button', 'label', 'edit', 'text', 'combo']
        operation_name = f"Style Generation ({len(widget_types)} widget types)"

        # Create mock widgets for each type
        from .mocks import MockWidget
        widgets = [MockWidget(widget_type) for widget_type in widget_types]

        with self._measure_performance(operation_name) as data:
            for widget in widgets:
                for i in range(iterations):
                    start_time = time.perf_counter()

                    try:
                        stylesheet = generator.generate_stylesheet(theme_data, widget)
                        # Validate stylesheet is not empty
                        if not stylesheet.strip():
                            data['warnings'].append(f"Empty stylesheet generated for {widget.widget_type}")
                    except Exception as e:
                        data['errors'].append(f"Style generation error: {str(e)}")

                    end_time = time.perf_counter()
                    data['times'].append(end_time - start_time)

        total_operations = len(widget_types) * iterations
        return self._create_benchmark_result(operation_name, data, total_operations)

    def benchmark_concurrent_access(
        self,
        provider: Any,
        thread_count: int = 10,
        operations_per_thread: int = 100
    ) -> BenchmarkResult:
        """Benchmark concurrent theme access performance.

        Args:
            provider: Theme provider to test concurrent access on.
            thread_count: Number of concurrent threads.
            operations_per_thread: Number of operations per thread.

        Returns:
            BenchmarkResult with concurrent access timing statistics.
        """
        operation_name = f"Concurrent Access ({thread_count} threads)"

        def worker_function(thread_id: int) -> List[float]:
            """Worker function for concurrent testing."""
            times = []
            properties = ['primary_color', 'background', 'foreground']

            for i in range(operations_per_thread):
                prop = properties[i % len(properties)]

                start_time = time.perf_counter()
                try:
                    value = provider.get_property(prop)
                except Exception:
                    pass  # Include error handling time
                end_time = time.perf_counter()

                times.append(end_time - start_time)

            return times

        with self._measure_performance(operation_name) as data:
            with ThreadPoolExecutor(max_workers=thread_count) as executor:
                futures = []

                # Submit all worker tasks
                start_time = time.perf_counter()
                for thread_id in range(thread_count):
                    future = executor.submit(worker_function, thread_id)
                    futures.append(future)

                # Collect results
                for future in as_completed(futures):
                    try:
                        thread_times = future.result()
                        data['times'].extend(thread_times)
                    except Exception as e:
                        data['errors'].append(f"Thread execution error: {str(e)}")

                end_time = time.perf_counter()

        total_operations = thread_count * operations_per_thread
        result = self._create_benchmark_result(operation_name, data, total_operations)
        result.metadata['thread_count'] = thread_count
        result.metadata['total_execution_time'] = end_time - start_time

        return result

    def _create_benchmark_result(
        self,
        operation_name: str,
        measurement_data: Dict[str, Any],
        iterations: int
    ) -> BenchmarkResult:
        """Create a BenchmarkResult from measurement data.

        Args:
            operation_name: Name of the benchmarked operation.
            measurement_data: Raw measurement data.
            iterations: Number of iterations performed.

        Returns:
            Formatted BenchmarkResult instance.
        """
        times = measurement_data['times']

        if not times:
            # Handle case where no measurements were taken
            return BenchmarkResult(
                operation_name=operation_name,
                total_time=0.0,
                iterations=0,
                min_time=0.0,
                max_time=0.0,
                average_time=0.0,
                median_time=0.0,
                p95_time=0.0,
                p99_time=0.0,
                operations_per_second=0.0,
                memory_usage_bytes=measurement_data.get('memory_peak', 0),
                cache_hits=measurement_data.get('cache_hits', 0),
                cache_misses=measurement_data.get('cache_misses', 0),
                errors=measurement_data.get('errors', []),
                warnings=measurement_data.get('warnings', []),
            )

        total_time = sum(times)
        average_time = total_time / len(times)
        sorted_times = sorted(times)

        result = BenchmarkResult(
            operation_name=operation_name,
            total_time=total_time,
            iterations=len(times),
            min_time=min(times),
            max_time=max(times),
            average_time=average_time,
            median_time=statistics.median(times),
            p95_time=sorted_times[int(len(sorted_times) * 0.95)] if len(sorted_times) > 20 else max(times),
            p99_time=sorted_times[int(len(sorted_times) * 0.99)] if len(sorted_times) > 100 else max(times),
            operations_per_second=len(times) / total_time if total_time > 0 else 0,
            memory_usage_bytes=measurement_data.get('memory_peak', 0),
            cache_hits=measurement_data.get('cache_hits', 0),
            cache_misses=measurement_data.get('cache_misses', 0),
            errors=measurement_data.get('errors', []),
            warnings=measurement_data.get('warnings', []),
        )

        self._results.append(result)
        return result

    def get_all_results(self) -> List[BenchmarkResult]:
        """Get all benchmark results from this session."""
        return self._results.copy()

    def validate_all_requirements(self) -> bool:
        """Validate that all benchmark results meet performance requirements.

        Returns:
            True if all results meet requirements.
        """
        return all(result.meets_requirements(self._performance_requirements) for result in self._results)

    def generate_report(self) -> str:
        """Generate a comprehensive performance report.

        Returns:
            Formatted string report of all benchmark results.
        """
        if not self._results:
            return "No benchmark results available."

        report_lines = [
            "VFWidgets Theme System Performance Report",
            "=" * 50,
            "",
        ]

        for result in self._results:
            report_lines.extend([
                f"Operation: {result.operation_name}",
                f"Iterations: {result.iterations}",
                f"Average Time: {result.average_time:.6f}s",
                f"Min Time: {result.min_time:.6f}s",
                f"Max Time: {result.max_time:.6f}s",
                f"95th Percentile: {result.p95_time:.6f}s",
                f"Operations/Second: {result.operations_per_second:.0f}",
                f"Memory Usage: {result.memory_usage_bytes} bytes",
                f"Cache Hit Rate: {result.cache_hit_rate:.1f}%",
                ""
            ])

            if result.errors:
                report_lines.extend([
                    "Errors:",
                    *[f"  - {error}" for error in result.errors],
                    ""
                ])

            if result.warnings:
                report_lines.extend([
                    "Warnings:",
                    *[f"  - {warning}" for warning in result.warnings],
                    ""
                ])

            meets_reqs = result.meets_requirements(self._performance_requirements)
            report_lines.extend([
                f"Requirements Met: {'✓' if meets_reqs else '✗'}",
                "-" * 30,
                ""
            ])

        overall_pass = self.validate_all_requirements()
        report_lines.extend([
            f"Overall Performance: {'PASS' if overall_pass else 'FAIL'}",
            "=" * 50,
        ])

        return "\n".join(report_lines)


# Convenience functions for quick benchmarking

def benchmark_theme_switch(widgets: List[Any], iterations: int = 50) -> BenchmarkResult:
    """Quick benchmark for theme switching performance.

    Args:
        widgets: List of widgets to test.
        iterations: Number of iterations.

    Returns:
        BenchmarkResult with timing statistics.
    """
    benchmark = ThemeBenchmark()
    return benchmark.benchmark_theme_switch(widgets, iterations)


def benchmark_property_access(provider: Any, iterations: int = 1000) -> BenchmarkResult:
    """Quick benchmark for property access performance.

    Args:
        provider: Theme provider to test.
        iterations: Number of iterations per property.

    Returns:
        BenchmarkResult with timing statistics.
    """
    benchmark = ThemeBenchmark()
    return benchmark.benchmark_property_access(provider, iterations=iterations)


def benchmark_memory_usage(widget_factory: Callable[[], Any], widget_count: int = 100) -> BenchmarkResult:
    """Quick benchmark for memory usage.

    Args:
        widget_factory: Function that creates widgets.
        widget_count: Number of widgets to create.

    Returns:
        BenchmarkResult with memory statistics.
    """
    benchmark = ThemeBenchmark()
    return benchmark.benchmark_memory_usage(widget_factory, widget_count)


def validate_performance_requirements(results: List[BenchmarkResult]) -> Dict[str, bool]:
    """Validate benchmark results against performance requirements.

    Args:
        results: List of benchmark results to validate.

    Returns:
        Dictionary mapping requirement names to pass/fail status.
    """
    requirements = {
        'theme_switch_time': 0.1,
        'property_access_time': 0.000001,
        'memory_overhead_per_widget': 1024,
        'cache_hit_rate': 0.9,
        'callback_registration_time': 0.00001,
        'style_generation_time': 0.01,
    }

    validation_results = {}

    for req_name, threshold in requirements.items():
        validation_results[req_name] = all(
            result.meets_requirements({req_name: threshold})
            for result in results
        )

    return validation_results


# Performance testing decorators

def performance_test(max_time: float):
    """Decorator for marking performance test methods.

    Args:
        max_time: Maximum allowed execution time in seconds.

    Example:
        @performance_test(max_time=0.001)
        def test_fast_operation():
            # Test code here
            pass
    """
    def decorator(test_func):
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = test_func(*args, **kwargs)
            end_time = time.perf_counter()

            elapsed = end_time - start_time
            assert elapsed < max_time, (
                f"Test {test_func.__name__} took {elapsed:.6f}s, "
                f"expected < {max_time:.6f}s"
            )

            return result
        return wrapper
    return decorator


def memory_test(max_memory_mb: float):
    """Decorator for marking memory usage test methods.

    Args:
        max_memory_mb: Maximum allowed memory usage in megabytes.

    Example:
        @memory_test(max_memory_mb=10.0)
        def test_memory_efficient_operation():
            # Test code here
            pass
    """
    def decorator(test_func):
        def wrapper(*args, **kwargs):
            tracemalloc.start()
            result = test_func(*args, **kwargs)
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            peak_mb = peak / (1024 * 1024)
            assert peak_mb < max_memory_mb, (
                f"Test {test_func.__name__} used {peak_mb:.2f}MB, "
                f"expected < {max_memory_mb:.2f}MB"
            )

            return result
        return wrapper
    return decorator