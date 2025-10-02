"""Extension system core implementation.

Provides secure plugin system for theme extensions with sandboxed execution,
dependency management, and hot reload support.
"""

import hashlib
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

from ..errors import ExtensionError
from ..logging import get_logger
from ..utils.file_utils import ensure_directory
from .api import ExtensionAPI
from .loader import ExtensionLoader
from .sandbox import ExtensionSandbox

logger = get_logger(__name__)


@dataclass
class Extension:
    """Represents a loaded extension."""

    name: str
    version: str
    description: str
    author: str
    path: Path
    module: Any = None
    dependencies: List[str] = field(default_factory=list)
    provides: List[str] = field(default_factory=list)
    enabled: bool = True
    loaded_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Extension hooks
    hooks: Dict[str, Callable] = field(default_factory=dict)

    def __post_init__(self):
        """Post-initialization setup."""
        if not self.metadata:
            self.metadata = {}

        # Generate extension ID from name and path
        self.id = self._generate_id()

    def _generate_id(self) -> str:
        """Generate unique extension ID."""
        content = f"{self.name}:{self.path}:{self.version}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def has_hook(self, hook_name: str) -> bool:
        """Check if extension provides a hook."""
        return hook_name in self.hooks

    def call_hook(self, hook_name: str, *args, **kwargs) -> Any:
        """Call extension hook if available."""
        if hook_name in self.hooks:
            return self.hooks[hook_name](*args, **kwargs)
        return None


class ExtensionSystem:
    """Secure plugin system for theme extensions.

    Provides extension discovery, loading, sandboxed execution,
    dependency management, and hot reload capabilities.
    """

    # Standard extension hooks
    STANDARD_HOOKS = {
        'on_theme_loaded',      # Called when theme is loaded
        'on_theme_applied',     # Called when theme is applied
        'on_theme_changed',     # Called when theme changes
        'transform_theme',      # Transform theme data
        'provide_widgets',      # Provide custom widgets
        'customize_colors',     # Customize color palette
        'add_properties',       # Add theme properties
        'validate_theme',       # Validate theme data
        'on_extension_loaded',  # Called when extension loads
        'on_extension_unloaded' # Called when extension unloads
    }

    def __init__(self, extensions_dir: Optional[Path] = None):
        """Initialize extension system.

        Args:
            extensions_dir: Directory containing extensions

        """
        self.extensions_dir = extensions_dir or Path.home() / ".vfwidgets" / "extensions"
        self.extensions: Dict[str, Extension] = {}
        self.sandbox = ExtensionSandbox()
        self.api = ExtensionAPI()
        self.loader = ExtensionLoader()

        # Extension monitoring
        self._file_monitors: Dict[str, float] = {}  # path -> last_modified
        self._hot_reload_enabled = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._shutdown_event = threading.Event()

        # Dependency graph
        self._dependency_graph: Dict[str, Set[str]] = {}
        self._load_order: List[str] = []

        # Hook registry
        self._hook_listeners: Dict[str, List[str]] = {}  # hook_name -> extension_ids

        # Ensure extensions directory exists
        ensure_directory(self.extensions_dir)

        logger.info(f"Extension system initialized with directory: {self.extensions_dir}")

    def discover_extensions(self) -> List[Path]:
        """Discover extension files in extensions directory.

        Returns:
            List of extension file paths

        """
        logger.info("Discovering extensions...")

        extension_paths = []

        if not self.extensions_dir.exists():
            logger.warning(f"Extensions directory does not exist: {self.extensions_dir}")
            return extension_paths

        # Look for Python files and directories with __init__.py
        for item in self.extensions_dir.iterdir():
            if item.is_file() and item.suffix == '.py':
                extension_paths.append(item)
            elif item.is_dir() and (item / "__init__.py").exists():
                extension_paths.append(item / "__init__.py")

        logger.info(f"Discovered {len(extension_paths)} extensions")
        return extension_paths

    def load_extension(self, path: Path) -> Extension:
        """Load and validate an extension.

        Args:
            path: Path to extension file

        Returns:
            Loaded extension

        Raises:
            ExtensionError: If extension cannot be loaded

        """
        logger.info(f"Loading extension: {path}")

        if not path.exists():
            raise ExtensionError(f"Extension file not found: {path}")

        try:
            # Load extension metadata and module
            extension = self.loader.load_from_file(path)

            # Validate extension
            self._validate_extension(extension)

            # Check dependencies
            self._check_dependencies(extension)

            # Initialize in sandbox
            self.sandbox.initialize_extension(extension)

            # Register extension
            self.extensions[extension.id] = extension

            # Update dependency graph
            self._update_dependency_graph(extension)

            # Register hooks
            self._register_extension_hooks(extension)

            # Call extension initialization
            if extension.has_hook('on_extension_loaded'):
                self.sandbox.execute_safely(
                    extension,
                    lambda: extension.call_hook('on_extension_loaded')
                )

            # Start monitoring for changes if hot reload enabled
            if self._hot_reload_enabled:
                self._file_monitors[str(path)] = path.stat().st_mtime

            logger.info(f"Successfully loaded extension: {extension.name}")
            return extension

        except Exception as e:
            logger.error(f"Failed to load extension {path}: {e}")
            raise ExtensionError(f"Extension loading failed: {e}")

    def unload_extension(self, extension_id: str) -> None:
        """Unload an extension.

        Args:
            extension_id: Extension identifier

        """
        if extension_id not in self.extensions:
            logger.warning(f"Extension not found for unloading: {extension_id}")
            return

        extension = self.extensions[extension_id]
        logger.info(f"Unloading extension: {extension.name}")

        try:
            # Call extension cleanup
            if extension.has_hook('on_extension_unloaded'):
                self.sandbox.execute_safely(
                    extension,
                    lambda: extension.call_hook('on_extension_unloaded')
                )

            # Unregister hooks
            self._unregister_extension_hooks(extension)

            # Remove from dependency graph
            self._remove_from_dependency_graph(extension)

            # Cleanup sandbox
            self.sandbox.cleanup_extension(extension)

            # Remove from registry
            del self.extensions[extension_id]

            # Stop monitoring
            extension_path = str(extension.path)
            if extension_path in self._file_monitors:
                del self._file_monitors[extension_path]

            logger.info(f"Successfully unloaded extension: {extension.name}")

        except Exception as e:
            logger.error(f"Error unloading extension {extension.name}: {e}")

    def reload_extension(self, extension_id: str) -> Extension:
        """Reload an extension (hot reload).

        Args:
            extension_id: Extension identifier

        Returns:
            Reloaded extension

        """
        if extension_id not in self.extensions:
            raise ExtensionError(f"Extension not found: {extension_id}")

        extension = self.extensions[extension_id]
        extension_path = extension.path

        logger.info(f"Reloading extension: {extension.name}")

        # Unload current version
        self.unload_extension(extension_id)

        # Load new version
        return self.load_extension(extension_path)

    def get_extension(self, extension_id: str) -> Optional[Extension]:
        """Get extension by ID."""
        return self.extensions.get(extension_id)

    def list_extensions(self) -> List[Extension]:
        """Get list of all loaded extensions."""
        return list(self.extensions.values())

    def list_enabled_extensions(self) -> List[Extension]:
        """Get list of enabled extensions."""
        return [ext for ext in self.extensions.values() if ext.enabled]

    def enable_extension(self, extension_id: str) -> None:
        """Enable an extension."""
        if extension_id in self.extensions:
            self.extensions[extension_id].enabled = True
            logger.info(f"Enabled extension: {extension_id}")

    def disable_extension(self, extension_id: str) -> None:
        """Disable an extension."""
        if extension_id in self.extensions:
            self.extensions[extension_id].enabled = False
            logger.info(f"Disabled extension: {extension_id}")

    def call_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Call a hook on all extensions that provide it.

        Args:
            hook_name: Name of hook to call
            *args: Hook arguments
            **kwargs: Hook keyword arguments

        Returns:
            List of results from extensions

        """
        results = []

        if hook_name not in self._hook_listeners:
            return results

        for extension_id in self._hook_listeners[hook_name]:
            extension = self.extensions.get(extension_id)
            if extension and extension.enabled and extension.has_hook(hook_name):
                try:
                    result = self.sandbox.execute_safely(
                        extension,
                        lambda: extension.call_hook(hook_name, *args, **kwargs)
                    )
                    results.append(result)

                except Exception as e:
                    logger.error(f"Error calling hook {hook_name} on {extension.name}: {e}")

        return results

    def register_api(self, api_name: str, api_object: Any) -> None:
        """Register API for extensions to use.

        Args:
            api_name: Name of API
            api_object: API object

        """
        self.api.register_api(api_name, api_object)
        logger.info(f"Registered API: {api_name}")

    def enable_hot_reload(self) -> None:
        """Enable hot reload monitoring."""
        if self._hot_reload_enabled:
            return

        self._hot_reload_enabled = True
        self._shutdown_event.clear()

        # Start monitoring thread
        self._monitor_thread = threading.Thread(
            target=self._monitor_files,
            daemon=True,
            name="ExtensionMonitor"
        )
        self._monitor_thread.start()

        logger.info("Hot reload monitoring enabled")

    def disable_hot_reload(self) -> None:
        """Disable hot reload monitoring."""
        if not self._hot_reload_enabled:
            return

        self._hot_reload_enabled = False
        self._shutdown_event.set()

        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5.0)

        logger.info("Hot reload monitoring disabled")

    def _validate_extension(self, extension: Extension) -> None:
        """Validate extension structure and metadata."""
        if not extension.name:
            raise ExtensionError("Extension must have a name")

        if not extension.version:
            raise ExtensionError("Extension must have a version")

        # Check for required module attributes
        if not hasattr(extension.module, '__extension_info__'):
            logger.warning(f"Extension {extension.name} missing __extension_info__")

        # Validate hook functions
        for hook_name, hook_func in extension.hooks.items():
            if hook_name not in self.STANDARD_HOOKS:
                logger.warning(f"Extension {extension.name} uses non-standard hook: {hook_name}")

            if not callable(hook_func):
                raise ExtensionError(f"Hook {hook_name} is not callable")

    def _check_dependencies(self, extension: Extension) -> None:
        """Check if extension dependencies are satisfied."""
        for dep in extension.dependencies:
            # Check if dependency is loaded
            dep_found = False
            for loaded_ext in self.extensions.values():
                if dep in loaded_ext.provides or loaded_ext.name == dep:
                    dep_found = True
                    break

            if not dep_found:
                raise ExtensionError(f"Extension {extension.name} requires {dep}")

    def _update_dependency_graph(self, extension: Extension) -> None:
        """Update dependency graph with new extension."""
        self._dependency_graph[extension.id] = set(extension.dependencies)

        # Recompute load order
        self._compute_load_order()

    def _remove_from_dependency_graph(self, extension: Extension) -> None:
        """Remove extension from dependency graph."""
        if extension.id in self._dependency_graph:
            del self._dependency_graph[extension.id]

        # Remove as dependency from other extensions
        for deps in self._dependency_graph.values():
            deps.discard(extension.id)
            deps.discard(extension.name)

    def _compute_load_order(self) -> None:
        """Compute topological sort for extension load order."""
        # Simple topological sort
        visited = set()
        temp_visited = set()
        self._load_order = []

        def visit(ext_id: str):
            if ext_id in temp_visited:
                raise ExtensionError(f"Circular dependency detected involving {ext_id}")

            if ext_id in visited:
                return

            temp_visited.add(ext_id)

            # Visit dependencies first
            for dep in self._dependency_graph.get(ext_id, set()):
                # Find extension by name or ID
                dep_id = None
                for eid, ext in self.extensions.items():
                    if ext.name == dep or eid == dep:
                        dep_id = eid
                        break

                if dep_id:
                    visit(dep_id)

            temp_visited.remove(ext_id)
            visited.add(ext_id)
            self._load_order.append(ext_id)

        for ext_id in self._dependency_graph:
            if ext_id not in visited:
                visit(ext_id)

    def _register_extension_hooks(self, extension: Extension) -> None:
        """Register extension hooks in the hook registry."""
        for hook_name in extension.hooks:
            if hook_name not in self._hook_listeners:
                self._hook_listeners[hook_name] = []
            self._hook_listeners[hook_name].append(extension.id)

    def _unregister_extension_hooks(self, extension: Extension) -> None:
        """Unregister extension hooks from the hook registry."""
        for hook_name in extension.hooks:
            if hook_name in self._hook_listeners:
                if extension.id in self._hook_listeners[hook_name]:
                    self._hook_listeners[hook_name].remove(extension.id)

                # Clean up empty hook lists
                if not self._hook_listeners[hook_name]:
                    del self._hook_listeners[hook_name]

    def _monitor_files(self) -> None:
        """Monitor extension files for changes (hot reload)."""
        logger.info("Starting extension file monitoring")

        while not self._shutdown_event.wait(1.0):  # Check every second
            try:
                for file_path, last_modified in list(self._file_monitors.items()):
                    path = Path(file_path)
                    if path.exists():
                        current_modified = path.stat().st_mtime
                        if current_modified > last_modified:
                            logger.info(f"Extension file changed: {file_path}")

                            # Find extension to reload
                            extension_to_reload = None
                            for ext in self.extensions.values():
                                if str(ext.path) == file_path:
                                    extension_to_reload = ext
                                    break

                            if extension_to_reload:
                                try:
                                    self.reload_extension(extension_to_reload.id)
                                    self._file_monitors[file_path] = current_modified
                                except Exception as e:
                                    logger.error(f"Hot reload failed for {file_path}: {e}")
                    else:
                        # File was deleted
                        logger.info(f"Extension file deleted: {file_path}")
                        del self._file_monitors[file_path]

            except Exception as e:
                logger.error(f"Error in file monitoring: {e}")

        logger.info("Extension file monitoring stopped")

    def load_all_extensions(self) -> None:
        """Discover and load all extensions in the extensions directory."""
        logger.info("Loading all extensions...")

        extension_paths = self.discover_extensions()
        loaded_count = 0
        failed_count = 0

        for path in extension_paths:
            try:
                self.load_extension(path)
                loaded_count += 1
            except Exception as e:
                logger.error(f"Failed to load extension {path}: {e}")
                failed_count += 1

        logger.info(f"Loaded {loaded_count} extensions, {failed_count} failed")

    def shutdown(self) -> None:
        """Shutdown extension system and cleanup resources."""
        logger.info("Shutting down extension system")

        # Disable hot reload
        self.disable_hot_reload()

        # Unload all extensions
        extension_ids = list(self.extensions.keys())
        for ext_id in extension_ids:
            try:
                self.unload_extension(ext_id)
            except Exception as e:
                logger.error(f"Error unloading extension {ext_id}: {e}")

        # Cleanup sandbox
        self.sandbox.shutdown()

        logger.info("Extension system shutdown complete")
