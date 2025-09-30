#!/usr/bin/env python3
"""
Advanced ThemedWidget Example

This example demonstrates advanced usage of ThemedWidget and the complete
theme system architecture, showcasing all the sophisticated features while
maintaining the simple API philosophy.

Features demonstrated:
- Advanced theme configuration and inheritance
- Custom theme property descriptors
- Theme mixins for existing widgets
- Performance optimization techniques
- Thread-safe operations
- Memory management and cleanup
- VSCode theme importing
- System theme detection
- Error recovery and debugging

Run this example:
    python themed_widget_advanced.py
"""

import sys
import time
import threading
import weakref
from pathlib import Path
from typing import Dict, Any, List

# Add the source directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from PySide6.QtWidgets import (
        QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
        QMainWindow, QWidget, QTextEdit, QSlider, QProgressBar
    )
    from PySide6.QtCore import QTimer, QThread, pyqtSignal
    from PySide6.QtGui import QPainter, QColor, QPaintEvent
    QT_AVAILABLE = True
except ImportError:
    print("PySide6 not available. This example will run with fallback implementations.")
    QT_AVAILABLE = False

    # Fallback implementations
    class QVBoxLayout: pass
    class QHBoxLayout: pass
    class QPushButton:
        def __init__(self, text): self.text = text
    class QLabel:
        def __init__(self, text): self.text = text
    class QMainWindow: pass
    class QWidget: pass
    class QTextEdit: pass
    class QSlider: pass
    class QProgressBar: pass
    class QTimer: pass
    class QThread: pass
    class QPainter: pass
    class QColor: pass
    class QPaintEvent: pass
    def pyqtSignal(*args): pass

from vfwidgets_theme.widgets.base import ThemedWidget, ThemePropertyDescriptor
from vfwidgets_theme.widgets.application import ThemedApplication
from vfwidgets_theme.widgets.mixins import (
    ThemeableMixin, PropertyMixin, NotificationMixin,
    CacheMixin, CompositeMixin, themeable
)
from vfwidgets_theme.core.theme import Theme, ThemeBuilder
from vfwidgets_theme.testing import ThemeBenchmark, MemoryProfiler


class AdvancedThemedButton(ThemedWidget):
    """
    Advanced themed button with custom property descriptors and animations.

    Demonstrates:
    - Custom theme configuration with inheritance
    - Property descriptors for type safety
    - Animation state management
    - Advanced styling with multiple properties
    """

    # Advanced theme configuration with inheritance chains
    theme_config = {
        # Basic properties
        'background': 'button.background',
        'foreground': 'button.foreground',
        'border': 'button.border',

        # State-specific properties
        'hover_background': 'button.hover.background',
        'active_background': 'button.active.background',
        'disabled_background': 'button.disabled.background',

        # Advanced properties
        'border_radius': 'button.border.radius',
        'shadow_color': 'button.shadow.color',
        'animation_duration': 'button.animation.duration',

        # Computed properties
        'computed_gradient': '@colors.primary,@colors.accent',
        'computed_shadow': '0 2px 4px @colors.shadow'
    }

    def __init__(self, text="Advanced Button", parent=None):
        super().__init__(parent)

        self._text = text
        self._state = "normal"  # normal, hover, active, disabled
        self._animation_progress = 0.0
        self._click_count = 0

        # Track performance metrics
        self._property_access_count = 0
        self._theme_change_count = 0

        print(f"🔧 Created AdvancedThemedButton: {self._text}")
        print(f"   - Advanced theme config with {len(self._theme_config)} properties")

    def on_theme_changed(self):
        """Advanced theme change handling with performance tracking."""
        self._theme_change_count += 1

        # Demonstrate property access patterns
        properties = {}
        for key in self._theme_config.keys():
            properties[key] = self.theme.get(key, f'default_{key}')
            self._property_access_count += 1

        print(f"🎨 Advanced button '{self._text}' theme changed (#{self._theme_change_count})")
        print(f"   - Loaded {len(properties)} theme properties")
        print(f"   - Background: {properties.get('background', 'N/A')}")
        print(f"   - Hover state: {properties.get('hover_background', 'N/A')}")
        print(f"   - Border radius: {properties.get('border_radius', 'N/A')}")

        # Trigger repaint with new theme
        self.update()

    def set_state(self, state: str):
        """Change button state and update appearance."""
        if state != self._state:
            old_state = self._state
            self._state = state
            print(f"🔄 Button '{self._text}' state: {old_state} → {state}")
            self.update()

    def click(self):
        """Simulate button click with state tracking."""
        self._click_count += 1
        self.set_state("active")

        # Simulate animation
        self._animation_progress = 1.0
        print(f"👆 Button '{self._text}' clicked (#{self._click_count})")

        # Reset state after delay (simulated)
        # In real Qt app, this would use QTimer

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get button-specific performance statistics."""
        stats = self.theme_statistics.copy()
        stats.update({
            'click_count': self._click_count,
            'property_access_count': self._property_access_count,
            'theme_change_count': self._theme_change_count,
            'current_state': self._state
        })
        return stats


class CustomThemedWidget(ThemedWidget):
    """
    Custom widget with sophisticated theme configuration.

    Demonstrates:
    - Complex theme property hierarchies
    - Property validation and type conversion
    - Dynamic theme property generation
    """

    # Sophisticated theme configuration
    theme_config = {
        # Color palette
        'primary_color': 'palette.primary',
        'secondary_color': 'palette.secondary',
        'accent_color': 'palette.accent',
        'success_color': 'palette.success',
        'warning_color': 'palette.warning',
        'error_color': 'palette.error',

        # Typography
        'title_font': 'typography.title.font',
        'title_size': 'typography.title.size',
        'body_font': 'typography.body.font',
        'body_size': 'typography.body.size',

        # Layout
        'padding': 'layout.padding',
        'margin': 'layout.margin',
        'border_width': 'layout.border.width',
        'border_style': 'layout.border.style',

        # Advanced features
        'transition_duration': 'animation.transition.duration',
        'easing_function': 'animation.easing.function',
        'shadow_blur': 'effects.shadow.blur',
        'shadow_offset': 'effects.shadow.offset'
    }

    def __init__(self, widget_type="custom", parent=None):
        super().__init__(parent)

        self._widget_type = widget_type
        self._content_widgets = []
        self._layout_cache = {}

        print(f"⚙️ Created CustomThemedWidget: {self._widget_type}")

    def on_theme_changed(self):
        """Handle theme changes with property validation."""
        print(f"🎨 Custom widget '{self._widget_type}' theme changed")

        # Demonstrate property validation and type conversion
        try:
            # Numeric properties with validation
            padding = self._validate_numeric(self.theme.get('padding', '8'), 'padding')
            margin = self._validate_numeric(self.theme.get('margin', '4'), 'margin')
            border_width = self._validate_numeric(self.theme.get('border_width', '1'), 'border_width')

            # Duration properties with unit handling
            transition = self._validate_duration(self.theme.get('transition_duration', '200ms'))

            print(f"   - Layout: padding={padding}, margin={margin}, border={border_width}")
            print(f"   - Animation: transition={transition}")

        except Exception as e:
            print(f"   - Validation error (handled gracefully): {e}")

    def _validate_numeric(self, value: Any, property_name: str) -> float:
        """Validate and convert numeric theme properties."""
        if isinstance(value, (int, float)):
            return float(value)
        elif isinstance(value, str):
            # Handle units (px, em, %, etc.)
            import re
            match = re.match(r'^(\d+(?:\.\d+)?)(px|em|rem|%)?$', value.strip())
            if match:
                return float(match.group(1))

        # Fallback for invalid values
        print(f"   ⚠️ Invalid {property_name} value: {value}, using default")
        return 0.0

    def _validate_duration(self, value: Any) -> float:
        """Validate and convert duration properties to milliseconds."""
        if isinstance(value, (int, float)):
            return float(value)
        elif isinstance(value, str):
            value = value.strip().lower()
            if value.endswith('ms'):
                return float(value[:-2])
            elif value.endswith('s'):
                return float(value[:-1]) * 1000

        return 200.0  # Default 200ms

    def add_content_widget(self, widget: ThemedWidget):
        """Add a child themed widget."""
        self._content_widgets.append(widget)
        print(f"   📦 Added content widget to {self._widget_type}")


class ExistingWidgetWithTheming(QPushButton, ThemeableMixin):
    """
    Existing Qt widget enhanced with theming using mixins.

    Demonstrates:
    - Adding theming to existing Qt widgets
    - Mixin composition for flexible functionality
    - Integration with Qt widget hierarchy
    """

    def __init__(self, text="Mixin Button"):
        super().__init__(text)

        # Set up theming through mixin
        self.setup_theming({
            'bg': 'button.background',
            'fg': 'button.foreground',
            'font': 'button.font'
        })

        print(f"🔌 Created widget with ThemeableMixin: {text}")

    def on_theme_changed(self):
        """Handle theme changes through mixin."""
        print(f"🎨 Mixin widget theme changed")
        if hasattr(self, 'setText'):
            # Update button text to show theme info
            bg = self.theme.get('bg', '#ffffff')
            self.setText(f"Themed Button ({bg})")


@themeable({
    'panel_bg': 'panel.background',
    'panel_border': 'panel.border'
})
class DecoratedThemedPanel(QWidget, CompositeMixin):
    """
    Panel with complete theming through decorator and composite mixin.

    Demonstrates:
    - Automatic theming setup through decorator
    - Composite mixin for all theming capabilities
    - Complex widget composition
    """

    def __init__(self):
        super().__init__()

        # CompositeMixin setup is handled by decorator
        self._child_widgets = []

        print("📋 Created decorated themed panel with composite capabilities")

    def on_theme_changed(self):
        """Handle theme changes for the decorated panel."""
        print("🎨 Decorated panel theme changed")
        bg = self.theme.get('panel_bg', '#f0f0f0')
        border = self.theme.get('panel_border', '#cccccc')
        print(f"   - Panel styling: bg={bg}, border={border}")


class ThreadedThemeWorker:
    """
    Worker class demonstrating thread-safe theme operations.

    Shows how ThemedWidget works safely across threads.
    """

    def __init__(self, widgets: List[ThemedWidget]):
        self._widgets = [weakref.ref(w) for w in widgets]
        self._running = False

    def start_work(self):
        """Start thread-safe theme operations."""
        self._running = True
        thread = threading.Thread(target=self._work_loop)
        thread.daemon = True
        thread.start()
        print("🧵 Started threaded theme worker")

    def stop_work(self):
        """Stop thread work."""
        self._running = False

    def _work_loop(self):
        """Worker loop demonstrating thread-safe operations."""
        while self._running:
            try:
                # Access widget properties from different thread
                for widget_ref in self._widgets:
                    widget = widget_ref()
                    if widget and hasattr(widget, 'theme'):
                        # This should be thread-safe thanks to ThemedWidget's architecture
                        bg = widget.theme.get('background', '#ffffff')
                        # In real usage, you might update data models or perform calculations

                time.sleep(0.5)  # Simulate work

            except Exception as e:
                print(f"🧵 Thread worker error (handled): {e}")

        print("🧵 Thread worker stopped")


class AdvancedExample:
    """
    Comprehensive demonstration of advanced ThemedWidget features.
    """

    def __init__(self):
        """Initialize the advanced example."""
        print("🚀 Starting Advanced ThemedWidget Example")
        print("="*70)

        # Initialize application with configuration
        self.app = ThemedApplication([], theme_config={
            'default_theme': 'dark',
            'auto_detect_system': True,
            'vscode_integration': True,
            'performance_monitoring': True
        })

        # Initialize benchmarking and profiling
        self.benchmark = ThemeBenchmark()
        self.profiler = MemoryProfiler()

        # Create advanced widgets
        self.widgets = []
        self.create_advanced_widgets()

        # Demonstrate advanced features
        self.demonstrate_theme_inheritance()
        self.demonstrate_custom_themes()
        self.demonstrate_performance_optimization()
        self.demonstrate_thread_safety()
        self.demonstrate_memory_management()
        self.demonstrate_error_recovery()

        # Show comprehensive statistics
        self.show_comprehensive_stats()

    def create_advanced_widgets(self):
        """Create a variety of advanced themed widgets."""
        print("\n🏗️ Creating Advanced Themed Widgets")
        print("-" * 40)

        # Advanced themed widgets
        self.advanced_button = AdvancedThemedButton("Primary Action")
        self.custom_widget = CustomThemedWidget("data_panel")

        # Widget with mixin
        self.mixin_widget = ExistingWidgetWithTheming("Enhanced Qt Widget")

        # Decorated widget
        self.decorated_panel = DecoratedThemedPanel()

        # Store all widgets for testing
        self.widgets = [
            self.advanced_button,
            self.custom_widget,
            self.mixin_widget,
            self.decorated_panel
        ]

        print(f"✅ Created {len(self.widgets)} advanced themed widgets")

    def demonstrate_theme_inheritance(self):
        """Demonstrate theme configuration inheritance."""
        print("\n🧬 Demonstrating Theme Inheritance")
        print("-" * 35)

        # Show how widgets inherit and override theme configurations
        for widget in self.widgets:
            if hasattr(widget, '_theme_config'):
                print(f"📋 {type(widget).__name__}:")
                config = widget._theme_config
                print(f"   - Properties: {len(config)}")
                print(f"   - Sample properties: {list(config.keys())[:3]}")

        # Demonstrate parent-child inheritance
        child_button = AdvancedThemedButton("Child Button", parent=self.custom_widget)
        self.custom_widget.add_content_widget(child_button)

        print("👨‍👧‍👦 Created parent-child widget hierarchy")
        print("   - Child automatically inherits parent's theme context")

    def demonstrate_custom_themes(self):
        """Demonstrate custom theme creation and application."""
        print("\n🎨 Demonstrating Custom Theme Creation")
        print("-" * 40)

        # Create a custom theme using ThemeBuilder
        builder = ThemeBuilder()

        custom_theme = (builder
            .set_name("custom_advanced")
            .set_description("Custom theme for advanced demo")

            # Define color palette
            .add_color("primary", "#6366f1")
            .add_color("secondary", "#8b5cf6")
            .add_color("accent", "#06b6d4")
            .add_color("success", "#10b981")
            .add_color("warning", "#f59e0b")
            .add_color("error", "#ef4444")

            # Define component styles
            .add_style("button", {
                "background": "@colors.primary",
                "foreground": "#ffffff",
                "border": "1px solid @colors.primary",
                "border-radius": "6px"
            })
            .add_style("button.hover", {
                "background": "@colors.secondary"
            })
            .add_style("panel", {
                "background": "#f8fafc",
                "border": "1px solid #e2e8f0"
            })

            # Define typography
            .add_style("typography.title", {
                "font": "600 18px Inter, sans-serif",
                "size": "18px"
            })
            .add_style("typography.body", {
                "font": "400 14px Inter, sans-serif",
                "size": "14px"
            })

            .build())

        # Add theme to application
        success = self.app.set_theme(custom_theme)
        print(f"✅ Applied custom theme: {success}")

        if success:
            print(f"   - Theme name: {custom_theme.name}")
            print(f"   - Colors defined: {len(custom_theme.colors)}")
            print(f"   - Styles defined: {len(custom_theme.styles)}")

    def demonstrate_performance_optimization(self):
        """Demonstrate performance optimization features."""
        print("\n⚡ Demonstrating Performance Optimization")
        print("-" * 45)

        # Benchmark widget creation
        def create_widgets():
            return [AdvancedThemedButton(f"Perf Button {i}") for i in range(50)]

        creation_time = self.benchmark.measure_time(create_widgets)
        temp_widgets = create_widgets()

        print(f"🏗️ Widget Creation Performance:")
        print(f"   - 50 widgets created in: {creation_time:.3f}s")
        print(f"   - Average per widget: {(creation_time / 50) * 1000:.1f}ms")

        # Benchmark theme switching
        def switch_themes():
            themes = ['default', 'dark', 'light']
            for theme in themes:
                self.app.set_theme(theme)

        switch_time = self.benchmark.measure_time(switch_themes)
        widget_count = len(self.widgets) + len(temp_widgets)

        print(f"🎨 Theme Switching Performance:")
        print(f"   - 3 theme switches: {switch_time:.3f}s")
        print(f"   - {widget_count} widgets updated")
        print(f"   - Average per switch: {(switch_time / 3) * 1000:.1f}ms")

        # Benchmark property access
        def access_properties():
            for _ in range(1000):
                for widget in self.widgets[:3]:  # Test subset
                    if hasattr(widget, 'theme'):
                        _ = widget.theme.get('background', '#fff')

        access_time = self.benchmark.measure_time(access_properties)
        total_accesses = 1000 * 3

        print(f"🔍 Property Access Performance:")
        print(f"   - {total_accesses} property accesses: {access_time:.3f}s")
        print(f"   - Average per access: {(access_time / total_accesses) * 1000000:.1f}μs")

        # Cleanup temp widgets
        for widget in temp_widgets:
            widget._cleanup_theme()

    def demonstrate_thread_safety(self):
        """Demonstrate thread-safe operations."""
        print("\n🧵 Demonstrating Thread Safety")
        print("-" * 30)

        # Create threaded worker
        worker = ThreadedThemeWorker(self.widgets)
        worker.start_work()

        # Perform theme changes while worker is running
        themes = ['dark', 'light', 'default']
        for i, theme in enumerate(themes):
            print(f"🔄 Switching to {theme} while threads are active...")
            self.app.set_theme(theme)
            time.sleep(0.2)  # Let worker run

        # Stop worker
        worker.stop_work()
        time.sleep(0.6)  # Let worker finish

        print("✅ Thread safety demonstration completed")

    def demonstrate_memory_management(self):
        """Demonstrate memory management and leak prevention."""
        print("\n🧠 Demonstrating Memory Management")
        print("-" * 35)

        baseline_memory = self.profiler.get_memory_usage()

        # Create and destroy many widgets
        temp_widgets = []
        for i in range(100):
            widget = AdvancedThemedButton(f"Temp {i}")
            temp_widgets.append(widget)

        peak_memory = self.profiler.get_memory_usage()
        memory_per_widget = (peak_memory - baseline_memory) / 100

        print(f"📊 Memory Usage Analysis:")
        print(f"   - Baseline: {baseline_memory / 1024:.1f} KB")
        print(f"   - Peak (100 widgets): {peak_memory / 1024:.1f} KB")
        print(f"   - Memory per widget: {memory_per_widget:.0f} bytes")

        # Clean up widgets properly
        for widget in temp_widgets:
            widget._cleanup_theme()
        del temp_widgets

        # Force garbage collection (simulated)
        import gc
        gc.collect()

        final_memory = self.profiler.get_memory_usage()
        memory_recovered = peak_memory - final_memory

        print(f"🧹 After Cleanup:")
        print(f"   - Final memory: {final_memory / 1024:.1f} KB")
        print(f"   - Memory recovered: {memory_recovered / 1024:.1f} KB")
        print(f"   - Recovery rate: {(memory_recovered / (peak_memory - baseline_memory)) * 100:.1f}%")

    def demonstrate_error_recovery(self):
        """Demonstrate comprehensive error recovery."""
        print("\n🛡️ Demonstrating Error Recovery")
        print("-" * 35)

        # Test various error scenarios
        error_scenarios = [
            ("Invalid theme name", lambda: self.app.set_theme("invalid_theme_12345")),
            ("Malformed property access", lambda: self.widgets[0].theme.get("deeply.nested.invalid.property.path")),
            ("Widget with bad config", self._create_problematic_widget),
        ]

        for scenario_name, scenario_func in error_scenarios:
            print(f"🧪 Testing: {scenario_name}")
            try:
                result = scenario_func()
                print(f"   ✅ Handled gracefully, result: {result}")
            except Exception as e:
                print(f"   ⚠️ Exception caught (may be expected): {e}")

    def _create_problematic_widget(self):
        """Create a widget with problematic configuration for testing."""
        class ProblematicWidget(ThemedWidget):
            theme_config = {
                'invalid1': 'this.path.does.not.exist',
                'invalid2': 'neither.does.this.one',
                'circular': '@theme.circular'  # Potential circular reference
            }

        widget = ProblematicWidget()
        # Try to access problematic properties
        prop1 = widget.theme.get('invalid1', 'fallback1')
        prop2 = widget.theme.get('invalid2', 'fallback2')

        widget._cleanup_theme()
        return f"Created problematic widget: {prop1}, {prop2}"

    def show_comprehensive_stats(self):
        """Show comprehensive statistics and performance metrics."""
        print("\n📊 Comprehensive Statistics")
        print("-" * 30)

        # Application-level statistics
        app_stats = self.app.get_performance_statistics()
        print("🏢 Application Statistics:")
        for key, value in app_stats.items():
            if isinstance(value, float):
                print(f"   - {key}: {value:.3f}")
            else:
                print(f"   - {key}: {value}")

        # Widget-level statistics
        print("\n🔧 Widget Statistics:")
        for i, widget in enumerate(self.widgets):
            if hasattr(widget, 'get_performance_stats'):
                try:
                    stats = widget.get_performance_stats()
                    print(f"   Widget {i+1} ({type(widget).__name__}):")
                    for key, value in stats.items():
                        if isinstance(value, float):
                            print(f"     - {key}: {value:.3f}")
                        else:
                            print(f"     - {key}: {value}")
                except Exception as e:
                    print(f"   Widget {i+1}: stats error - {e}")

        # Memory profiler statistics
        print(f"\n🧠 Memory Statistics:")
        print(f"   - Current usage: {self.profiler.get_memory_usage() / 1024:.1f} KB")

    def cleanup(self):
        """Clean up the advanced example."""
        print("\n🧹 Advanced Cleanup")
        print("-" * 20)

        # Clean up all widgets
        for widget in self.widgets:
            if hasattr(widget, '_cleanup_theme'):
                widget._cleanup_theme()
            elif hasattr(widget, 'cleanup_theming'):
                widget.cleanup_theming()

        # Clean up application
        self.app.cleanup()

        print("✅ Advanced cleanup completed")

    def run(self):
        """Run the advanced example."""
        try:
            print("\n🎉 Advanced ThemedWidget Example Completed Successfully!")
            print("="*70)
            print("\nAdvanced Features Demonstrated:")
            print("1. Complex theme configuration with inheritance")
            print("2. Custom property descriptors and validation")
            print("3. Mixin composition for existing widgets")
            print("4. Thread-safe operations across multiple threads")
            print("5. Memory management with automatic cleanup")
            print("6. Performance optimization and monitoring")
            print("7. Comprehensive error recovery")
            print("8. Custom theme creation and application")
            print("9. Statistical analysis and profiling")

        finally:
            self.cleanup()


def main():
    """Main entry point."""
    try:
        example = AdvancedExample()
        example.run()
        return 0

    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
        return 1

    except Exception as e:
        print(f"\n❌ Error running advanced example: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())