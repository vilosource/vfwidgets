#!/usr/bin/env python3
"""
Simple Benchmark Test to verify framework works
"""

import sys
import time
from pathlib import Path

from PySide6.QtWidgets import QApplication

# Ensure QApplication exists before importing our modules
if not QApplication.instance():
    app = QApplication(sys.argv)

from suite import BenchmarkSuite


def test_simple_benchmarks():
    """Simple benchmark test."""
    print("Testing Benchmark Suite...")

    # Create benchmark suite with temporary directory
    temp_dir = Path("/tmp/benchmark_test")
    suite = BenchmarkSuite(results_dir=temp_dir)

    print("Suite initialized")

    # Test simple property access benchmark
    print("\nRunning property access benchmark...")
    result1 = suite.bench_property_access()
    print(f"Property access: {result1.mean_time * 1000:.2f}ms average")

    # Test widget creation benchmark
    print("\nRunning widget creation benchmark...")
    result2 = suite.bench_widget_creation()
    print(f"Widget creation: {result2.mean_time * 1000:.2f}ms average")

    # Test QSS generation benchmark
    print("\nRunning QSS generation benchmark...")
    result3 = suite.bench_qss_generation()
    print(f"QSS generation: {result3.mean_time * 1000:.2f}ms average")

    # Generate report
    report = suite.generate_report()
    print("\nBenchmark Report:")
    print(f"Total benchmarks: {report['total_benchmarks']}")
    print(f"Total time: {report['total_time']:.3f}s")

    # Check performance validation
    validation = report["performance_validation"]
    print(f"Performance validation: {'PASS' if validation['overall_pass'] else 'FAIL'}")

    if validation["failed"]:
        print("Failed benchmarks:")
        for failure in validation["failed"]:
            print(
                f"  {failure['benchmark']}: {failure['actual'] * 1000:.2f}ms > {failure['requirement'] * 1000:.2f}ms"
            )

    if validation["passed"]:
        print("Passed benchmarks:")
        for passed in validation["passed"]:
            print(
                f"  {passed['benchmark']}: {passed['actual'] * 1000:.2f}ms < {passed['requirement'] * 1000:.2f}ms"
            )

    print(f"Results saved to: {suite.results_db}")
    return True


def test_regression_detection():
    """Test regression detection."""
    print("\nTesting regression detection...")

    temp_dir = Path("/tmp/benchmark_regression_test")
    suite = BenchmarkSuite(results_dir=temp_dir)

    # Run same benchmark multiple times with different performance
    @suite.benchmark("test_regression", iterations=10, warmup=2)
    def slow_benchmark():
        time.sleep(0.001)  # 1ms sleep

    @suite.benchmark("test_regression", iterations=10, warmup=2)
    def slower_benchmark():
        time.sleep(0.002)  # 2ms sleep (regression)

    # Run benchmarks
    slow_benchmark()
    slower_benchmark()

    # Check for regressions
    regressions = suite.detect_regressions(threshold=0.1)  # 10% threshold
    print(f"Detected {len(regressions)} regressions")

    for regression in regressions:
        print(
            f"  {regression['name']}: {regression['current_time'] * 1000:.2f}ms vs {regression['baseline_time'] * 1000:.2f}ms "
            f"({regression['threshold_exceeded']:.1f}% slower)"
        )

    return len(regressions) > 0


if __name__ == "__main__":
    try:
        print("=" * 60)
        print("VFWidgets Theme System - Benchmark Suite Test")
        print("=" * 60)

        # Test basic benchmarks
        success1 = test_simple_benchmarks()

        # Test regression detection
        success2 = test_regression_detection()

        if success1:
            print("\n✅ Benchmark suite test PASSED")
        else:
            print("\n❌ Benchmark suite test FAILED")

        if success2:
            print("✅ Regression detection WORKS")
        else:
            print("❌ Regression detection FAILED")

    except Exception as e:
        print(f"\n❌ Benchmark test ERROR: {e}")
        import traceback

        traceback.print_exc()
