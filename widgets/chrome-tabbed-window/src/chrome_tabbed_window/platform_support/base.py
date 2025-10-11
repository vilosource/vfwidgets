"""
Base platform adapter interface for ChromeTabbedWindow.

Defines the interface for platform-specific functionality.
"""

from __future__ import annotations

from typing import Optional, Protocol

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QWidget

from .capabilities import PlatformCapabilities
from .detector import PlatformDetector


class IPlatformAdapter(Protocol):
    """
    Protocol defining the interface for platform adapters.

    Platform adapters handle platform-specific functionality like
    window management, native features, and platform quirks.
    """

    def setup_widget(self, widget: QWidget) -> None:
        """Set up the widget for the platform."""
        ...

    def can_use_frameless_mode(self) -> bool:
        """Check if frameless mode can be used."""
        ...

    def enable_frameless_mode(self, widget: QWidget) -> bool:
        """Enable frameless mode for the widget."""
        ...

    def handle_window_move(self, widget: QWidget, global_pos) -> bool:
        """Handle window move request."""
        ...

    def handle_window_resize(self, widget: QWidget, edge, global_pos) -> bool:
        """Handle window resize request."""
        ...


class BasePlatformAdapter(QObject):
    """
    Base implementation of platform adapter.

    Provides default implementations that work on most platforms.
    Platform-specific adapters can override methods as needed.
    """

    def __init__(self, capabilities: PlatformCapabilities, parent: Optional[QObject] = None):
        """Initialize the platform adapter."""
        super().__init__(parent)
        self._capabilities = capabilities

    @property
    def capabilities(self) -> PlatformCapabilities:
        """Get platform capabilities."""
        return self._capabilities

    def setup_widget(self, widget: QWidget) -> None:
        """Set up the widget for the platform."""
        # Default implementation - no special setup needed
        pass

    def can_use_frameless_mode(self) -> bool:
        """Check if frameless mode can be used."""
        return self._capabilities.can_use_window_mode

    def enable_frameless_mode(self, widget: QWidget) -> bool:
        """Enable frameless mode for the widget."""
        if not self.can_use_frameless_mode():
            return False

        # Default implementation using Qt flags
        from PySide6.QtCore import Qt

        widget.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowMinMaxButtonsHint
            | Qt.WindowType.WindowCloseButtonHint
        )
        return True

    def handle_window_move(self, widget: QWidget, global_pos) -> bool:
        """Handle window move request."""
        if not self._capabilities.supports_system_move:
            return False

        # Default implementation - move window to position
        widget.move(global_pos)
        return True

    def handle_window_resize(self, widget: QWidget, edge, global_pos) -> bool:
        """Handle window resize request."""
        if not self._capabilities.supports_system_resize:
            return False

        # Default implementation - basic resize support
        # Real implementation would handle different edges
        return False


class PlatformFactory:
    """
    Factory for creating platform adapters.

    Automatically detects the platform and creates the appropriate adapter.
    """

    _capabilities: Optional[PlatformCapabilities] = None

    @classmethod
    def get_capabilities(cls) -> PlatformCapabilities:
        """Get cached platform capabilities."""
        if cls._capabilities is None:
            cls._capabilities = PlatformDetector.detect()
        return cls._capabilities

    @classmethod
    def create(cls, parent: Optional[QObject] = None) -> BasePlatformAdapter:
        """
        Create a platform adapter for the current platform.

        Returns the most appropriate adapter for the current platform.
        """
        capabilities = cls.get_capabilities()

        # Import platform-specific adapters
        import sys

        if sys.platform == "win32":
            from .windows import WindowsPlatformAdapter

            return WindowsPlatformAdapter(capabilities, parent)
        elif sys.platform == "darwin":
            from .macos import MacOSPlatformAdapter

            return MacOSPlatformAdapter(capabilities, parent)
        elif sys.platform.startswith("linux"):
            from .linux import LinuxPlatformAdapter

            return LinuxPlatformAdapter(capabilities, parent)
        else:
            # Fallback to base adapter for unknown platforms
            return BasePlatformAdapter(capabilities, parent)

    @classmethod
    def reset_detection(cls) -> None:
        """Reset platform detection cache."""
        cls._capabilities = None
