# Frameless Window Behavior Guide

This guide explains how to use `FramelessWindowBehavior` to add custom window frame functionality to your Qt widgets.

## Overview

`FramelessWindowBehavior` is a composition-based utility class that encapsulates all the logic needed for frameless window management:

- **Window dragging** via native `QWindow.startSystemMove()` API
- **Edge resizing** via native `QWindow.startSystemResize()` API
- **Cursor management** for resize edges (auto-updates cursor shape)
- **Fallback implementations** for older Qt versions or platforms without native support
- **Flexible draggable areas** via widget reference or custom callback

## Why Use FramelessWindowBehavior?

### Before (Code Duplication)

Prior to `FramelessWindowBehavior`, each widget implementing frameless windows had ~150 lines of duplicate code for:

- Edge detection logic
- Cursor shape updates
- Mouse event handling
- Manual window dragging/resizing

This led to:
- **Bug duplication**: Fixes needed in multiple places
- **Maintenance burden**: Changes required updating multiple widgets
- **Inconsistent behavior**: Subtle differences between implementations

### After (Shared Behavior)

With `FramelessWindowBehavior`:
- **Single source of truth**: One implementation, multiple users
- **Tested once, works everywhere**: Comprehensive test suite (21 tests)
- **Consistent behavior**: All widgets use identical logic
- **Easy to use**: 4-line integration per mouse event

## Architecture

### Composition Pattern

`FramelessWindowBehavior` uses **composition** rather than inheritance:

```python
class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        # Compose, don't inherit
        self._frameless_behavior = FramelessWindowBehavior(...)
```

**Benefits:**
- No multiple inheritance conflicts
- Works with any widget hierarchy
- Optional - only use when needed
- Easy to test in isolation

### API Design

The behavior provides a simple event delegation API:

```python
def mousePressEvent(self, event):
    # Delegate to behavior, returns True if handled
    if self._frameless_behavior.handle_press(self, event):
        return  # Behavior handled it
    super().mousePressEvent(event)  # Pass to parent
```

## Usage Patterns

### Pattern 1: Simple Draggable Title Bar

Use when you have a dedicated title bar widget:

```python
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from vfwidgets_common import FramelessWindowBehavior

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Create title bar
        self.title_bar = QLabel("My Application")
        self.title_bar.setFixedHeight(30)

        # Setup behavior - only title_bar is draggable
        self._frameless_behavior = FramelessWindowBehavior(
            draggable_widget=self.title_bar,
            resize_margin=5,
        )

        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.title_bar)
        layout.addWidget(QLabel("Content area (not draggable)"))

    def mousePressEvent(self, event):
        if self._frameless_behavior.handle_press(self, event):
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._frameless_behavior.handle_move(self, event):
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._frameless_behavior.handle_release(self, event):
            return
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if self._frameless_behavior.handle_double_click(self, event):
            return
        super().mouseDoubleClickEvent(event)
```

### Pattern 2: Custom Draggable Area Callback

Use when draggable area logic is complex (e.g., only empty tab bar areas):

```python
class MyTabbedWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self.tab_bar = QTabBar()

        # Custom callback for complex logic
        def is_draggable_area(widget: QWidget, pos: QPoint) -> bool:
            """Only empty tab bar areas are draggable, not tabs themselves."""
            # Map position to tab bar coordinates
            tab_bar_rect = self.tab_bar.rect()
            tab_bar_pos = self.tab_bar.mapTo(self, tab_bar_rect.topLeft())
            tab_bar_global_rect = QRect(tab_bar_pos, tab_bar_rect.size())

            if tab_bar_global_rect.contains(pos):
                local_pos = self.tab_bar.mapFrom(self, pos)
                tab_index = self.tab_bar.tabAt(local_pos)

                # Empty area = draggable, tab = not draggable
                return tab_index < 0 or tab_index >= self.tab_bar.count()

            return False

        self._frameless_behavior = FramelessWindowBehavior(
            draggable_widget=None,  # Use callback instead
            is_draggable_area=is_draggable_area,
            resize_margin=4,
        )

    # Mouse event handlers same as Pattern 1...
```

### Pattern 3: Conditional Behavior (Mode Switching)

Use when widget supports both frameless and embedded modes:

```python
class MyWindow(QWidget):
    def __init__(self, mode="frameless"):
        super().__init__()
        self._mode = mode
        self._frameless_behavior = None

        if mode == "frameless":
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
            self._setup_frameless_behavior()

    def _setup_frameless_behavior(self):
        """Initialize frameless behavior after UI is set up."""
        self._frameless_behavior = FramelessWindowBehavior(
            draggable_widget=self.title_bar,
            resize_margin=5,
        )

    def mousePressEvent(self, event):
        # Only delegate if behavior exists
        if self._frameless_behavior and self._frameless_behavior.handle_press(self, event):
            return
        super().mousePressEvent(event)

    # Other mouse handlers check self._frameless_behavior before delegating...
```

## Configuration Options

### Constructor Parameters

```python
FramelessWindowBehavior(
    draggable_widget: Optional[QWidget] = None,
    resize_margin: int = 5,
    enable_resize: bool = True,
    enable_drag: bool = True,
    enable_double_click_maximize: bool = True,
    is_draggable_area: Optional[Callable[[QWidget, QPoint], bool]] = None,
)
```

**Parameters:**

- `draggable_widget`: Widget that triggers window dragging when clicked (e.g., title bar)
- `resize_margin`: Pixel width of resize edges (default: 5px)
- `enable_resize`: Enable edge-based window resizing
- `enable_drag`: Enable window dragging
- `enable_double_click_maximize`: Enable double-click to maximize window
- `is_draggable_area`: Custom callback for complex draggable area logic

### Choosing Between draggable_widget and is_draggable_area

**Use `draggable_widget` when:**
- You have a single, dedicated draggable widget (title bar)
- The draggable area doesn't change dynamically
- Simple use case

**Use `is_draggable_area` callback when:**
- Draggable area logic is complex
- Multiple widgets with conditional dragging (e.g., tab bar with tabs)
- Need to check child widget positions dynamically
- Draggable area changes based on state

**Note:** If both are provided, `is_draggable_area` takes precedence.

## Implementation Details

### Native API Usage

`FramelessWindowBehavior` prioritizes native window management APIs:

1. **Window Dragging:**
   - Primary: `QWindow.startSystemMove()` (Qt 5.15+)
   - Fallback: Manual window position updates

2. **Window Resizing:**
   - Primary: `QWindow.startSystemResize(edge)` (Qt 5.15+)
   - Fallback: Manual resize via geometry updates

**Benefits of native APIs:**
- Smooth, OS-native animations
- Respects OS window snapping/tiling
- Better touch and gesture support
- Lower CPU usage

### Edge Detection

The behavior automatically detects window edges for resizing:

```
┌─────────────────────────┐
│ TL     Top Edge      TR │  TL/TR = Top-Left/Top-Right corners
│                         │
├─ Left          Right ───┤  Edges detected within resize_margin pixels
│                         │
│ BL    Bottom Edge    BR │  BL/BR = Bottom-Left/Bottom-Right corners
└─────────────────────────┘
```

**Cursor shapes automatically applied:**
- Corners: Diagonal resize cursors (↖ ↗ ↙ ↘)
- Edges: Horizontal or vertical resize cursors (↔ ↕)
- Center: Arrow cursor

## Real-World Examples

### ChromeTabbedWindow

Uses custom callback for tab bar dragging:

```python
def _initialize_frameless_behavior(self) -> None:
    def is_draggable_area(widget: QWidget, pos) -> bool:
        # Only empty tab bar areas, not tabs or buttons
        tab_bar_rect = self._tab_bar.rect()
        tab_bar_pos = self._tab_bar.mapTo(self, tab_bar_rect.topLeft())
        tab_bar_global_rect = QRect(tab_bar_pos, tab_bar_rect.size())

        if tab_bar_global_rect.contains(pos):
            local_pos = self._tab_bar.mapFrom(self, pos)
            tab_index = self._tab_bar.tabAt(local_pos)
            is_valid_tab = tab_index >= 0 and tab_index < self._tab_bar.count()

            if not is_valid_tab:
                # Check if on new tab button
                return not (hasattr(self._tab_bar, 'new_tab_button_rect') and
                           self._tab_bar.new_tab_button_rect.contains(local_pos))
        return False

    self._frameless_behavior = FramelessWindowBehavior(
        draggable_widget=None,
        is_draggable_area=is_draggable_area,
        resize_margin=4,
    )
```

See: `widgets/chrome-tabbed-window/src/chrome_tabbed_window/chrome_tabbed_window.py:304-343`

### ViloCodeWindow

Uses simple title bar widget:

```python
def _initialize_frameless_behavior(self) -> None:
    if self._window_mode != WindowMode.Frameless or self._title_bar is None:
        return

    self._frameless_behavior = FramelessWindowBehavior(
        draggable_widget=self._title_bar,
        resize_margin=5,
        enable_resize=True,
        enable_drag=True,
        enable_double_click_maximize=True,
    )
```

See: `widgets/vilocode_window/src/vfwidgets_vilocode_window/vilocode_window.py:158-170`

## Testing

`FramelessWindowBehavior` has comprehensive test coverage:

```bash
# Run tests
cd shared/vfwidgets_common
pytest tests/test_frameless.py -v

# 21 tests covering:
# - Edge detection (8 tests for corners/edges)
# - Cursor updates (5 tests)
# - Draggable area detection (4 tests)
# - Custom configuration (4 tests)
```

## Best Practices

1. **Initialize after UI setup**: Create behavior after all widgets exist
   ```python
   self._setup_ui()  # Create title bar, etc.
   self._initialize_frameless_behavior()  # Now create behavior
   ```

2. **Enable mouse tracking**: Required for cursor updates
   ```python
   self.setMouseTracking(True)
   ```

3. **Set resize margins in layout**: Prevent child widgets from consuming edge events
   ```python
   margin = 4 if frameless else 0
   main_layout.setContentsMargins(margin, margin, margin, margin)
   ```

4. **Check behavior exists**: In conditional mode, verify behavior before delegating
   ```python
   if self._frameless_behavior and self._frameless_behavior.handle_press(self, event):
       return
   ```

5. **Use composition**: Don't inherit from FramelessWindowBehavior
   ```python
   # Good: Composition
   self._frameless_behavior = FramelessWindowBehavior(...)

   # Bad: Don't do this
   class MyWidget(FramelessWindowBehavior, QWidget):  # ❌
   ```

## Troubleshooting

### Window doesn't drag

**Possible causes:**
1. `draggable_widget` not set and no `is_draggable_area` callback
2. `enable_drag=False`
3. Mouse events not delegated to behavior
4. Child widget consuming mouse events (check `setMouseTracking`)

### Edge resizing doesn't work

**Possible causes:**
1. `enable_resize=False`
2. `resize_margin` too small (try increasing to 10)
3. Layout margins covering resize edges (check `contentsMargins`)
4. Child widgets overlapping edges

### Cursor doesn't update

**Possible causes:**
1. `setMouseTracking(True)` not called
2. Not delegating `mouseMoveEvent` to behavior
3. Child widget overriding cursor

### Double-click maximize not working

**Possible causes:**
1. `enable_double_click_maximize=False`
2. Not delegating `mouseDoubleClickEvent` to behavior
3. Position not in draggable area

## Migration Guide

If you have existing frameless window code, here's how to migrate:

### Step 1: Add Dependency

```toml
# pyproject.toml
dependencies = [
    "vfwidgets-common>=0.1.0",
]
```

### Step 2: Import and Initialize

```python
from vfwidgets_common import FramelessWindowBehavior

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._frameless_behavior = None  # Initialize as None
        # ... setup UI ...
        self._initialize_frameless_behavior()

    def _initialize_frameless_behavior(self):
        self._frameless_behavior = FramelessWindowBehavior(
            draggable_widget=self.title_bar,
            resize_margin=5,
        )
```

### Step 3: Delegate Mouse Events

```python
def mousePressEvent(self, event):
    if self._frameless_behavior and self._frameless_behavior.handle_press(self, event):
        return
    super().mousePressEvent(event)

def mouseMoveEvent(self, event):
    if self._frameless_behavior and self._frameless_behavior.handle_move(self, event):
        return
    super().mouseMoveEvent(event)

def mouseReleaseEvent(self, event):
    if self._frameless_behavior and self._frameless_behavior.handle_release(self, event):
        return
    super().mouseReleaseEvent(event)

def mouseDoubleClickEvent(self, event):
    if self._frameless_behavior and self._frameless_behavior.handle_double_click(self, event):
        return
    super().mouseDoubleClickEvent(event)
```

### Step 4: Remove Old Code

Delete these methods/attributes from your widget:
- `_get_resize_edge()`
- `_update_cursor_for_edge()`
- `_start_system_resize()`
- `_drag_position` state variable
- `_resize_edge` state variable
- `RESIZE_MARGIN` constant
- Manual `startSystemMove()` calls
- Manual cursor update logic

### Step 5: Test

Run your widget and verify:
- [ ] Window drags from title bar
- [ ] Window resizes from edges
- [ ] Cursor updates on edge hover
- [ ] Double-click maximizes
- [ ] All examples still work

## API Reference

### FramelessWindowBehavior

```python
class FramelessWindowBehavior:
    """Encapsulates frameless window dragging and resizing behavior."""

    def __init__(
        self,
        draggable_widget: Optional[QWidget] = None,
        resize_margin: int = 5,
        enable_resize: bool = True,
        enable_drag: bool = True,
        enable_double_click_maximize: bool = True,
        is_draggable_area: Optional[Callable[[QWidget, QPoint], bool]] = None,
    ):
        """Initialize frameless window behavior.

        Args:
            draggable_widget: Widget that triggers window dragging (e.g., title bar)
            resize_margin: Pixel width of resize edges
            enable_resize: Enable edge-based window resizing
            enable_drag: Enable window dragging
            enable_double_click_maximize: Enable double-click to maximize
            is_draggable_area: Custom callback for draggable area logic
        """

    def handle_press(self, widget: QWidget, event: QMouseEvent) -> bool:
        """Handle mouse press event.

        Args:
            widget: The window widget
            event: Mouse press event

        Returns:
            True if event was handled, False otherwise
        """

    def handle_move(self, widget: QWidget, event: QMouseEvent) -> bool:
        """Handle mouse move event.

        Args:
            widget: The window widget
            event: Mouse move event

        Returns:
            True if event was handled, False otherwise
        """

    def handle_release(self, widget: QWidget, event: QMouseEvent) -> bool:
        """Handle mouse release event.

        Args:
            widget: The window widget
            event: Mouse release event

        Returns:
            True if event was handled, False otherwise
        """

    def handle_double_click(self, widget: QWidget, event: QMouseEvent) -> bool:
        """Handle mouse double-click event.

        Args:
            widget: The window widget
            event: Mouse double-click event

        Returns:
            True if event was handled, False otherwise
        """
```

## Related Documentation

- [VFWidgets Common API](../README.md)
- [ChromeTabbedWindow Implementation](../../widgets/chrome-tabbed-window/src/chrome_tabbed_window/chrome_tabbed_window.py)
- [ViloCodeWindow Implementation](../../widgets/vilocode_window/src/vfwidgets_vilocode_window/vilocode_window.py)
- [FramelessWindowBehavior Tests](../tests/test_frameless.py)

## Contributing

If you find issues with `FramelessWindowBehavior` or have suggestions for improvements, please:

1. Check existing issues: https://github.com/vilosource/vfwidgets/issues
2. Create a new issue with:
   - Clear description of the problem
   - Minimal reproducible example
   - Expected vs actual behavior
   - Qt version and platform

Pull requests welcome!
