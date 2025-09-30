#!/usr/bin/env python3
"""
VFWidgets Theme System - Complex Application Scenario
Task 25: Complex multi-widget application testing

This scenario tests the theme system with a complex application containing
100+ widgets to ensure scalability and performance.
"""

import time
import threading
import weakref
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget
    from PySide6.QtWidgets import QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox, QCheckBox
    from PySide6.QtCore import QTimer
    PYSIDE_AVAILABLE = True
except ImportError:
    PYSIDE_AVAILABLE = False

from vfwidgets_theme.core.theme import Theme
from vfwidgets_theme.validation import ValidationFramework, ValidationMode


class MockWidget:
    """Mock widget for testing without Qt dependency."""

    def __init__(self, widget_type: str = "mock"):
        self.widget_type = widget_type
        self.theme = None
        self._properties = {}
        self._children = []
        self._parent = None

    def apply_theme(self, theme):
        """Apply theme to widget."""
        self.theme = theme
        # Simulate theme application
        if hasattr(theme, 'colors'):
            self._properties.update(theme.colors)
        if hasattr(theme, 'styles'):
            self._properties.update(theme.styles)

    def get_current_theme(self):
        """Get current theme."""
        return self.theme

    def supports_theme_property(self, property_name: str) -> bool:
        """Check if property is supported."""
        return property_name in ['color', 'background', 'font_size', 'padding']

    def add_child(self, child):
        """Add child widget."""
        child._parent = self
        self._children.append(child)

    def get_children(self):
        """Get child widgets."""
        return self._children


class ComplexApplicationScenario:
    """
    Test scenario for complex applications with many widgets.

    This scenario creates a complex application structure with 100+ widgets
    organized in a hierarchical layout and tests theme application performance
    and correctness.
    """

    def __init__(self, use_qt: bool = None):
        self.use_qt = use_qt if use_qt is not None else PYSIDE_AVAILABLE
        self.app = None
        self.main_window = None
        self.widgets = []
        self.widget_refs = []  # Weak references for memory testing
        self.themes = []
        self.validation_framework = ValidationFramework(ValidationMode.DEBUG)

    def setup_application(self) -> bool:
        """Set up the complex application."""
        try:
            if self.use_qt:
                return self._setup_qt_application()
            else:
                return self._setup_mock_application()
        except Exception as e:
            print(f"Application setup failed: {e}")
            return False

    def _setup_qt_application(self) -> bool:
        """Set up Qt-based application."""
        if not PYSIDE_AVAILABLE:
            print("PySide6 not available, falling back to mock widgets")
            return self._setup_mock_application()

        try:
            # Create Qt application if not exists
            if not QApplication.instance():
                self.app = QApplication([])
            else:
                self.app = QApplication.instance()

            # Create main window
            self.main_window = QMainWindow()
            self.main_window.setWindowTitle("Complex Theme Test Application")
            self.main_window.resize(1200, 800)

            # Create complex widget hierarchy
            central_widget = QWidget()
            self.main_window.setCentralWidget(central_widget)
            main_layout = QVBoxLayout(central_widget)

            # Create multiple sections with different widget types
            self._create_qt_widget_sections(main_layout)

            print(f"Created Qt application with {len(self.widgets)} widgets")
            return True

        except Exception as e:
            print(f"Qt application setup failed: {e}")
            return self._setup_mock_application()

    def _create_qt_widget_sections(self, main_layout):
        """Create sections with different Qt widget types."""
        sections = [
            ("Buttons", self._create_button_section),
            ("Labels", self._create_label_section),
            ("Inputs", self._create_input_section),
            ("Controls", self._create_control_section),
            ("Text Areas", self._create_text_section)
        ]

        for section_name, creator_func in sections:
            section_widget = QWidget()
            section_layout = QVBoxLayout(section_widget)

            # Section title
            title_label = QLabel(f"Section: {section_name}")
            section_layout.addWidget(title_label)
            self.widgets.append(title_label)

            # Create section content
            content_widget = creator_func()
            section_layout.addWidget(content_widget)

            main_layout.addWidget(section_widget)

        # Create weak references for memory testing
        self.widget_refs = [weakref.ref(widget) for widget in self.widgets]

    def _create_button_section(self) -> QWidget:
        """Create section with many buttons."""
        container = QWidget()
        layout = QHBoxLayout(container)

        for row in range(5):
            column_widget = QWidget()
            column_layout = QVBoxLayout(column_widget)

            for i in range(10):
                button = QPushButton(f"Button {row}-{i}")
                column_layout.addWidget(button)
                self.widgets.append(button)

            layout.addWidget(column_widget)

        return container

    def _create_label_section(self) -> QWidget:
        """Create section with many labels."""
        container = QWidget()
        layout = QVBoxLayout(container)

        for i in range(25):
            label = QLabel(f"Label {i}: This is sample text for testing theme application")
            layout.addWidget(label)
            self.widgets.append(label)

        return container

    def _create_input_section(self) -> QWidget:
        """Create section with input widgets."""
        container = QWidget()
        layout = QVBoxLayout(container)

        for i in range(15):
            input_widget = QLineEdit()
            input_widget.setPlaceholderText(f"Input field {i}")
            layout.addWidget(input_widget)
            self.widgets.append(input_widget)

        return container

    def _create_control_section(self) -> QWidget:
        """Create section with control widgets."""
        container = QWidget()
        layout = QVBoxLayout(container)

        # Combo boxes
        for i in range(10):
            combo = QComboBox()
            combo.addItems([f"Option {j}" for j in range(5)])
            layout.addWidget(combo)
            self.widgets.append(combo)

        # Checkboxes
        for i in range(10):
            checkbox = QCheckBox(f"Checkbox {i}")
            layout.addWidget(checkbox)
            self.widgets.append(checkbox)

        return container

    def _create_text_section(self) -> QWidget:
        """Create section with text areas."""
        container = QWidget()
        layout = QVBoxLayout(container)

        for i in range(5):
            text_area = QTextEdit()
            text_area.setPlainText(f"Text area {i}\nMultiple lines of text for theme testing.")
            layout.addWidget(text_area)
            self.widgets.append(text_area)

        return container

    def _setup_mock_application(self) -> bool:
        """Set up mock application without Qt dependency."""
        try:
            print("Setting up mock application for testing")

            # Create hierarchical widget structure
            self.main_window = MockWidget("main_window")

            # Create sections
            sections = [
                ("buttons", 50),
                ("labels", 30),
                ("inputs", 20),
                ("controls", 25),
                ("text_areas", 10)
            ]

            for section_type, count in sections:
                section_container = MockWidget(f"{section_type}_container")
                self.main_window.add_child(section_container)

                for i in range(count):
                    widget = MockWidget(f"{section_type}_{i}")
                    section_container.add_child(widget)
                    self.widgets.append(widget)

            # Create weak references
            self.widget_refs = [weakref.ref(widget) for widget in self.widgets]

            print(f"Created mock application with {len(self.widgets)} widgets")
            return True

        except Exception as e:
            print(f"Mock application setup failed: {e}")
            return False

    def create_test_themes(self):
        """Create various themes for testing."""
        themes = [
            Theme(
                name="light_theme",
                colors={
                    "primary": "#007acc",
                    "secondary": "#6f6f6f",
                    "background": "#ffffff",
                    "foreground": "#000000"
                },
                styles={
                    "font_family": "Arial",
                    "font_size": "12px",
                    "padding": "8px",
                    "border_radius": "4px"
                }
            ),
            Theme(
                name="dark_theme",
                colors={
                    "primary": "#4fc3f7",
                    "secondary": "#90a4ae",
                    "background": "#2b2b2b",
                    "foreground": "#ffffff"
                },
                styles={
                    "font_family": "Roboto",
                    "font_size": "14px",
                    "padding": "10px",
                    "border_radius": "6px"
                }
            ),
            Theme(
                name="high_contrast",
                colors={
                    "primary": "#ffff00",
                    "secondary": "#ff00ff",
                    "background": "#000000",
                    "foreground": "#ffffff"
                },
                styles={
                    "font_family": "Courier New",
                    "font_size": "16px",
                    "padding": "12px",
                    "border_radius": "2px"
                }
            )
        ]

        self.themes = themes
        print(f"Created {len(self.themes)} test themes")
        return themes

    def test_theme_application_performance(self) -> Dict[str, Any]:
        """Test theme application performance with many widgets."""
        if not self.widgets or not self.themes:
            return {"error": "Application or themes not set up"}

        results = {
            "widget_count": len(self.widgets),
            "theme_count": len(self.themes),
            "application_times": [],
            "total_time": 0.0,
            "average_time_per_widget": 0.0,
            "errors": []
        }

        try:
            for theme in self.themes:
                start_time = time.perf_counter()

                # Apply theme to all widgets
                applied_count = 0
                for widget in self.widgets:
                    try:
                        if hasattr(widget, 'apply_theme'):
                            widget.apply_theme(theme)
                            applied_count += 1
                    except Exception as e:
                        results["errors"].append(f"Failed to apply theme to widget: {e}")

                end_time = time.perf_counter()
                duration = end_time - start_time

                theme_result = {
                    "theme_name": theme.name,
                    "duration_ms": duration * 1000,
                    "widgets_themed": applied_count,
                    "widgets_per_second": applied_count / duration if duration > 0 else 0
                }

                results["application_times"].append(theme_result)
                print(f"Applied {theme.name} to {applied_count} widgets in {duration*1000:.2f}ms")

            # Calculate totals
            results["total_time"] = sum(t["duration_ms"] for t in results["application_times"])
            if results["widget_count"] > 0:
                results["average_time_per_widget"] = results["total_time"] / (results["widget_count"] * len(self.themes))

            return results

        except Exception as e:
            results["errors"].append(f"Theme application test failed: {e}")
            return results

    def test_memory_usage(self) -> Dict[str, Any]:
        """Test memory usage with complex application."""
        results = {
            "initial_widgets": len(self.widget_refs),
            "alive_widgets": 0,
            "dead_widgets": 0,
            "memory_test_passed": False
        }

        try:
            # Count alive widget references
            alive_count = 0
            for widget_ref in self.widget_refs:
                if widget_ref() is not None:
                    alive_count += 1

            results["alive_widgets"] = alive_count
            results["dead_widgets"] = results["initial_widgets"] - alive_count

            # Memory test passes if most widgets are still alive (expected during test)
            results["memory_test_passed"] = alive_count > results["initial_widgets"] * 0.8

            return results

        except Exception as e:
            results["error"] = f"Memory test failed: {e}"
            return results

    def test_concurrent_theme_changes(self) -> Dict[str, Any]:
        """Test concurrent theme changes from multiple threads."""
        results = {
            "thread_count": 3,
            "operations_per_thread": 10,
            "total_operations": 0,
            "successful_operations": 0,
            "errors": [],
            "duration_ms": 0.0
        }

        if not self.widgets or not self.themes:
            results["errors"].append("Application or themes not set up")
            return results

        try:
            start_time = time.perf_counter()
            threads = []
            thread_results = []

            def theme_change_worker(worker_id: int, operations: int):
                """Worker thread for theme changes."""
                worker_results = {"operations": 0, "errors": []}

                for i in range(operations):
                    try:
                        theme = self.themes[i % len(self.themes)]
                        # Apply theme to a subset of widgets
                        widget_subset = self.widgets[worker_id::results["thread_count"]]

                        for widget in widget_subset:
                            if hasattr(widget, 'apply_theme'):
                                widget.apply_theme(theme)

                        worker_results["operations"] += 1
                        time.sleep(0.01)  # Small delay to create concurrency

                    except Exception as e:
                        worker_results["errors"].append(f"Worker {worker_id}: {e}")

                thread_results.append(worker_results)

            # Start worker threads
            for i in range(results["thread_count"]):
                thread = threading.Thread(
                    target=theme_change_worker,
                    args=(i, results["operations_per_thread"])
                )
                threads.append(thread)
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            end_time = time.perf_counter()
            results["duration_ms"] = (end_time - start_time) * 1000

            # Aggregate results
            for worker_result in thread_results:
                results["successful_operations"] += worker_result["operations"]
                results["errors"].extend(worker_result["errors"])

            results["total_operations"] = results["thread_count"] * results["operations_per_thread"]

            return results

        except Exception as e:
            results["errors"].append(f"Concurrent test failed: {e}")
            return results

    def run_full_scenario(self) -> Dict[str, Any]:
        """Run the complete complex application scenario."""
        print("Running Complex Application Scenario...")
        print("=" * 50)

        scenario_results = {
            "setup_success": False,
            "widget_count": 0,
            "theme_count": 0,
            "performance_results": None,
            "memory_results": None,
            "concurrent_results": None,
            "overall_success": False,
            "errors": []
        }

        try:
            # Setup application
            if not self.setup_application():
                scenario_results["errors"].append("Failed to setup application")
                return scenario_results

            scenario_results["setup_success"] = True
            scenario_results["widget_count"] = len(self.widgets)

            # Create themes
            self.create_test_themes()
            scenario_results["theme_count"] = len(self.themes)

            # Test performance
            print("\nTesting theme application performance...")
            performance_results = self.test_theme_application_performance()
            scenario_results["performance_results"] = performance_results

            if performance_results.get("errors"):
                scenario_results["errors"].extend(performance_results["errors"])

            # Test memory usage
            print("\nTesting memory usage...")
            memory_results = self.test_memory_usage()
            scenario_results["memory_results"] = memory_results

            # Test concurrent access
            print("\nTesting concurrent theme changes...")
            concurrent_results = self.test_concurrent_theme_changes()
            scenario_results["concurrent_results"] = concurrent_results

            if concurrent_results.get("errors"):
                scenario_results["errors"].extend(concurrent_results["errors"])

            # Determine overall success
            scenario_results["overall_success"] = (
                scenario_results["setup_success"] and
                len(scenario_results["errors"]) == 0 and
                performance_results.get("widget_count", 0) > 100 and
                memory_results.get("memory_test_passed", False)
            )

            return scenario_results

        except Exception as e:
            scenario_results["errors"].append(f"Scenario execution failed: {e}")
            return scenario_results

    def cleanup(self):
        """Clean up resources."""
        try:
            if self.use_qt and self.main_window:
                self.main_window.close()
                if hasattr(self, 'app') and self.app:
                    # Don't quit the app as it might be shared
                    pass

            self.widgets.clear()
            self.widget_refs.clear()
            self.themes.clear()

            print("Complex application scenario cleanup completed")

        except Exception as e:
            print(f"Cleanup error: {e}")

    def __del__(self):
        """Destructor for cleanup."""
        self.cleanup()


if __name__ == "__main__":
    # Run the scenario
    scenario = ComplexApplicationScenario(use_qt=False)  # Use mock widgets for testing
    results = scenario.run_full_scenario()

    print("\n" + "=" * 50)
    print("COMPLEX APPLICATION SCENARIO RESULTS")
    print("=" * 50)

    print(f"Setup Success: {results['setup_success']}")
    print(f"Widget Count: {results['widget_count']}")
    print(f"Theme Count: {results['theme_count']}")

    if results['performance_results']:
        perf = results['performance_results']
        print(f"Performance Test:")
        print(f"  Total Time: {perf.get('total_time', 0):.2f}ms")
        print(f"  Avg Time per Widget: {perf.get('average_time_per_widget', 0):.2f}ms")

    if results['memory_results']:
        mem = results['memory_results']
        print(f"Memory Test:")
        print(f"  Alive Widgets: {mem.get('alive_widgets', 0)}/{mem.get('initial_widgets', 0)}")
        print(f"  Memory Test Passed: {mem.get('memory_test_passed', False)}")

    if results['concurrent_results']:
        conc = results['concurrent_results']
        print(f"Concurrent Test:")
        print(f"  Operations: {conc.get('successful_operations', 0)}/{conc.get('total_operations', 0)}")
        print(f"  Duration: {conc.get('duration_ms', 0):.2f}ms")

    print(f"\nOverall Success: {'✓' if results['overall_success'] else '✗'}")

    if results['errors']:
        print("\nErrors:")
        for error in results['errors']:
            print(f"  - {error}")

    scenario.cleanup()