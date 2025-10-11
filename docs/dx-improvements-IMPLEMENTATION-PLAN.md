# VFWidgets DX Improvements - Implementation Plan

## Overview

**Goal:** Transform VFWidgets from "functional but difficult" to "delightful and intuitive"

**Timeline:** 6 weeks
**Team Size:** 1-2 developers
**Approach:** Iterative with early user testing

---

## Phase 1: Core Menu API (Week 1-2)

### Week 1: ViloCodeWindow Menu Builder

**Goal:** Make menu creation trivial

#### Day 1-2: MenuBuilder Implementation

**File:** `widgets/vilocode_window/src/vfwidgets_vilocode_window/menu_builder.py`

```python
"""Fluent menu builder for ViloCodeWindow."""

from typing import Callable, Optional
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMenu


class MenuBuilder:
    """Fluent interface for building menus.

    Example:
        >>> window.add_menu("File") \\
        ...     .add_action("Open", on_open, "Ctrl+O") \\
        ...     .add_separator() \\
        ...     .add_action("Exit", window.close)
    """

    def __init__(self, menu: QMenu, window):
        self._menu = menu
        self._window = window
        self._submenu_stack: list[QMenu] = []

    def add_action(
        self,
        text: str,
        callback: Optional[Callable] = None,
        shortcut: Optional[str] = None,
        icon: Optional[QIcon] = None,
        tooltip: Optional[str] = None,
    ) -> 'MenuBuilder':
        """Add action to menu."""
        action = self._current_menu().addAction(text)

        if callback:
            action.triggered.connect(callback)
        if shortcut:
            action.setShortcut(shortcut)
        if icon:
            action.setIcon(icon)
        if tooltip:
            action.setToolTip(tooltip)
            action.setStatusTip(tooltip)

        return self

    def add_separator(self) -> 'MenuBuilder':
        """Add separator."""
        self._current_menu().addSeparator()
        return self

    def add_submenu(self, title: str) -> 'MenuBuilder':
        """Add submenu and switch context to it."""
        submenu = self._current_menu().addMenu(title)
        self._submenu_stack.append(submenu)
        return self

    def end_submenu(self) -> 'MenuBuilder':
        """Return to parent menu."""
        if self._submenu_stack:
            self._submenu_stack.pop()
        return self

    def add_checkable(
        self,
        text: str,
        callback: Optional[Callable[[bool], None]] = None,
        checked: bool = False,
        shortcut: Optional[str] = None,
    ) -> 'MenuBuilder':
        """Add checkable action."""
        action = self._current_menu().addAction(text)
        action.setCheckable(True)
        action.setChecked(checked)

        if callback:
            action.triggered.connect(callback)
        if shortcut:
            action.setShortcut(shortcut)

        return self

    def _current_menu(self) -> QMenu:
        """Get current menu (submenu or root)."""
        return self._submenu_stack[-1] if self._submenu_stack else self._menu


__all__ = ['MenuBuilder']
```

**Tests:** `widgets/vilocode_window/tests/test_menu_builder.py`

```python
"""Tests for MenuBuilder."""

import pytest
from PySide6.QtWidgets import QApplication
from vfwidgets_vilocode_window import MenuBuilder
from PySide6.QtWidgets import QMenu


def test_add_action():
    """Test adding simple action."""
    menu = QMenu("Test")
    builder = MenuBuilder(menu, None)

    builder.add_action("Open", lambda: None, "Ctrl+O")

    actions = menu.actions()
    assert len(actions) == 1
    assert actions[0].text() == "Open"
    assert actions[0].shortcut().toString() == "Ctrl+O"


def test_fluent_chaining():
    """Test fluent interface chaining."""
    menu = QMenu("Test")
    builder = MenuBuilder(menu, None)

    result = builder \
        .add_action("Action 1") \
        .add_separator() \
        .add_action("Action 2")

    # Should return same builder
    assert result is builder

    # Check menu structure
    actions = menu.actions()
    assert len(actions) == 3
    assert actions[0].text() == "Action 1"
    assert actions[1].isSeparator()
    assert actions[2].text() == "Action 2"


def test_submenu():
    """Test submenu creation."""
    menu = QMenu("Test")
    builder = MenuBuilder(menu, None)

    builder \
        .add_action("Root Action") \
        .add_submenu("Submenu") \
            .add_action("Sub Action 1") \
            .add_action("Sub Action 2") \
            .end_submenu() \
        .add_action("Root Action 2")

    root_actions = menu.actions()
    assert len(root_actions) == 3

    # Check submenu
    submenu_action = root_actions[1]
    submenu = submenu_action.menu()
    assert submenu is not None
    assert submenu.title() == "Submenu"

    sub_actions = submenu.actions()
    assert len(sub_actions) == 2
    assert sub_actions[0].text() == "Sub Action 1"


def test_checkable_action():
    """Test checkable action."""
    menu = QMenu("Test")
    builder = MenuBuilder(menu, None)

    called_with = []
    def callback(checked):
        called_with.append(checked)

    builder.add_checkable("Toggle", callback, checked=True)

    action = menu.actions()[0]
    assert action.isCheckable()
    assert action.isChecked()

    # Trigger action
    action.trigger()
    assert called_with == [False]  # Toggled to false
```

#### Day 3-4: ViloCodeWindow Integration

**File:** `widgets/vilocode_window/src/vfwidgets_vilocode_window/vilocode_window.py`

Add methods:

```python
from .menu_builder import MenuBuilder

class ViloCodeWindow:

    def add_menu(self, title: str) -> MenuBuilder:
        """Add menu with fluent interface.

        Args:
            title: Menu title (e.g., "File", "Edit")

        Returns:
            MenuBuilder for adding actions

        Example:
            >>> window.add_menu("File") \\
            ...     .add_action("Open", on_open, "Ctrl+O") \\
            ...     .add_action("Exit", window.close)
        """
        menubar = self._ensure_menu_bar()
        menu = menubar.addMenu(title)
        return MenuBuilder(menu, self)

    def get_menu_bar(self) -> QMenuBar:
        """Get menu bar (auto-created).

        Returns:
            QMenuBar instance (never None)
        """
        return self._ensure_menu_bar()

    def _ensure_menu_bar(self) -> QMenuBar:
        """Ensure menu bar exists."""
        if self._menu_bar is None:
            from PySide6.QtWidgets import QMenuBar
            self._menu_bar = QMenuBar()
            self._menu_bar_needs_integration = True
        return self._menu_bar

    def _integrate_menu_bar(self):
        """Integrate menu bar with title bar (called before show)."""
        if not self._menu_bar or not self._menu_bar_needs_integration:
            return

        if self._window_mode == WindowMode.Frameless and self._title_bar:
            self._title_bar.integrate_menu_bar(self._menu_bar)
            self._apply_menu_theme()

        self._menu_bar_needs_integration = False

    def showEvent(self, event):
        """Auto-integrate menu before show."""
        if hasattr(self, '_menu_bar_needs_integration') and self._menu_bar_needs_integration:
            self._integrate_menu_bar()
        super().showEvent(event)
```

#### Day 5: TitleBar Auto-Theming

**File:** `widgets/vilocode_window/src/vfwidgets_vilocode_window/components/title_bar.py`

Improvements:

```python
class TitleBar(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._menu_bar = None
        self._setup_ui()
        self._register_theme_listener()

    def _register_theme_listener(self):
        """Register for theme changes."""
        try:
            from vfwidgets_theme import get_themed_application
            app = get_themed_application()
            if app:
                app.theme_changed.connect(self._on_theme_changed)
        except ImportError:
            pass

    def _on_theme_changed(self, theme):
        """Auto-update styling when theme changes."""
        if self._menu_bar:
            self._apply_menu_styling(theme)

    def integrate_menu_bar(self, menubar: QMenuBar) -> None:
        """Integrate menu bar (new method replacing set_menu_bar logic).

        Handles:
        - Action transfer
        - Theme styling
        - Layout integration
        """
        # Remove old if exists
        if self._menu_bar:
            self._layout.removeWidget(self._menu_bar)
            self._menu_bar.setParent(None)

        # Create draggable wrapper
        draggable = DraggableMenuBar(self)

        # Transfer actions
        actions_to_transfer = list(menubar.actions())
        for action in actions_to_transfer:
            menubar.removeAction(action)
            draggable.addAction(action)

        self._menu_bar = draggable

        # Hide title when menu present
        self._title_label.hide()

        # Apply theme styling
        self._apply_menu_styling()

        # Add to layout
        self._layout.insertWidget(0, self._menu_bar)

    def _apply_menu_styling(self, theme=None):
        """Apply theme-aware menu styling."""
        if not self._menu_bar:
            return

        # Get theme colors
        try:
            from vfwidgets_theme import get_themed_application
            app = get_themed_application()
            if app and app.get_current_theme():
                current_theme = theme or app.get_current_theme()
                fg = current_theme.get_color('menu.foreground', '#cccccc')
                hover_bg = current_theme.get_color('menu.selectionBackground', '#2d2d30')
                active_bg = current_theme.get_color('menubar.selectionBackground', '#007acc')
            else:
                fg, hover_bg, active_bg = '#cccccc', '#2d2d30', '#007acc'
        except (ImportError, AttributeError):
            fg, hover_bg, active_bg = '#cccccc', '#2d2d30', '#007acc'

        # Apply stylesheet
        self._menu_bar.setStyleSheet(f"""
            QMenuBar {{
                background-color: transparent;
                color: {fg};
                border: none;
                padding: 0px;
                margin: 0px;
            }}
            QMenuBar::item {{
                background-color: transparent;
                padding: 5px 10px;
                color: {fg};
            }}
            QMenuBar::item:selected {{
                background-color: {hover_bg};
            }}
            QMenuBar::item:pressed {{
                background-color: {active_bg};
            }}
        """)
```

---

### Week 2: ThemedApplication Improvements

#### Day 1-2: Fix Initialization & Add Validation

**File:** `widgets/theme_system/src/vfwidgets_theme/widgets/application.py`

```python
class ThemeNotFoundError(Exception):
    """Raised when theme doesn't exist."""

    def __init__(self, theme_name: str, available: list[str]):
        self.theme_name = theme_name
        self.available_themes = available

        suggestion = ""
        if available:
            # Find closest match
            import difflib
            matches = difflib.get_close_matches(theme_name, available, n=1)
            if matches:
                suggestion = f" Did you mean '{matches[0]}'?"

        super().__init__(
            f"Theme '{theme_name}' not found.{suggestion}\n"
            f"Available themes: {', '.join(available)}\n"
            f"See: https://docs.vfwidgets.com/themes"
        )


class ThemedApplication:

    def __init__(
        self,
        argv: list[str],
        *,
        theme: Optional[str] = None,
        theme_config: Optional[dict] = None,
        prefer_dark: bool = False,
        prefer_light: bool = False,
    ):
        """Initialize with better defaults."""
        # Build config
        if theme:
            # Explicit theme - validate it exists
            config = {'default_theme': theme, 'persist_theme': False}
        elif prefer_dark:
            config = {'default_theme': 'dark', 'persist_theme': False}
        elif prefer_light:
            config = {'default_theme': 'light', 'persist_theme': False}
        else:
            config = theme_config or {}

        super().__init__(argv, theme_config=config)

    def set_theme(self, theme_name: str, persist: bool = None) -> None:
        """Set theme with validation.

        Args:
            theme_name: Name of theme to apply
            persist: Save preference (default: use config)

        Raises:
            ThemeNotFoundError: If theme doesn't exist

        Example:
            >>> app.set_theme("dark")
            >>> app.set_theme("VSCode Dark+", persist=True)
        """
        # Validate theme exists
        if not self._theme_manager.has_theme(theme_name):
            available = self._theme_manager.list_themes()
            raise ThemeNotFoundError(theme_name, available)

        # Apply theme
        super().set_theme(theme_name, persist=persist)

    def _initialize_theme_system(self) -> None:
        """Initialize theme system (FIXED)."""
        try:
            # ... setup code ...

            # FIX: Mark initialized BEFORE setting theme
            self._is_initialized = True

            # Now theme setting works
            if self._config.auto_detect_system:
                system_theme = self.auto_detect_system_theme()
                if system_theme:
                    self.set_theme(system_theme)

            elif self._config.persist_theme:
                saved = load_theme_preference()
                if saved and self._theme_manager.has_theme(saved):
                    self.set_theme(saved)

            # Set default if none set
            if not self._current_theme:
                if self._theme_manager.has_theme(self._config.default_theme):
                    self.set_theme(self._config.default_theme)
                else:
                    available = self._theme_manager.list_themes()
                    if available:
                        logger.warning(
                            f"Default theme '{self._config.default_theme}' not found. "
                            f"Using '{available[0]}' instead."
                        )
                        self.set_theme(available[0])

        except Exception as e:
            logger.error(f"Theme initialization failed: {e}")
            self._is_initialized = True  # Still mark as initialized
            raise
```

#### Day 3: Update Reamde to Use New API

**File:** `apps/reamde/src/reamde/window.py`

**OLD CODE (50+ lines):**
```python
def _setup_file_menu(self) -> None:
    menu_bar = self.get_menu_bar()
    if not menu_bar:
        from PySide6.QtWidgets import QMenuBar
        menu_bar = QMenuBar()

    file_menu = menu_bar.addMenu("&File")

    open_action = file_menu.addAction("&Open...")
    open_action.setShortcut("Ctrl+O")
    open_action.triggered.connect(self._on_open_file)

    # ... 40 more lines ...

    self.set_menu_bar(menu_bar)
```

**NEW CODE (15 lines):**
```python
def _setup_file_menu(self) -> None:
    """Setup File menu using fluent API."""
    file_menu = self.add_menu("&File")

    file_menu.add_action("&Open...", self._on_open_file, "Ctrl+O")
    file_menu.add_action("&Close", self._on_close_current_tab, "Ctrl+W")
    file_menu.add_separator()

    # Theme Preferences (if available)
    try:
        from vfwidgets_theme.widgets.dialogs import ThemePickerDialog
        file_menu.add_action(
            "Theme &Preferences...",
            lambda: ThemePickerDialog(self).exec()
        )
    except ImportError:
        pass

    file_menu.add_separator()
    file_menu.add_action("E&xit", self.close, "Ctrl+Q")
```

**File:** `apps/reamde/src/reamde/app.py`

**OLD CODE:**
```python
def __init__(self, argv):
    super().__init__(argv, app_id="reamde", prefer_dark=True)
```

**NEW CODE (same - but now works!):**
```python
def __init__(self, argv):
    super().__init__(argv, app_id="reamde", prefer_dark=True)
```

#### Day 4-5: Documentation & Examples

Create:
- `docs/vilocode-window-menu-QUICKSTART.md`
- `docs/themed-application-QUICKSTART.md`
- Update `widgets/vilocode_window/examples/04_customization.py` to show new API

---

## Phase 2: Testing & Validation (Week 3)

### Week 3: Comprehensive Testing

#### Day 1-2: Unit Tests

**New test files:**
- `widgets/vilocode_window/tests/test_menu_builder.py` (done above)
- `widgets/vilocode_window/tests/test_menu_integration.py`
- `widgets/theme_system/tests/test_application_initialization.py`
- `widgets/theme_system/tests/test_theme_validation.py`

#### Day 3: Integration Tests

**Test scenarios:**
1. Menu bar with theme changes
2. Menu bar in frameless vs embedded mode
3. Multiple theme switches
4. Invalid theme names
5. Empty menu bar warnings

#### Day 4: User Testing

**Create test application:**
```python
"""User test application - measure time to complete tasks."""

# Task 1: Add a File menu with Open and Exit
# Task 2: Change to dark theme
# Task 3: Add a View menu with Toggle Sidebar
# Task 4: Test with custom theme

# Measure: Time to complete, errors encountered, confusion points
```

**Invite 3-5 developers to try it (internally)**

#### Day 5: Fix Issues from Testing

Address any issues found during testing.

---

## Phase 3: Extended Widgets (Week 4-5)

### Week 4: Widget Audit

#### Day 1-2: Audit All Widgets

For each widget, evaluate:
1. How easy is it to create and use?
2. Are there initialization traps?
3. Does theme integration work automatically?
4. Are error messages helpful?
5. Is there a quick start example?

**Widgets to audit:**
- ChromeTabbedWindow
- MarkdownViewer
- TerminalWidget
- MultiSplitWidget
- ActivityBar, SideBar, AuxiliaryBar

**Output:** DX audit report with priority rankings

#### Day 3-5: Implement Top 3 Improvements

Based on audit, fix the worst DX issues in top 3 widgets.

### Week 5: Polish & Documentation

#### Day 1-3: Apply DX Patterns

Apply the same patterns to remaining widgets:
- Auto-creation where needed
- Validation and error messages
- Theme integration
- Quick start docs

#### Day 4-5: Create Migration Guide

**File:** `docs/MIGRATION-2.0.md`

Document:
- Old pattern → New pattern
- Deprecated methods
- Breaking changes (if any)
- Code examples

---

## Phase 4: Developer Tools (Week 6)

### Week 6: Debugging & Tools

#### Day 1-3: Widget Inspector

**File:** `shared/vfwidgets_common/src/vfwidgets_common/inspector.py`

```python
"""Runtime widget inspector for debugging."""

class WidgetInspector(QWidget):
    """Visual inspector for widget hierarchy and theming.

    Usage:
        >>> from vfwidgets_common import WidgetInspector
        >>> inspector = WidgetInspector(window)
        >>> inspector.show()
    """

    # Shows:
    # - Widget tree
    # - Applied theme colors
    # - Layout information
    # - Event handlers
```

#### Day 4: Error Message Review

Review all error messages and warnings:
- Add "See: <docs-link>" to all errors
- Add suggestions for common mistakes
- Test error messages are helpful

#### Day 5: Final Polish

- Run linter on all new code
- Ensure all tests pass
- Update CHANGELOG
- Create release notes

---

## Deliverables

### Code
- [ ] MenuBuilder class with tests
- [ ] ViloCodeWindow.add_menu() method
- [ ] Auto-creation of menu bar
- [ ] Lazy menu integration
- [ ] TitleBar auto-theming
- [ ] ThemedApplication validation
- [ ] ThemeNotFoundError with suggestions
- [ ] Fix initialization bug
- [ ] Fix prefer_dark override
- [ ] All existing tests pass
- [ ] 50+ new tests added

### Documentation
- [ ] vilocode-window-menu-QUICKSTART.md
- [ ] themed-application-QUICKSTART.md
- [ ] MIGRATION-2.0.md
- [ ] Updated API reference
- [ ] 5+ runnable examples

### Tools
- [ ] WidgetInspector utility
- [ ] Error message improvements
- [ ] Debugging guide

---

## Success Metrics

### Before (Current State)
- Time to add menu: **3 hours** (with debugging)
- Lines of code: **~50 lines**
- Error messages: **Silent failures**
- Tests: **Integration tests only**
- Documentation: **Scattered in examples**

### After (Target State)
- Time to add menu: **< 5 minutes**
- Lines of code: **~10 lines** (80% reduction)
- Error messages: **Clear with suggestions**
- Tests: **Unit + integration coverage**
- Documentation: **Quick start + API reference**

### Validation
- [ ] New developer can add menu in < 5 minutes
- [ ] All common mistakes have warnings
- [ ] Zero initialization traps
- [ ] Theme integration automatic
- [ ] 100% API documentation coverage

---

## Risk Mitigation

### Risk 1: Breaking Changes

**Mitigation:**
- Keep old API working (deprecated)
- Provide automatic migration script
- 6-month deprecation period
- Clear migration guide

### Risk 2: Performance Regression

**Mitigation:**
- Benchmark before/after
- Lazy initialization where possible
- Profile critical paths
- No synchronous theme operations

### Risk 3: Incomplete Testing

**Mitigation:**
- Test-driven development
- User testing before release
- Gradual rollout (beta tag)
- Feedback collection system

---

## Timeline Summary

| Week | Focus | Deliverable |
|------|-------|-------------|
| 1 | MenuBuilder + ViloCodeWindow | Working menu API |
| 2 | ThemedApplication fixes | Theme system improvements |
| 3 | Testing & validation | Test suite + user feedback |
| 4 | Widget audit | DX audit report |
| 5 | Extended widgets | Top 3 widgets improved |
| 6 | Tools & polish | Inspector + final docs |

**Total: 6 weeks to transform VFWidgets DX**

---

## Next Steps

1. **Review this plan** - Get feedback from team
2. **Create branch** - `feature/dx-improvements`
3. **Start Week 1** - Begin MenuBuilder implementation
4. **Daily standups** - Track progress and blockers
5. **Weekly demos** - Show progress to stakeholders

Let's make VFWidgets amazing! 🚀
