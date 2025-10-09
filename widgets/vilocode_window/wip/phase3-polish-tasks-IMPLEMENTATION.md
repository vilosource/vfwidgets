# Phase 3: Polish & Examples Tasks — ViloCodeWindow Implementation

**Goal**: Add animations, keyboard navigation, helper functions, template classes, comprehensive examples, and final documentation.

**Status**: 🔴 Not Started (Blocked by Phase 2)

---

## Task Checklist

### Animations & Transitions

- [ ] **Task 3.1**: Implement sidebar collapse animation
  ```python
  def toggle_sidebar(self) -> None:
      """Toggle sidebar with smooth animation."""
      animation = QPropertyAnimation(self._sidebar, b"minimumWidth")
      animation.setDuration(200)
      animation.setEasingCurve(QEasingCurve.Type.OutCubic)

      if self._sidebar.isVisible():
          # Collapse: current width → 0
          animation.setStartValue(self._sidebar.width())
          animation.setEndValue(0)
          animation.finished.connect(lambda: self._sidebar.setVisible(False))
      else:
          # Expand: 0 → last width
          self._sidebar.setVisible(True)
          animation.setStartValue(0)
          animation.setEndValue(self._last_sidebar_width)

      animation.start()
  ```

- [ ] **Task 3.2**: Implement auxiliary bar collapse animation
  - Same as sidebar, but for right auxiliary bar
  - Remember last width when collapsing

- [ ] **Task 3.3**: Implement activity item hover animation
  - Smooth background color transition on hover
  - Subtle scale effect (optional, check if too much)

- [ ] **Task 3.4**: Implement panel switching animation
  - Fade out old panel, fade in new panel
  - Or slide transition (left/right)
  - Keep it subtle, < 150ms

---

### Keyboard Navigation & Shortcuts

- [ ] **Task 3.5**: Implement keyboard navigation for activity bar
  - Tab/Shift+Tab: Navigate between activity items
  - Enter/Space: Activate item
  - Arrow Up/Down: Navigate items
  - Focus indicator (dotted outline)

- [ ] **Task 3.6**: Add default keyboard shortcuts
  ```python
  def _setup_default_shortcuts(self) -> None:
      """Set up default keyboard shortcuts."""
      # Toggle sidebar: Ctrl+B
      QShortcut(QKeySequence("Ctrl+B"), self, self.toggle_sidebar)

      # Toggle auxiliary bar: Ctrl+Alt+B
      QShortcut(QKeySequence("Ctrl+Alt+B"), self, self.toggle_auxiliary_bar)

      # Focus main pane: Ctrl+1
      QShortcut(QKeySequence("Ctrl+1"), self, self._focus_main_pane)

      # Focus sidebar: Ctrl+0
      QShortcut(QKeySequence("Ctrl+0"), self, self._focus_sidebar)
  ```

- [ ] **Task 3.7**: Implement focus management
  ```python
  def _focus_main_pane(self) -> None:
      """Set focus to main pane content."""
      if self._main_pane and self._main_pane.get_content():
          self._main_pane.get_content().setFocus()

  def _focus_sidebar(self) -> None:
      """Set focus to current sidebar panel."""
      if self._sidebar.isVisible():
          panel = self._sidebar.get_current_panel_widget()
          if panel:
              panel.setFocus()
  ```

- [ ] **Task 3.8**: Add accessibility support
  - Set object names for screen readers
  - Add aria labels (via Qt accessibility)
  - Test with screen reader (basic check)

---

### Helper Functions

- [ ] **Task 3.9**: Create `helpers.py` with convenience functions
  ```python
  # widgets/vilocode_window/src/vfwidgets_vilocode_window/helpers.py

  def create_basic_ide_window(title: str = "IDE") -> ViloCodeWindow:
      """Create a basic IDE window with common defaults.

      Includes:
      - Files activity item + explorer panel (placeholder)
      - Search activity item + search panel (placeholder)
      - Empty main pane (set with .set_main_content())
      - Status bar ready to use
      """

  def create_terminal_ide_window(
      terminal_provider,
      title: str = "Terminal IDE"
  ) -> ViloCodeWindow:
      """Create an IDE window with terminal-focused setup.

      Pre-configured with MultisplitWidget in main pane.
      """

  def create_editor_ide_window(
      title: str = "Editor IDE"
  ) -> ViloCodeWindow:
      """Create an IDE window with tabbed editor setup.

      Pre-configured with ChromeTabbedWindow in main pane.
      """
  ```

- [ ] **Task 3.10**: Implement `create_basic_ide_window()`
  - Add files, search, git activity items
  - Add placeholder panels (QLabel with instructions)
  - Auto-connect activity items to panels
  - Return configured window

- [ ] **Task 3.11**: Implement `create_terminal_ide_window()`
  - Requires MultisplitWidget + provider
  - Add terminal-focused activity items
  - Configure status bar with terminal info
  - Return configured window

- [ ] **Task 3.12**: Implement `create_editor_ide_window()`
  - Use ChromeTabbedWindow in embedded mode
  - Add editor-focused activity items (files, search, extensions)
  - Return configured window

---

### Template Classes

- [ ] **Task 3.13**: Create `templates.py` with base classes
  ```python
  # widgets/vilocode_window/src/vfwidgets_vilocode_window/templates.py

  class BasicIDEWindow(ViloCodeWindow):
      """Template for basic IDE with files and search.

      Subclass and override methods to customize:
      - create_explorer_widget() → Your file tree
      - create_search_widget() → Your search UI
      - create_main_widget() → Your editor
      - get_files_icon() → Custom icon
      """
  ```

- [ ] **Task 3.14**: Implement `BasicIDEWindow` template
  - Override-able methods for all widgets
  - Sensible defaults (QLabel placeholders)
  - Auto-setup in `__init__`
  - Example in docstring

- [ ] **Task 3.15**: Create `TerminalIDEWindow` template
  ```python
  class TerminalIDEWindow(ViloCodeWindow):
      """Template for terminal-focused IDE.

      Pre-configured with MultisplitWidget.
      Requires providing a WidgetProvider in __init__.
      """

      def __init__(self, provider: WidgetProvider):
          super().__init__()
          self._provider = provider
          self._setup_terminal_layout()
  ```

- [ ] **Task 3.16**: Create example subclass showing usage
  - `examples/templates_example.py`
  - Shows how to subclass BasicIDEWindow
  - Override methods with real widgets

---

### Examples

- [ ] **Task 3.17**: Create `01_minimal_window.py`
  ```python
  """Simplest possible ViloCodeWindow usage.

  Just main content, no sidebar or activity bar.
  """
  from PySide6.QtWidgets import QApplication, QTextEdit
  from vfwidgets_vilocode_window import ViloCodeWindow

  app = QApplication([])

  window = ViloCodeWindow()
  window.setWindowTitle("Minimal Window")
  window.set_main_content(QTextEdit("Hello World"))
  window.show()

  app.exec()
  ```

- [ ] **Task 3.18**: Create `02_activity_sidebar.py`
  - Add activity items
  - Add sidebar panels
  - Connect signals manually
  - Show how to build layout from scratch

- [ ] **Task 3.19**: Create `03_full_layout.py`
  - All components: activity bar, sidebar, main pane, auxiliary bar, status bar
  - Multiple panels in sidebar
  - Auxiliary bar with outline view
  - Status bar with widgets
  - Menu bar with File/Edit/View menus

- [ ] **Task 3.20**: Create `04_terminal_ide.py`
  - Use MultisplitWidget in main pane
  - Terminal provider with real terminals
  - Terminal-focused activity items
  - Status bar showing terminal info

- [ ] **Task 3.21**: Create `05_tabbed_editor.py`
  - Use ChromeTabbedWindow (embedded) in main pane
  - Editor-focused layout
  - Files panel with tree
  - Show opening files in tabs

- [ ] **Task 3.22**: Create `06_themed_ide.py`
  - Integration with vfwidgets-theme
  - Show theme switching
  - Multiple themes (dark, light, custom)
  - Add theme menu

- [ ] **Task 3.23**: Create `07_helper_functions.py`
  - Demonstrate helper functions
  - Show `create_basic_ide_window()`
  - Show `create_terminal_ide_window()`
  - Show `create_editor_ide_window()`

- [ ] **Task 3.24**: Create `08_templates.py`
  - Demonstrate template subclassing
  - Subclass `BasicIDEWindow`
  - Override methods with custom widgets
  - Show how easy it is

- [ ] **Task 3.25**: Create `run_examples.py` interactive launcher
  ```python
  """Interactive example launcher for ViloCodeWindow.

  Run this script to see a menu of all examples.
  """
  import sys
  from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QPushButton

  # Import all examples
  # Show dialog with buttons for each example
  # Launch selected example
  ```

---

### Documentation

- [ ] **Task 3.26**: Create comprehensive README.md
  - Project description
  - Features list
  - Quick start (Tier 1 API)
  - Installation instructions
  - Link to examples
  - Link to full docs

- [ ] **Task 3.27**: Create `docs/api.md` - Complete API reference
  - All public methods documented
  - All signals documented
  - All properties documented
  - Code examples for each API

- [ ] **Task 3.28**: Create `docs/usage.md` - Usage patterns
  - Tier 1: Zero config
  - Tier 2: Helper functions
  - Tier 3: Template subclasses
  - Tier 4: Full manual control
  - Best practices
  - Common patterns

- [ ] **Task 3.29**: Create `docs/theming.md` - Theme integration
  - How to use with vfwidgets-theme
  - Theme token mapping
  - Custom themes
  - Fallback colors
  - QSS styling (without theme system)

- [ ] **Task 3.30**: Create `docs/platform-notes.md` - Platform-specific details
  - Windows notes
  - macOS notes
  - Linux X11 notes
  - Linux Wayland notes
  - WSL/WSLg notes
  - Known issues per platform

- [ ] **Task 3.31**: Update `docs/architecture.md` with final architecture
  - Complete component diagram
  - Signal flow diagram
  - Theme integration details
  - Layout calculations
  - Performance considerations

- [ ] **Task 3.32**: Create `docs/examples.md` - Example descriptions
  - Description of each example
  - What it demonstrates
  - Key concepts
  - How to run

- [ ] **Task 3.33**: Create CONTRIBUTING.md
  - How to contribute
  - Code style (black, ruff, mypy)
  - Testing requirements
  - PR process
  - Where to ask questions

- [ ] **Task 3.34**: Create CHANGELOG.md
  - v1.0.0 initial release notes
  - Features list
  - Known limitations
  - Future roadmap (v2.0+)

---

### Performance & Polish

- [ ] **Task 3.35**: Optimize layout calculations
  - Profile layout performance
  - Ensure < 16ms layout updates (60 FPS)
  - Optimize resize handle dragging

- [ ] **Task 3.36**: Optimize painting
  - Use caching for static elements
  - Minimize repaints on theme change
  - Profile paint events

- [ ] **Task 3.37**: Memory leak check
  - Test add/remove panels many times
  - Check for leaked widgets
  - Verify proper cleanup

- [ ] **Task 3.38**: Add debug logging
  - Log mode detection
  - Log platform detection
  - Log component initialization
  - Optional debug flag to enable

---

### Final Testing

- [ ] **Task 3.39**: Manual testing on all platforms
  - Windows 10/11: Frameless, Aero snap, HiDPI
  - macOS: Frameless, fullscreen, HiDPI
  - Linux X11: Frameless, window management
  - Linux Wayland: Compositor compatibility
  - WSL/WSLg: Fallback behavior

- [ ] **Task 3.40**: Cross-platform screenshot tests
  - Capture screenshots on each platform
  - Verify visual consistency
  - Check theme colors

- [ ] **Task 3.41**: Accessibility testing
  - Test with screen reader
  - Test keyboard-only navigation
  - Test high contrast themes

- [ ] **Task 3.42**: Integration testing with other VFWidgets
  - Use with ChromeTabbedWindow
  - Use with MultisplitWidget
  - Use with TerminalWidget
  - Use with vfwidgets-theme
  - Verify no conflicts

---

### Package & Release

- [ ] **Task 3.43**: Finalize pyproject.toml
  - Correct version (1.0.0)
  - All dependencies listed
  - Correct package metadata
  - Classifiers, keywords, URLs

- [ ] **Task 3.44**: Test installation from source
  ```bash
  pip install -e "./widgets/vilocode_window[dev]"
  python -c "from vfwidgets_vilocode_window import ViloCodeWindow"
  ```

- [ ] **Task 3.45**: Run all tests
  ```bash
  cd widgets/vilocode_window
  pytest --cov=vfwidgets_vilocode_window --cov-report=html
  # Verify > 80% coverage
  ```

- [ ] **Task 3.46**: Run code quality checks
  ```bash
  black --check src/
  ruff check src/
  mypy src/
  # All pass with no errors
  ```

- [ ] **Task 3.47**: Build package
  ```bash
  python -m build
  # Check dist/ for wheel and sdist
  ```

---

## Phase 3 Completion Criteria

✅ Phase 3 (and v1.0) is complete when:
1. ✅ All animations implemented and smooth
2. ✅ Keyboard navigation working
3. ✅ Helper functions implemented and tested
4. ✅ Template classes implemented with examples
5. ✅ All 8+ examples working and documented
6. ✅ Comprehensive documentation (README, API, usage, theming, platform notes)
7. ✅ All tests passing with > 80% coverage
8. ✅ Code quality checks passing (black, ruff, mypy)
9. ✅ Manual testing on all platforms successful
10. ✅ Package builds successfully
11. ✅ Can build a simple IDE in < 100 lines of code (Tier 2 API)
12. ✅ Zero errors on basic usage (Tier 1 API)

**Next Phase**: v2.0 Planning (persistence, advanced layouts, plugins)

---

## Notes

- Polish is critical for professional appearance
- Examples are documentation — make them excellent
- Test on real platforms, not just VMs
- Performance matters — optimize hot paths
- Accessibility is not optional

---

## Evidence Requirements

- Show animations working (video/GIF)
- Show keyboard navigation working
- Show all examples running (screenshots)
- Show test coverage report (> 80%)
- Show code quality passing (black, ruff, mypy output)
- Show package building successfully
- Show installation and import working
