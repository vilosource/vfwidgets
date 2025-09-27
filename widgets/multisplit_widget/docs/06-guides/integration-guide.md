# MultiSplit Integration Guide

## Overview

This guide covers advanced integration techniques for optimizing MultiSplit performance in production applications. It focuses on provider optimization, caching strategies, pooling mechanisms, and performance tuning for large-scale applications.

## What This Covers

- **Provider optimization patterns** - Caching, pooling, lazy loading
- **Memory management strategies** - Resource pooling, cleanup automation
- **Performance optimization** - Async operations, bottleneck elimination
- **Scalability patterns** - Large workspace handling, resource limits
- **Production deployment** - Monitoring, error recovery, graceful degradation

## What This Doesn't Cover

- **Basic provider implementation** - See [Usage Guide](usage-guide.md)
- **Widget creation patterns** - See [Widget Provider Architecture](../02-architecture/widget-provider.md)
- **Custom extension development** - See [Extension Guide](extension-guide.md)
- **UI styling and theming** - See original [Styling Guide](../../styling-and-theming-GUIDE.md)

---

## Provider Optimization Strategies

### Multi-Level Caching Architecture

Implement sophisticated caching with multiple tiers for optimal performance:

```python
from dataclasses import dataclass
from typing import Dict, Optional, Any, Protocol
from weakref import WeakValueDictionary
import time
import threading
from concurrent.futures import ThreadPoolExecutor

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    widget: QWidget
    created_time: float
    last_access_time: float
    access_count: int
    memory_size: int  # Estimated memory usage

class CachePolicy(Protocol):
    """Cache eviction policy interface"""
    def should_evict(self, entry: CacheEntry, current_time: float) -> bool: ...
    def calculate_priority(self, entry: CacheEntry) -> float: ...

class LRUCachePolicy:
    """Least Recently Used eviction policy"""

    def __init__(self, max_age_seconds: float = 3600):
        self.max_age_seconds = max_age_seconds

    def should_evict(self, entry: CacheEntry, current_time: float) -> bool:
        age = current_time - entry.last_access_time
        return age > self.max_age_seconds

    def calculate_priority(self, entry: CacheEntry) -> float:
        # Higher priority = more likely to keep
        return entry.access_count / (time.time() - entry.last_access_time + 1)

class OptimizedProvider:
    """High-performance provider with multi-level caching"""

    def __init__(self, max_cache_size: int = 100, max_memory_mb: int = 500):
        # Level 1: Active widgets (strong references)
        self.active_cache: Dict[str, CacheEntry] = {}

        # Level 2: Recently used widgets (weak references)
        self.recent_cache: WeakValueDictionary = WeakValueDictionary()

        # Level 3: Widget state cache (for recreation)
        self.state_cache: Dict[str, Dict[str, Any]] = {}

        # Cache management
        self.max_cache_size = max_cache_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.current_memory_usage = 0
        self.cache_policy = LRUCachePolicy()

        # Async operations
        self.executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="widget-loader")
        self.pending_loads: Dict[str, Any] = {}

        # Statistics
        self.cache_hits = 0
        self.cache_misses = 0
        self.widgets_created = 0

        # Background cleanup
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self.cleanup_cache)
        self.cleanup_timer.start(30000)  # Every 30 seconds

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Optimized widget provision with multi-level caching"""

        current_time = time.time()

        # Level 1: Check active cache
        if widget_id in self.active_cache:
            entry = self.active_cache[widget_id]
            entry.last_access_time = current_time
            entry.access_count += 1
            self.cache_hits += 1
            return entry.widget

        # Level 2: Check recent cache (weak references)
        if widget_id in self.recent_cache:
            widget = self.recent_cache[widget_id]
            if widget is not None:  # Widget still alive
                # Promote back to active cache
                entry = CacheEntry(
                    widget=widget,
                    created_time=current_time,
                    last_access_time=current_time,
                    access_count=1,
                    memory_size=self.estimate_widget_memory(widget)
                )
                self.active_cache[widget_id] = entry
                self.cache_hits += 1
                return widget

        # Level 3: Create new widget
        self.cache_misses += 1
        return self.create_and_cache_widget(widget_id, pane_id)

    def create_and_cache_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Create widget and add to cache with memory management"""

        # Check if creation is already in progress
        if widget_id in self.pending_loads:
            placeholder = LoadingPlaceholder(f"Loading {widget_id}...")
            self.finalize_async_widget(widget_id, pane_id, placeholder)
            return placeholder

        # Create widget
        widget = self.create_widget_instance(widget_id, pane_id)
        self.widgets_created += 1

        # Restore state if available
        if widget_id in self.state_cache:
            self.restore_widget_state(widget, self.state_cache[widget_id])

        # Add to cache
        memory_size = self.estimate_widget_memory(widget)
        entry = CacheEntry(
            widget=widget,
            created_time=time.time(),
            last_access_time=time.time(),
            access_count=1,
            memory_size=memory_size
        )

        # Ensure cache limits
        self.ensure_cache_limits(memory_size)

        self.active_cache[widget_id] = entry
        self.current_memory_usage += memory_size

        return widget

    def ensure_cache_limits(self, new_widget_size: int):
        """Ensure cache doesn't exceed memory or size limits"""

        # Check if we need to evict
        while (len(self.active_cache) >= self.max_cache_size or
               self.current_memory_usage + new_widget_size > self.max_memory_bytes):

            if not self.active_cache:
                break

            # Find widget to evict using cache policy
            current_time = time.time()
            evict_candidates = []

            for widget_id, entry in self.active_cache.items():
                if self.cache_policy.should_evict(entry, current_time):
                    priority = self.cache_policy.calculate_priority(entry)
                    evict_candidates.append((priority, widget_id, entry))

            if not evict_candidates:
                # Force evict least recently used
                widget_id = min(self.active_cache.keys(),
                              key=lambda k: self.active_cache[k].last_access_time)
                entry = self.active_cache[widget_id]
                evict_candidates = [(0, widget_id, entry)]

            # Evict lowest priority widget
            evict_candidates.sort()
            _, evict_id, evict_entry = evict_candidates[0]

            self.evict_widget(evict_id, evict_entry)

    def evict_widget(self, widget_id: str, entry: CacheEntry):
        """Evict widget from active cache"""

        # Save state before eviction
        state = self.extract_widget_state(entry.widget)
        if state:
            self.state_cache[widget_id] = state

        # Move to weak reference cache
        self.recent_cache[widget_id] = entry.widget

        # Remove from active cache
        del self.active_cache[widget_id]
        self.current_memory_usage -= entry.memory_size

    def estimate_widget_memory(self, widget: QWidget) -> int:
        """Estimate widget memory usage"""

        # Base widget overhead
        base_size = 1024  # 1KB base

        # Size based on widget type
        if isinstance(widget, QTextEdit):
            text_length = len(widget.toPlainText())
            return base_size + text_length * 2  # Unicode characters

        elif isinstance(widget, QWebEngineView):
            return base_size + 10 * 1024 * 1024  # 10MB estimate for web view

        elif isinstance(widget, QGraphicsView):
            return base_size + 5 * 1024 * 1024  # 5MB for graphics view

        else:
            return base_size

    def cleanup_cache(self):
        """Periodic cache cleanup"""

        current_time = time.time()
        cleanup_candidates = []

        for widget_id, entry in self.active_cache.items():
            if self.cache_policy.should_evict(entry, current_time):
                cleanup_candidates.append(widget_id)

        for widget_id in cleanup_candidates:
            entry = self.active_cache[widget_id]
            self.evict_widget(widget_id, entry)

    def widget_closing(self, widget_id: str, widget: QWidget) -> None:
        """Enhanced cleanup with state preservation"""

        # Save state
        state = self.extract_widget_state(widget)
        if state:
            self.state_cache[widget_id] = state

        # Remove from caches
        if widget_id in self.active_cache:
            entry = self.active_cache[widget_id]
            self.current_memory_usage -= entry.memory_size
            del self.active_cache[widget_id]

        if widget_id in self.recent_cache:
            del self.recent_cache[widget_id]

    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache performance statistics"""

        total_requests = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total_requests if total_requests > 0 else 0

        return {
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": hit_rate,
            "active_widgets": len(self.active_cache),
            "recent_widgets": len(self.recent_cache),
            "memory_usage_mb": self.current_memory_usage / (1024 * 1024),
            "widgets_created": self.widgets_created
        }
```

### Resource Pooling System

Implement widget pooling for expensive-to-create widgets:

```python
class WidgetPool:
    """Pool expensive widgets for reuse"""

    def __init__(self, widget_factory: callable, max_pool_size: int = 10):
        self.widget_factory = widget_factory
        self.max_pool_size = max_pool_size
        self.available_widgets = []
        self.active_widgets: Set[QWidget] = set()
        self.creation_lock = threading.Lock()

    def acquire_widget(self, widget_id: str) -> QWidget:
        """Get widget from pool or create new one"""

        with self.creation_lock:
            # Try to get from pool
            if self.available_widgets:
                widget = self.available_widgets.pop()
                self.reset_widget(widget)
            else:
                # Create new widget
                widget = self.widget_factory()

            self.active_widgets.add(widget)
            self.configure_widget(widget, widget_id)
            return widget

    def release_widget(self, widget: QWidget):
        """Return widget to pool"""

        if widget in self.active_widgets:
            self.active_widgets.remove(widget)

            # Return to pool if under limit
            if len(self.available_widgets) < self.max_pool_size:
                self.cleanup_widget(widget)
                self.available_widgets.append(widget)
            else:
                # Pool full, destroy widget
                widget.deleteLater()

    def reset_widget(self, widget: QWidget):
        """Reset widget to clean state"""

        if isinstance(widget, QTextEdit):
            widget.clear()
            widget.document().setModified(False)
        elif isinstance(widget, QWebEngineView):
            widget.load(QUrl("about:blank"))
        # Add more widget types as needed

    def configure_widget(self, widget: QWidget, widget_id: str):
        """Configure widget for specific use"""

        # Set widget-specific properties based on ID
        if isinstance(widget, QTextEdit) and ":" in widget_id:
            widget_type, param = widget_id.split(":", 1)
            if param.endswith('.py'):
                widget.setProperty("language", "python")

    def cleanup_widget(self, widget: QWidget):
        """Clean widget before returning to pool"""

        # Disconnect all signals to prevent leaks
        if hasattr(widget, 'blockSignals'):
            widget.blockSignals(True)

        # Clear any temporary properties
        widget.setProperty("widget_id", None)

class PooledProvider:
    """Provider using widget pools for performance"""

    def __init__(self):
        self.pools: Dict[str, WidgetPool] = {}
        self.widget_to_pool: Dict[QWidget, WidgetPool] = {}

    def register_pool(self, widget_type: str, factory: callable, pool_size: int = 10):
        """Register a widget pool for a specific type"""
        self.pools[widget_type] = WidgetPool(factory, pool_size)

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Provide widget from appropriate pool"""

        widget_type = widget_id.split(":", 1)[0]

        if widget_type in self.pools:
            pool = self.pools[widget_type]
            widget = pool.acquire_widget(widget_id)
            self.widget_to_pool[widget] = pool
            return widget
        else:
            # Fall back to direct creation
            return self.create_widget_direct(widget_id, pane_id)

    def widget_closing(self, widget_id: str, widget: QWidget) -> None:
        """Return widget to pool when closing"""

        if widget in self.widget_to_pool:
            pool = self.widget_to_pool[widget]
            pool.release_widget(widget)
            del self.widget_to_pool[widget]
        else:
            # Direct creation, just delete
            widget.deleteLater()
```

### Async Loading Framework

Implement comprehensive async loading for better responsiveness:

```python
class AsyncLoadingProvider:
    """Provider with advanced async loading capabilities"""

    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=6, thread_name_prefix="async-provider")
        self.loading_widgets: Dict[str, LoadingPlaceholder] = {}
        self.load_callbacks: Dict[str, List[callable]] = {}

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Provide widget with async loading for heavy operations"""

        # Check if already loading
        if widget_id in self.loading_widgets:
            return self.loading_widgets[widget_id]

        # Determine if widget needs async loading
        if self.needs_async_loading(widget_id):
            return self.start_async_loading(widget_id, pane_id)
        else:
            return self.create_widget_sync(widget_id, pane_id)

    def needs_async_loading(self, widget_id: str) -> bool:
        """Determine if widget should be loaded asynchronously"""

        # Large files
        if widget_id.startswith("editor:"):
            file_path = widget_id[7:]
            try:
                file_size = os.path.getsize(file_path)
                return file_size > 1024 * 1024  # > 1MB
            except:
                return False

        # Network resources
        if widget_id.startswith("web:"):
            return True

        # Database queries
        if widget_id.startswith("query:"):
            return True

        return False

    def start_async_loading(self, widget_id: str, pane_id: str) -> QWidget:
        """Start async loading and return placeholder"""

        # Create placeholder
        placeholder = LoadingPlaceholder(f"Loading {widget_id}...")
        placeholder.cancel_requested.connect(
            lambda: self.cancel_loading(widget_id)
        )

        self.loading_widgets[widget_id] = placeholder

        # Start async loading
        future = self.executor.submit(self.load_widget_async, widget_id, pane_id)
        future.add_done_callback(
            lambda f: self.on_widget_loaded(widget_id, pane_id, f)
        )

        return placeholder

    def load_widget_async(self, widget_id: str, pane_id: str) -> QWidget:
        """Load widget in background thread"""

        try:
            if widget_id.startswith("editor:"):
                return self.load_large_file(widget_id[7:])
            elif widget_id.startswith("web:"):
                return self.load_web_content(widget_id[4:])
            elif widget_id.startswith("query:"):
                return self.load_database_result(widget_id[6:])
            else:
                return self.create_widget_sync(widget_id, pane_id)

        except Exception as e:
            # Return error widget
            return ErrorWidget(f"Failed to load {widget_id}: {e}")

    def on_widget_loaded(self, widget_id: str, pane_id: str, future):
        """Handle completion of async widget loading"""

        if widget_id not in self.loading_widgets:
            return  # Loading was cancelled

        placeholder = self.loading_widgets[widget_id]

        try:
            widget = future.result()

            # Signal to replace placeholder
            self.widget_ready.emit(widget_id, pane_id, widget, placeholder)

        except Exception as e:
            error_widget = ErrorWidget(f"Loading failed: {e}")
            self.widget_ready.emit(widget_id, pane_id, error_widget, placeholder)

        finally:
            del self.loading_widgets[widget_id]

    widget_ready = Signal(str, str, QWidget, QWidget)  # widget_id, pane_id, new_widget, placeholder

class LoadingPlaceholder(QWidget):
    """Placeholder widget shown during async loading"""

    cancel_requested = Signal()

    def __init__(self, message: str):
        super().__init__()
        self.setup_ui(message)
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_progress)
        self.progress_timer.start(100)
        self.progress_value = 0

    def setup_ui(self, message: str):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # Loading message
        self.message_label = QLabel(message)
        self.message_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.message_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        layout.addWidget(self.progress_bar)

        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_requested.emit)
        layout.addWidget(self.cancel_button)

    def update_progress(self):
        # Pulse animation for indeterminate progress
        self.progress_value = (self.progress_value + 1) % 100
        self.progress_bar.setValue(self.progress_value)
```

---

## Memory Management Strategies

### Memory Monitoring System

Implement comprehensive memory monitoring and management:

```python
class MemoryMonitor:
    """Monitor and manage memory usage across MultiSplit"""

    def __init__(self, provider):
        self.provider = provider
        self.memory_samples = []
        self.max_samples = 100

        # Memory limits
        self.soft_limit_mb = 500  # Start cleanup
        self.hard_limit_mb = 800  # Force cleanup

        # Monitoring timer
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.check_memory_usage)
        self.monitor_timer.start(5000)  # Every 5 seconds

    def check_memory_usage(self):
        """Check current memory usage and trigger cleanup if needed"""

        current_usage = self.get_memory_usage_mb()
        self.memory_samples.append({
            'timestamp': time.time(),
            'memory_mb': current_usage,
            'widget_count': len(self.provider.active_cache)
        })

        # Keep only recent samples
        if len(self.memory_samples) > self.max_samples:
            self.memory_samples.pop(0)

        # Check if cleanup needed
        if current_usage > self.hard_limit_mb:
            self.force_cleanup()
        elif current_usage > self.soft_limit_mb:
            self.gentle_cleanup()

    def get_memory_usage_mb(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / (1024 * 1024)
        except ImportError:
            # Fallback to provider estimate
            return self.provider.current_memory_usage / (1024 * 1024)

    def gentle_cleanup(self):
        """Perform gentle cleanup to reduce memory usage"""

        # Clean up provider caches
        initial_count = len(self.provider.active_cache)
        self.provider.cleanup_cache()

        # Clear unused state caches
        self.cleanup_old_state_caches()

        cleaned_count = initial_count - len(self.provider.active_cache)
        if cleaned_count > 0:
            print(f"Gentle cleanup: removed {cleaned_count} cached widgets")

    def force_cleanup(self):
        """Aggressive cleanup when hitting hard limits"""

        print("Force cleanup: memory limit exceeded")

        # Clear more aggressive
        old_policy = self.provider.cache_policy
        self.provider.cache_policy = AggressiveCachePolicy()

        self.provider.cleanup_cache()

        # Force garbage collection
        import gc
        gc.collect()

        # Restore original policy
        self.provider.cache_policy = old_policy

    def cleanup_old_state_caches(self):
        """Remove old state cache entries"""

        current_time = time.time()
        old_entries = []

        for widget_id, state in self.provider.state_cache.items():
            if 'last_access' in state:
                age = current_time - state['last_access']
                if age > 3600:  # 1 hour old
                    old_entries.append(widget_id)

        for widget_id in old_entries:
            del self.provider.state_cache[widget_id]

class AggressiveCachePolicy:
    """More aggressive cache eviction policy"""

    def should_evict(self, entry: CacheEntry, current_time: float) -> bool:
        # Evict anything older than 5 minutes
        age = current_time - entry.last_access_time
        return age > 300

    def calculate_priority(self, entry: CacheEntry) -> float:
        # Heavily favor recently accessed items
        return entry.access_count * 100 / (time.time() - entry.last_access_time + 1)
```

### Lazy Resource Loading

Implement lazy loading for widget content and resources:

```python
class LazyLoadingWidget(QWidget):
    """Base class for widgets with lazy content loading"""

    def __init__(self):
        super().__init__()
        self._content_loaded = False
        self._loading_requested = False
        self._load_future = None

    def showEvent(self, event):
        """Load content when widget becomes visible"""
        super().showEvent(event)
        if not self._content_loaded and not self._loading_requested:
            self.request_content_load()

    def request_content_load(self):
        """Request content loading (async)"""
        if self._loading_requested:
            return

        self._loading_requested = True

        # Show loading indicator
        self.show_loading_indicator()

        # Start async loading
        executor = QThreadPool.globalInstance()
        worker = LazyLoadWorker(self.load_content)
        worker.signals.finished.connect(self.on_content_loaded)
        worker.signals.error.connect(self.on_content_error)
        executor.start(worker)

    def load_content(self) -> Any:
        """Override this method to load actual content"""
        raise NotImplementedError

    def on_content_loaded(self, content):
        """Handle successful content loading"""
        self._content_loaded = True
        self.hide_loading_indicator()
        self.apply_content(content)

    def on_content_error(self, error):
        """Handle content loading error"""
        self._loading_requested = False
        self.show_error_indicator(str(error))

    def apply_content(self, content):
        """Apply loaded content to widget"""
        raise NotImplementedError

class LazyCodeEditor(LazyLoadingWidget):
    """Code editor with lazy file loading"""

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
        self.editor = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Placeholder until content loads
        self.placeholder = QLabel("Code editor will load when visible...")
        self.placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.placeholder)

    def load_content(self) -> str:
        """Load file content in background thread"""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def apply_content(self, content: str):
        """Apply loaded content to editor"""

        # Create actual editor
        self.editor = QTextEdit()
        self.editor.setPlainText(content)

        # Replace placeholder
        layout = self.layout()
        layout.removeWidget(self.placeholder)
        self.placeholder.deleteLater()
        layout.addWidget(self.editor)

class LazyWebView(LazyLoadingWidget):
    """Web view with lazy content loading"""

    def __init__(self, url: str):
        super().__init__()
        self.url = url
        self.web_view = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.placeholder = QLabel(f"Web page will load when visible...\n{self.url}")
        self.placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.placeholder)

    def load_content(self):
        """Prepare web view (still loads in main thread)"""
        return self.url

    def apply_content(self, url: str):
        """Create and load web view"""

        self.web_view = QWebEngineView()

        # Replace placeholder
        layout = self.layout()
        layout.removeWidget(self.placeholder)
        self.placeholder.deleteLater()
        layout.addWidget(self.web_view)

        # Load URL
        self.web_view.load(QUrl(url))
```

---

## Performance Optimization Techniques

### Complexity Analysis and Bottleneck Elimination

Understand and optimize MultiSplit performance characteristics:

```python
class PerformanceProfiler:
    """Profile MultiSplit operations for optimization"""

    def __init__(self, splitter: MultiSplitWidget):
        self.splitter = splitter
        self.operation_times = {}
        self.call_counts = {}

    def profile_operation(self, operation_name: str):
        """Decorator to profile operation timing"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                result = func(*args, **kwargs)
                end_time = time.perf_counter()

                duration = end_time - start_time

                if operation_name not in self.operation_times:
                    self.operation_times[operation_name] = []
                    self.call_counts[operation_name] = 0

                self.operation_times[operation_name].append(duration)
                self.call_counts[operation_name] += 1

                # Log slow operations
                if duration > 0.1:  # > 100ms
                    print(f"Slow operation: {operation_name} took {duration:.3f}s")

                return result
            return wrapper
        return decorator

    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance analysis report"""

        report = {}

        for operation, times in self.operation_times.items():
            if times:
                avg_time = sum(times) / len(times)
                max_time = max(times)
                min_time = min(times)
                total_time = sum(times)

                report[operation] = {
                    'call_count': self.call_counts[operation],
                    'avg_time_ms': avg_time * 1000,
                    'max_time_ms': max_time * 1000,
                    'min_time_ms': min_time * 1000,
                    'total_time_ms': total_time * 1000,
                    'time_per_call_ms': (total_time / self.call_counts[operation]) * 1000
                }

        return report

class OptimizedMultiSplitWidget(MultiSplitWidget):
    """MultiSplit with performance optimizations"""

    def __init__(self):
        super().__init__()
        self.profiler = PerformanceProfiler(self)

        # Optimization flags
        self.batch_updates = True
        self.defer_geometry_calculations = True
        self.use_viewport_culling = True

        # Update batching
        self.pending_updates = set()
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.process_pending_updates)

    @profile_operation("widget_creation")
    def provide_widget_optimized(self, widget_id: str, pane_id: str) -> QWidget:
        """Optimized widget provision with batching"""

        if self.batch_updates:
            self.pending_updates.add((widget_id, pane_id))
            if not self.update_timer.isActive():
                self.update_timer.start(16)  # ~60 FPS
            return PlaceholderWidget()
        else:
            return super().provide_widget(widget_id, pane_id)

    def process_pending_updates(self):
        """Process batched widget updates"""

        if not self.pending_updates:
            return

        # Process all pending updates at once
        widgets_to_create = list(self.pending_updates)
        self.pending_updates.clear()

        for widget_id, pane_id in widgets_to_create:
            widget = self.create_widget_immediate(widget_id, pane_id)
            self.replace_placeholder(pane_id, widget)

    @profile_operation("layout_calculation")
    def calculate_layout_optimized(self) -> Dict[str, QRect]:
        """Optimized layout calculation with viewport culling"""

        if not self.use_viewport_culling:
            return super().calculate_layout()

        # Get visible viewport
        viewport = self.visibleRegion().boundingRect()

        # Only calculate layout for visible panes
        visible_panes = {}
        all_layout = super().calculate_layout()

        for pane_id, rect in all_layout.items():
            if viewport.intersects(rect):
                visible_panes[pane_id] = rect
            else:
                # Use placeholder rect for invisible panes
                visible_panes[pane_id] = QRect()

        return visible_panes

    @profile_operation("tree_reconciliation")
    def reconcile_tree_optimized(self, new_tree):
        """Optimized tree reconciliation with minimal updates"""

        # Calculate diff more efficiently
        old_tree = self.get_current_tree()
        diff = self.calculate_minimal_diff(old_tree, new_tree)

        # Apply only necessary changes
        self.apply_minimal_changes(diff)

    def calculate_minimal_diff(self, old_tree, new_tree):
        """Calculate minimal changes needed"""

        # Use more efficient diff algorithm
        old_panes = set(self.extract_pane_ids(old_tree))
        new_panes = set(self.extract_pane_ids(new_tree))

        return {
            'added': new_panes - old_panes,
            'removed': old_panes - new_panes,
            'modified': self.find_modified_panes(old_tree, new_tree)
        }
```

### Rendering Optimization

Optimize rendering performance for large numbers of panes:

```python
class OptimizedRenderer:
    """Optimized rendering for MultiSplit with many panes"""

    def __init__(self):
        self.render_cache = {}
        self.dirty_regions = set()
        self.frame_rate_limiter = QTimer()
        self.frame_rate_limiter.setSingleShot(True)
        self.frame_rate_limiter.timeout.connect(self.render_frame)
        self.target_fps = 60

    def request_render(self, region: QRect = None):
        """Request rendering with frame rate limiting"""

        if region:
            self.dirty_regions.add(region)

        if not self.frame_rate_limiter.isActive():
            frame_time = 1000 // self.target_fps  # ms per frame
            self.frame_rate_limiter.start(frame_time)

    def render_frame(self):
        """Render accumulated dirty regions"""

        if not self.dirty_regions:
            return

        # Combine overlapping regions
        combined_region = self.combine_regions(self.dirty_regions)
        self.dirty_regions.clear()

        # Render only the combined region
        self.render_region(combined_region)

    def combine_regions(self, regions: Set[QRect]) -> QRect:
        """Combine overlapping regions into minimal bounding rect"""

        if not regions:
            return QRect()

        combined = QRect()
        for region in regions:
            combined = combined.united(region)

        return combined

    def render_region(self, region: QRect):
        """Render specific region with optimization"""

        # Use cached rendering if available
        cache_key = f"{region.x()},{region.y()},{region.width()},{region.height()}"

        if cache_key in self.render_cache:
            cached_render = self.render_cache[cache_key]
            if self.is_cache_valid(cached_render):
                self.apply_cached_render(cached_render, region)
                return

        # Perform actual rendering
        render_result = self.perform_rendering(region)

        # Cache result for future use
        self.render_cache[cache_key] = {
            'result': render_result,
            'timestamp': time.time(),
            'widget_states': self.capture_widget_states(region)
        }

class GeometryOptimizer:
    """Optimize geometry calculations for large layouts"""

    def __init__(self):
        self.calculation_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0

    def calculate_geometry(self, tree_structure: dict, available_rect: QRect) -> Dict[str, QRect]:
        """Calculate geometry with caching"""

        # Create cache key from tree structure and rect
        cache_key = self.create_cache_key(tree_structure, available_rect)

        if cache_key in self.calculation_cache:
            self.cache_hits += 1
            return self.calculation_cache[cache_key]

        self.cache_misses += 1

        # Perform calculation
        result = self.calculate_geometry_impl(tree_structure, available_rect)

        # Cache result
        self.calculation_cache[cache_key] = result

        # Limit cache size
        if len(self.calculation_cache) > 1000:
            self.cleanup_geometry_cache()

        return result

    def calculate_geometry_impl(self, tree: dict, rect: QRect) -> Dict[str, QRect]:
        """Actual geometry calculation implementation"""

        if tree['type'] == 'leaf':
            return {tree['pane_id']: rect}

        # Split calculation
        result = {}
        orientation = tree['orientation']
        ratios = tree.get('ratios', [])
        children = tree['children']

        if not ratios:
            # Equal ratios
            ratios = [1.0 / len(children)] * len(children)

        if orientation == 'horizontal':
            current_x = rect.x()
            for i, child in enumerate(children):
                child_width = int(rect.width() * ratios[i])
                child_rect = QRect(current_x, rect.y(), child_width, rect.height())
                child_result = self.calculate_geometry_impl(child, child_rect)
                result.update(child_result)
                current_x += child_width
        else:  # vertical
            current_y = rect.y()
            for i, child in enumerate(children):
                child_height = int(rect.height() * ratios[i])
                child_rect = QRect(rect.x(), current_y, rect.width(), child_height)
                child_result = self.calculate_geometry_impl(child, child_rect)
                result.update(child_result)
                current_y += child_height

        return result

    def create_cache_key(self, tree: dict, rect: QRect) -> str:
        """Create cache key from tree and rectangle"""

        # Create deterministic string representation
        tree_str = json.dumps(tree, sort_keys=True)
        rect_str = f"{rect.x()},{rect.y()},{rect.width()},{rect.height()}"

        # Use hash for efficiency
        import hashlib
        combined = f"{tree_str}:{rect_str}"
        return hashlib.md5(combined.encode()).hexdigest()

    def cleanup_geometry_cache(self):
        """Remove old cache entries"""

        # Remove oldest 20% of entries
        cache_items = list(self.calculation_cache.items())
        remove_count = len(cache_items) // 5

        # For simplicity, remove first N items (should use LRU in production)
        for i in range(remove_count):
            key, _ = cache_items[i]
            del self.calculation_cache[key]

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""

        total_requests = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total_requests if total_requests > 0 else 0

        return {
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate': hit_rate,
            'cache_size': len(self.calculation_cache)
        }
```

---

## Scalability Patterns

### Large Workspace Management

Handle applications with hundreds of panes efficiently:

```python
class ScalableWorkspaceManager:
    """Manage large workspaces with many panes efficiently"""

    def __init__(self, splitter: MultiSplitWidget):
        self.splitter = splitter
        self.virtual_panes = {}  # Panes not currently rendered
        self.viewport_panes = set()  # Currently visible panes
        self.max_active_panes = 50

        # Viewport tracking
        self.viewport_timer = QTimer()
        self.viewport_timer.timeout.connect(self.update_viewport)
        self.viewport_timer.start(100)  # 10 FPS viewport updates

    def add_pane_virtualized(self, widget_id: str, position: WherePosition) -> str:
        """Add pane with virtualization for large workspaces"""

        # Check if we need virtualization
        current_count = len(self.splitter.all_pane_ids)

        if current_count < self.max_active_panes:
            # Normal addition
            return self.splitter.split_with_widget_id(
                self.splitter.current_pane_id, position, widget_id
            )
        else:
            # Virtual addition
            pane_id = self.generate_virtual_pane_id()
            self.virtual_panes[pane_id] = {
                'widget_id': widget_id,
                'position': position,
                'target_pane': self.splitter.current_pane_id,
                'created_time': time.time()
            }
            return pane_id

    def update_viewport(self):
        """Update which panes are in viewport"""

        visible_rect = self.splitter.visibleRegion().boundingRect()
        new_viewport_panes = set()

        # Check which panes are visible
        for pane_id in self.splitter.all_pane_ids:
            pane_rect = self.splitter.get_pane_rect(pane_id)
            if visible_rect.intersects(pane_rect):
                new_viewport_panes.add(pane_id)

        # Handle panes entering/leaving viewport
        entering = new_viewport_panes - self.viewport_panes
        leaving = self.viewport_panes - new_viewport_panes

        for pane_id in entering:
            self.pane_entered_viewport(pane_id)

        for pane_id in leaving:
            self.pane_left_viewport(pane_id)

        self.viewport_panes = new_viewport_panes

    def pane_entered_viewport(self, pane_id: str):
        """Handle pane becoming visible"""

        # Ensure widget is loaded
        widget = self.splitter.get_widget_for_pane(pane_id)
        if isinstance(widget, PlaceholderWidget):
            # Load actual widget
            widget_id = self.splitter.get_widget_id_for_pane(pane_id)
            actual_widget = self.splitter.widget_provider.provide_widget(widget_id, pane_id)
            self.splitter.replace_widget(pane_id, actual_widget, widget_id)

    def pane_left_viewport(self, pane_id: str):
        """Handle pane becoming invisible"""

        # Optionally virtualize widget to save memory
        if self.should_virtualize_pane(pane_id):
            widget = self.splitter.get_widget_for_pane(pane_id)
            widget_id = self.splitter.get_widget_id_for_pane(pane_id)

            # Save widget state
            state = self.save_widget_state(widget)

            # Replace with placeholder
            placeholder = PlaceholderWidget(f"Virtualized: {widget_id}")
            self.splitter.replace_widget(pane_id, placeholder, widget_id)

            # Store state for restoration
            self.virtual_panes[pane_id] = {
                'widget_id': widget_id,
                'state': state,
                'virtualized_time': time.time()
            }

    def should_virtualize_pane(self, pane_id: str) -> bool:
        """Determine if pane should be virtualized to save memory"""

        # Don't virtualize if total pane count is reasonable
        if len(self.splitter.all_pane_ids) < self.max_active_panes:
            return False

        # Don't virtualize recently accessed panes
        widget = self.splitter.get_widget_for_pane(pane_id)
        if hasattr(widget, 'last_access_time'):
            age = time.time() - widget.last_access_time
            if age < 300:  # 5 minutes
                return False

        return True

class HierarchicalPaneManager:
    """Manage panes in hierarchical groups for better organization"""

    def __init__(self):
        self.pane_groups = {}  # group_id -> list of pane_ids
        self.pane_to_group = {}  # pane_id -> group_id
        self.group_metadata = {}  # group_id -> metadata

    def create_pane_group(self, group_id: str, metadata: dict = None) -> str:
        """Create a logical grouping of panes"""

        self.pane_groups[group_id] = []
        self.group_metadata[group_id] = metadata or {}

        return group_id

    def add_pane_to_group(self, pane_id: str, group_id: str):
        """Add pane to a group"""

        if group_id not in self.pane_groups:
            self.create_pane_group(group_id)

        self.pane_groups[group_id].append(pane_id)
        self.pane_to_group[pane_id] = group_id

    def get_group_panes(self, group_id: str) -> List[str]:
        """Get all panes in a group"""
        return self.pane_groups.get(group_id, [])

    def close_group(self, group_id: str):
        """Close all panes in a group"""

        if group_id not in self.pane_groups:
            return

        panes_to_close = self.pane_groups[group_id].copy()

        for pane_id in panes_to_close:
            self.splitter.close_pane(pane_id)

        # Clean up group
        del self.pane_groups[group_id]
        del self.group_metadata[group_id]

    def get_group_for_pane(self, pane_id: str) -> Optional[str]:
        """Get group ID for a pane"""
        return self.pane_to_group.get(pane_id)

    def save_group_layout(self, group_id: str) -> dict:
        """Save layout for a specific group"""

        if group_id not in self.pane_groups:
            return {}

        # Get full layout
        full_layout = self.splitter.save_layout()

        # Filter to group panes only
        group_panes = set(self.pane_groups[group_id])
        filtered_layout = self.filter_layout_to_panes(full_layout, group_panes)

        return filtered_layout

    def restore_group_layout(self, group_id: str, layout: dict):
        """Restore layout for a specific group"""

        # Create group if doesn't exist
        if group_id not in self.pane_groups:
            self.create_pane_group(group_id)

        # Apply layout (will trigger pane creation)
        self.splitter.restore_layout(layout)

        # Update group tracking
        new_panes = self.extract_pane_ids_from_layout(layout)
        for pane_id in new_panes:
            self.add_pane_to_group(pane_id, group_id)
```

---

## Common Pitfalls

### Pitfall 1: Memory Leaks in Caching

**Problem**: Cache grows without bounds
```python
# ❌ BAD: Unbounded cache
class BadProvider:
    def __init__(self):
        self.cache = {}  # Never cleaned up!

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        if widget_id not in self.cache:
            self.cache[widget_id] = expensive_widget_creation(widget_id)
        return self.cache[widget_id]
```

**Solution**: Implement cache limits and cleanup
```python
# ✅ GOOD: Bounded cache with cleanup
class GoodProvider:
    def __init__(self):
        self.cache = {}
        self.max_cache_size = 100
        self.access_times = {}

    def cleanup_cache(self):
        if len(self.cache) >= self.max_cache_size:
            # Remove oldest entries
            sorted_items = sorted(self.access_times.items(), key=lambda x: x[1])
            for widget_id, _ in sorted_items[:10]:  # Remove 10 oldest
                del self.cache[widget_id]
                del self.access_times[widget_id]
```

### Pitfall 2: Blocking the UI with Expensive Operations

**Problem**: Synchronous expensive operations
```python
# ❌ BAD: Blocking UI
def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
    if widget_id.startswith("heavy:"):
        # This blocks the UI for seconds!
        data = expensive_database_query()
        return create_widget_with_data(data)
```

**Solution**: Use async operations with placeholders
```python
# ✅ GOOD: Async with placeholders
def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
    if widget_id.startswith("heavy:"):
        placeholder = LoadingPlaceholder("Loading data...")
        self.load_async(widget_id, pane_id, placeholder)
        return placeholder
```

### Pitfall 3: Not Handling Widget Lifecycle

**Problem**: Ignoring widget cleanup
```python
# ❌ BAD: No cleanup
def widget_closing(self, widget_id: str, widget: QWidget) -> None:
    pass  # Ignoring cleanup!
```

**Solution**: Proper resource management
```python
# ✅ GOOD: Complete cleanup
def widget_closing(self, widget_id: str, widget: QWidget) -> None:
    # Save state
    self.save_widget_state(widget_id, widget)

    # Clean up resources
    if hasattr(widget, 'cleanup'):
        widget.cleanup()

    # Remove from caches
    self.remove_from_cache(widget_id)
```

### Pitfall 4: Poor Cache Invalidation

**Problem**: Stale cache entries
```python
# ❌ BAD: Never invalidating cache
class BadCache:
    def get_widget(self, widget_id: str) -> QWidget:
        if widget_id in self.cache:
            return self.cache[widget_id]  # Might be stale!
```

**Solution**: Smart cache invalidation
```python
# ✅ GOOD: Cache with invalidation
class GoodCache:
    def get_widget(self, widget_id: str) -> QWidget:
        if widget_id in self.cache:
            entry = self.cache[widget_id]
            if self.is_cache_entry_valid(entry):
                return entry.widget
            else:
                del self.cache[widget_id]  # Remove stale entry
```

### Pitfall 5: Memory Usage Not Monitored

**Problem**: No memory monitoring
```python
# ❌ BAD: No memory awareness
class BadProvider:
    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        # Creates widgets without checking memory usage
        return ExpensiveWidget(widget_id)
```

**Solution**: Memory-aware widget creation
```python
# ✅ GOOD: Memory monitoring
class GoodProvider:
    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        current_memory = self.get_memory_usage()
        if current_memory > self.memory_limit:
            self.force_cleanup()
        return self.create_widget_with_limits(widget_id)
```

---

## Quick Reference

### Optimization Checklist

| Component | Optimization | Impact |
|-----------|-------------|---------|
| Widget Provider | Multi-level caching | High |
| Memory Management | Automatic cleanup | High |
| Rendering | Viewport culling | Medium |
| Geometry | Calculation caching | Medium |
| Async Loading | Non-blocking creation | High |

### Performance Targets

| Operation | Target Time | Optimization Strategy |
|-----------|-------------|----------------------|
| Widget provision | < 50ms | Caching + async loading |
| Layout calculation | < 16ms | Geometry caching |
| Tree reconciliation | < 10ms | Minimal diff algorithm |
| Memory cleanup | < 100ms | Background processing |
| Viewport update | < 5ms | Efficient rect calculation |

### Memory Management Guidelines

| Resource Type | Management Strategy | Cleanup Trigger |
|--------------|-------------------|----------------|
| Widget instances | LRU cache with size limit | Cache size + memory pressure |
| Widget states | Time-based expiration | Age > 1 hour |
| Render cache | Access-based eviction | Memory limit reached |
| Async operations | Immediate cleanup | Operation completion |
| Event handlers | Weak references | Widget destruction |

### Caching Strategies

| Cache Type | Use Case | Eviction Policy |
|------------|----------|----------------|
| Active widgets | Currently displayed | LRU + memory pressure |
| Recent widgets | Recently used | Weak references |
| Widget states | Persistence | Time-based |
| Geometry | Layout calculations | Size-based |
| Render results | Visual optimization | Access frequency |

## Validation Checklist

### Memory Management ✓

- [ ] Cache has size and memory limits
- [ ] Automatic cleanup runs periodically
- [ ] Memory usage is monitored
- [ ] Eviction policies are appropriate
- [ ] Weak references prevent leaks

### Performance Optimization ✓

- [ ] Expensive operations are async
- [ ] Viewport culling is implemented
- [ ] Geometry calculations are cached
- [ ] Rendering is frame-rate limited
- [ ] Bottlenecks are profiled and optimized

### Scalability ✓

- [ ] Handles 100+ panes efficiently
- [ ] Virtualization works for large workspaces
- [ ] Resource usage scales linearly
- [ ] No O(n²) algorithms in hot paths
- [ ] Background processing doesn't block UI

### Integration Quality ✓

- [ ] Provider implements all optimizations
- [ ] Error handling prevents crashes
- [ ] Recovery mechanisms work correctly
- [ ] Performance monitoring is in place
- [ ] Resource cleanup is complete

### Production Readiness ✓

- [ ] Memory leaks are prevented
- [ ] Performance is consistent under load
- [ ] Error conditions are handled gracefully
- [ ] Monitoring provides actionable insights
- [ ] Degradation strategies are implemented

## Related Documents

- **[Usage Guide](usage-guide.md)** - Basic usage patterns and examples
- **[Extension Guide](extension-guide.md)** - Custom extensions and advanced features
- **[Widget Provider Architecture](../02-architecture/widget-provider.md)** - Provider pattern fundamentals
- **[Model Design](../04-design/model-design.md)** - Core data structures and algorithms
- **[View Design](../04-design/view-design.md)** - Rendering and UI optimization

---

This integration guide provides the advanced techniques needed to build high-performance, scalable applications with MultiSplit. Focus on implementing proper caching, memory management, and async operations to ensure excellent user experience even with complex layouts and large numbers of widgets.