"""Base widget class for all VFWidgets."""

from typing import Any, Optional

from PySide6.QtCore import QEvent, Signal
from PySide6.QtWidgets import QWidget


class VFBaseWidget(QWidget):
    """Base class for all VFWidgets with common functionality."""

    # Common signals
    widget_initialized = Signal()
    widget_error = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None, **kwargs: Any) -> None:
        """Initialize the base widget.

        Args:
            parent: Parent widget
            **kwargs: Additional keyword arguments for customization
        """
        super().__init__(parent)
        self._config: dict[str, Any] = kwargs
        self._initialized: bool = False
        self._setup_widget()

    def _setup_widget(self) -> None:
        """Set up the widget. Override in subclasses."""
        self._initialized = True
        self.widget_initialized.emit()

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        return self._config.get(key, default)

    def set_config(self, key: str, value: Any) -> None:
        """Set a configuration value.

        Args:
            key: Configuration key
            value: Configuration value
        """
        self._config[key] = value

    def is_initialized(self) -> bool:
        """Check if the widget is initialized.

        Returns:
            True if initialized, False otherwise
        """
        return self._initialized

    def emit_error(self, message: str) -> None:
        """Emit an error signal.

        Args:
            message: Error message
        """
        self.widget_error.emit(message)

    def changeEvent(self, event: QEvent) -> None:
        """Handle change events for theme switching support.

        Args:
            event: The change event
        """
        super().changeEvent(event)
        if event.type() == QEvent.Type.StyleChange:
            self._on_style_changed()

    def _on_style_changed(self) -> None:
        """Handle style changes. Override in subclasses for theme support."""
        pass
