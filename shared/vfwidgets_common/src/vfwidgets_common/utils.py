"""Utility functions for VFWidgets."""

from pathlib import Path
from typing import Optional, Union

from PySide6.QtCore import QFile, QTextStream
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget


def setup_widget_style(
    widget: QWidget,
    style_file: Optional[Union[str, Path]] = None,
    style_string: Optional[str] = None,
) -> None:
    """Apply styles to a widget.

    Args:
        widget: Widget to style
        style_file: Path to QSS stylesheet file
        style_string: Direct stylesheet string

    Raises:
        ValueError: If neither style_file nor style_string is provided
        FileNotFoundError: If style_file doesn't exist
    """
    if style_string:
        widget.setStyleSheet(style_string)
    elif style_file:
        style_path = Path(style_file)
        if not style_path.exists():
            raise FileNotFoundError(f"Style file not found: {style_file}")

        qss_file = QFile(str(style_path))
        if qss_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            stream = QTextStream(qss_file)
            widget.setStyleSheet(stream.readAll())
            qss_file.close()
    else:
        raise ValueError("Either style_file or style_string must be provided")


def load_widget_icon(
    icon_path: Union[str, Path],
    fallback: Optional[Union[str, Path]] = None,
) -> QIcon:
    """Load an icon for a widget.

    Args:
        icon_path: Path to the icon file
        fallback: Optional fallback icon path

    Returns:
        QIcon object

    Raises:
        FileNotFoundError: If neither icon_path nor fallback exists
    """
    icon = QIcon()

    icon_file = Path(icon_path)
    if icon_file.exists():
        icon = QIcon(str(icon_file))
    elif fallback:
        fallback_file = Path(fallback)
        if fallback_file.exists():
            icon = QIcon(str(fallback_file))
        else:
            raise FileNotFoundError(f"Neither {icon_path} nor {fallback} found")
    else:
        raise FileNotFoundError(f"Icon file not found: {icon_path}")

    return icon


def get_widget_resource_path(
    widget_module: str,
    resource_name: str,
    resource_type: str = "icons",
) -> Path:
    """Get the path to a widget resource.

    Args:
        widget_module: Name of the widget module (e.g., 'vfwidgets_button')
        resource_name: Name of the resource file
        resource_type: Type of resource ('icons', 'styles', etc.)

    Returns:
        Path to the resource

    Raises:
        FileNotFoundError: If resource doesn't exist
    """
    import importlib.resources

    try:
        if hasattr(importlib.resources, "files"):
            # Python 3.9+
            resource_path = (
                importlib.resources.files(widget_module)
                / "resources"
                / resource_type
                / resource_name
            )
        else:
            # Fallback for older Python
            import pkg_resources

            resource_path = Path(
                pkg_resources.resource_filename(
                    widget_module, f"resources/{resource_type}/{resource_name}"
                )
            )

        if not resource_path.exists():
            raise FileNotFoundError(f"Resource not found: {resource_path}")

        return resource_path
    except Exception as e:
        raise FileNotFoundError(f"Could not load resource {resource_name}: {e}") from e


def ensure_widget_size(
    widget: QWidget,
    min_width: Optional[int] = None,
    min_height: Optional[int] = None,
    max_width: Optional[int] = None,
    max_height: Optional[int] = None,
) -> None:
    """Set size constraints for a widget.

    Args:
        widget: Widget to constrain
        min_width: Minimum width
        min_height: Minimum height
        max_width: Maximum width
        max_height: Maximum height
    """
    if min_width is not None:
        widget.setMinimumWidth(min_width)
    if min_height is not None:
        widget.setMinimumHeight(min_height)
    if max_width is not None:
        widget.setMaximumWidth(max_width)
    if max_height is not None:
        widget.setMaximumHeight(max_height)
