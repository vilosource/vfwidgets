"""
Linux platform adapter for ChromeTabbedWindow.

Provides Linux-specific features including X11/Wayland support,
desktop environment integration, and compositor detection.
"""

from __future__ import annotations

import os
from typing import Optional

from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import QWidget

from ..core import WindowMode
from .base import BasePlatformAdapter
from .capabilities import PlatformCapabilities


class LinuxPlatformAdapter(BasePlatformAdapter):
    """
    Linux-specific platform adapter.

    Features:
    - X11/Wayland detection and adaptation
    - Desktop environment detection (GNOME, KDE, etc.)
    - Compositor support
    - Client-side decorations
    - EWMH hints support
    """

    def __init__(self, capabilities: PlatformCapabilities, parent: Optional[QObject] = None):
        """Initialize Linux platform adapter."""
        super().__init__(capabilities, parent)

        # Detect display server
        self.is_wayland = "WAYLAND_DISPLAY" in os.environ
        self.is_x11 = "DISPLAY" in os.environ and not self.is_wayland

        # Detect desktop environment
        self.desktop_env = self._detect_desktop_environment()

        # Detect compositor
        self.has_compositor = self._detect_compositor()

    def setup_widget(self, widget: QWidget) -> None:
        """Apply Linux-specific setup."""
        super().setup_widget(widget)

        if self.is_wayland:
            self._setup_wayland_features(widget)
        elif self.is_x11:
            self._setup_x11_features(widget)

        # Setup desktop environment specific features
        self._setup_desktop_environment_features(widget)

    def _detect_desktop_environment(self) -> str:
        """Detect the current desktop environment."""
        # Check common desktop environment variables
        desktop_vars = ["XDG_CURRENT_DESKTOP", "DESKTOP_SESSION", "GDMSESSION"]

        for var in desktop_vars:
            if var in os.environ:
                env = os.environ[var].lower()
                if "gnome" in env:
                    return "gnome"
                elif "kde" in env or "plasma" in env:
                    return "kde"
                elif "xfce" in env:
                    return "xfce"
                elif "mate" in env:
                    return "mate"
                elif "cinnamon" in env:
                    return "cinnamon"
                elif "lxde" in env:
                    return "lxde"
                elif "lxqt" in env:
                    return "lxqt"

        # Fallback detection
        if os.path.exists("/usr/bin/gnome-shell"):
            return "gnome"
        elif os.path.exists("/usr/bin/kwin"):
            return "kde"

        return "unknown"

    def _detect_compositor(self) -> bool:
        """Detect if a compositor is running."""
        if self.is_wayland:
            # Wayland always has compositing
            return True

        if self.is_x11:
            # Check for common X11 compositors
            compositors = ["COMPIZ_CONFIG_PROFILE", "KWIN_COMPOSE", "_COMPIZ_WM_WINDOW_OPACITY"]

            for comp in compositors:
                if comp in os.environ:
                    return True

            # Check if a compositor process is running
            try:
                import subprocess

                result = subprocess.run(
                    ["pgrep", "-f", "compiz|compton|picom|kwin"], capture_output=True
                )
                return result.returncode == 0
            except Exception:
                pass

        return False

    def _setup_wayland_features(self, widget: QWidget) -> None:
        """Setup Wayland-specific features."""
        # Wayland limitations and features
        if hasattr(widget, "_window_mode") and widget._window_mode == WindowMode.Frameless:
            # Wayland has limited window positioning control
            # Client-side decorations are preferred
            self._enable_client_side_decorations(widget)

    def _setup_x11_features(self, widget: QWidget) -> None:
        """Setup X11-specific features."""
        if hasattr(widget, "_window_mode") and widget._window_mode == WindowMode.Frameless:
            # Set EWMH hints for better window manager integration
            self._set_ewmh_hints(widget)

            # Enable window shadows if compositor is available
            if self.has_compositor:
                self._enable_compositor_effects(widget)

    def _setup_desktop_environment_features(self, widget: QWidget) -> None:
        """Setup desktop environment specific features."""
        if self.desktop_env == "gnome":
            self._setup_gnome_features(widget)
        elif self.desktop_env == "kde":
            self._setup_kde_features(widget)

    def _enable_client_side_decorations(self, widget: QWidget) -> bool:
        """Enable client-side decorations for Wayland."""
        try:
            # Set window properties for client-side decorations
            window = widget.windowHandle()
            if window:
                window.setProperty("_GTK_THEME_VARIANT", "dark")
                return True
        except Exception:
            pass
        return False

    def _set_ewmh_hints(self, widget: QWidget) -> bool:
        """Set Extended Window Manager Hints for X11."""
        if not self.is_x11:
            return False

        try:
            # Set window type hints
            window = widget.windowHandle()
            if window and hasattr(window, "setProperty"):
                # Set window type to normal
                window.setProperty("_NET_WM_WINDOW_TYPE", "_NET_WM_WINDOW_TYPE_NORMAL")

                # Set window state hints
                window.setProperty("_NET_WM_STATE", "_NET_WM_STATE_ABOVE")

                return True
        except Exception:
            pass
        return False

    def _enable_compositor_effects(self, widget: QWidget) -> bool:
        """Enable compositor effects like shadows."""
        if not self.has_compositor:
            return False

        try:
            window = widget.windowHandle()
            if window and hasattr(window, "setProperty"):
                # Enable shadow
                window.setProperty("_COMPTON_SHADOW", 1)
                window.setProperty("_KDE_NET_WM_SHADOW", 1)
                return True
        except Exception:
            pass
        return False

    def _setup_gnome_features(self, widget: QWidget) -> None:
        """Setup GNOME-specific features."""
        # GNOME Shell integration
        try:
            window = widget.windowHandle()
            if window and hasattr(window, "setProperty"):
                # Use GNOME's client-side decorations
                window.setProperty("_GTK_CSD", 1)
        except Exception:
            pass

    def _setup_kde_features(self, widget: QWidget) -> None:
        """Setup KDE Plasma-specific features."""
        # KDE Plasma integration
        try:
            window = widget.windowHandle()
            if window and hasattr(window, "setProperty"):
                # Use KDE's window decorations
                window.setProperty("_KDE_NET_WM_WINDOW_TYPE_OVERRIDE", 1)
        except Exception:
            pass

    def enable_frameless_mode(self, widget: QWidget) -> bool:
        """Enable frameless mode with Linux-specific enhancements."""
        if not super().enable_frameless_mode(widget):
            return False

        # Apply Linux-specific frameless enhancements
        if self.is_wayland:
            self._enable_client_side_decorations(widget)
        elif self.is_x11:
            self._set_ewmh_hints(widget)
            if self.has_compositor:
                self._enable_compositor_effects(widget)

        return True

    def handle_window_resize(self, widget: QWidget, edge, global_pos) -> bool:
        """Handle window resize with Linux-specific optimizations."""
        if self.is_wayland:
            # Wayland has limited resize support
            # Try Qt's built-in methods
            if hasattr(widget.windowHandle(), "startSystemResize"):
                try:
                    edge_map = {
                        "left": Qt.Edge.LeftEdge,
                        "right": Qt.Edge.RightEdge,
                        "top": Qt.Edge.TopEdge,
                        "bottom": Qt.Edge.BottomEdge,
                    }

                    qt_edges = 0
                    for e in edge:
                        if e in edge_map:
                            qt_edges |= edge_map[e]

                    if qt_edges:
                        widget.windowHandle().startSystemResize(qt_edges)
                        return True
                except Exception:
                    pass

        return super().handle_window_resize(widget, edge, global_pos)

    def can_use_native_menu_bar(self) -> bool:
        """Check if native Linux menu bar can be used."""
        # Global menu support varies by desktop environment
        return self.desktop_env in ["gnome", "kde"]

    def supports_global_menu(self) -> bool:
        """Check if global menu is supported."""
        return (
            self.desktop_env == "kde"
            or "UBUNTU_MENUPROXY" in os.environ
            or "APPMENU_DISPLAY_BOTH" in os.environ
        )

    def get_theme_name(self) -> str:
        """Get the current system theme name."""
        try:
            if self.desktop_env == "gnome":
                import subprocess

                result = subprocess.run(
                    ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
                    capture_output=True,
                    text=True,
                )
                return result.stdout.strip().strip("'")

            elif self.desktop_env == "kde":
                # Read KDE theme from config
                kde_config = os.path.expanduser("~/.config/kdeglobals")
                if os.path.exists(kde_config):
                    # Parse KDE config for theme
                    pass

        except Exception:
            pass

        return "default"

    def is_dark_theme(self) -> bool:
        """Check if the system is using a dark theme."""
        try:
            if self.desktop_env == "gnome":
                import subprocess

                result = subprocess.run(
                    ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
                    capture_output=True,
                    text=True,
                )
                theme = result.stdout.strip().lower()
                return "dark" in theme

        except Exception:
            pass

        return False
