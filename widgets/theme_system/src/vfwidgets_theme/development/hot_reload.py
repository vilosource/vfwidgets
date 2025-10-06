#!/usr/bin/env python3
"""Hot Reload System - Task 18

This module provides hot reloading functionality for theme files during development.
It watches theme files for changes and automatically reloads them with debouncing
to prevent rapid successive reloads.

Features:
- QFileSystemWatcher for file monitoring
- Debounced reload to prevent rapid reloads
- Error recovery on bad reload attempts
- Development mode toggle
- Integration with ThemedApplication
"""

import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Set

try:
    from PySide6.QtCore import QFileSystemWatcher, QObject, QTimer, Signal

    QT_AVAILABLE = True
except ImportError:
    # Mock classes for testing without Qt
    class QObject:
        pass

    class QTimer:
        def __init__(self):
            self.single_shot = False
            self.timeout = MockSignal()

        def setSingleShot(self, single_shot: bool):
            self.single_shot = single_shot

        def start(self, ms: int):
            pass

        def stop(self):
            pass

    class QFileSystemWatcher:
        def __init__(self):
            self.fileChanged = MockSignal()
            self.directoryChanged = MockSignal()

        def addPath(self, path: str) -> bool:
            return True

        def removePath(self, path: str) -> bool:
            return True

        def files(self) -> list:
            return []

        def directories(self) -> list:
            return []

    class Signal:
        def connect(self, func):
            pass

        def emit(self, *args):
            pass

    class MockSignal:
        def connect(self, func):
            self._func = func

        def emit(self, *args):
            if hasattr(self, "_func"):
                self._func(*args)

    QT_AVAILABLE = False


@dataclass
class ReloadEvent:
    """Information about a theme reload event."""

    file_path: Path
    timestamp: float
    success: bool
    error: Optional[str] = None
    reload_time_ms: Optional[float] = None


class HotReloader(QObject):
    """Watch and reload themes during development.

    Features:
    - File system watching with QFileSystemWatcher
    - Debounced reloading to prevent rapid successive reloads
    - Error recovery with graceful fallback
    - Development mode toggle
    - Performance monitoring
    """

    # Signals
    theme_reloaded = Signal(str, bool)  # (file_path, success)
    reload_error = Signal(str, str)  # (file_path, error_message)

    def __init__(self, debounce_ms: int = 100):
        """Initialize hot reloader.

        Args:
            debounce_ms: Debounce time in milliseconds (default: 100ms)

        """
        super().__init__()

        self.debounce_ms = debounce_ms
        self.enabled = False
        self.logger = logging.getLogger(__name__)

        # File system watcher
        self.watcher = QFileSystemWatcher()
        self.watcher.fileChanged.connect(self._on_file_changed)
        self.watcher.directoryChanged.connect(self._on_directory_changed)

        # Debounce timer
        self.reload_timer = QTimer()
        self.reload_timer.setSingleShot(True)
        self.reload_timer.timeout.connect(self._perform_reload)

        # State tracking
        self.watched_files: Dict[str, Path] = {}
        self.watched_directories: Set[Path] = set()
        self.pending_reloads: Set[Path] = set()
        self.reload_callback: Optional[Callable[[Path], bool]] = None
        self.last_reload_times: Dict[Path, float] = {}

        # Statistics
        self.reload_events: list[ReloadEvent] = []
        self.total_reloads = 0
        self.successful_reloads = 0

        self.logger.info(f"HotReloader initialized with {debounce_ms}ms debounce")

    def enable(self, enabled: bool = True):
        """Enable or disable hot reloading."""
        self.enabled = enabled
        self.logger.info(f"Hot reloading {'enabled' if enabled else 'disabled'}")

        if not enabled:
            self.stop_watching()

    def is_enabled(self) -> bool:
        """Check if hot reloading is enabled."""
        return self.enabled

    def set_reload_callback(self, callback: Callable[[Path], bool]):
        """Set callback function for theme reloading.

        Args:
            callback: Function that takes a Path and returns bool (success)

        """
        self.reload_callback = callback
        self.logger.debug("Reload callback set")

    def watch_file(self, file_path: Path) -> bool:
        """Watch a specific theme file for changes.

        Args:
            file_path: Path to theme file to watch

        Returns:
            bool: True if watching started successfully

        """
        if not self.enabled:
            self.logger.warning("Cannot watch file - hot reloading disabled")
            return False

        if not file_path.exists():
            self.logger.warning(f"Cannot watch non-existent file: {file_path}")
            return False

        file_str = str(file_path.absolute())

        if file_str in self.watched_files:
            self.logger.debug(f"File already being watched: {file_path}")
            return True

        success = self.watcher.addPath(file_str)
        if success:
            self.watched_files[file_str] = file_path
            self.logger.info(f"Now watching file: {file_path}")
        else:
            self.logger.error(f"Failed to watch file: {file_path}")

        return success

    def watch_directory(self, directory_path: Path, recursive: bool = False) -> bool:
        """Watch a directory for theme file changes.

        Args:
            directory_path: Path to directory to watch
            recursive: Whether to watch subdirectories (not implemented yet)

        Returns:
            bool: True if watching started successfully

        """
        if not self.enabled:
            self.logger.warning("Cannot watch directory - hot reloading disabled")
            return False

        if not directory_path.exists() or not directory_path.is_dir():
            self.logger.warning(f"Cannot watch non-existent directory: {directory_path}")
            return False

        if recursive:
            self.logger.warning("Recursive directory watching not yet implemented")

        dir_str = str(directory_path.absolute())

        if directory_path in self.watched_directories:
            self.logger.debug(f"Directory already being watched: {directory_path}")
            return True

        success = self.watcher.addPath(dir_str)
        if success:
            self.watched_directories.add(directory_path)
            self.logger.info(f"Now watching directory: {directory_path}")

            # Also watch existing theme files in the directory
            theme_files = list(directory_path.glob("*.json")) + list(
                directory_path.glob("*.vftheme")
            )
            for theme_file in theme_files:
                self.watch_file(theme_file)
        else:
            self.logger.error(f"Failed to watch directory: {directory_path}")

        return success

    def unwatch_file(self, file_path: Path) -> bool:
        """Stop watching a specific file.

        Args:
            file_path: Path to file to stop watching

        Returns:
            bool: True if unwatching succeeded

        """
        file_str = str(file_path.absolute())

        if file_str not in self.watched_files:
            self.logger.debug(f"File not being watched: {file_path}")
            return True

        success = self.watcher.removePath(file_str)
        if success:
            del self.watched_files[file_str]
            self.logger.info(f"Stopped watching file: {file_path}")
        else:
            self.logger.error(f"Failed to stop watching file: {file_path}")

        return success

    def unwatch_directory(self, directory_path: Path) -> bool:
        """Stop watching a directory.

        Args:
            directory_path: Path to directory to stop watching

        Returns:
            bool: True if unwatching succeeded

        """
        if directory_path not in self.watched_directories:
            self.logger.debug(f"Directory not being watched: {directory_path}")
            return True

        dir_str = str(directory_path.absolute())
        success = self.watcher.removePath(dir_str)
        if success:
            self.watched_directories.remove(directory_path)
            self.logger.info(f"Stopped watching directory: {directory_path}")
        else:
            self.logger.error(f"Failed to stop watching directory: {directory_path}")

        return success

    def stop_watching(self):
        """Stop watching all files and directories."""
        # Stop timer
        self.reload_timer.stop()

        # Remove all watched paths
        for file_path in list(self.watched_files.values()):
            self.unwatch_file(file_path)

        for directory_path in list(self.watched_directories):
            self.unwatch_directory(directory_path)

        self.pending_reloads.clear()
        self.logger.info("Stopped watching all files and directories")

    def get_watched_files(self) -> list[Path]:
        """Get list of currently watched files."""
        return list(self.watched_files.values())

    def get_watched_directories(self) -> list[Path]:
        """Get list of currently watched directories."""
        return list(self.watched_directories)

    def _on_file_changed(self, file_path: str):
        """Handle file change signal from QFileSystemWatcher."""
        if not self.enabled:
            return

        path_obj = Path(file_path)

        # Check if file still exists (might be deleted)
        if not path_obj.exists():
            self.logger.debug(f"File deleted or moved: {path_obj}")
            return

        # Check if this is a theme file
        if path_obj.suffix not in [".json", ".vftheme"]:
            self.logger.debug(f"Ignoring non-theme file: {path_obj}")
            return

        self.logger.debug(f"File changed: {path_obj}")
        self._queue_reload(path_obj)

    def _on_directory_changed(self, directory_path: str):
        """Handle directory change signal from QFileSystemWatcher."""
        if not self.enabled:
            return

        dir_path = Path(directory_path)
        self.logger.debug(f"Directory changed: {dir_path}")

        # Find new theme files and watch them
        theme_files = list(dir_path.glob("*.json")) + list(dir_path.glob("*.vftheme"))
        for theme_file in theme_files:
            if str(theme_file.absolute()) not in self.watched_files:
                self.logger.info(f"New theme file detected: {theme_file}")
                self.watch_file(theme_file)
                self._queue_reload(theme_file)

    def _queue_reload(self, file_path: Path):
        """Queue a file for reloading with debouncing.

        Args:
            file_path: Path to file to reload

        """
        # Add to pending reloads
        self.pending_reloads.add(file_path)

        # Start/restart debounce timer
        self.reload_timer.stop()
        self.reload_timer.start(self.debounce_ms)

        self.logger.debug(f"Queued reload for: {file_path} (debounce: {self.debounce_ms}ms)")

    def _perform_reload(self):
        """Perform the actual theme reload for all pending files."""
        if not self.enabled or not self.pending_reloads:
            return

        files_to_reload = list(self.pending_reloads)
        self.pending_reloads.clear()

        self.logger.info(f"Performing hot reload for {len(files_to_reload)} files")

        for file_path in files_to_reload:
            self._reload_single_file(file_path)

    def _reload_single_file(self, file_path: Path):
        """Reload a single theme file.

        Args:
            file_path: Path to theme file to reload

        """
        start_time = time.perf_counter()
        success = False
        error_msg = None

        try:
            if self.reload_callback:
                self.logger.debug(f"Reloading theme: {file_path}")
                success = self.reload_callback(file_path)

                if success:
                    self.logger.info(f"Successfully reloaded: {file_path}")
                    self.successful_reloads += 1
                else:
                    error_msg = "Reload callback returned False"
                    self.logger.warning(f"Reload failed: {file_path}")
            else:
                error_msg = "No reload callback set"
                self.logger.error("Cannot reload - no callback set")

        except Exception as e:
            success = False
            error_msg = str(e)
            self.logger.error(f"Exception during reload of {file_path}: {e}")

        # Calculate reload time
        end_time = time.perf_counter()
        reload_time_ms = (end_time - start_time) * 1000

        # Update statistics
        self.total_reloads += 1
        self.last_reload_times[file_path] = time.time()

        # Create reload event
        event = ReloadEvent(
            file_path=file_path,
            timestamp=time.time(),
            success=success,
            error=error_msg,
            reload_time_ms=reload_time_ms,
        )
        self.reload_events.append(event)

        # Keep only last 100 events
        if len(self.reload_events) > 100:
            self.reload_events = self.reload_events[-100:]

        # Emit signals
        self.theme_reloaded.emit(str(file_path), success)
        if not success and error_msg:
            self.reload_error.emit(str(file_path), error_msg)

        # Performance check
        if reload_time_ms > 200:  # Performance requirement: <200ms
            self.logger.warning(f"Slow reload: {reload_time_ms:.2f}ms for {file_path}")
        else:
            self.logger.debug(f"Reload time: {reload_time_ms:.2f}ms for {file_path}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get hot reload statistics."""
        success_rate = (
            (self.successful_reloads / self.total_reloads * 100) if self.total_reloads > 0 else 0
        )

        recent_events = [
            e for e in self.reload_events if e.timestamp > time.time() - 300
        ]  # Last 5 minutes
        avg_reload_time = 0.0
        if recent_events:
            reload_times = [e.reload_time_ms for e in recent_events if e.reload_time_ms is not None]
            avg_reload_time = sum(reload_times) / len(reload_times) if reload_times else 0.0

        return {
            "enabled": self.enabled,
            "total_reloads": self.total_reloads,
            "successful_reloads": self.successful_reloads,
            "success_rate": success_rate,
            "watched_files": len(self.watched_files),
            "watched_directories": len(self.watched_directories),
            "debounce_ms": self.debounce_ms,
            "recent_events_count": len(recent_events),
            "avg_reload_time_ms": avg_reload_time,
            "last_reload_time": (
                max(self.last_reload_times.values()) if self.last_reload_times else None
            ),
        }

    def get_recent_events(self, limit: int = 10) -> list[ReloadEvent]:
        """Get recent reload events."""
        return self.reload_events[-limit:] if self.reload_events else []


def debounced(wait_ms: int):
    """Decorator to debounce function calls.

    Args:
        wait_ms: Wait time in milliseconds

    """

    def decorator(func):
        last_called = [0.0]

        def wrapper(*args, **kwargs):
            now = time.time()
            if now - last_called[0] >= wait_ms / 1000.0:
                last_called[0] = now
                return func(*args, **kwargs)

        return wrapper

    return decorator


# Development mode utilities
class DevModeManager:
    """Manage development mode settings for hot reloading."""

    _instance = None
    _dev_mode = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def is_dev_mode(cls) -> bool:
        """Check if development mode is enabled."""
        # Check environment variable
        env_dev_mode = os.environ.get("VFWIDGETS_DEV_MODE", "").lower() in (
            "1",
            "true",
            "yes",
            "on",
        )

        # Use class variable if set, otherwise use environment
        return cls._dev_mode or env_dev_mode

    @classmethod
    def enable_dev_mode(cls, enabled: bool = True):
        """Enable or disable development mode."""
        cls._dev_mode = enabled
        logging.getLogger(__name__).info(f"Development mode {'enabled' if enabled else 'disabled'}")

    @classmethod
    def get_instance(cls):
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
