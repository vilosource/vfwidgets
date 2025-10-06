"""ThemeApplicator for applying themes to widgets and applications.

This module provides the ThemeApplicator class that handles theme application
to individual widgets and the entire application. It follows the Single
Responsibility Principle by focusing solely on theme application logic.

Key Classes:
- ThemeApplicator: Main coordinator for theme application
- WidgetThemeApplicator: Applies themes to individual widgets
- ApplicationThemeApplicator: Applies themes at application level
- BatchThemeUpdater: Efficient bulk theme updates
- StyleInvalidator: Manages style cache invalidation
- AsyncThemeApplicator: Non-blocking theme application
- PlatformThemeAdapter: Platform-specific adaptations

Design Principles:
- Single Responsibility: Applicator focuses only on theme application
- Performance: Batch updates and caching for efficiency
- Thread Safety: Safe concurrent theme application
- Error Recovery: Graceful handling of application errors
- Platform Awareness: Adapts themes for different platforms

Performance Requirements:
- Theme switching: < 100ms for 100 widgets
- Batch update overhead: < 10ms additional cost
- Memory overhead per widget: < 1KB
- Async operations: Non-blocking with callback support
"""

import platform
import threading
import time
import weakref
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

# Import Qt components with fallback for headless testing
try:
    from PySide6.QtCore import QObject, QThread, QTimer, Signal
    from PySide6.QtGui import QPalette
    from PySide6.QtWidgets import QApplication, QWidget

    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False

    # Create mock classes for headless testing
    class QObject:
        def __init__(self):
            pass

    class QWidget(QObject):
        def __init__(self, parent=None):
            super().__init__()

        def setStyleSheet(self, stylesheet):
            pass

        def styleSheet(self):
            return ""

    class QApplication(QObject):
        def __init__(self):
            super().__init__()

        def setStyleSheet(self, stylesheet):
            pass

        def styleSheet(self):
            return ""

        @staticmethod
        def instance():
            return None


# Import foundation modules
from ..logging import get_debug_logger
from .registry import ThemeWidgetRegistry
from .theme import PropertyResolver, Theme

logger = get_debug_logger(__name__)


@dataclass
class ApplicationStats:
    """Statistics for theme application operations."""

    widgets_themed: int = 0
    global_updates: int = 0
    batch_updates: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    errors: int = 0
    total_time: float = 0.0


class WidgetThemeApplicator:
    """Applies themes to individual widgets.

    Handles widget-specific theme application including:
    - Style sheet generation from theme data
    - Color reference resolution
    - Widget-specific style targeting
    - Error recovery for individual widgets
    """

    def __init__(self, registry: Optional[ThemeWidgetRegistry] = None):
        """Initialize widget theme applicator.

        Args:
            registry: Widget registry for tracking themed widgets

        """
        self._registry = registry
        self._property_resolver: Optional[PropertyResolver] = None
        self._style_cache: Dict[str, str] = {}
        self._lock = threading.RLock()
        logger.debug("WidgetThemeApplicator initialized")

    def apply_theme(self, widget: QWidget, theme: Theme) -> bool:
        """Apply theme to individual widget.

        Args:
            widget: Widget to theme
            theme: Theme to apply

        Returns:
            True if successfully applied

        """
        try:
            # Generate stylesheet for widget
            stylesheet = self._generate_widget_stylesheet(widget, theme)

            # Apply stylesheet to widget
            widget.setStyleSheet(stylesheet)

            logger.debug(f"Applied theme '{theme.name}' to widget {type(widget).__name__}")
            return True

        except Exception as e:
            logger.error(f"Error applying theme to widget: {e}")
            return False

    def apply_theme_by_id(self, widget_id: str, theme: Theme) -> bool:
        """Apply theme to widget by registry ID.

        Args:
            widget_id: Widget ID in registry
            theme: Theme to apply

        Returns:
            True if successfully applied

        """
        if not self._registry:
            logger.error("No registry available for widget ID lookup")
            return False

        try:
            entry = self._registry.get_entry(widget_id)
            if not entry or not entry.is_alive:
                logger.warning(f"Widget {widget_id} not found or no longer alive")
                return False

            widget = entry.widget
            success = self.apply_theme(widget, theme)

            if success:
                # Update registry metadata
                self._registry.apply_theme_to_widget(widget_id, theme.name)

            return success

        except Exception as e:
            logger.error(f"Error applying theme to widget {widget_id}: {e}")
            return False

    def apply_theme_batch(self, widget_ids: List[str], theme: Theme) -> Dict[str, bool]:
        """Apply theme to batch of widgets efficiently.

        Args:
            widget_ids: List of widget IDs
            theme: Theme to apply

        Returns:
            Dictionary mapping widget ID to success status

        """
        results = {}

        if not self._registry:
            logger.error("No registry available for batch widget application")
            return dict.fromkeys(widget_ids, False)

        # Pre-generate common stylesheet components
        with self._lock:
            base_styles = self._generate_base_styles(theme)

        for widget_id in widget_ids:
            try:
                entry = self._registry.get_entry(widget_id)
                if not entry or not entry.is_alive:
                    results[widget_id] = False
                    continue

                widget = entry.widget
                stylesheet = self._generate_widget_specific_stylesheet(widget, theme, base_styles)

                widget.setStyleSheet(stylesheet)
                self._registry.apply_theme_to_widget(widget_id, theme.name)

                results[widget_id] = True

            except Exception as e:
                logger.error(f"Error applying theme to widget {widget_id}: {e}")
                results[widget_id] = False

        logger.debug(f"Batch applied theme '{theme.name}' to {len(widget_ids)} widgets")
        return results

    def _generate_widget_stylesheet(self, widget: QWidget, theme: Theme) -> str:
        """Generate complete stylesheet for widget."""
        # Create property resolver for this theme if needed
        if self._property_resolver is None or self._property_resolver.theme != theme:
            self._property_resolver = PropertyResolver(theme)

        cache_key = f"{theme.name}:{type(widget).__name__}"

        with self._lock:
            if cache_key in self._style_cache:
                return self._style_cache[cache_key]

            # Generate base styles
            base_styles = self._generate_base_styles(theme)
            stylesheet = self._generate_widget_specific_stylesheet(widget, theme, base_styles)

            # Cache the result
            self._style_cache[cache_key] = stylesheet
            return stylesheet

    def _generate_base_styles(self, theme: Theme) -> Dict[str, Any]:
        """Generate base style components from theme."""
        # Create property resolver for this theme if needed
        if self._property_resolver is None or self._property_resolver.theme != theme:
            self._property_resolver = PropertyResolver(theme)

        # Resolve all color references once
        resolved_colors = {}
        for key, value in theme.colors.items():
            resolved_colors[key] = self._property_resolver.resolve_reference(value, theme.to_dict())

        return {"colors": resolved_colors, "resolved_styles": {}}

    def _generate_widget_specific_stylesheet(
        self, widget: QWidget, theme: Theme, base_styles: Dict[str, Any]
    ) -> str:
        """Generate stylesheet specific to widget type."""
        widget_class = type(widget).__name__
        stylesheet_parts = []

        # Add global styles (apply to all widgets)
        if "*" in theme.styles:
            global_style = theme.styles["*"]
            resolved_style = self._resolve_style_references(global_style, base_styles["colors"])
            stylesheet_parts.append(f"* {{ {resolved_style} }}")

        # Add widget-specific styles
        if widget_class in theme.styles:
            widget_style = theme.styles[widget_class]
            resolved_style = self._resolve_style_references(widget_style, base_styles["colors"])
            stylesheet_parts.append(f"{widget_class} {{ {resolved_style} }}")

        # Add state-specific styles (hover, active, etc.)
        for style_key, style_value in theme.styles.items():
            if style_key.startswith(f"{widget_class}:"):
                resolved_style = self._resolve_style_references(style_value, base_styles["colors"])
                stylesheet_parts.append(f"{style_key} {{ {resolved_style} }}")

        return "\n".join(stylesheet_parts)

    def _resolve_style_references(self, style: str, colors: Dict[str, str]) -> str:
        """Resolve color references in style string."""
        resolved_style = style

        # Replace color references (@colors.key)
        for color_key, color_value in colors.items():
            reference = f"@colors.{color_key}"
            resolved_style = resolved_style.replace(reference, color_value)

        return resolved_style

    def clear_cache(self) -> None:
        """Clear style cache."""
        with self._lock:
            self._style_cache.clear()
            logger.debug("Cleared widget style cache")


class ApplicationThemeApplicator:
    """Applies themes at application level.

    Handles application-wide theme application including:
    - Global stylesheet application
    - Application palette updates
    - System-wide style coordination
    """

    def __init__(self):
        """Initialize application theme applicator."""
        self._current_theme: Optional[str] = None
        self._property_resolver: Optional[PropertyResolver] = None
        logger.debug("ApplicationThemeApplicator initialized")

    def apply_theme(self, theme: Theme) -> bool:
        """Apply theme to entire application.

        Args:
            theme: Theme to apply globally

        Returns:
            True if successfully applied

        """
        try:
            # Create property resolver for this theme if needed
            if self._property_resolver is None or self._property_resolver.theme != theme:
                self._property_resolver = PropertyResolver(theme)

            app = QApplication.instance()
            if not app:
                logger.warning("No QApplication instance found for global theme application")
                return False

            # Generate global stylesheet
            stylesheet = self._generate_application_stylesheet(theme)

            # Apply to application
            app.setStyleSheet(stylesheet)

            self._current_theme = theme.name
            logger.debug(f"Applied theme '{theme.name}' to application")
            return True

        except Exception as e:
            logger.error(f"Error applying theme to application: {e}")
            return False

    def clear_theme(self) -> bool:
        """Clear application theme.

        Returns:
            True if successfully cleared

        """
        try:
            app = QApplication.instance()
            if app:
                app.setStyleSheet("")
                self._current_theme = None
                logger.debug("Cleared application theme")
                return True
            return False

        except Exception as e:
            logger.error(f"Error clearing application theme: {e}")
            return False

    def get_current_stylesheet(self) -> str:
        """Get current application stylesheet.

        Returns:
            Current stylesheet string

        """
        try:
            app = QApplication.instance()
            if app:
                return app.styleSheet()
            return ""

        except Exception as e:
            logger.error(f"Error getting application stylesheet: {e}")
            return ""

    def _generate_application_stylesheet(self, theme: Theme) -> str:
        """Generate application-wide stylesheet."""
        stylesheet_parts = []

        # Resolve colors once
        resolved_colors = {}
        for key, value in theme.colors.items():
            resolved_colors[key] = self._property_resolver.resolve_reference(value, theme.to_dict())

        # Add all styles from theme
        for selector, style in theme.styles.items():
            resolved_style = self._resolve_style_references(style, resolved_colors)
            stylesheet_parts.append(f"{selector} {{ {resolved_style} }}")

        return "\n".join(stylesheet_parts)

    def _resolve_style_references(self, style: str, colors: Dict[str, str]) -> str:
        """Resolve references in style string."""
        resolved_style = style

        # Replace color references
        for color_key, color_value in colors.items():
            reference = f"@colors.{color_key}"
            resolved_style = resolved_style.replace(reference, color_value)

        return resolved_style


class BatchThemeUpdater:
    """Efficient bulk theme updates.

    Optimizes theme application for large numbers of widgets by:
    - Batching style generation
    - Minimizing Qt update calls
    - Parallel processing where safe
    """

    def __init__(self, registry: ThemeWidgetRegistry):
        """Initialize batch theme updater.

        Args:
            registry: Widget registry for batch operations

        """
        self._registry = registry
        self._widget_applicator = WidgetThemeApplicator(registry)
        logger.debug("BatchThemeUpdater initialized")

    def update_widgets(self, widget_ids: List[str], theme: Theme) -> Dict[str, bool]:
        """Update multiple widgets with theme efficiently.

        Args:
            widget_ids: List of widget IDs to update
            theme: Theme to apply

        Returns:
            Dictionary mapping widget ID to success status

        """
        start_time = time.time()
        results = {}

        try:
            # Use batch application for efficiency
            results = self._widget_applicator.apply_theme_batch(widget_ids, theme)

            update_time = time.time() - start_time
            success_count = sum(1 for success in results.values() if success)

            logger.debug(
                f"Batch updated {success_count}/{len(widget_ids)} widgets "
                f"with theme '{theme.name}' in {update_time:.3f}s"
            )

        except Exception as e:
            logger.error(f"Error in batch theme update: {e}")
            results = dict.fromkeys(widget_ids, False)

        return results

    def update_all_widgets(self, theme: Theme) -> Dict[str, bool]:
        """Update all registered widgets with theme.

        Args:
            theme: Theme to apply

        Returns:
            Dictionary mapping widget ID to success status

        """
        widget_ids = self._registry.list_widgets(include_dead=False)
        return self.update_widgets(widget_ids, theme)


class StyleInvalidator:
    """Manages style cache invalidation.

    Handles cache management for theme changes by:
    - Invalidating widget-specific caches
    - Coordinating cache cleanup
    - Managing theme-specific invalidation
    """

    def __init__(self):
        """Initialize style invalidator."""
        self._widget_theme_associations: Dict[weakref.ref, str] = {}
        self._lock = threading.RLock()
        logger.debug("StyleInvalidator initialized")

    def invalidate_widget(self, widget: QWidget) -> None:
        """Invalidate style cache for specific widget.

        Args:
            widget: Widget to invalidate

        """
        try:
            # Force widget to repaint/reapply styles
            # In Qt, this would typically involve calling update() or repaint()
            if hasattr(widget, "update"):
                widget.update()

            logger.debug(f"Invalidated style cache for widget {type(widget).__name__}")

        except Exception as e:
            logger.error(f"Error invalidating widget cache: {e}")

    def invalidate_all(self) -> None:
        """Invalidate all style caches."""
        with self._lock:
            self._widget_theme_associations.clear()
            logger.debug("Invalidated all style caches")

    def invalidate_theme(self, theme_name: str) -> int:
        """Invalidate caches for specific theme.

        Args:
            theme_name: Theme to invalidate

        Returns:
            Number of widgets invalidated

        """
        invalidated_count = 0

        with self._lock:
            # Find widgets associated with this theme
            widgets_to_invalidate = []
            for widget_ref, associated_theme in self._widget_theme_associations.items():
                if associated_theme == theme_name:
                    widget = widget_ref()
                    if widget:
                        widgets_to_invalidate.append(widget)

            # Invalidate each widget
            for widget in widgets_to_invalidate:
                self.invalidate_widget(widget)
                invalidated_count += 1

        logger.debug(f"Invalidated {invalidated_count} widgets for theme '{theme_name}'")
        return invalidated_count

    def associate_widget_theme(self, widget: QWidget, theme_name: str) -> None:
        """Associate widget with theme for selective invalidation.

        Args:
            widget: Widget to associate
            theme_name: Theme name

        """
        with self._lock:
            widget_ref = weakref.ref(widget)
            self._widget_theme_associations[widget_ref] = theme_name


class AsyncThemeApplicator:
    """Non-blocking theme application.

    Provides asynchronous theme application using:
    - Thread pool for parallel processing
    - Future objects for async operations
    - Callback support for completion notification
    """

    def __init__(self, registry: ThemeWidgetRegistry, max_workers: int = 4):
        """Initialize async theme applicator.

        Args:
            registry: Widget registry
            max_workers: Maximum number of worker threads

        """
        self._registry = registry
        self._widget_applicator = WidgetThemeApplicator(registry)
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        logger.debug(f"AsyncThemeApplicator initialized with {max_workers} workers")

    def apply_theme_async(
        self, widget_id: str, theme: Theme, callback: Optional[Callable[[bool, str], None]] = None
    ) -> Future[bool]:
        """Apply theme to widget asynchronously.

        Args:
            widget_id: Widget ID to theme
            theme: Theme to apply
            callback: Optional completion callback

        Returns:
            Future object for async operation

        """

        def apply_worker():
            """Worker function for async theme application."""
            try:
                success = self._widget_applicator.apply_theme_by_id(widget_id, theme)

                if callback:
                    callback(success, widget_id)

                return success

            except Exception as e:
                logger.error(f"Error in async theme application: {e}")
                if callback:
                    callback(False, widget_id)
                return False

        future = self._executor.submit(apply_worker)
        logger.debug(f"Started async theme application for widget {widget_id}")
        return future

    def apply_theme_batch_async(
        self,
        widget_ids: List[str],
        theme: Theme,
        callback: Optional[Callable[[Dict[str, bool]], None]] = None,
    ) -> Future[Dict[str, bool]]:
        """Apply theme to batch of widgets asynchronously.

        Args:
            widget_ids: List of widget IDs
            theme: Theme to apply
            callback: Optional completion callback

        Returns:
            Future object for async batch operation

        """

        def batch_worker():
            """Worker function for async batch theme application."""
            try:
                results = self._widget_applicator.apply_theme_batch(widget_ids, theme)

                if callback:
                    callback(results)

                return results

            except Exception as e:
                logger.error(f"Error in async batch theme application: {e}")
                error_results = dict.fromkeys(widget_ids, False)
                if callback:
                    callback(error_results)
                return error_results

        future = self._executor.submit(batch_worker)
        logger.debug(f"Started async batch theme application for {len(widget_ids)} widgets")
        return future

    def shutdown(self, wait: bool = True) -> None:
        """Shutdown async executor.

        Args:
            wait: Whether to wait for pending operations

        """
        self._executor.shutdown(wait=wait)
        logger.debug("Async theme applicator shutdown")


class PlatformThemeAdapter:
    """Platform-specific theme adaptations.

    Adapts themes for different platforms by:
    - Platform-specific color adjustments
    - Font family adaptations
    - System-specific style tweaks
    """

    def __init__(self):
        """Initialize platform theme adapter."""
        self._current_platform = platform.system()
        logger.debug(f"PlatformThemeAdapter initialized for {self._current_platform}")

    def adapt_theme_for_platform(self, theme: Theme) -> Theme:
        """Adapt theme for current platform.

        Args:
            theme: Base theme to adapt

        Returns:
            Platform-adapted theme

        """
        if self._current_platform == "Windows":
            return self._adapt_for_windows(theme)
        elif self._current_platform == "Darwin":  # macOS
            return self._adapt_for_macos(theme)
        elif self._current_platform == "Linux":
            return self._adapt_for_linux(theme)
        else:
            return theme  # No adaptation for unknown platforms

    def _adapt_for_windows(self, theme: Theme) -> Theme:
        """Adapt theme for Windows platform."""
        adapted_data = theme.to_dict()

        # Windows-specific font adaptations
        adapted_styles = {}
        for selector, style in adapted_data["styles"].items():
            adapted_style = style.replace("'System Font'", "'Segoe UI'")
            adapted_styles[selector] = adapted_style

        adapted_data["styles"] = adapted_styles
        return Theme.from_dict(adapted_data)

    def _adapt_for_macos(self, theme: Theme) -> Theme:
        """Adapt theme for macOS platform."""
        adapted_data = theme.to_dict()

        # macOS-specific font adaptations
        adapted_styles = {}
        for selector, style in adapted_data["styles"].items():
            adapted_style = style.replace("'System Font'", "'-apple-system'")
            adapted_styles[selector] = adapted_style

        adapted_data["styles"] = adapted_styles
        return Theme.from_dict(adapted_data)

    def _adapt_for_linux(self, theme: Theme) -> Theme:
        """Adapt theme for Linux platform."""
        adapted_data = theme.to_dict()

        # Linux-specific font adaptations
        adapted_styles = {}
        for selector, style in adapted_data["styles"].items():
            adapted_style = style.replace("'System Font'", "'Liberation Sans'")
            adapted_styles[selector] = adapted_style

        adapted_data["styles"] = adapted_styles
        return Theme.from_dict(adapted_data)


class ThemeApplicator:
    """Main coordinator for theme application operations.

    Coordinates theme application across:
    - Individual widgets via WidgetThemeApplicator
    - Application level via ApplicationThemeApplicator
    - Batch operations via BatchThemeUpdater
    - Cache management via StyleInvalidator
    - Async operations via AsyncThemeApplicator
    - Platform adaptations via PlatformThemeAdapter

    Follows Single Responsibility Principle by acting as a facade
    that delegates to specialized applicator components.
    """

    def __init__(
        self,
        registry: Optional[ThemeWidgetRegistry] = None,
        widget_applicator: Optional[WidgetThemeApplicator] = None,
        app_applicator: Optional[ApplicationThemeApplicator] = None,
        batch_updater: Optional[BatchThemeUpdater] = None,
        invalidator: Optional[StyleInvalidator] = None,
        async_applicator: Optional[AsyncThemeApplicator] = None,
        platform_adapter: Optional[PlatformThemeAdapter] = None,
    ):
        """Initialize theme applicator with dependency injection.

        Args:
            registry: Widget registry for theme tracking
            widget_applicator: Widget theme applicator
            app_applicator: Application theme applicator
            batch_updater: Batch theme updater
            invalidator: Style cache invalidator
            async_applicator: Async theme applicator
            platform_adapter: Platform theme adapter

        """
        self._registry = registry or ThemeWidgetRegistry()
        self._widget_applicator = widget_applicator or WidgetThemeApplicator(self._registry)
        self._app_applicator = app_applicator or ApplicationThemeApplicator()
        self._batch_updater = batch_updater or BatchThemeUpdater(self._registry)
        self._invalidator = invalidator or StyleInvalidator()
        self._async_applicator = async_applicator or AsyncThemeApplicator(self._registry)
        self._platform_adapter = platform_adapter or PlatformThemeAdapter()

        self._stats = ApplicationStats()
        self._lock = threading.RLock()

        logger.debug("ThemeApplicator initialized with all components")

    def apply_theme_to_widget(self, widget_id: str, theme: Theme) -> bool:
        """Apply theme to specific widget.

        Args:
            widget_id: Widget ID in registry
            theme: Theme to apply

        Returns:
            True if successfully applied

        """
        start_time = time.time()

        try:
            # Adapt theme for current platform
            adapted_theme = self._platform_adapter.adapt_theme_for_platform(theme)

            # Apply theme to widget
            success = self._widget_applicator.apply_theme_by_id(widget_id, adapted_theme)

            # Update statistics
            with self._lock:
                if success:
                    self._stats.widgets_themed += 1
                else:
                    self._stats.errors += 1
                self._stats.total_time += time.time() - start_time

            return success

        except Exception as e:
            logger.error(f"Error applying theme to widget {widget_id}: {e}")
            with self._lock:
                self._stats.errors += 1
            return False

    def apply_theme_globally(self, theme: Theme) -> Dict[str, bool]:
        """Apply theme to all registered widgets and application.

        Args:
            theme: Theme to apply globally

        Returns:
            Dictionary mapping widget ID to success status

        """
        start_time = time.time()

        try:
            # Adapt theme for current platform
            adapted_theme = self._platform_adapter.adapt_theme_for_platform(theme)

            # Apply to application first
            app_success = self._app_applicator.apply_theme(adapted_theme)

            # Apply to all widgets using batch updater
            widget_results = self._batch_updater.update_all_widgets(adapted_theme)

            # Update statistics
            with self._lock:
                self._stats.global_updates += 1
                self._stats.widgets_themed += sum(
                    1 for success in widget_results.values() if success
                )
                self._stats.errors += sum(1 for success in widget_results.values() if not success)
                if not app_success:
                    self._stats.errors += 1
                self._stats.total_time += time.time() - start_time

            logger.debug(
                f"Applied theme '{theme.name}' globally: "
                f"app={app_success}, widgets={len(widget_results)}"
            )

            return widget_results

        except Exception as e:
            logger.error(f"Error applying theme globally: {e}")
            with self._lock:
                self._stats.errors += 1
            return {}

    def apply_theme_to_application(self, theme: Theme) -> bool:
        """Apply theme at application level only.

        Args:
            theme: Theme to apply

        Returns:
            True if successfully applied

        """
        try:
            adapted_theme = self._platform_adapter.adapt_theme_for_platform(theme)
            return self._app_applicator.apply_theme(adapted_theme)

        except Exception as e:
            logger.error(f"Error applying theme to application: {e}")
            return False

    def batch_update_theme(
        self, theme: Theme, widget_ids: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """Batch update theme for specified widgets.

        Args:
            theme: Theme to apply
            widget_ids: Widget IDs to update (None for all)

        Returns:
            Dictionary mapping widget ID to success status

        """
        start_time = time.time()

        try:
            adapted_theme = self._platform_adapter.adapt_theme_for_platform(theme)

            if widget_ids is None:
                results = self._batch_updater.update_all_widgets(adapted_theme)
            else:
                results = self._batch_updater.update_widgets(widget_ids, adapted_theme)

            # Update statistics
            with self._lock:
                self._stats.batch_updates += 1
                self._stats.widgets_themed += sum(1 for success in results.values() if success)
                self._stats.errors += sum(1 for success in results.values() if not success)
                self._stats.total_time += time.time() - start_time

            return results

        except Exception as e:
            logger.error(f"Error in batch theme update: {e}")
            with self._lock:
                self._stats.errors += 1
            return {}

    def invalidate_theme_cache(self, theme_name: Optional[str] = None) -> None:
        """Invalidate theme cache.

        Args:
            theme_name: Specific theme to invalidate (None for all)

        """
        try:
            if theme_name:
                self._invalidator.invalidate_theme(theme_name)
            else:
                self._invalidator.invalidate_all()

            # Clear widget applicator cache
            self._widget_applicator.clear_cache()

            logger.debug(f"Invalidated theme cache: {theme_name or 'all'}")

        except Exception as e:
            logger.error(f"Error invalidating theme cache: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get theme application statistics.

        Returns:
            Dictionary with application statistics

        """
        with self._lock:
            return {
                "widgets_themed": self._stats.widgets_themed,
                "global_updates": self._stats.global_updates,
                "batch_updates": self._stats.batch_updates,
                "cache_hits": self._stats.cache_hits,
                "cache_misses": self._stats.cache_misses,
                "errors": self._stats.errors,
                "total_time": self._stats.total_time,
                "average_time_per_operation": (
                    self._stats.total_time / max(1, self._stats.widgets_themed + self._stats.errors)
                ),
            }

    def shutdown(self) -> None:
        """Shutdown applicator and clean up resources."""
        try:
            self._async_applicator.shutdown(wait=True)
            self.invalidate_theme_cache()  # Clear all caches
            logger.debug("ThemeApplicator shutdown completed")

        except Exception as e:
            logger.error(f"Error during applicator shutdown: {e}")


def create_theme_applicator(
    registry: Optional[ThemeWidgetRegistry] = None, max_workers: int = 4
) -> ThemeApplicator:
    """Factory function for creating theme applicator with defaults.

    Args:
        registry: Widget registry (creates default if None)
        max_workers: Maximum worker threads for async operations

    Returns:
        Configured theme applicator

    """
    registry = registry or ThemeWidgetRegistry()

    # Create all specialized applicators
    widget_applicator = WidgetThemeApplicator(registry)
    app_applicator = ApplicationThemeApplicator()
    batch_updater = BatchThemeUpdater(registry)
    invalidator = StyleInvalidator()
    async_applicator = AsyncThemeApplicator(registry, max_workers)
    platform_adapter = PlatformThemeAdapter()

    applicator = ThemeApplicator(
        registry=registry,
        widget_applicator=widget_applicator,
        app_applicator=app_applicator,
        batch_updater=batch_updater,
        invalidator=invalidator,
        async_applicator=async_applicator,
        platform_adapter=platform_adapter,
    )

    logger.debug("Created theme applicator with default configuration")
    return applicator


__all__ = [
    "ThemeApplicator",
    "WidgetThemeApplicator",
    "ApplicationThemeApplicator",
    "BatchThemeUpdater",
    "StyleInvalidator",
    "AsyncThemeApplicator",
    "PlatformThemeAdapter",
    "ApplicationStats",
    "create_theme_applicator",
]
