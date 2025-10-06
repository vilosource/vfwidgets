"""ThemeManager as facade coordinating theme system components.

This module provides the ThemeManager class that handles theme lifecycle
management, loading, and coordination. It follows the Single Responsibility
Principle by acting as a facade that coordinates specialized components
while providing a clean, unified interface.

Key Classes:
- ThemeManager: Main facade coordinating all theme operations
- FileThemeLoader: Loads themes from files (JSON, YAML formats)
- ThemeManagerStats: Statistics tracking for theme operations

Design Principles:
- Single Responsibility: Manager coordinates but doesn't implement details
- Dependency Injection: All dependencies are injected, not hardcoded
- Clean Architecture: Manager delegates to specialized components
- Performance: Efficient coordination with caching and batching
- Thread Safety: Safe concurrent theme operations

Performance Requirements:
- Theme switching: < 100ms for 100 widgets
- Theme loading: < 200ms including validation
- Memory overhead: < 2KB per managed theme
- Concurrent access: Thread-safe with minimal locking
"""

import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Import Qt components with fallback for headless testing
try:
    from PySide6.QtCore import QObject
    from PySide6.QtWidgets import QApplication, QWidget

    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False

    # Create mock classes for headless testing
    class QObject:
        def __init__(self):
            pass

    class QWidget(QObject):
        pass


# Import foundation modules
from ..errors import ThemeApplicationError, ThemeLoadError, ThemeNotFoundError
from ..lifecycle import LifecycleManager
from ..logging import get_debug_logger
from ..protocols import ThemeChangeCallback
from ..threading import ThreadSafeThemeManager
from .applicator import ThemeApplicator, create_theme_applicator
from .notifier import ThemeNotifier, create_theme_notifier
from .provider import DefaultThemeProvider, create_default_provider
from .registry import ThemeWidgetRegistry, create_widget_registry
from .repository import ThemeRepository, create_theme_repository

# Import core components
from .theme import Theme

logger = get_debug_logger(__name__)


@dataclass
class ThemeManagerStats:
    """Statistics for theme manager operations."""

    theme_switches: int = 0
    themes_loaded: int = 0
    themes_saved: int = 0
    widgets_registered: int = 0
    callbacks_registered: int = 0
    errors: int = 0
    total_operation_time: float = 0.0


class ThemeManager:
    """Main facade coordinating all theme system components.

    The ThemeManager acts as the primary interface for theme operations,
    coordinating between specialized components:
    - ThemeRepository: Theme storage and retrieval
    - ThemeApplicator: Theme application to widgets and application
    - ThemeNotifier: Change notifications
    - ThemeProvider: Theme data access with caching
    - ThemeWidgetRegistry: Widget registration and tracking

    This design ensures each component has a single responsibility
    while the manager provides a clean, unified interface that
    ThemedWidget and ThemedApplication can use.
    """

    _instance: Optional["ThemeManager"] = None
    _instance_lock = threading.Lock()

    def __init__(
        self,
        repository: Optional[ThemeRepository] = None,
        applicator: Optional[ThemeApplicator] = None,
        notifier: Optional[ThemeNotifier] = None,
        provider: Optional[DefaultThemeProvider] = None,
        widget_registry: Optional[ThemeWidgetRegistry] = None,
        lifecycle_manager: Optional[LifecycleManager] = None,
        thread_manager: Optional[ThreadSafeThemeManager] = None,
    ):
        """Initialize theme manager with dependency injection.

        Args:
            repository: Theme storage and retrieval
            applicator: Theme application coordinator
            notifier: Change notification coordinator
            provider: Theme data provider with caching
            widget_registry: Widget registration and tracking
            lifecycle_manager: Widget lifecycle management
            thread_manager: Thread-safe operations

        """
        # Initialize core components with dependency injection
        self._widget_registry = widget_registry or create_widget_registry()
        self._repository = repository or create_theme_repository()
        self._applicator = applicator or create_theme_applicator(self._widget_registry)
        self._notifier = notifier or create_theme_notifier()
        self._provider = provider or create_default_provider()

        # Optional components
        self._lifecycle_manager = lifecycle_manager
        self._thread_manager = thread_manager

        # Internal state
        self._current_theme: Optional[Theme] = None
        self._stats = ThemeManagerStats()
        self._lock = threading.RLock()

        # Initialize with built-in themes
        self._initialize_builtin_themes()

        logger.debug("ThemeManager initialized with all components")

    @classmethod
    def get_instance(cls) -> "ThemeManager":
        """Get singleton instance of ThemeManager.

        This method ensures thread-safe singleton access for ThemedApplication.
        Creates the manager on first call with default components.

        Returns:
            ThemeManager singleton instance

        """
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = create_theme_manager()
                    logger.debug("Created ThemeManager singleton instance")
        return cls._instance

    def _initialize_builtin_themes(self) -> None:
        """Initialize built-in themes from repository."""
        try:
            builtin_themes = self._repository.list_themes()
            for theme_name in builtin_themes:
                theme = self._repository.get_theme(theme_name)
                self._provider.add_theme(theme)

            # Set default theme as current
            if "default" in builtin_themes:
                self._current_theme = self._repository.get_theme("default")
                self._provider.set_current_theme("default")

            logger.debug(f"Initialized {len(builtin_themes)} built-in themes")

        except Exception as e:
            logger.error(f"Error initializing built-in themes: {e}")

    @property
    def current_theme(self) -> Optional[Theme]:
        """Get currently active theme."""
        with self._lock:
            return self._current_theme

    def add_theme(self, theme: Theme) -> None:
        """Add theme to manager.

        Args:
            theme: Theme to add

        """
        try:
            with self._lock:
                self._repository.add_theme(theme)
                self._provider.add_theme(theme)

            logger.debug(f"Added theme: {theme.name}")

        except Exception as e:
            logger.error(f"Error adding theme {theme.name}: {e}")
            with self._lock:
                self._stats.errors += 1
            raise ThemeLoadError(f"Failed to add theme: {e}")

    def get_theme(self, name: str) -> Theme:
        """Get theme by name.

        Args:
            name: Theme name

        Returns:
            Theme object

        Raises:
            ThemeNotFoundError: If theme not found

        """
        try:
            theme = self._repository.get_theme(name)
            return theme

        except ThemeNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting theme {name}: {e}")
            with self._lock:
                self._stats.errors += 1
            raise ThemeNotFoundError(f"Error accessing theme '{name}': {e}")

    def has_theme(self, name: str) -> bool:
        """Check if theme exists.

        Args:
            name: Theme name

        Returns:
            True if theme exists

        """
        return self._repository.has_theme(name)

    def list_themes(self) -> List[str]:
        """List all available themes.

        Returns:
            List of theme names

        """
        return self._repository.list_themes()

    def get_builtin_themes(self) -> List[str]:
        """Get list of built-in theme names.

        Returns:
            List of built-in theme names

        """
        all_themes = self._repository.list_themes()
        # Built-in themes are those loaded at initialization
        builtin_themes = ["default", "dark", "light", "minimal"]
        return [name for name in builtin_themes if name in all_themes]

    def set_theme(self, theme_name: str) -> None:
        """Set active theme system-wide.

        This method coordinates theme switching across all components:
        1. Validates the theme exists
        2. Applies theme to all registered widgets
        3. Updates application-level styling
        4. Notifies all registered callbacks
        5. Updates current theme state

        Args:
            theme_name: Name of theme to set

        Raises:
            ThemeNotFoundError: If theme doesn't exist
            ThemeApplicationError: If theme application fails

        """
        start_time = time.time()

        try:
            with self._lock:
                # Validate theme exists
                if not self.has_theme(theme_name):
                    raise ThemeNotFoundError(f"Theme '{theme_name}' not found")

                theme = self.get_theme(theme_name)

                # Apply theme globally through applicator
                results = self._applicator.apply_theme_globally(theme)

                # Update provider state
                self._provider.set_current_theme(theme_name)

                # Notify all registered callbacks
                self._notifier.notify_theme_changed(theme_name)

                # Update current theme
                self._current_theme = theme

                # Update statistics
                self._stats.theme_switches += 1
                self._stats.total_operation_time += time.time() - start_time

                logger.debug(
                    f"Set theme '{theme_name}': {len(results)} widgets updated, "
                    f"{sum(1 for success in results.values() if success)} successful"
                )

        except (ThemeNotFoundError, ThemeApplicationError):
            raise
        except Exception as e:
            logger.error(f"Error setting theme {theme_name}: {e}")
            with self._lock:
                self._stats.errors += 1
            raise ThemeApplicationError(f"Failed to set theme '{theme_name}': {e}")

    def reset_to_default(self) -> None:
        """Reset to default theme."""
        if self.has_theme("default"):
            self.set_theme("default")
        else:
            logger.warning("Default theme not available for reset")

    def register_widget(self, widget: QObject) -> str:
        """Register widget for theme management.

        Args:
            widget: Widget to register

        Returns:
            Unique widget ID

        """
        try:
            # Register with notifier for change notifications
            self._notifier.register_widget(widget)

            # Register with widget registry for tracking
            widget_id = self._widget_registry.register_widget(widget)

            # Apply current theme if available
            if self._current_theme:
                self._applicator.apply_theme_to_widget(widget_id, self._current_theme)

            with self._lock:
                self._stats.widgets_registered += 1

            logger.debug(f"Registered widget: {widget_id}")
            return widget_id

        except Exception as e:
            logger.error(f"Error registering widget: {e}")
            with self._lock:
                self._stats.errors += 1
            raise ThemeApplicationError(f"Failed to register widget: {e}")

    def unregister_widget(self, widget: QObject) -> bool:
        """Unregister widget from theme management.

        Args:
            widget: Widget to unregister

        Returns:
            True if successfully unregistered

        """
        try:
            success = self._notifier.unregister_widget(widget)

            if success:
                with self._lock:
                    self._stats.widgets_registered -= 1

            return success

        except Exception as e:
            logger.error(f"Error unregistering widget: {e}")
            return False

    def is_widget_registered(self, widget: QObject) -> bool:
        """Check if widget is registered.

        Args:
            widget: Widget to check

        Returns:
            True if widget is registered

        """
        return self._notifier.is_widget_registered(widget)

    def load_theme_from_file(self, file_path: Union[str, Path]) -> Theme:
        """Load theme from file and add to manager.

        Args:
            file_path: Path to theme file

        Returns:
            Loaded theme

        Raises:
            ThemeLoadError: If file cannot be loaded

        """
        start_time = time.time()

        try:
            theme = self._repository.load_from_file(file_path)
            self._provider.add_theme(theme)

            with self._lock:
                self._stats.themes_loaded += 1
                self._stats.total_operation_time += time.time() - start_time

            logger.debug(f"Loaded theme '{theme.name}' from file: {file_path}")
            return theme

        except Exception as e:
            logger.error(f"Error loading theme from file {file_path}: {e}")
            with self._lock:
                self._stats.errors += 1
            raise ThemeLoadError(f"Failed to load theme from {file_path}: {e}")

    def save_theme_to_file(self, theme_name: str, file_path: Union[str, Path]) -> None:
        """Save theme to file.

        Args:
            theme_name: Name of theme to save
            file_path: Path to save file

        Raises:
            ThemeNotFoundError: If theme doesn't exist
            ThemeLoadError: If file cannot be saved

        """
        start_time = time.time()

        try:
            theme = self.get_theme(theme_name)
            self._repository.save_to_file(theme, file_path)

            with self._lock:
                self._stats.themes_saved += 1
                self._stats.total_operation_time += time.time() - start_time

            logger.debug(f"Saved theme '{theme_name}' to file: {file_path}")

        except ThemeNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error saving theme {theme_name} to file {file_path}: {e}")
            with self._lock:
                self._stats.errors += 1
            raise ThemeLoadError(f"Failed to save theme to {file_path}: {e}")

    def discover_themes(self, directory: Union[str, Path], recursive: bool = True) -> List[Theme]:
        """Discover and load themes from directory.

        Args:
            directory: Directory to scan
            recursive: Whether to scan subdirectories

        Returns:
            List of discovered themes

        """
        try:
            discovered_themes = self._repository.discover_themes(directory, recursive)

            # Add discovered themes to provider
            for theme in discovered_themes:
                self._provider.add_theme(theme)

            with self._lock:
                self._stats.themes_loaded += len(discovered_themes)

            logger.debug(f"Discovered {len(discovered_themes)} themes from {directory}")
            return discovered_themes

        except Exception as e:
            logger.error(f"Error discovering themes in {directory}: {e}")
            with self._lock:
                self._stats.errors += 1
            raise ThemeLoadError(f"Failed to discover themes in {directory}: {e}")

    def register_theme_change_callback(self, callback: ThemeChangeCallback) -> str:
        """Register callback for theme change notifications.

        Args:
            callback: Callback function

        Returns:
            Unique callback ID

        """
        try:
            callback_id = self._notifier.register_callback(callback)

            with self._lock:
                self._stats.callbacks_registered += 1

            logger.debug(f"Registered theme change callback: {callback_id}")
            return callback_id

        except Exception as e:
            logger.error(f"Error registering theme change callback: {e}")
            with self._lock:
                self._stats.errors += 1
            raise ThemeApplicationError(f"Failed to register callback: {e}")

    def unregister_theme_change_callback(self, callback_id: str) -> bool:
        """Unregister theme change callback.

        Args:
            callback_id: Callback ID to remove

        Returns:
            True if successfully removed

        """
        try:
            success = self._notifier.unregister_callback(callback_id)

            if success:
                with self._lock:
                    self._stats.callbacks_registered -= 1

            return success

        except Exception as e:
            logger.error(f"Error unregistering callback {callback_id}: {e}")
            return False

    def clear_themes(self) -> None:
        """Clear all custom themes, preserving built-in themes."""
        try:
            self._repository.clear_themes()

            # Reinitialize built-in themes in provider
            self._provider = create_default_provider()
            self._initialize_builtin_themes()

            # Reset to default theme if available
            if self.has_theme("default"):
                self._current_theme = self.get_theme("default")
                self._provider.set_current_theme("default")
            else:
                self._current_theme = None

            logger.debug("Cleared all custom themes, preserved built-ins")

        except Exception as e:
            logger.error(f"Error clearing themes: {e}")
            with self._lock:
                self._stats.errors += 1

    def get_statistics(self) -> Dict[str, Any]:
        """Get theme manager statistics.

        Returns:
            Dictionary with manager statistics

        """
        with self._lock:
            base_stats = {
                "total_themes": len(self.list_themes()),
                "builtin_themes": len(self.get_builtin_themes()),
                "custom_themes": len(self.list_themes()) - len(self.get_builtin_themes()),
                "current_theme": self._current_theme.name if self._current_theme else None,
                "widgets_registered": self._stats.widgets_registered,
                "callbacks_registered": self._stats.callbacks_registered,
                "theme_switches": self._stats.theme_switches,
                "themes_loaded": self._stats.themes_loaded,
                "themes_saved": self._stats.themes_saved,
                "errors": self._stats.errors,
                "total_operation_time": self._stats.total_operation_time,
                "average_operation_time": (
                    self._stats.total_operation_time
                    / max(
                        1,
                        self._stats.theme_switches
                        + self._stats.themes_loaded
                        + self._stats.themes_saved,
                    )
                ),
            }

            # Add component statistics
            try:
                base_stats.update(
                    {
                        "repository_stats": self._repository.get_statistics(),
                        "applicator_stats": self._applicator.get_statistics(),
                        "notifier_stats": self._notifier.get_statistics(),
                    }
                )
            except Exception as e:
                logger.error(f"Error getting component statistics: {e}")

            return base_stats

    def shutdown(self) -> None:
        """Shutdown theme manager and clean up resources."""
        try:
            self._applicator.shutdown()
            self._notifier.shutdown()
            logger.debug("ThemeManager shutdown completed")

        except Exception as e:
            logger.error(f"Error during manager shutdown: {e}")


def create_theme_manager(
    repository: Optional[ThemeRepository] = None,
    applicator: Optional[ThemeApplicator] = None,
    notifier: Optional[ThemeNotifier] = None,
    widget_registry: Optional[ThemeWidgetRegistry] = None,
    lifecycle_manager: Optional[LifecycleManager] = None,
    thread_manager: Optional[ThreadSafeThemeManager] = None,
) -> ThemeManager:
    """Factory function for creating ThemeManager with dependency injection.

    This factory function sets up a fully configured ThemeManager
    with all necessary dependencies, using defaults where not provided.

    Args:
        repository: Theme storage and retrieval
        applicator: Theme application coordinator
        notifier: Change notification coordinator
        widget_registry: Widget registration and tracking
        lifecycle_manager: Widget lifecycle management
        thread_manager: Thread-safe operations

    Returns:
        Configured ThemeManager instance

    """
    logger.debug("Creating theme manager with factory function")

    # Create widget registry first (needed by other components)
    widget_registry = widget_registry or create_widget_registry()

    # Create other components with proper dependencies
    repository = repository or create_theme_repository()
    applicator = applicator or create_theme_applicator(widget_registry)
    notifier = notifier or create_theme_notifier()
    provider = create_default_provider()

    manager = ThemeManager(
        repository=repository,
        applicator=applicator,
        notifier=notifier,
        provider=provider,
        widget_registry=widget_registry,
        lifecycle_manager=lifecycle_manager,
        thread_manager=thread_manager,
    )

    logger.debug("Created theme manager with all components initialized")
    return manager


__all__ = [
    "ThemeManager",
    "ThemeManagerStats",
    "create_theme_manager",
]
