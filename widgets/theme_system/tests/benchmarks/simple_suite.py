#!/usr/bin/env python3
"""
Simplified Benchmark Suite for VFWidgets Theme System
Task 23: Core performance benchmarking functionality
"""

import json
import statistics
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from PySide6.QtWidgets import QApplication

from vfwidgets_theme import ThemedApplication, ThemedWidget
from vfwidgets_theme.core.theme import Theme


@dataclass
class BenchmarkResult:
    """Result of a single benchmark."""
    name: str
    mean_time: float  # seconds
    iterations: int
    timestamp: datetime
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class SimpleBenchmarkSuite:
    """Simplified performance benchmarking suite."""

    def __init__(self, results_dir: Path = None):
        if results_dir is None:
            results_dir = Path("tests/benchmarks/results")

        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)

        self.results: List[BenchmarkResult] = []
        self.requirements = {
            'property_access': 0.000010,  # 10μs
            'widget_creation': 0.010,     # 10ms
            'theme_switching': 0.100,     # 100ms
        }

    def run_benchmark(self, name: str, func, iterations: int = 100) -> BenchmarkResult:
        """Run a benchmark function."""
        print(f"Running benchmark: {name} ({iterations} iterations)")

        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            func()
            end = time.perf_counter()
            times.append(end - start)

        mean_time = statistics.mean(times)

        result = BenchmarkResult(
            name=name,
            mean_time=mean_time,
            iterations=iterations,
            timestamp=datetime.now()
        )

        self.results.append(result)
        print(f"  Mean time: {mean_time*1000:.3f}ms")

        return result

    def bench_property_access(self) -> BenchmarkResult:
        """Benchmark theme property access."""
        theme = Theme(
            name="benchmark_theme",
            colors={"primary": "#007acc", "secondary": "#6f6f6f"},
            styles={"font_size": "12px", "margin": "4px"}
        )

        def benchmark_func():
            _ = theme.colors.get("primary")
            _ = theme.colors.get("secondary")
            _ = theme.styles.get("font_size")
            _ = theme.styles.get("margin")

        return self.run_benchmark("property_access", benchmark_func, 1000)

    def bench_widget_creation(self) -> BenchmarkResult:
        """Benchmark themed widget creation."""
        def benchmark_func():
            widget = ThemedWidget()
            widget.deleteLater()

        return self.run_benchmark("widget_creation", benchmark_func, 100)

    def bench_theme_switching(self) -> BenchmarkResult:
        """Benchmark theme switching."""
        app = QApplication.instance()
        if not app or not hasattr(app, 'set_theme'):
            print("Skipping theme switching benchmark - no themed application")
            return BenchmarkResult(
                name="theme_switching",
                mean_time=0.0,
                iterations=0,
                timestamp=datetime.now()
            )

        def benchmark_func():
            theme = Theme(
                name=f"bench_theme_{time.time()}",
                colors={"primary": "#ff0000"}
            )
            app.set_theme(theme)

        return self.run_benchmark("theme_switching", benchmark_func, 50)

    def bench_qss_generation(self) -> BenchmarkResult:
        """Benchmark QSS style generation."""
        theme = Theme(
            name="qss_benchmark",
            colors={
                "background": "#ffffff",
                "foreground": "#000000",
                "primary": "#007acc"
            },
            styles={
                "font_family": "Arial",
                "font_size": "12px",
                "padding": "8px"
            }
        )

        def benchmark_func():
            # Simulate QSS generation
            qss_parts = []
            for color_name, color_value in theme.colors.items():
                qss_parts.append(f"color: {color_value};")

            for style_name, style_value in theme.styles.items():
                if style_name == "font_family":
                    qss_parts.append(f"font-family: {style_value};")
                elif style_name == "font_size":
                    qss_parts.append(f"font-size: {style_value};")

            qss = " ".join(qss_parts)
            return qss

        return self.run_benchmark("qss_generation", benchmark_func, 200)

    def run_all_benchmarks(self) -> List[BenchmarkResult]:
        """Run all benchmarks."""
        print("Running all benchmarks...")
        print("=" * 50)

        results = []
        try:
            results.append(self.bench_property_access())
        except Exception as e:
            print(f"Property access benchmark failed: {e}")

        try:
            results.append(self.bench_widget_creation())
        except Exception as e:
            print(f"Widget creation benchmark failed: {e}")

        try:
            results.append(self.bench_theme_switching())
        except Exception as e:
            print(f"Theme switching benchmark failed: {e}")

        try:
            results.append(self.bench_qss_generation())
        except Exception as e:
            print(f"QSS generation benchmark failed: {e}")

        print("=" * 50)
        print("Benchmarks completed!")
        return results

    def validate_performance(self) -> Dict[str, Any]:
        """Validate performance against requirements."""
        validation = {
            'passed': [],
            'failed': [],
            'overall_pass': True
        }

        for result in self.results:
            if result.name in self.requirements:
                requirement = self.requirements[result.name]

                if result.mean_time <= requirement:
                    validation['passed'].append({
                        'benchmark': result.name,
                        'actual_ms': result.mean_time * 1000,
                        'requirement_ms': requirement * 1000,
                        'margin_ms': (requirement - result.mean_time) * 1000
                    })
                else:
                    validation['failed'].append({
                        'benchmark': result.name,
                        'actual_ms': result.mean_time * 1000,
                        'requirement_ms': requirement * 1000,
                        'excess_ms': (result.mean_time - requirement) * 1000
                    })
                    validation['overall_pass'] = False

        return validation

    def generate_report(self) -> Dict[str, Any]:
        """Generate performance report."""
        if not self.results:
            return {'error': 'No benchmark results available'}

        validation = self.validate_performance()

        return {
            'timestamp': datetime.now().isoformat(),
            'total_benchmarks': len(self.results),
            'validation': validation,
            'results': [
                {
                    'name': r.name,
                    'mean_time_ms': r.mean_time * 1000,
                    'iterations': r.iterations,
                    'timestamp': r.timestamp.isoformat()
                }
                for r in self.results
            ]
        }

    def save_report(self, filename: str = None) -> Path:
        """Save report to file."""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"benchmark_report_{timestamp}.json"

        report_path = self.results_dir / filename
        report = self.generate_report()

        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        return report_path


if __name__ == "__main__":
    # Example usage

    # Ensure QApplication exists
    if not QApplication.instance():
        app = ThemedApplication()

    # Run benchmarks
    suite = SimpleBenchmarkSuite()
    results = suite.run_all_benchmarks()

    # Generate and display report
    report = suite.generate_report()
    print("\nPerformance Report:")
    print(f"Total benchmarks: {report['total_benchmarks']}")

    validation = report['validation']
    print(f"Validation: {'PASS' if validation['overall_pass'] else 'FAIL'}")

    if validation['passed']:
        print("\nPassed benchmarks:")
        for passed in validation['passed']:
            print(f"  ✅ {passed['benchmark']}: {passed['actual_ms']:.2f}ms "
                  f"(< {passed['requirement_ms']:.2f}ms)")

    if validation['failed']:
        print("\nFailed benchmarks:")
        for failed in validation['failed']:
            print(f"  ❌ {failed['benchmark']}: {failed['actual_ms']:.2f}ms "
                  f"(> {failed['requirement_ms']:.2f}ms)")

    # Save report
    report_path = suite.save_report()
    print(f"\nReport saved to: {report_path}")
