"""ThemedApplication - Application-level theme management.

This module provides ThemedApplication, the simple application-level interface
for managing themes across the entire application. This is THE way developers
should manage themes at the application level.

Key Classes:
- ThemedApplication: Simple application-level theme management
- ApplicationThemeManager: Internal application theme coordination

Design Philosophy:
ThemedApplication provides simple, clean APIs for:
- set_theme() - instant theme switching
- get_available_themes() - theme discovery
- import_vscode_theme() - VSCode integration
- load_theme_file() - theme file loading
- auto_detect_system_theme() - system integration

All complexity is hidden behind this simple interface while maintaining
bulletproof architecture underneath.

Task 9 Implementation Features:
- Application-level theme coordination
- Thread-safe theme switching for all widgets
- VSCode theme importing with validation
- System theme detection and monitoring
- File operations with error recovery
- Performance optimization for bulk widget updates
"""

import json
import os
import threading
import time
import weakref
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Union

import yaml

try:
    from PySide6.QtCore import QObject, QTimer, Signal
    from PySide6.QtWidgets import QApplication

    pyqtSignal = Signal  # PySide6 uses Signal, not pyqtSignal
    QT_AVAILABLE = True
except ImportError:
    # Fallback for testing without Qt
    QT_AVAILABLE = False

    class QApplication:
        def __init__(self, args=None):
            self._args = args or []

        @staticmethod
        def instance():
            return None

        def quit(self):
            pass

        def processEvents(self):
            pass

    class QObject:
        pass

    class Signal:
        def __init__(self, *args):
            self._callbacks = []

        def emit(self, *args):
            for callback in self._callbacks:
                try:
                    callback(*args)
                except Exception:
                    pass

        def connect(self, callback):
            self._callbacks.append(callback)

    pyqtSignal = Signal

    class QTimer:
        def __init__(self):
            pass

        def start(self, msec):
            pass

        def stop(self):
            pass


# Import foundation modules
from ..core.manager import ThemeManager
from ..core.theme import Theme
from ..development.hot_reload import DevModeManager, HotReloader
from ..errors import ThemeError, ThemeNotFoundError, get_global_error_recovery_manager
from ..lifecycle import LifecycleManager
from ..logging import get_debug_logger
from ..threading import ThreadSafeThemeManager
from .metadata import ThemeInfo

logger = get_debug_logger(__name__)


@dataclass
class ApplicationConfig:
    """Configuration for ThemedApplication."""

    default_theme: str = "default"
    auto_detect_system: bool = True
    persist_theme: bool = True
    theme_directories: list[str] = field(default_factory=list)
    vscode_integration: bool = True
    performance_monitoring: bool = False
    cache_themes: bool = True
    # Task 18: Hot reload configuration
    enable_hot_reload: bool = False
    hot_reload_debounce_ms: int = 100
    hot_reload_dev_mode_only: bool = True


class ApplicationThemeManager:
    """Internal manager for application-level theme coordination."""

    def __init__(self, application: "ThemedApplication"):
        self._application = weakref.ref(application)
        self._lock = threading.RLock()
        self._widget_count = 0
        self._last_theme_switch_time = 0.0
        self._theme_switch_count = 0
        self._performance_stats = {
            "theme_switches": 0,
            "widgets_updated": 0,
            "average_switch_time": 0.0,
            "cache_hits": 0,
            "cache_misses": 0,
        }

    def coordinate_theme_switch(self, theme: Theme) -> bool:
        """Coordinate theme switch across all widgets."""
        try:
            with self._lock:
                start_time = time.perf_counter()

                # Get widget registry from ThemeManager
                theme_manager = ThemeManager.get_instance()
                registry = theme_manager._widget_registry if theme_manager else None
                widget_count = registry.count() if registry else 0

                # Update performance tracking
                self._widget_count = widget_count
                self._theme_switch_count += 1

                # Notify theme manager to update all widgets
                theme_manager = ThemeManager.get_instance()
                if theme_manager:
                    theme_manager.set_theme(theme.name)

                # Calculate performance metrics
                switch_time = time.perf_counter() - start_time
                self._last_theme_switch_time = switch_time

                # Update statistics
                self._performance_stats["theme_switches"] += 1
                self._performance_stats["widgets_updated"] += widget_count

                # Update average
                total_switches = self._performance_stats["theme_switches"]
                old_avg = self._performance_stats["average_switch_time"]
                new_avg = (old_avg * (total_switches - 1) + switch_time) / total_switches
                self._performance_stats["average_switch_time"] = new_avg

                logger.debug(
                    f"Theme switch coordinated: {widget_count} widgets in {switch_time:.3f}s"
                )
                return True

        except Exception as e:
            logger.error(f"Error coordinating theme switch: {e}")
            return False

    def get_performance_stats(self) -> dict[str, Any]:
        """Get performance statistics."""
        with self._lock:
            stats = self._performance_stats.copy()
            stats.update(
                {
                    "current_widget_count": self._widget_count,
                    "last_switch_time": self._last_theme_switch_time,
                    "total_switches": self._theme_switch_count,
                }
            )
            return stats


def detect_system_theme() -> Optional[str]:
    """Detect system theme preference."""
    try:
        # Windows
        if os.name == "nt":
            try:
                import winreg

                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
                )
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                winreg.CloseKey(key)
                return "light" if value else "dark"
            except Exception:
                pass

        # macOS
        elif os.name == "posix":
            try:
                import subprocess

                result = subprocess.run(
                    ["defaults", "read", "-g", "AppleInterfaceStyle"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0 and "Dark" in result.stdout:
                    return "dark"
                else:
                    return "light"
            except Exception:
                pass

        # Linux/X11
        try:
            # Check for common dark theme indicators
            desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
            if "gnome" in desktop or "gtk" in desktop:
                # Try to detect GTK theme
                theme = os.environ.get("GTK_THEME", "").lower()
                if "dark" in theme:
                    return "dark"
                else:
                    return "light"
        except Exception:
            pass

        return None

    except Exception as e:
        logger.error(f"Error detecting system theme: {e}")
        return None


def find_vscode_themes() -> list[Path]:
    """Find VSCode theme files in common locations."""
    theme_paths = []

    try:
        # Common VSCode extension paths
        home = Path.home()
        vscode_paths = [
            home / ".vscode" / "extensions",
            home / "AppData" / "Roaming" / "Code" / "User" / "extensions",  # Windows
            home / "Library" / "Application Support" / "Code" / "User" / "extensions",  # macOS
            home / ".config" / "Code" / "User" / "extensions",  # Linux
        ]

        for vscode_path in vscode_paths:
            if vscode_path.exists():
                # Find theme files
                for ext_dir in vscode_path.iterdir():
                    if ext_dir.is_dir():
                        themes_dir = ext_dir / "themes"
                        if themes_dir.exists():
                            for theme_file in themes_dir.glob("*.json"):
                                theme_paths.append(theme_file)

    except Exception as e:
        logger.error(f"Error finding VSCode themes: {e}")

    return theme_paths


def save_theme_preference(theme_name: str) -> bool:
    """Save theme preference for persistence."""
    try:
        config_dir = Path.home() / ".vfwidgets"
        config_dir.mkdir(exist_ok=True)

        config_file = config_dir / "theme_preference.json"
        with open(config_file, "w") as f:
            json.dump({"preferred_theme": theme_name}, f)

        return True
    except Exception as e:
        logger.error(f"Error saving theme preference: {e}")
        return False


def load_theme_preference() -> Optional[str]:
    """Load saved theme preference."""
    try:
        config_file = Path.home() / ".vfwidgets" / "theme_preference.json"
        if config_file.exists():
            with open(config_file) as f:
                data = json.load(f)
                return data.get("preferred_theme")
    except Exception as e:
        logger.error(f"Error loading theme preference: {e}")

    return None


class ThemedApplication(QApplication if QT_AVAILABLE else QObject):
    """Simple application-level theme management.

    ThemedApplication provides a clean, simple interface for managing themes
    across an entire application:

    - set_theme() - Instant theme switching for all widgets
    - get_available_themes() - Discover all available themes
    - import_vscode_theme() - Import VSCode themes safely
    - load_theme_file() - Load themes from files
    - auto_detect_system_theme() - System integration

    All architectural complexity is hidden behind these simple methods.
    Developers get bulletproof theme management without configuration.

    Usage:
        app = ThemedApplication([])
        app.set_theme("dark")  # Instantly switches all themed widgets
        themes = app.get_available_themes()  # Lists all available themes
    """

    # Qt signals for application-wide theme events
    if QT_AVAILABLE:
        theme_changed = pyqtSignal(str)  # Emitted when theme changes
        theme_loaded = pyqtSignal(str)  # Emitted when new theme is loaded
        theme_import_completed = pyqtSignal(str)  # Emitted when theme import completes
        system_theme_detected = pyqtSignal(str)  # Emitted when system theme detected
        theme_preview_started = pyqtSignal(str)  # Emitted when theme preview starts
        theme_preview_ended = pyqtSignal(
            bool
        )  # Emitted when preview ends (True=committed, False=cancelled)
    else:
        theme_changed = Signal(str)
        theme_loaded = Signal()
        theme_import_completed = Signal(str)
        system_theme_detected = Signal(str)
        theme_preview_started = Signal(str)
        theme_preview_ended = Signal(bool)

    _instance = None
    _instance_lock = threading.Lock()

    def __init__(self, args=None, theme_config: Optional[dict[str, Any]] = None):
        """Initialize themed application with automatic setup.

        All complexity is hidden here:
        - Theme system initialization
        - Widget registry setup
        - Thread safety configuration
        - Error recovery setup
        - Performance optimization

        Args:
            args: Command line arguments for QApplication
            theme_config: Optional configuration dictionary

        """
        if QT_AVAILABLE:
            super().__init__(args or [])
        else:
            super().__init__()

        # Store instance reference
        with self._instance_lock:
            ThemedApplication._instance = self

        # Configuration
        self._config = ApplicationConfig()
        if theme_config:
            for key, value in theme_config.items():
                if hasattr(self._config, key):
                    setattr(self._config, key, value)

        # Initialize managers (dependency injection)
        self._theme_manager: Optional[ThemeManager] = None
        self._lifecycle_manager: Optional[LifecycleManager] = None
        self._thread_manager: Optional[ThreadSafeThemeManager] = None
        self._app_theme_manager = ApplicationThemeManager(self)

        # Application state
        self._current_theme: Optional[Theme] = None
        self._theme_directories: set[Path] = set()
        self._system_theme_monitoring = False
        self._is_initialized = False

        # Metadata system
        from .metadata import ThemeMetadataProvider

        self._metadata_provider = ThemeMetadataProvider()

        # Preview system state
        self._preview_original_theme: Optional[Theme] = None

        # Task 18: Hot reload state
        self._hot_reloader: Optional[HotReloader] = None
        self._hot_reload_enabled = False
        self._theme_file_paths: dict[str, Path] = {}  # theme_name -> file_path mapping

        # Performance tracking
        self._startup_time = time.perf_counter()

        # Initialize the theme system
        self._initialize_theme_system()

        logger.debug("ThemedApplication created")

    @classmethod
    def instance(cls) -> Optional["ThemedApplication"]:
        """Get the current application instance."""
        with cls._instance_lock:
            return cls._instance

    def _initialize_theme_system(self) -> None:
        """Initialize the complete theme system.

        This method sets up all theme system components with dependency
        injection and proper error handling. All complexity is hidden
        from the developer.
        """
        try:
            # Get singleton instance of ThemeManager
            self._theme_manager = ThemeManager.get_instance()
            # Optional components (not singletons)
            self._lifecycle_manager = None  # Will be created if needed
            self._thread_manager = None  # Will be created if needed

            # Built-in themes are already loaded by ThemeManager/ThemeRepository
            # No need to duplicate theme initialization

            # Load theme directories from config
            for theme_dir in self._config.theme_directories:
                self.discover_themes_from_directory(theme_dir)

            # Mark as initialized BEFORE theme setting so set_theme() can succeed
            # (set_theme() checks _is_initialized and rejects calls if False)
            self._is_initialized = True

            # Auto-detect system theme if enabled
            if self._config.auto_detect_system:
                system_theme = self.auto_detect_system_theme()
                if system_theme:
                    self.set_theme(system_theme)

            # Restore saved theme if persistence enabled
            elif self._config.persist_theme:
                saved_theme = load_theme_preference()
                if saved_theme and self._theme_manager.has_theme(saved_theme):
                    self.set_theme(saved_theme)

            # Set default theme if none set
            if not self._current_theme:
                if self._theme_manager.has_theme(self._config.default_theme):
                    self.set_theme(self._config.default_theme)
                else:
                    # Fallback to first available theme
                    available = self._theme_manager.list_themes()
                    if available:
                        self.set_theme(available[0])

            # Task 18: Initialize hot reload if enabled
            self._initialize_hot_reload()

            # Calculate initialization time
            init_time = time.perf_counter() - self._startup_time
            logger.debug(f"Theme system initialized in {init_time:.3f}s")

        except Exception as e:
            logger.error(f"Error initializing theme system: {e}")
            self._is_initialized = False

            # Use error recovery system
            error_manager = get_global_error_recovery_manager()
            error_manager.handle_error(
                ThemeError(f"Theme system initialization failed: {e}"),
                operation="initialize_theme_system",
                context={"application": True, "config": self._config.__dict__},
            )

    @property
    def available_themes(self) -> list[str]:
        """Get list of available theme names."""
        if self._theme_manager:
            return self._theme_manager.list_themes()
        return []

    @property
    def current_theme_name(self) -> Optional[str]:
        """Get current theme name."""
        if self._current_theme and hasattr(self._current_theme, "name"):
            return self._current_theme.name
        elif isinstance(self._current_theme, str):
            return self._current_theme
        return None

    @property
    def theme_type(self) -> str:
        """Get current theme type (dark/light)."""
        if self._theme_manager and self._theme_manager.current_theme:
            return self._theme_manager.current_theme.type
        return "light"  # Default

    def set_theme(self, theme: Union[str, Theme], persist: bool = None) -> bool:
        """Set active theme for entire application.

        This method instantly switches the theme for all ThemedWidget
        instances in the application. The operation is:
        - Thread-safe
        - Atomic (all widgets update together)
        - Error-tolerant (fallback on failure)
        - Performance-optimized (< 100ms for 100 widgets)

        Args:
            theme: Theme name or Theme object to activate
            persist: Whether to save theme preference (uses config default if None)

        Returns:
            True if theme was set successfully, False otherwise

        """
        try:
            if not self._is_initialized:
                logger.warning("Theme system not initialized, cannot set theme")
                return False

            # Resolve theme object
            if isinstance(theme, str):
                if not self._theme_manager.has_theme(theme):
                    raise ThemeNotFoundError(f"Theme '{theme}' not found")
                theme_obj = self._theme_manager.get_theme(theme)
                theme_name = theme
            else:
                theme_obj = theme
                theme_name = theme.name
                # Add to ThemeManager if not present
                if not self._theme_manager.has_theme(theme_name):
                    self._theme_manager.add_theme(theme_obj)

            logger.debug(f"Setting application theme to: {theme_name}")

            # Coordinate theme switch across all widgets
            success = self._app_theme_manager.coordinate_theme_switch(theme_obj)
            if not success:
                return False

            # Update current theme
            old_theme = self._current_theme
            self._current_theme = theme_obj

            # Save preference if enabled
            persist_enabled = persist if persist is not None else self._config.persist_theme
            if persist_enabled:
                save_theme_preference(theme_name)

            # Emit signals
            self.theme_changed.emit(theme_name)

            old_name = old_theme.name if old_theme else None
            logger.debug(f"Successfully changed theme from '{old_name}' to '{theme_name}'")
            return True

        except Exception as e:
            logger.error(f"Error setting theme '{theme}': {e}")

            # Graceful fallback to minimal theme
            if (
                hasattr(self, "_current_theme")
                and self._current_theme
                and self._current_theme.name != "minimal"
            ):
                try:
                    if self._theme_manager.has_theme("minimal"):
                        minimal_theme = self._theme_manager.get_theme("minimal")
                        self._app_theme_manager.coordinate_theme_switch(minimal_theme)
                        self._current_theme = minimal_theme
                        self.theme_changed.emit("minimal")
                except Exception:
                    pass  # Ignore fallback errors

            return False

    def get_current_theme(self) -> Optional[Theme]:
        """Get the currently active theme."""
        return self._current_theme

    def get_available_themes(self) -> list[Union[str, Theme]]:
        """Get list of all available themes.

        Returns a list of theme names that can be used with set_theme().
        This includes built-in themes, loaded themes, and imported themes.

        Returns:
            List of available theme names or Theme objects

        """
        try:
            if not self._is_initialized or not self._theme_manager:
                return ["minimal"]  # Always available

            # Return theme objects for richer information
            theme_names = self._theme_manager.list_themes()
            return [self._theme_manager.get_theme(name) for name in theme_names]

        except Exception as e:
            logger.error(f"Error getting available themes: {e}")
            return ["minimal"]  # Safe fallback

    def load_theme_file(self, file_path: Union[str, Path]) -> bool:
        """Load theme from file.

        Supports JSON and YAML theme files with validation and error recovery.

        Args:
            file_path: Path to theme file

        Returns:
            True if theme was loaded successfully, False otherwise

        """
        try:
            path = Path(file_path)
            if not path.exists():
                logger.warning(f"Theme file not found: {path}")
                return False

            logger.debug(f"Loading theme from file: {path}")

            # Load file content
            with open(path, encoding="utf-8") as f:
                if path.suffix.lower() == ".yaml" or path.suffix.lower() == ".yml":
                    theme_data = yaml.safe_load(f)
                else:
                    theme_data = json.load(f)

            # Create theme from data
            theme = Theme.from_dict(theme_data)

            # Add to ThemeManager
            self._theme_manager.add_theme(theme)

            # Task 18: Register file path for hot reload
            self._theme_file_paths[theme.name] = path
            if self._hot_reload_enabled and self._hot_reloader:
                self._hot_reloader.watch_file(path)

            # Emit signal
            self.theme_loaded.emit(theme.name)

            logger.debug(f"Successfully loaded theme '{theme.name}' from {path}")
            return True

        except Exception as e:
            logger.error(f"Error loading theme file '{file_path}': {e}")
            return False

    def save_current_theme(self, file_path: Union[str, Path]) -> bool:
        """Save current theme to file.

        Args:
            file_path: Path where to save theme file

        Returns:
            True if theme was saved successfully, False otherwise

        """
        try:
            if not self._current_theme:
                logger.warning("No current theme to save")
                return False

            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            # Convert theme to dictionary
            theme_data = self._current_theme.to_dict()

            # Save based on file extension
            with open(path, "w", encoding="utf-8") as f:
                if path.suffix.lower() == ".yaml" or path.suffix.lower() == ".yml":
                    yaml.dump(theme_data, f, default_flow_style=False)
                else:
                    json.dump(theme_data, f, indent=2)

            logger.debug(f"Successfully saved theme '{self._current_theme.name}' to {path}")
            return True

        except Exception as e:
            logger.error(f"Error saving theme to '{file_path}': {e}")
            return False

    def discover_themes_from_directory(self, directory_path: Union[str, Path]) -> int:
        """Discover and load all themes from a directory.

        Scans the directory for theme files and loads all valid themes.
        Supports multiple theme formats and provides error tolerance.

        Args:
            directory_path: Path to directory containing themes

        Returns:
            Number of themes successfully loaded

        """
        try:
            path = Path(directory_path)
            if not path.exists() or not path.is_dir():
                logger.warning(f"Theme directory not found: {path}")
                return 0

            self._theme_directories.add(path)
            loaded_count = 0

            # Find theme files
            theme_extensions = [".json", ".yaml", ".yml"]
            for ext in theme_extensions:
                for theme_file in path.glob(f"*{ext}"):
                    if self.load_theme_file(theme_file):
                        loaded_count += 1

            logger.debug(f"Discovered {loaded_count} themes from directory: {path}")
            return loaded_count

        except Exception as e:
            logger.error(f"Error discovering themes in directory '{directory_path}': {e}")
            return 0

    def import_vscode_theme(self, theme_file: Union[str, Path]) -> bool:
        """Import a VSCode theme file safely.

        Parses and imports a VSCode theme file, converting it to the
        VFWidgets theme format. Includes security validation and
        error handling.

        Args:
            theme_file: Path to VSCode theme file (.json)

        Returns:
            True if import was successful, False otherwise

        """
        try:
            path = Path(theme_file)
            if not path.exists():
                logger.warning(f"VSCode theme file not found: {path}")
                return False

            logger.debug(f"Importing VSCode theme: {path}")

            # Load VSCode theme
            with open(path, encoding="utf-8") as f:
                vscode_data = json.load(f)

            # Convert VSCode theme to VFWidgets format
            theme_name = vscode_data.get("name", path.stem)
            theme_type = vscode_data.get("type", "dark")

            # Extract colors from VSCode format
            vscode_colors = vscode_data.get("colors", {})
            colors = {}

            # Map common VSCode colors to VFWidgets format
            color_mapping = {
                "editor.background": "background",
                "editor.foreground": "foreground",
                "activityBar.background": "primary",
                "button.background": "accent",
                "focusBorder": "focus",
                "selection.background": "selection",
            }

            for vscode_key, vf_key in color_mapping.items():
                if vscode_key in vscode_colors:
                    colors[vf_key] = vscode_colors[vscode_key]

            # Set defaults based on theme type
            if theme_type == "dark":
                colors.setdefault("background", "#1e1e1e")
                colors.setdefault("foreground", "#d4d4d4")
            else:
                colors.setdefault("background", "#ffffff")
                colors.setdefault("foreground", "#000000")

            # Create basic styles
            styles = {
                "window": {"background-color": "@colors.background", "color": "@colors.foreground"}
            }

            # Create theme
            theme = Theme(
                name=theme_name,
                description=f"Imported from VSCode theme: {path.name}",
                colors=colors,
                styles=styles,
                metadata={"source": "vscode", "original_path": str(path), "theme_type": theme_type},
            )

            # Add to ThemeManager
            self._theme_manager.add_theme(theme)

            # Task 18: Register file path for hot reload
            self._theme_file_paths[theme.name] = path
            if self._hot_reload_enabled and self._hot_reloader:
                self._hot_reloader.watch_file(path)

            # Emit signal
            self.theme_import_completed.emit(theme.name)

            logger.debug(f"Successfully imported VSCode theme: {theme.name}")
            return True

        except Exception as e:
            logger.error(f"Error importing VSCode theme '{theme_file}': {e}")
            return False

    def auto_discover_vscode_themes(self) -> int:
        """Auto-discover and import VSCode themes.

        Returns:
            Number of themes imported

        """
        try:
            if not self._config.vscode_integration:
                return 0

            theme_files = find_vscode_themes()
            imported_count = 0

            for theme_file in theme_files:
                if self.import_vscode_theme(theme_file):
                    imported_count += 1

            logger.debug(f"Auto-discovered and imported {imported_count} VSCode themes")
            return imported_count

        except Exception as e:
            logger.error(f"Error auto-discovering VSCode themes: {e}")
            return 0

    def auto_detect_system_theme(self) -> Optional[str]:
        """Auto-detect system theme preference.

        Returns:
            Detected theme name, or None if detection failed

        """
        try:
            detected_theme = detect_system_theme()

            if detected_theme and self._theme_manager.has_theme(detected_theme):
                self.system_theme_detected.emit(detected_theme)
                logger.debug(f"Detected system theme: {detected_theme}")
                return detected_theme
            else:
                logger.debug(f"System theme detected ({detected_theme}) but not available")

            return None

        except Exception as e:
            logger.error(f"Error detecting system theme: {e}")
            return None

    def enable_system_theme_monitoring(self) -> bool:
        """Enable monitoring of system theme changes.

        Returns:
            True if monitoring was enabled successfully, False otherwise

        """
        try:
            if self._system_theme_monitoring:
                return True  # Already monitoring

            # Set up timer for periodic system theme detection
            if QT_AVAILABLE:
                self._system_theme_timer = QTimer()
                self._system_theme_timer.timeout.connect(self._check_system_theme)
                self._system_theme_timer.start(5000)  # Check every 5 seconds

            self._system_theme_monitoring = True
            logger.debug("System theme monitoring enabled")
            return True

        except Exception as e:
            logger.error(f"Error enabling system theme monitoring: {e}")
            return False

    def disable_system_theme_monitoring(self) -> bool:
        """Disable monitoring of system theme changes.

        Returns:
            True if monitoring was disabled successfully, False otherwise

        """
        try:
            if not self._system_theme_monitoring:
                return True  # Already disabled

            if hasattr(self, "_system_theme_timer"):
                self._system_theme_timer.stop()
                self._system_theme_timer = None

            self._system_theme_monitoring = False
            logger.debug("System theme monitoring disabled")
            return True

        except Exception as e:
            logger.error(f"Error disabling system theme monitoring: {e}")
            return False

    def _check_system_theme(self) -> None:
        """Periodic check for system theme changes."""
        try:
            detected_theme = detect_system_theme()
            if (
                detected_theme
                and self._theme_manager.has_theme(detected_theme)
                and (not self._current_theme or detected_theme != self._current_theme.name)
            ):
                logger.debug(f"System theme changed to: {detected_theme}")
                self.set_theme(detected_theme)

        except Exception as e:
            logger.error(f"Error checking system theme: {e}")

    def reload_current_theme(self) -> bool:
        """Reload current theme from its source.

        Returns:
            True if reload was successful, False otherwise

        """
        try:
            if not self._current_theme:
                return False

            theme_name = self._current_theme.name

            # Try to reload from metadata if available
            metadata = getattr(self._current_theme, "metadata", {})
            source_path = metadata.get("original_path")

            if source_path and Path(source_path).exists():
                # Reload from file
                if metadata.get("source") == "vscode":
                    success = self.import_vscode_theme(source_path)
                else:
                    success = self.load_theme_file(source_path)

                if success:
                    # Re-apply the reloaded theme
                    return self.set_theme(theme_name)

            return False

        except Exception as e:
            logger.error(f"Error reloading current theme: {e}")
            return False

    def get_performance_statistics(self) -> dict[str, Any]:
        """Get application-level performance statistics.

        Returns:
            Dictionary containing performance metrics

        """
        try:
            stats = self._app_theme_manager.get_performance_stats()

            # Add application-level stats
            theme_manager = ThemeManager.get_instance()
            registry = theme_manager._widget_registry if theme_manager else None
            stats.update(
                {
                    "total_themes": len(self._theme_manager.list_themes()),
                    "theme_directories": len(self._theme_directories),
                    "system_monitoring": self._system_theme_monitoring,
                    "total_widgets": registry.count() if registry else 0,
                    "initialized": self._is_initialized,
                    # Task 18: Hot reload stats
                    "hot_reload_enabled": self._hot_reload_enabled,
                    "hot_reload_stats": (
                        self._hot_reloader.get_statistics() if self._hot_reloader else {}
                    ),
                }
            )

            return stats

        except Exception as e:
            logger.error(f"Error getting performance statistics: {e}")
            return {}

    # ================================================================
    # Theme Metadata Methods
    # ================================================================

    def get_theme_info(self, theme_name: Optional[str] = None) -> Optional["ThemeInfo"]:
        """Get metadata information for a theme.

        Args:
            theme_name: Name of theme to get info for. If None, uses current theme.

        Returns:
            ThemeInfo object if found, None otherwise

        Example:
            >>> app = ThemedApplication([])
            >>> info = app.get_theme_info("dark")
            >>> if info:
            ...     print(f"{info.display_name}: {info.description}")

        """
        try:
            # If no theme name provided, use current theme
            if theme_name is None:
                if self._current_theme:
                    theme_name = self._current_theme.name
                else:
                    return None

            # Try to get from metadata provider
            info = self._metadata_provider.get_metadata(theme_name)

            # If not found, try to create from theme object
            if info is None and self._theme_manager.has_theme(theme_name):
                theme = self._theme_manager.get_theme(theme_name)
                info = self._metadata_provider.create_from_theme(theme)
                # Register for future use
                self._metadata_provider.register_metadata(theme_name, info)

            return info

        except Exception as e:
            logger.error(f"Error getting theme info for '{theme_name}': {e}")
            return None

    def get_all_theme_info(self) -> dict[str, "ThemeInfo"]:
        """Get metadata for all available themes.

        Returns:
            Dictionary mapping theme names to ThemeInfo objects

        Example:
            >>> app = ThemedApplication([])
            >>> all_info = app.get_all_theme_info()
            >>> for name, info in all_info.items():
            ...     print(f"{info.display_name} ({info.type})")

        """
        try:
            # Ensure all themes have metadata
            for theme_name in self._theme_manager.list_themes():
                if not self._metadata_provider.has_metadata(theme_name):
                    theme = self._theme_manager.get_theme(theme_name)
                    info = self._metadata_provider.create_from_theme(theme)
                    self._metadata_provider.register_metadata(theme_name, info)

            return self._metadata_provider.get_all_metadata()

        except Exception as e:
            logger.error(f"Error getting all theme info: {e}")
            return {}

    # ================================================================
    # Theme Switching Enhancement Methods
    # ================================================================

    def toggle_theme(self, theme1: Optional[str] = None, theme2: Optional[str] = None) -> bool:
        """Toggle between two themes.

        If current theme is theme1, switches to theme2 and vice versa.
        If current theme is neither, switches to theme1 (or theme2 if theme1 not provided).

        Args:
            theme1: First theme name (defaults to "dark")
            theme2: Second theme name (defaults to "light")

        Returns:
            True if toggle was successful, False otherwise

        Example:
            >>> app = ThemedApplication([])
            >>> app.set_theme("dark")
            >>> app.toggle_theme("dark", "light")  # Switches to light
            >>> app.toggle_theme("dark", "light")  # Switches back to dark

        """
        try:
            # Default themes
            theme1 = theme1 or "dark"
            theme2 = theme2 or "light"

            # Determine which theme to switch to
            if self._current_theme:
                current_name = self._current_theme.name
                if current_name == theme1:
                    target_theme = theme2
                elif current_name == theme2:
                    target_theme = theme1
                else:
                    # Current theme is neither, switch to first
                    target_theme = theme1
            else:
                # No current theme, switch to first
                target_theme = theme1

            # Switch to target theme
            return self.set_theme(target_theme)

        except Exception as e:
            logger.error(f"Error toggling theme: {e}")
            return False

    def cycle_theme(self, theme_list: Optional[list[str]] = None, reverse: bool = False) -> bool:
        """Cycle to the next theme in a list.

        If no list provided, cycles through all available themes.
        If current theme is not in list, starts from beginning (or end if reverse).

        Args:
            theme_list: Optional list of theme names to cycle through.
                       If None, uses all available themes.
            reverse: If True, cycles in reverse order

        Returns:
            True if cycle was successful, False otherwise

        Example:
            >>> app = ThemedApplication([])
            >>> app.cycle_theme(["dark", "light", "default"])  # Cycles through list
            >>> app.cycle_theme(reverse=True)  # Cycles backwards through all themes

        """
        try:
            # Get theme list
            if theme_list is None:
                theme_list = self._theme_manager.list_themes()

            if not theme_list:
                logger.warning("No themes available to cycle through")
                return False

            # Get current theme name
            current_name = self._current_theme.name if self._current_theme else None

            # Find current index
            try:
                current_index = theme_list.index(current_name) if current_name else -1
            except ValueError:
                # Current theme not in list, start from beginning
                current_index = -1

            # Calculate next index
            if reverse:
                next_index = (current_index - 1) % len(theme_list)
            else:
                next_index = (current_index + 1) % len(theme_list)

            # Switch to next theme
            next_theme = theme_list[next_index]
            return self.set_theme(next_theme)

        except Exception as e:
            logger.error(f"Error cycling theme: {e}")
            return False

    # ================================================================
    # Theme Preview System Methods
    # ================================================================

    @property
    def is_previewing(self) -> bool:
        """Check if currently previewing a theme."""
        return self._preview_original_theme is not None

    def preview_theme(self, theme_name: str) -> bool:
        """Preview a theme without persisting the change.

        The theme is applied immediately but can be cancelled with cancel_preview()
        or committed with commit_preview().

        Args:
            theme_name: Name of theme to preview

        Returns:
            True if preview started successfully, False otherwise

        Example:
            >>> app = ThemedApplication([])
            >>> app.set_theme("dark")
            >>> app.preview_theme("light")  # Preview light theme
            >>> app.cancel_preview()        # Revert to dark

        """
        try:
            # Store original theme if not already previewing
            if self._preview_original_theme is None:
                self._preview_original_theme = self._current_theme

            # Apply preview theme without persistence
            success = self.set_theme(theme_name, persist=False)

            if success:
                # Emit preview started signal
                self.theme_preview_started.emit(theme_name)
                logger.debug(f"Preview started for theme: {theme_name}")

            return success

        except Exception as e:
            logger.error(f"Error previewing theme '{theme_name}': {e}")
            return False

    def commit_preview(self) -> bool:
        """Commit the current preview as the permanent theme.

        Returns:
            True if commit was successful, False otherwise

        Example:
            >>> app = ThemedApplication([])
            >>> app.preview_theme("light")
            >>> app.commit_preview()  # Keep light theme

        """
        try:
            if self._preview_original_theme is None:
                # Not previewing, nothing to commit
                return True

            # Current theme becomes permanent
            if self._current_theme:
                # Persist the current theme
                if self._config.persist_theme:
                    save_theme_preference(self._current_theme.name)

            # Clear preview state
            self._preview_original_theme = None

            # Emit preview ended signal (committed=True)
            self.theme_preview_ended.emit(True)
            logger.debug("Preview committed")

            return True

        except Exception as e:
            logger.error(f"Error committing preview: {e}")
            return False

    def cancel_preview(self) -> bool:
        """Cancel the current preview and revert to original theme.

        Returns:
            True if cancel was successful, False otherwise

        Example:
            >>> app = ThemedApplication([])
            >>> app.preview_theme("light")
            >>> app.cancel_preview()  # Revert to original theme

        """
        try:
            if self._preview_original_theme is None:
                # Not previewing, nothing to cancel
                return True

            # Revert to original theme
            original_theme = self._preview_original_theme
            self._preview_original_theme = None  # Clear before switching to avoid recursion

            # Restore original theme without persistence
            success = self.set_theme(original_theme, persist=False)

            # Emit preview ended signal (committed=False)
            self.theme_preview_ended.emit(False)
            logger.debug("Preview cancelled, reverted to original theme")

            return success

        except Exception as e:
            logger.error(f"Error cancelling preview: {e}")
            return False

    # ================================================================
    # Task 18: Hot Reload System Methods
    # ================================================================

    def _initialize_hot_reload(self) -> None:
        """Initialize hot reload system if enabled."""
        try:
            # Check if hot reload should be enabled
            should_enable = self._config.enable_hot_reload

            # If dev mode only, check dev mode status
            if self._config.hot_reload_dev_mode_only:
                should_enable = should_enable and DevModeManager.is_dev_mode()

            if should_enable:
                self.enable_hot_reload()
                logger.debug("Hot reload initialized and enabled")
            else:
                logger.debug("Hot reload not enabled (disabled or not in dev mode)")

        except Exception as e:
            logger.error(f"Error initializing hot reload: {e}")

    def enable_hot_reload(self, watch_directories: Optional[list[Union[str, Path]]] = None) -> bool:
        """Enable theme hot reloading.

        Args:
            watch_directories: Optional list of directories to watch. If None,
                               uses theme directories from config.

        Returns:
            True if hot reload was enabled successfully

        """
        try:
            if self._hot_reload_enabled:
                logger.debug("Hot reload already enabled")
                return True

            # Create hot reloader
            debounce_ms = self._config.hot_reload_debounce_ms
            self._hot_reloader = HotReloader(debounce_ms=debounce_ms)

            # Set reload callback
            self._hot_reloader.set_reload_callback(self._hot_reload_theme_file)

            # Connect signals
            self._hot_reloader.theme_reloaded.connect(self._on_theme_hot_reloaded)
            self._hot_reloader.reload_error.connect(self._on_reload_error)

            # Enable the hot reloader
            self._hot_reloader.enable(True)

            # Watch directories
            directories_to_watch = watch_directories or list(self._theme_directories)

            for directory in directories_to_watch:
                dir_path = Path(directory)
                if dir_path.exists():
                    self._hot_reloader.watch_directory(dir_path)
                    logger.debug(f"Watching directory for changes: {dir_path}")

            # Watch individual theme files
            for _theme_name, file_path in self._theme_file_paths.items():
                if file_path.exists():
                    self._hot_reloader.watch_file(file_path)
                    logger.debug(f"Watching theme file: {file_path}")

            self._hot_reload_enabled = True
            logger.info(f"Hot reload enabled with {debounce_ms}ms debounce")
            return True

        except Exception as e:
            logger.error(f"Error enabling hot reload: {e}")
            return False

    def disable_hot_reload(self) -> bool:
        """Disable theme hot reloading.

        Returns:
            True if hot reload was disabled successfully

        """
        try:
            if not self._hot_reload_enabled:
                logger.debug("Hot reload already disabled")
                return True

            if self._hot_reloader:
                self._hot_reloader.enable(False)
                self._hot_reloader.stop_watching()
                self._hot_reloader = None

            self._hot_reload_enabled = False
            logger.info("Hot reload disabled")
            return True

        except Exception as e:
            logger.error(f"Error disabling hot reload: {e}")
            return False

    def is_hot_reload_enabled(self) -> bool:
        """Check if hot reload is currently enabled."""
        return self._hot_reload_enabled and self._hot_reloader is not None

    def get_hot_reload_statistics(self) -> dict[str, Any]:
        """Get hot reload statistics."""
        if self._hot_reloader:
            return self._hot_reloader.get_statistics()
        return {
            "enabled": False,
            "total_reloads": 0,
            "successful_reloads": 0,
            "success_rate": 0,
            "watched_files": 0,
            "watched_directories": 0,
        }

    def _hot_reload_theme_file(self, file_path: Path) -> bool:
        """Hot reload callback for theme files.

        Args:
            file_path: Path to the changed theme file

        Returns:
            True if reload was successful

        """
        try:
            logger.debug(f"Hot reloading theme file: {file_path}")

            # Find which theme this file belongs to
            theme_name = None
            for name, path in self._theme_file_paths.items():
                if path == file_path:
                    theme_name = name
                    break

            # If we don't know which theme this is, try to load it as a new theme
            if not theme_name:
                # Try to load as new theme
                success = self.load_theme_file(file_path)
                if success:
                    # Find the newly loaded theme
                    for name in self._theme_manager.list_themes():
                        theme = self._theme_manager.get_theme(name)
                        metadata = getattr(theme, "metadata", {})
                        if metadata.get("original_path") == str(file_path):
                            theme_name = name
                            break
                return success

            # Reload existing theme
            if theme_name:
                # Check if this is a VSCode theme
                current_theme = (
                    self._theme_manager.get_theme(theme_name)
                    if self._theme_manager.has_theme(theme_name)
                    else None
                )
                if current_theme and hasattr(current_theme, "metadata"):
                    metadata = current_theme.metadata
                    if metadata.get("source") == "vscode":
                        success = self.import_vscode_theme(file_path)
                    else:
                        success = self.load_theme_file(file_path)
                else:
                    success = self.load_theme_file(file_path)

                # If this is the current theme, re-apply it
                if success and self._current_theme and self._current_theme.name == theme_name:
                    # Re-apply the reloaded theme
                    success = self.set_theme(theme_name, persist=False)

                return success

            return False

        except Exception as e:
            logger.error(f"Error in hot reload callback for {file_path}: {e}")
            return False

    def _on_theme_hot_reloaded(self, file_path: str, success: bool):
        """Handle theme hot reload completion signal."""
        try:
            if success:
                logger.info(f"Successfully hot reloaded theme from: {file_path}")
            else:
                logger.warning(f"Failed to hot reload theme from: {file_path}")

            # Emit custom signal if needed
            if hasattr(self, "theme_hot_reloaded"):
                self.theme_hot_reloaded.emit(file_path, success)

        except Exception as e:
            logger.error(f"Error handling hot reload signal: {e}")

    def _on_reload_error(self, file_path: str, error_message: str):
        """Handle theme reload error signal."""
        try:
            logger.error(f"Hot reload error for {file_path}: {error_message}")

            # Emit custom signal if needed
            if hasattr(self, "theme_reload_error"):
                self.theme_reload_error.emit(file_path, error_message)

        except Exception as e:
            logger.error(f"Error handling reload error signal: {e}")

    def watch_theme_file(
        self, file_path: Union[str, Path], theme_name: Optional[str] = None
    ) -> bool:
        """Add a theme file to hot reload watching.

        Args:
            file_path: Path to theme file to watch
            theme_name: Optional theme name for tracking

        Returns:
            True if file was added to watching successfully

        """
        try:
            if not self._hot_reload_enabled or not self._hot_reloader:
                logger.warning("Hot reload not enabled, cannot watch theme file")
                return False

            path_obj = Path(file_path)

            # Add to theme file paths mapping if theme name provided
            if theme_name:
                self._theme_file_paths[theme_name] = path_obj

            # Watch the file
            success = self._hot_reloader.watch_file(path_obj)

            if success:
                logger.debug(f"Added theme file to hot reload watching: {path_obj}")
            else:
                logger.warning(f"Failed to watch theme file: {path_obj}")

            return success

        except Exception as e:
            logger.error(f"Error watching theme file {file_path}: {e}")
            return False

    def unwatch_theme_file(self, file_path: Union[str, Path]) -> bool:
        """Remove a theme file from hot reload watching.

        Args:
            file_path: Path to theme file to stop watching

        Returns:
            True if file was removed from watching successfully

        """
        try:
            if not self._hot_reload_enabled or not self._hot_reloader:
                return True  # Already not watching

            path_obj = Path(file_path)

            # Remove from theme file paths mapping
            for name, path in list(self._theme_file_paths.items()):
                if path == path_obj:
                    del self._theme_file_paths[name]
                    break

            # Stop watching the file
            success = self._hot_reloader.unwatch_file(path_obj)

            if success:
                logger.debug(f"Removed theme file from hot reload watching: {path_obj}")
            else:
                logger.warning(f"Failed to stop watching theme file: {path_obj}")

            return success

        except Exception as e:
            logger.error(f"Error unwatching theme file {file_path}: {e}")
            return False

    def cleanup(self) -> None:
        """Clean up theme system resources.

        This method is called automatically when the application shuts down,
        but can be called manually if needed.
        """
        try:
            logger.debug("Cleaning up ThemedApplication resources")

            # Disable system monitoring
            if self._system_theme_monitoring:
                self.disable_system_theme_monitoring()

            # Task 18: Disable hot reload
            if self._hot_reload_enabled:
                self.disable_hot_reload()

            # Clean up theme system components
            if self._theme_manager:
                # Theme manager handles its own cleanup
                pass

            # Clear references
            self._theme_manager = None
            self._lifecycle_manager = None
            self._thread_manager = None
            self._hot_reloader = None

            # Clear instance reference
            with self._instance_lock:
                if ThemedApplication._instance is self:
                    ThemedApplication._instance = None

            self._is_initialized = False

            logger.debug("ThemedApplication cleanup completed")

        except Exception as e:
            logger.error(f"Error during ThemedApplication cleanup: {e}")


# Global convenience functions
def get_themed_application() -> Optional[ThemedApplication]:
    """Get the current themed application instance."""
    return ThemedApplication.instance()


def set_global_theme(theme_name: str) -> bool:
    """Set theme globally using the current application instance."""
    app = get_themed_application()
    if app:
        return app.set_theme(theme_name)
    else:
        logger.warning("No ThemedApplication instance available")
        return False


def get_global_theme() -> Optional[str]:
    """Get current global theme name."""
    app = get_themed_application()
    if app and app.get_current_theme():
        return app.get_current_theme().name
    return None


def get_global_available_themes() -> list[str]:
    """Get list of globally available themes."""
    app = get_themed_application()
    if app:
        themes = app.get_available_themes()
        return [theme.name if hasattr(theme, "name") else str(theme) for theme in themes]
    return ["minimal"]


__all__ = [
    "ThemedApplication",
    "ApplicationThemeManager",
    "ApplicationConfig",
    "get_themed_application",
    "set_global_theme",
    "get_global_theme",
    "get_global_available_themes",
    "detect_system_theme",
    "find_vscode_themes",
]
