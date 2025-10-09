"""Base platform adapter interface for ViloCodeWindow.

Defines the interface for platform-specific functionality.
"""

from __future__ import annotations

from typing import Optional, Protocol

from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import QWidget

from .capabilities import PlatformCapabilities
from .detector import PlatformDetector


class IPlatformAdapter(Protocol):
    """Protocol defining the interface for platform adapters."""

    def setup_widget(self, widget: QWidget) -> None:
        """Set up the widget for the platform."""
        ...

    def can_use_frameless_mode(self) -> bool:
        """Check if frameless mode can be used."""
        ...

    def enable_frameless_mode(self, widget: QWidget) -> bool:
        """Enable frameless mode for the widget."""
        ...


class BasePlatformAdapter(QObject):
    """Base implementation of platform adapter.

    Provides default implementations that work on most platforms.
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
        return self._capabilities.can_use_frameless_mode

    def enable_frameless_mode(self, widget: QWidget) -> bool:
        """Enable frameless mode for the widget."""
        if not self.can_use_frameless_mode():
            return False

        # Default implementation using Qt flags
        widget.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowMinMaxButtonsHint
            | Qt.WindowType.WindowCloseButtonHint
        )
        widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        return True


class PlatformFactory:
    """Factory for creating platform adapters.

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
        """Create a platform adapter for the current platform."""
        capabilities = cls.get_capabilities()

        # For now, use base adapter on all platforms
        # Platform-specific adapters can be added later
        return BasePlatformAdapter(capabilities, parent)

    @classmethod
    def reset_detection(cls) -> None:
        """Reset platform detection cache."""
        cls._capabilities = None
