# Phase 2: Components Tasks — ViloCodeWindow Implementation

**Goal**: Implement all UI components (ActivityBar, SideBar, MainPane, AuxiliaryBar) and wire them together with the core widget.

**Status**: 🔴 Not Started (Blocked by Phase 1)

---

## Task Checklist

### Activity Bar Component

- [ ] **Task 2.1**: Create ActivityBar widget class
  ```python
  class ActivityBar(QWidget):
      """Vertical icon bar on the left edge.

      Features:
      - Fixed width (~48px)
      - Vertical layout of icon buttons
      - One active (highlighted) item at a time
      - Emits signals when items clicked
      """

      item_clicked = Signal(str)  # item_id

      def __init__(self, parent=None):
          super().__init__(parent)
          self._items = {}  # item_id -> ActivityBarItem
          self._active_item = None
          self._setup_ui()
  ```

- [ ] **Task 2.2**: Create ActivityBarItem widget
  ```python
  class ActivityBarItem(QWidget):
      """Single item in activity bar (icon button).

      States:
      - Normal: Default appearance
      - Hover: Slightly lighter background
      - Active: Border highlight on left edge
      - Pressed: Darker background
      """

      clicked = Signal()

      def __init__(self, item_id: str, icon: QIcon, tooltip: str = ""):
          super().__init__()
          self._item_id = item_id
          self._icon = icon
          self._tooltip = tooltip
          self._is_active = False

          self.setFixedSize(48, 48)  # Square button
          self.setToolTip(tooltip)
  ```

- [ ] **Task 2.3**: Implement ActivityBarItem painting
  - Paint icon centered in 48x48 square
  - Paint left border (3px) when active
  - Use theme colors or fallbacks
  - Smooth hover transitions

- [ ] **Task 2.4**: Implement ActivityBar API
  ```python
  def add_item(self, item_id: str, icon: QIcon, tooltip: str = "") -> QAction:
      """Add an activity bar item."""

  def remove_item(self, item_id: str) -> None:
      """Remove an activity bar item."""

  def set_active_item(self, item_id: str) -> None:
      """Set the active (highlighted) item."""

  def get_active_item(self) -> Optional[str]:
      """Get the currently active item ID."""

  # NEW: Enhanced APIs
  def set_item_icon(self, item_id: str, icon: QIcon) -> None:
      """Update item icon."""

  def set_item_enabled(self, item_id: str, enabled: bool) -> None:
      """Enable/disable item."""

  def is_item_enabled(self, item_id: str) -> bool:
      """Check if item is enabled."""

  def get_items(self) -> List[str]:
      """Get all item IDs in order."""
  ```

- [ ] **Task 2.5**: Wire ActivityBar to ViloCodeWindow
  - Replace placeholder in layout
  - Implement `add_activity_item()` in ViloCodeWindow
  - Connect signals: ActivityBar.item_clicked → ViloCodeWindow.activity_item_clicked
  - Expose QAction for each item

---

### SideBar Component

- [ ] **Task 2.6**: Create SideBar widget class
  ```python
  class SideBar(QWidget):
      """Collapsible sidebar with stackable panels.

      Structure:
      ┌─────────────────┐
      │ PANEL TITLE     │  ← Header
      ├─────────────────┤
      │                 │
      │  Panel Content  │  ← QStackedWidget
      │  (one at a time)│
      │                 │
      └─────────────────┘

      Features:
      - Multiple panels, one visible at a time
      - Collapsible (toggle visibility)
      - Resizable width (drag border)
      - Panel title shown in header
      """

      panel_changed = Signal(str)  # panel_id
      visibility_changed = Signal(bool)  # is_visible

      def __init__(self, parent=None):
          super().__init__(parent)
          self._panels = {}  # panel_id -> (widget, title)
          self._current_panel = None
          self._setup_ui()
  ```

- [ ] **Task 2.7**: Create SideBar header
  ```python
  class SideBarHeader(QWidget):
      """Header showing current panel title.

      Layout: [Title Label] [Stretch] [Optional Buttons]
      """
      def __init__(self, parent=None):
          super().__init__(parent)
          self._title_label = QLabel()
          self._title_label.setStyleSheet("font-weight: bold; font-size: 11px;")
          # Add to layout
  ```

- [ ] **Task 2.8**: Implement SideBar layout
  - Vertical layout: [Header] [Content Stack]
  - Content = QStackedWidget for panels
  - Default width: 250px
  - Minimum width: 150px
  - Maximum width: 500px

- [ ] **Task 2.9**: Implement SideBar API
  ```python
  def add_panel(self, panel_id: str, widget: QWidget, title: str = "") -> None:
      """Add a stackable panel."""

  def remove_panel(self, panel_id: str) -> None:
      """Remove a panel."""

  def show_panel(self, panel_id: str) -> None:
      """Switch to specified panel."""

  def get_panel(self, panel_id: str) -> Optional[QWidget]:
      """Get panel widget by ID."""

  def toggle_visibility(self) -> None:
      """Toggle sidebar visibility."""

  def set_visible(self, visible: bool) -> None:
      """Show/hide sidebar."""
  ```

- [ ] **Task 2.10**: Implement SideBar resize handle
  - Add vertical resize handle on right edge
  - Drag to resize width
  - Cursor changes to resize cursor on hover
  - Emit signal when width changes (for persistence in v2.0)

- [ ] **Task 2.11**: Wire SideBar to ViloCodeWindow
  - Replace placeholder in layout
  - Implement `add_sidebar_panel()` in ViloCodeWindow
  - Implement `show_sidebar_panel()` in ViloCodeWindow
  - Implement `toggle_sidebar()` in ViloCodeWindow
  - Connect signals

---

### Main Pane Component

- [ ] **Task 2.12**: Create MainPane widget class
  ```python
  class MainPane(QWidget):
      """Main content area (center).

      Simple container for developer-provided content.
      Takes all remaining horizontal space.
      """

      def __init__(self, parent=None):
          super().__init__(parent)
          self._content = None
          self._setup_ui()
  ```

- [ ] **Task 2.13**: Implement MainPane layout
  - Single QVBoxLayout with margins=0, spacing=0
  - When content set, clear old and add new

- [ ] **Task 2.14**: Implement MainPane API
  ```python
  def set_content(self, widget: QWidget) -> None:
      """Set the main pane content widget."""

  def get_content(self) -> Optional[QWidget]:
      """Get the current content widget."""
  ```

- [ ] **Task 2.15**: Wire MainPane to ViloCodeWindow
  - Replace placeholder in layout
  - Implement `set_main_content()` in ViloCodeWindow
  - Implement `get_main_content()` in ViloCodeWindow
  - Set stretch factor = 1 (takes remaining space)

---

### Auxiliary Bar Component

- [ ] **Task 2.16**: Create AuxiliaryBar widget class
  ```python
  class AuxiliaryBar(QWidget):
      """Right sidebar (auxiliary panel).

      Features:
      - Single content widget (not stackable)
      - Hidden by default
      - Resizable width (drag left border)
      - No header (just content)
      """

      visibility_changed = Signal(bool)  # is_visible

      def __init__(self, parent=None):
          super().__init__(parent)
          self._content = None
          self._setup_ui()
          self.setVisible(False)  # Hidden by default
  ```

- [ ] **Task 2.17**: Implement AuxiliaryBar layout
  - Single QVBoxLayout for content
  - Default width: 300px
  - Minimum width: 150px
  - Maximum width: 500px

- [ ] **Task 2.18**: Implement AuxiliaryBar resize handle
  - Add vertical resize handle on left edge
  - Drag to resize width
  - Cursor changes to resize cursor on hover

- [ ] **Task 2.19**: Implement AuxiliaryBar API
  ```python
  def set_content(self, widget: QWidget) -> None:
      """Set the auxiliary bar content widget."""

  def get_content(self) -> Optional[QWidget]:
      """Get the current content widget."""

  def toggle_visibility(self) -> None:
      """Toggle auxiliary bar visibility."""
  ```

- [ ] **Task 2.20**: Wire AuxiliaryBar to ViloCodeWindow
  - Replace placeholder in layout
  - Implement `set_auxiliary_content()` in ViloCodeWindow
  - Implement `toggle_auxiliary_bar()` in ViloCodeWindow
  - Connect signals

---

### Component Styling & Theming

- [ ] **Task 2.21**: Add theme tokens for all components
  ```python
  theme_config = {
      # Activity Bar
      "activity_bar_background": "activityBar.background",
      "activity_bar_foreground": "activityBar.foreground",
      "activity_bar_border": "activityBar.border",
      "activity_bar_active_border": "activityBar.activeBorder",
      "activity_bar_inactive_foreground": "activityBar.inactiveForeground",

      # Sidebar
      "sidebar_background": "sideBar.background",
      "sidebar_foreground": "sideBar.foreground",
      "sidebar_border": "sideBar.border",
      "sidebar_title_foreground": "sideBarTitle.foreground",

      # Editor/Main Pane
      "editor_background": "editor.background",
      "editor_foreground": "editor.foreground",

      # Auxiliary Bar (reuse sidebar colors)
      # ... same as sidebar
  }
  ```

- [ ] **Task 2.22**: Implement component painting with theme colors
  - ActivityBar: Apply background, foreground, borders
  - SideBar: Apply background, title color, borders
  - MainPane: Apply editor background
  - AuxiliaryBar: Apply sidebar colors

- [ ] **Task 2.23**: Implement fallback colors for non-themed mode
  - Dark theme defaults (VS Code Dark+)
  - Apply via QSS when theme system unavailable

---

### Resize Handles

- [ ] **Task 2.24**: Create ResizeHandle widget
  ```python
  class ResizeHandle(QWidget):
      """Vertical resize handle for sidebars.

      Features:
      - 4px wide, full height
      - Cursor changes to SizeHorCursor on hover
      - Drag to resize adjacent widget
      """

      resize_started = Signal()
      resize_moved = Signal(int)  # delta_x
      resize_finished = Signal()

      def __init__(self, parent=None):
          super().__init__(parent)
          self.setFixedWidth(4)
          self.setCursor(Qt.CursorShape.SizeHorCursor)
  ```

- [ ] **Task 2.25**: Implement ResizeHandle dragging
  - mousePressEvent: Start drag
  - mouseMoveEvent: Emit delta
  - mouseReleaseEvent: Finish drag
  - Paint visual indicator (subtle line)

- [ ] **Task 2.26**: Integrate ResizeHandle with SideBar
  - Add handle to right edge of SideBar
  - Connect signals to resize sidebar width
  - Constrain to min/max width

- [ ] **Task 2.27**: Integrate ResizeHandle with AuxiliaryBar
  - Add handle to left edge of AuxiliaryBar
  - Connect signals to resize auxiliary bar width
  - Constrain to min/max width

---

### Integration & Signal Wiring

- [ ] **Task 2.28**: Connect ActivityBar to SideBar
  - When activity item clicked, show corresponding sidebar panel
  - Option 1: Auto-connect if IDs match
  - Option 2: Developer manually connects QAction.triggered
  - Recommended: Option 2 (more flexible)

- [ ] **Task 2.29**: Update active activity item when sidebar panel changes
  - When sidebar panel shown, highlight corresponding activity item
  - Handle case where no corresponding activity item exists

- [ ] **Task 2.30**: Implement sidebar visibility tracking
  - Remember last visible panel when hiding sidebar
  - Restore same panel when showing sidebar again
  - Emit `sidebar_visibility_changed` signal

---

### Component Tests

- [ ] **Task 2.31**: Write ActivityBar tests
  - Add/remove items
  - Set active item
  - Signal emission
  - Painting (visual test)

- [ ] **Task 2.32**: Write SideBar tests
  - Add/remove panels
  - Switch panels
  - Toggle visibility
  - Resize width

- [ ] **Task 2.33**: Write MainPane tests
  - Set content
  - Widget reparenting
  - Clear old content

- [ ] **Task 2.34**: Write AuxiliaryBar tests
  - Set content
  - Toggle visibility
  - Resize width

- [ ] **Task 2.35**: Write integration tests
  - Activity item → sidebar panel switching
  - All components together
  - Theme changes propagate to all components

---

### Documentation

- [ ] **Task 2.36**: Update API documentation
  - All component APIs
  - Signal descriptions
  - Usage examples

- [ ] **Task 2.37**: Create component architecture diagram
  - Visual diagram showing component hierarchy
  - Data flow (signals)
  - Layout structure

---

## Phase 2 Completion Criteria

✅ Phase 2 is complete when:
1. ActivityBar implemented with add/remove/active items
2. SideBar implemented with stackable panels
3. MainPane implemented with content setter
4. AuxiliaryBar implemented with content setter
5. All resize handles working
6. Theme colors applied to all components
7. Signals properly connected
8. All component tests passing
9. Visual appearance matches VS Code (with theme system)
10. API documentation updated

**Next Phase**: Phase 3 - Polish & Examples

---

## Notes

- Focus on MVC separation: components handle view, ViloCodeWindow orchestrates
- Use composition: ViloCodeWindow owns all components
- Keep components independent: don't couple ActivityBar to SideBar directly
- Theme integration critical for professional appearance
- Test resize handles thoroughly (common source of bugs)

---

## Evidence Requirements

- Show ActivityBar with icons rendered
- Show SideBar with multiple panels switching
- Show MainPane with actual content widget
- Show AuxiliaryBar toggle working
- Show resize handles working (video or GIF)
- Show theme colors applied correctly
- All tests passing with output shown
