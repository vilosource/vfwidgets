"""
macOS platform adapter for ChromeTabbedWindow.

Provides macOS-specific features including traffic light positioning,
native window controls, and Cocoa integration.
"""

from __future__ import annotations

import sys
from typing import Optional

from PySide6.QtCore import QObject, Qt
from PySide6.QtGui import QWindow
from PySide6.QtWidgets import QWidget

from ..core import WindowMode
from .base import BasePlatformAdapter
from .capabilities import PlatformCapabilities


class MacOSPlatformAdapter(BasePlatformAdapter):
    """
    macOS-specific platform adapter.

    Features:
    - Native traffic light positioning
    - macOS window management
    - Retina display support
    - Mission Control integration
    - Native menu bar support
    """

    def __init__(self, capabilities: PlatformCapabilities, parent: Optional[QObject] = None):
        """Initialize macOS platform adapter."""
        super().__init__(capabilities, parent)

        # macOS-specific state
        self._traffic_lights_positioned = False
        self._native_title_bar_hidden = False

    def setup_widget(self, widget: QWidget) -> None:
        """Apply macOS-specific setup."""
        super().setup_widget(widget)

        # Setup traffic lights for frameless windows
        if hasattr(widget, "_window_mode") and widget._window_mode == WindowMode.Frameless:
            self._setup_traffic_lights(widget)

        # Enable native fullscreen support
        self._enable_native_fullscreen(widget)

        # Setup Retina display support
        self._setup_retina_support(widget)

    def _setup_traffic_lights(self, widget: QWidget) -> bool:
        """Setup native macOS traffic light buttons."""
        if sys.platform != "darwin":
            return False

        try:
            # Get the window handle
            window = widget.windowHandle()
            if not window:
                return False

            # Use Cocoa to position traffic lights
            # This requires the window to be created first
            if not window.winId():
                return False

            # Try to access the native window
            self._position_traffic_lights(window)
            self._traffic_lights_positioned = True
            return True

        except Exception:
            return False

    def _position_traffic_lights(self, window: QWindow) -> None:
        """Position traffic light buttons using Cocoa."""
        try:
            # This would typically use PyObjC to access Cocoa APIs
            # For now, we'll use Qt's built-in macOS integration

            # Hide the default title bar but keep the window controls
            if hasattr(window, "setProperty"):
                window.setProperty("_q_macOSCustomizeWindow", True)

        except Exception:
            pass

    def _enable_native_fullscreen(self, widget: QWidget) -> bool:
        """Enable native macOS fullscreen support."""
        if sys.platform != "darwin":
            return False

        try:
            window = widget.windowHandle()
            if window and hasattr(window, "setProperty"):
                # Enable native fullscreen
                window.setProperty("_q_macOSFullScreen", True)
                return True
        except Exception:
            pass

        return False

    def _setup_retina_support(self, widget: QWidget) -> None:
        """Setup Retina display support."""
        # Qt handles most Retina support automatically
        # Additional macOS-specific enhancements can go here
        pass

    def enable_frameless_mode(self, widget: QWidget) -> bool:
        """Enable frameless mode with macOS-specific enhancements."""
        if not super().enable_frameless_mode(widget):
            return False

        # Apply macOS-specific frameless enhancements
        self._setup_traffic_lights(widget)
        self._hide_title_bar_but_keep_controls(widget)

        return True

    def _hide_title_bar_but_keep_controls(self, widget: QWidget) -> bool:
        """Hide title bar but keep traffic light controls."""
        try:
            window = widget.windowHandle()
            if window:
                # Use macOS-specific window flags
                flags = window.flags()
                flags |= Qt.WindowType.FramelessWindowHint

                # Keep window controls visible
                if hasattr(window, "setProperty"):
                    window.setProperty("_q_macOSHideTitleBar", True)
                    window.setProperty("_q_macOSKeepControls", True)

                window.setFlags(flags)
                self._native_title_bar_hidden = True
                return True

        except Exception:
            pass

        return False

    def handle_window_move(self, widget: QWidget, global_pos) -> bool:
        """Handle window move with macOS optimizations."""
        # macOS has built-in window move support
        # Use the native implementation when possible
        return super().handle_window_move(widget, global_pos)

    def handle_window_resize(self, widget: QWidget, edge, global_pos) -> bool:
        """Handle window resize with macOS optimizations."""
        # Try native resize first
        if hasattr(widget.windowHandle(), "startSystemResize"):
            try:
                # Map edge to Qt edge constant
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
        """Check if native macOS menu bar can be used."""
        return True

    def setup_dock_integration(self, widget: QWidget) -> bool:
        """Setup macOS Dock integration."""
        # TODO: Implement Dock integration
        # - Dock menu
        # - Badge support
        # - Progress indicators
        return False

    def setup_mission_control_integration(self, widget: QWidget) -> bool:
        """Setup Mission Control integration."""
        # TODO: Implement Mission Control integration
        # - Window grouping
        # - Expose support
        return False

    def get_traffic_light_position(self) -> tuple:
        """Get the position where traffic lights should be placed."""
        # Standard macOS traffic light position
        return (20, 20)  # x, y from top-left

    def is_dark_mode(self) -> bool:
        """Check if macOS is in dark mode."""
        try:
            import subprocess

            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"], capture_output=True, text=True
            )

            return result.stdout.strip() == "Dark"
        except Exception:
            return False
