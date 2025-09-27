"""Foundation types for MultiSplit widget.

Pure Python types with no Qt dependencies.
All types are JSON-serializable and immutable where appropriate.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import NewType, Optional

# Type aliases
PaneId = NewType('PaneId', str)
NodeId = NewType('NodeId', str)
WidgetId = NewType('WidgetId', str)


class Orientation(str, Enum):
    """Split orientation."""
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class WherePosition(str, Enum):
    """Positions for pane placement operations."""
    REPLACE = "replace"
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"
    BEFORE = "before"  # Insert before target (same parent)
    AFTER = "after"    # Insert after target (same parent)

    def to_orientation(self) -> Optional[Orientation]:
        """Convert position to split orientation."""
        if self in (WherePosition.LEFT, WherePosition.RIGHT):
            return Orientation.HORIZONTAL
        elif self in (WherePosition.TOP, WherePosition.BOTTOM):
            return Orientation.VERTICAL
        return None  # REPLACE, BEFORE, AFTER have no orientation


class Direction(str, Enum):
    """Cardinal directions for focus navigation."""
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"

    def to_where_position(self) -> WherePosition:
        """Convert direction to where position for splits."""
        return WherePosition(self.value)


# Custom exceptions
class PaneError(Exception):
    """Base exception for pane operations."""
    pass


class PaneNotFoundError(PaneError):
    """Raised when a pane ID is not found in the tree."""
    def __init__(self, pane_id: PaneId):
        self.pane_id = pane_id
        super().__init__(f"Pane not found: {pane_id}")


class InvalidStructureError(PaneError):
    """Raised when tree structure is invalid."""
    pass


class InvalidRatioError(PaneError):
    """Raised when split ratios are invalid."""
    def __init__(self, ratios: list[float], message: str = ""):
        self.ratios = ratios
        msg = f"Invalid ratios: {ratios}"
        if message:
            msg += f" - {message}"
        super().__init__(msg)


class WidgetProviderError(PaneError):
    """Raised when widget provider fails."""
    def __init__(self, widget_id: str, message: str = ""):
        self.widget_id = widget_id
        msg = f"Widget provider failed for: {widget_id}"
        if message:
            msg += f" - {message}"
        super().__init__(msg)


class CommandExecutionError(PaneError):
    """Raised when a command fails to execute."""
    pass





@dataclass(frozen=True)
class Size:
    """Immutable size representation."""
    width: int
    height: int

    def __post_init__(self):
        if self.width < 0 or self.height < 0:
            raise ValueError(f"Size dimensions must be non-negative: {self.width}x{self.height}")


@dataclass(frozen=True)
class Position:
    """Immutable position representation."""
    x: int
    y: int


@dataclass(frozen=True)
class Rect:
    """Immutable rectangle representation."""
    position: Position
    size: Size

    @property
    def x(self) -> int:
        return self.position.x

    @property
    def y(self) -> int:
        return self.position.y

    @property
    def width(self) -> int:
        return self.size.width

    @property
    def height(self) -> int:
        return self.size.height


@dataclass(frozen=True)
class SizeConstraints:
    """Size constraints for panes."""
    min_width: int = 50
    min_height: int = 50
    max_width: Optional[int] = None
    max_height: Optional[int] = None

    def __post_init__(self):
        """Validate constraints."""
        if self.min_width < 0 or self.min_height < 0:
            raise ValueError("Minimum sizes must be non-negative")
        if self.max_width and self.max_width < self.min_width:
            raise ValueError("Max width must be >= min width")
        if self.max_height and self.max_height < self.min_height:
            raise ValueError("Max height must be >= min height")

    def clamp_size(self, width: int, height: int) -> tuple[int, int]:
        """Clamp size to constraints."""
        w = max(self.min_width, width)
        h = max(self.min_height, height)
        if self.max_width:
            w = min(self.max_width, w)
        if self.max_height:
            h = min(self.max_height, h)
        return w, h


@dataclass(frozen=True)
class Bounds:
    """Immutable bounds representation for geometry calculations."""
    x: int
    y: int
    width: int
    height: int

    def __post_init__(self):
        """Validate bounds values."""
        if self.width < 0 or self.height < 0:
            raise ValueError(f"Bounds dimensions must be non-negative: {self.width}x{self.height}")

    @property
    def right(self) -> int:
        """Get right edge coordinate."""
        return self.x + self.width

    @property
    def bottom(self) -> int:
        """Get bottom edge coordinate."""
        return self.y + self.height

    def contains_point(self, x: int, y: int) -> bool:
        """Check if point is within bounds.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            True if point is inside bounds
        """
        return (self.x <= x < self.right and
                self.y <= y < self.bottom)

    def intersects(self, other: Bounds) -> bool:
        """Check if bounds intersect with another.

        Args:
            other: Other bounds to check

        Returns:
            True if bounds overlap
        """
        return not (self.right <= other.x or
                   other.right <= self.x or
                   self.bottom <= other.y or
                   other.bottom <= self.y)
