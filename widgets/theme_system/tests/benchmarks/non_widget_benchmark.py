#!/usr/bin/env python3
"""
Non-Widget Benchmark Test - focuses on theme operations without Qt widgets
"""

import time
import statistics
import sys
from pathlib import Path

# Import only what we need
from vfwidgets_theme.core.theme import Theme


def run_theme_benchmarks():
    """Run benchmarks that don't require Qt widgets."""
    print("Running Theme System Benchmarks (Non-Widget)")
    print("=" * 60)

    results = {}

    # Benchmark 1: Theme Creation
    print("\n1. Theme Creation Benchmark")
    theme_create_times = []

    for i in range(100):
        start = time.perf_counter()
        theme = Theme(
            name=f"test_theme_{i}",
            colors={
                "primary": "#007acc",
                "secondary": "#6f6f6f",
                "background": "#ffffff",
                "foreground": "#000000"
            },
            styles={
                "font_family": "Arial",
                "font_size": "12px",
                "border_radius": "4px",
                "padding": "8px"
            }
        )
        end = time.perf_counter()
        theme_create_times.append(end - start)

    mean_create = statistics.mean(theme_create_times)
    results['theme_creation'] = mean_create
    print(f"   Mean theme creation time: {mean_create*1000:.3f}ms")

    # Benchmark 2: Property Access
    print("\n2. Property Access Benchmark")
    theme = Theme(
        name="property_test",
        colors={"primary": "#007acc", "secondary": "#6f6f6f"},
        styles={"font_size": "12px", "margin": "4px"}
    )

    property_times = []
    for i in range(1000):
        start = time.perf_counter()
        _ = theme.colors.get("primary")
        _ = theme.colors.get("secondary")
        _ = theme.styles.get("font_size")
        _ = theme.styles.get("margin")
        end = time.perf_counter()
        property_times.append(end - start)

    mean_property = statistics.mean(property_times)
    results['property_access'] = mean_property
    print(f"   Mean property access time: {mean_property*1000:.3f}ms")

    # Benchmark 3: Theme Comparison
    print("\n3. Theme Comparison Benchmark")
    theme1 = Theme(
        name="theme1",
        colors={"primary": "#007acc"},
        styles={"font_size": "12px"}
    )
    theme2 = Theme(
        name="theme2",
        colors={"primary": "#ff0000"},
        styles={"font_size": "12px"}
    )

    compare_times = []
    for i in range(500):
        start = time.perf_counter()
        # Simple comparison
        same_colors = theme1.colors == theme2.colors
        same_styles = theme1.styles == theme2.styles
        same_name = theme1.name == theme2.name
        end = time.perf_counter()
        compare_times.append(end - start)

    mean_compare = statistics.mean(compare_times)
    results['theme_comparison'] = mean_compare
    print(f"   Mean theme comparison time: {mean_compare*1000:.3f}ms")

    # Benchmark 4: QSS Generation Simulation
    print("\n4. QSS Generation Simulation Benchmark")
    qss_theme = Theme(
        name="qss_test",
        colors={
            "background": "#ffffff",
            "foreground": "#000000",
            "primary": "#007acc",
            "secondary": "#6f6f6f"
        },
        styles={
            "font_family": "Arial",
            "font_size": "12px",
            "border_radius": "4px",
            "padding": "8px"
        }
    )

    qss_times = []
    for i in range(200):
        start = time.perf_counter()

        # Simulate QSS generation
        qss_parts = []
        for color_name, color_value in qss_theme.colors.items():
            qss_parts.append(f"color: {color_value};")

        for style_name, style_value in qss_theme.styles.items():
            if style_name == "font_family":
                qss_parts.append(f"font-family: {style_value};")
            elif style_name == "font_size":
                qss_parts.append(f"font-size: {style_value};")
            elif style_name == "border_radius":
                qss_parts.append(f"border-radius: {style_value};")

        qss = " ".join(qss_parts)

        end = time.perf_counter()
        qss_times.append(end - start)

    mean_qss = statistics.mean(qss_times)
    results['qss_generation'] = mean_qss
    print(f"   Mean QSS generation time: {mean_qss*1000:.3f}ms")

    # Summary
    print("\n" + "=" * 60)
    print("BENCHMARK SUMMARY")
    print("=" * 60)

    requirements = {
        'theme_creation': 0.001,      # 1ms
        'property_access': 0.00001,   # 10μs
        'theme_comparison': 0.0001,   # 100μs
        'qss_generation': 0.001,      # 1ms
    }

    all_passed = True
    for benchmark_name, actual_time in results.items():
        requirement = requirements.get(benchmark_name, float('inf'))
        passed = actual_time <= requirement

        status = "PASS" if passed else "FAIL"
        print(f"{benchmark_name:20}: {actual_time*1000:8.3f}ms ({status})")

        if not passed:
            all_passed = False

    print("-" * 60)
    overall_status = "PASS" if all_passed else "FAIL"
    print(f"{'Overall Performance:':20} {overall_status:>14}")
    print("=" * 60)

    return results, all_passed


def run_stress_test():
    """Run a stress test on theme operations."""
    print("\nRunning Theme Stress Test (30 seconds)...")

    start_time = time.time()
    end_time = start_time + 30.0  # 30 seconds

    theme_count = 0
    property_accesses = 0
    errors = 0

    base_theme = Theme(
        name="stress_base",
        colors={"primary": "#007acc"},
        styles={"font_size": "12px"}
    )

    while time.time() < end_time:
        try:
            # Create themes
            theme = Theme(
                name=f"stress_theme_{theme_count}",
                colors={"primary": f"#{theme_count % 256:02x}0000"},
                styles={"font_size": f"{12 + theme_count % 10}px"}
            )
            theme_count += 1

            # Access properties
            for _ in range(10):
                _ = theme.colors.get("primary")
                _ = theme.styles.get("font_size")
                property_accesses += 1

        except Exception as e:
            errors += 1
            if errors > 100:
                print("Too many errors, stopping stress test")
                break

    duration = time.time() - start_time
    themes_per_second = theme_count / duration
    accesses_per_second = property_accesses / duration

    print(f"Stress test completed:")
    print(f"  Duration: {duration:.1f} seconds")
    print(f"  Themes created: {theme_count}")
    print(f"  Property accesses: {property_accesses}")
    print(f"  Errors: {errors}")
    print(f"  Themes per second: {themes_per_second:.1f}")
    print(f"  Accesses per second: {accesses_per_second:.0f}")

    return {
        'duration': duration,
        'themes_created': theme_count,
        'property_accesses': property_accesses,
        'errors': errors,
        'themes_per_second': themes_per_second,
        'accesses_per_second': accesses_per_second
    }


if __name__ == "__main__":
    try:
        # Run main benchmarks
        results, passed = run_theme_benchmarks()

        # Run stress test
        stress_results = run_stress_test()

        if passed:
            print("\n✅ All benchmarks PASSED")
        else:
            print("\n❌ Some benchmarks FAILED")

        print(f"\n📊 Stress test: {stress_results['themes_per_second']:.0f} themes/sec, "
              f"{stress_results['accesses_per_second']:.0f} accesses/sec")

    except Exception as e:
        print(f"\n❌ Benchmark ERROR: {e}")
        import traceback
        traceback.print_exc()