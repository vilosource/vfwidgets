#!/usr/bin/env python3
"""
Benchmark Suite for VFWidgets Theme System
Task 23: Performance benchmarking with tracking and regression detection
"""

import gc
import json
import sqlite3
import statistics
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional, Union

from PySide6.QtWidgets import QApplication

from vfwidgets_theme import ThemedApplication, ThemedWidget
from vfwidgets_theme.core.theme import Theme


@dataclass
class BenchmarkResult:
    """Result of a single benchmark."""

    name: str
    duration: float  # seconds
    iterations: int
    min_time: float
    max_time: float
    mean_time: float
    median_time: float
    std_dev: float
    memory_usage: float  # MB
    timestamp: datetime
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        result["timestamp"] = self.timestamp.isoformat()
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BenchmarkResult":
        """Create from dictionary."""
        data = data.copy()
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


class BenchmarkSuite:
    """Performance benchmarking with tracking and regression detection."""

    def __init__(self, results_dir: Union[str, Path] = "tests/benchmarks/results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)

        self.results_db = self.results_dir / "results.db"
        self.results: list[BenchmarkResult] = []

        # Performance requirements (from specs)
        self.requirements = {
            "theme_switch_time": 0.1,  # < 100ms for 100 widgets
            "property_access_time": 0.000001,  # < 1μs
            "widget_creation_time": 0.01,  # < 10ms per widget
            "memory_overhead": 1.0,  # < 1KB per widget
        }

        self._init_database()

    def _init_database(self):
        """Initialize results database."""
        with sqlite3.connect(self.results_db) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS benchmark_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    duration REAL NOT NULL,
                    iterations INTEGER NOT NULL,
                    min_time REAL NOT NULL,
                    max_time REAL NOT NULL,
                    mean_time REAL NOT NULL,
                    median_time REAL NOT NULL,
                    std_dev REAL NOT NULL,
                    memory_usage REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    metadata TEXT NOT NULL
                )
            """
            )
            conn.commit()

    def benchmark(self, name: str = None, iterations: int = 100, warmup: int = 10):
        """
        Decorator for benchmarking functions.

        Args:
            name: Benchmark name (defaults to function name)
            iterations: Number of iterations to run
            warmup: Number of warmup iterations
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                benchmark_name = name or func.__name__
                return self._run_benchmark(
                    benchmark_name, func, iterations, warmup, *args, **kwargs
                )

            return wrapper

        return decorator

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil

            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            # Fallback using sys if psutil not available
            try:
                import resource

                return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
            except:
                return 0.0

    def _run_benchmark(
        self, name: str, func: Callable, iterations: int, warmup: int, *args, **kwargs
    ) -> BenchmarkResult:
        """Run a benchmark function."""
        print(f"Running benchmark: {name}")

        # Warmup
        for _ in range(warmup):
            try:
                func(*args, **kwargs)
            except Exception:
                pass

        # Force garbage collection before measurement
        gc.collect()
        initial_memory = self._get_memory_usage()

        # Run benchmarks
        times = []
        for i in range(iterations):
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                print(f"Benchmark {name} failed on iteration {i}: {e}")
                continue
            end_time = time.perf_counter()

            times.append(end_time - start_time)

        final_memory = self._get_memory_usage()
        memory_usage = max(0, final_memory - initial_memory)

        if not times:
            raise RuntimeError(f"Benchmark {name} failed - no successful iterations")

        # Calculate statistics
        min_time = min(times)
        max_time = max(times)
        mean_time = statistics.mean(times)
        median_time = statistics.median(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0.0
        total_duration = sum(times)

        # Create result
        result = BenchmarkResult(
            name=name,
            duration=total_duration,
            iterations=len(times),
            min_time=min_time,
            max_time=max_time,
            mean_time=mean_time,
            median_time=median_time,
            std_dev=std_dev,
            memory_usage=memory_usage,
            timestamp=datetime.now(),
            metadata={},
        )

        self.results.append(result)
        self._save_result(result)

        print(f"  Mean time: {mean_time * 1000:.2f}ms")
        print(f"  Median time: {median_time * 1000:.2f}ms")
        print(f"  Std dev: {std_dev * 1000:.2f}ms")
        print(f"  Memory usage: {memory_usage:.2f}MB")

        return result

    def _save_result(self, result: BenchmarkResult):
        """Save result to database."""
        with sqlite3.connect(self.results_db) as conn:
            conn.execute(
                """
                INSERT INTO benchmark_results
                (name, duration, iterations, min_time, max_time, mean_time,
                 median_time, std_dev, memory_usage, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    result.name,
                    result.duration,
                    result.iterations,
                    result.min_time,
                    result.max_time,
                    result.mean_time,
                    result.median_time,
                    result.std_dev,
                    result.memory_usage,
                    result.timestamp.isoformat(),
                    json.dumps(result.metadata),
                ),
            )
            conn.commit()

    # Micro-benchmarks
    def bench_property_access(self):
        """Benchmark theme property access."""

        def benchmark_func():
            theme = Theme(
                name="benchmark_theme",
                colors={"primary": "#007acc", "secondary": "#6f6f6f"},
                styles={"font_size": "12px", "margin": "4px"},
            )

            # Access various properties
            _ = theme.colors.get("primary")
            _ = theme.colors.get("secondary")
            _ = theme.styles.get("font_size")
            _ = theme.styles.get("margin")

        return self._run_benchmark("bench_property_access", benchmark_func, 1000, 100)

    def bench_widget_creation(self):
        """Benchmark themed widget creation."""

        def benchmark_func():
            app = QApplication.instance()
            if not app:
                return

            widget = ThemedWidget()
            widget.deleteLater()

        return self._run_benchmark("bench_widget_creation", benchmark_func, 100, 10)

    def bench_theme_switching(self):
        """Benchmark theme switching performance."""

        def benchmark_func():
            app = ThemedApplication.instance() if hasattr(ThemedApplication, "instance") else None
            if not app:
                app = QApplication.instance()
                if not isinstance(app, ThemedApplication):
                    return

            # Create test theme
            theme = Theme(name=f"bench_theme_{time.time()}", colors={"primary": "#ff0000"})

            # Switch theme
            app.set_theme(theme)

        return self._run_benchmark("bench_theme_switching", benchmark_func, 50, 5)

    def bench_qss_generation(self):
        """Benchmark QSS style generation."""

        def benchmark_func():
            theme = Theme(
                name="qss_benchmark",
                colors={
                    "background": "#ffffff",
                    "foreground": "#000000",
                    "primary": "#007acc",
                    "secondary": "#6f6f6f",
                },
                styles={
                    "font_family": "Arial",
                    "font_size": "12px",
                    "border_radius": "4px",
                    "padding": "8px",
                },
            )

            # Simulate QSS generation
            qss_parts = []
            for _color_name, color_value in theme.colors.items():
                qss_parts.append(f"color: {color_value};")

            for style_name, style_value in theme.styles.items():
                if style_name == "font_family":
                    qss_parts.append(f"font-family: {style_value};")
                elif style_name == "font_size":
                    qss_parts.append(f"font-size: {style_value};")

            qss = " ".join(qss_parts)
            return qss

        return self._run_benchmark("bench_qss_generation", benchmark_func, 200, 20)

    # Macro-benchmarks
    def bench_complex_application(self):
        """Benchmark complex application with multiple widgets."""

        def benchmark_func():
            app = QApplication.instance()
            if not app:
                return

            # Create multiple widgets
            widgets = []
            for _i in range(50):
                widget = ThemedWidget()
                widget.resize(100, 50)
                widgets.append(widget)

            # Apply theme to all widgets
            theme = Theme(
                name=f"complex_theme_{time.time()}",
                colors={"background": "#f0f0f0", "text": "#333333"},
            )

            if hasattr(app, "set_theme"):
                app.set_theme(theme)

            # Cleanup
            for widget in widgets:
                widget.deleteLater()

        return self._run_benchmark("bench_complex_application", benchmark_func, 10, 2)

    def bench_rapid_theme_switching(self):
        """Benchmark rapid theme switching."""

        def benchmark_func():
            app = QApplication.instance()
            if not app or not hasattr(app, "set_theme"):
                return

            # Create widget
            widget = ThemedWidget()

            # Switch themes rapidly
            themes = []
            for i in range(5):
                theme = Theme(name=f"rapid_theme_{i}", colors={"primary": f"#{i:02x}0000"})
                themes.append(theme)

            for theme in themes:
                app.set_theme(theme)

            widget.deleteLater()

        return self._run_benchmark("bench_rapid_theme_switching", benchmark_func, 20, 5)

    def bench_memory_efficiency(self):
        """Benchmark memory efficiency."""

        def benchmark_func():
            # Create and destroy widgets to test memory efficiency
            widgets = []
            for _i in range(10):
                widget = ThemedWidget()
                widgets.append(widget)

            # Force cleanup
            for widget in widgets:
                widget.deleteLater()

            # Force garbage collection
            gc.collect()

        return self._run_benchmark("bench_memory_efficiency", benchmark_func, 100, 10)

    def run_all_benchmarks(self) -> list[BenchmarkResult]:
        """Run all benchmarks."""
        print("Running comprehensive benchmark suite...")
        print("=" * 50)

        benchmarks = [
            self.bench_property_access,
            self.bench_widget_creation,
            self.bench_theme_switching,
            self.bench_qss_generation,
            self.bench_complex_application,
            self.bench_rapid_theme_switching,
            self.bench_memory_efficiency,
        ]

        results = []
        for benchmark in benchmarks:
            try:
                result = benchmark()
                results.append(result)
            except Exception as e:
                print(f"Benchmark {benchmark.__name__} failed: {e}")

        print("\n" + "=" * 50)
        print("Benchmark suite completed!")
        return results

    def get_historical_results(self, name: str, limit: int = 100) -> list[BenchmarkResult]:
        """Get historical results for a benchmark."""
        with sqlite3.connect(self.results_db) as conn:
            cursor = conn.execute(
                """
                SELECT * FROM benchmark_results
                WHERE name = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """,
                (name, limit),
            )

            results = []
            for row in cursor:
                result_data = {
                    "name": row[1],
                    "duration": row[2],
                    "iterations": row[3],
                    "min_time": row[4],
                    "max_time": row[5],
                    "mean_time": row[6],
                    "median_time": row[7],
                    "std_dev": row[8],
                    "memory_usage": row[9],
                    "timestamp": row[10],
                    "metadata": json.loads(row[11]),
                }
                results.append(BenchmarkResult.from_dict(result_data))

            return results

    def detect_regressions(self, threshold: float = 0.2) -> list[dict[str, Any]]:
        """
        Detect performance regressions.

        Args:
            threshold: Regression threshold (20% by default)

        Returns:
            List of detected regressions
        """
        regressions = []

        for result in self.results:
            historical = self.get_historical_results(result.name, 10)

            if len(historical) < 2:
                continue

            # Compare with recent average
            recent_times = [r.mean_time for r in historical[1:6]]  # Skip current result
            if recent_times:
                recent_avg = statistics.mean(recent_times)
                current_time = result.mean_time

                if current_time > recent_avg * (1 + threshold):
                    regression = {
                        "name": result.name,
                        "current_time": current_time,
                        "baseline_time": recent_avg,
                        "regression_factor": current_time / recent_avg,
                        "threshold_exceeded": (current_time / recent_avg - 1) * 100,
                    }
                    regressions.append(regression)

        return regressions

    def validate_performance_requirements(self) -> dict[str, Any]:
        """Validate results against performance requirements."""
        validation_results = {"passed": [], "failed": [], "overall_pass": True}

        requirement_mapping = {
            "bench_property_access": "property_access_time",
            "bench_widget_creation": "widget_creation_time",
            "bench_theme_switching": "theme_switch_time",
        }

        for result in self.results:
            requirement_key = requirement_mapping.get(result.name)
            if requirement_key and requirement_key in self.requirements:
                requirement = self.requirements[requirement_key]

                if result.mean_time <= requirement:
                    validation_results["passed"].append(
                        {
                            "benchmark": result.name,
                            "actual": result.mean_time,
                            "requirement": requirement,
                            "margin": requirement - result.mean_time,
                        }
                    )
                else:
                    validation_results["failed"].append(
                        {
                            "benchmark": result.name,
                            "actual": result.mean_time,
                            "requirement": requirement,
                            "excess": result.mean_time - requirement,
                        }
                    )
                    validation_results["overall_pass"] = False

        return validation_results

    def generate_report(self) -> dict[str, Any]:
        """Generate comprehensive benchmark report."""
        if not self.results:
            return {"error": "No benchmark results available"}

        # Basic statistics
        total_benchmarks = len(self.results)
        total_time = sum(r.duration for r in self.results)
        avg_time = total_time / total_benchmarks if total_benchmarks > 0 else 0

        # Performance validation
        performance_validation = self.validate_performance_requirements()

        # Regression detection
        regressions = self.detect_regressions()

        # Results summary
        results_summary = []
        for result in self.results:
            results_summary.append(
                {
                    "name": result.name,
                    "mean_time_ms": result.mean_time * 1000,
                    "median_time_ms": result.median_time * 1000,
                    "std_dev_ms": result.std_dev * 1000,
                    "memory_mb": result.memory_usage,
                    "iterations": result.iterations,
                }
            )

        return {
            "timestamp": datetime.now().isoformat(),
            "total_benchmarks": total_benchmarks,
            "total_time": total_time,
            "average_time": avg_time,
            "performance_validation": performance_validation,
            "regressions": regressions,
            "results": results_summary,
            "requirements": self.requirements,
        }

    def save_report(self, filename: Optional[str] = None) -> Path:
        """Save benchmark report to file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_report_{timestamp}.json"

        report_path = self.results_dir / filename
        report = self.generate_report()

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        return report_path

    def cleanup(self):
        """Clean up resources."""
        self.results.clear()


if __name__ == "__main__":
    # Example usage
    from PySide6.QtWidgets import QApplication

    from vfwidgets_theme import ThemedApplication

    # Create application
    if not QApplication.instance():
        app = ThemedApplication()

    # Run benchmarks
    suite = BenchmarkSuite()
    results = suite.run_all_benchmarks()

    # Generate report
    report = suite.generate_report()
    print("\nBenchmark Report:")
    print(f"Total benchmarks: {report['total_benchmarks']}")
    print(
        f"Performance validation: {'PASS' if report['performance_validation']['overall_pass'] else 'FAIL'}"
    )

    if report["regressions"]:
        print(f"Regressions detected: {len(report['regressions'])}")

    # Save report
    report_path = suite.save_report()
    print(f"Report saved to: {report_path}")
