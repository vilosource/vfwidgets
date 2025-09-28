# Phase 2 Remaining Tasks - Detailed Implementation Guide

## Overview
Complete the remaining Phase 2 features to achieve full Chrome browser parity.

**Working Directory:** `/home/kuja/GitHub/vfwidgets/widgets/chrome-tabbed-window/`

---

## 1. Tab Animations (Priority 1)

### 1.1 Create TabAnimator Component
**File:** `src/chrome_tabbed_window/components/tab_animator.py`

```python
from PySide6.QtCore import QObject, QPropertyAnimation, QEasingCurve, QRect, Signal
from PySide6.QtWidgets import QWidget

class TabAnimator(QObject):
    """Handles all tab animations for smooth 60 FPS transitions."""

    animationFinished = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.animations = []
        self.ANIMATION_DURATION = 200  # ms

    def animate_tab_insertion(self, tab_bar, index: int):
        """Animate new tab sliding in from right."""
        # Implementation:
        # 1. Get tab rect at index
        # 2. Start tab at width=0
        # 3. Animate to full width over 200ms
        # 4. Use QEasingCurve.OutCubic for smooth deceleration

    def animate_tab_removal(self, tab_bar, index: int):
        """Animate tab collapsing and others sliding left."""
        # Implementation:
        # 1. Animate removed tab width to 0
        # 2. Simultaneously slide other tabs left
        # 3. Duration: 150ms for snappy feel

    def animate_hover(self, widget: QWidget, hover: bool):
        """Animate hover state with opacity fade."""
        # Implementation:
        # 1. Create QPropertyAnimation for opacity
        # 2. Fade in to 1.0 on hover, fade out to 0.8
        # 3. Duration: 100ms for responsive feel
```

### 1.2 Integration Points
- **ChromeTabBar:** Connect animator to tab add/remove events
- **Signal connections:** tabAdded → animate_tab_insertion
- **Frame rate:** Ensure 60 FPS by using Qt's animation framework

### 1.3 Testing Requirements
```python
def test_animation_performance():
    """Verify animations run at 60 FPS."""
    # Measure frame times during animation
    # Assert average frame time < 16.67ms (60 FPS)
```

---

## 2. New Tab Button (+)

### 2.1 Implementation in ChromeTabBar
**File:** `src/chrome_tabbed_window/view/chrome_tab_bar.py`

Add to `__init__`:
```python
self.new_tab_button_rect = QRect()
self.new_tab_button_hovered = False
self.new_tab_button_size = QSize(28, 28)
```

Add method:
```python
def _calculate_new_tab_button_position(self) -> QRect:
    """Position new tab button after last tab."""
    if self.count() > 0:
        last_tab_rect = self.tabRect(self.count() - 1)
        x = last_tab_rect.right() + 8
        y = last_tab_rect.center().y() - self.new_tab_button_size.height() // 2
    else:
        x = 8
        y = (self.height() - self.new_tab_button_size.height()) // 2

    return QRect(x, y, self.new_tab_button_size.width(),
                 self.new_tab_button_size.height())
```

Paint in `paintEvent`:
```python
# After painting tabs, paint new tab button
self.new_tab_button_rect = self._calculate_new_tab_button_position()
state = TabState.HOVER if self.new_tab_button_hovered else TabState.NORMAL
ChromeTabRenderer.draw_new_tab_button(painter, self.new_tab_button_rect, state)
```

Handle clicks:
```python
def mousePressEvent(self, event):
    if self.new_tab_button_rect.contains(event.pos()):
        self.newTabRequested.emit()  # New signal
        return
    super().mousePressEvent(event)
```

---

## 3. Tab Drag-and-Drop Reordering

### 3.1 Drag Detection
**File:** `src/chrome_tabbed_window/view/chrome_tab_bar.py`

Add drag state:
```python
self._drag_start_position = None
self._dragged_tab_index = -1
self._drag_indicator_position = -1
```

Implement drag detection:
```python
def mousePressEvent(self, event):
    if event.button() == Qt.LeftButton:
        index = self.tabAt(event.pos())
        if index >= 0:
            self._drag_start_position = event.pos()
            self._dragged_tab_index = index
```

Start drag on movement:
```python
def mouseMoveEvent(self, event):
    if self._drag_start_position is not None:
        if (event.pos() - self._drag_start_position).manhattanLength() > 5:
            # Start drag
            self._start_tab_drag()
```

### 3.2 Visual Feedback
```python
def _paint_drag_indicator(self, painter):
    """Paint insertion indicator between tabs."""
    if self._drag_indicator_position >= 0:
        # Draw vertical line where tab will be inserted
        x = self._calculate_drop_position(self._drag_indicator_position)
        painter.setPen(QPen(QColor(0, 120, 215), 2))  # Windows blue
        painter.drawLine(x, 5, x, self.height() - 5)
```

### 3.3 Drop Handling
```python
def dropEvent(self, event):
    """Handle tab drop to reorder."""
    drop_index = self._calculate_drop_index(event.pos())
    if drop_index != self._dragged_tab_index:
        # Animate the move
        animator = TabAnimator(self)
        animator.animate_tab_reorder(self, self._dragged_tab_index, drop_index)

        # Update model
        self._model.move_tab(self._dragged_tab_index, drop_index)
```

---

## 4. Tab Overflow with Scroll

### 4.1 Scroll Button Implementation
**File:** `src/chrome_tabbed_window/view/chrome_tab_bar.py`

Add scroll state:
```python
self._scroll_offset = 0
self._needs_scroll = False
self._left_scroll_button = QRect()
self._right_scroll_button = QRect()
```

Calculate if scrolling needed:
```python
def _calculate_scroll_need(self):
    """Check if tabs exceed available width."""
    total_tab_width = sum(self.tabSizeHint(i).width() for i in range(self.count()))
    available_width = self.width() - self.new_tab_button_size.width() - 20
    self._needs_scroll = total_tab_width > available_width
```

Paint scroll buttons:
```python
def _paint_scroll_buttons(self, painter):
    """Paint left/right scroll buttons when needed."""
    if not self._needs_scroll:
        return

    # Left button
    self._left_scroll_button = QRect(0, 0, 20, self.height())
    painter.fillRect(self._left_scroll_button, QColor(200, 200, 200))
    # Draw < arrow

    # Right button (before new tab button)
    x = self.new_tab_button_rect.left() - 25
    self._right_scroll_button = QRect(x, 0, 20, self.height())
    painter.fillRect(self._right_scroll_button, QColor(200, 200, 200))
    # Draw > arrow
```

---

## 5. Window Edge Resizing

### 5.1 Edge Detection
**File:** `src/chrome_tabbed_window/chrome_tabbed_window.py`

Add edge detection:
```python
def _get_resize_edge(self, pos):
    """Detect which edge/corner mouse is over."""
    MARGIN = 8
    rect = self.rect()

    edges = []
    if pos.x() < MARGIN:
        edges.append('left')
    elif pos.x() > rect.width() - MARGIN:
        edges.append('right')

    if pos.y() < MARGIN:
        edges.append('top')
    elif pos.y() > rect.height() - MARGIN:
        edges.append('bottom')

    return edges
```

### 5.2 Cursor Changes
```python
def mouseMoveEvent(self, event):
    if self._window_mode == WindowMode.Frameless:
        edges = self._get_resize_edge(event.pos())

        if 'left' in edges and 'top' in edges:
            self.setCursor(Qt.SizeFDiagCursor)
        elif 'right' in edges and 'bottom' in edges:
            self.setCursor(Qt.SizeFDiagCursor)
        elif 'left' in edges or 'right' in edges:
            self.setCursor(Qt.SizeHorCursor)
        elif 'top' in edges or 'bottom' in edges:
            self.setCursor(Qt.SizeVerCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
```

### 5.3 Resize Implementation
```python
def mousePressEvent(self, event):
    if self._window_mode == WindowMode.Frameless:
        edges = self._get_resize_edge(event.pos())
        if edges:
            # Qt 6.5+ method
            if hasattr(self.windowHandle(), 'startSystemResize'):
                edge_map = {
                    ('left',): Qt.LeftEdge,
                    ('right',): Qt.RightEdge,
                    ('top',): Qt.TopEdge,
                    ('bottom',): Qt.BottomEdge,
                    ('left', 'top'): Qt.TopLeftEdge,
                    # etc.
                }
                qt_edge = edge_map.get(tuple(edges))
                if qt_edge:
                    self.windowHandle().startSystemResize(qt_edge)
```

---

## 6. Platform-Specific Adapters

### 6.1 Windows Platform Adapter
**File:** `src/chrome_tabbed_window/platform/windows.py`

```python
from ..base import PlatformAdapter
import sys

class WindowsPlatformAdapter(PlatformAdapter):
    """Windows-specific features and optimizations."""

    def setup_widget(self, widget):
        """Apply Windows-specific setup."""
        super().setup_widget(widget)

        if widget._window_mode == WindowMode.Frameless:
            # Enable DWM shadow
            if sys.platform == 'win32':
                try:
                    import ctypes
                    from ctypes import wintypes

                    # Enable shadow
                    MARGINS = ctypes.c_int * 4
                    margins = MARGINS(1, 1, 1, 1)
                    ctypes.windll.dwmapi.DwmExtendFrameIntoClientArea(
                        widget.winId(),
                        ctypes.byref(margins)
                    )
                except:
                    pass  # Graceful fallback

    def handle_aero_snap(self, widget):
        """Handle Windows Aero Snap zones."""
        # Implementation for snap detection
        pass
```

### 6.2 macOS Platform Adapter
**File:** `src/chrome_tabbed_window/platform/macos.py`

```python
class MacOSPlatformAdapter(PlatformAdapter):
    """macOS-specific features."""

    def setup_widget(self, widget):
        """Apply macOS-specific setup."""
        super().setup_widget(widget)

        if widget._window_mode == WindowMode.Frameless:
            # Position window controls on left
            if hasattr(widget, '_window_controls'):
                # Move controls to left side
                pass

    def setup_traffic_lights(self, widget):
        """Setup native traffic light buttons."""
        # Use native macOS window buttons if possible
        pass
```

### 6.3 Linux Platform Adapter
**File:** `src/chrome_tabbed_window/platform/linux.py`

```python
import os

class LinuxPlatformAdapter(PlatformAdapter):
    """Linux/X11/Wayland support."""

    def __init__(self):
        super().__init__()
        self.is_wayland = 'WAYLAND_DISPLAY' in os.environ
        self.is_x11 = 'DISPLAY' in os.environ and not self.is_wayland

    def setup_widget(self, widget):
        """Apply Linux-specific setup."""
        super().setup_widget(widget)

        if self.is_wayland:
            # Wayland limitations
            # - Can't set window position
            # - Limited decoration control
            pass
        elif self.is_x11:
            # X11 features
            # - EWMH hints
            # - Compositor detection
            pass
```

---

## Testing Strategy

### Performance Tests
```python
def test_animation_fps():
    """Ensure 60 FPS during animations."""
    # Create timer to measure frame rates
    # Assert average > 55 FPS

def test_drag_responsiveness():
    """Test drag operation responsiveness."""
    # Measure drag start latency
    # Assert < 50ms
```

### Visual Tests
```python
def test_chrome_appearance():
    """Compare rendering to reference Chrome screenshot."""
    # Render widget
    # Compare to reference image
    # Assert similarity > 95%
```

---

## Implementation Order

1. **Tab Animations** (2 days)
   - Create TabAnimator class
   - Integrate with ChromeTabBar
   - Test performance

2. **New Tab Button** (1 day)
   - Add button rendering
   - Handle clicks
   - Position correctly

3. **Drag and Drop** (2 days)
   - Implement drag detection
   - Visual feedback
   - Reorder logic

4. **Tab Overflow** (1 day)
   - Scroll detection
   - Button rendering
   - Scroll logic

5. **Edge Resizing** (1 day)
   - Edge detection
   - Cursor changes
   - Resize handling

6. **Platform Adapters** (2 days)
   - Windows adapter
   - macOS adapter
   - Linux adapter

---

## Success Criteria

✅ All animations run at 60 FPS
✅ New tab button works like Chrome
✅ Tabs can be reordered by dragging
✅ Many tabs scroll properly
✅ Window can be resized from edges
✅ Platform-specific features work

---

## Notes for Developer Agent

- Use Qt's animation framework for smooth 60 FPS
- Follow existing MVC architecture strictly
- Test on all platforms if possible
- Maintain QTabWidget compatibility
- Reference ChromeTabRenderer for visual consistency
- Use signals for all user interactions
- Handle edge cases (0 tabs, 100+ tabs)
- Performance is critical - profile everything