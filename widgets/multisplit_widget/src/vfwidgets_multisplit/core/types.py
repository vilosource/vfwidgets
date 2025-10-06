"""Foundation types for MultiSplit widget.

Pure Python types with no Qt dependencies.
All types are JSON-serializable and immutable where appropriate.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import NewType

# Type aliases
PaneId = NewType("PaneId", str)
NodeId = NewType("NodeId", str)
WidgetId = NewType("WidgetId", str)


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
    AFTER = "after"  # Insert after target (same parent)

    def to_orientation(self) -> Orientation | None:
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
    max_width: int | None = None
    max_height: int | None = None

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
        return self.x <= x < self.right and self.y <= y < self.bottom

    def intersects(self, other: Bounds) -> bool:
        """Check if bounds intersect with another.

        Args:
            other: Other bounds to check

        Returns:
            True if bounds overlap
        """
        return not (
            self.right <= other.x
            or other.right <= self.x
            or self.bottom <= other.y
            or other.bottom <= self.y
        )


@dataclass(frozen=True)
class SplitterStyle:
    """Configuration for splitter appearance.

    This dataclass controls the visual styling of split pane dividers.
    All settings are optional with sensible defaults for comfortable use.

    Preset Styles:
        - minimal(): 1px handles, no margins (terminal emulators)
        - compact(): 3px handles, 1px margins (compact layouts)
        - comfortable(): 6px handles, 2px margins (default, easy to grab)

    Example - Minimal style:
        >>> style = SplitterStyle.minimal()
        >>> multisplit = MultisplitWidget(provider=provider, splitter_style=style)

    Example - Custom colors:
        >>> style = SplitterStyle(
        ...     handle_width=2,
        ...     handle_bg="#1e1e1e",
        ...     handle_hover_bg="#007acc"
        ... )
    """

    # Dimensions
    handle_width: int = 6
    """Width of splitter handle in pixels (default: 6)."""

    handle_margin_horizontal: int = 2
    """Top/bottom margin for horizontal handles in pixels (default: 2)."""

    handle_margin_vertical: int = 2
    """Left/right margin for vertical handles in pixels (default: 2)."""

    hit_area_padding: int = 0
    """Extra invisible padding on each side for easier grabbing (default: 0).

    This expands the interactive area without changing visual appearance.
    Useful for minimal 1px dividers to provide comfortable hit targets.
    Total hit area width = handle_width + (2 * hit_area_padding)
    """

    # Colors (optional - defaults to theme if None)
    handle_bg: str | None = None
    """Background color for handle (default: uses theme 'widget.background')."""

    handle_hover_bg: str | None = None
    """Hover background color (default: uses theme 'list.hoverBackground')."""

    handle_border: str | None = None
    """Border color (default: transparent)."""

    handle_hover_border: str | None = None
    """Border color on hover (default: uses theme 'widget.border' if show_hover_effect)."""

    # Border styles
    border_width: int = 1
    """Border width in pixels (default: 1)."""

    border_radius: int = 0
    """Corner radius for handle in pixels (default: 0, square corners)."""

    # Hover behavior
    show_hover_effect: bool = True
    """Enable/disable hover highlighting (default: True)."""

    cursor_on_hover: bool = True
    """Change cursor to resize arrows on hover (default: True)."""

    def __post_init__(self):
        """Validate splitter style values."""
        if self.handle_width < 0:
            raise ValueError(f"handle_width must be non-negative: {self.handle_width}")
        if self.handle_margin_horizontal < 0:
            raise ValueError(
                f"handle_margin_horizontal must be non-negative: {self.handle_margin_horizontal}"
            )
        if self.handle_margin_vertical < 0:
            raise ValueError(
                f"handle_margin_vertical must be non-negative: {self.handle_margin_vertical}"
            )
        if self.hit_area_padding < 0:
            raise ValueError(f"hit_area_padding must be non-negative: {self.hit_area_padding}")
        if self.border_width < 0:
            raise ValueError(f"border_width must be non-negative: {self.border_width}")
        if self.border_radius < 0:
            raise ValueError(f"border_radius must be non-negative: {self.border_radius}")

    @classmethod
    def minimal(cls) -> SplitterStyle:
        """Minimal style for terminal emulators.

        Returns 1px handles with no margins for a clean, minimal appearance.
        Ideal for terminal emulators and applications where space is critical.

        Visual width: 1px (very thin divider line)
        Hit area: 7px (1px + 3px padding on each side for easy grabbing)

        Returns:
            SplitterStyle with minimal dimensions but comfortable hit area
        """
        return cls(
            handle_width=1,
            handle_margin_horizontal=0,
            handle_margin_vertical=0,
            border_width=0,
            hit_area_padding=3,  # 3px padding on each side = 7px total hit area
        )

    @classmethod
    def compact(cls) -> SplitterStyle:
        """Compact style for space-efficient layouts.

        Returns 3px handles with 1px margins for a compact appearance
        while still being easy to grab.

        Total visual width: 5px (3px + 1px margin each side)

        Returns:
            SplitterStyle with compact dimensions
        """
        return cls(
            handle_width=3, handle_margin_horizontal=1, handle_margin_vertical=1, border_width=1
        )

    @classmethod
    def comfortable(cls) -> SplitterStyle:
        """Comfortable style - current default.

        Returns 6px handles with 2px margins for comfortable grabbing.
        This is the default style used when no style is specified.

        Total visual width: 10px (6px + 2px margin each side)

        Returns:
            SplitterStyle with comfortable dimensions
        """
        return cls(
            handle_width=6, handle_margin_horizontal=2, handle_margin_vertical=2, border_width=1
        )


__all__ = [
    # Type aliases
    "PaneId",
    "NodeId",
    "WidgetId",
    # Enums
    "Orientation",
    "WherePosition",
    "Direction",
    # Exceptions
    "PaneError",
    "PaneNotFoundError",
    "InvalidStructureError",
    "InvalidRatioError",
    "WidgetProviderError",
    "CommandExecutionError",
    # Data classes
    "Size",
    "Position",
    "Rect",
    "SizeConstraints",
    "Bounds",
    "SplitterStyle",
]
