# MultiSplit Extension Guide

## Overview

This guide covers advanced extension patterns, performance analysis, and customization techniques for extending MultiSplit functionality. It provides deep insights into complexity analysis, extension architectures, and advanced usage patterns for power users and framework developers.

## What This Covers

- **Extension architecture patterns** - Plugins, custom commands, renderers
- **Performance complexity analysis** - Big O analysis, optimization strategies
- **Custom command development** - New operations, validation, undo support
- **Renderer extensions** - Custom drawing, theming, visual effects
- **Framework integration** - Embedding in larger systems, protocol extensions

## What This Doesn't Cover

- **Basic usage patterns** - See [Usage Guide](usage-guide.md)
- **Provider implementation** - See [Integration Guide](integration-guide.md)
- **Core architecture** - See [Architecture docs](../02-architecture/)
- **Standard API usage** - See [Public API](../05-api/public-api.md)

---

## Performance Complexity Analysis

### Core Operation Complexity

Understanding the computational complexity of MultiSplit operations is crucial for building performant extensions:

```python
class ComplexityAnalyzer:
    """Analyze and document MultiSplit operation complexity"""

    @staticmethod
    def analyze_operation_complexity():
        """Document complexity of core operations"""

        return {
            # Tree Operations
            "find_node": "O(log n)",  # Balanced tree traversal
            "find_parent": "O(log n)",  # Path traversal
            "split_pane": "O(log n)",  # Find + modify tree
            "close_pane": "O(log n)",  # Find + restructure
            "save_layout": "O(n)",     # Visit all nodes
            "restore_layout": "O(n)",  # Create all nodes

            # Widget Operations (depends on provider)
            "provide_widget": "O(1) to O(k)",  # k = widget creation cost
            "widget_closing": "O(1)",          # Cleanup only

            # Geometry Calculations
            "calculate_geometry": "O(n)",      # Visit all panes
            "resize_pane": "O(log n)",         # Update split ratios

            # Focus Operations
            "focus_pane": "O(1)",              # Direct access
            "focus_next": "O(n)",              # Linear search
            "spatial_navigation": "O(n)",      # Check all panes

            # Reconciliation
            "reconcile_tree": "O(n + m)",      # n=old, m=new nodes
            "apply_diff": "O(d)",              # d=diff size

            # Memory Operations
            "memory_cleanup": "O(c)",          # c=cache size
            "cache_lookup": "O(1)",            # Hash table access
        }

    @staticmethod
    def optimization_strategies():
        """Strategies for optimizing different complexity classes"""

        return {
            "O(1) operations": [
                "Ensure hash table access for widget lookup",
                "Use direct references for pane access",
                "Cache frequently used calculations"
            ],

            "O(log n) operations": [
                "Maintain balanced tree structure",
                "Use path caching for repeated access",
                "Implement breadcrumb navigation"
            ],

            "O(n) operations": [
                "Use lazy evaluation where possible",
                "Implement viewport culling",
                "Batch operations to reduce iterations",
                "Use incremental updates"
            ],

            "O(n²) operations to avoid": [
                "Nested loops over all panes",
                "Repeated tree traversals",
                "Redundant geometry calculations",
                "Unbounded cache searches"
            ]
        }

class PerformanceBenchmarks:
    """Benchmark MultiSplit operations for optimization"""

    def __init__(self, splitter: MultiSplitWidget):
        self.splitter = splitter
        self.benchmark_results = {}

    def benchmark_tree_operations(self, pane_counts: List[int]):
        """Benchmark tree operations across different pane counts"""

        results = {}

        for count in pane_counts:
            # Setup test scenario
            layout = self.create_test_layout(count)
            self.splitter.restore_layout(layout)

            # Benchmark operations
            operations = {
                'find_pane': lambda: self.benchmark_find_operations(count),
                'split_operations': lambda: self.benchmark_split_operations(count),
                'geometry_calc': lambda: self.benchmark_geometry_calculation(),
                'reconciliation': lambda: self.benchmark_reconciliation(),
                'focus_navigation': lambda: self.benchmark_focus_navigation(count)
            }

            count_results = {}
            for op_name, op_func in operations.items():
                times = []
                for _ in range(10):  # Multiple runs for accuracy
                    start_time = time.perf_counter()
                    op_func()
                    end_time = time.perf_counter()
                    times.append(end_time - start_time)

                count_results[op_name] = {
                    'avg_time': sum(times) / len(times),
                    'min_time': min(times),
                    'max_time': max(times)
                }

            results[count] = count_results

        return results

    def create_test_layout(self, pane_count: int) -> dict:
        """Create balanced test layout with specified pane count"""

        if pane_count == 1:
            return {
                "type": "leaf",
                "pane_id": "pane_0",
                "widget_id": "test:0"
            }

        # Create balanced binary tree
        def create_balanced_tree(start: int, end: int) -> dict:
            if start == end:
                return {
                    "type": "leaf",
                    "pane_id": f"pane_{start}",
                    "widget_id": f"test:{start}"
                }

            mid = (start + end) // 2
            left = create_balanced_tree(start, mid)
            right = create_balanced_tree(mid + 1, end)

            return {
                "type": "split",
                "orientation": "horizontal" if (end - start) % 2 == 0 else "vertical",
                "ratios": [0.5, 0.5],
                "children": [left, right]
            }

        return create_balanced_tree(0, pane_count - 1)

    def analyze_complexity_scaling(self, benchmark_results: dict) -> dict:
        """Analyze how operations scale with pane count"""

        analysis = {}

        for operation in benchmark_results[list(benchmark_results.keys())[0]].keys():
            pane_counts = list(benchmark_results.keys())
            times = [benchmark_results[count][operation]['avg_time'] for count in pane_counts]

            # Fit to different complexity curves
            complexity_fits = {}

            # O(1) - constant time
            if len(set(times)) == 1:  # All times equal
                complexity_fits['O(1)'] = 1.0
            else:
                complexity_fits['O(1)'] = self.calculate_fit_quality(pane_counts, times, lambda n: 1)

            # O(log n) - logarithmic
            complexity_fits['O(log n)'] = self.calculate_fit_quality(
                pane_counts, times, lambda n: math.log2(n)
            )

            # O(n) - linear
            complexity_fits['O(n)'] = self.calculate_fit_quality(
                pane_counts, times, lambda n: n
            )

            # O(n log n) - linearithmic
            complexity_fits['O(n log n)'] = self.calculate_fit_quality(
                pane_counts, times, lambda n: n * math.log2(n)
            )

            # O(n²) - quadratic
            complexity_fits['O(n²)'] = self.calculate_fit_quality(
                pane_counts, times, lambda n: n * n
            )

            # Find best fit
            best_complexity = max(complexity_fits.keys(), key=lambda k: complexity_fits[k])

            analysis[operation] = {
                'complexity_fits': complexity_fits,
                'best_fit': best_complexity,
                'fit_quality': complexity_fits[best_complexity]
            }

        return analysis

    def calculate_fit_quality(self, x_values: List[int], y_values: List[float],
                            complexity_func: callable) -> float:
        """Calculate how well data fits a complexity curve (R² coefficient)"""

        # Transform x values using complexity function
        x_transformed = [complexity_func(x) for x in x_values]

        # Calculate R² coefficient
        try:
            correlation = numpy.corrcoef(x_transformed, y_values)[0, 1]
            return correlation ** 2
        except:
            # Fallback if numpy not available
            return self.calculate_r_squared_simple(x_transformed, y_values)

    def calculate_r_squared_simple(self, x_values: List[float], y_values: List[float]) -> float:
        """Simple R² calculation without numpy"""

        n = len(x_values)
        if n < 2:
            return 0.0

        # Calculate means
        x_mean = sum(x_values) / n
        y_mean = sum(y_values) / n

        # Calculate correlation coefficient
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
        x_variance = sum((x - x_mean) ** 2 for x in x_values)
        y_variance = sum((y - y_mean) ** 2 for y in y_values)

        if x_variance == 0 or y_variance == 0:
            return 0.0

        correlation = numerator / (math.sqrt(x_variance) * math.sqrt(y_variance))
        return correlation ** 2
```

### Optimization Patterns

Implement optimization patterns based on complexity analysis:

```python
class OptimizationPatterns:
    """Advanced optimization patterns for MultiSplit extensions"""

    @staticmethod
    def implement_spatial_indexing(splitter: MultiSplitWidget):
        """Optimize spatial operations with indexing"""

        class SpatialIndex:
            """2D spatial index for fast pane location queries"""

            def __init__(self):
                self.pane_rects = {}  # pane_id -> QRect
                self.grid_size = 50   # Grid cell size in pixels
                self.grid = {}        # (grid_x, grid_y) -> set of pane_ids

            def update_pane(self, pane_id: str, rect: QRect):
                """Update pane position in spatial index"""

                # Remove from old grid cells
                if pane_id in self.pane_rects:
                    old_rect = self.pane_rects[pane_id]
                    self.remove_from_grid(pane_id, old_rect)

                # Add to new grid cells
                self.pane_rects[pane_id] = rect
                self.add_to_grid(pane_id, rect)

            def add_to_grid(self, pane_id: str, rect: QRect):
                """Add pane to grid cells it overlaps"""

                start_x = rect.left() // self.grid_size
                end_x = rect.right() // self.grid_size
                start_y = rect.top() // self.grid_size
                end_y = rect.bottom() // self.grid_size

                for grid_x in range(start_x, end_x + 1):
                    for grid_y in range(start_y, end_y + 1):
                        grid_key = (grid_x, grid_y)
                        if grid_key not in self.grid:
                            self.grid[grid_key] = set()
                        self.grid[grid_key].add(pane_id)

            def find_panes_at_point(self, point: QPoint) -> List[str]:
                """Find panes containing a point - O(1) average case"""

                grid_x = point.x() // self.grid_size
                grid_y = point.y() // self.grid_size
                grid_key = (grid_x, grid_y)

                if grid_key not in self.grid:
                    return []

                # Check only panes in the grid cell
                candidates = self.grid[grid_key]
                result = []

                for pane_id in candidates:
                    rect = self.pane_rects[pane_id]
                    if rect.contains(point):
                        result.append(pane_id)

                return result

            def find_panes_in_region(self, region: QRect) -> List[str]:
                """Find panes overlapping a region - O(k) where k is result size"""

                start_x = region.left() // self.grid_size
                end_x = region.right() // self.grid_size
                start_y = region.top() // self.grid_size
                end_y = region.bottom() // self.grid_size

                candidates = set()
                for grid_x in range(start_x, end_x + 1):
                    for grid_y in range(start_y, end_y + 1):
                        grid_key = (grid_x, grid_y)
                        if grid_key in self.grid:
                            candidates.update(self.grid[grid_key])

                # Check actual intersection
                result = []
                for pane_id in candidates:
                    rect = self.pane_rects[pane_id]
                    if rect.intersects(region):
                        result.append(pane_id)

                return result

        # Integrate spatial index with splitter
        splitter.spatial_index = SpatialIndex()

        # Override geometry calculation to update index
        original_calculate = splitter.calculate_layout_geometry

        def calculate_with_indexing():
            geometry = original_calculate()
            for pane_id, rect in geometry.items():
                splitter.spatial_index.update_pane(pane_id, rect)
            return geometry

        splitter.calculate_layout_geometry = calculate_with_indexing

    @staticmethod
    def implement_lazy_evaluation(splitter: MultiSplitWidget):
        """Implement lazy evaluation for expensive operations"""

        class LazyCalculator:
            """Lazy calculation with invalidation"""

            def __init__(self):
                self.cached_results = {}
                self.cache_validity = {}
                self.calculation_functions = {}

            def register_calculation(self, key: str, calc_func: callable,
                                   invalidation_signals: List[str]):
                """Register a lazy calculation"""

                self.calculation_functions[key] = calc_func
                self.cached_results[key] = None
                self.cache_validity[key] = False

                # Connect to invalidation signals
                for signal_name in invalidation_signals:
                    if hasattr(splitter, signal_name):
                        signal = getattr(splitter, signal_name)
                        signal.connect(lambda k=key: self.invalidate(k))

            def get_result(self, key: str):
                """Get calculation result (lazy evaluation)"""

                if not self.cache_validity.get(key, False):
                    # Calculate and cache
                    calc_func = self.calculation_functions[key]
                    self.cached_results[key] = calc_func()
                    self.cache_validity[key] = True

                return self.cached_results[key]

            def invalidate(self, key: str):
                """Invalidate cached result"""
                self.cache_validity[key] = False

        # Add lazy calculator to splitter
        splitter.lazy_calc = LazyCalculator()

        # Register common calculations
        splitter.lazy_calc.register_calculation(
            'geometry',
            lambda: splitter.calculate_layout_geometry(),
            ['layout_changed', 'pane_resized']
        )

        splitter.lazy_calc.register_calculation(
            'focus_order',
            lambda: splitter.calculate_focus_order(),
            ['layout_changed', 'pane_added', 'pane_removed']
        )

    @staticmethod
    def implement_operation_batching(splitter: MultiSplitWidget):
        """Batch multiple operations for better performance"""

        class OperationBatcher:
            """Batch operations to reduce overhead"""

            def __init__(self):
                self.pending_operations = []
                self.batch_timer = QTimer()
                self.batch_timer.setSingleShot(True)
                self.batch_timer.timeout.connect(self.execute_batch)
                self.batch_delay = 16  # ~60 FPS

            def add_operation(self, operation: callable):
                """Add operation to batch"""

                self.pending_operations.append(operation)

                if not self.batch_timer.isActive():
                    self.batch_timer.start(self.batch_delay)

            def execute_batch(self):
                """Execute all pending operations in batch"""

                if not self.pending_operations:
                    return

                # Execute all operations
                operations = self.pending_operations.copy()
                self.pending_operations.clear()

                # Batch execution with single update
                splitter.setUpdatesEnabled(False)
                try:
                    for operation in operations:
                        operation()
                finally:
                    splitter.setUpdatesEnabled(True)
                    splitter.update()

        splitter.operation_batcher = OperationBatcher()
```

---

## Extension Architecture Patterns

### Plugin System Framework

Build a comprehensive plugin system for MultiSplit extensions:

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import importlib
import inspect

class MultiSplitPlugin(ABC):
    """Base class for MultiSplit plugins"""

    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
        self.enabled = True
        self.dependencies = []

    @abstractmethod
    def initialize(self, splitter: MultiSplitWidget) -> bool:
        """Initialize plugin with splitter instance"""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Clean up plugin resources"""
        pass

    def get_commands(self) -> Dict[str, callable]:
        """Return commands provided by this plugin"""
        return {}

    def get_renderers(self) -> Dict[str, callable]:
        """Return custom renderers provided by this plugin"""
        return {}

    def get_menu_items(self) -> List[dict]:
        """Return menu items for integration"""
        return []

    def on_pane_created(self, pane_id: str, widget_id: str) -> None:
        """Called when a pane is created"""
        pass

    def on_pane_focused(self, pane_id: str) -> None:
        """Called when a pane receives focus"""
        pass

    def on_layout_changed(self) -> None:
        """Called when layout structure changes"""
        pass

class PluginManager:
    """Manage MultiSplit plugins"""

    def __init__(self, splitter: MultiSplitWidget):
        self.splitter = splitter
        self.plugins: Dict[str, MultiSplitPlugin] = {}
        self.plugin_paths = []
        self.command_registry = {}
        self.renderer_registry = {}

        # Connect to splitter signals
        self.splitter.pane_created.connect(self.on_pane_created)
        self.splitter.pane_focused.connect(self.on_pane_focused)
        self.splitter.layout_changed.connect(self.on_layout_changed)

    def add_plugin_path(self, path: str):
        """Add path to search for plugins"""
        self.plugin_paths.append(path)

    def load_plugin(self, plugin_name: str) -> bool:
        """Load a plugin by name"""

        try:
            # Try to import plugin module
            module = None
            for path in self.plugin_paths:
                try:
                    spec = importlib.util.spec_from_file_location(
                        plugin_name,
                        f"{path}/{plugin_name}.py"
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    break
                except:
                    continue

            if module is None:
                print(f"Plugin module not found: {plugin_name}")
                return False

            # Find plugin class
            plugin_classes = []
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and
                    issubclass(obj, MultiSplitPlugin) and
                    obj != MultiSplitPlugin):
                    plugin_classes.append(obj)

            if not plugin_classes:
                print(f"No plugin class found in {plugin_name}")
                return False

            # Instantiate plugin
            plugin_class = plugin_classes[0]
            plugin = plugin_class()

            # Check dependencies
            if not self.check_dependencies(plugin):
                print(f"Dependencies not met for {plugin_name}")
                return False

            # Initialize plugin
            if plugin.initialize(self.splitter):
                self.plugins[plugin_name] = plugin
                self.register_plugin_features(plugin)
                print(f"Loaded plugin: {plugin_name}")
                return True
            else:
                print(f"Failed to initialize plugin: {plugin_name}")
                return False

        except Exception as e:
            print(f"Error loading plugin {plugin_name}: {e}")
            return False

    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin"""

        if plugin_name not in self.plugins:
            return False

        plugin = self.plugins[plugin_name]

        try:
            # Cleanup plugin
            plugin.cleanup()

            # Unregister features
            self.unregister_plugin_features(plugin)

            # Remove from registry
            del self.plugins[plugin_name]

            print(f"Unloaded plugin: {plugin_name}")
            return True

        except Exception as e:
            print(f"Error unloading plugin {plugin_name}: {e}")
            return False

    def register_plugin_features(self, plugin: MultiSplitPlugin):
        """Register plugin's commands and renderers"""

        # Register commands
        commands = plugin.get_commands()
        for cmd_name, cmd_func in commands.items():
            self.command_registry[cmd_name] = cmd_func

        # Register renderers
        renderers = plugin.get_renderers()
        for renderer_name, renderer_func in renderers.items():
            self.renderer_registry[renderer_name] = renderer_func

    def execute_command(self, command_name: str, *args, **kwargs) -> Any:
        """Execute a plugin command"""

        if command_name in self.command_registry:
            return self.command_registry[command_name](*args, **kwargs)
        else:
            raise ValueError(f"Unknown command: {command_name}")

    def get_renderer(self, renderer_name: str) -> Optional[callable]:
        """Get a plugin renderer"""
        return self.renderer_registry.get(renderer_name)

    # Plugin event handlers
    def on_pane_created(self, pane_id: str, widget_id: str):
        for plugin in self.plugins.values():
            if plugin.enabled:
                plugin.on_pane_created(pane_id, widget_id)

    def on_pane_focused(self, pane_id: str):
        for plugin in self.plugins.values():
            if plugin.enabled:
                plugin.on_pane_focused(pane_id)

    def on_layout_changed(self):
        for plugin in self.plugins.values():
            if plugin.enabled:
                plugin.on_layout_changed()

# Example plugins

class GridLayoutPlugin(MultiSplitPlugin):
    """Plugin that adds grid layout functionality"""

    def __init__(self):
        super().__init__("GridLayout", "1.0")

    def initialize(self, splitter: MultiSplitWidget) -> bool:
        self.splitter = splitter
        return True

    def cleanup(self) -> None:
        pass

    def get_commands(self) -> Dict[str, callable]:
        return {
            'create_grid': self.create_grid_layout,
            'resize_grid': self.resize_grid_layout
        }

    def create_grid_layout(self, rows: int, cols: int, widget_ids: List[str]):
        """Create a grid layout"""

        if rows * cols != len(widget_ids):
            raise ValueError("Widget count must equal rows × cols")

        # Generate grid structure
        layout = self.generate_grid_structure(rows, cols, widget_ids)

        # Apply to splitter
        self.splitter.restore_layout(layout)

    def generate_grid_structure(self, rows: int, cols: int,
                               widget_ids: List[str]) -> dict:
        """Generate grid layout structure"""

        # Create panes for widgets
        panes = []
        for i, widget_id in enumerate(widget_ids):
            panes.append({
                "type": "leaf",
                "pane_id": f"grid_pane_{i}",
                "widget_id": widget_id
            })

        # Build row splits
        row_splits = []
        for r in range(rows):
            row_panes = panes[r * cols:(r + 1) * cols]

            if cols == 1:
                row_splits.append(row_panes[0])
            else:
                row_split = {
                    "type": "split",
                    "orientation": "horizontal",
                    "ratios": [1.0 / cols] * cols,
                    "children": row_panes
                }
                row_splits.append(row_split)

        # Combine rows
        if rows == 1:
            return row_splits[0]
        else:
            return {
                "type": "split",
                "orientation": "vertical",
                "ratios": [1.0 / rows] * rows,
                "children": row_splits
            }

class SessionManagerPlugin(MultiSplitPlugin):
    """Plugin for session management"""

    def __init__(self):
        super().__init__("SessionManager", "1.0")
        self.sessions = {}

    def initialize(self, splitter: MultiSplitWidget) -> bool:
        self.splitter = splitter
        return True

    def cleanup(self) -> None:
        pass

    def get_commands(self) -> Dict[str, callable]:
        return {
            'save_session': self.save_session,
            'load_session': self.load_session,
            'list_sessions': self.list_sessions
        }

    def save_session(self, session_name: str):
        """Save current layout as a session"""

        layout = self.splitter.save_layout()
        self.sessions[session_name] = {
            'layout': layout,
            'timestamp': time.time()
        }

    def load_session(self, session_name: str):
        """Load a saved session"""

        if session_name not in self.sessions:
            raise ValueError(f"Session not found: {session_name}")

        session = self.sessions[session_name]
        self.splitter.restore_layout(session['layout'])

    def list_sessions(self) -> List[dict]:
        """List all saved sessions"""

        return [
            {
                'name': name,
                'timestamp': session['timestamp']
            }
            for name, session in self.sessions.items()
        ]
```

### Custom Command Development

Develop sophisticated custom commands with full undo support:

```python
class CustomCommand(ABC):
    """Base class for custom MultiSplit commands"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.can_undo = True
        self.undo_data = None

    @abstractmethod
    def execute(self, splitter: MultiSplitWidget, *args, **kwargs) -> Any:
        """Execute the command"""
        pass

    @abstractmethod
    def undo(self, splitter: MultiSplitWidget) -> bool:
        """Undo the command"""
        pass

    def can_execute(self, splitter: MultiSplitWidget, *args, **kwargs) -> bool:
        """Check if command can be executed"""
        return True

    def validate_parameters(self, *args, **kwargs) -> bool:
        """Validate command parameters"""
        return True

class AdvancedSplitCommand(CustomCommand):
    """Advanced split command with custom positioning"""

    def __init__(self):
        super().__init__("advanced_split", "Split pane with advanced options")

    def execute(self, splitter: MultiSplitWidget, pane_id: str,
               split_type: str, ratio: float = 0.5,
               widget_id: str = None, **options) -> str:
        """Execute advanced split"""

        # Validate parameters
        if not self.validate_parameters(pane_id, split_type, ratio, widget_id):
            raise ValueError("Invalid parameters")

        # Save current state for undo
        self.undo_data = {
            'layout': splitter.save_layout(),
            'focus': splitter.current_pane_id
        }

        # Execute split based on type
        if split_type == "golden_ratio":
            return self.split_golden_ratio(splitter, pane_id, widget_id, options)
        elif split_type == "proportional":
            return self.split_proportional(splitter, pane_id, ratio, widget_id)
        elif split_type == "adaptive":
            return self.split_adaptive(splitter, pane_id, widget_id, options)
        else:
            raise ValueError(f"Unknown split type: {split_type}")

    def split_golden_ratio(self, splitter: MultiSplitWidget, pane_id: str,
                          widget_id: str, options: dict) -> str:
        """Split using golden ratio (1.618)"""

        phi = 1.618
        main_ratio = phi / (1 + phi)  # ≈ 0.618

        # Determine orientation based on current pane size
        pane_rect = splitter.get_pane_rect(pane_id)
        if pane_rect.width() > pane_rect.height():
            where = WherePosition.RIGHT
        else:
            where = WherePosition.BOTTOM

        # Create widget
        widget = splitter.widget_provider.provide_widget(widget_id, pane_id)

        # Execute split
        new_pane_id = splitter.split_with_widget(pane_id, where, widget, widget_id)

        # Adjust ratios to golden ratio
        parent_split = splitter.find_parent_split(pane_id)
        if parent_split:
            child_index = parent_split.get_child_index(pane_id)
            parent_split.ratios[child_index] = main_ratio
            parent_split.ratios[child_index + 1] = 1 - main_ratio

        return new_pane_id

    def split_adaptive(self, splitter: MultiSplitWidget, pane_id: str,
                      widget_id: str, options: dict) -> str:
        """Adaptive split based on content and context"""

        # Analyze current pane content
        current_widget = splitter.get_widget_for_pane(pane_id)
        current_widget_id = splitter.get_widget_id_for_pane(pane_id)

        # Determine optimal split direction
        pane_rect = splitter.get_pane_rect(pane_id)
        aspect_ratio = pane_rect.width() / pane_rect.height()

        # Smart positioning based on widget types
        if current_widget_id.startswith("editor:") and widget_id.startswith("terminal:"):
            # Editor + terminal: split horizontally (terminal at bottom)
            where = WherePosition.BOTTOM
            ratio = 0.7  # Give more space to editor
        elif current_widget_id.startswith("file_tree") and widget_id.startswith("editor:"):
            # File tree + editor: split vertically (editor on right)
            where = WherePosition.RIGHT
            ratio = 0.3  # File tree takes less space
        elif aspect_ratio > 1.5:
            # Wide pane: split vertically
            where = WherePosition.RIGHT
            ratio = 0.5
        else:
            # Tall pane: split horizontally
            where = WherePosition.BOTTOM
            ratio = 0.5

        # Execute split
        widget = splitter.widget_provider.provide_widget(widget_id, pane_id)
        new_pane_id = splitter.split_with_widget(pane_id, where, widget, widget_id)

        # Apply calculated ratio
        parent_split = splitter.find_parent_split(pane_id)
        if parent_split:
            child_index = parent_split.get_child_index(pane_id)
            parent_split.ratios[child_index] = ratio
            parent_split.ratios[child_index + 1] = 1 - ratio

        return new_pane_id

    def undo(self, splitter: MultiSplitWidget) -> bool:
        """Undo the advanced split"""

        if not self.undo_data:
            return False

        try:
            # Restore layout
            splitter.restore_layout(self.undo_data['layout'])

            # Restore focus
            if self.undo_data['focus']:
                splitter.focus_pane(self.undo_data['focus'])

            return True

        except Exception as e:
            print(f"Failed to undo advanced split: {e}")
            return False

class WorkspaceLayoutCommand(CustomCommand):
    """Command to apply workspace layouts"""

    def __init__(self):
        super().__init__("workspace_layout", "Apply predefined workspace layout")
        self.layout_templates = self.load_layout_templates()

    def execute(self, splitter: MultiSplitWidget, layout_name: str,
               widget_mappings: Dict[str, str] = None) -> bool:
        """Apply workspace layout"""

        if layout_name not in self.layout_templates:
            raise ValueError(f"Unknown layout: {layout_name}")

        # Save current state
        self.undo_data = {
            'layout': splitter.save_layout(),
            'focus': splitter.current_pane_id
        }

        # Get template
        template = self.layout_templates[layout_name].copy()

        # Apply widget mappings
        if widget_mappings:
            self.apply_widget_mappings(template, widget_mappings)

        # Apply layout
        splitter.restore_layout(template)

        return True

    def load_layout_templates(self) -> Dict[str, dict]:
        """Load predefined layout templates"""

        return {
            "ide": {
                "type": "split",
                "orientation": "horizontal",
                "ratios": [0.2, 0.8],
                "children": [
                    {
                        "type": "leaf",
                        "pane_id": "sidebar",
                        "widget_id": "file_tree"
                    },
                    {
                        "type": "split",
                        "orientation": "vertical",
                        "ratios": [0.7, 0.3],
                        "children": [
                            {
                                "type": "leaf",
                                "pane_id": "main_editor",
                                "widget_id": "editor:main"
                            },
                            {
                                "type": "leaf",
                                "pane_id": "terminal",
                                "widget_id": "terminal:main"
                            }
                        ]
                    }
                ]
            },

            "dashboard": {
                "type": "split",
                "orientation": "vertical",
                "ratios": [0.3, 0.7],
                "children": [
                    {
                        "type": "leaf",
                        "pane_id": "controls",
                        "widget_id": "control_panel"
                    },
                    {
                        "type": "split",
                        "orientation": "horizontal",
                        "ratios": [0.6, 0.4],
                        "children": [
                            {
                                "type": "leaf",
                                "pane_id": "main_plot",
                                "widget_id": "plot:main"
                            },
                            {
                                "type": "split",
                                "orientation": "vertical",
                                "ratios": [0.5, 0.5],
                                "children": [
                                    {
                                        "type": "leaf",
                                        "pane_id": "secondary_plot",
                                        "widget_id": "plot:secondary"
                                    },
                                    {
                                        "type": "leaf",
                                        "pane_id": "data_table",
                                        "widget_id": "table:data"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }

    def apply_widget_mappings(self, layout: dict, mappings: Dict[str, str]):
        """Apply widget ID mappings to layout template"""

        if layout['type'] == 'leaf':
            widget_id = layout.get('widget_id')
            if widget_id in mappings:
                layout['widget_id'] = mappings[widget_id]
        else:
            for child in layout.get('children', []):
                self.apply_widget_mappings(child, mappings)

    def undo(self, splitter: MultiSplitWidget) -> bool:
        """Undo workspace layout application"""

        if not self.undo_data:
            return False

        try:
            splitter.restore_layout(self.undo_data['layout'])
            if self.undo_data['focus']:
                splitter.focus_pane(self.undo_data['focus'])
            return True
        except:
            return False

class CommandRegistry:
    """Registry for custom commands"""

    def __init__(self, splitter: MultiSplitWidget):
        self.splitter = splitter
        self.commands: Dict[str, CustomCommand] = {}
        self.command_history = []
        self.max_history = 100

    def register_command(self, command: CustomCommand):
        """Register a custom command"""
        self.commands[command.name] = command

    def execute_command(self, command_name: str, *args, **kwargs) -> Any:
        """Execute a registered command"""

        if command_name not in self.commands:
            raise ValueError(f"Unknown command: {command_name}")

        command = self.commands[command_name]

        # Validate execution
        if not command.can_execute(self.splitter, *args, **kwargs):
            raise RuntimeError(f"Cannot execute command: {command_name}")

        # Execute command
        result = command.execute(self.splitter, *args, **kwargs)

        # Add to history for undo
        if command.can_undo:
            self.command_history.append(command)
            if len(self.command_history) > self.max_history:
                self.command_history.pop(0)

        return result

    def undo_last_command(self) -> bool:
        """Undo the last executed command"""

        if not self.command_history:
            return False

        command = self.command_history.pop()
        return command.undo(self.splitter)
```

---

## Renderer Extensions

### Custom Drawing System

Create sophisticated custom renderers for visual effects:

```python
class CustomRenderer(ABC):
    """Base class for custom MultiSplit renderers"""

    def __init__(self, name: str):
        self.name = name
        self.enabled = True

    @abstractmethod
    def render(self, painter: QPainter, rect: QRect, context: dict) -> None:
        """Render custom content"""
        pass

    def can_render(self, context: dict) -> bool:
        """Check if this renderer can handle the context"""
        return True

class AnimatedDividerRenderer(CustomRenderer):
    """Renderer with animated divider effects"""

    def __init__(self):
        super().__init__("animated_divider")
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_value = 0.0
        self.animation_direction = 1
        self.animation_speed = 0.05

    def render(self, painter: QPainter, rect: QRect, context: dict) -> None:
        """Render animated divider"""

        painter.save()

        # Base divider
        base_color = context.get('base_color', QColor(200, 200, 200))
        painter.fillRect(rect, base_color)

        # Animated highlight
        if context.get('state') == 'hover':
            self.start_animation()
            highlight_color = QColor(100, 150, 255, int(100 * self.animation_value))

            # Create gradient effect
            gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
            gradient.setColorAt(0, highlight_color)
            gradient.setColorAt(0.5, highlight_color.lighter(150))
            gradient.setColorAt(1, highlight_color)

            painter.fillRect(rect, gradient)

        # Pulse effect during drag
        elif context.get('state') == 'drag':
            self.start_animation()
            pulse_color = QColor(255, 100, 100, int(150 * abs(math.sin(self.animation_value * math.pi))))
            painter.fillRect(rect, pulse_color)

        painter.restore()

    def start_animation(self):
        """Start animation timer"""
        if not self.animation_timer.isActive():
            self.animation_timer.start(50)  # 20 FPS

    def update_animation(self):
        """Update animation frame"""

        self.animation_value += self.animation_direction * self.animation_speed

        if self.animation_value >= 1.0:
            self.animation_value = 1.0
            self.animation_direction = -1
        elif self.animation_value <= 0.0:
            self.animation_value = 0.0
            self.animation_direction = 1

        # Request repaint
        # Note: In real implementation, would need reference to widget
        # self.widget.update()

class ThemeAwareRenderer(CustomRenderer):
    """Renderer that adapts to system themes"""

    def __init__(self):
        super().__init__("theme_aware")
        self.current_theme = self.detect_system_theme()

    def render(self, painter: QPainter, rect: QRect, context: dict) -> None:
        """Render with theme awareness"""

        painter.save()

        # Get theme-appropriate colors
        colors = self.get_theme_colors()

        # Base styling
        if context.get('type') == 'divider':
            color = colors['divider']
            if context.get('state') == 'hover':
                color = colors['divider_hover']
            elif context.get('state') == 'drag':
                color = colors['divider_active']

            painter.fillRect(rect, color)

            # Add subtle shadow effect
            if self.current_theme == 'dark':
                shadow_color = QColor(0, 0, 0, 50)
                shadow_rect = rect.adjusted(1, 1, 1, 1)
                painter.fillRect(shadow_rect, shadow_color)

        elif context.get('type') == 'focus_indicator':
            # Theme-aware focus ring
            focus_color = colors['accent']
            pen = QPen(focus_color, 2)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(rect.adjusted(1, 1, -1, -1))

        painter.restore()

    def detect_system_theme(self) -> str:
        """Detect system theme (light/dark)"""

        # Platform-specific theme detection
        try:
            if sys.platform == "darwin":  # macOS
                return self.detect_macos_theme()
            elif sys.platform == "win32":  # Windows
                return self.detect_windows_theme()
            else:  # Linux/Unix
                return self.detect_linux_theme()
        except:
            return "light"  # Fallback

    def get_theme_colors(self) -> Dict[str, QColor]:
        """Get colors for current theme"""

        if self.current_theme == 'dark':
            return {
                'divider': QColor(60, 60, 60),
                'divider_hover': QColor(80, 80, 80),
                'divider_active': QColor(100, 150, 255),
                'accent': QColor(100, 150, 255),
                'background': QColor(30, 30, 30),
                'text': QColor(240, 240, 240)
            }
        else:
            return {
                'divider': QColor(200, 200, 200),
                'divider_hover': QColor(160, 160, 160),
                'divider_active': QColor(0, 120, 215),
                'accent': QColor(0, 120, 215),
                'background': QColor(255, 255, 255),
                'text': QColor(0, 0, 0)
            }

class EffectsRenderer(CustomRenderer):
    """Renderer with advanced visual effects"""

    def __init__(self):
        super().__init__("effects")
        self.effect_cache = {}

    def render(self, painter: QPainter, rect: QRect, context: dict) -> None:
        """Render with visual effects"""

        effect_type = context.get('effect', 'none')

        if effect_type == 'glow':
            self.render_glow_effect(painter, rect, context)
        elif effect_type == 'blur':
            self.render_blur_effect(painter, rect, context)
        elif effect_type == 'gradient':
            self.render_gradient_effect(painter, rect, context)
        elif effect_type == 'texture':
            self.render_texture_effect(painter, rect, context)

    def render_glow_effect(self, painter: QPainter, rect: QRect, context: dict):
        """Render glow effect around element"""

        painter.save()

        glow_color = context.get('glow_color', QColor(100, 150, 255))
        glow_radius = context.get('glow_radius', 10)

        # Create glow using multiple transparent rectangles
        for i in range(glow_radius):
            alpha = int(255 * (1 - i / glow_radius) ** 2)
            glow_color.setAlpha(alpha)

            glow_rect = rect.adjusted(-i, -i, i, i)
            painter.fillRect(glow_rect, glow_color)

        painter.restore()

    def render_gradient_effect(self, painter: QPainter, rect: QRect, context: dict):
        """Render gradient effects"""

        painter.save()

        gradient_type = context.get('gradient_type', 'linear')
        colors = context.get('colors', [QColor(255, 255, 255), QColor(0, 0, 0)])

        if gradient_type == 'linear':
            gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        elif gradient_type == 'radial':
            gradient = QRadialGradient(rect.center(), rect.width() / 2)
        else:
            gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())

        # Add color stops
        for i, color in enumerate(colors):
            stop = i / (len(colors) - 1) if len(colors) > 1 else 0
            gradient.setColorAt(stop, color)

        painter.fillRect(rect, gradient)
        painter.restore()

    def render_texture_effect(self, painter: QPainter, rect: QRect, context: dict):
        """Render texture patterns"""

        painter.save()

        texture_type = context.get('texture_type', 'dots')

        if texture_type == 'dots':
            self.render_dot_pattern(painter, rect, context)
        elif texture_type == 'lines':
            self.render_line_pattern(painter, rect, context)
        elif texture_type == 'grid':
            self.render_grid_pattern(painter, rect, context)

        painter.restore()

    def render_dot_pattern(self, painter: QPainter, rect: QRect, context: dict):
        """Render dot texture pattern"""

        dot_color = context.get('dot_color', QColor(128, 128, 128, 100))
        dot_size = context.get('dot_size', 3)
        dot_spacing = context.get('dot_spacing', 10)

        painter.setPen(Qt.NoPen)
        painter.setBrush(dot_color)

        y = rect.top()
        while y < rect.bottom():
            x = rect.left()
            while x < rect.right():
                painter.drawEllipse(x, y, dot_size, dot_size)
                x += dot_spacing
            y += dot_spacing

class RendererManager:
    """Manage custom renderers"""

    def __init__(self):
        self.renderers: Dict[str, CustomRenderer] = {}
        self.render_contexts = {}

    def register_renderer(self, renderer: CustomRenderer):
        """Register a custom renderer"""
        self.renderers[renderer.name] = renderer

    def render_element(self, element_type: str, painter: QPainter,
                      rect: QRect, context: dict = None):
        """Render element using appropriate renderer"""

        if context is None:
            context = {}

        context['type'] = element_type

        # Find appropriate renderer
        for renderer in self.renderers.values():
            if renderer.enabled and renderer.can_render(context):
                renderer.render(painter, rect, context)
                break
        else:
            # Fall back to default rendering
            self.default_render(painter, rect, context)

    def default_render(self, painter: QPainter, rect: QRect, context: dict):
        """Default rendering when no custom renderer available"""

        element_type = context.get('type', 'unknown')

        if element_type == 'divider':
            color = QColor(200, 200, 200)
            painter.fillRect(rect, color)
        elif element_type == 'focus_indicator':
            pen = QPen(QColor(0, 120, 215), 2)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(rect)
```

---

## Framework Integration

### Embedding in Larger Systems

Integrate MultiSplit into larger application frameworks:

```python
class FrameworkAdapter(ABC):
    """Base adapter for framework integration"""

    @abstractmethod
    def integrate_multisplit(self, splitter: MultiSplitWidget) -> bool:
        """Integrate MultiSplit into framework"""
        pass

    @abstractmethod
    def handle_framework_events(self, event_type: str, event_data: dict) -> None:
        """Handle framework-specific events"""
        pass

class DockingSystemAdapter(FrameworkAdapter):
    """Adapter for docking systems (like Qt Dock Widgets)"""

    def __init__(self):
        self.dock_widgets = {}
        self.multisplit_docks = {}

    def integrate_multisplit(self, splitter: MultiSplitWidget) -> bool:
        """Integrate MultiSplit as dockable component"""

        # Create dock widget for MultiSplit
        dock = QDockWidget("MultiSplit Layout")
        dock.setWidget(splitter)

        # Allow docking in all areas
        dock.setAllowedAreas(Qt.AllDockWidgetAreas)

        # Store reference
        self.multisplit_docks[splitter] = dock

        return True

    def add_to_main_window(self, main_window: QMainWindow,
                          splitter: MultiSplitWidget,
                          area: Qt.DockWidgetArea = Qt.CentralDockWidgetArea):
        """Add MultiSplit dock to main window"""

        if splitter not in self.multisplit_docks:
            self.integrate_multisplit(splitter)

        dock = self.multisplit_docks[splitter]
        main_window.addDockWidget(area, dock)

    def handle_framework_events(self, event_type: str, event_data: dict) -> None:
        """Handle docking system events"""

        if event_type == "dock_moved":
            # Handle dock widget movement
            self.on_dock_moved(event_data)
        elif event_type == "dock_resized":
            # Handle dock widget resizing
            self.on_dock_resized(event_data)

class PluginSystemAdapter(FrameworkAdapter):
    """Adapter for plugin-based applications"""

    def __init__(self, plugin_manager):
        self.plugin_manager = plugin_manager
        self.multisplit_instances = {}

    def integrate_multisplit(self, splitter: MultiSplitWidget) -> bool:
        """Register MultiSplit with plugin system"""

        # Register as service
        self.plugin_manager.register_service(
            'multisplit_layout',
            splitter,
            interfaces=['ILayoutManager', 'IPaneContainer']
        )

        # Register event handlers
        self.plugin_manager.register_event_handler(
            'pane_created',
            lambda event: self.handle_pane_event(splitter, event)
        )

        self.multisplit_instances[id(splitter)] = splitter
        return True

    def handle_framework_events(self, event_type: str, event_data: dict) -> None:
        """Handle plugin system events"""

        if event_type == "plugin_loaded":
            self.on_plugin_loaded(event_data)
        elif event_type == "plugin_unloaded":
            self.on_plugin_unloaded(event_data)

    def on_plugin_loaded(self, plugin_data: dict):
        """Handle plugin loading"""

        plugin = plugin_data['plugin']

        # Check if plugin provides widgets
        if hasattr(plugin, 'get_widget_types'):
            widget_types = plugin.get_widget_types()

            # Register widget types with all MultiSplit instances
            for splitter in self.multisplit_instances.values():
                provider = splitter.widget_provider
                if hasattr(provider, 'register_widget_types'):
                    provider.register_widget_types(widget_types)

class MVVMAdapter(FrameworkAdapter):
    """Adapter for MVVM (Model-View-ViewModel) frameworks"""

    def __init__(self):
        self.view_models = {}
        self.data_bindings = {}

    def integrate_multisplit(self, splitter: MultiSplitWidget) -> bool:
        """Integrate with MVVM framework"""

        # Create view model for layout
        layout_vm = LayoutViewModel(splitter)
        self.view_models[splitter] = layout_vm

        # Setup data binding
        self.setup_data_binding(splitter, layout_vm)

        return True

    def setup_data_binding(self, splitter: MultiSplitWidget, view_model):
        """Setup two-way data binding"""

        # Bind layout changes to view model
        splitter.layout_changed.connect(
            lambda: view_model.update_layout(splitter.save_layout())
        )

        # Bind view model changes to layout
        view_model.layout_changed.connect(
            lambda layout: splitter.restore_layout(layout)
        )

        # Bind focus changes
        splitter.pane_focused.connect(view_model.set_focused_pane)
        view_model.focused_pane_changed.connect(splitter.focus_pane)

    def handle_framework_events(self, event_type: str, event_data: dict) -> None:
        """Handle MVVM framework events"""

        if event_type == "model_changed":
            self.sync_model_to_view(event_data)
        elif event_type == "view_changed":
            self.sync_view_to_model(event_data)

class LayoutViewModel(QObject):
    """View model for MultiSplit layout"""

    layout_changed = Signal(dict)
    focused_pane_changed = Signal(str)
    pane_added = Signal(str, str)  # pane_id, widget_id
    pane_removed = Signal(str)

    def __init__(self, splitter: MultiSplitWidget):
        super().__init__()
        self.splitter = splitter
        self._layout = {}
        self._focused_pane = None

    @property
    def layout(self) -> dict:
        return self._layout

    @layout.setter
    def layout(self, value: dict):
        if self._layout != value:
            self._layout = value
            self.layout_changed.emit(value)

    @property
    def focused_pane(self) -> str:
        return self._focused_pane

    @focused_pane.setter
    def focused_pane(self, value: str):
        if self._focused_pane != value:
            self._focused_pane = value
            self.focused_pane_changed.emit(value)

    def update_layout(self, layout: dict):
        """Update layout from splitter"""
        self.layout = layout

    def set_focused_pane(self, pane_id: str):
        """Set focused pane from splitter"""
        self.focused_pane = pane_id

    def add_pane(self, widget_id: str, position: str):
        """Add pane through view model"""
        # Implementation would trigger splitter operations
        pass

    def remove_pane(self, pane_id: str):
        """Remove pane through view model"""
        # Implementation would trigger splitter operations
        pass

class IntegrationManager:
    """Manage different framework integrations"""

    def __init__(self):
        self.adapters: Dict[str, FrameworkAdapter] = {}
        self.active_integrations = {}

    def register_adapter(self, framework_name: str, adapter: FrameworkAdapter):
        """Register framework adapter"""
        self.adapters[framework_name] = adapter

    def integrate_with_framework(self, framework_name: str,
                                splitter: MultiSplitWidget,
                                **integration_options) -> bool:
        """Integrate MultiSplit with specified framework"""

        if framework_name not in self.adapters:
            raise ValueError(f"No adapter for framework: {framework_name}")

        adapter = self.adapters[framework_name]
        success = adapter.integrate_multisplit(splitter)

        if success:
            self.active_integrations[splitter] = {
                'framework': framework_name,
                'adapter': adapter,
                'options': integration_options
            }

        return success

    def handle_framework_event(self, event_type: str, event_data: dict):
        """Route framework events to appropriate adapters"""

        for integration in self.active_integrations.values():
            adapter = integration['adapter']
            adapter.handle_framework_events(event_type, event_data)
```

---

## Common Pitfalls

### Pitfall 1: Inefficient Tree Traversal

**Problem**: Using linear search instead of leveraging tree structure
```python
# ❌ BAD: O(n) search for every operation
def find_pane_badly(tree: dict, target_id: str) -> dict:
    all_nodes = []
    flatten_tree(tree, all_nodes)  # O(n) traversal
    for node in all_nodes:  # O(n) search
        if node.get('pane_id') == target_id:
            return node
    return None
```

**Solution**: Use path-based navigation
```python
# ✅ GOOD: O(log n) tree traversal
def find_pane_efficiently(tree: dict, target_id: str) -> dict:
    def search_tree(node: dict, path: List[str]) -> Optional[dict]:
        if node['type'] == 'leaf' and node['pane_id'] == target_id:
            return node
        if node['type'] == 'split':
            for child in node['children']:
                result = search_tree(child, path + [child['pane_id']])
                if result:
                    return result
        return None

    return search_tree(tree, [])
```

### Pitfall 2: Creating Expensive Extensions

**Problem**: Extension that blocks the UI
```python
# ❌ BAD: Blocking extension
class BadExtension:
    def on_layout_changed(self):
        # This runs on every layout change!
        expensive_analysis()  # Blocks UI for seconds
        complex_calculation()
        network_request()  # Synchronous network call
```

**Solution**: Use async processing and throttling
```python
# ✅ GOOD: Non-blocking extension
class GoodExtension:
    def __init__(self):
        self.analysis_timer = QTimer()
        self.analysis_timer.setSingleShot(True)
        self.analysis_timer.timeout.connect(self.perform_analysis)

    def on_layout_changed(self):
        # Throttle analysis - only run after changes stop
        self.analysis_timer.start(500)  # 500ms delay

    def perform_analysis(self):
        # Run in background thread
        QtConcurrent.run(self.expensive_analysis)
```

### Pitfall 3: Memory Leaks in Renderers

**Problem**: Renderer that accumulates resources
```python
# ❌ BAD: Resource accumulation
class LeakyRenderer:
    def __init__(self):
        self.cached_pixmaps = {}  # Never cleared!

    def render(self, painter, rect, context):
        key = f"{rect.width()}x{rect.height()}"
        if key not in self.cached_pixmaps:
            pixmap = create_expensive_pixmap(rect.size())
            self.cached_pixmaps[key] = pixmap  # Memory leak!
        painter.drawPixmap(rect, self.cached_pixmaps[key])
```

**Solution**: Implement resource management
```python
# ✅ GOOD: Bounded cache with cleanup
class ManagedRenderer:
    def __init__(self):
        self.cached_pixmaps = {}
        self.cache_usage = {}
        self.max_cache_size = 20

    def render(self, painter, rect, context):
        key = f"{rect.width()}x{rect.height()}"

        if key not in self.cached_pixmaps:
            self.cleanup_cache_if_needed()
            pixmap = create_expensive_pixmap(rect.size())
            self.cached_pixmaps[key] = pixmap

        self.cache_usage[key] = time.time()
        painter.drawPixmap(rect, self.cached_pixmaps[key])

    def cleanup_cache_if_needed(self):
        if len(self.cached_pixmaps) >= self.max_cache_size:
            # Remove least recently used
            oldest_key = min(self.cache_usage.keys(),
                           key=lambda k: self.cache_usage[k])
            del self.cached_pixmaps[oldest_key]
            del self.cache_usage[oldest_key]
```

### Pitfall 4: Poor Error Handling in Extensions

**Problem**: Extension crashes break the entire system
```python
# ❌ BAD: No error handling
class CrashyExtension:
    def execute_command(self, command_name: str, *args):
        command = self.commands[command_name]  # KeyError possible!
        return command.execute(*args)  # Any exception crashes UI
```

**Solution**: Comprehensive error handling
```python
# ✅ GOOD: Robust error handling
class RobustExtension:
    def execute_command(self, command_name: str, *args):
        try:
            if command_name not in self.commands:
                raise ValueError(f"Unknown command: {command_name}")

            command = self.commands[command_name]
            return command.execute(*args)

        except Exception as e:
            self.handle_extension_error(f"Command execution failed: {e}")
            return None

    def handle_extension_error(self, error_msg: str):
        # Log error but don't crash
        print(f"Extension error: {error_msg}")

        # Optionally show user-friendly error
        QMessageBox.warning(None, "Extension Error",
                          f"An extension encountered an error:\n{error_msg}")
```

### Pitfall 5: Not Considering Performance Impact

**Problem**: Extension that creates performance bottlenecks
```python
# ❌ BAD: Performance-killing extension
class SlowExtension:
    def on_pane_focused(self, pane_id: str):
        # Called on every focus change!
        all_panes = self.splitter.get_all_panes()  # O(n)
        for other_pane in all_panes:  # O(n) loop
            self.update_pane_relationships(other_pane)  # O(n) operation
        # Total: O(n²) on every focus change!
```

**Solution**: Optimize for common operations
```python
# ✅ GOOD: Performance-aware extension
class FastExtension:
    def __init__(self):
        self.pane_relationships = {}  # Cache relationships
        self.focus_update_timer = QTimer()
        self.focus_update_timer.setSingleShot(True)
        self.focus_update_timer.timeout.connect(self.batch_update_relationships)

    def on_pane_focused(self, pane_id: str):
        # Just note that update is needed
        self.pending_focus_update = pane_id

        # Batch updates to avoid frequent recalculation
        if not self.focus_update_timer.isActive():
            self.focus_update_timer.start(50)  # 50ms delay

    def batch_update_relationships(self):
        # Only update relationships for focused pane
        if hasattr(self, 'pending_focus_update'):
            self.update_pane_relationships(self.pending_focus_update)
```

---

## Quick Reference

### Performance Complexity Guide

| Operation Type | Target Complexity | Optimization Strategy |
|---------------|------------------|----------------------|
| Tree navigation | O(log n) | Use balanced trees, path caching |
| Widget lookup | O(1) | Hash tables, direct references |
| Geometry calculation | O(n) | Viewport culling, lazy evaluation |
| Focus navigation | O(1) to O(log n) | Spatial indexing, adjacency maps |
| Layout persistence | O(n) | Incremental serialization |

### Extension Development Checklist

| Component | Requirements | Best Practices |
|-----------|-------------|----------------|
| Commands | Validation, undo support | Parameter checking, atomic operations |
| Renderers | Resource management | Bounded caches, cleanup timers |
| Plugins | Error handling | Isolation, graceful degradation |
| Framework adapters | Event handling | Async processing, batching |
| Performance monitoring | Profiling hooks | Complexity analysis, benchmarking |

### Optimization Patterns

| Pattern | Use Case | Implementation |
|---------|----------|---------------|
| Spatial indexing | Point/region queries | Grid-based lookup, O(1) average |
| Lazy evaluation | Expensive calculations | Cache with invalidation |
| Operation batching | Frequent updates | Timer-based batching |
| Resource pooling | Object creation | Pre-allocated object pools |
| Viewport culling | Large layouts | Visible-only processing |

### Integration Strategies

| Framework Type | Adapter Pattern | Key Considerations |
|---------------|----------------|-------------------|
| Docking systems | Widget wrapping | Dock widget compatibility |
| Plugin systems | Service registration | Event routing, lifecycle |
| MVVM frameworks | Data binding | Two-way synchronization |
| Web frameworks | Bridge interfaces | JSON serialization |
| Game engines | Scene integration | Frame rate compatibility |

## Validation Checklist

### Performance ✓

- [ ] Extensions have O(log n) or better complexity for common operations
- [ ] No blocking operations in UI thread
- [ ] Resource usage is bounded and monitored
- [ ] Memory leaks are prevented
- [ ] Performance is profiled and optimized

### Architecture ✓

- [ ] Clean separation between core and extensions
- [ ] Plugin system supports isolation
- [ ] Commands have proper validation and undo
- [ ] Renderers manage resources correctly
- [ ] Framework adapters handle events properly

### Quality ✓

- [ ] Comprehensive error handling prevents crashes
- [ ] Extensions degrade gracefully on failure
- [ ] Documentation covers complexity and usage
- [ ] Testing includes performance benchmarks
- [ ] Code follows established patterns

### Integration ✓

- [ ] Framework adapters are complete
- [ ] Event handling is robust
- [ ] Data binding works correctly
- [ ] Lifecycle management is proper
- [ ] Cross-platform compatibility verified

### Extensibility ✓

- [ ] Plugin API is stable and versioned
- [ ] Extension points are well-defined
- [ ] Custom commands integrate seamlessly
- [ ] Renderer system is flexible
- [ ] Framework integration is straightforward

## Related Documents

- **[Usage Guide](usage-guide.md)** - Basic usage patterns and examples
- **[Integration Guide](integration-guide.md)** - Provider optimization and caching
- **[Controller Design](../04-design/controller-design.md)** - Command system architecture
- **[View Design](../04-design/view-design.md)** - Rendering system details
- **[Public API](../05-api/public-api.md)** - Extension points and interfaces

---

This extension guide provides the advanced techniques needed to build sophisticated extensions, optimize performance, and integrate MultiSplit into larger systems. Focus on understanding complexity implications, implementing robust error handling, and following established architectural patterns for maximum reliability and performance.