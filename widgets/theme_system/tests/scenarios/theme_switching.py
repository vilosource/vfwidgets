#!/usr/bin/env python3
"""
VFWidgets Theme System - Theme Switching Scenario
Task 25: Rapid theme switching under load testing

This scenario tests rapid theme switching capabilities and ensures
the system remains stable under heavy theme change loads.
"""

import random
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, List

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from vfwidgets_theme.core.theme import Theme
from vfwidgets_theme.validation import ValidationFramework, ValidationMode


class MockThemedApplication:
    """Mock themed application for testing."""

    def __init__(self):
        self.current_theme = None
        self.widgets = []
        self.theme_change_callbacks = []
        self.theme_history = []
        self.lock = threading.RLock()

    def set_theme(self, theme):
        """Set application theme."""
        with self.lock:
            self.current_theme = theme
            self.theme_history.append((time.time(), theme.name))

            # Apply theme to all widgets
            for widget in self.widgets:
                if hasattr(widget, 'apply_theme'):
                    widget.apply_theme(theme)

            # Call callbacks
            for callback in self.theme_change_callbacks:
                try:
                    callback(theme)
                except Exception as e:
                    print(f"Theme change callback error: {e}")

    def get_current_theme(self):
        """Get current theme."""
        return self.current_theme

    def add_widget(self, widget):
        """Add widget to application."""
        with self.lock:
            self.widgets.append(widget)
            if self.current_theme:
                widget.apply_theme(self.current_theme)

    def add_theme_change_callback(self, callback):
        """Add theme change callback."""
        self.theme_change_callbacks.append(callback)


class MockWidget:
    """Mock widget for theme switching tests."""

    def __init__(self, widget_id: str):
        self.widget_id = widget_id
        self.current_theme = None
        self.theme_application_count = 0
        self.last_theme_change = None
        self.lock = threading.Lock()

    def apply_theme(self, theme):
        """Apply theme to widget."""
        with self.lock:
            self.current_theme = theme
            self.theme_application_count += 1
            self.last_theme_change = time.time()

    def get_current_theme(self):
        """Get current theme."""
        return self.current_theme


class ThemeSwitchingScenario:
    """
    Test scenario for rapid theme switching under load.

    This scenario tests the system's ability to handle rapid theme changes
    across multiple widgets while maintaining stability and performance.
    """

    def __init__(self):
        self.app = MockThemedApplication()
        self.widgets = []
        self.themes = []
        self.validation_framework = ValidationFramework(ValidationMode.DEBUG)
        self.stress_test_running = False

    def setup_scenario(self, widget_count: int = 50) -> bool:
        """Set up the theme switching scenario."""
        try:
            # Create mock widgets
            for i in range(widget_count):
                widget = MockWidget(f"widget_{i}")
                self.widgets.append(widget)
                self.app.add_widget(widget)

            # Create test themes
            self.themes = self._create_switching_themes()

            print(f"Set up theme switching scenario with {len(self.widgets)} widgets and {len(self.themes)} themes")
            return True

        except Exception as e:
            print(f"Scenario setup failed: {e}")
            return False

    def _create_switching_themes(self) -> List[Theme]:
        """Create themes optimized for switching tests."""
        themes = [
            Theme(
                name="switch_theme_1",
                colors={
                    "primary": "#e74c3c",
                    "secondary": "#95a5a6",
                    "background": "#ecf0f1",
                    "text": "#2c3e50"
                },
                styles={
                    "font_family": "Arial",
                    "font_size": "12px",
                    "padding": "8px"
                }
            ),
            Theme(
                name="switch_theme_2",
                colors={
                    "primary": "#3498db",
                    "secondary": "#e67e22",
                    "background": "#34495e",
                    "text": "#ecf0f1"
                },
                styles={
                    "font_family": "Roboto",
                    "font_size": "14px",
                    "padding": "10px"
                }
            ),
            Theme(
                name="switch_theme_3",
                colors={
                    "primary": "#2ecc71",
                    "secondary": "#f39c12",
                    "background": "#1abc9c",
                    "text": "#ffffff"
                },
                styles={
                    "font_family": "Segoe UI",
                    "font_size": "13px",
                    "padding": "6px"
                }
            ),
            Theme(
                name="switch_theme_4",
                colors={
                    "primary": "#9b59b6",
                    "secondary": "#16a085",
                    "background": "#27ae60",
                    "text": "#f8c471"
                },
                styles={
                    "font_family": "Helvetica",
                    "font_size": "11px",
                    "padding": "12px"
                }
            ),
            Theme(
                name="switch_theme_5",
                colors={
                    "primary": "#f1c40f",
                    "secondary": "#e74c3c",
                    "background": "#8e44ad",
                    "text": "#ecf0f1"
                },
                styles={
                    "font_family": "Calibri",
                    "font_size": "15px",
                    "padding": "9px"
                }
            )
        ]
        return themes

    def test_sequential_switching(self, iterations: int = 20) -> Dict[str, Any]:
        """Test sequential theme switching performance."""
        results = {
            "iterations": iterations,
            "theme_count": len(self.themes),
            "widget_count": len(self.widgets),
            "switch_times": [],
            "total_time": 0.0,
            "average_switch_time": 0.0,
            "switches_per_second": 0.0,
            "errors": []
        }

        try:
            start_total = time.perf_counter()

            for i in range(iterations):
                theme = self.themes[i % len(self.themes)]

                start_switch = time.perf_counter()
                self.app.set_theme(theme)
                end_switch = time.perf_counter()

                switch_time = (end_switch - start_switch) * 1000  # Convert to ms
                results["switch_times"].append({
                    "iteration": i,
                    "theme_name": theme.name,
                    "duration_ms": switch_time
                })

                # Small delay to simulate real usage
                time.sleep(0.01)

            end_total = time.perf_counter()
            results["total_time"] = (end_total - start_total) * 1000

            # Calculate statistics
            if results["switch_times"]:
                switch_durations = [st["duration_ms"] for st in results["switch_times"]]
                results["average_switch_time"] = sum(switch_durations) / len(switch_durations)
                results["switches_per_second"] = iterations / ((end_total - start_total) or 0.001)

            print(f"Sequential switching: {iterations} switches in {results['total_time']:.2f}ms")
            print(f"Average switch time: {results['average_switch_time']:.2f}ms")

            return results

        except Exception as e:
            results["errors"].append(f"Sequential switching test failed: {e}")
            return results

    def test_rapid_switching(self, duration_seconds: int = 5) -> Dict[str, Any]:
        """Test rapid theme switching for a duration."""
        results = {
            "duration_seconds": duration_seconds,
            "total_switches": 0,
            "switches_per_second": 0.0,
            "failed_switches": 0,
            "theme_distribution": {},
            "errors": []
        }

        try:
            start_time = time.time()
            end_time = start_time + duration_seconds
            switch_count = 0
            failed_count = 0

            while time.time() < end_time:
                try:
                    # Pick random theme
                    theme = random.choice(self.themes)
                    self.app.set_theme(theme)
                    switch_count += 1

                    # Track theme distribution
                    theme_name = theme.name
                    results["theme_distribution"][theme_name] = (
                        results["theme_distribution"].get(theme_name, 0) + 1
                    )

                    # Small delay to prevent overwhelming
                    time.sleep(0.005)

                except Exception as e:
                    failed_count += 1
                    if failed_count < 5:  # Only log first few errors
                        results["errors"].append(f"Switch failed: {e}")

            actual_duration = time.time() - start_time
            results["total_switches"] = switch_count
            results["failed_switches"] = failed_count
            results["switches_per_second"] = switch_count / actual_duration

            print(f"Rapid switching: {switch_count} switches in {actual_duration:.2f}s")
            print(f"Rate: {results['switches_per_second']:.1f} switches/sec")

            return results

        except Exception as e:
            results["errors"].append(f"Rapid switching test failed: {e}")
            return results

    def test_concurrent_switching(self, thread_count: int = 3, operations_per_thread: int = 20) -> Dict[str, Any]:
        """Test concurrent theme switching from multiple threads."""
        results = {
            "thread_count": thread_count,
            "operations_per_thread": operations_per_thread,
            "total_operations": 0,
            "successful_operations": 0,
            "thread_results": [],
            "duration_ms": 0.0,
            "errors": []
        }

        try:
            start_time = time.perf_counter()
            threads = []
            thread_results = []

            def switching_worker(worker_id: int):
                """Worker thread for theme switching."""
                worker_result = {
                    "worker_id": worker_id,
                    "operations": 0,
                    "errors": []
                }

                for i in range(operations_per_thread):
                    try:
                        # Use different theme selection strategy per worker
                        if worker_id == 0:
                            theme = self.themes[i % len(self.themes)]  # Sequential
                        elif worker_id == 1:
                            theme = random.choice(self.themes)  # Random
                        else:
                            # Alternating between first and last theme
                            theme = self.themes[0 if i % 2 == 0 else -1]

                        self.app.set_theme(theme)
                        worker_result["operations"] += 1

                        # Small delay to create realistic concurrency
                        time.sleep(0.02)

                    except Exception as e:
                        worker_result["errors"].append(f"Operation {i}: {e}")

                thread_results.append(worker_result)

            # Start threads
            for i in range(thread_count):
                thread = threading.Thread(target=switching_worker, args=(i,))
                threads.append(thread)
                thread.start()

            # Wait for completion
            for thread in threads:
                thread.join()

            end_time = time.perf_counter()
            results["duration_ms"] = (end_time - start_time) * 1000

            # Aggregate results
            for worker_result in thread_results:
                results["successful_operations"] += worker_result["operations"]
                results["errors"].extend(worker_result["errors"])

            results["total_operations"] = thread_count * operations_per_thread
            results["thread_results"] = thread_results

            print(f"Concurrent switching: {results['successful_operations']}/{results['total_operations']} operations")
            print(f"Duration: {results['duration_ms']:.2f}ms")

            return results

        except Exception as e:
            results["errors"].append(f"Concurrent switching test failed: {e}")
            return results

    def test_theme_consistency(self) -> Dict[str, Any]:
        """Test that all widgets have consistent theme after switching."""
        results = {
            "widget_count": len(self.widgets),
            "consistent_widgets": 0,
            "inconsistent_widgets": 0,
            "current_theme": None,
            "widget_states": [],
            "consistency_check_passed": False
        }

        try:
            # Apply a specific theme
            test_theme = self.themes[0] if self.themes else None
            if not test_theme:
                results["error"] = "No themes available for consistency test"
                return results

            self.app.set_theme(test_theme)
            time.sleep(0.1)  # Allow theme application to complete

            # Check all widgets
            current_theme_name = test_theme.name
            results["current_theme"] = current_theme_name

            consistent_count = 0
            for widget in self.widgets:
                widget_theme = widget.get_current_theme()
                widget_state = {
                    "widget_id": widget.widget_id,
                    "has_theme": widget_theme is not None,
                    "theme_name": widget_theme.name if widget_theme else None,
                    "is_consistent": widget_theme and widget_theme.name == current_theme_name
                }

                results["widget_states"].append(widget_state)

                if widget_state["is_consistent"]:
                    consistent_count += 1

            results["consistent_widgets"] = consistent_count
            results["inconsistent_widgets"] = len(self.widgets) - consistent_count
            results["consistency_check_passed"] = results["inconsistent_widgets"] == 0

            print(f"Theme consistency: {consistent_count}/{len(self.widgets)} widgets consistent")

            return results

        except Exception as e:
            results["error"] = f"Consistency test failed: {e}"
            return results

    def test_stress_switching(self, duration_seconds: int = 10) -> Dict[str, Any]:
        """Stress test with extremely rapid theme switching."""
        results = {
            "duration_seconds": duration_seconds,
            "total_switches": 0,
            "max_switches_per_second": 0.0,
            "errors": [],
            "performance_degradation": False
        }

        try:
            self.stress_test_running = True
            start_time = time.time()
            switch_count = 0
            performance_samples = []

            while time.time() - start_time < duration_seconds and self.stress_test_running:
                sample_start = time.time()
                sample_switches = 0

                # Switch rapidly for 1 second samples
                sample_end = sample_start + 1.0
                while time.time() < sample_end and self.stress_test_running:
                    try:
                        theme = self.themes[switch_count % len(self.themes)]
                        self.app.set_theme(theme)
                        switch_count += 1
                        sample_switches += 1

                        # Minimal delay to prevent overwhelming
                        time.sleep(0.001)

                    except Exception as e:
                        if len(results["errors"]) < 10:  # Limit error logging
                            results["errors"].append(f"Stress switch failed: {e}")

                # Record performance sample
                performance_samples.append(sample_switches)

            results["total_switches"] = switch_count

            if performance_samples:
                results["max_switches_per_second"] = max(performance_samples)

                # Check for performance degradation
                if len(performance_samples) > 2:
                    early_avg = sum(performance_samples[:3]) / 3
                    late_avg = sum(performance_samples[-3:]) / 3
                    degradation_ratio = late_avg / early_avg if early_avg > 0 else 1.0
                    results["performance_degradation"] = degradation_ratio < 0.8  # >20% degradation

            print(f"Stress test: {switch_count} switches in {duration_seconds}s")
            print(f"Max rate: {results['max_switches_per_second']} switches/sec")

            return results

        except Exception as e:
            results["errors"].append(f"Stress test failed: {e}")
            return results

        finally:
            self.stress_test_running = False

    def run_full_scenario(self) -> Dict[str, Any]:
        """Run the complete theme switching scenario."""
        print("Running Theme Switching Scenario...")
        print("=" * 50)

        scenario_results = {
            "setup_success": False,
            "sequential_results": None,
            "rapid_results": None,
            "concurrent_results": None,
            "consistency_results": None,
            "stress_results": None,
            "overall_success": False,
            "summary": {}
        }

        try:
            # Setup
            if not self.setup_scenario():
                return scenario_results

            scenario_results["setup_success"] = True

            # Test sequential switching
            print("\n1. Testing sequential theme switching...")
            sequential_results = self.test_sequential_switching()
            scenario_results["sequential_results"] = sequential_results

            # Test rapid switching
            print("\n2. Testing rapid theme switching...")
            rapid_results = self.test_rapid_switching()
            scenario_results["rapid_results"] = rapid_results

            # Test concurrent switching
            print("\n3. Testing concurrent theme switching...")
            concurrent_results = self.test_concurrent_switching()
            scenario_results["concurrent_results"] = concurrent_results

            # Test consistency
            print("\n4. Testing theme consistency...")
            consistency_results = self.test_theme_consistency()
            scenario_results["consistency_results"] = consistency_results

            # Stress test
            print("\n5. Running stress test...")
            stress_results = self.test_stress_switching(duration_seconds=5)
            scenario_results["stress_results"] = stress_results

            # Evaluate overall success
            success_criteria = [
                scenario_results["setup_success"],
                not bool(sequential_results.get("errors", [])),
                rapid_results.get("switches_per_second", 0) > 10,  # At least 10 switches/sec
                concurrent_results.get("successful_operations", 0) > 0,
                consistency_results.get("consistency_check_passed", False),
                not stress_results.get("performance_degradation", True)
            ]

            scenario_results["overall_success"] = all(success_criteria)

            # Create summary
            scenario_results["summary"] = {
                "total_widgets": len(self.widgets),
                "total_themes": len(self.themes),
                "sequential_avg_time": sequential_results.get("average_switch_time", 0),
                "rapid_switch_rate": rapid_results.get("switches_per_second", 0),
                "concurrent_operations": concurrent_results.get("successful_operations", 0),
                "consistency_passed": consistency_results.get("consistency_check_passed", False),
                "stress_max_rate": stress_results.get("max_switches_per_second", 0)
            }

            return scenario_results

        except Exception as e:
            scenario_results["error"] = f"Scenario execution failed: {e}"
            return scenario_results

    def cleanup(self):
        """Clean up scenario resources."""
        self.stress_test_running = False
        self.widgets.clear()
        self.themes.clear()
        self.app = None


if __name__ == "__main__":
    # Run the scenario
    scenario = ThemeSwitchingScenario()
    results = scenario.run_full_scenario()

    print("\n" + "=" * 50)
    print("THEME SWITCHING SCENARIO RESULTS")
    print("=" * 50)

    summary = results.get("summary", {})
    print(f"Setup Success: {results['setup_success']}")
    print(f"Widgets: {summary.get('total_widgets', 0)}")
    print(f"Themes: {summary.get('total_themes', 0)}")
    print(f"Sequential Avg: {summary.get('sequential_avg_time', 0):.2f}ms")
    print(f"Rapid Rate: {summary.get('rapid_switch_rate', 0):.1f} switches/sec")
    print(f"Concurrent Ops: {summary.get('concurrent_operations', 0)}")
    print(f"Consistency: {'✓' if summary.get('consistency_passed', False) else '✗'}")
    print(f"Stress Max Rate: {summary.get('stress_max_rate', 0):.1f} switches/sec")
    print(f"\nOverall Success: {'✓' if results['overall_success'] else '✗'}")

    scenario.cleanup()
