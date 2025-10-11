"""Bridge between abstract model signals and Qt signals.

This module provides the connection between pure Python
signals in the Model layer and Qt signals in the View layer.
"""

from typing import Any, Protocol

from ..core.signals import AbstractSignal


class QtSignalProtocol(Protocol):
    """Protocol for Qt signals (without importing Qt)."""

    def emit(self, *args) -> None:
        """Emit the Qt signal."""
        ...

    def connect(self, slot: Any) -> None:
        """Connect to Qt signal."""
        ...

    def disconnect(self, slot: Any) -> None:
        """Disconnect from Qt signal."""
        ...


class SignalBridge:
    """Bridges abstract signals to Qt signals without Qt dependency in Model."""

    def __init__(self):
        """Initialize bridge with empty connections."""
        self._bridges: list[tuple[AbstractSignal, QtSignalProtocol, Any]] = []

    def bridge_to_qt(self, abstract_signal: AbstractSignal, qt_signal: QtSignalProtocol) -> None:
        """Create bridge from abstract signal to Qt signal.

        Args:
            abstract_signal: Source signal from Model
            qt_signal: Target Qt signal in View
        """

        # Create relay function
        def relay(*args, **kwargs):
            # Qt signals typically don't use kwargs
            qt_signal.emit(*args)

        # Connect abstract signal to relay
        abstract_signal.connect(relay)

        # Store bridge info for cleanup
        self._bridges.append((abstract_signal, qt_signal, relay))

    def bridge_from_qt(self, qt_signal: QtSignalProtocol, abstract_signal: AbstractSignal) -> None:
        """Create bridge from Qt signal to abstract signal.

        Args:
            qt_signal: Source Qt signal from View
            abstract_signal: Target signal in Model
        """

        # Create relay function
        def relay(*args):
            abstract_signal.emit(*args)

        # Connect Qt signal to relay
        qt_signal.connect(relay)

        # Store bridge info for cleanup
        self._bridges.append((abstract_signal, qt_signal, relay))

    def cleanup(self) -> None:
        """Remove all signal bridges."""
        for bridge in self._bridges:
            if len(bridge) == 3:
                source, target, relay = bridge
                try:
                    # Try to disconnect
                    if hasattr(source, "disconnect"):
                        source.disconnect(relay)
                    if hasattr(target, "disconnect"):
                        target.disconnect(relay)
                except:
                    pass  # Ignore disconnect errors during cleanup

        self._bridges.clear()
