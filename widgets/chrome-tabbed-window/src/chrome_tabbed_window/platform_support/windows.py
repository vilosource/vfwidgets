"""
Windows platform adapter for ChromeTabbedWindow.

Provides Windows-specific features and optimizations including DWM shadow support,
Aero snap handling, and native window management.
"""

from __future__ import annotations

import sys
from typing import Optional

from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import QWidget

from ..core import WindowMode
from .base import BasePlatformAdapter
from .capabilities import PlatformCapabilities


class WindowsPlatformAdapter(BasePlatformAdapter):
    """
    Windows-specific platform adapter.

    Features:
    - DWM shadow support for frameless windows
    - Aero snap zone detection
    - Windows 11 rounded corners
    - High DPI handling
    """

    def __init__(self, capabilities: PlatformCapabilities, parent: Optional[QObject] = None):
        """Initialize Windows platform adapter."""
        super().__init__(capabilities, parent)

        # Windows-specific state
        self._dwm_shadow_enabled = False
        self._snap_zones_enabled = False

    def setup_widget(self, widget: QWidget) -> None:
        """Apply Windows-specific setup."""
        super().setup_widget(widget)

        # Enable DWM shadow for frameless windows
        if hasattr(widget, '_window_mode') and widget._window_mode == WindowMode.Frameless:
            self._enable_dwm_shadow(widget)

        # Setup Windows 11 rounded corners if available
        self._setup_rounded_corners(widget)

        # Enable high DPI support
        self._setup_high_dpi(widget)

    def _enable_dwm_shadow(self, widget: QWidget) -> bool:
        """Enable DWM shadow for better visual integration."""
        if not sys.platform == 'win32':
            return False

        try:
            import ctypes

            # Get window handle
            hwnd = widget.winId()
            if not hwnd:
                return False

            # Enable shadow by extending frame into client area
            MARGINS = ctypes.c_int * 4
            margins = MARGINS(1, 1, 1, 1)  # 1px on all sides

            # Call DwmExtendFrameIntoClientArea
            result = ctypes.windll.dwmapi.DwmExtendFrameIntoClientArea(
                int(hwnd),
                ctypes.byref(margins)
            )

            self._dwm_shadow_enabled = (result == 0)
            return self._dwm_shadow_enabled

        except Exception:
            # Graceful fallback if DWM is not available
            return False

    def _setup_rounded_corners(self, widget: QWidget) -> bool:
        """Setup Windows 11 rounded corners if available."""
        if not sys.platform == 'win32':
            return False

        try:
            import ctypes

            # Windows 11 build number check
            import platform
            windows_version = platform.version()
            build_number = int(windows_version.split('.')[-1])

            if build_number < 22000:  # Windows 11 minimum build
                return False

            # Get window handle
            hwnd = widget.winId()
            if not hwnd:
                return False

            # Set rounded corner preference
            DWM_WINDOW_CORNER_PREFERENCE = 33
            DWMWCP_ROUND = 2

            corner_preference = ctypes.c_int(DWMWCP_ROUND)
            result = ctypes.windll.dwmapi.DwmSetWindowAttribute(
                int(hwnd),
                DWM_WINDOW_CORNER_PREFERENCE,
                ctypes.byref(corner_preference),
                ctypes.sizeof(corner_preference)
            )

            return result == 0

        except Exception:
            return False

    def _setup_high_dpi(self, widget: QWidget) -> None:
        """Setup high DPI support for Windows."""
        # Qt handles most of this automatically, but we can add
        # Windows-specific enhancements here if needed
        pass

    def handle_aero_snap(self, widget: QWidget, global_pos) -> bool:
        """Handle Windows Aero Snap zones."""
        if not self._snap_zones_enabled:
            return False

        # TODO: Implement Aero snap zone detection
        # This would detect when the window is dragged to screen edges
        # and trigger the appropriate snap behavior
        return False

    def enable_frameless_mode(self, widget: QWidget) -> bool:
        """Enable frameless mode with Windows-specific enhancements."""
        if not super().enable_frameless_mode(widget):
            return False

        # Apply Windows-specific frameless enhancements
        self._enable_dwm_shadow(widget)
        self._setup_rounded_corners(widget)

        return True

    def handle_window_resize(self, widget: QWidget, edge, global_pos) -> bool:
        """Handle window resize with Windows-specific optimizations."""
        # Try to use system resize if available
        if hasattr(widget.windowHandle(), 'startSystemResize'):
            try:
                # Map edge to Qt edge constant
                edge_map = {
                    'left': Qt.Edge.LeftEdge,
                    'right': Qt.Edge.RightEdge,
                    'top': Qt.Edge.TopEdge,
                    'bottom': Qt.Edge.BottomEdge,
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
        """Check if native Windows menu bar can be used."""
        return True

    def setup_taskbar_integration(self, widget: QWidget) -> bool:
        """Setup Windows taskbar integration."""
        # TODO: Implement taskbar integration
        # - Taskbar progress
        # - Thumbnail toolbar
        # - Jump lists
        return False
