"""Utility functions for MultiSplit widget.

Pure Python utilities with no Qt dependencies.
"""

import uuid

from .types import NodeId, PaneId, WidgetId


def generate_pane_id(prefix: str = "pane") -> PaneId:
    """Generate unique pane ID that remains stable across sessions.

    Args:
        prefix: Optional prefix for the ID

    Returns:
        Unique PaneId like 'pane_a3f2b8c1'
    """
    return PaneId(f"{prefix}_{uuid.uuid4().hex[:8]}")


def generate_node_id(prefix: str = "node") -> NodeId:
    """Generate unique node ID for split nodes.

    Args:
        prefix: Optional prefix for the ID

    Returns:
        Unique NodeId like 'node_5d7e9a2f'
    """
    return NodeId(f"{prefix}_{uuid.uuid4().hex[:8]}")


def generate_widget_id(type_hint: str, identifier: str) -> WidgetId:
    """Generate widget ID from type and identifier.

    Args:
        type_hint: Widget type (e.g., 'editor', 'terminal')
        identifier: Unique identifier (e.g., 'main.py', 'session1')

    Returns:
        Formatted WidgetId like 'editor:main.py'
    """
    return WidgetId(f"{type_hint}:{identifier}")


def validate_ratio(ratio: float) -> None:
    """Validate a single ratio value."""
    from .types import InvalidRatioError
    if not 0.0 < ratio < 1.0:
        raise InvalidRatioError([ratio], "Ratio must be between 0 and 1")


def validate_ratios(ratios: list[float]) -> None:
    """Validate a list of split ratios."""
    from .types import InvalidRatioError
    if len(ratios) < 2:
        raise InvalidRatioError(ratios, "At least 2 ratios required")

    total = sum(ratios)
    if abs(total - 1.0) > 0.001:  # Allow small floating point errors
        raise InvalidRatioError(ratios, f"Ratios must sum to 1.0, got {total}")

    for ratio in ratios:
        if ratio <= 0:
            raise InvalidRatioError(ratios, f"All ratios must be positive, got {ratio}")


def validate_id_format(id_string: str, id_type: str) -> bool:
    """Validate ID format is correct for the given type.

    Args:
        id_string: ID string to validate
        id_type: Type of ID ('pane', 'node', 'widget')

    Returns:
        True if format is valid
    """
    if not id_string:
        return False

    if id_type == "widget":
        # Widget IDs must have format "type:identifier"
        parts = id_string.split(":")
        return len(parts) == 2 and all(parts)
    elif id_type in ["pane", "node"]:
        # Pane/node IDs must have format "prefix_8hexchars"
        parts = id_string.split("_")
        if len(parts) != 2:
            return False
        prefix, hex_part = parts
        return len(hex_part) == 8 and all(c in '0123456789abcdef' for c in hex_part)
    return False


def parse_widget_id(widget_id: WidgetId) -> tuple[str, str]:
    """Parse widget ID into type and identifier.

    Args:
        widget_id: Widget ID to parse

    Returns:
        Tuple of (type_hint, identifier)

    Raises:
        ValueError: If widget_id format is invalid
    """
    if not validate_id_format(str(widget_id), "widget"):
        raise ValueError(f"Invalid widget ID format: {widget_id}")

    type_hint, identifier = str(widget_id).split(":", 1)
    return type_hint, identifier
