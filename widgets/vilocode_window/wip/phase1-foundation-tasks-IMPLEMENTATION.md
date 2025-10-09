# Phase 1: Foundation Tasks — ViloCodeWindow Implementation

**Goal**: Create the core ViloCodeWindow class with basic layout structure, mode detection, and minimal functionality.

**Status**: 🔴 Not Started

---

## Task Checklist

### Setup & Project Structure

- [ ] **Task 1.1**: Create pyproject.toml with dependencies
  - PySide6 >= 6.5.0
  - Optional: vfwidgets-theme >= 2.0.0
  - Dev dependencies: pytest, pytest-qt, black, ruff, mypy
  - Package metadata: name, version, description, authors

- [ ] **Task 1.2**: Create package structure
  - `src/vfwidgets_vilocode_window/__init__.py` - Public API exports
  - `src/vfwidgets_vilocode_window/vilocode_window.py` - Main class
  - `src/vfwidgets_vilocode_window/core/__init__.py` - Core components
  - `src/vfwidgets_vilocode_window/components/__init__.py` - UI components
  - `tests/test_vilocode_window.py` - Basic tests

- [ ] **Task 1.3**: Create README.md with basic documentation
  - Project description
  - Quick start example
  - Installation instructions
  - Link to full specification

---

### Core Widget Implementation

- [ ] **Task 1.4**: Create ViloCodeWindow class skeleton
  ```python
  class ViloCodeWindow(QWidget):
      """VS Code-style application window."""

      # Signals
      activity_item_clicked = Signal(str)  # item_id
      sidebar_panel_changed = Signal(str)  # panel_id
      sidebar_visibility_changed = Signal(bool)  # is_visible
      auxiliary_bar_visibility_changed = Signal(bool)  # is_visible

      def __init__(
          self,
          parent: Optional[QWidget] = None,
          enable_default_shortcuts: bool = True
      ):
          super().__init__(parent)

          # Mode detection
          self._window_mode = self._detect_window_mode()

          # Components (create in later tasks)
          self._activity_bar = None
          self._sidebar = None
          self._main_pane = None
          self._auxiliary_bar = None
          self._status_bar = None
          self._menu_bar = None

          # Keyboard shortcuts
          self._shortcuts = {}  # key_sequence -> QShortcut
          self._action_callbacks = {}  # action_name -> callback (for set_shortcut)
          self._enable_default_shortcuts = enable_default_shortcuts

          self._setup_ui()

          if enable_default_shortcuts:
              self._setup_default_shortcuts()

      # Placeholder methods (implemented in Phase 2)
      def toggle_sidebar(self) -> None:
          """Toggle sidebar visibility (placeholder for Phase 1)."""
          pass

      def toggle_auxiliary_bar(self) -> None:
          """Toggle auxiliary bar visibility (placeholder for Phase 1)."""
          pass
  ```

- [ ] **Task 1.5**: Implement mode detection
  ```python
  def _detect_window_mode(self) -> WindowMode:
      """Detect if widget is top-level (frameless) or embedded."""
      if self.parent() is None:
          return WindowMode.Frameless
      else:
          return WindowMode.Embedded
  ```
  - Create `WindowMode` enum (Frameless, Embedded)
  - Store in `core/constants.py`

- [ ] **Task 1.6**: Implement frameless window setup (reuse ChromeTabbedWindow pattern)
  ```python
  def _setup_frameless_window(self) -> None:
      """Set up frameless window for top-level mode."""
      self.setWindowFlags(
          Qt.WindowType.FramelessWindowHint
          | Qt.WindowType.WindowSystemMenuHint
          | Qt.WindowType.WindowMinMaxButtonsHint
          | Qt.WindowType.WindowCloseButtonHint
      )
      self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
      self.setMinimumSize(600, 400)
  ```

- [ ] **Task 1.6b**: Implement paintEvent for frameless background
  ```python
  def paintEvent(self, event: QPaintEvent) -> None:
      """Paint window background in frameless mode."""
      if self._window_mode == WindowMode.Frameless:
          painter = QPainter(self)

          # Get background color (from theme or fallback)
          if THEME_AVAILABLE and hasattr(self, "_theme_manager"):
              bg_color = self._get_theme_color("titlebar_background")
          else:
              bg_color = self._get_fallback_color("titlebar_background")

          # Fill background
          painter.fillRect(self.rect(), bg_color)

          # Optional: draw border for better definition
          painter.setPen(QColor("#333333"))
          painter.drawRect(self.rect().adjusted(0, 0, -1, -1))

      super().paintEvent(event)
  ```

- [ ] **Task 1.7**: Create basic layout structure
  ```python
  def _setup_ui(self) -> None:
      """Set up the user interface layout."""
      main_layout = QVBoxLayout(self)
      main_layout.setContentsMargins(0, 0, 0, 0)
      main_layout.setSpacing(0)

      # Title bar (frameless mode only)
      if self._window_mode == WindowMode.Frameless:
          self._setup_title_bar()
          main_layout.addWidget(self._title_bar)

      # Content layout (horizontal: activity + sidebar + main + auxiliary)
      content_layout = QHBoxLayout()
      content_layout.setContentsMargins(0, 0, 0, 0)
      content_layout.setSpacing(0)

      # Placeholder widgets (implement in Phase 2)
      content_layout.addWidget(QLabel("Activity Bar"))  # Replace with ActivityBar
      content_layout.addWidget(QLabel("Sidebar"))       # Replace with SideBar
      content_layout.addWidget(QLabel("Main Pane"), 1)  # Replace with MainPane, stretch=1
      content_layout.addWidget(QLabel("Auxiliary"))     # Replace with AuxiliaryBar

      main_layout.addLayout(content_layout, 1)  # Stretch=1

      # Status bar
      self._status_bar = QStatusBar(self)
      main_layout.addWidget(self._status_bar)
  ```

- [ ] **Task 1.7b**: Implement status bar API
  ```python
  def get_status_bar(self) -> QStatusBar:
      """Get the status bar widget for customization."""
      return self._status_bar

  def set_status_bar_visible(self, visible: bool) -> None:
      """Show/hide status bar."""
      self._status_bar.setVisible(visible)

  def is_status_bar_visible(self) -> bool:
      """Check if status bar is visible."""
      return self._status_bar.isVisible()

  def set_status_message(self, message: str, timeout: int = 0) -> None:
      """Convenience method to show status message.

      Args:
          message: Status message to display
          timeout: Time in milliseconds (0 = until next message)
      """
      self._status_bar.showMessage(message, timeout)
  ```

---

### Platform Detection & Adaptation

- [ ] **Task 1.8**: Copy platform detection from ChromeTabbedWindow
  - Copy `platform_support/` directory structure
  - `platform_support/detector.py` - Platform detection
  - `platform_support/capabilities.py` - PlatformCapabilities dataclass
  - `platform_support/base.py` - IPlatformAdapter protocol
  - Adapt for ViloCodeWindow needs

- [ ] **Task 1.9**: Implement platform factory
  ```python
  class PlatformFactory:
      @staticmethod
      def create(window: QWidget) -> IPlatformAdapter:
          """Create appropriate platform adapter."""
          system = platform.system()

          if system == "Windows":
              return WindowsPlatformAdapter(window)
          elif system == "Darwin":
              return MacOSPlatformAdapter(window)
          elif system == "Linux":
              if PlatformFactory._is_wsl():
                  return WSLPlatformAdapter(window)
              elif PlatformFactory._is_wayland():
                  return LinuxWaylandAdapter(window)
              else:
                  return LinuxX11Adapter(window)
          else:
              return FallbackPlatformAdapter(window)
  ```

- [ ] **Task 1.10**: Implement basic platform adapters
  - Windows: Full frameless support
  - macOS: Full frameless support
  - Linux X11: Full frameless support
  - Linux Wayland: Qt 6.5+ check
  - WSL: Fallback to native decorations
  - Fallback: Native decorations

---

### Window Controls & Title Bar

- [ ] **Task 1.11**: Copy WindowControls from ChromeTabbedWindow
  - `components/window_controls.py`
  - Minimize, maximize, close buttons
  - Platform-aware styling
  - Signal connections

- [ ] **Task 1.12**: Create custom title bar component
  ```python
  class TitleBar(QWidget):
      """Custom title bar for frameless mode.

      Layout: [Menu Bar] [Stretch] [Window Controls]
      """
      def __init__(self, parent):
          super().__init__(parent)
          self._setup_ui()

      def _setup_ui(self):
          layout = QHBoxLayout(self)
          layout.setContentsMargins(0, 0, 0, 0)
          layout.setSpacing(0)

          # Menu bar placeholder (set later)
          self._menu_bar_container = QWidget()
          layout.addWidget(self._menu_bar_container)

          # Stretch
          layout.addStretch(1)

          # Window controls
          self._window_controls = WindowControls(self)
          layout.addWidget(self._window_controls)

      def set_menu_bar(self, menubar: QMenuBar) -> None:
          """Set the menu bar (displayed in title bar)."""
          self._menu_bar = menubar
          # Add to container
          layout = self._menu_bar_container.layout()
          if not layout:
              layout = QHBoxLayout(self._menu_bar_container)
              layout.setContentsMargins(0, 0, 0, 0)
          layout.addWidget(menubar)

      def get_menu_bar(self) -> Optional[QMenuBar]:
          """Get the menu bar widget."""
          return self._menu_bar
  ```

- [ ] **Task 1.12b**: Implement menu bar API in ViloCodeWindow
  ```python
  def set_menu_bar(self, menubar: QMenuBar) -> None:
      """Set the menu bar (appears in top bar).

      In frameless mode, the menu bar is added to the title bar.
      In embedded mode, behavior depends on parent widget.

      Args:
          menubar: QMenuBar widget to set
      """
      self._menu_bar = menubar

      if self._window_mode == WindowMode.Frameless:
          # Add to title bar
          if self._title_bar:
              self._title_bar.set_menu_bar(menubar)
      else:
          # In embedded mode, developer can access via get_menu_bar()
          # and place it themselves
          pass

  def get_menu_bar(self) -> Optional[QMenuBar]:
      """Get the menu bar widget.

      Returns:
          The menu bar widget, or None if not set
      """
      return self._menu_bar
  ```

- [ ] **Task 1.13**: Implement window dragging
  - Copy event filter from ChromeTabbedWindow
  - Install on title bar for window move
  - Use `startSystemMove()` when available
  - Fallback to manual dragging

- [ ] **Task 1.14**: Implement window resizing
  - Copy resize edge detection from ChromeTabbedWindow
  - Implement `_get_resize_edge()` method
  - Use `startSystemResize()` when available
  - Fallback to manual resize

- [ ] **Task 1.15**: Implement double-click to maximize
  - Double-click title bar toggles maximize/restore
  - Update window controls button state

---

### Theme Integration

- [ ] **Task 1.16**: Set up theme system integration
  ```python
  try:
      from vfwidgets_theme import ThemedWidget
      THEME_AVAILABLE = True
  except ImportError:
      THEME_AVAILABLE = False
      ThemedWidget = object

  if THEME_AVAILABLE:
      _BaseClass = type("_BaseClass", (ThemedWidget, QWidget), {})
  else:
      _BaseClass = QWidget

  class ViloCodeWindow(_BaseClass):
      theme_config = {
          "titlebar_background": "titleBar.activeBackground",
          "titlebar_foreground": "titleBar.activeForeground",
          "statusbar_background": "statusBar.background",
          "statusbar_foreground": "statusBar.foreground",
          # Add more in Phase 2
      }
  ```

- [ ] **Task 1.17**: Implement `_on_theme_changed()` callback
  ```python
  def _on_theme_changed(self) -> None:
      """Called when theme changes (ThemedWidget callback)."""
      if not THEME_AVAILABLE:
          return

      # Update all components
      if self._title_bar:
          self._title_bar.update()
      if self._status_bar:
          self._status_bar.update()

      self.update()
  ```

- [ ] **Task 1.18**: Implement fallback colors (no theme system)
  ```python
  def _get_fallback_color(self, token: str) -> QColor:
      """Get fallback color when theme system unavailable."""
      fallback_colors = {
          "titlebar_background": "#323233",
          "titlebar_foreground": "#cccccc",
          "statusbar_background": "#007acc",
          "statusbar_foreground": "#ffffff",
          # Add more
      }
      return QColor(fallback_colors.get(token, "#1e1e1e"))
  ```

---

### Keyboard Shortcuts Infrastructure

- [ ] **Task 1.19**: Create shortcuts constants file
  ```python
  # core/shortcuts.py

  DEFAULT_SHORTCUTS = {
      # Core Layout (VS Code compatible)
      "toggle_sidebar": "Ctrl+B",
      "toggle_auxiliary_bar": "Ctrl+Alt+B",
      "focus_sidebar": "Ctrl+0",
      "focus_main_pane": "Ctrl+1",

      # Activity Items (dynamically bound to first 5)
      "show_activity_1": "Ctrl+Shift+E",
      "show_activity_2": "Ctrl+Shift+F",
      "show_activity_3": "Ctrl+Shift+G",
      "show_activity_4": "Ctrl+Shift+D",
      "show_activity_5": "Ctrl+Shift+X",

      # Window
      "toggle_fullscreen": "F11",
  }
  ```

- [ ] **Task 1.20**: Implement keyboard shortcut management
  ```python
  def register_shortcut(
      self,
      key_sequence: str,
      callback: Callable,
      description: str = ""
  ) -> QShortcut:
      """Register a keyboard shortcut."""
      shortcut = QShortcut(QKeySequence(key_sequence), self)
      shortcut.activated.connect(callback)
      self._shortcuts[key_sequence] = {
          "shortcut": shortcut,
          "callback": callback,
          "description": description
      }
      return shortcut

  def unregister_shortcut(self, key_sequence: str) -> None:
      """Unregister a keyboard shortcut."""
      if key_sequence in self._shortcuts:
          self._shortcuts[key_sequence]["shortcut"].setEnabled(False)
          self._shortcuts[key_sequence]["shortcut"].deleteLater()
          del self._shortcuts[key_sequence]

  def get_shortcuts(self) -> Dict[str, QShortcut]:
      """Get all registered shortcuts."""
      return {k: v["shortcut"] for k, v in self._shortcuts.items()}

  def get_default_shortcuts(self) -> Dict[str, str]:
      """Get default keyboard shortcuts."""
      from .core.shortcuts import DEFAULT_SHORTCUTS
      return DEFAULT_SHORTCUTS.copy()

  def set_shortcut(self, action: str, key_sequence: str) -> None:
      """Override a default shortcut.

      Args:
          action: Action name (e.g., "toggle_sidebar")
          key_sequence: New key sequence (e.g., "Ctrl+Shift+B")

      Raises:
          ValueError: If action name is unknown
      """
      from .core.shortcuts import DEFAULT_SHORTCUTS

      if action not in DEFAULT_SHORTCUTS:
          raise ValueError(f"Unknown action: {action}")

      if action not in self._action_callbacks:
          raise ValueError(f"Action {action} has no registered callback")

      # Get callback for this action
      callback = self._action_callbacks[action]

      # Find and unregister old shortcut
      old_key = DEFAULT_SHORTCUTS[action]
      if old_key in self._shortcuts:
          self.unregister_shortcut(old_key)

      # Register with new key sequence
      self.register_shortcut(key_sequence, callback, f"Override: {action}")
  ```

- [ ] **Task 1.21**: Implement default shortcuts setup
  ```python
  def _setup_default_shortcuts(self) -> None:
      """Set up default VS Code-compatible shortcuts."""
      from .core.shortcuts import DEFAULT_SHORTCUTS

      # Store action callbacks for set_shortcut() to use
      self._action_callbacks["toggle_sidebar"] = self.toggle_sidebar
      self._action_callbacks["toggle_auxiliary_bar"] = self.toggle_auxiliary_bar
      self._action_callbacks["focus_sidebar"] = self._focus_sidebar
      self._action_callbacks["focus_main_pane"] = self._focus_main_pane
      self._action_callbacks["toggle_fullscreen"] = self._toggle_fullscreen

      # Core layout shortcuts
      self.register_shortcut(
          DEFAULT_SHORTCUTS["toggle_sidebar"],
          self.toggle_sidebar,
          "Toggle sidebar visibility"
      )
      self.register_shortcut(
          DEFAULT_SHORTCUTS["toggle_auxiliary_bar"],
          self.toggle_auxiliary_bar,
          "Toggle auxiliary bar visibility"
      )
      self.register_shortcut(
          DEFAULT_SHORTCUTS["focus_sidebar"],
          self._focus_sidebar,
          "Focus sidebar panel"
      )
      self.register_shortcut(
          DEFAULT_SHORTCUTS["focus_main_pane"],
          self._focus_main_pane,
          "Focus main pane"
      )
      self.register_shortcut(
          DEFAULT_SHORTCUTS["toggle_fullscreen"],
          self._toggle_fullscreen,
          "Toggle fullscreen"
      )

      # Activity shortcuts (bound dynamically in Phase 2)
      # Will populate _action_callbacks for show_activity_1 through show_activity_5
  ```

- [ ] **Task 1.22**: Implement focus management helpers
  ```python
  def _focus_sidebar(self) -> None:
      """Set focus to current sidebar panel (internal)."""
      # Implementation in Phase 2 when SideBar component exists
      pass

  def _focus_main_pane(self) -> None:
      """Set focus to main pane content (internal)."""
      # Implementation in Phase 2 when MainPane component exists
      pass

  def _toggle_fullscreen(self) -> None:
      """Toggle fullscreen mode (internal)."""
      if self.isFullScreen():
          self.showNormal()
      else:
          self.showFullScreen()
  ```

---

### Basic Tests

- [ ] **Task 1.23**: Write mode detection tests
  ```python
  def test_frameless_mode_no_parent(qtbot):
      window = ViloCodeWindow()
      assert window._window_mode == WindowMode.Frameless

  def test_embedded_mode_with_parent(qtbot):
      parent = QWidget()
      window = ViloCodeWindow(parent=parent)
      assert window._window_mode == WindowMode.Embedded
  ```

- [ ] **Task 1.24**: Write basic functionality tests
  - Window creation
  - Layout structure
  - Status bar access
  - Window flags (frameless mode)

- [ ] **Task 1.25**: Write keyboard shortcut tests
  ```python
  def test_default_shortcuts_enabled(qtbot):
      window = ViloCodeWindow(enable_default_shortcuts=True)
      shortcuts = window.get_shortcuts()
      assert len(shortcuts) > 0
      assert "Ctrl+B" in shortcuts  # toggle_sidebar

  def test_default_shortcuts_disabled(qtbot):
      window = ViloCodeWindow(enable_default_shortcuts=False)
      shortcuts = window.get_shortcuts()
      assert len(shortcuts) == 0

  def test_register_custom_shortcut(qtbot):
      window = ViloCodeWindow(enable_default_shortcuts=False)
      called = []
      window.register_shortcut("F5", lambda: called.append(True))
      # Trigger shortcut
      assert len(called) == 1

  def test_unregister_shortcut(qtbot):
      window = ViloCodeWindow()
      window.unregister_shortcut("Ctrl+B")
      shortcuts = window.get_shortcuts()
      assert "Ctrl+B" not in shortcuts
  ```

---

### Documentation

- [ ] **Task 1.26**: Create architecture.md
  - MVC pattern overview
  - Component structure
  - Layout flow
  - Platform abstraction
  - Keyboard shortcut system

- [ ] **Task 1.27**: Create initial API documentation
  - Class overview
  - Constructor parameters
  - Mode detection behavior
  - Keyboard shortcut APIs
  - Public methods (implemented so far)

---

## Phase 1 Completion Criteria

✅ Phase 1 is complete when:
1. ViloCodeWindow class created with mode detection
2. Signals declared (4 signals)
3. Placeholder methods exist (toggle_sidebar, toggle_auxiliary_bar)
4. Frameless window setup working on all platforms
5. Frameless background painting implemented (paintEvent)
6. Basic layout structure in place (placeholders for components)
7. Platform detection and adaptation implemented
8. Window controls working (minimize, maximize, close)
9. Window dragging and resizing functional
10. Theme system integration set up (even if not fully styled)
11. **Status bar API complete** (get_status_bar, set_status_bar_visible, is_status_bar_visible, set_status_message)
12. **Menu bar API complete** (set_menu_bar, get_menu_bar)
13. **Keyboard shortcut system implemented** (register, unregister, get, get_default, set_shortcut)
14. **Action-to-callback mapping implemented**
15. **Default VS Code shortcuts registered**
16. Basic tests passing (including shortcut tests)
17. Architecture documentation written

**Task Count**: 30 tasks (was 22, added 8 total):
- Added 5 for keyboard shortcuts
- Added 3 sub-tasks: 1.6b (paintEvent), 1.7b (status bar API), 1.12b (menu bar API)

**Next Phase**: Phase 2 - Components (ActivityBar, SideBar, MainPane, AuxiliaryBar)

---

## Notes

- Reuse as much as possible from ChromeTabbedWindow (platform code, window controls)
- Focus on foundation - components will be implemented in Phase 2
- Use placeholder widgets for now (QLabel with text)
- Ensure mode detection works correctly before moving to Phase 2
- All code must pass type checking (mypy), formatting (black), and linting (ruff)

---

## Evidence Requirements

Following VFWidgets evidence-based development:
- Show actual terminal output for tests
- Display import verification: `python -c "from vfwidgets_vilocode_window import ViloCodeWindow"`
- Show window running (screenshot or terminal output)
- Verify no errors in basic usage
